#!/usr/bin/env python3
"""Check a translator output against the transcript it claims to come from.

    python3 verify/check.py --input inputs/call.txt --output runs/call.json
    python3 verify/check.py --input inputs/call.txt --output out.json --corrections corrections.txt
    python3 verify/check.py --matrix      # every final run (runs/*.json) against the input it names
    python3 verify/check.py --selftest    # every planted fixture must fail through its declared gate

Python standard library only. No network, no model, no install.
Exit 0 when every gate passes, 1 when any gate fails, 2 on bad usage.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from otr_core import (NO_SPEAKER, SCHEMA_FILE, SENTINEL, contains_phrase, find_occurrences,  # noqa: E402
                      load_lexicons, norm, parse_transcript, phrase_regex)

GATES = ["shape", "trace", "speaker", "owner", "trigger", "due", "coverage", "corrections"]

LIMITS = """What a green run does NOT prove:
  - that the transcript itself is right. Mishearings are kept as heard, on purpose.
  - that speaker labels are right. The checker trusts the transcript's own labels.
  - that a commitment phrased without any trigger word was caught ("that's on me").
  - that spelled-out numbers ("eighty-five thousand") were all listed. Coverage sees digits only.
  - that a self-correction later in the call was linked to the line it corrects.
  - that a correction is actually right. A cited correction is shown, never verified.
  - that reported speech was always caught. The reporting-frame check is a short word list,
    not a parse of the sentence, and the idiom list can never be exhaustive.
  - that every negation before a due date was caught. Only an immediately adjacent
    "not"/"n't"/"never" is checked, not one earlier in the sentence."""

NUMBER_WORD = re.compile(r"\d|\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|"
                         r"fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|"
                         r"eighty|ninety|hundred|thousand|million|billion|percent|grand|half)\b", re.I)

NEG_PRECEDERS = ("not ", "n't ", "never ")

REPORT_VERBS = ("said", "says", "told", "mentioned", "reckons", "thinks", "asked")
REPORT_RE = re.compile(r"(?<![a-z0-9'])(?:" + "|".join(REPORT_VERBS) + r")(?![a-z0-9'])")

ZERO_WIDTH_RE = re.compile("[​‌‍⁠﻿]")

# ------------------------------------------------------------------ helpers

def in_text(needle, hay):
    return needle in hay or (norm(needle) != "" and norm(needle) in norm(hay))


def spans(needle, hay):
    """Offsets of needle inside norm(hay).lower(), for coverage."""
    n, h = norm(needle).lower(), norm(hay).lower()
    out, i = [], h.find(n) if n else -1
    while i != -1:
        out.append((i, i + len(n)))
        i = h.find(n, i + 1)
    return out


def load_corrections(path):
    if not path:
        return None
    table, n = {}, 0
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#") and "=>" in ln:
            n += 1
            heard, meant = [x.strip() for x in ln.split("=>", 1)]
            table["C%03d" % n] = (heard, meant)
    return table


def cited_rows(out):
    """(section, row) for every row that carries quote/line/speaker."""
    rows = []
    for key in ("title", "date"):
        v = out.get("meeting", {}).get(key)
        if isinstance(v, dict):
            rows.append(("meeting." + key, v))
    for sec in ("actions", "decisions", "figures", "questions"):
        rows += [(sec, r) for r in out.get(sec, []) if isinstance(r, dict)]
    return rows


def label(sec, row):
    return "%s %s" % (sec, row.get("id", row.get("line", "?")))

# --------------------------------------------------- boundary & sentence helpers

def clean(s):
    """Strip zero-width characters before any boundary test. otr_core.norm()
    does not (yet) do this, so without it a zero-width character planted
    inside a word (e.g. "dis<ZWSP>agreed") would fake a word boundary."""
    return ZERO_WIDTH_RE.sub("", s or "")


FILLERS = {"well", "so", "right", "look", "actually", "honestly", "listen", "okay", "ok", "anyway", "now",
           "yes", "no", "oh", "um", "hmm", "thanks", "sorry", "please", "also", "then", "yeah"}
NAME_TOKEN = re.compile(r"^[^\W\d_][^\W\d_'\u2019\-]*$")


def name_shaped(owner):
    """A vocative owner looks like a name: one to three capitalised words, not a filler."""
    toks = owner.split()
    return (0 < len(toks) <= 3 and toks[0].lower() not in FILLERS
            and all(NAME_TOKEN.match(tk) and tk[0].isupper() for tk in toks))


def alnum_boundary(text, s, e):
    """True if the span [s:e) of `text` begins and ends on a word boundary —
    the character just outside it on either side (if any) is not a letter or
    digit, so the span can never be carved out of the middle of a word."""
    before_ok = s == 0 or not text[s - 1].isalnum()
    after_ok = e == len(text) or not text[e].isalnum() or text[e - 1] in ".?!"
    return before_ok and after_ok


def quote_on_boundary(quote, line_text):
    """True if `quote` occurs in `line_text` at a position that begins and
    ends on a word boundary (never mid-word, e.g. carved out of "disagreed").
    Zero-width characters are stripped from both sides first so one planted
    inside a word cannot fake a boundary that isn't really there."""
    for s, e in spans(clean(quote), clean(line_text)):
        if alnum_boundary(norm(clean(line_text)).lower(), s, e):
            return True
    return False


ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "prof", "ltd", "inc", "plc", "co", "corp", "approx", "etc",
                 "e.g", "i.e", "vs", "no", "st", "rev", "sr", "jr", "mt", "ave", "fig", "vol"}


