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
                      load_lexicons, norm, parse_transcript)

GATES = ["shape", "trace", "speaker", "owner", "trigger", "due", "coverage", "corrections"]

LIMITS = """What a green run does NOT prove:
  - that the transcript itself is right. Mishearings are kept as heard, on purpose.
  - that speaker labels are right. The checker trusts the transcript's own labels.
  - that a commitment phrased without any trigger word was caught ("that's on me").
  - that spelled-out numbers ("eighty-five thousand") were all listed. Coverage sees digits only.
  - that a self-correction later in the call was linked to the line it corrects."""

NUMBER_WORD = re.compile(r"\d|\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|"
                         r"fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|"
                         r"eighty|ninety|hundred|thousand|million|billion|percent|grand|half)\b", re.I)

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
    for sec, prefix in (("actions", "A"), ("decisions", "D"), ("figures", "F"), ("questions", "Q")):
        rows = out[sec]
        ids = [r["id"] for r in rows]
        if ids != ["%s%d" % (prefix, i + 1) for i in range(len(rows))]:
            errs.append("%s: ids must run %s1..%s%d in order, got %s" % (sec, prefix, prefix, len(rows), ids))
        order = [r["line"] for r in rows]
        if order != sorted(order):
            errs.append("%s: rows must be in transcript order" % sec)
    if [r["line"] for r in out["not_mapped"]] != sorted(r["line"] for r in out["not_mapped"]):
        errs.append("not_mapped: rows must be in transcript order")
    return errs

# ------------------------------------------------------------ source gates

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
            if not any(contains_phrase(a["accepted_quote"], p) for p in lex["acceptance"]):
                errs.append("%s: accepted_quote contains no acceptance phrase" % where)
            if a["owner"] != nxt.speaker:
                errs.append("%s: the acceptance on %s was said by %r, owner says %r"
                            % (where, nxt.id, nxt.speaker, a["owner"]))
        elif a["owner"] != SENTINEL:
            if a["owner"] == a["speaker"]:
                errs.append("%s: a request is not owned by the person asking" % where)
            elif not re.search(r"(?<!\w)" + re.escape(a["owner"]) + r"(?!\w)", a["quote"]):
                errs.append("%s: owner %r is not named in the quote and nobody accepted; use %r"
                            % (where, a["owner"], SENTINEL))
    return errs


def runs_to_sentence_end(quote, trigger, line_text):
    """A quote may start late but must not stop before the end of the sentence
    holding its trigger, so a condition ("…if the bank replies") can't be cut."""
    text = norm(line_text).lower()
    for qs, qe in spans(quote, line_text):
        m = re.search(r"(?<![a-z0-9'])" + re.escape(norm(trigger).lower()), text[qs:qe])
        if not m:
            continue
        stop = re.search(r"[.?!](?=\s|$)", text[qs + m.end():])
        sentence_end = qs + m.end() + stop.end() if stop else len(text)
        if qe >= sentence_end:
            return True
    return False


def gate_trigger(out, lines, ctx):
    errs, lex, by_id = [], ctx["lex"], ctx["by_id"]
    for sec in ("actions", "decisions"):
        for r in out[sec]:
            ln = by_id.get(r["line"])
            if ln and in_text(r["quote"], ln.text) and contains_phrase(r["quote"], r["trigger"]) \
                    and not runs_to_sentence_end(r["quote"], r["trigger"], ln.text):
                errs.append("%s: the quote stops before the end of the sentence holding %r; a condition or "
                            "qualifier may have been cut" % (label(sec, r), r["trigger"]))
    for a in out["actions"]:
        where = label("actions", a)
        if a["trigger"] not in lex[a["kind"]]:
            errs.append("%s: %r is not a %s trigger in reference/triggers.md" % (where, a["trigger"], a["kind"]))
        elif not contains_phrase(a["quote"], a["trigger"]):
            errs.append("%s: trigger %r is not in the quote" % (where, a["trigger"]))
        hedges = [p for p in lex["tentative"] if contains_phrase(a["quote"], p)]
        if hedges and a["kind"] != "tentative":
            errs.append("%s: the quote hedges (%r) so the action must be tentative, not %s"
                        % (where, hedges[0], a["kind"]))
    for d in out["decisions"]:
        if d["trigger"] not in lex["decision"] or not contains_phrase(d["quote"], d["trigger"]):
            errs.append("%s: needs a decision trigger from reference/triggers.md inside its quote" % label("decisions", d))
    for q in out["questions"]:
        if "?" not in q["quote"]:
            errs.append("%s: a question quote must contain its question mark" % label("questions", q))
    for f in out["figures"]:
        if not NUMBER_WORD.search(f["token"]):
            errs.append("%s: token %r is not a number" % (label("figures", f), f["token"]))
    return errs


