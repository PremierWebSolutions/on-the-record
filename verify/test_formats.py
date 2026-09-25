#!/usr/bin/env python3
"""Prove every transcript format the README names is parsed correctly.

    python3 verify/test_formats.py

For each raw sample in verify/formats/ with a matching <name>.expected file,
parses the sample with otr_core.parse_transcript and checks the resulting
canonical lines (Line.canonical()) match the expected lines exactly, in
order. The expected lines are derived from the rules documented in
translator/reference/input-format.md, not copied from whatever the parser
currently produces, so a mismatch here means either the sample/expectation
is wrong or the parser does not do what the doc promises.

Prints one ok/XX line per format and exits 1 if any format mismatches.
Python standard library only.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from otr_core import parse_transcript  # noqa: E402

FORMATS_DIR = Path(__file__).resolve().parent / "formats"


def expected_lines(path):
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def parsed_lines(path):
    lines = parse_transcript(path.read_text(encoding="utf-8"))
    return [line.canonical() for line in lines]


def find_samples():
    if not FORMATS_DIR.is_dir():
        return []
    samples = []
    for p in sorted(FORMATS_DIR.iterdir()):
        if not p.is_file() or p.name.endswith(".expected"):
            continue
        expected_path = p.with_name(p.name + ".expected")
        if expected_path.exists():
            samples.append((p, expected_path))
    return samples


def main():
    samples = find_samples()
    if not samples:
        print("test_formats.py: no samples with a matching .expected found in %s" % FORMATS_DIR,
              file=sys.stderr)
        return 1

    failed = 0
    for raw_path, expected_path in samples:
        name = raw_path.stem
        got = parsed_lines(raw_path)
        want = expected_lines(expected_path)
        if got == want:
            print("ok   %-18s %-22s (%d lines)" % (name, raw_path.name, len(got)))
            continue
        failed += 1
        print("XX   %-18s %-22s MISMATCH" % (name, raw_path.name))
        if len(got) != len(want):
            print("     line count: expected %d, got %d" % (len(want), len(got)))
        for i, (w, g) in enumerate(zip(want, got)):
            if w != g:
                print("     line %d:" % (i + 1))
                print("       expected: %s" % w)
                print("       got:      %s" % g)
        if len(got) > len(want):
            for g in got[len(want):]:
                print("     unexpected extra line: %s" % g)
        elif len(want) > len(got):
            for w in want[len(got):]:
                print("     missing expected line: %s" % w)

    print()
    if failed:
        print("%d of %d formats FAILED" % (failed, len(samples)))
        return 1
    print("%d of %d formats ok" % (len(samples), len(samples)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