def sentence_breaks(text):
    """Offsets just past each genuine sentence end in normalised, lower-cased text.
    A '.' after an abbreviation or a single letter, or inside a number, is not
    one. A run-on with no space after the full stop still counts."""
    ends = []
    for m in re.finditer(r"[.?!]", text):
        nxt = text[m.end():m.end() + 1]
        if nxt and not (nxt.isspace() or nxt.isalpha()):
            continue
        if m.group() == ".":
            prev = re.search(r"([a-z][a-z.]*)$", text[:m.start()])
            tok = prev.group(1) if prev else ""
            if tok in ABBREVIATIONS or len(tok) == 1:
                continue
        ends.append(m.end())
    return ends


def sentence_span(text, pos):
    """(start, end) of the sentence in normalised `text` that contains `pos`."""
    breaks = sentence_breaks(text)
    start = 0
    for b in breaks:
        if b <= pos:
            start = b
        else:
            break
    while start < len(text) and text[start] == " ":
        start += 1
    end = next((b for b in breaks if b > pos), len(text))
    return start, end


def quote_is_whole_sentence(quote, trigger, line_text):
    """The quote must run from the start of the sentence holding `trigger` to
    that sentence's end — not stop early (dropping a condition) and not start
    late (dropping a negation or other context in the same breath)."""
    text = norm(line_text).lower()
    trig_re = phrase_regex(trigger)
    for qs, qe in spans(quote, line_text):
        m = trig_re.search(text, qs, qe)
        if not m:
            continue
        sent_s, sent_e = sentence_span(text, m.start())
        if qs == sent_s and qe == sent_e:
            return True
    return False


def genuine_trigger(occurrences, line_id, kind, trigger, quote, line_text):
    """A row's trigger must correspond to a real, word-boundary occurrence
    found by find_occurrences() on that line, positioned inside the quote's
    own span — so a trigger carved out of a longer word (which find_occurrences
    itself would never report) can never be credited as genuine."""
    for o in occurrences:
        if o["line"] != line_id or o["kind"] != kind or o["trigger"] != trigger:
            continue
        for qs, qe in spans(quote, line_text):
            if qs <= o["start"] and o["end"] <= qe:
                return True
    return False


def idiom_containing(quote, trigger, idioms):
    """The idiom (if any) whose occurrence in `quote` fully contains the
    trigger's own occurrence — meaning the trigger is part of a set phrase,
    not a real commitment, request or hedge."""
    low = norm(quote).lower()
    m = phrase_regex(trigger).search(low)
    if not m:
        return None
    for idiom in idioms:
        im = phrase_regex(idiom).search(low)
        if im and im.start() <= m.start() and m.end() <= im.end():
            return idiom
    return None


def is_reported_speech(quote, trigger):
    """A reporting frame ("Tom said, ...") before the trigger, or the trigger
    sitting inside quotation marks, means these are someone else's words, not
    the speaker's own. A heuristic on word choice and punctuation only."""
    low = norm(quote).lower()
    m = phrase_regex(trigger).search(low)
    if not m:
        return False
    before = low[:m.start()]
    if REPORT_RE.search(before):
        return True
    if before.count('"') % 2 == 1:
        return True
    return before.count("“") > before.count("”")


