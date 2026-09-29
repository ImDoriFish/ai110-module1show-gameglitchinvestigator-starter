"""Tests for the pure game logic in logic_utils.py.

Each group below is a regression test for a bug that was found and fixed - if
someone reintroduces the bug, the matching test fails. Every test in the "Bug"
sections was written to FAIL against the original broken code.
"""

import math

import pytest

from logic_utils import (
    check_guess,
    hint_message,
    get_range_for_difficulty,
    get_attempts_for_difficulty,
    update_score,
    parse_guess,
)


# ---------------------------------------------------------------------------
# Original provided tests - outcome labels only
# ---------------------------------------------------------------------------

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# ---------------------------------------------------------------------------
# Bug #1 - the hint messages were swapped
#
# The three tests above all passed against the broken code, because they only
# check the outcome LABEL. The bug was in the player-facing MESSAGE, which
# nothing asserted on. These close that gap.
# ---------------------------------------------------------------------------

def test_too_high_tells_player_to_go_lower():
    # Guessing above the secret must point the player DOWN, not up.
    assert "LOWER" in hint_message("Too High")


def test_too_low_tells_player_to_go_higher():
    # Guessing below the secret must point the player UP, not down.
    assert "HIGHER" in hint_message("Too Low")


def test_win_message_does_not_give_a_direction():
    # A win is not a direction - it should not tell the player to move.
    message = hint_message("Win")
    assert "LOWER" not in message
    assert "HIGHER" not in message


def test_label_and_message_agree():
    # The real defect was a label and a message that contradicted each other,
    # so assert on both halves together for the same guess.
    outcome = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in hint_message(outcome)


# ---------------------------------------------------------------------------
# Bug #2 - the secret was cast to str() on even attempts
#
# That made comparisons alphabetical instead of numeric. Alphabetically
# "9" > "100" is True, because "9" beats "1" at the first character - so the
# game would claim 9 was higher than 100.
# ---------------------------------------------------------------------------

def test_single_digit_guess_below_three_digit_secret():
    # The exact case the string comparison got wrong: 9 vs 100.
    assert check_guess(9, 100) == "Too Low"


def test_three_digit_guess_above_single_digit_secret():
    assert check_guess(100, 9) == "Too High"


def test_win_is_detected_for_equal_numbers():
    # Under the bug, 49 == "49" was False, so a correct guess was not a win.
    assert check_guess(49, 49) == "Win"


# ---------------------------------------------------------------------------
# Bug #4 - the secret ignored the selected difficulty
#
# The session-state half of this fix lives in app.py and needs a running
# Streamlit session, so it cannot be unit tested here. What IS testable is that
# each difficulty reports the range the secret is supposed to be drawn from.
# ---------------------------------------------------------------------------

def test_easy_range():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_normal_range():
    assert get_range_for_difficulty("Normal") == (1, 50)


def test_hard_range():
    assert get_range_for_difficulty("Hard") == (1, 100)


def test_unknown_difficulty_falls_back_to_normal():
    assert get_range_for_difficulty("Nonsense") == (1, 50)


def test_ranges_grow_with_difficulty():
    # Bug #12: Hard used to have a NARROWER range than Normal. This states the
    # rule rather than the specific numbers, so it survives future retuning.
    _, easy = get_range_for_difficulty("Easy")
    _, normal = get_range_for_difficulty("Normal")
    _, hard = get_range_for_difficulty("Hard")
    assert easy < normal < hard


def test_every_difficulty_is_winnable():
    # The test that would actually have caught Bug #12. Hard was 1-50 with only
    # 5 attempts, but binary search needs 6 guesses for a range of 50 - so Hard
    # could not be won reliably at all. Range and attempt limit have to be
    # checked against each other, not in isolation.
    for difficulty in ["Easy", "Normal", "Hard"]:
        low, high = get_range_for_difficulty(difficulty)
        attempts = get_attempts_for_difficulty(difficulty)
        needed = math.ceil(math.log2(high - low + 1))
        assert attempts >= needed, (
            f"{difficulty} spans {low}-{high} which needs {needed} guesses, "
            f"but only allows {attempts}"
        )


# ---------------------------------------------------------------------------
# Bug #13 - a wrong "Too High" guess used to ADD 5 points on even attempts
# ---------------------------------------------------------------------------

