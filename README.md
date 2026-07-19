# jameskostohryz.com

The personal site of **James A. Kostohryz** — independent investment strategist and author.
A fast, owned, static site hosted on GitHub Pages. No CMS, no database, no build framework.

The whole site is designed around **one idea**: publishing a report is a *file drop*.
An automated task generates an HTML report, commits it to `reports/`, and pushes.
Everything else — sorting, the listing, the homepage links — updates itself.

---

## The publishing contract (the important part)

> **To publish a report: put one HTML file in `reports/`, commit, push. That's it.**
> Never edit the index, the navigation, or any listing by hand.

### 1. Name the file

```
reports/<type>_<YYYY-MM-DD>[-<variant>].html
```

| part      | required | notes                                                            |
|-----------|----------|------------------------------------------------------------------|
| `type`    | yes      | `daily` · `weekly` · `geo` · `special` · `method` (others allowed) |
| `date`    | yes      | ISO `YYYY-MM-DD` — this is what sorts the report                  |
| `variant` | no       | e.g. `am`, `pm`, or a slug, to disambiguate same-day reports     |

Examples:

```
reports/daily_2026-07-19.html
reports/weekly_2026-07-19.html
reports/geo_2026-07-19-am.html
reports/special_2026-07-22-oil-shock.html
```

`type` → badge/label mapping lives in `build/build_reports.py` (`TYPE_MAP`).
Unknown types still list; they just get a neutral badge.

### 2. (Optional) Add metadata for a nicer card

The report is a normal, self-contained HTML file. If you add these `<meta>` tags to its
`<head>`, the hub card gets a proper headline and teaser. If you don't, the script falls
back to the `<title>`, the first paragraph, and the filename — so a bare file still works.

```html
<meta name="report:title"   content="Daily Market Brief — Oil Shock Watch">
<meta name="report:summary" content="One-line teaser shown on the card.">
<meta name="report:type"    content="Daily Market Brief">   <!-- overrides the label -->
<meta name="report:date"    content="2026-07-19">           <!-- overrides the filename date -->
```

> Tip for double-quoted `content`: apostrophes inside are fine (the parser matches the
> opening quote). No need to escape them.

### 3. Commit & push

```bash
cp my_new_brief.html reports/daily_2026-07-20.html
git add reports/daily_2026-07-20.html
git commit -m "Daily brief 2026-07-20"
git push
```

On push, GitHub Actions (`.github/workflows/deploy.yml`) runs `build/build_reports.py`
to regenerate `reports/reports.json`, then deploys the whole site to Pages. The reports
hub reads that JSON and rebuilds its list — newest first — with zero manual editing.

---

## How it fits together

```
index.html            Home — the front door (three doors: Reports · Method · About)
about.html            About / Bio — credibility infrastructure
method.html           The AEG method + mispricing lens + case studies
contact.html          Work with me — subscribe · consulting · media
reports/
  index.html          Reports hub SHELL (fixed — renders reports.json; never hand-edit)
  reports.json        GENERATED manifest (rebuilt on every push by the build script)
  *.html              The dropped, self-contained report files
build/
  build_reports.py    Scans reports/*.html -> writes reports.json  (stdlib only)
assets/
  site.css            The house brand (navy #123a5e, gold #c9a94e)
  site.js             Mobile nav toggle
  headshot.jpg        Portrait
.github/workflows/
  deploy.yml          Regenerate manifest + deploy to Pages on push
CNAME                 jameskostohryz.com
.nojekyll             Serve files as-is (no Jekyll processing)
```

`reports.json` is committed as a working fallback, but it is authoritatively regenerated
on every deploy — you never need to touch it.

---

## Run it locally

```bash
python build/build_reports.py          # regenerate reports/reports.json
python -m http.server 8000             # then open http://localhost:8000
```

---

## Deploy setup (one time)

1. Create the repo `jameskostohryz-site` under the `JamesKostohryz` account and push this folder.
2. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
3. DNS for `jameskostohryz.com`: point an `ALIAS`/`ANAME` (or four `A` records) at GitHub
   Pages, and a `CNAME` for `www` → `JamesKostohryz.github.io`. The `CNAME` file here sets
   the custom domain. Enable **Enforce HTTPS** once the cert issues.

---

## Email capture

The reports hub carries a light, dismissible "get these in your inbox" prompt — an *offer,
never a toll*. It never gates the free reports. It currently stores submissions client-side
as a stub; wire the form in `reports/index.html` (`#capForm`) to a list provider
(Buttondown, ConvertKit, Mailchimp) when ready — replace the stub handler with a POST to the
provider's form endpoint.

---

## Notes

- Reports are standalone HTML and are listed **as-is** — the site never rewrites them.
- No paywall (deliberate, for reach). No countdown timers or aggressive CTAs (deliberate,
  for credibility). Add the course / options service by linking out when they're live.
- For informational and educational purposes only. Nothing here is investment advice.
