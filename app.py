import random
import streamlit as st

# ============================================================================
# FIXME [Bug #21]: These four functions belong in logic_utils.py.
#   tests/test_game_logic.py imports from logic_utils, not app.py, so pytest
#   cannot reach this code while it lives here. Move them over, then replace
#   this block with:  from logic_utils import (...)
#   Do this LAST, after the logic itself is correct.
# ============================================================================


def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    # FIXME [Bug #12]: Hard (1-50) is an EASIER range than Normal (1-100).
    #   Higher difficulty should widen the range, not shrink it.
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


# FIXME [Bug #16]: No range validation anywhere in here. A guess of 500 is
#   happily accepted on Easy (1-20). Consider accepting low/high as arguments
#   and rejecting out-of-range guesses with a clear message.
def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        # FIXME [Bug #17]: int(float("3.7")) silently truncates to 3 instead of
        #   telling the player to enter a whole number.
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


# FIXME [Bug #22]: This returns a TUPLE -> ("Win", "message"), but
#   tests/test_game_logic.py asserts against a bare string -> "Win".
#   Pick one shape and commit to it. Cleanest option: return only the outcome
#   from here and build the display message up in the Streamlit section.
def check_guess(guess, secret):
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        # FIXME [Bug #1]: The two hint messages are swapped.
        #   guess > secret means the player aimed too HIGH, so the hint should
        #   tell them to go LOWER - and vice versa.
        #   Note: the outcome LABELS ("Too High"/"Too Low") are already correct.
        #   Only the message strings are backwards, which is exactly why the
        #   pytest suite does not catch this bug.
        if guess > secret:
            return "Too High", "📈 Go HIGHER!"
        else:
            return "Too Low", "📉 Go LOWER!"
    except TypeError:
        # FIXME [Bug #3]: This fallback HIDES Bug #2 instead of surfacing it.
        #   When secret arrives as a string the comparison should fail loudly,
        #   but this quietly falls back to comparing TEXT:
        #       "9" > "100"  ->  True   (compares character by character)
        #   So hints come back wrong in a way that isn't even consistent.
        #   Delete this whole except block once Bug #2 is fixed - after that,
        #   nothing should ever reach it.
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📈 Go HIGHER!"
        return "Too Low", "📉 Go LOWER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        # FIXME [Bug #14]: Off-by-one. attempt_number is already 1-based
        #   (see Bug #7), so this +1 double-counts and underpays every win.
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIXME [Bug #13]: A WRONG guess ADDS 5 points on even attempts.
    #   "Too High" and "Too Low" are both misses and should be scored
    #   identically. Compare this branch with the "Too Low" branch below.
    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FIXME [Bug #4]: This guard means the secret is generated ONCE, ever.
#   Switching the difficulty dropdown recalculates low/high and updates the
#   sidebar caption, but never picks a new secret - so you can sit on Easy
#   (1-20) hunting a number like 87, which is unwinnable.
#   Repro: start on Normal, note the secret in Developer Debug Info, switch to
#   Easy, and compare the secret against the new range.
#   Hint: remember the current difficulty in session state too, and regenerate
#   the secret whenever it changes.
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIXME [Bug #7]: Should start at 0, not 1. Starting at 1 means the player
#   silently loses an attempt before ever guessing. Note the New Game handler
#   further down resets this to 0 (Bug #8) - the two disagree with each other.
if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

# FIXME [Bug #11]: "between 1 and 100" is hardcoded and ignores the difficulty.
#   The low/high variables are already computed above - use them.
# FIXME [Bug #10]: "Attempts left" is off by one, downstream of Bug #7.
st.info(
    f"Guess a number between 1 and 100. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

# FIXME [Bug #23]: This expander leaks the secret to the player.
#   Intentional for now - the README tells you to use it to find the secret
#   while debugging. Only remove or gate it if you do the stretch UI challenge.
with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

# FIXME [Bug #19]: The widget key changes with the difficulty, so switching
#   difficulty silently wipes whatever the player had typed.
raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIXME [Bug #6]: New Game never resets "status". After the st.rerun() below,
#   the status check further down still sees "won"/"lost", prints Game Over and
#   calls st.stop() - which halts the script BEFORE the submit handler. The
#   input box still renders (it is above the stop), so you can type, but
#   nothing happens. This is why New Game appears completely dead.
# FIXME [Bug #15]: New Game also fails to reset "score" and "history", so both
#   carry over from the previous round.
# FIXME [Bug #8]: Resets attempts to 0 here, but the initialiser above uses 1
#   (Bug #7). Pick one and make both agree.
if new_game:
    st.session_state.attempts = 0
    # FIXME [Bug #5]: Hardcodes randint(1, 100) and ignores low/high entirely,
    #   so New Game always breaks out of the selected difficulty's range.
    st.session_state.secret = random.randint(1, 100)
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    # FIXME [Bug #9]: The attempt is burned BEFORE the input is validated, so
    #   typing "abc" costs the player a turn. Move this after the parse check.
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        # FIXME [Bug #18]: Invalid input is appended to history as a raw string,
        #   mixing types in what should be a list of numeric guesses.
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # FIXME [Bug #2]: *** THE HEADLINE BUG ***
        #   On every even attempt the secret is converted to a STRING before
        #   being compared. That makes check_guess() raise TypeError, which
        #   drops it into the broken string-comparison fallback (Bug #3).
        #   Net effect: hints are wrong on attempts 2, 4, 6... in a way that is
        #   not even consistently inverted.
        #   Watch out: after you fix Bug #1 you will STILL get bad hints on even
        #   attempts because of this - do not assume your Bug #1 fix failed.
        #   The secret should stay an int for its entire lifetime.
        if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
