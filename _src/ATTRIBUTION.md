# Store-link attribution

One token, `ct`, names where an install came from. Every channel links to a smart link
`https://calcalou.com/go/<channel>/` (below) or to `https://calcalou.com/?ct=<ct>`; the site is the only place
that turns a `ct` into store parameters, so the scheme changes in one place.

## Smart links `/go/<channel>/`

`_src/go.json` maps a channel to its `ct`, one line each; `python3 _src/build.py` writes `go/<channel>/index.html`
and caches its QR code in `_src/qr/<channel>.svg` (macOS CoreImage via `_src/tools/qr.swift`). The page is
counted by Cloudflare Web Analytics as a view of `/go/<channel>/` (so clicks per channel need no custom events),
then a phone goes to its store with the channel's attribution; desktop and no-JS visitors stay on a page with
both store badges and a QR code of the same link. The redirect waits for the beacon to load (+0.4 s, at most
1.5 s) and runs at once when no beacon is configured. Pages are `noindex` and not in the sitemap.

Channel names: `yt`, `ig`, `tt`, `fb`, `site`, `creator-<name>` (ct `cr-<name>-<lang>`), `doctor-<id>`
(ct `doctor-<id>`).

| Store | Parameters |
|---|---|
| App Store | `?pt=128407090&ct=<ct>&mt=8` (campaign token, max 40 characters `A-Za-z0-9_-`) |
| Google Play | `&referrer=` URL-encoded `utm_source=<source>&utm_medium=<medium>&utm_campaign=<ct>` |

`<source>` and `<medium>` come from the part of `ct` before the first `-`
(`CHANNELS` in `assets/landing.js`, mirrored by `store_links()` in `build.py`; a test keeps them equal):

| ct prefix | utm_source | utm_medium | ct format | example |
|---|---|---|---|---|
| `web` | calcalou.com | referral | `web-<page>[-<lang>]` | `web-calc-en`, `web-food-banana-pl`, `web-site`, `web-press` |
| `yt` | youtube | social | `yt-r<round>-ep<NN>`, `yt-<variant>-<lang>-<name>` | `yt-r1-ep07` |
| `tt` | tiktok | social | `tt-<variant>-<lang>-<name>` | `tt-a-en-calcaloo` |
| `ig` | instagram | social | `ig-<variant>-<lang>-<name>` | `ig-a-en-calcaloo` |
| `fb` | facebook | social | `fb-<variant>-<lang>-<name>` | `fb-a-en-calcaloo` |
| `reddit` | reddit | social | `reddit-<sub>-<lang>-<name>` | `reddit-other-en-calcaloo` |
| `cr` | creator | social | `cr-<creator>-<lang>` | `cr-airfry-de` |
| `links` | linkinbio | social | `links` (bio page without `ct`) | `links` |
| `share` | app-share | referral | `share-<what>` | `share-ach` |
| `invite` | app-invite | referral | `invite` (the `/i/` page adds `&invite=<code>` to the Play referrer, read by the app) | `invite` |
| `doctor` | doctor | referral | `doctor-<id>` | `doctor-krakow01` |
| anything else | the prefix | other | add a row instead | |

A new channel is a new row in `CHANNELS` and in `build.py`; the node tests fail until both match. Every
`<a href>` to a store on any page must carry these parameters (`landing.test.js` scans all HTML).

## Web analytics

Cloudflare Web Analytics (cookieless, no consent banner) on every generated page, the `/go/` links and on
`links/`, `i/`, `press/` and `404.html` (not on the Jekyll pages `privacy/`, `support/`, nor `delete-account/`). Set `CF_BEACON_TOKEN` in `build.py` to the site token from the Cloudflare dashboard
and run `python3 _src/build.py`; with an empty token no beacon is rendered. Visitors who arrive on a phone
with `?ct=` go straight to the store, so that traffic shows up in the store consoles by `ct`, not in web
analytics.

## Server-side click counts (`calcalou-go`)

Bio links point at `https://calcalou-go.web.app/go/<channel>` (Firebase Hosting site `calcalou-go`, project `calorie-tracker-96de2`, config in `_src/go-hosting/`). It 302s to `https://calcalou.com/go/<channel>/`, which picks the store.

- Counting: log-based metric `logging.googleapis.com/user/go_link_clicks`, label `channel`, from Hosting's Cloud Logging (`cloudLoggingEnabled` on the site).
- Privacy: exclusion `go-links-no-raw` on the `_Default` sink drops every `calcalou-go` request record, so no IP or user agent is stored; the metric still counts them.
- Read counts: Cloud Console → Metrics Explorer → `go_link_clicks`, group by `channel`.
- Deploy: `cd _src/go-hosting && firebase deploy --only hosting:calcalou-go`.
