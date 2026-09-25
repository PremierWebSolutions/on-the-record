# Deliberate traps in the test inputs

Each row names the line, what a careless note-taker does with it, and what the contract requires. People and businesses in the constructed files are fictional. Line ids refer to the numbered files beside each input.

## pac-hmrc-2026-05-18.txt (real)

| Line | Trap | Contract |
|---|---|---|
| L0008 | "we will have to write to you to give you the precise number" | Committed action, owner John-Paul Marks, due `not in source`. |
| L0008, L0010 | "in the hundreds" is all the witness gives | No number appears anywhere. The figure pattern does not match it and nothing is filled in. |
| L0009 | "Could you let us have the figures, then?" | Requested action. The next turn by another speaker, "We will give you the precise figures.", takes it on with a commitment phrase, so it is the acceptance: owner John-Paul Marks, `accepted_line` L0010. |
| L0006 | "from September we will launch three specific test and learns" | Committed, owner Nicole Newbury, due "from September". No year is added. |
| L0004 | "£10 billion in ’29-30" | Figure "£10 billion" as printed. The year is not reformatted. |
| L0017 | "We expect our yield to increase" | An expectation, not a commitment. No trigger, no action. |
| L0015 | "We will see." | Trigger present, not a commitment: listed in `not_mapped`. |

## accountant-yearend-call.txt (constructed)

| Line | Trap | Contract |
|---|---|---|
| L0007, L0031 | "zero" for the software Xero | Any quote keeps "zero". Only a user corrections file can map it, and then it is cited. |
| L0017 | "Haldane Timber", elsewhere "Halden Timber" | Each quote keeps its own spelling. |
| L0074 | "the 31st of June", a date that does not exist | Quoted as said. No due date is derived from it. |
| L0028–L0029 | "that's exempt" then "Sorry, zero-rated, not exempt" | Neither line has a trigger, so neither becomes a row. The translator does not decide which statement stands. |
| L0042 | "I'll try to get the mileage log over by the end of next week" | Tentative, owner Sarah Lomax, due "by the end of next week". |
| L0062 | "I'll send you the bank statements by Friday" | Committed, owner Priya Nair, due "by Friday". Never a calendar date. |
| L0037 | "Could you check whether the van was bought on finance?" | The next turn changes the subject. Owner `not in source`. |
| L0044–L0045 | "Can you send me the payroll summary?" / "Yes, I'll do that today." | Requested, accepted on L0045, owner Sarah Lomax, due "today". |
| L0034 | "Tom, can you dig out the invoice from the stove supplier?" | No acceptance follows. Owner "Tom", named on the line, exactly as spelled. |
| L0064 | "We'll get the draft accounts to you in about three weeks." | Committed, owner Priya Nair (who said it), due "in about three weeks". |
| L0070 | "I'll be honest, it was a tough year" | Trigger present, not a commitment: `not_mapped`. |
| L0053 | "HMRC said they will send a new code" | Reported speech with no trigger. No row. |
| L0024 | "If we registered for VAT we'd have to charge twenty percent" | A question row. No decision, no action. |
| L0027, L0060 | "Agreed." and "agreed, let's go with the cash basis" | Decisions, quoted as said. |
| L0009, L0013, L0085 | "85k", "£85,000", "eighty-five thousand pounds" | Each kept as said, never merged or converted. The first two are required by the pattern. |
| L0010, L0047 | One question is answered, one is not | Both are question rows. Whether they were answered is not recorded. |
| L0077 | "The accounts need filing at some point" | No trigger, nobody takes it on. No row. |

## project-kickoff.vtt (constructed, Teams WebVTT)

| Line | Trap | Contract |
|---|---|---|
| L0007 | "The budget agreed is £12,500" | "agreed" is a decision trigger. Recorded as a decision or listed as `not_a_decision`, never dropped. |
| L0007, L0009 | "£12,500" and "12.5k" | Two figures, kept as said. |
| L0013 | "Nadia, can you send over the moodboard by Wednesday?" | Owner from the acceptance on the next turn, or "Nadia" as named. |
| L0016, L0018 | "by Wednesday", "by the end of the month" | Due as said. |
| L0020 | "Could someone loop in our copywriter this week" | Requested, owner `not in source`. |
| L0024 | "let's go with the current host then" | Decision. |
| L0026 | "I might be able to get a first working draft over by Friday" | Tentative. |
| L0028 | "Unknown speaker" | The label is kept. Nobody is guessed. |
| Cue 23 | A cue split over two lines | Joined into one numbered line. |

## quick-checkin.txt (constructed)

Nothing to map, by construction. Every section is present and empty.
