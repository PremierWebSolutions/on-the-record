# Deliberate traps in the test inputs

All people and businesses are fictional. Each row cites the exact line text.

## accountant-yearend-call.txt

| Trap | Line text | Correct behaviour |
|---|---|---|
| Xero → "zero" | "it's all in zero" | Keep "zero", never correct to "Xero" |
| Supplier misheard | "Haldane Timber" (elsewhere "Halden Timber") | Quote each spelling as transcribed |
| Nonexistent date | "the 31st of June" | Quote verbatim, don't resolve to a real date |
| Self-correction | "that's exempt" → "sorry, zero-rated, not exempt" | Only "zero-rated" is the fact |
| Hedged commitment | "I'll try to get the mileage log over by the end of next week" | Action, flagged hedged |
| Firm commitment | "I'll send you the bank statements by Friday" | Action, due "by Friday" |
| Unaccepted request | "Could you check whether the van was bought on finance?" | Request only, owner "not in source" |
| Accepted request | "Can you send me the payroll summary?" → "Yes, I'll do that today" | Action, owner = accepter, due "today" |
| Addressed request | "Tom, can you dig out the invoice from the stove supplier?" | Owner = Tom, from the vocative |
| "We'll" commitment | "We'll get the draft accounts to you in about three weeks" | Action, owner = speaker/firm |
| "I'll" non-commitment | "I'll be honest, it was a tough year" | Not an action |
| Reported speech | "HMRC said they will send a new code" | Not a commitment; exclude |
| Hypothetical | "If we registered for VAT we'd have to charge twenty percent" | Conditional, not a decision |
| Decision | "agreed, let's go with the cash basis" | Decision, verbatim |
| Figures, 3 forms | "about 85k" / "£85,000" / "eighty-five thousand pounds" | Keep each quote separate |
| Percentage, 2 forms | "twenty percent" / "20%" | Keep both verbatim |
| Decimal | "£1,412.50" | Quoted exactly |
| Mileage | "4,200 miles" | Quoted exactly |
| Answered question | "Is that up on last year?" → "closer to seventy" | Question and answer both captured |
| Unanswered question | "Does the roof count as a repair or an improvement for tax?" | No answer exists; none invented |
| Implied-only step | "The accounts need filing at some point" | NOT an action — no owner, no acceptance |

## project-kickoff.vtt

| Trap | Line text | Correct behaviour |
|---|---|---|
| Firm commitment | "We'll send the sitemap by Wednesday" | Action, due "by Wednesday" |
| Firm commitment | "first full designs ready by the end of the month" | Action, due "end of the month" |
| Tentative | "I might be able to get a first working draft over by Friday" | Tentative, not firm |
| Unaccepted request | "Could someone loop in our copywriter this week...?" | Request only, owner "not in source" |
| Accepted request | "can you send over the moodboard by Wednesday?" → "Yes, by Wednesday" | Action, owner = Nadia |
| Decision | "let's go with the current host then, no migration needed" | Decision |
| Budget, 2 forms | "£12,500" and "12.5k" | Kept verbatim |
| Percentage | "10% contingency" | Quoted verbatim |
| Two-line cue | Cue 23 (Ben Farrell) | One utterance, one speaker, one citation |
| Unattributed speaker | Cue 28, `<v Unknown speaker>` | Speaker = "Unknown speaker", never guessed |

## quick-checkin.txt

No commitments, decisions, figures or questions exist, by construction. Every register section must still appear, empty — nothing invented to fill it.
