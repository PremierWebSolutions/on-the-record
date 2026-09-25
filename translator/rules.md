# Rules

Follow these in order. Each rule is checked by a named gate in `verify/check.py`, shown in brackets.

## Before you start

1. **Work from numbered lines.** Cite lines only by their `L####` id. If the input is not numbered, number it by [reference/input-format.md](reference/input-format.md) first, and cite those numbers.
2. **Your worklist is the trigger index.** If the input ends with a `# TRIGGER INDEX`, every entry in it is on your worklist. If it does not, build the list yourself: every whole-word match of a phrase in [reference/triggers.md](reference/triggers.md), every question mark, and every match of the figure pattern. When two phrases overlap, the longer one wins. *(coverage)*

## Every row

3. **Quote, don't paraphrase.** `quote` is an exact, unbroken piece of the text on the line you cite. Keep the transcript's spelling, grammar, filler words and mishearings. You may start a quote late and leave out what comes after, but you may not change or reorder any words. An action or decision quote runs at least from its trigger to the end of that sentence, so a condition such as "if the bank gets back to me" is never cut off. A quote never spans two lines. *(trace, trigger)*
4. **Copy the speaker.** `speaker` is the label on the cited line, character for character. *(speaker)*
5. **Missing means `not in source`.** When the transcript does not say it, the field is exactly `not in source`. Never leave a field out, never write null, never guess. *(shape)*

## Actions

6. **Kind comes from the words.** A line with a `committed` phrase is a commitment, a `requested` phrase is a request, a `tentative` phrase is a hedge. If a hedge phrase is anywhere in the quote, the kind is `tentative`. `trigger` is the exact list entry that matched. *(trigger)*
7. **Committed and tentative actions belong to the speaker.** `owner` equals `speaker`. For "we'll", the owner is still the person who said it. *(owner)*
8. **A request belongs to whoever took it.** If the very next line by a different speaker accepts it (a phrase from the acceptance list), fill `accepted_line` and `accepted_quote` from that line and make that speaker the owner. Otherwise, if the request names its addressee on the same line ("Tom, can you…"), the owner is that name exactly as spelled. Otherwise the owner is `not in source`. *(owner)*
9. **Due dates are kept as said.** `due_as_said` is a verbatim piece of the quote or the acceptance ("by Friday", "in about three weeks"), or `not in source`. Never convert it to a calendar date. *(due)*
10. **Implied next steps are not actions.** "The accounts need filing at some point" has no trigger and nobody taking it on. It produces no action row.

## Decisions, figures, questions

11. **A decision needs a decision phrase** on its line, inside its quote. *(trigger)*
12. **Every figure the pattern finds is listed**, with `token` copied exactly as transcribed: "85k" stays "85k", "£85,000" stays "£85,000". You may also list a spelled-out number ("eighty-five thousand"). Never convert, total or round. *(coverage, trace)*
13. **A question row quotes the question, including its question mark.** Whether it was answered is not recorded. That is a judgement. *(trigger)*

## Accounting for everything

14. **Nothing on the worklist is dropped.** Each entry is either inside a row's quote on that line, or listed in `not_mapped` with the trigger exactly as the index shows it and one reason from the closed list: `not_a_commitment` ("I'll be honest"), `hypothetical` ("if we registered, we'd…"), `reported_speech` ("HMRC said they will…"), `repeat` (the same thing already recorded, with `see_line` pointing at it), `not_a_decision`, `rhetorical`, `inaudible`, `label_or_reference`, `procedural` (running the meeting: "we will move on to…"). `see_line` is `not in source` unless the reason is `repeat`. *(coverage)*
15. **Rows run in transcript order** and ids count up from 1 in each section: A1, A2… D1… F1… Q1… *(shape)*
16. **`meeting.participants` is every speaker label** in order of first appearance, excluding `(none)`. `title` and `date` are quoted from the transcript's own header or speech, or `not in source`. *(shape)*

## Corrections (optional)

17. **Only the user can correct the transcript.** If the user supplies a corrections file (`heard => meant`, one per line, numbered C001, C002… in order), a row whose quote contains a heard form may list that correction's id in `corrections`. The quote itself still shows the words as heard. Without a corrections file, every `corrections` list is empty. *(corrections)*

## Output

18. **Reply with the JSON object only**, in the key order of the schema. No commentary, no summary, no markdown around it.
