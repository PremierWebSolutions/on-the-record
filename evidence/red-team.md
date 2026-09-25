# Red team

Before submission the checker was attacked by five independent agents and one outside reader, each told: forge an output that contains an invented, altered or misattributed value and still passes every gate. The forgeries they produced are the reason most of the gates in `verify/check.py` exist in their current form. Every hole below is closed and carries a planted fixture in `verify/fixtures/` that must fail through the gate named; `python3 verify/check.py --selftest` proves it.

## Round 1: holes that passed the checker as first built

| # | Forgery that passed | Why it is disqualifying | Closed by |
|---|---|---|---|
| 1 | Request owner "June", taken from "the 31st of June, can you confirm that?" | An owner nobody named | owner: a named owner must open the sentence as the person addressed ("Tom, can you…") or come from an acceptance |
| 2 | Owner "Sarah" from "Can you send Sarah the invoice?" (a participant mentioned, not asked) | A task credited to someone never asked | same |
| 3 | Owner "invoice" from "Can you sort the invoice, please?" | Not even a person | same |
| 4 | "Yes, the office is open." and "Yes, but I can't do that" counted as accepting a request | A refusal or an unrelated reply recorded as acceptance | owner: bare yes/okay removed from the acceptance list; refusal markers reject |
| 5 | `Tom said, "I'll send the file by Friday."` booked as the speaker's own commitment | Reported speech credited to the wrong person | trigger: reporting frames and quotation marks before a trigger |
| 6 | "I'll be honest, it was a tough year" recorded as a committed action | An idiom promoted to a task | trigger: idiom list |
| 7 | Decision "agreed on the merger…" sliced from "We **dis**agreed on the merger" | The opposite of what was said | trace: quotes must start and end on word boundaries; a trigger must be a genuine occurrence on the line |
| 8 | "dis​agreed" with an invisible zero-width character inside the word | Same, hidden | norm() strips zero-width characters |
| 9 | Decision quote starting after "We haven't " | A non-decision recorded as one | trigger: action and decision quotes are the whole sentence |
| 10 | Question "going ahead with the launch…?" sliced from "Are we not going ahead…?" | The question inverted | trigger: question quotes are the whole sentence |
| 11 | Due "by Friday" from "not by Friday, by Monday" | The date the speaker ruled out | due: not preceded by a negation, same sentence as the trigger |
| 12 | Due "by Friday" borrowed from an unrelated later sentence | A date the commitment never carried | due: same sentence |
| 13 | "I'll send the draft. Can you review it?" recorded as one committed action | The request vanishes with no trace | coverage: a row only accounts for triggers of its own kind |
| 14 | Figure token "12" from "£12,500", "£85" from "£85,000", "1,412" from "£1,412.50" | A number changed by orders of magnitude | coverage/trace: a token must be a whole figure on its line |
| 15 | ".5%" indexed as "5%", "-£1,250" as "£1,250", "€12 500" as "€12" | The figure pattern itself altered numbers | triggers.md: pattern extended |
| 16 | Meeting date taken from a line spoken mid-call | Rule 16 unenforced | shape: header lines only |
| 17 | `source.file` naming a different transcript than the one checked | A run validated against an easier input | shape/matrix: file names must agree |
| 18 | A correction cited because "I" is a substring of "I'll" | An uncited claim riding on a passing run | corrections: whole-word match; corrections rendered as user assertions |
| 19 | The same figure row twice | Padding | shape: no duplicate rows |
| 20 | "Action: I'll send the statements" inside a turn parsed as a speaker called "Action" | Words credited to a person who does not exist | parser: reserved label words |
| 21 | "The Comptroller and Auditor General: …" (six words) credited to the previous speaker | Wrong person | parser: label cap raised to eight words |
| 22 | Zoë, José, Ó Briain, 王芳, SPEAKER_00 not recognised as speakers | Their words merged into the previous speaker | parser: Unicode-aware labels |
| 23 | Two `<v>` tags in one Teams cue credited to the first | Wrong person | parser: one line per voice tag |
| 24 | A `|` in a speaker label breaking the numbered format | Label text leaks into speech | parser: `|` replaced by `/` |

Forgeries the checker caught before any fix, for contrast: a quote credited to the other speaker, the right quote on the neighbouring line, a hedge upgraded to a commitment, a condition cut off a promise, a calendar date worked out from "by the 20th", a summary field, a figure normalised, a quote spliced across two speakers, a correction cited with no corrections file.

## Round 2: fresh agents attacking the patched checker

Five new agents, five lanes: faithful outputs the new gates wrongly reject, sentence-boundary abuse, the new owner rule, lexicon gaps, and the parser again. Their forgeries and the faithful outputs they built are the fixtures named below.

| # | Finding | Kind | Closed by |
|---|---|---|---|
| 25 | "Mr. Osei, I will send the deposit by Friday." quoted from after "Mr.", dropping "Unless the funding comes through" | forgery passed | trigger: a full stop after an abbreviation or a single letter does not end a sentence (`fail-abbreviation-cut`, `pass-abbreviation-whole`) |
| 26 | "I won't confirm with Hartley Ltd. until they reply, but I'll email them anyway." rejected as two sentences; only the truncated half was accepted | faithful output failed | same |
| 27 | "by Friday.We'll finalise" with no space: two faithful rows rejected as a mid-word splice | faithful output failed | trace and trigger: a full stop with no space after it still ends a sentence (`pass-runon-two-sentences`) |
| 28 | Owner "Well" from "Well, can you send the invoice?" and "Tom at the bank" from "Tom at the bank, can you confirm…" | forgery passed | owner: a vocative must look like a name, one to three capitalised words, not a filler or a description (`fail-owner-filler`, `fail-owner-descriptive`) |
| 29 | "we're going with the cash basis" on the real accountant call: a restated decision the lexicon could not see, so the blind run dropped it and passed | silent omission | triggers.md: nine phrases added (`i'm on it`, `that's on me`, `count me in`, `leave it to me`, `we're going with`, `settled on`…); the old run now fails coverage (`fail-decision-dropped`) |
| 30 | Google Meet and Otter headers with "10:03 AM" or milliseconds, Rev and Fireflies "Name (00:00:03):", and dash-bulleted turns all credited to the previous speaker | parser | otr_core.py: three more label shapes, each with a format test |

Confirmed not exploitable in round 2: a vocative before a commitment ("Tom, I'll do it myself") is still owned by the speaker; a title in a vocative ("Mr Hartley, can you…") passes; "no later than Friday" is not read as a negation; an acceptance can only be the next turn by a different speaker, so no other line can be cited; real names on the reserved-label list (a speaker called Will or Grace) still parse.

## What the two rounds cost

Eleven attackers, over two rounds, found thirty holes in a checker that passed its own planted fixtures throughout. Every one is closed with a fixture, and the four published runs were made blind again under the final rules. The count is the honest measure of how far a string checker can be trusted, and it is why [LIMITS.md](../LIMITS.md) is as long as it is.

## What this does not prove

Thirty findings by eleven attackers is evidence, not a proof. The gates are string checks over a lexicon, and [LIMITS.md](../LIMITS.md) lists the classes a passing run still cannot rule out.
