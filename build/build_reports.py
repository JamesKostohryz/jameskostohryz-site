#!/usr/bin/env python3
"""
build_reports.py  —  the file-drop contract for the Reports hub.

WHAT IT DOES
------------
Scans reports/*.html, reads a tiny bit of metadata from each file, and writes
reports/reports.json — the manifest that reports/index.html renders from.

The automated publishing task NEVER edits the index or any navigation. To add a
report, it does exactly one thing: drop an HTML file into reports/ using the
naming convention below, commit, and push. This script (run in CI on every push)
regenerates the manifest, and the hub updates itself.

NAMING CONVENTION (required — this is how a report self-sorts)
--------------------------------------------------------------
    <type>_<YYYY-MM-DD>[-<variant>].html

    type     one of: daily | weekly | geo | method | special   (others allowed;
             unknown types render with a neutral badge)
    date     ISO date, used for reverse-chronological sorting
    variant  optional, e.g. "am", "pm", a slug — disambiguates same-day reports

    examples:  daily_2026-07-19.html
               weekly_2026-07-19.html
               geo_2026-07-19-am.html
               special_2026-07-22-oil-shock.html

OPTIONAL METADATA (nice-to-have — improves the card, never required)
--------------------------------------------------------------------
Put these <meta> tags in the report's <head> for a better headline/teaser:

    <meta name="report:title"   content="Daily Market Brief — Oil Shock Watch">
    <meta name="report:summary" content="One-line teaser shown on the card.">
    <meta name="report:type"    content="Daily Market Brief">   (overrides label)
    <meta name="report:date"    content="2026-07-19">           (overrides filename)

If absent, the script falls back to the <title>, the first paragraph, and the
type/date parsed from the filename. So a bare, self-contained HTML file still
lists correctly — the metadata just makes it look sharper.
"""

import json, re, html, sys
from datetime import datetime, timezone
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

# type key -> (display label, css class used by the badge)
TYPE_MAP = {
    "daily":   ("Daily Market Brief", "daily"),
    "weekly":  ("Weekly Report",      "weekly"),
    "geo":     ("Geopolitical Brief", "geo"),
    "method":  ("AEG / Method",       "method"),
    "aeg":     ("AEG / Method",       "method"),
    "special": ("Special Report",     "special"),
}

NAME_RE = re.compile(
    r"^(?P<type>[a-z0-9]+)_(?P<date>\d{4}-\d{2}-\d{2})(?:-(?P<variant>[a-z0-9][a-z0-9-]*))?\.html$",
    re.IGNORECASE,
)

DESK_PREFIX_RE = re.compile(r"^(oil\s*&?\s*gas desk|jk consulting|successful portfolio strategy)\s*[—–\-:|]\s*", re.I)


def meta(content: str, name: str):
    # match the SAME quote char that opens the attribute (\2 backref) so that an
    # apostrophe inside a double-quoted value doesn't prematurely end the match.
    m = re.search(
        r'<meta[^>]+name=(["\'])%s\1[^>]*content=(["\'])(.*?)\2' % re.escape(name),
        content, re.I | re.S,
    )
    if not m:
        m = re.search(
            r'<meta[^>]+content=(["\'])(.*?)\1[^>]*name=(["\'])%s\3' % re.escape(name),
            content, re.I | re.S,
        )
        return html.unescape(m.group(2).strip()) if m else None
    return html.unescape(m.group(3).strip()) if m else None


def first_paragraph(content: str):
    # strip scripts/styles first
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", content, flags=re.I | re.S)
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", body, re.I | re.S):
        text = re.sub(r"<[^>]+>", "", m.group(1))
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        if len(text) >= 40:
            return text
    return ""


def doc_title(content: str):
    m = re.search(r"<title>(.*?)</title>", content, re.I | re.S)
    if not m:
        return None
    t = html.unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    return DESK_PREFIX_RE.sub("", t) or t


def truncate(text: str, n: int = 190):
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0]
    return cut.rstrip(".,;: ") + "…"


def build():
    reports = []
    if not REPORTS_DIR.exists():
        print("no reports/ directory", file=sys.stderr)
    files = sorted(REPORTS_DIR.glob("*.html"))
    for f in files:
        if f.name.lower() in ("index.html",):
            continue
        m = NAME_RE.match(f.name)
        if not m:
            print(f"  skip (name off-convention): {f.name}", file=sys.stderr)
            continue
        type_key = m.group("type").lower()
        date_str = m.group("date")
        variant = (m.group("variant") or "").lower()

        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  skip (unreadable): {f.name} ({e})", file=sys.stderr)
            continue

        label, css = TYPE_MAP.get(type_key, (type_key.replace("-", " ").title(), "report"))
        label = meta(content, "report:type") or label
        date_str = meta(content, "report:date") or date_str
        title = meta(content, "report:title") or doc_title(content) or label
        summary = meta(content, "report:summary") or truncate(first_paragraph(content))

        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            display_date = dt.strftime("%B %-d, %Y")
        except ValueError:
            dt = datetime.min
            display_date = date_str
        if variant:
            display_date += " · " + variant.upper()

        reports.append({
            "file": f.name,
            "type_key": type_key,
            "type_label": label,
            "css": css,
            "date": date_str,
            "variant": variant,
            "display_date": display_date,
            "title": title,
            "summary": summary,
            "_sort": (date_str, variant),
        })

    # newest first; same-day pm before am so latest-of-day leads
    reports.sort(key=lambda r: (r["_sort"][0], r["_sort"][1]), reverse=True)
    for r in reports:
        r.pop("_sort", None)

    # distinct type filters actually present, in a sensible order
    order = ["daily", "weekly", "geo", "special", "method"]
    present = [t for t in order if any(r["type_key"] == t for r in reports)]
    present += [r["type_key"] for r in reports if r["type_key"] not in order and r["type_key"] not in present]

    manifest = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(reports),
        "types": [{"key": t, "label": TYPE_MAP.get(t, (t.title(),))[0]} for t in present],
        "reports": reports,
    }
    out = REPORTS_DIR / "reports.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out.relative_to(REPORTS_DIR.parent)} — {len(reports)} report(s).")
    return manifest


if __name__ == "__main__":
    build()