def token_is_whole_figure(text, s, e):
    """A digit-bearing figure token must not be a fragment of a longer one:
    the character just before it must not continue a number (digit, '.', ',',
    a minus sign or a currency symbol), and what follows must not continue one
    either (a digit, a '.'/',' then a digit, or a space then a 3-digit group)."""
    before = text[s - 1] if s > 0 else ""
    if before and (before.isdigit() or before in ".,-−£$€"):
        return False
    after = text[e:]
    if after[:1].isdigit():
        return False
    if len(after) >= 2 and after[0] in ".," and after[1].isdigit():
        return False
    if re.match(r" \d{3}(?!\d)", after):
        return False
    return True


def due_supported_by(due, phrases, text):
    """True if `due` appears in `text` at an occurrence that is not negated
    (not immediately preceded by "not "/"n't "/"never ") and sits in the same
    sentence as one of `phrases` (the trigger, or the acceptance wording) —
    so neither a negation nor an unrelated later sentence can supply it."""
    hay = norm(text).lower()
    phrase_positions = [m.start() for p in phrases for m in phrase_regex(p).finditer(hay)]
    for s, e in spans(due, text):
        if any(hay[:s].endswith(neg) for neg in NEG_PRECEDERS):
            continue
        due_sent = sentence_span(hay, s)
        if any(sentence_span(hay, ps) == due_sent for ps in phrase_positions):
            return True
    return False

# ------------------------------------------------------------ schema gate

def validate(node, schema, root, path, errs):
    if "$ref" in schema:
        ref = root
        for part in schema["$ref"].lstrip("#/").split("/"):
            ref = ref[part]
        schema = ref
    if "anyOf" in schema:
        for sub in schema["anyOf"]:
            trial = []
            validate(node, sub, root, path, trial)
            if not trial:
                return
        errs.append("%s: %r matches none of the allowed forms" % (path, node))
        return
    if "const" in schema:
        if node != schema["const"]:
            errs.append("%s: must be %r" % (path, schema["const"]))
        return
    if "enum" in schema:
        if node not in schema["enum"]:
            errs.append("%s: %r is not one of %s" % (path, node, schema["enum"]))
        return
    t = schema.get("type")
    if t == "object":
        if not isinstance(node, dict):
            errs.append("%s: must be an object" % path)
            return
        req = schema.get("required", [])
        missing = [k for k in req if k not in node]
        extra = [k for k in node if k not in schema.get("properties", {})]
        if missing:
            errs.append("%s: missing %s" % (path, missing))
        if extra and schema.get("additionalProperties") is False:
            errs.append("%s: fields the contract has no place for: %s" % (path, extra))
        if not missing and not extra and list(node.keys()) != req:
            errs.append("%s: fields out of order, expected %s" % (path, req))
        for k, sub in schema.get("properties", {}).items():
            if k in node:
                validate(node[k], sub, root, "%s.%s" % (path, k), errs)
    elif t == "array":
        if not isinstance(node, list):
            errs.append("%s: must be a list" % path)
            return
        for i, item in enumerate(node):
            validate(item, schema.get("items", {}), root, "%s[%d]" % (path, i), errs)
    elif t == "string":
        if not isinstance(node, str):
            errs.append("%s: must be a string" % path)
        elif "pattern" in schema and not re.fullmatch(schema["pattern"], node):
            errs.append("%s: %r does not match %s" % (path, node, schema["pattern"]))


