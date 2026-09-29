# FIXME [Bug #22]: These tests expect check_guess() to return a BARE STRING,
#   but the implementation in app.py returns a TUPLE -> ("Too High", "message").
#   One of the two has to change. Recommended: have check_guess return only the
#   outcome and build the display message in app.py, which keeps the logic layer
#   free of UI strings.
#
# NOTE: these tests only ever check the OUTCOME LABEL, never the hint message.
#   That is precisely why they pass straight over Bug #1 (the swapped hint
#   messages). Worth remembering for the reflection: a green test suite does not
#   mean the app is correct, only that what you asserted on is correct.
#   Consider adding a test that asserts on the message text once Bug #1 is fixed.

from logic_utils import check_guess

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
