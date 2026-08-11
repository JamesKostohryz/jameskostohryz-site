# Deployment — read this before touching DNS or the CNAME file

*Written 11 August 2026, when the site was first pushed to GitHub.*

## Where things actually stand

| | |
|---|---|
| `jameskostohryz.com` | served by **Vercel**, with **different content** from this repo (its title is "JK Investment \| Strategic Investment & Business Development") |
| This repo | GitHub Pages, at `https://jameskostohryz.github.io/jameskostohryz-site/` |

They are two separate sites. Pushing here does **not** change what visitors to
jameskostohryz.com see. Until DNS moves, this repo is the staging site.

Earlier notes claimed the domain was already served from Pages out of this
folder. It was not — the folder had never been pushed to GitHub at all.

## The CNAME file was deliberately removed

`CNAME` used to contain `jameskostohryz.com`.

**A `CNAME` file makes GitHub Pages redirect the `github.io` URL to the custom
domain.** With DNS still pointing at Vercel, that redirect would have sent every
visitor to the `github.io` address straight back to the Vercel site — the Pages
deployment would have been unreachable. So the file is gone for now.

## Cutting the domain over to Pages, when you want to

Do these in order. Step 3 is the switch; everything before it is reversible.

1. **Restore the CNAME file.** Create a file named `CNAME` at the top of this
   repo containing exactly one line, `jameskostohryz.com`, then commit and push.
2. **Set the custom domain in GitHub.** Repo → **Settings** → **Pages** →
   *Custom domain* → type `jameskostohryz.com` → **Save**.
3. **Point DNS at GitHub.** At your DNS provider, replace the Vercel records for
   the apex with GitHub's four A records —
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` —
   and set `www` as a CNAME to `JamesKostohryz.github.io`.
   *(Confirm these addresses against GitHub's current documentation first; they
   have changed before.)*
4. **Wait for the certificate**, then tick **Enforce HTTPS** on the same Pages
   settings screen. It can take up to an hour.
5. **Remove the Vercel project** only once the domain resolves to Pages and the
   site loads correctly over HTTPS. Not before.

After step 3 the portfolio dashboard becomes `https://jameskostohryz.com/portfolio/`
with no further work — that is the URL to put in the trade-post caption.

## The portfolio dashboard

`portfolio/index.html` is unlisted: it carries `<meta name="robots" content="noindex, nofollow">`
and nothing on the site links to it. To make it public, remove that meta tag and
add a nav entry to `index.html`, `about.html`, `method.html`, `contact.html` and
`reports/index.html`.

It reads its data at load time from the public feed repo
`JamesKostohryz/trs-portfolio-feed`, refreshed by `python scripts/publish_feed.py`
in the `trs-portfolio` repo. The page itself never needs editing to show new
numbers — publish the feed and it updates.
