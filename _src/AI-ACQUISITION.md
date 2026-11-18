# Calcalou AI acquisition

Local-only change; publishing remains with the owner. Product copy describes **1.7** and explicitly warns about store rollout: Apple Lookup still showed 1.6.0 on 16 November 2026. No aggregate ratings were invented.

Publication dependency: this branch is based on `policy-1.7` (`d2b7474`), so it also includes the three pending privacy-policy commits above `main`. Their existing release decision ties publication to the 1.7 submission/privacy approval. Review that dependency before pushing this branch to the published site.

Sources: `acquisition.json` (ten product-guide locales), `acquisition.py` (source-linked English comparisons, schema, llms summaries), `acquisition.html`, `assets/guide.css`. `build.py`, `page_sets()`, `check_locales.py` and `seo.py` include the new pages. Comparisons and the protein guide intentionally use English; the key product page covers EN/PL/DE/ES/FR/IT/PT-BR/RU/TR/UK.

Attribution lives in `assets/landing.js`, mirrored for static campaigns by `build.store_links()`. Known AI referrer/UTM → `ct=ai_<assistant>`, Apple provider `128407090`, nested Play `utm_source/medium/campaign`; top-level Play UTMs also support listing reports. Internal links preserve a known source without storage. Generic `/go/ai?src=…`, source-specific smart links and QR assets use the existing Firebase wildcard redirect. Invite codes remain inside Play's referrer.

The existing Cloudflare beacon emits ordinary page views on new pages. It has no custom-event/UTM API; no synthetic endpoint or new pre-consent tracking was added. Cloudflare's [FAQ](https://developers.cloudflare.com/web-analytics/faq/) explains this limit. Source-specific smart-link paths and store campaigns supply the additional breakdown.

Checked vendor references before implementation: [OpenAI bot definitions](https://developers.openai.com/api/docs/bots), [Anthropic bot definitions](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler), [Google AI search guidance](https://developers.google.com/search/docs/appearance/ai-features), [Apple campaign links](https://developer.apple.com/help/app-store-connect-analytics/acquisition/campaign-links/), [Google Play report definitions](https://support.google.com/googleplay/android-developer/answer/9859173). Competitor sources are linked directly in each generated page.

Verification: regenerate with the repo's existing Jinja2 environment, run `seo.py`, Python unit tests, Node tests and `check_locales.py`. Tests cover visible FAQ/JSON-LD equality, product schema/real offers, crawler permissions, local links, locale coverage, campaign parity, exact referrer hosts, unknown inputs, no automatic article redirect, existing campaigns, smart links and invitation preservation.

Final foreground verification on 16 November: the complete suite passed through `heavy.py` (40 Node tests, 44 Python tests, 123 generated pages and `check_locales.py`, all exit 0). Put the existing site Jinja2 virtualenv on PATH for Node’s child Python. Evidence: the private marketing workspace (`resume-checks-latest.json`). Public indexing and genuine store-install attribution remain post-publication checks.

The final copy audit removed blanket 7-day trial promises from the nine existing landing locales, including visible FAQs and JSON-LD. The current product decision limits the trial to the annual plan; actual eligibility is shown by the store. No subscription configuration changed.

Full reporting instructions, consent limits and residual post-publication/store checks: the private product docs (`ai-acquisition.md`). Research and approved-publication drafts remain outside this Git repo in the private marketing workspace.
