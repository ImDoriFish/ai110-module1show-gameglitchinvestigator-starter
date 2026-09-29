# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [ ] Describe the game's purpose.
- [ ] Detail which bugs you found.
- [ ] Explain what fixes you applied.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. Run `python -m streamlit run app.py`. It opens on Normal: range 1 to 50, 8 attempts.
2. Guess above the secret and the hint says "Go LOWER". Guess below and it says "Go HIGHER". It stays correct every turn.
3. You can open "Developer Debug Info" to see the secret to double check.
4. Type `abc` and submit. You get an error and lose no attempt.
5. Type `500` and submit. You get "Enter a number between 1 and 50" and lose no attempt.
6. Type `3.7` and submit. You get "Enter a whole number, not a decimal" and lose no attempt.
7. You can change the difficulty, and the amount of attempts and the range will vary.
8. Win a round, and you will receive a certain amount of points based on the number of guesses. The fewest guesses gives the highest points.
9. Lose a round, the game will present the secret and stop accepting new guesses.
10. Press "New Game" to restart for a new session. Everything including score, history and attempts will be reset, and the new secret will be generated based on the current difficulty.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

The suite started as the 3 provided tests, which could not run at all until the
logic was refactored out of `app.py` into `logic_utils.py` — they import from
`logic_utils`, and importing `app.py` executes Streamlit code at module level.
It now stands at 23 tests, with a regression test for each bug that was fixed.

```
$ .venv/Scripts/python.exe -m pytest tests/ -v

============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.6.0
rootdir: ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collected 23 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  4%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  8%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 13%]
tests/test_game_logic.py::test_too_high_tells_player_to_go_lower PASSED  [ 17%]
tests/test_game_logic.py::test_too_low_tells_player_to_go_higher PASSED  [ 21%]
tests/test_game_logic.py::test_win_message_does_not_give_a_direction PASSED [ 26%]
tests/test_game_logic.py::test_label_and_message_agree PASSED            [ 30%]
tests/test_game_logic.py::test_single_digit_guess_below_three_digit_secret PASSED [ 34%]
tests/test_game_logic.py::test_three_digit_guess_above_single_digit_secret PASSED [ 39%]
tests/test_game_logic.py::test_win_is_detected_for_equal_numbers PASSED  [ 43%]
tests/test_game_logic.py::test_easy_range PASSED                         [ 47%]
tests/test_game_logic.py::test_normal_range PASSED                       [ 52%]
tests/test_game_logic.py::test_hard_range PASSED                         [ 56%]
tests/test_game_logic.py::test_unknown_difficulty_falls_back_to_normal PASSED [ 60%]
tests/test_game_logic.py::test_ranges_grow_with_difficulty PASSED        [ 65%]
tests/test_game_logic.py::test_every_difficulty_is_winnable PASSED       [ 69%]
tests/test_game_logic.py::test_wrong_guesses_always_lose_points PASSED   [ 73%]
tests/test_game_logic.py::test_both_wrong_outcomes_are_scored_the_same PASSED [ 78%]
tests/test_game_logic.py::test_win_on_first_guess_pays_full_bonus PASSED [ 82%]
tests/test_game_logic.py::test_win_bonus_drops_by_ten_per_guess PASSED   [ 86%]
tests/test_game_logic.py::test_winning_earlier_always_scores_higher PASSED [ 91%]
tests/test_game_logic.py::test_slow_win_still_pays_the_minimum PASSED    [ 95%]
tests/test_game_logic.py::test_unknown_outcome_leaves_the_score_alone PASSED [100%]

============================= 23 passed in 0.04s ==============================
```

### Which test covers which bug

| Bug | Test | What it catches |
|-----|------|-----------------|
| #1 — hint messages swapped | `test_too_high_tells_player_to_go_lower`, `test_too_low_tells_player_to_go_higher`, `test_label_and_message_agree` | The 3 provided tests only check the outcome label, so they passed against the broken code. These check the message the player actually reads. |
| #2 — secret cast to `str` | `test_single_digit_guess_below_three_digit_secret`, `test_win_is_detected_for_equal_numbers` | String comparison made `"9" > "100"` true, and `49 == "49"` false, so a correct guess was not a win. |
| #3 — `try/except TypeError` removed | (covered by the Bug #2 tests) | A bad type now fails loudly instead of silently returning a wrong answer. |
| #12 — difficulty ranges | `test_ranges_grow_with_difficulty`, `test_every_difficulty_is_winnable` | Hard was 1–50 with 5 attempts, but binary search needs 6 — it was unwinnable. This test fails against the old values. |
| #13 — wrong guess added points | `test_wrong_guesses_always_lose_points`, `test_both_wrong_outcomes_are_scored_the_same` | `"Too High"` gained 5 points on even attempts. The tests loop over attempts 1–10, because a single odd-numbered call would have passed. |
| #14 — win bonus off by one | `test_win_on_first_guess_pays_full_bonus`, `test_winning_earlier_always_scores_higher` | A first-guess win paid 80 instead of 90. |

### What the tests do not cover

Everything in `app.py` — the session-state wiring, the New Game button, the
difficulty-change handling. pytest cannot import `app.py` outside a running
Streamlit session, so those fixes (bugs #4, #5, #6, #7, #8, #9, #10, #11, #15,
#18) were verified by hand in the browser instead.

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
