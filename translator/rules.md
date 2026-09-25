# Rules

Follow these in order. Each rule is checked by a named gate in `verify/check.py`, shown in brackets.

## Before you start

1. **Work from numbered lines.** Cite lines only by their `L####` id. If the input is not numbered, number it by [reference/input-format.md](reference/input-format.md) first, and cite those numbers.
2. **Your worklist is the trigger index.** If the input ends with a `# TRIGGER INDEX`, every entry in it is on your worklist. If it does not, build the list yourself: every whole-word match of a phrase in [reference/triggers.md](reference/triggers.md), every question mark, and every match of the figure pattern. When two phrases overlap, the longer one wins. *(coverage)*

## Every row

3. **Quote, don't paraphrase.** `quote` is an exact, unbroken piece of the text on the line you cite, beginning and ending on a word boundary — never carved out of the middle of a word (`agreed` is never quoted starting inside `disagreed`, however that word is spelled). Keep the transcript's spelling, grammar, filler words and mishearings; you may not change or reorder any words. An action, decision or question quote is the **whole sentence** holding its trigger (or its `?`): from the start of that sentence to its end. Not starting late — which could drop a negation just before the trigger ("we **haven't** agreed…") — and not stopping early — which could drop a condition ("…if the bank gets back to me"). A quote never spans two lines. A sentence runs from the line start, or from just after the previous full stop, question mark or exclamation mark, to the next one. A full stop after an abbreviation ("Mr.", "Ltd.", "e.g.") or a single letter does not end a sentence, and a full stop with no space after it still does. *(trace, trigger)*
4. **Copy the speaker.** `speaker` is the label on the cited line, character for character. *(speaker)*
5. **Missing means `not in source`.** When the transcript does not say it, the field is exactly `not in source`. Never leave a field out, never write null, never guess. *(shape)*

## Actions

6. **Kind comes from the words.** A line with a `committed` phrase is a commitment, a `requested` phrase is a request, a `tentative` phrase is a hedge. If a hedge phrase is anywhere in the quote, the kind is `tentative`. `trigger` is the exact list entry that matched a genuine, word-boundary occurrence on that line — never a fragment of a longer word; if more than one phrase of that kind is in the quote, use the first. *(trigger)*
7. **Committed and tentative actions belong to the speaker.** `owner` equals `speaker`. For "we'll", the owner is still the person who said it. *(owner)*
8. **A request belongs to whoever took it.** If the very next line by a different speaker contains an unambiguous acceptance — a phrase from the acceptance list, or a committed-list phrase ("Yes, I'll send it today") — and no refusal marker ("can't", "won't", "unable"…), fill `accepted_line` and `accepted_quote` from that line and make that speaker the owner. A bare "yes"/"okay" accepts nothing on its own: "Yes, the office is open" and "Yes, but I can't do that" are both not acceptances. Otherwise the owner is `not in source` — **unless** the request opens with its addressee's name as a vocative: the quote (always the whole sentence, per rule 3) starts with that name followed by a comma (`Tom, can you…`), spelled exactly as the transcript has it. A name anywhere else in the sentence — a bystander ("send **Sarah** the invoice"), the object of the request ("sort the **invoice**"), a date ("the 31st of **June**, can you…") — is never an owner. The name must look like a name: one to three capitalised words, never a filler such as "Well" or a description such as "Tom at the bank". *(owner)*
9. **Due dates are kept as said.** `due_as_said` is a verbatim piece of the quote or the acceptance ("by Friday", "in about three weeks"), or `not in source`. Never convert it to a calendar date. *(due)*
10. **Implied next steps are not actions.** "The accounts need filing at some point" has no trigger and nobody taking it on. It produces no action row.

## Decisions, figures, questions

