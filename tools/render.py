#!/usr/bin/env python3
"""Render a translator JSON record as a Markdown file note and/or HTML view.

    python3 tools/render.py --input call.txt --output call.json [--md out.md] [--html out.html]
--output is read, not written: it is the translator's JSON. With neither
--md nor --html, the Markdown goes to stdout. A mechanical layout only: no
value is added that is not already a field in the record. Stdlib only.
"""
import argparse
import html
import json
import sys
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from otr_core import SENTINEL, norm, parse_transcript  # noqa: E402

_WS_SUB = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-", "\u2014": "-", "\u00a0": " "}

def _norm_map(text):
    """Mirror otr_core.norm() char by char, tracking each output char's index in `text`."""
    chars, idx = [], []
    for i, ch in enumerate(text):
        ch = _WS_SUB.get(ch, ch)
        if ch.isspace():
            if chars and chars[-1] == " ":
                continue
            ch = " "
        chars.append(ch)
        idx.append(i)
    while chars and chars[0] == " ":
        chars.pop(0); idx.pop(0)
    while chars and chars[-1] == " ":
        chars.pop(); idx.pop()
    return "".join(chars), idx

def find_quote_span(quote, text):
    """(start, end) of `quote` in `text`: exact substring, then typography-normalised. None if absent."""
    i = text.find(quote)
    if i != -1:
        return i, i + len(quote)
    nq = norm(quote)
    if not nq:
        return None
    ntext, idx = _norm_map(text)
    j = ntext.find(nq)
    return (idx[j], idx[j + len(nq) - 1] + 1) if j != -1 else None

def collect_spans(out, text_by_line):
    """line id -> [(start, end, category)] for every quote the JSON cites."""
    spans = {}
    def add(line_id, quote, category):
        if line_id in text_by_line and quote:
            span = find_quote_span(quote, text_by_line[line_id])
            if span:
                spans.setdefault(line_id, []).append((span[0], span[1], category))
    for key, category in (("actions", "action"), ("decisions", "decision"),
                          ("figures", "figure"), ("questions", "question")):
        for row in out[key]:
            add(row["line"], row["quote"], category)
    for a in out["actions"]:
        if a["accepted_line"] != SENTINEL:
            add(a["accepted_line"], a["accepted_quote"], "action")
    return spans
PRIORITY = {"action": 0, "decision": 1, "figure": 2, "question": 3}


def resolve_spans(spans):
    """One highlight per range (action > decision > figure > question); drop a span
    containing another (the more specific wins); keep the rest non-overlapping."""
    best = {}
    for start, end, cat in spans:
        if (start, end) not in best or PRIORITY[cat] < PRIORITY[best[(start, end)]]:
            best[(start, end)] = cat
    uniq = sorted((s, e, c) for (s, e), c in best.items())
    keep = [s for s in uniq if not any((s[0], s[1]) != (t[0], t[1]) and s[0] <= t[0] and t[1] <= s[1] for t in uniq)]
    keep.sort(key=lambda s: (s[0], s[1] - s[0]))
    out, cursor = [], 0
    for s in keep:
        if s[0] >= cursor:
            out.append(s)
            cursor = s[1]
    return out
def mark_line(text, spans):
    out, pos = [], 0
    for start, end, cat in resolve_spans(spans):
        out.append(esc(text[pos:start]))
        out.append('<mark class="%s">%s</mark>' % (cat, esc(text[start:end])))
        pos = end
    out.append(esc(text[pos:]))
    return "".join(out)

def esc(v):
    return html.escape(str(v), quote=True)
def cite(line_id, speaker):  # plain-text citation, e.g. "L0004 \u00b7 Dana Okoro"
    return "%s \u00b7 %s" % (line_id, speaker)
def cite_link(line_id, speaker):  # same citation as an HTML anchor to #<line_id>
    return '<a href="#%s">%s \u00b7 %s</a>' % (esc(line_id), esc(line_id), esc(speaker))
def line_link(line_id):
    return esc(SENTINEL) if line_id == SENTINEL else '<a href="#%s">%s</a>' % (esc(line_id), esc(line_id))

def action_row(a, html_out):
    quote = '"%s"' % (esc(a["quote"]) if html_out else a["quote"])
    cited = cite_link(a["line"], a["speaker"]) if html_out else cite(a["line"], a["speaker"])
    if a["accepted_line"] != SENTINEL:
        accepted = esc(a["accepted_quote"]) if html_out else a["accepted_quote"]
        quote += '<br>Accepted: "%s"' % accepted
        cited += "<br>" + (line_link(a["accepted_line"]) if html_out else a["accepted_line"])
    kind, owner, due = a["kind"], a["owner"], a["due_as_said"]
    if html_out:
        kind, owner, due = esc(kind), esc(owner), esc(due)
    return [kind, owner, quote, due, cited]
