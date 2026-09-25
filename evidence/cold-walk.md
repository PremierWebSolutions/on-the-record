# Cold walk

A reader who has never seen the repo opens the README and tries to translate a transcript and check the result. The predictions were written and committed before the walk; the walk and the fixes are added underneath.

## Predictions (committed before the walk)

1. The reader will not know which file to give a Claude project: the whole repo or `translator/`.
2. The reader will run the checker on the raw transcript without knowing it numbers the file itself, and will worry the line ids won't match.
3. `not_mapped` will read as "errors" rather than "triggers deliberately not used".
4. The reader will expect a summary and wonder whether the output is incomplete without one.
5. The reader will not find the real input among the constructed ones.

## Walk

**Who walked:** a fresh Claude Haiku 4.5 agent, briefed as a bookkeeper who runs commands but does not program, told to start from README.md and open other files only when sent there. This is an agent walk, not a human one, and a smaller model was chosen on purpose as the less forgiving reader. No human stranger walk was run before the deadline.

**Commands:** step 1 (number), step 3 (check) and step 4 (render) all worked first time from the README's own commands. Step 2 needs a Claude project, so the walker was handed an existing run as a colleague's note.

**Predictions against what happened:** none of the five predicted confusions occurred. The walker named `translator/` as the folder to give a project, said the checker takes the original transcript, read `not_mapped` as deliberate rather than errors, understood the missing summary as intended, and identified the real input. The confusions it did have were different:

1. The README's example file read as possibly illustrative rather than something to run as-is.
2. Step 2 said to save `note.json` without saying where.
3. It knew which input was real but not how to check the claim.
4. The checker already prints its limits, so the pointer to LIMITS.md looked redundant.
5. The CLI shortcut sat inside step 2, which muddled the steps for someone without the CLI.

## Fixes

1. The steps now open with "Try it on the included accountant call first, then swap in your own transcript's path."
2. Step 2 says to save the reply as `note.json` in the repository root, which is git-ignored.
3. The README now says SOURCE.md gives Parliament's URL and the file's SHA-256, so a reader can compare the two.
4. The limits line now says the checker prints a short list and LIMITS.md has the full one.
5. The CLI shortcut moved out of step 2 into its own line after the steps.

Predictions were committed in `a2ed329`; the walk and fixes are in the commit after it.