11. **A decision needs a decision phrase** on its line, inside its quote. If the quote holds more than one, `trigger` is the first. A second speaker agreeing to the same decision is its own row. *(trigger)*
12. **Every figure the pattern finds is listed**, with `token` copied exactly from the line (the index shows the same text): "85k" stays "85k", "£85,000" stays "£85,000". You may also list a spelled-out number ("eighty-five thousand"). Never convert, total or round. *(coverage, trace)*
13. **A question row quotes the question, including its question mark.** Whether it was answered is not recorded. That is a judgement. The quote is the whole sentence that holds the question mark, so "Are we not going ahead?" cannot become "going ahead?". *(trigger)*

## Accounting for everything

14. **Nothing on the worklist is dropped.** Each entry is either inside a row's quote on that line, or listed in `not_mapped` with the trigger exactly as the index shows it and one reason from the closed list: `not_a_commitment` (a trigger used for something other than taking on a task: "I'll be honest", "we will see", "we'll need his UTR"), `hypothetical` ("if we registered, we'd…"), `reported_speech` ("HMRC said they will…"), `repeat` (the same thing already recorded, with `see_line` pointing at it), `not_a_decision`, `rhetorical`, `inaudible`, `label_or_reference`, `procedural` (running the meeting: "we will move on to…"). `see_line` is `not in source` unless the reason is `repeat`. A committed, requested and tentative trigger on the same line are tracked separately: a row of one kind does not account for a trigger of a different kind on the same line — "I'll email the accountant and can you chase Tom?" needs two rows, one committed and one requested, not one. `accepted_quote` is the exception: it legitimately reuses wording of any kind, since an acceptance may itself contain a committed phrase. *(coverage)*
15. **Rows run in transcript order** and ids count up from 1 in each section: A1, A2… D1… F1… Q1… *(shape)*
16. **`meeting.participants` is every speaker label** in order of first appearance, excluding `(none)`. `title` and `date` are quoted only from the unlabelled header lines before anyone speaks (speaker `(none)`), or are `not in source`. Something said during the call is not a title. *(shape, speaker)*

## Corrections (optional)

17. **Only the user can correct the transcript.** If the user supplies a corrections file (`heard => meant`, one per line, numbered C001, C002… in order), a row whose quote contains a heard form may list that correction's id in `corrections`. The quote itself still shows the words as heard. Without a corrections file, every `corrections` list is empty. *(corrections)*

## Faithfulness beyond the words

18. **An idiom is never a commitment, request or hedge.** If the trigger's own occurrence in the quote falls inside one of the fixed phrases in the idiom list in [reference/triggers.md](reference/triggers.md) ("I'll be honest", "we'll see"…), it produces no action row — file it in `not_mapped` as `not_a_commitment`. The list is short and known to be incomplete. *(trigger)*

19. **Reported speech is not the speaker's own.** If a reporting verb ("said", "told", "asked"…) sits between the start of the sentence and the trigger, or the trigger sits inside quotation marks, the words belong to whoever is being quoted, not to the speaker of the line — file it in `not_mapped` as `reported_speech`, never as a row owned by the line's own speaker. *(trigger)*

20. **A figure is cited whole.** `token` is never a fragment of a longer figure — not a stray digit, a truncated thousands group, nor a dropped currency symbol, minus sign or decimal point. A spelled-out token is a whole word in its quote. *(trace)*

21. **A title or date comes from before anyone speaks.** `meeting.title` and `meeting.date` must cite a line that comes before the first line carrying a real speaker label — a header-shaped cue that happens to fall after someone has already spoken is not the header. *(shape)*

22. **`source.file` names the transcript actually being checked.** It must match the input file this record is checked against, and — for a filed run — the run's own filename, so a run cannot claim an easier transcript than the one it is named for. *(shape)*

23. **No two rows are exact duplicates.** The same section, line, quote and trigger (or token, for a figure) recorded twice is one finding filed twice, not two. *(shape)*

24. **`due_as_said` is not pulled across a negation.** It is never taken from words immediately preceded by "not", "n't" or "never" ("not by Friday, by Monday" — the due date is "by Monday"), and it sits in the same sentence as the words that gave it. *(due)*

## Output

25. **Reply with the JSON object only**, in the key order of the schema. No commentary, no summary, no markdown around it.
