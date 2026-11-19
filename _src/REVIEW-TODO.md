# Review TODO before deploy

The site deploys only when 1.7 is live (it states 1.7 features and carries the 1.7 privacy policy). Then:

1. Codex pass (quota back after 2026-11-20) over: the protein calculator (`assets/protein.js`, `i18n/protein/*`), `SITE-1.7-CLAIMS.md`, and the translations (`i18n/protein/*`, `i18n/protein-landing/*`, the 29 landing keys, `acquisition.json` features). Sonnet wrote the translations from the app glossary; no native review yet.
2. Research results are in `SITE-1.7-CLAIMS.md` («Verification 17.11»): 16 competitor claims confirmed, EFSA 2012 and ISSN 2026 sources confirmed. Open: Lose It! barcode plan wording (keep «check the current plan»); the ISSN 2026 guidance on ideal body weight in obesity was seen only in a news summary, so the pages do not use it.
3. Re-check store/version wording the day 1.7 goes live; replace the 1.4 landing screenshots.
4. Lighthouse was not run (no DevTools Chrome in the authoring session).

## 18.11 publish pass (Vladimir: «заливай сайт»)
- iOS 1.7 went live 2026-11-19: the rollout notice and `IOS_17_PENDING` are removed. `softwareVersion` is still left out of the app JSON-LD; re-add it if wanted.
- Independent review done instead of Codex: Opus (code, SEO) and Fable (claims); findings fixed (iOS wording, meta lengths, «three goals», strength-band attribution, check date 17 Nov, Lose It! barcode hedge). The Codex pass after 20.11 stays.
- Lighthouse (CLI, mobile): performance 100, accessibility 100, SEO 100, best practices 96 on /, /protein-tracker-app/, /protein-calculator/, /what-is-calcalou/, /pl/, /best-protein-tracker/ (the 96 is a localhost-only Cloudflare beacon CORS error).
- Search Console and Bing steps: `SEARCH-CONSOLE.md`.

## 18.11 live
- Live at 6c6b113. IndexNow POST (116 sitemap URLs, key 0d795eff…) returned 200. Live smoke: 116/116 sitemap URLs 200 with canonical, hreflang matching the sitemap and valid JSON-LD (only /delete-account/ has no canonical, as before). Live Lighthouse mobile on / and /protein-calculator/: 100/100/96/100 (96 = Cloudflare beacon CORS console error).
- Still open: the Codex pass after 2026-11-20 (item 1 above).

## 1.8 backlog (site)
- og: og.jpg (en) uses the older bubble card, the 9 other locales use the Today/goal-reached card: unify (also add an icon + name lockup, widen the headline column). Backlog only; see design/store-1.7/v4/NOTES-1.8.md.
- Localized official store badges (9 Apple SVGs, 1 Google Play uk): `_src/BADGES-NEEDED.md`.