def gate_shape(out, lines, ctx):
    errs = []
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validate(out, schema, schema, "output", errs)
    if errs:
        return errs  # the other shape checks assume a valid skeleton
    if out["source"]["last_line"] != lines[-1].id:
        errs.append("source.last_line is %s but the transcript ends at %s" % (out["source"]["last_line"], lines[-1].id))
    seen = []
    for ln in lines:
        if ln.speaker != NO_SPEAKER and ln.speaker not in seen:
            seen.append(ln.speaker)
    if out["meeting"]["participants"] != seen:
        errs.append("meeting.participants must be the speaker labels in order of first appearance: %s" % seen)
    for sec, prefix, extra in (("actions", "A", "trigger"), ("decisions", "D", "trigger"),
                               ("figures", "F", "token"), ("questions", "Q", None)):
        rows = out[sec]
        ids = [r["id"] for r in rows]
        if ids != ["%s%d" % (prefix, i + 1) for i in range(len(rows))]:
            errs.append("%s: ids must run %s1..%s%d in order, got %s" % (sec, prefix, prefix, len(rows), ids))
        order = [r["line"] for r in rows]
        if order != sorted(order):
            errs.append("%s: rows must be in transcript order" % sec)
        seen_rows = {}
        for r in rows:
            key = (r["line"], r["quote"], r.get(extra) if extra else None)
            if key in seen_rows:
                errs.append("%s: %s and %s are exact duplicates (same line, quote%s)"
                            % (sec, seen_rows[key], r["id"], " and " + extra if extra else ""))
            else:
                seen_rows[key] = r["id"]
    if [r["line"] for r in out["not_mapped"]] != sorted(r["line"] for r in out["not_mapped"]):
        errs.append("not_mapped: rows must be in transcript order")
    first_spoken = next((ln.id for ln in lines if ln.speaker != NO_SPEAKER), None)
    for key in ("title", "date"):
        v = out["meeting"].get(key)
        if isinstance(v, dict) and first_spoken and v["line"] >= first_spoken:
            errs.append("meeting.%s cites %s, which is not before the first spoken line (%s); a title or "
                        "date must come from the header, before anyone speaks" % (key, v["line"], first_spoken))
    ip = ctx.get("input_path")
    if ip is not None:
        claimed = out.get("source", {}).get("file", "")
        actual = Path(ip).name
        if Path(claimed).name != actual:
            errs.append("source.file is %r but this output is being checked against %r" % (claimed, actual))
    return errs

# ------------------------------------------------------------ content gates

def gate_trace(out, lines, ctx):
    errs, by_id = [], ctx["by_id"]

    def check(where, quote, line_id):
        if line_id not in by_id:
            errs.append("%s cites %s, which is not a line of this transcript" % (where, line_id))
            return
        if not quote.strip():
            errs.append("%s has an empty quote" % where)
            return
        if in_text(quote, by_id[line_id].text):
            if not quote_on_boundary(quote, by_id[line_id].text):
                errs.append("%s: the quote begins or ends inside a word on %s (a mid-word splice)\n"
                            "      %s says: %s" % (where, line_id, line_id, by_id[line_id].text))
            return
        elsewhere = [ln.id for ln in lines if in_text(quote, ln.text)]
        if elsewhere:
            errs.append("%s: quote is not on %s, it is on %s (wrong line cited)\n      %s says: %s"
                        % (where, line_id, ", ".join(elsewhere), line_id, by_id[line_id].text))
        else:
            errs.append("%s: quote appears nowhere in the transcript (invented)\n      quote: %s" % (where, quote))

    for sec, row in cited_rows(out):
        check(label(sec, row), row["quote"], row["line"])
        if sec == "figures" and not in_text(row["token"], row["quote"]):
            errs.append("%s: token %r is not inside its quote" % (label(sec, row), row["token"]))
        if sec == "actions" and row["accepted_line"] != SENTINEL:
            check(label(sec, row) + " accepted_quote", row["accepted_quote"], row["accepted_line"])

    for f in out["figures"]:
        where = label("figures", f)
        if not NUMBER_WORD.search(f["token"]):
            errs.append("%s: token %r is not a number" % (where, f["token"]))
        elif re.search(r"\d", f["token"]):
            ln = by_id.get(f["line"])
            if ln:
                hay = norm(clean(ln.text)).lower()
                whole = any(token_is_whole_figure(hay, s, e) for s, e in spans(clean(f["token"]), clean(ln.text)))
                if not whole:
                    errs.append("%s: token %r is not a whole figure on %s — it looks like part of a longer "
                                "number\n      %s says: %s" % (where, f["token"], f["line"], f["line"], ln.text))
        else:
            qhay = norm(clean(f["quote"])).lower()
            if not any(alnum_boundary(qhay, s, e) for s, e in spans(clean(f["token"]), clean(f["quote"]))):
                errs.append("%s: token %r is not a whole word in its quote" % (where, f["token"]))
    return errs


def gate_speaker(out, lines, ctx):
    errs, by_id = [], ctx["by_id"]
    for sec, row in cited_rows(out):
        ln = by_id.get(row["line"])
        if sec.startswith("meeting.") and row["speaker"] != NO_SPEAKER:
            errs.append("%s must come from an unlabelled header line, not from what someone said" % sec)
        if ln and row["speaker"] != ln.speaker:
            errs.append("%s: %s is spoken by %r, the row says %r" % (label(sec, row), ln.id, ln.speaker, row["speaker"]))
    return errs


