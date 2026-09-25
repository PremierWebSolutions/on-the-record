# AGENTS.md

Instructions for any coding agent working on this repository.

## This project

**What it is:** a folder-based translator (meeting transcript → fixed-shape JSON file note) plus the offline checker that proves every value traces to its line and speaker.
**Stack:** Markdown and JSON for the translator folder; Python 3 standard library for the tools and checker. No web app, no database, no network, no dependencies.
**Deploy:** none. The repo is the deliverable. Roll back with `git revert`.

## Layout
- `translator/` — the drop-in folder: identity, rules, examples, reference/ (the contract). This is what goes into a Claude project.
- `tools/` — `number.py` (normaliser + trigger index), `otr_core.py` (shared parsing), `render.py` (file note view), `build_examples.py`.
- `verify/` — `check.py` (the gates), `examples/` (checked pairs shown in examples.md), `fixtures/` (planted defects).
- `inputs/` — test transcripts, their numbered forms, SOURCE.md, TRAPS.md.
- `runs/` — translator outputs; `first-pass/` keeps the failed first attempts unedited.
- `evidence/` — test method, results, control run, cold walk, sources.

## Conventions
- Every output value is a verbatim piece of its cited line, a speaker label copied from it, or a closed-enum code. Any change that adds a free-text field breaks the entry.
- `triggers.md` is read by both the translator and the checker. Change the lexicon there only.
- Numbered inputs and `examples.md` are generated. Regenerate them after any change to the lexicon or examples; `--selftest` fails on a stale copy.

## Working rules
- **Build what was asked, nothing else.** Propose extras; don't add them.
- **If intent is ambiguous, ask one question and stop.** When you hit a wall, say what you tried and stop; never switch approach silently.
- **Report honestly.** If a check fails, show the output. A failed run is kept, not replaced.
- **Plan before code, one section at a time.** Implement a section, verify it, commit it, then start the next.
- **Commit every time something works**, with a message of the form `type: short description`.
- **Never delete or reset without a recoverable copy first.** Branch the mess, then reset.
- **Python standard library only**, including the checker, because judges run it from a clean clone with no install.
- **Small modules with one job.** Files past about 300 lines and functions past about 50 are a prompt to split, not a hard cap.
- **Debug before rewriting.** State the likely causes, add logging, use exact error text, and after three failed attempts question the assumption rather than the code.
- **Tested means input, expected output and assertion.** Every checker gate has a planted fixture that must fail through it and a clean one that must pass.
- **Docs describe what exists.** Update them in the same commit as the change; never document something that is only planned.
- **No personal or company attribution** in shipped files beyond what the owner has approved.

## Rules that override the owner's global ruleset
- This public copy carries only the parts of the owner's standard ruleset that apply to a standard-library Python repo, with no internal notes, names or paths, because the repository is public. The web, database, payments, auth and hosting rules are out of scope here.

## Do not touch
- `runs/first-pass/` — kept unedited as evidence.
- `inputs/pac-hmrc-2026-05-18.txt` — byte-identical to the publisher's paragraphs (hash in SOURCE.md).

## Gotchas
- A `Speaker:` label is taken from any short text before the first ": ", so a heading or annotation ("Action: …", "Note: …") would become a speaker; `tools/otr_core.py` keeps a reserved-word list that stops the common ones, and `input-format.md` says it cannot be airtight.
- Action, decision and question quotes must be the whole sentence holding their trigger. A run made under the earlier "start late" rule fails the trigger gate; regenerate the run, don't relax the gate.
- `number.py` treats text before the first ": " as a speaker label if it is five words or fewer, so a header like "Oral evidence: …" would become a speaker. Header lines in inputs avoid colons.
- The first blind pass ran on numbered files generated before a figure-pattern fix. Stale derived files are now a selftest failure.
