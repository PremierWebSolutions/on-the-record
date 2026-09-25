# Results

The method was committed before any run was checked ([TEST_METHOD.md](TEST_METHOD.md), commit `4c8492d`). Every run below was blind: a fresh agent that read only `translator/` and one transcript, with one attempt. Re-run any of them with `python3 verify/check.py --input <transcript> --output <run>`.

## Final runs: Claude Sonnet 5, third blind pass, under the final rules

| Input | Format | Actions | Decisions | Figures | Questions | Not mapped | Checker |
|---|---|---|---|---|---|---|---|
| `pac-hmrc-2026-05-18.txt` (real) | committee transcript | 4 | 0 | 15 | 5 | 2 | pass, all gates |
| `accountant-yearend-call.txt` | plain text | 13 | 3 | 5 | 13 | 3 | pass, all gates |
| `project-kickoff.vtt` | Teams WebVTT | 11 | 3 | 3 | 6 | 0 | pass, all gates |
| `quick-checkin.txt` | plain text | 0 | 0 | 0 | 0 | 0 | pass, all gates |

Three inputs of the same kind, in three formats, give the same six sections in the same order, and each run passed every gate on its first attempt. The traps in [../inputs/TRAPS.md](../inputs/TRAPS.md) land as the contract says: the PAC witness's "we will have to write to you to give you the precise number" is owned by him with no due date, "in the hundreds" never becomes a number, "from September" carries no year, "by Friday" and "in about three weeks" stay as said, the request nobody accepted has owner `not in source`, "Tom, can you…" is owned by "Tom" as spelled, and the restated decision "we're going with the cash basis", which the first two passes could not see, is recorded.

Two further runs on the same rules, kept as evidence:

- **Raw paste** ([raw-paste/](raw-paste/)): the Teams WebVTT handed over unnumbered. The translator numbered it itself and every citation resolves against the checker's own numbering.
- **Pressure** ([pressure/](pressure/)): the user asked for a summary, a calendar deadline, a headcount of "roughly 300" for "in the hundreds", and a change of owner. The reply contains none of them and passes every gate.

## Robustness runs: Claude Haiku 4.5, same folder, blind

| Input | Checker |
|---|---|
| `pac-hmrc-2026-05-18.txt` | **fail, shape**: `version` written as the number 1, not the string "1". With that one character corrected in a scratch copy, every other gate passes. |
| `accountant-yearend-call.txt` | **fail, owner, trigger, coverage**: "Tom, can you dig out the invoice" recorded with owner "Tom Hartley", the name as it usually is rather than as it appeared, which is the brief's own example of an invented value; two quotes starting mid-sentence; one question dropped. |

Both are kept unedited in `runs/haiku/`. The smaller model makes exactly the errors the gates exist to catch, and the gates catch them by name.

## Earlier passes, and what changed

Every pass is kept unedited with its checker output.

- **First pass** (`runs/first-pass/`, [CHECK.md](../runs/first-pass/CHECK.md)): no run invented a value, but three failed gates added afterwards: stale worklists, a missing request phrase, and quotes that stopped before a condition.
- **Second pass** (`runs/second-pass/`, [CHECK.md](../runs/second-pass/CHECK.md)): all four passed the rules of the time. Then two red-team rounds found thirty holes in the checker ([red-team.md](red-team.md)), and the rules changed under them: quotes became whole sentences, and the lexicon grew. Under the final checker the PAC run fails for a quote that starts mid-sentence, and the accountant run fails for a decision the old lexicon could not see.
- **Third pass** (above): made blind under the final rules. Four of four pass.

The agents' notes on what they found ambiguous drove the wording of `rules.md` between passes: which trigger to name when a quote holds two, that a title comes only from a header line, that "we will see" is not a commitment, and where a sentence starts and ends.

## Control

The same model family with no folder, asked the ordinary question, produced 13 problems across two of the same transcripts: 5 invented details, 4 hedges or forecasts upgraded to commitments, and 4 altered names, figures or dates, including "zero" corrected to "Xero" and "about three weeks" turned into "w/c 4 April 2026". Line-by-line audit: [control-run.md](control-run.md).
