#!/usr/bin/env python3
"""Normalise a transcript into numbered lines, followed by its trigger index.

    python3 tools/number.py inputs/call.txt > inputs/call.numbered.txt

Accepts plain `Speaker: text` lines (optionally with a timestamp or a
committee question number in front), Otter-style speaker/timestamp headers,
WebVTT (Teams, Zoom) with <v Speaker> voice tags, or a file this script has
already numbered. The rules are in translator/reference/input-format.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from otr_core import find_occurrences, load_lexicons, parse_transcript  # noqa: E402


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    src = Path(argv[1])
    lines = parse_transcript(src.read_text(encoding="utf-8"))
    if not lines:
        print("number.py: no transcript lines found in %s" % src, file=sys.stderr)
        return 1
    lexicons, patterns = load_lexicons()
    occ = find_occurrences(lines, lexicons, patterns)
    print("# on-the-record numbered transcript, version 1")
    print("# source: %s | lines: %d | format: L#### | mark | speaker | text" % (src.name, len(lines)))
    for line in lines:
        print(line.canonical())
    print("# TRIGGER INDEX: every entry below must be cited by a row or listed in not_mapped")
    for o in occ:
        print('# %s %s "%s"' % (o["line"], o["category"], o["trigger"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
