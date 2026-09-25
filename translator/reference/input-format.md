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
2. **Speaker label:** the text before the first `": "`, when it starts with a letter, is at most five words, and does not end in a full stop. An optional timestamp (`00:12:07`, `[12:07]`) or question number (`Q12`) in front of it becomes the mark.
3. **Unlabelled lines** continue the previous speaker's turn, as transcripts print a long turn over several paragraphs. Lines before anyone has spoken (a title, a date) have the speaker `(none)`.
4. **Otter-style exports** put the speaker and a timestamp on their own line (`Priya Nair  0:42`). That line sets the speaker and mark for the lines that follow and is not itself numbered.
5. **WebVTT (Teams, Zoom):** each cue becomes one line. The mark is the cue's start time to the second. The speaker comes from the `<v Name>` voice tag, or from a `Name:` prefix. A cue whose text runs over two lines is joined with a space. Other tags are removed.

## Known limits of the formats

Exports do not mark overlapping speech, and a diarisation error puts words in the wrong mouth. The translator trusts the labels it is given and says so in every checker run.
