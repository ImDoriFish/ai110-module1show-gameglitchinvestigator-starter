import random
import streamlit as st

# FIXED [Bugs #20 / #21] - refactor into logic_utils.py:
#   I asked Claude to do this move for me after working through the earlier bugs
#   myself. It moved the four functions, added the import to app.py, and updated
#   the call site. I verified with pytest, which passed for the first time -
#   before the refactor the tests could not run at all, because they import from
#   logic_utils and the functions were still in app.py.
from logic_utils import (
    get_range_for_difficulty,
    get_attempts_for_difficulty,
    parse_guess,
    check_guess,
    hint_message,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit = get_attempts_for_difficulty(difficulty)

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FIXED [Bug #4] - the secret ignored the difficulty:
#   Claude explained that the `if "secret" not in st.session_state` guard runs
#   only once, so switching difficulty updated the range but never the secret.
#   It suggested a single `if` using `or`; I used if/elif instead because I found
#   it easier to read, and confirmed with Claude that both were correct. I
#   verified by switching Normal -> Easy -> Hard -> Normal and checking the
#   secret changed each time and stayed inside the range shown in the sidebar,
#   and that it did NOT change when I submitted a guess.
if "secret" not in st.session_state:
    st.session_state.difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
elif st.session_state.difficulty != difficulty:
    st.session_state.difficulty = difficulty
    st.session_state.secret = random.randint(low, high)

# FIXED [Bug #7]: Claude pointed out that attempts started at 1 instead of 0, so the player silently lost
# an attempt before guessing. I fixed it by changing the initial value to 0, which also resolved Bug #8 since New Game already used 0.
# I manually tested it by restarting the app and checking the info bar showed 8 attempts on Normal, then 7 after one guess.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

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


if new_game:
    #FIXED [Bug #6]: Claude explained that New Game reset attempts and secret but never status, so after
    # st.rerun() the status check further down still saw "won" or "lost" and called st.stop().
    # I fixed it by adding st.session_state.status = "playing" to the New Game block.
    # I manually tested it by losing a game on purpose, then pressing "New Game" and guessing again.
    st.session_state.status = "playing"
    st.session_state.attempts = 0

    # FIXED [Bug #15]: Claude pointed out that New Game reset status, attempts and secret but left score and
    # history from the previous round, so a new game started with the old score and old guesses still showing.
    # I fixed it by adding st.session_state.score = 0 and st.session_state.history = [] to the New Game block.
    # I manually tested it by making a few wrong guesses, pressing "New Game", and checking Developer Debug Info showed score 0 and an empty history.
    st.session_state.score = 0
    st.session_state.history = []
    # FIXED [Bug #5]: Claude pointed out that this line hardcoded randint(1, 100) even though low
    # and high were already computed from the current difficulty further up. I fixed it by replacing (1, 100) with (low, high).
    # I manually tested it by changing the difficulty and press "New Game".
    st.session_state.secret = random.randint(low, high)
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    # FIXED [Bug #9]: Claude pointed out that the attempt was counted before the input was validated, so typing
    # something like "abc" showed an error and still cost the player a turn. I fixed it by moving the increment into
    # the else branch so only a valid guess counts, keeping it first so update_score still gets the right attempt number.
    # I manually tested it by submitting "abc" and checking Attempts left did not change, then submitting a real number.
    

    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIXED [Bug #18]: Claude pointed out that invalid input was still appended to history, so the list mixed numbers
        # and junk text like [45, "abc", 60] even though history is meant to hold guesses only. I fixed it by removing the
        # append from the error branch, which matches the Bug #9 fix where invalid input no longer costs an attempt either.
        # I manually tested it by submitting "abc" and checking Developer Debug Info showed no new history entry.
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIXED [Bug #2] - the secret was cast to a string:
        #   I reported to Claude that my Bug #1 fix still showed the wrong hint.
        #   It traced the cause to a second bug that stringified the secret on
        #   even attempts, and explained that the TypeError this caused was
        #   routing execution past my fixed code entirely. I deleted the if/else
        #   so the secret stays an int, and verified by making several guesses in
        #   a row and confirming the hints no longer alternated between right
        #   and wrong.
        secret = st.session_state.secret

        # FIXED [Bug #22] - check_guess returned a tuple:
        #   The provided tests assert against a plain string but the function
        #   returned (outcome, message). Claude suggested splitting it:
        #   check_guess returns the outcome only, and a new hint_message()
        #   supplies the text. I took that suggestion because it let the provided
        #   tests pass unmodified and made the hint messages testable - which was
        #   the exact gap that let my first Bug #1 attempt look correct when it
        #   wasn't.
        outcome = check_guess(guess_int, secret)
        message = hint_message(outcome)

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

# FIXED [Bug #24]: I found this one myself while testing - after submitting a guess the number did not show up in
# History until my NEXT guess, and "Attempts left" was one behind too. Claude explained that Streamlit runs the file
# top to bottom, and these two blocks used to sit ABOVE the submit handler, so they drew the screen before the guess
# updated attempts, score and history. I fixed it by moving both blocks below the submit handler so the values are
# changed first and drawn second. I manually tested it by submitting a guess and checking Attempts left dropped
# straight away and the number appeared in History immediately instead of one guess late.

# FIXED [Bug #11]: Claude pointed out that this line hardcoded "1 and 100" so it contradicted the sidebar
# whenever I picked a difficulty other than Normal. I fixed it by putting {low} and {high} in the f-string.
# I manually tested it by switching between Easy, Normal and Hard and checking the text matched the sidebar range.
st.info(
    f"Guess a number between {low} and {high}. "
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

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
