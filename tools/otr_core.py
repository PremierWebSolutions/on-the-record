"""Shared, deterministic pieces used by number.py, check.py and render.py.

Python standard library only. Nothing here calls a model or the network.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRIGGERS_FILE = ROOT / "translator" / "reference" / "triggers.md"
SCHEMA_FILE = ROOT / "translator" / "reference" / "output-schema.json"

SENTINEL = "not in source"
NO_SPEAKER = "(none)"
NO_MARK = "-"

# ---------------------------------------------------------------- lexicons

def load_lexicons(path=TRIGGERS_FILE):
    """Read every ```triggers:<kind>``` and ```pattern:<name>``` block."""
    text = Path(path).read_text(encoding="utf-8")
    lists, patterns = {}, {}
    for kind, name, body in re.findall(r"```(triggers|pattern):([a-z]+)\n(.*?)```", text, re.S):
        entries = [ln.strip() for ln in body.splitlines() if ln.strip()]
        if kind == "triggers":
            lists[name] = entries
        else:
            patterns[name] = re.compile(entries[0], re.I)
    return lists, patterns


def norm(s):
    """Typography only: quotes, dashes, whitespace. Never letters or digits."""
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def phrase_regex(phrase):
    if phrase == "?":
        return re.compile(r"\?")
    body = re.escape(norm(phrase).lower()).replace("\\ ", r"\s+")
    return re.compile(r"(?<![a-z0-9'])" + body + r"(?![a-z0-9'])")


def contains_phrase(text, phrase):
    return bool(phrase_regex(phrase).search(norm(text).lower()))

# ------------------------------------------------------------- transcript

class Line:
    __slots__ = ("id", "mark", "speaker", "text")

    def __init__(self, n, mark, speaker, text):
        self.id = "L%04d" % n
        self.mark = mark or NO_MARK
        self.speaker = speaker or NO_SPEAKER
        self.text = text

    def canonical(self):
        return "%s | %s | %s | %s" % (self.id, self.mark, self.speaker, self.text)


TS = r"\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d+)?"
LABEL = re.compile(
    r"^(?:\[?(?P<ts>" + TS + r")\]?\s*(?:[-–]\s*)?)?"
    r"(?:(?P<q>Q\d+)\s+)?"
    r"(?P<spk>[A-Za-z][A-Za-z0-9.'’()&\- ]{0,47}?):\s+(?P<text>\S.*)$"
)
OTTER_HEADER = re.compile(r"^(?P<spk>[A-Za-z][^:]{0,47}?)\s{2,}(?P<ts>\d{1,2}:\d{2}(?::\d{2})?)\s*$")
CANONICAL = re.compile(r"^L(\d{4}) \| ")


def _clean_ts(ts):
    if not ts:
        return None
    ts = re.split(r"[.,]", ts)[0]
    return ts


def _valid_speaker(spk):
    spk = spk.strip()
    return 0 < len(spk) <= 48 and len(spk.split()) <= 5 and not spk.endswith(".")


def parse_transcript(text):
    """Any supported raw format, or an already-numbered file, to a list of Line."""
    raw = text.replace("﻿", "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    first = next((ln for ln in raw if ln.strip() and not ln.startswith("#")), "")
    if CANONICAL.match(first):
        return _parse_canonical(raw)
    if first.strip().startswith("WEBVTT"):
        return _parse_vtt(raw)
    return _parse_plain(raw)


def _parse_canonical(raw):
    out = []
    for ln in raw:
        if CANONICAL.match(ln):
            parts = ln.split(" | ", 3)
            parts += [""] * (4 - len(parts))
            line = Line(int(parts[0][1:]), parts[1], parts[2], parts[3])
            out.append(line)
    return out


def _parse_plain(raw):
    out, current = [], None
    header_speaker, header_ts = None, None
    for ln in raw:
        s = ln.rstrip()
        if not s.strip():
            continue
        m_hdr = OTTER_HEADER.match(s.strip())
        if m_hdr and _valid_speaker(m_hdr.group("spk")):
            header_speaker, header_ts = m_hdr.group("spk").strip(), m_hdr.group("ts")
            current = header_speaker
            continue
        m = LABEL.match(s.strip())
        if m and _valid_speaker(m.group("spk")):
            current = m.group("spk").strip()
            mark = m.group("q") or _clean_ts(m.group("ts"))
            out.append(Line(len(out) + 1, mark, current, m.group("text").strip()))
            header_ts = None
        else:
            mark = header_ts
            out.append(Line(len(out) + 1, mark, current, s.strip()))
    return out


def _parse_vtt(raw):
    out, block = [], []
    blocks = []
    for ln in raw + [""]:
        if ln.strip():
            block.append(ln.strip())
        elif block:
            blocks.append(block)
            block = []
    for b in blocks:
        t = next((i for i, x in enumerate(b) if "-->" in x), None)
        if t is None:
            continue
        start = b[t].split("-->")[0].strip()
        start = _clean_ts(start)
        if start and start.count(":") == 1:
            start = "00:" + start
        payload = " ".join(b[t + 1:])
        speaker, text = None, payload
        mv = re.match(r"^<v(?:\.[^\s>]*)?\s+([^>]+)>(.*)$", payload)
        if mv:
            speaker, text = mv.group(1).strip(), mv.group(2)
        text = re.sub(r"</?[^>]+>", "", text).strip()
        if not mv:
            m = LABEL.match(text)
            if m and _valid_speaker(m.group("spk")):
                speaker, text = m.group("spk").strip(), m.group("text").strip()
        if text:
            out.append(Line(len(out) + 1, start, speaker, text))
    return out

# ---------------------------------------------------------- trigger index

def find_occurrences(lines, lexicons, patterns):
    """Every trigger occurrence, after overlap resolution (longest match wins).

    Returns a list of dicts: line, category, trigger (lexicon entry or matched
    figure text), start, end (offsets into norm(text).lower()).
    """
    occ = []
    kinds = [("committed", "action"), ("requested", "action"), ("tentative", "action"), ("decision", "decision")]
    for line in lines:
        low = norm(line.text).lower()
        found = []
        for kind, cat in kinds:
            for phrase in lexicons.get(kind, []):
                for m in phrase_regex(phrase).finditer(low):
                    found.append({"line": line.id, "category": cat, "kind": kind, "trigger": phrase,
                                  "start": m.start(), "end": m.end()})
        # longest match wins across action/decision categories
        found.sort(key=lambda o: (-(o["end"] - o["start"]), o["start"]))
        kept = []
        for o in found:
            if not any(o["start"] < k["end"] and k["start"] < o["end"] for k in kept):
                kept.append(o)
        for m in re.finditer(r"\?", low):
            kept.append({"line": line.id, "category": "question", "kind": "question", "trigger": "?",
                         "start": m.start(), "end": m.end()})
        fig = patterns.get("figure")
        if fig:
            text_n = norm(line.text)
            for m in fig.finditer(text_n):
                kept.append({"line": line.id, "category": "figure", "kind": "figure",
                             "trigger": m.group(0).strip(), "start": m.start(), "end": m.end()})
        kept.sort(key=lambda o: o["start"])
        occ.extend(kept)
    return occ