def next_turn(lines, line_id, speaker):
    idx = next(i for i, ln in enumerate(lines) if ln.id == line_id)
    for ln in lines[idx + 1:]:
        if ln.speaker not in (speaker, NO_SPEAKER):
            return ln
    return None


def gate_owner(out, lines, ctx):
    errs, by_id, lex = [], ctx["by_id"], ctx["lex"]
    for a in out["actions"]:
        where = label("actions", a)
        if a["kind"] in ("committed", "tentative"):
            if a["owner"] != a["speaker"]:
                errs.append("%s: a %s action is owned by whoever said it (%r), not %r"
                            % (where, a["kind"], a["speaker"], a["owner"]))
            if a["accepted_line"] != SENTINEL:
                errs.append("%s: only a requested action can carry an acceptance" % where)
            continue
        if a["accepted_line"] != SENTINEL:
            if a["line"] not in by_id:
                continue
            nxt = next_turn(lines, a["line"], a["speaker"])
            if not nxt or nxt.id != a["accepted_line"]:
                errs.append("%s: accepted_line must be the next line by a different speaker (%s)"
                            % (where, nxt.id if nxt else "none"))
                continue
            has_acceptance = any(contains_phrase(a["accepted_quote"], p) for p in lex["acceptance"] + lex["committed"])
            has_refusal = any(contains_phrase(a["accepted_quote"], p) for p in lex.get("refusal", []))
            if not has_acceptance or has_refusal:
                errs.append("%s: accepted_quote %r is not an unambiguous acceptance (%s)"
                            % (where, a["accepted_quote"],
                               "it contains a refusal marker" if has_refusal else "no acceptance phrase in it"))
            if a["owner"] != nxt.speaker:
                errs.append("%s: the acceptance on %s was said by %r, owner says %r"
                            % (where, nxt.id, nxt.speaker, a["owner"]))
        elif a["owner"] != SENTINEL:
            if a["owner"] == a["speaker"]:
                errs.append("%s: a request is not owned by the person asking" % where)
            else:
                vocative = re.match(r"^\W*" + re.escape(a["owner"]) + r"\s*,", clean(a["quote"])) and name_shaped(a["owner"])
                if not vocative:
                    errs.append("%s: without an acceptance, owner %r is valid only as a sentence-opening "
                                "vocative (\"%s, can you...\"), exactly as spelled; the quote does not open "
                                "that way, so use %r" % (where, a["owner"], a["owner"], SENTINEL))
    return errs


def gate_trigger(out, lines, ctx):
    errs, lex, by_id = [], ctx["lex"], ctx["by_id"]
    occ = find_occurrences(lines, lex, ctx["patterns"])

    for a in out["actions"]:
        where = label("actions", a)
        ln = by_id.get(a["line"])
        if a["trigger"] not in lex[a["kind"]]:
            errs.append("%s: %r is not a %s trigger in reference/triggers.md" % (where, a["trigger"], a["kind"]))
        elif not contains_phrase(a["quote"], a["trigger"]):
            errs.append("%s: trigger %r is not in the quote" % (where, a["trigger"]))
        elif ln:
            if not quote_is_whole_sentence(a["quote"], a["trigger"], ln.text):
                errs.append("%s: the quote is not the whole sentence holding %r (must run from sentence start "
                            "to sentence end, so a negation or a condition can't be cut off)" % (where, a["trigger"]))
            if not genuine_trigger(occ, a["line"], a["kind"], a["trigger"], a["quote"], ln.text):
                errs.append("%s: %r inside the quote does not correspond to a genuine %s trigger on %s (it may "
                            "be carved out of a longer word)" % (where, a["trigger"], a["kind"], a["line"]))
            idiom = idiom_containing(a["quote"], a["trigger"], lex.get("idiom", []))
            if idiom:
                errs.append("%s: %r lies inside the idiom %r, not a commitment; file it in not_mapped as "
                            "not_a_commitment instead" % (where, a["trigger"], idiom))
            if is_reported_speech(a["quote"], a["trigger"]):
                errs.append("%s: %r follows a reporting frame or sits inside quotation marks — this is "
                            "reported speech, not %s's own words; file it in not_mapped as reported_speech "
                            "instead" % (where, a["trigger"], a["speaker"]))
        hedges = [p for p in lex["tentative"] if contains_phrase(a["quote"], p)]
        if hedges and a["kind"] != "tentative":
            errs.append("%s: the quote hedges (%r) so the action must be tentative, not %s"
                        % (where, hedges[0], a["kind"]))

    for d in out["decisions"]:
        where = label("decisions", d)
        ln = by_id.get(d["line"])
        if d["trigger"] not in lex["decision"] or not contains_phrase(d["quote"], d["trigger"]):
            errs.append("%s: needs a decision trigger from reference/triggers.md inside its quote" % where)
        elif ln:
            if not quote_is_whole_sentence(d["quote"], d["trigger"], ln.text):
                errs.append("%s: the quote is not the whole sentence holding %r (must run from sentence start "
                            "to sentence end)" % (where, d["trigger"]))
            if not genuine_trigger(occ, d["line"], "decision", d["trigger"], d["quote"], ln.text):
                errs.append("%s: %r inside the quote does not correspond to a genuine decision trigger on %s "
                            "(it may be carved out of a longer word)" % (where, d["trigger"], d["line"]))
            if is_reported_speech(d["quote"], d["trigger"]):
                errs.append("%s: %r follows a reporting frame or sits inside quotation marks — reported "
                            "speech, not a decision made here; file it in not_mapped as reported_speech "
                            "instead" % (where, d["trigger"]))

    for q in out["questions"]:
        where = label("questions", q)
        if "?" not in q["quote"]:
            errs.append("%s: a question quote must contain its question mark" % where)
            continue
        ln = by_id.get(q["line"])
        if ln and in_text(q["quote"], ln.text) and not quote_is_whole_sentence(q["quote"], "?", ln.text):
            errs.append("%s: the quote is not the whole question (must run from the sentence start to its '?')" % where)

    return errs


