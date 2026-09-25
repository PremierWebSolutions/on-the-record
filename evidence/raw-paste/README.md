# Raw paste

Judges will paste a transcript straight into a project, not a numbered one. A fresh agent was given the translator folder and the raw `inputs/project-kickoff.vtt`, with no numbering and no trigger index, and told nothing else. It numbered the WebVTT itself by [input-format.md](../../translator/reference/input-format.md), built its own worklist from [triggers.md](../../translator/reference/triggers.md), and produced [project-kickoff.json](project-kickoff.json).

`python3 verify/check.py --input inputs/project-kickoff.vtt --output evidence/raw-paste/project-kickoff.json` passes every gate: the line ids the translator assigned by hand are the ones the checker derives from the raw file, so every citation resolves.