def test_wrong_guesses_always_lose_points():
    # Looping over the attempt numbers is the whole point: the old code only
    # misbehaved on EVEN attempts, so a single call with attempt 1 would have
    # passed against the broken version.
    for attempt in range(1, 11):
        assert update_score(100, "Too High", attempt) == 95
        assert update_score(100, "Too Low", attempt) == 95


def test_both_wrong_outcomes_are_scored_the_same():
    # "Too High" and "Too Low" are both misses and must cost the same.
    for attempt in range(1, 11):
        high = update_score(100, "Too High", attempt)
        low = update_score(100, "Too Low", attempt)
        assert high == low


# ---------------------------------------------------------------------------
# Bug #14 - the win bonus was off by one and underpaid every win
# ---------------------------------------------------------------------------

def test_win_on_first_guess_pays_full_bonus():
    # Was 80 under the bug, because (attempt_number + 1) charged for a guess
    # that was never made.
    assert update_score(0, "Win", 1) == 90


def test_win_bonus_drops_by_ten_per_guess():
    assert update_score(0, "Win", 2) == 80
    assert update_score(0, "Win", 3) == 70
    assert update_score(0, "Win", 5) == 50


def test_winning_earlier_always_scores_higher():
    # States the rule rather than the exact numbers, so it survives retuning.
    scores = [update_score(0, "Win", attempt) for attempt in range(1, 10)]
    assert scores == sorted(scores, reverse=True)


def test_slow_win_still_pays_the_minimum():
    # Not a bug - the floor stops a very slow win paying 0 or going negative.
    assert update_score(0, "Win", 10) == 10
    assert update_score(0, "Win", 50) == 10


def test_unknown_outcome_leaves_the_score_alone():
    assert update_score(42, "Nonsense", 3) == 42


# ---------------------------------------------------------------------------
# parse_guess - input validation
#
# low and high are required arguments rather than optional ones, so a caller
# cannot forget the range and silently skip validation.
# ---------------------------------------------------------------------------

def test_valid_guess_is_accepted():
    ok, value, err = parse_guess("15", 1, 20)
    assert ok is True
    assert value == 15
    assert err is None


def test_empty_input_is_rejected():
    ok, value, err = parse_guess("", 1, 20)
    assert ok is False
    assert value is None
    assert err is not None


def test_none_input_is_rejected():
    ok, value, err = parse_guess(None, 1, 20)
    assert ok is False
    assert value is None


def test_non_numeric_input_is_rejected():
    ok, value, err = parse_guess("abc", 1, 20)
    assert ok is False
    assert value is None


# ---------------------------------------------------------------------------
# Bug #16 - any number was accepted regardless of the difficulty's range
# ---------------------------------------------------------------------------

def test_guess_below_range_is_rejected():
    ok, value, err = parse_guess("0", 1, 20)
    assert ok is False
    assert value is None


def test_guess_above_range_is_rejected():
    # The original case: 500 was accepted on Easy, burning an attempt on a
    # guess that could never be right.
    ok, value, err = parse_guess("500", 1, 20)
    assert ok is False
    assert value is None


def test_negative_guess_is_rejected():
    assert parse_guess("-7", 1, 20)[0] is False


def test_guesses_at_the_edges_are_accepted():
    # The range is inclusive, so 1 and 20 are both legal on Easy. Writing < and
    # > as <= and >= here is the classic off-by-one, and it would quietly
    # reject two perfectly valid guesses.
    assert parse_guess("1", 1, 20)[0] is True
    assert parse_guess("20", 1, 20)[0] is True


def test_the_same_guess_can_be_legal_on_one_difficulty_and_not_another():
    # 73 is valid on Hard (1-100) but out of range on Easy (1-20).
    assert parse_guess("73", 1, 100)[0] is True
    assert parse_guess("73", 1, 20)[0] is False


# ---------------------------------------------------------------------------
# Bug #17 - decimals were silently truncated instead of rejected
# ---------------------------------------------------------------------------

def test_decimal_input_is_rejected():
    # "3.7" used to become 3 with no warning, so the player was scored against
    # a number they did not type.
    ok, value, err = parse_guess("3.7", 1, 20)
    assert ok is False
    assert value is None


def test_decimal_is_not_rounded_or_truncated():
    # Guard against a "fix" that rounds instead of rejecting.
    assert parse_guess("3.9", 1, 20)[1] is None


def test_decimal_that_looks_whole_is_still_rejected():
    assert parse_guess("5.0", 1, 20)[0] is False

