"""Pure game logic for the number guessing game.

FIXED [Bugs #20 / #21] - refactor into logic_utils.py:
    I asked Claude to do this move for me after working through the earlier bugs
    myself. It moved the four functions, added the import to app.py, and updated
    the call site. I verified with pytest, which passed for the first time -
    before the refactor the tests could not run at all, because they import from
    logic_utils and the functions were still in app.py.
"""


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    # FIXED [Bug #12]: Claude first said Hard's range was too small and should be widened, but checking the attempt
    # limits showed that was wrong - Hard had 1-50 with only 5 attempts, and binary search needs 6 guesses for a range
    # of 50, so Hard was already unwinnable and widening it would have made it worse. The real problem was that the
    # range and the attempt limit lived in different files and nothing checked them against each other. I fixed it by
    # swapping Normal to 1-50 and Hard to 1-100, setting attempts to Easy 10, Normal 8, Hard 7 so every difficulty is
    # beatable but Hard needs perfect play, and moving the attempt limits here so both numbers live in one file.
    # I tested it with test_every_difficulty_is_winnable, which fails against the old Hard values, and by playing each
    # difficulty and checking the sidebar range and attempt count matched.
    if difficulty == "Hard":
        return 1, 100
    # Unknown difficulty falls back to Normal's range, not Hard's.
    return 1, 50


def get_attempts_for_difficulty(difficulty: str):
    """Return how many guesses a difficulty allows."""
    # Moved out of app.py so the range and the attempt limit can be tested
    # against each other - see test_every_difficulty_is_winnable. Bug #12 was
    # only possible because these two numbers lived in different files and
    # nothing checked that a difficulty was actually beatable.
    if difficulty == "Easy":
        return 10
    if difficulty == "Hard":
        return 7
    return 8


# FIXED [Bug #16]: Claude pointed out that parse_guess only checked the input was a number, never that it was in
# range, so a guess of 500 was accepted on Easy (1-20) and burned an attempt on a number that could never be right.
# Claude suggested giving low and high default values of None, but I made them required instead so a caller cannot
# forget the range and silently skip validation. I fixed it by adding a range check after the int conversion and
# updating the call in app.py to pass low and high. I tested it with test_guess_above_range_is_rejected and
# test_guesses_at_the_edges_are_accepted, which checks 1 and 20 are still legal since the range is inclusive.
def parse_guess(raw: str, low: int, high: int):

    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
    # FIXED [Bug #17]: Claude pointed out that int(float("3.7")) silently truncated a decimal to 3, so the player was
    # scored against a number they never typed, and it truncated rather than rounded so 3.9 also became 3. I fixed it by
    # rejecting decimals with their own message instead of converting them, so the player is told what was actually wrong.
    # I tested it with test_decimal_input_is_rejected and test_decimal_is_not_rounded_or_truncated.
        if "." in raw:
            return False, None, "Enter a whole number, not a decimal."
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    if value < low or value > high:
        return False, None, f"Enter a number between {low} and {high}."


    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    Returns one of: "Win", "Too High", "Too Low"
    """
    # FIXED [Bug #22] - check_guess returned a tuple:
    #   The provided tests assert against a plain string but the function
    #   returned (outcome, message). Claude suggested splitting it: check_guess
    #   returns the outcome only, and a new hint_message() supplies the text. I
    #   took that suggestion because it let the provided tests pass unmodified
    #   and made the hint messages testable - which was the exact gap that let
    #   my first Bug #1 attempt look correct when it wasn't.
    if guess == secret:
        return "Win"

    if guess > secret:
        return "Too High"
    return "Too Low"
# FIXED [Bug #3] - removed the try/except TypeError:
    #   Claude explained that once Bug #2 was fixed, this block was unreachable,
    #   and that it still held a second unfixed copy of the hint messages. I
    #   removed the wrapper and unindented the body. The useful part of the
    #   explanation was why removing error handling makes the code SAFER here: a
    #   stray string now crashes with a clear line number instead of silently
    #   returning a wrong answer.


def hint_message(outcome: str):
    """Return the player-facing hint text for a given outcome."""
    # FIXED [Bug #1] - swapped hint messages:
    #   Claude located the bug in check_guess and explained that the label and
    #   the message contradicted each other. My first fix flipped the comparison
    #   operator from > to <, which made the on-screen hint correct - but Claude
    #   caught that this had inverted the outcome labels instead, so I'd moved
    #   the bug rather than fixed it. I changed approach and swapped the two
    #   message strings, leaving the operator alone, so each line pairs a
    #   correct label with a correct message.
    if outcome == "Win":
        return "🎉 Correct!"
    if outcome == "Too High":
        return "📉 Go LOWER!"
    return "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        # FIXED [Bug #14]: Claude pointed out that attempt_number is already 1-based because app.py increments attempts
    # before calling this, so the +1 charged the player for a guess they never made and underpaid every win by 10 -
    # a first-guess win paid 80 instead of 90. I fixed it by removing the +1. I left the floor alone since that is not
    # a bug, it just stops a very slow win paying 0. I tested it with test_win_on_first_guess_pays_full_bonus.
        points = 100 - 10 * attempt_number 
        if points < 10:
            points = 10
        return current_score + points

    # FIXED [Bug #13]: Claude pointed out that a wrong "Too High" guess ADDED 5 points on even attempts, so the two
    # wrong outcomes were scored differently and you could farm points by guessing high every other turn. I fixed it by
    # making both branches subtract 5. I tested it with test_wrong_guesses_always_lose_points, which loops over attempts
    # 1-10 and fails against the old code because it only misbehaved on even numbers.
    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