def gate_due(out, lines, ctx):
    errs, by_id, lex = [], ctx["by_id"], ctx["lex"]
    for a in out["actions"]:
        where = label("actions", a)
        if (a["accepted_line"] == SENTINEL) != (a["accepted_quote"] == SENTINEL):
            errs.append("%s: accepted_line and accepted_quote must both be filled or both be %r" % (where, SENTINEL))
        due = a["due_as_said"]
        if due == SENTINEL:
            continue
        in_quote = in_text(due, a["quote"])
        in_accept = a["accepted_quote"] != SENTINEL and in_text(due, a["accepted_quote"])
        if not in_quote and not in_accept:
            errs.append("%s: due_as_said %r was not said in the cited words; a due date is kept as said, "
                        "never worked out" % (where, due))
            continue
        ok = False
        ln = by_id.get(a["line"])
        if in_quote and ln and due_supported_by(due, [a["trigger"]], ln.text):
            ok = True
        if not ok and in_accept:
            acc_ln = by_id.get(a["accepted_line"])
            if acc_ln and due_supported_by(due, lex["acceptance"] + lex["committed"], acc_ln.text):
                ok = True
        if not ok:
            errs.append("%s: due_as_said %r is negated (\"not\"/\"n't\"/\"never\" immediately before it) or "
                        "not in the same sentence as the words that gave it" % (where, due))
    return errs


def recorded_at(out, category, trigger, line_id):
    """True when a row of that category on line_id already carries the trigger."""
    section = {"action": "actions", "decision": "decisions", "figure": "figures", "question": "questions"}[category]
    for r in out[section]:
        if r["line"] != line_id:
            continue
        text = r["token"] if category == "figure" else r["quote"]
        if category == "question" and "?" in text:
            return True
        if category != "question" and norm(trigger).lower() in norm(text).lower():
            return True
    return False


