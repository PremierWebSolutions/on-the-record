# Limits

What a passing check proves, and what it does not. The checker prints the short version of this on every run. The gates are string checks over a short lexicon: they are strong against a value that is not on the cited line, and weaker against a value that is on the line but means something else.

## Proved by a pass

- Every quote is an unbroken, whole-word piece of the line it cites, and that line is spoken by the speaker the row names. A quote cannot start inside a word ("agreed" out of "disagreed") or hide behind an invisible character.
- Every action, decision and question quote is the whole sentence that holds its trigger, so a "not", a condition or a second clause cannot be cut off.
- Every owner is the speaker, the person who accepted on the next turn with an unambiguous phrase, a name that opens the sentence as the person addressed, or `not in source`.
- Every due date is words that were said in the same sentence, not preceded by a negation, never a calculated date.
- Every figure token is a whole figure exactly as it appears on its line, and every figure the pattern finds on the transcript is listed or accounted for.
- Every trigger phrase, question mark and figure the lexicon finds is used by a row of the matching kind or listed in `not_mapped` with a reason.
- The output has exactly the contract's fields, in order, no duplicate rows, nowhere to put a summary, and it names the transcript it was checked against.

## Not proved

- **The transcript is right.** Mishearings are kept as heard on purpose. A user can map them with a corrections file; the checker confirms each cited correction's heard form is a whole word in the quote, and the renderer shows the mapping as a user assertion. What the user says was meant is not verified.
- **The speaker labels are right.** Transcription tools attribute speech with a measurable error rate, and the translator trusts the labels it is given. A label word from the reserved list (Action, Note, Present…) is never a speaker; a real person called Will or Grace is fine, but a transcript that labels a heading "Summary:" and also has a speaker called Summary cannot be told apart from text alone.
- **A commitment with no trigger word was caught.** "You can leave that to us", "I've got that covered", "it's in hand" are not in the lexicon. The lexicon is English and deliberately short; a phrase it does not contain never reaches the worklist, so it can be missing from the output without any gate noticing. The list grew by nine phrases after a red-team pass found a real decision ("we're going with the cash basis") it could not see; it will still have gaps.
- **Reported speech and idioms are fully separated from real commitments.** The checks are heuristics: a reporting verb or quotation mark before the trigger in the same sentence, and a short idiom list ("I'll be honest", "we will see"). Speech reported without a reporting verb, or an idiom not on the list, passes as a commitment. A line filed as `not_a_commitment` or `reported_speech` stays visible in `not_mapped`, so a wrong call is misfiled, not hidden.
- **Sentence boundaries are a rule, not a reading.** A sentence ends at `.`, `?` or `!` followed by a space, a letter or the line end, except after a listed abbreviation ("Mr.", "Ltd.", "e.g.") or a single letter. An abbreviation not on the list still splits a sentence, and a line with no terminal punctuation is one sentence to its end.
- **Every `not_mapped` reason is the right call.** The checker proves each listed trigger is really on that line and of that kind, so nothing can be hidden; a real commitment could still be filed under the wrong reason, in plain view.
- **Spelled-out numbers were all listed.** Coverage is enforced for figures with digits. "Eighty-five thousand" may be listed but is not required.
- **A self-correction later in the call was linked.** "Sorry, zero-rated, not exempt" is not tied to the line it corrects.
- **An acceptance given later in the call was caught.** Only the very next turn by a different speaker counts, so a late acceptance leaves the owner `not in source`. That errs towards saying less.
