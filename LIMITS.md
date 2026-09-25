# Limits

What a passing check proves, and what it does not. The checker prints the short version of this on every run.

## Proved by a pass

- Every quote is an unbroken piece of the line it cites, and that line is spoken by the speaker the row names.
- Every owner is either the speaker, the person who accepted on the next turn, a name written on the line, or `not in source`.
- Every due date is words that were said, never a calculated date.
- Every action and decision quote runs to the end of its sentence, so a condition cannot be cut off.
- Every trigger phrase, question mark and figure the lexicon finds is either used in a row or listed in `not_mapped` with a reason.
- The output has exactly the contract's fields, in order, with nowhere to put a summary.

## Not proved

- **The transcript is right.** Mishearings are kept as heard on purpose. A user can map them with a corrections file, which is cited.
- **The speaker labels are right.** Transcription tools attribute speech with a measurable error rate, and the translator trusts the labels it is given.
- **A commitment with no trigger word was caught.** "That one's on me" or "leave it with Sarah" are not in the lexicon. The lexicon is English and deliberately short.
- **Every `not_mapped` reason is the right call.** The checker proves each listed trigger is really on that line, so nothing can be hidden, but a real commitment could be filed as `not_a_commitment`. It would be visible in the output, not missing from it.
- **Spelled-out numbers were all listed.** Coverage is enforced for digits. "Eighty-five thousand" may be listed but is not required.
- **A later correction was linked.** "Sorry, zero-rated, not exempt" is not tied to the line it corrects.
- **An acceptance given later in the call was caught.** Only the very next turn by a different speaker counts, so a late acceptance leaves the owner `not in source`. That errs towards saying less.
