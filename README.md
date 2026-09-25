# on-the-record

Turns a meeting or call transcript into a file note you can rely on: who took what on, what was asked of whom, what was decided, which figures were said and which questions were asked. Every value is copied from a numbered line of the transcript and credited to the speaker on that line. If the transcript does not say it, the note says `not in source`.

Accountants write these notes by hand after client calls, and project managers after kickoffs. Tools that automate it add things: given two of our test transcripts without this folder, the same model put a year on "from September", turned "about three weeks" into a date, and corrected "zero" to "Xero" ([evidence/control-run.md](evidence/control-run.md)).

## Use it

The translator is the `translator/` folder: five Markdown files and a JSON schema, nothing else. Add that folder, and only that folder, to a Claude project and set the project instructions to *"You are the translator in identity.md. Follow rules.md exactly."* Then paste a transcript. Plain `Speaker: text`, Otter exports and Teams or Zoom WebVTT all work, and the folder numbers the lines itself. What comes back is the note.

The scripts below are not the translator. They prove it kept its promise. Run them from the repository root, on the included accountant call first.

1. **Number the transcript, optionally.** `python3 tools/number.py inputs/accountant-yearend-call.txt > call.txt` gives the translator numbered lines and its worklist. Paste `call.txt` instead of the raw file.
2. **Check the note.** Save the reply as `note.json` in the repository root, then `python3 verify/check.py --input inputs/accountant-yearend-call.txt --output note.json`. Python 3 only, no install, no network. It takes the original transcript and numbers it the same way.
3. **Read it.** `python3 tools/render.py --input inputs/accountant-yearend-call.txt --output note.json --html note.html` puts the transcript beside the note with every quote highlighted.

With the Claude Code CLI, `tools/translate.sh inputs/accountant-yearend-call.txt` does all three and writes to `runs/`.

## What comes back

One JSON object with the same six sections every time: `meeting`, `actions`, `decisions`, `figures`, `questions`, `not_mapped`. Every value is a verbatim piece of the cited line, that line's speaker label, or a code from a closed list. There is no field for a summary. `not_mapped` is not an error list: it holds every trigger phrase the translator saw and chose not to use, with the reason, so nothing is dropped silently. The contract lives in [translator/reference/](translator/reference/).

## How we know it holds

- `python3 verify/check.py --selftest` runs planted defects, each of which must be caught by the gate it names: a quote credited to the wrong speaker, an owner taken from a date, a decision sliced out of "disagreed". Eight independent attackers forged outputs against the checker before submission; what got past it and how each hole was closed is in [evidence/red-team.md](evidence/red-team.md).
- `python3 verify/check.py --matrix` checks every final run in `runs/`.
- One input is real: a Public Accounts Committee hearing with HMRC. [inputs/SOURCE.md](inputs/SOURCE.md) gives Parliament's URL and the file's SHA-256, so you can compare the two yourself.
- Every run was blind, made by a fresh agent given only `translator/` and one transcript. Failed first attempts are kept ([evidence/RESULTS.md](evidence/RESULTS.md)).

The checker prints a short list of what a pass does not prove; [LIMITS.md](LIMITS.md) has the full one.

Built with Claude: Opus built the folder and checker, Sonnet and Haiku made the blind runs, and the entrant chose the conversion and directed the work.
