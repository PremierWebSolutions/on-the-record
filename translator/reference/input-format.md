# Input format

The translator reads numbered lines. `tools/number.py` produces them from the common transcript exports, and the checker numbers the raw file the same way, so a citation always means the same line to the translator, the checker and a reader.

## Numbered line

```
L0042 | 00:12:07 | Priya Nair | I'll send you the bank statements by Friday.
```

`L####` is the line id, counting from `L0001`. The mark is the timestamp or committee question number if the export had one, otherwise `-`. The speaker is the label exactly as the export printed it, or `(none)`. The rest of the line is the text, unchanged.

A numbered file ends with a `# TRIGGER INDEX` listing every trigger the lexicon finds, one per line (`# L0042 action "i'll"`). That list is the translator's worklist.

## How a raw transcript becomes numbered lines

1. **Every non-blank line becomes one numbered line, in order.** Nothing is merged, split or reworded.
2. **Speaker label:** the text before the first `": "`, when it starts with a letter (any script — `Zoë Smith`, `José García`, `Ó Briain`, `王芳`, and diarisation labels like `SPEAKER_00` or `Speaker_1` all count), is at most eight words and 64 characters, and does not end in a full stop. An optional timestamp (`00:12:07`, `[12:07]`, `(12:07)` — square brackets or parentheses, or none) or question number (`Q12`) in front of it becomes the mark. The label may also carry one leading list marker (`- `, `• `, `* `), for exports that print each turn as a bulleted line. A timestamp in brackets or parentheses immediately *after* the name, right before the colon (Rev.com / Fireflies style — `Tom Hartley (00:00:03): I'll send it.`), is recognised the same way and becomes the mark.
3. **Label words that are never a speaker:** a line whose would-be label is one of `action`, `action item`, `action items`, `note`, `notes`, `decision`, `decisions`, `update`, `reminder`, `follow-up`, `fyi`, `re`, `correction`, `aside`, `summary`, `recap`, `minutes`, `agenda`, `apologies`, `attendees`, `present`, `oral evidence`, `witnesses`, `members present`, `date`, `time`, `location`, `subject`, `title` (case-insensitive, matched against the whole label) is never treated as a new speaker — it is treated like any other unlabelled line: it keeps its full text, label included, and belongs to whoever is currently speaking, or `(none)` before anyone has spoken. This list cannot be exhaustive — plain "Name:" text has no marker that reliably distinguishes a speaker from a section header, so a label outside this list that happens to look like one (a heading, a footer) can still be mistaken for a speaker. This is a known limit of the format, not a bug to chase with more entries.
4. **Unlabelled lines** continue the previous speaker's turn, as transcripts print a long turn over several paragraphs. Lines before anyone has spoken (a title, a date) have the speaker `(none)`.
5. **Otter-style exports** put the speaker and a timestamp on their own line (`Priya Nair  0:42`). That line sets the speaker and mark for the lines that follow and is not itself numbered. The timestamp may carry fractional seconds (`0:03.250`) or a 12-hour AM/PM suffix (`10:03 AM`, as Google Meet / Gemini export), which is recognised but dropped from the mark.
6. **WebVTT (Teams, Zoom):** each cue becomes one line. The mark is the cue's start time to the second. The speaker comes from the `<v Name>` voice tag, or from a `Name:` prefix, or — if the cue has neither — carries forward from the previous cue's speaker, exactly as an unlabelled plain-text line does (a cue before anyone has spoken stays `(none)`). A cue with two or more `<v Name>` segments (a speaker change inside one cue) becomes one numbered line per segment, all sharing that cue's mark. A cue whose text runs over two lines is joined with a space. Other tags are removed. A `|` inside a voice tag's label (`<v Alice | CFO>`) is replaced with `/` when the line is parsed, so it can never be mistaken for the `|` that separates the fields of a numbered line — both the translator and the checker parse it the same way.

## Known limits of the formats

Exports do not mark overlapping speech, and a diarisation error puts words in the wrong mouth. The translator trusts the labels it is given and says so in every checker run. Speaker-label recognition from plain "Name:" text is inherently a heuristic — the reserved-label list in rule 3 covers annotation headers seen in practice, but plain text cannot be made airtight against every possible section heading a transcript might use.
