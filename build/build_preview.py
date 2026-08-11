#!/usr/bin/env python3
"""
build_preview.py — assemble a single self-contained _preview.html for review.

Why: the site is multi-page and the Reports hub renders reports.json via fetch(),
which browsers block over file://. This stitches every page into ONE local file
with a tab bar so the user can double-click _preview.html and click through the
whole site (including a pre-rendered Reports hub) with no server.

Run:  python build/build_preview.py    (from the repo root)
Output: _preview.html  (gitignored; do not deploy)

Top tabs: Home · Reports · Method · RVA · About · Work with me.
AOIG (rva/aoig.html) is included as a pane reachable from the RVA "Subjects"
sidebar, but is intentionally NOT a top tab (it isn't in the real site nav either).
"""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def inner(fn):
    """Body between </header> and the footer, with cross-links rewired to tab switches for the preview."""
    h = (ROOT / fn).read_text(encoding="utf-8")
    body = re.search(r'</header>(.*)<footer class="site-foot"', h, re.S).group(1).strip()
    if fn == "method.html":
        body = body.replace('href="rva.html"', 'href="#" data-p="rva"')
    if fn == "rva.html":
        body = body.replace('href="method.html"', 'href="#" data-p="method"').replace('href="rva/aoig.html"', 'href="#" data-p="aoig"')
    if fn == "rva/aoig.html":
        body = (body.replace('href="../rva.html"', 'href="#" data-p="rva"')
                    .replace('href="../method.html"', 'href="#" data-p="method"')
                    .replace('href="../reports/index.html"', 'href="#" data-p="reports"'))
    return body


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def reports_pane():
    man = json.loads((ROOT / "reports/reports.json").read_text(encoding="utf-8"))
    reps = man["reports"]
    lead, rest = reps[0], reps[1:]
    feature = (f'<div class="feature"><a class="card-link" href="reports/{lead["file"]}">'
               f'<span class="newest">Latest · {esc(lead["type_label"])}</span>'
               f'<h2>{esc(lead["title"])}</h2><div class="meta">{esc(lead["display_date"])}</div>'
               f'<p class="sum">{esc(lead["summary"])}</p></a></div>')
    cards = "".join(
        f'<a class="rcard" href="reports/{r["file"]}"><span class="rtype {r["css"]}">{esc(r["type_label"])}</span>'
        f'<h3>{esc(r["title"])}</h3><div class="rdate">{esc(r["display_date"])}</div>'
        f'<p class="rsum">{esc(r["summary"])}</p><span class="rgo">Read →</span></a>' for r in rest)
    chips = '<button class="chip on">All</button>' + "".join(
        f'<button class="chip">{esc(t["label"])}</button>' for t in man["types"])
    return (f'<section class="reports-head"><div class="wrap"><p class="eyebrow">Research library · Free access</p>'
            f'<h1>Reports</h1><p class="lede" style="max-width:760px">Daily market briefs, weekly reports, and live '
            f'geopolitical desk notes.</p><div class="filters">{chips}</div></div></section>'
            f'<main class="wrap" style="padding-top:34px;padding-bottom:40px">{feature}<div class="rlist">{cards}</div></main>')


def build():
    css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
    pages = {
        "home": ("Home", inner("index.html")),
        "reports": ("Reports", reports_pane()),
        "method": ("Method", inner("method.html")),
        "rva": ("RVA", inner("rva.html")),
        "about": ("About", inner("about.html")),
        "contact": ("Work with me", inner("contact.html")),
    }
    aoig = inner("rva/aoig.html")
    foot = re.search(r'(<footer class="site-foot".*?</footer>)', (ROOT / "index.html").read_text(encoding="utf-8"), re.S).group(1)
    tabs = "".join(f'<button class="pv-tab" data-p="{k}">{v[0]}</button>' for k, v in pages.items())
    panes = "".join(f'<div class="pv-page" id="pv-{k}">{v[1]}</div>' for k, v in pages.items())
    panes += f'<div class="pv-page" id="pv-aoig">{aoig}</div>'
    mono = ('<svg class="mono" width="38" height="38" viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#c9a94e"/>'
            '<text x="20" y="27" font-size="19" font-weight="700" fill="#123a5e" text-anchor="middle" font-family="Georgia,serif">JK</text></svg>')
    html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>PREVIEW · James A. Kostohryz</title>
<style>{css}
.pv-bar{{position:sticky;top:0;z-index:100;background:#0d2c48;color:#fff;display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:8px 16px}}
.pv-bar .pv-lbl{{font:700 11px/1 sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#c9a94e;margin-right:10px}}
.pv-tab{{font:600 14px/1 sans-serif;color:#cfe;background:transparent;border:0;padding:9px 14px;border-radius:7px;cursor:pointer}}
.pv-tab.on{{background:#c9a94e;color:#152535}} .pv-note{{margin-left:auto;font:500 12px/1.3 sans-serif;color:#9fb4c6}}
.pv-page{{display:none}} .pv-page.on{{display:block}}</style></head><body>
<div class="pv-bar"><span class="pv-lbl">Preview</span>{tabs}<span class="pv-note">Local preview · click tabs · AOIG via RVA sidebar</span></div>
<header class="site-head"><div class="wrap nav"><a class="brand" href="#" data-p="home">{mono}<span class="name">James A. Kostohryz<small>Successful Portfolio Strategy</small></span></a><nav class="nav-links"><a href="#" data-p="home">Home</a><a href="#" data-p="reports">Reports</a><a href="#" data-p="method">Method</a><a href="#" data-p="about">About</a><a class="nav-cta" href="#" data-p="contact">Work with me</a></nav></div></header>
{panes}{foot}
<script>
var tabs=document.querySelectorAll('.pv-tab'),pages=document.querySelectorAll('.pv-page');
function show(p){{if(!document.getElementById('pv-'+p))return;pages.forEach(function(x){{x.classList.toggle('on',x.id==='pv-'+p)}});tabs.forEach(function(t){{t.classList.toggle('on',t.dataset.p===p)}});window.scrollTo(0,0);}}
document.addEventListener('click',function(e){{var el=e.target.closest('[data-p]');if(el){{e.preventDefault();show(el.dataset.p);}}}});
show('home');
</script></body></html>'''
    (ROOT / "_preview.html").write_text(html, encoding="utf-8")
    print("Wrote _preview.html")


if __name__ == "__main__":
    build()