def gate_due(out, lines, ctx):
    errs = []
    for a in out["actions"]:
        where = label("actions", a)
        if (a["accepted_line"] == SENTINEL) != (a["accepted_quote"] == SENTINEL):
            errs.append("%s: accepted_line and accepted_quote must both be filled or both be %r" % (where, SENTINEL))
        due = a["due_as_said"]
        if due == SENTINEL:
            continue
        said = [a["quote"]] + ([a["accepted_quote"]] if a["accepted_quote"] != SENTINEL else [])
        if not any(in_text(due, s) for s in said):
            errs.append("%s: due_as_said %r was not said in the cited words; a due date is kept as said, "
                        "never worked out" % (where, due))
    return errs


def gate_coverage(out, lines, ctx):
    errs, by_id = [], ctx["by_id"]
    occ = find_occurrences(lines, ctx["lex"], ctx["patterns"])
    covers = {}  # (line, category) -> list of spans or trigger names

    def add(line_id, cat, text, source_text):
        for sp in spans(text, source_text):
            covers.setdefault((line_id, cat), []).append(sp)

    for a in out["actions"]:
        if a["line"] in by_id:
            add(a["line"], "action", a["quote"], by_id[a["line"]].text)
        if a["accepted_line"] in by_id:
            add(a["accepted_line"], "action", a["accepted_quote"], by_id[a["accepted_line"]].text)
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
        hit = any(s <= o["start"] and o["end"] <= e for s, e in covers.get((o["line"], o["category"]), []))
        if o["category"] == "figure":
            hit = any(s < o["end"] and o["start"] < e for s, e in covers.get((o["line"], "figure"), []))
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
    return errs


def gate_corrections(out, lines, ctx):
    errs, table = [], ctx["corrections"]
    for sec, row in cited_rows(out):
        for cid in row.get("corrections", []):
            if table is None:
                errs.append("%s cites %s but no corrections file was supplied" % (label(sec, row), cid))
            elif cid not in table:
                errs.append("%s cites %s, which is not in the corrections file" % (label(sec, row), cid))
            elif not in_text(table[cid][0], row["quote"]):
                errs.append("%s cites %s but %r is not in its quote" % (label(sec, row), cid, table[cid][0]))
    return errs

# ------------------------------------------------------------------ runner

def run_gates(out, lines, corrections=None):
    lex, patterns = load_lexicons()
    ctx = {"by_id": {ln.id: ln for ln in lines}, "lex": lex, "patterns": patterns, "corrections": corrections}
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
    results = run_gates(out, lines, load_corrections(corrections_path))
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
        lines = parse_transcript((ROOT / fx["input"]).read_text(encoding="utf-8"))
        corr = load_corrections(ROOT / fx["corrections"]) if fx.get("corrections") else None
        results = run_gates(fx["output"], lines, corr)
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
        src = ROOT / out.get("source", {}).get("file", "")
        corr = r.with_suffix(".corrections.txt")
        ok, results = check_pair(src, r, corr if corr.exists() else None, quiet=True)
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