def cited_row(item, html_out, extra=None):
    """A decision/figure/question row: an optional lead field, the quote, its citation."""
    quote = '"%s"' % (esc(item["quote"]) if html_out else item["quote"])
    cited = cite_link(item["line"], item["speaker"]) if html_out else cite(item["line"], item["speaker"])
    lead = [] if extra is None else [esc(item[extra]) if html_out else item[extra]]
    return lead + [quote, cited]
def unmapped_row(u, html_out):
    if html_out:
        return [line_link(u["line"]), esc(u["category"]), esc(u["trigger"]), esc(u["reason"]),
                line_link(u["see_line"])]
    return [u["line"], u["category"], u["trigger"], u["reason"], u["see_line"]]

SECTIONS = [
    ("Actions", ["Kind", "Owner", "What was said", "Due (as said)", "Cited"], "actions", action_row),
    ("Decisions", ["Trigger", "What was said", "Cited"], "decisions", partial(cited_row, extra="trigger")),
    ("Figures", ["Token", "What was said", "Cited"], "figures", partial(cited_row, extra="token")),
    ("Questions", ["What was said", "Cited"], "questions", cited_row),
    ("Not mapped", ["Line", "Category", "Trigger", "Reason", "See also"], "not_mapped", unmapped_row),
]

FOOTER = "Every quoted value above is checked against the transcript by verify/check.py. Nothing here is summarised."

def md_cell(v):
    return str(v).replace("|", "\\|").replace("\n", "<br>")
def md_table(headers, rows):
    if not rows:
        return "None in this call.\n"
    head = "| " + " | ".join(headers) + " |"
    sep = "|" + "|".join("---" for _ in headers) + "|"
    body = "\n".join("| " + " | ".join(md_cell(c) for c in r) + " |" for r in rows)
    return "\n".join([head, sep, body]) + "\n"

def build_markdown(out):
    m = out["meeting"]
    title, date = m["title"], m["date"]
    heading = title["quote"] if isinstance(title, dict) else "Meeting (title not in source)"
    date_line = ("%s (%s)" % (date["quote"], cite(date["line"], date["speaker"]))
                 if isinstance(date, dict) else SENTINEL)
    participants = ", ".join(m["participants"]) if m["participants"] else SENTINEL
    parts = ["# %s" % heading, "", "**Date:** %s" % date_line, "**Participants:** %s" % participants]
    for name, headers, key, row_fn in SECTIONS:
        parts += ["", "## %s" % name, md_table(headers, [row_fn(r, False) for r in out[key]])]
    parts += ["---", FOOTER]
    return "\n".join(parts) + "\n"

def html_table(headers, rows):
    if not rows:
        return '<p class="empty">None in this call.</p>'
    head = "".join("<th>%s</th>" % esc(h) for h in headers)
    body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r) for r in rows)
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (head, body)
def render_transcript_line(ln, spans, is_not_mapped):
    cls = "line nm" if is_not_mapped else "line"
    return ('<div class="%s" id="%s"><span class="lid">%s</span><span class="markcol">%s</span>'
            '<span class="speaker">%s</span><span class="text">%s</span></div>') % (
        cls, esc(ln.id), esc(ln.id), esc(ln.mark), esc(ln.speaker), mark_line(ln.text, spans))

def build_notes_html(out):
    m = out["meeting"]
    title, date = m["title"], m["date"]
    heading = esc(title["quote"]) if isinstance(title, dict) else "Meeting (title not in source)"
    if isinstance(date, dict):
        date_html = '"%s" (%s)' % (esc(date["quote"]), cite_link(date["line"], date["speaker"]))
    else:
        date_html = esc(SENTINEL)
    participants = esc(", ".join(m["participants"])) if m["participants"] else esc(SENTINEL)
    parts = ["<h1>%s</h1>" % heading, "<p><strong>Date:</strong> %s</p>" % date_html,
             "<p><strong>Participants:</strong> %s</p>" % participants]
    for name, headers, key, row_fn in SECTIONS:
        parts += ["<h2>%s</h2>" % esc(name), html_table(headers, [row_fn(r, True) for r in out[key]])]
    parts.append('<p class="footer">%s</p>' % esc(FOOTER))
    return "\n".join(parts)

