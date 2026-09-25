# Test method

Written and committed before any translation run was checked, so the results in [RESULTS.md](RESULTS.md) could not shape the method.

## What is being tested

The brief's bar: three different inputs of the same kind give outputs of the same shape, every fact in each output traces to the input that produced it, and anything missing is marked missing.

## Runs

1. **Four inputs, four formats**: a real Public Accounts Committee excerpt, a constructed accountant–client call in plain text, a constructed Teams WebVTT kickoff, and a constructed call with nothing to map. Sources and traps: [../inputs/SOURCE.md](../inputs/SOURCE.md), [../inputs/TRAPS.md](../inputs/TRAPS.md).
2. **Blind translator**: each run is a fresh Claude agent that reads only the `translator/` folder and the numbered transcript. It is told not to open the checker, the trap list, other inputs or earlier runs, and it gets one attempt. The model used is recorded per run.
3. **Checked, not eyeballed**: every output goes through `python3 verify/check.py --input <transcript> --output <run>`. A run's result is whatever the checker prints. Failures are kept in `runs/` with their checker output, not replaced.
4. **Changes after a failure**: if a run fails, the cause is written down first (folder unclear, checker wrong, or translator error). If the folder or checker changes, every run is repeated blind and both results are kept, dated.

## Control

The same model is given the same transcripts with no folder, only the ordinary request a person would type ("turn this call into action items and a short summary"). Every owner, date, number or next step in its answer that is not in the transcript is counted. This shows what the folder is for.

## Planted defects

`verify/fixtures/` holds one deliberately broken output per gate, each declaring the gate that must catch it (`expect`), plus clean outputs that must pass. `python3 verify/check.py --selftest` fails if any fixture is caught by the wrong gate or not at all.

## Stranger walk

Before a stranger reads the README, the confusions we expect are written in [cold-walk.md](cold-walk.md) and committed. Then the walk happens, and what actually confused them is recorded beside the prediction, with the fix. A walk by a fresh agent is labelled as such and is not presented as a human walk.

## What would count as failure of the whole entry

Any value in any run that the checker cannot trace to its line and speaker. The disqualifier in the brief is one invented fact, so the checker is built to fail on one.
