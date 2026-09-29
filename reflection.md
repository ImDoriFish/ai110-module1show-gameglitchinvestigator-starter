# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

  It looked completely normal. The UI was fine, nothing crashed, and the game ran. It was only once. I actually started playing that the logic bugs showed up, and they made it unplayable.

- List at least two concrete bugs you noticed at the start 
  The hints were backwards. I guessed 20, 10 and 40 and it kept telling me to go lower no matter
  which way I moved, so there was no way to close in on the answer.

  New Game did nothing. Once I lost, pressing it left me on the "Game over" screen and I could type a guess but submitting did nothing.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input            | Expected Behavior                       | Actual Behavior         | Console Output / Error |
|------------------|-----------------------------------------|-------------------------|------------------------|
|input 20, 10, 40, |It should give lower or higher           |Always give the inverse  | Wrong hint/suspected in|
|etc               | as the number change                    |hint                     |app.py,check_guess      |
|                  |                                         |                         |                        |
|input New Game,   |It should start a new game and           |Doesn't start a new game |Doesn't start the game  |
|10.               |read in new input for new game           | or read in input        |(app.py, l.130)         |
|                  |                                         |                         |                        |
|input easy, normal|The text: "Guess a number between"       |It doesn't change always |the error maybe in app.py|
|difficult.        |should change according to the difficulty|state "1 to 100"         |l.109                    |



---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

  I used Claude, running in Claude Code inside VS Code, so it could read the actual project files rather than just code I pasted in. I mostly used it to locate bugs and explain why they happened, and I made the fixes myself so I understood what I was changing.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

  After I fixed the swapped hint messages in `check_guess` (Bug #1), the game still gave me the wrong hint, I guessed 50 against a secret of 49 and it told me to go higher. I was about to undo my fix, but Claude pointed out a second bug I had not logged: on even-numbered attempts the code ran `secret = str(st.session_state.secret)`, turning the number into text. Comparing an int to a string raised a `TypeError`, which sent execution into a `try/except` block that compared the values alphabetically instead, so my corrected code never ran on those turns. I verified it by making several guesses in a row and watching the hint alternate between right and wrong.

- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

  For Bug #16, `parse_guess` accepted any number regardless of the difficulty's range, so a guess of 500 was legal on Easy (1-20). Claude suggested adding `low` and `high` as optional parameters with default values of `None`, and skipping the range check when they were not supplied, so that existing callers would keep working. I did not accept that. A default that silently skips validation means a caller can forget to pass the range and get no error at all. I made `low` and `high` required instead, which forces every caller to be explicit. Before changing it I checked how many callers existed and found only one, in `app.py`, and
  no tests called it at all, so making the parameters required broke nothing. I verified my version with new tests, includin `test_the_same_guess_can_be_legal_on_one_difficulty_and_not_another`,

  A second, smaller example: Claude's original bug list said Hard's range was too small and should be widened. When I looked at the attempt limits, Hard had 1-50 with only 5 attempts, and binary search needs 6 guesses for a range of 50, so Hard was already unwinnable, and widening the range would have made it worse. The real problem was that the range and the attempt limit lived in different files and nothing checked them against each other. I retuned both and wrote `test_every_difficulty_is_winnable` to encode the rule, and confirmed it fails against the old values. This taught me that the AI's bug list needed verifying too, not just the code it pointed at.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

  Early on I would change something, try it once, and call it done. That failed me on Bug #1, where the hint looked right on one guess but the label underneath was wrong, and again on Bug #2, where my fix was correct but a second bug hid it. After that I started checking the same thing several times instead of once. For Bug #2 the real proof was that the hints stopped alternating, not that one guess was right.

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.

  `test_wrong_guesses_always_lose_points` loops over attempt numbers 1 to 10 and checks a wrong guess always costs 5 points. The old code only added points on even attempts, so a single call with attempt 1 would have passed. Writing the loop showed me that a test can pass and still miss the bug if it only checks one case.

- Did AI help you design or understand any tests? How?

  Yes. The three tests we were given only check the outcome label, never the hint message, which is why they passed against the broken code in Bug #1. Claude pointed that out and suggested splitting `check_guess` so the message came from its own function and could be tested. I also cut one test Claude wrote, `test_check_guess_returns_a_plain_string`, because one of its assertions could never fail and the existing tests already caught the same thing.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

  Every time you click anything, Streamlit runs the whole file again from line 1. So a normal variable is useless, it gets rebuilt every click. `st.session_state` is a box that survives the rerun, which is why the secret number lives in there.

  Two things caught me out. First, order matters: I was drawing the score and history near the top of the file and updating them near the bottom, so the screen was always one guess behind. Moving the display below the update fixed it. Second, the rerun only reloads `app.py`. Imported files like `logic_utils.py` stay cached, so after editing that file I got a `TypeError` on code that was actually correct and had to restart the server.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

  Marking every bug in the code with a numbered `FIXME` before fixing anything. It meant I always knew what was left, I could fix one thing at a time instead of changing five things and losing track, and searching for `FIXME` gave me my to-do list.

- What is one thing you would do differently next time you work with AI on a coding task?

  I would test more instead of taking the AI's word that a fix is done. Bug #1 turned out to be tied to Bug #2, so when I fixed #1 nothing changed on screen and I had to go back and trace where the real problem was. That confused me a lot and I nearly undid a fix that was actually correct. Having Claude flag every bug in the code was useful, but next time I would ask it to group them by category and tell me which ones are connected, so I know upfront that fixing one might not show any result until I fix the other. I would also check its analysis and not just its code, since its bug list said Hard's range was too small when Hard was actually unwinnable and widening it would have made it worse.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

  I would not trust it completely anymore. Instead of pasting in whatever it gives me, I read it
  first and make sure I understand how it fits with the rest of the code, then apply it myself, so that if something goes wrong later I actually know where to look.