def gate_coverage(out, lines, ctx):
    errs, by_id = [], ctx["by_id"]
    occ = find_occurrences(lines, ctx["lex"], ctx["patterns"])
    covers = {}  # (line, bucket) -> [(start, end), ...]; bucket is the action's kind, or the
                 # category for decisions/figures/questions, or "*" for an accepted_quote citation
                 # (which legitimately reuses wording of any kind, not just its own row's kind).

    def add(line_id, bucket, text, source_text):
        for sp in spans(text, source_text):
            covers.setdefault((line_id, bucket), []).append(sp)

    for a in out["actions"]:
        if a["line"] in by_id:
            add(a["line"], a["kind"], a["quote"], by_id[a["line"]].text)
        if a["accepted_line"] in by_id:
            add(a["accepted_line"], "*", a["accepted_quote"], by_id[a["accepted_line"]].text)
    for sec, cat, field in (("decisions", "decision", "quote"), ("questions", "question", "quote"),
                            ("figures", "figure", "token")):
        for r in out[sec]:
            if r["line"] in by_id:
                add(r["line"], cat, r[field], by_id[r["line"]].text)

    listed = {(u["line"], u["category"], norm(u["trigger"]).lower()) for u in out["not_mapped"]}
    for o in occ:
        key = (o["line"], o["category"], norm(o["trigger"]).lower())
        if key in listed:
            continue
        if o["category"] == "action":
            buckets = covers.get((o["line"], o["kind"]), []) + covers.get((o["line"], "*"), [])
        else:
            buckets = covers.get((o["line"], o["category"]), [])
        hit = any(s <= o["start"] and o["end"] <= e for s, e in buckets)
        if not hit:
            errs.append("%s: %s trigger %r is neither cited nor listed in not_mapped (dropped)\n      %s says: %s"
                        % (o["line"], o["category"], o["trigger"], o["line"], by_id[o["line"]].text))
    real = {(o["line"], o["category"], norm(o["trigger"]).lower()) for o in occ}
    for u in out["not_mapped"]:
        where = "not_mapped %s %s %r" % (u["line"], u["category"], u["trigger"])
        if (u["line"], u["category"], norm(u["trigger"]).lower()) not in real:
            errs.append("%s: that trigger is not on that line" % where)
        if (u["reason"] == "repeat") != (u["see_line"] != SENTINEL):
            errs.append("%s: see_line is filled exactly when the reason is 'repeat'" % where)
        elif u["see_line"] != SENTINEL and not (u["see_line"] in by_id and u["see_line"] < u["line"]):
            errs.append("%s: see_line must be an earlier line of this transcript" % where)
        elif u["see_line"] != SENTINEL and not recorded_at(out, u["category"], u["trigger"], u["see_line"]):
            errs.append("%s: see_line %s has no %s row carrying %r, so it is not a repeat of anything"
                        % (where, u["see_line"], u["category"], u["trigger"]))
    return errs


def gate_corrections(out, lines, ctx):
    errs, table = [], ctx["corrections"]
    for sec, row in cited_rows(out):
        for cid in row.get("corrections", []):
            if table is None:
                errs.append("%s cites %s but no corrections file was supplied" % (label(sec, row), cid))
            elif cid not in table:
                errs.append("%s cites %s, which is not in the corrections file" % (label(sec, row), cid))
            elif not contains_phrase(row["quote"], table[cid][0]):
                errs.append("%s cites %s but %r is not a whole word in its quote" % (label(sec, row), cid, table[cid][0]))
    return errs

# ------------------------------------------------------------------ runner

def run_gates(out, lines, corrections=None, input_path=None):
    lex, patterns = load_lexicons()
    ctx = {"by_id": {ln.id: ln for ln in lines}, "lex": lex, "patterns": patterns,
           "corrections": corrections, "input_path": input_path}
    results = {}
    shape = gate_shape(out, lines, ctx)
    results["shape"] = shape
    broken = ("missing", "must be an object", "must be a list", "must be a string")
    if any(b in e for e in shape for b in broken):
        for g in GATES[1:]:
            results[g] = ["not run: the output does not have the contract's shape"]
        return results
    for g in GATES[1:]:
        try:
            results[g] = globals()["gate_" + g](out, lines, ctx)
        except (KeyError, TypeError, StopIteration) as exc:
            results[g] = ["could not run on this output: %r" % exc]
    return results


def report(results, quiet=False):
    ok = True
    for g in GATES:
        errs = results[g]
        ok = ok and not errs
        if not quiet:
            print("  %-12s %s" % (g, "PASS" if not errs else "FAIL (%d)" % len(errs)))
            for e in errs[:20]:
                print("      - " + e)
    return ok


def check_pair(input_path, output_path, corrections_path=None, quiet=False):
    lines = parse_transcript(Path(input_path).read_text(encoding="utf-8"))
    out = json.loads(Path(output_path).read_text(encoding="utf-8"))
    results = run_gates(out, lines, load_corrections(corrections_path), input_path=input_path)
    return report(results, quiet), results


