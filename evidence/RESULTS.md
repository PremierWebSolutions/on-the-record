# Results

The method was committed before any run was checked ([TEST_METHOD.md](TEST_METHOD.md), commit `ebe0b71`). Every run below was blind: a fresh agent that read only `translator/` and one numbered transcript, with one attempt. Re-run any of them with `python3 verify/check.py --input <transcript> --output <run>`.

## Final runs: Claude Sonnet 5, second blind pass

| Input | Format | Actions | Decisions | Figures | Questions | Not mapped | Checker |
|---|---|---|---|---|---|---|---|
| `pac-hmrc-2026-05-18.txt` (real) | committee transcript | 4 | 0 | 15 | 5 | 3 | pass, all gates |
| `accountant-yearend-call.txt` | plain text | 14 | 2 | 5 | 13 | 3 | pass, all gates |
| `project-kickoff.vtt` | Teams WebVTT | 9 | 2 | 3 | 6 | 3 | pass, all gates |
| `quick-checkin.txt` | plain text | 0 | 0 | 0 | 0 | 0 | pass, all gates |

Three inputs of the same kind, in three formats, give the same six sections in the same order. Every trap in [../inputs/TRAPS.md](../inputs/TRAPS.md) lands as the contract says: the PAC witness's promise to "write to you to give you the precise number" is owned by him with no due date, "in the hundreds" never becomes a number, "from September" carries no year, "by Friday" and "in about three weeks" stay as said, the request nobody accepted has owner `not in source`, and "Tom, can you…" is owned by "Tom" as spelled.

## Robustness runs: Claude Haiku 4.5, same folder, blind

| Input | Checker |
|---|---|
| `pac-hmrc-2026-05-18.txt` | pass, all gates |
| `accountant-yearend-call.txt` | **fail, speaker gate**: question Q4 quotes line L0032, which Tom Hartley said, and credits it to Priya Nair |

The failing run is kept unedited in `runs/haiku/`. It is the failure this translator exists to prevent, a line put in the wrong mouth, made by a real model on a real run, and the checker caught it by name. The same Haiku run also recorded the PAC witness's "We will see." as a commitment where Sonnet filed it as `not_a_commitment`: a classification difference that is visible in the output, not an invented value.

## First blind pass, and what changed

The first pass (Sonnet on three inputs, Haiku on the empty call) is kept unedited in `runs/first-pass/`, with the checker's output in [CHECK.md](../runs/first-pass/CHECK.md). In all four runs the trace, speaker, owner and due gates passed: no run invented a value. Three runs failed on things we changed after they were made, each of which is now part of the folder or the checker:

1. **Stale worklists.** The numbered inputs had been generated before a fix to the figure pattern ("£95," had kept its comma and "£10 billion" had lost its "billion"). `--selftest` now fails if any numbered input or `examples.md` differs from a fresh regeneration.
2. **A missing request phrase.** The kickoff's "Could someone loop in our copywriter" was a request the lexicon could not see. "could someone" and its variants were added, and the kickoff failed coverage on the old run.
3. **Cut conditions.** Six accountant quotes and one each on the other two stopped before the end of their sentence. Nothing was invented, but the old rule allowed a condition to be dropped, so action and decision quotes must now run to the end of the trigger's sentence.

The agents' own notes on what they found ambiguous also led to three clarifications in `rules.md`: which trigger to name when a quote holds two, that a title or date comes only from a header line, and that "we will see" is an example of a trigger that is not a commitment.

## Control

The same model family with no folder, asked the ordinary question, produced 13 problems across the same two transcripts: 5 invented details, 4 hedges or forecasts upgraded to commitments, and 4 altered names, figures or dates, including "zero" corrected to "Xero" and "about three weeks" turned into "w/c 4 April 2026". Line-by-line audit: [control-run.md](control-run.md).
