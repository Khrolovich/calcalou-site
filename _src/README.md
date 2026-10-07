# Landing page sources (not published: Jekyll skips `_src/`)

- `template.html` + `i18n/<locale>.json` → `python3 _src/build.py` → `/index.html`, `/de/`, `/es/`, `/fr/`, `/it/`, `/pl/`, `/pt-br/`, `/ru/`, `/tr/` (needs `jinja2`).
- `make_assets.py` imports images into `/assets/img` from the Calcaloo project: approved 3D Lou renders (`design/mascot/reference/3d-png`), the app icon, store badges (`vendor/badges`) and store screenshots.
- **Screenshots are the current 1.4.0 (65) set** (`qa-runs/1.4.0-65-store-screenshots/raw/android-phone/<locale>` + the iPhone Today sample). When the final 1.4.0 set is ready: `python3 _src/make_assets.py --shots <set root>` then `python3 _src/build.py`.
- `og.html` is the source of `/assets/img/og.jpg` (1200×630, headless Chrome screenshot).
- Mascot rules: Lou (~1.5 m) stands **behind** the counter (counter hides the lower ~38 % of the render), never sits on it; eyes are solid dark, no whites.
- Copy: only features the app really has (store descriptions are the source). English is the source of truth; keep keys identical in every locale (the build fails otherwise).
- Store routing: `/assets/landing.js` keeps the `?ct=` campaign links and the phone redirect of the previous site; `/get/` forwards its query to `/`.
- Checks: `node --test _src/tests/landing.test.js` (store links, ct routing, pages up to date, assets exist, approved mascot only, legal files untouched).
- SEO beyond title/description/OG (hreflang, sitemap, robots, schema, verification) is owned by the SEO session: `seo_head.html` (canonical, hreflang, Twitter tags, schema.org graph; included by `template.html`), `seo.py` (writes `/sitemap.xml`; run after `build.py`), checks `python3 -m unittest discover -s _src/tests -p 'test_*.py'`.