def selftest():
    bad = 0
    examples = sorted((ROOT / "verify" / "examples").glob("*.json"))
    for ex in examples:
        src = next(p for p in ex.parent.glob(ex.stem + ".*") if p.suffix != ".json")
        ok, results = check_pair(src, ex, quiet=True)
        bad += 0 if ok else 1
        print("  %-4s %-38s expect %-10s %s" % ("ok" if ok else "XX", "example " + ex.stem, "pass",
                                                  "pass" if ok else "failed " + ",".join(g for g in GATES if results[g])))
    fixtures = sorted((ROOT / "verify" / "fixtures").glob("*.json"))
    for f in fixtures:
        fx = json.loads(f.read_text(encoding="utf-8"))
        input_path = ROOT / fx["input"]
        lines = parse_transcript(input_path.read_text(encoding="utf-8"))
        corr = load_corrections(ROOT / fx["corrections"]) if fx.get("corrections") else None
        results = run_gates(fx["output"], lines, corr, input_path=input_path)
        failed = [g for g in GATES if results[g]]
        if fx["expect"] == "pass":
            good = not failed
            got = "pass" if good else "failed " + ",".join(failed)
        else:
            good = fx["expect"] in failed
            got = "caught by " + ",".join(failed) if failed else "NOT CAUGHT"
        bad += 0 if good else 1
        print("  %-4s %-38s expect %-10s %s" % ("ok" if good else "XX", f.stem, fx["expect"], got))
    total = len(examples) + len(fixtures)
    print("\n%d/%d examples and fixtures behaved as declared" % (total - bad, total))
    stale = stale_derived_files()
    for s in stale:
        print("  XX   stale: %s does not match a fresh regeneration" % s)
    return bad == 0 and not stale


def stale_derived_files():
    """Numbered transcripts and examples.md are generated. A stale copy would
    hand the translator a worklist the checker no longer agrees with."""
    import subprocess
    stale = []
    for numbered in sorted((ROOT / "inputs").glob("*.numbered.txt")):
        raw = next((p for p in numbered.parent.glob(numbered.name.replace(".numbered.txt", ".*"))
                    if not p.name.endswith(".numbered.txt")), None)
        if raw is None:
            continue
        fresh = subprocess.run([sys.executable, str(ROOT / "tools" / "number.py"), str(raw)],
                               capture_output=True, text=True).stdout
        if fresh != numbered.read_text(encoding="utf-8"):
            stale.append(numbered.relative_to(ROOT).as_posix())
    examples = ROOT / "translator" / "examples.md"
    before = examples.read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_examples.py")], capture_output=True)
    if examples.read_text(encoding="utf-8") != before:
        examples.write_text(before, encoding="utf-8")
        stale.append("translator/examples.md")
    return stale


def matrix():
    runs = sorted((ROOT / "runs").glob("*.json"))
    passed = 0
    for r in runs:
        out = json.loads(r.read_text(encoding="utf-8"))
        claimed = out.get("source", {}).get("file", "")
        problems = []
        if not claimed:
            problems.append("source.file is missing")
        elif Path(claimed).stem != r.stem:
            problems.append("source.file %r does not match this run's own filename %r (a run cannot choose "
                            "an easier transcript)" % (claimed, r.name))
        else:
            src = ROOT / claimed
            if not src.exists():
                problems.append("source.file %r could not be read" % claimed)
        if problems:
            print("  %-4s %s  (%s)" % ("FAIL", r.relative_to(ROOT / "runs").as_posix(), "; ".join(problems)))
            continue
        corr = r.with_suffix(".corrections.txt")
        try:
            ok, results = check_pair(src, r, corr if corr.exists() else None, quiet=True)
        except (OSError, ValueError) as exc:
            print("  %-4s %s  (could not check: %r)" % ("FAIL", r.relative_to(ROOT / "runs").as_posix(), exc))
            continue
        passed += ok
        print("  %-4s %s  (%s)" % ("PASS" if ok else "FAIL", r.relative_to(ROOT / "runs").as_posix(), ", ".join(g for g in GATES if results[g]) or "all gates"))
    print("\n%d/%d runs pass every gate" % (passed, len(runs)))
    return passed == len(runs)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input")
    ap.add_argument("--output")
    ap.add_argument("--corrections")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--matrix", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        ok = selftest()
    elif a.matrix:
        ok = matrix()
    elif a.input and a.output:
        print("Checking %s against %s" % (a.output, a.input))
        ok, _ = check_pair(a.input, a.output, a.corrections)
        print("\nRESULT: %s" % ("PASS, every value traces to its line and speaker" if ok else "FAIL"))
    else:
        ap.print_help()
        return 2
    print("\n" + LIMITS)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
