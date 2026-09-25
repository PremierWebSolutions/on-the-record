# The translator folder

This folder is the translator. Add it to a Claude project, or give it to any capable model as its instructions, and it converts one meeting or call transcript into one JSON file note.

**Feed it** a transcript numbered by `tools/number.py`: lines of `L#### | mark | speaker | text`, followed by a trigger index. Given a raw transcript instead, it numbers it itself by the rules in [reference/input-format.md](reference/input-format.md).

**It returns** a single JSON object in the shape of [reference/output-schema.json](reference/output-schema.json), with nothing before or after it. The fields are explained in [reference/fields.md](reference/fields.md). Anything the transcript does not say is `not in source`.

| File | Job |
|---|---|
| [identity.md](identity.md) | What it converts, from what, to what, and what it never does |
| [rules.md](rules.md) | How it maps, in order, each rule tied to the checker gate that tests it |
| [examples.md](examples.md) | Three input/output pairs, each passing the checker |
| [reference/](reference/) | The contract: schema, field definitions, trigger phrases, input format |

Check any output from the repository root with `python3 verify/check.py --input <transcript> --output <note.json>`.