# Design: system-ui font (+ monospace ids), 4/8/12/16/24/32/48px spacing scale, muted
# per-category colours, light/dark via prefers-color-scheme, no purple/gradients, JS-free.
STYLE = """
:root{--bg:#fff;--fg:#1a1a1a;--muted:#666;--border:#d9d9d9;--panel:#f6f6f7;--link:#1355a6;--action-bg:#fbe7bd;--action-fg:#5c3d00;--decision-bg:#cfead4;--decision-fg:#134a24;--figure-bg:#cfe0f5;--figure-fg:#123b66;--question-bg:#e4e4ea;--question-fg:#33343b;--nm:#9a9a9a}
@media(prefers-color-scheme:dark){:root{--bg:#15171a;--fg:#e7e7e7;--muted:#9a9a9a;--border:#33363b;--panel:#1c1f23;--link:#8ab4f0;--action-bg:#4a3a10;--action-fg:#f3d78e;--decision-bg:#1f3a26;--decision-fg:#a8dcb2;--figure-bg:#1c3450;--figure-fg:#a9cdf2;--question-bg:#2a2c33;--question-fg:#d0d1d8;--nm:#5a5d63}}
*{box-sizing:border-box} html,body{overflow-x:hidden}
body{margin:0;background:var(--bg);color:var(--fg);line-height:1.5;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.legend{display:flex;flex-wrap:wrap;gap:16px;padding:8px 16px;font-size:.85rem;color:var(--muted);border-bottom:1px solid var(--border)}
.sw{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:4px;vertical-align:middle}
.sw.action{background:var(--action-bg)} .sw.decision{background:var(--decision-bg)} .sw.figure{background:var(--figure-bg)} .sw.question{background:var(--question-bg)} .sw.nm{background:transparent;border-left:3px solid var(--nm)}
.wrap{display:flex;gap:24px;align-items:flex-start;padding:16px}
.transcript,.notes{flex:1 1 0;min-width:0;background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:8px} .notes{overflow-x:auto}
.line{display:flex;gap:12px;padding:4px 8px;border-left:3px solid transparent;border-radius:2px} .line:target{outline:2px solid var(--link)} .line.nm{border-left-color:var(--nm)}
.lid{flex:0 0 auto;color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace} .markcol{flex:0 0 auto;min-width:3em;color:var(--muted)} .speaker{flex:0 0 auto;min-width:8em;font-weight:600}
.text{flex:1 1 auto;white-space:pre-wrap;word-break:break-word}
mark{padding:0 4px;border-radius:2px} mark.action{background:var(--action-bg);color:var(--action-fg)} mark.decision{background:var(--decision-bg);color:var(--decision-fg)} mark.figure{background:var(--figure-bg);color:var(--figure-fg)} mark.question{background:var(--question-bg);color:var(--question-fg)}
h1{margin:0 0 8px;font-size:1.3rem} h2{margin:24px 0 8px;font-size:1rem} table{width:100%;border-collapse:collapse;font-size:.9rem}
th,td{padding:4px 8px;border-bottom:1px solid var(--border);text-align:left;vertical-align:top;word-break:break-word}
a{color:var(--link)} .empty,.footer{color:var(--muted)} .footer{margin-top:32px;font-size:.85rem}
@media(max-width:1100px){.wrap{flex-direction:column;padding:8px} .speaker{min-width:6em} table{font-size:.85rem}}
"""

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title><style>__STYLE__</style></head>
<body>
<div class="legend"><span><i class="sw action"></i>Action</span><span><i class="sw decision"></i>Decision</span><span><i class="sw figure"></i>Figure</span><span><i class="sw question"></i>Question</span><span><i class="sw nm"></i>Not mapped trigger</span></div>
<div class="wrap"><div class="transcript">
__TRANSCRIPT__
</div><div class="notes">
__NOTES__
</div></div>
</body></html>
"""

def build_html(out, lines):
    text_by_line = {ln.id: ln.text for ln in lines}
    spans = collect_spans(out, text_by_line)
    nm_lines = {u["line"] for u in out["not_mapped"]}
    transcript_html = "\n".join(
        render_transcript_line(ln, spans.get(ln.id, []), ln.id in nm_lines) for ln in lines)
    title = out["meeting"]["title"]
    page_title = title["quote"] if isinstance(title, dict) else "Meeting (title not in source)"
    page = PAGE.replace("__STYLE__", STYLE).replace("__TITLE__", esc(page_title))
    return page.replace("__TRANSCRIPT__", transcript_html).replace("__NOTES__", build_notes_html(out))

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True, help="transcript file")
    ap.add_argument("--output", required=True, help="translator JSON record to render")
    ap.add_argument("--md", help="write the Markdown file note to this path")
    ap.add_argument("--html", help="write the HTML view to this path")
    args = ap.parse_args(argv)
    lines = parse_transcript(Path(args.input).read_text(encoding="utf-8"))
    out = json.loads(Path(args.output).read_text(encoding="utf-8"))
    markdown = build_markdown(out)
    if args.md:
        Path(args.md).write_text(markdown, encoding="utf-8")
    if args.html:
        Path(args.html).write_text(build_html(out, lines), encoding="utf-8")
    if not args.md and not args.html:
        print(markdown)
    return 0

if __name__ == "__main__":
    sys.exit(main())
