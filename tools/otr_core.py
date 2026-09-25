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


ZERO_WIDTH = "\u200b\u200c\u200d\u2060\ufeff"


def norm(s):
    """Typography only: quotes, dashes, whitespace, invisible characters. Never letters or digits."""
    for zw in ZERO_WIDTH:
        s = s.replace(zw, "")
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
        # A "|" inside a captured mark or speaker label (e.g. a WebVTT voice
        # tag `<v Alice | CFO>`) would collide with the " | " field
        # separator used by canonical(); swap it for "/" at parse time so
        # translator and checker always see the same, unambiguous label.
        self.mark = (mark or NO_MARK).replace("|", "/")
        self.speaker = (speaker or NO_SPEAKER).replace("|", "/")
        self.text = text

    def canonical(self):
        return "%s | %s | %s | %s" % (self.id, self.mark, self.speaker, self.text)


TS = r"\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d+)?"
# Speaker-label character classes are Unicode-aware: the first character is
# any letter (any script, via [^\W\d_]), continuation characters are any
# word character (letters/digits/underscore, again Unicode-aware) plus the
# punctuation and space a label may legitimately contain.
#
# LABEL has two alternative shapes, since Python's re forbids reusing a
# group name across alternatives (so the second shape uses spk2/ts2/text2 —
# see _match_label, which folds whichever branch matched back onto one
# shape):
#   1. mark (if any) before the name: "[00:12:07] Priya Nair: text",
#      "Q12 Priya Nair: text", plain "Priya Nair: text".
#   2. mark after the name, in brackets or parens, immediately before the
#      colon (Rev.com / Fireflies style): "Priya Nair (00:12:07): text".
# Either shape may carry a leading list marker ("- ", "• ", "* ").
LABEL = re.compile(
    r"^(?:[-•*]\s*)?(?:"
    r"(?:[\[(]?(?P<ts>" + TS + r")[\])]?\s*(?:[-–]\s*)?)?"
    r"(?:(?P<q>Q\d+)\s+)?"
    r"(?P<spk>[^\W\d_][\w.'’()&\- ]{0,63}?):\s+(?P<text>\S.*)"
    r"|"
    r"(?P<spk2>[^\W\d_][\w.'’&\- ]{0,63}?)\s*[\[(](?P<ts2>" + TS + r")[\])]\s*:\s+(?P<text2>\S.*)"
    r")$"
)


def _match_label(s):
    """Match LABEL and return {"spk", "q", "ts", "text"}, or None.

    Normalises whichever of LABEL's two alternative branches matched (see
    LABEL's comment) onto one set of keys, so callers never need to know
    which branch fired.
    """
    m = LABEL.match(s)
    if not m:
        return None
    if m.group("spk") is not None:
        return {"spk": m.group("spk"), "q": m.group("q"), "ts": m.group("ts"), "text": m.group("text")}
    return {"spk": m.group("spk2"), "q": None, "ts": m.group("ts2"), "text": m.group("text2")}


# Otter-style header line: speaker and timestamp on their own line, e.g.
# "Priya Nair  0:42". Accepts the same timestamp shapes LABEL does
# (including fractional seconds, "0:03.250") plus an optional AM/PM tail,
# for Google Meet / Gemini exports ("Tom Hartley  10:03 AM").
OTTER_HEADER = re.compile(
    r"^(?P<spk>[^\W\d_][^:]{0,63}?)\s{2,}(?P<ts>" + TS + r")\s*(?:[AaPp]\.?[Mm]\.?)?\s*$"
)
CANONICAL = re.compile(r"^L(\d{4}) \| ")

# Label words that introduce an annotation, not a new speaker: a plain-text
# line such as "Action: I'll send the statements by Friday." keeps its full
# text (label included) and stays with whoever is currently speaking, or
# "(none)" before anyone has spoken. Matched case-insensitively against the
# WHOLE candidate label (not a substring of it). Plain "Name:" text has no
# way to be made airtight against every possible section header a transcript
# might use — this list covers the ones seen in practice, documented here
# and in input-format.md so translator and checker never disagree.
NEVER_SPEAKERS = frozenset({
    "action", "action item", "action items", "note", "notes", "decision", "decisions",
    "update", "reminder", "follow-up", "fyi", "re", "correction", "aside", "summary",
    "recap", "minutes", "agenda", "apologies", "attendees", "present", "oral evidence",
    "witnesses", "members present", "date", "time", "location", "subject", "title",
})


def _clean_ts(ts):
    if not ts:
        return None
    ts = re.split(r"[.,]", ts)[0]
    return ts


def _valid_speaker(spk):
    spk = spk.strip()
    if not (0 < len(spk) <= 64 and len(spk.split()) <= 8 and not spk.endswith(".")):
        return False
    return spk.lower() not in NEVER_SPEAKERS


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
            header_speaker, header_ts = m_hdr.group("spk").strip(), _clean_ts(m_hdr.group("ts"))
            current = header_speaker
            continue
        m = _match_label(s.strip())
        if m and _valid_speaker(m["spk"]):
            current = m["spk"].strip()
            mark = m["q"] or _clean_ts(m["ts"])
            out.append(Line(len(out) + 1, mark, current, m["text"].strip()))
            header_ts = None
        else:
            mark = header_ts
            out.append(Line(len(out) + 1, mark, current, s.strip()))
    return out


VOICE_TAG_OPEN = re.compile(r"<v(?:\.[^\s>]*)?\s+([^>]+)>")


def _parse_vtt(raw):
    out, block = [], []
    blocks = []
    for ln in raw + [""]:
        if ln.strip():
            block.append(ln.strip())
        elif block:
            blocks.append(block)
            block = []
    prev_speaker = None
    for b in blocks:
        t = next((i for i, x in enumerate(b) if "-->" in x), None)
        if t is None:
            continue
        start = b[t].split("-->")[0].strip()
        start = _clean_ts(start)
        if start and start.count(":") == 1:
            start = "00:" + start
        payload = " ".join(b[t + 1:])
        tags = list(VOICE_TAG_OPEN.finditer(payload))
        if tags:
            # One numbered line per <v> segment (same cue, same mark), so a
            # cue that switches speaker mid-cue (`<v Alice>…</v> <v Bob>…</v>`)
            # never credits both segments to the first speaker.
            for i, tag in enumerate(tags):
                seg_end = tags[i + 1].start() if i + 1 < len(tags) else len(payload)
                segment = payload[tag.end():seg_end]
                text = re.sub(r"</?[^>]+>", "", segment).strip()
                if not text:
                    continue
                speaker = tag.group(1).strip()
                out.append(Line(len(out) + 1, start, speaker, text))
                prev_speaker = speaker
            continue
        text = re.sub(r"</?[^>]+>", "", payload).strip()
        m = _match_label(text)
        if m and _valid_speaker(m["spk"]):
            speaker, text = m["spk"].strip(), m["text"].strip()
        else:
            # No voice tag and no "Name:" prefix: this cue continues whoever
            # spoke last, exactly like unlabelled plain text, not "(none)".
            speaker = prev_speaker
        if text:
            out.append(Line(len(out) + 1, start, speaker, text))
        if speaker:
            prev_speaker = speaker
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
