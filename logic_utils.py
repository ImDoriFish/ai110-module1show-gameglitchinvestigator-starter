# ============================================================================
# FIXME [Bug #20]: Every function below is an unimplemented stub, so
#   tests/test_game_logic.py currently fails at import/call time with
#   NotImplementedError.
#
#   These are the destinations for the four functions currently sitting in
#   app.py (see Bug #21). Fix the logic in app.py FIRST, then move the working
#   versions here - that way, if a test breaks after the move, you know the
#   move caused it rather than the logic.
#
#   Order to work in:
#     1. Fix Bugs #1, #2, #3 in app.py  (hints and the string-cast)
#     2. Fix the state bugs #4, #5, #6  (New Game / difficulty range)
#     3. Move these four functions here and import them in app.py
#     4. Run pytest and settle Bug #22 (tuple vs bare string return)
# ============================================================================


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    # See also Bug #12: Hard is currently an easier range than Normal.
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    # See also Bug #16 (no range check) and Bug #17 (silent decimal truncation).
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIXME [Bug #22]: This docstring promises a tuple, but the tests assert
    #   against a bare string. Whatever you decide, make the docstring, the
    #   implementation and the tests agree.
    # See also Bug #1 (swapped messages) and Bug #3 (string-comparison fallback).
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    # See also Bug #13 (wrong guess adds points) and Bug #14 (off-by-one).
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")
