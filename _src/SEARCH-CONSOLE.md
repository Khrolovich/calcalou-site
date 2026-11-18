# Search Console and Bing Webmaster: what the browser task needs

Site: https://calcalou.com (GitHub Pages, custom domain, `CNAME` in repo root). Sitemap: https://calcalou.com/sitemap.xml.

## Google Search Console
- Preferred: **Domain property** `calcalou.com`, verified by a **DNS TXT** record (`google-site-verification=<token>`) at the domain's DNS host. It covers http/https and every subdomain. No repo change.
- Alternative: **URL-prefix property** `https://calcalou.com/`, verified by an **HTML file**. Google gives `google<token>.html`; save it to the repo root with exactly the content Google shows (`google-site-verification: google<token>.html`), commit, deploy, then press Verify. Needs the token first.
- Then: submit `sitemap.xml`; inspect `/`, `/protein-tracker-app/`, `/protein-calculator/` and request indexing.

## Bing Webmaster Tools
- Fastest: **Import from Google Search Console** (needs GSC verified first and the same Google login). No repo change.
- Otherwise: **XML file** `BingSiteAuth.xml` in the repo root (content `<users><user>TOKEN</user></users>` as Bing shows it), or a **CNAME** DNS record (host and target shown by Bing), or a `<meta name="msvalidate.01">` tag (would need a template change).
- Then: submit `sitemap.xml`.

## IndexNow
- Key file already live: `/0d795eff62fe5b776c30c6c96494f0a1.txt` (content equals the file name). After deploy, ping `https://www.bing.com/indexnow?url=<page>&key=0d795eff62fe5b776c30c6c96494f0a1` for new URLs (or POST a URL list to `https://api.indexnow.org/indexnow` with `keyLocation`). Google does not use IndexNow.

## What to hand back
The token (or confirmation that DNS/import was used), so an HTML or XML file can be added in a one-line commit. Which DNS host serves calcalou.com is not recorded in this repo.
