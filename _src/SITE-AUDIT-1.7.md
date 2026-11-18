# Home page audit for 1.7 (en `/`, 18.11.2026)

**Verdict: the live home looked like a 1.4 page. Its pictures showed the old UI and old numbers, and protein, the 1.7 headline feature, sat below four older feature blocks.** Stage 1 rebuilds only the en home (`_src/template_home2.html`). Other locales are unchanged.

Inputs: `~/Temp/calcalou-site-live/audit/home-{desktop,mobile}-before.png`; the approved 1.7 store set (`design/store-1.7/v4/out/ios/iphone-large/en-US/01–05`); competitor store screenshots (`design/benchmarks/store-screenshots/2026-11-17/`: Cal AI, MacroFactor, Yazio, Lose It!, MyFitnessPal).

## Findings on the live home
- **Hero:** "Tell Lou what you ate" leaves out protein. The visual is a fake dark counter showing 2 320 left, 1 780 eaten, 2 100 burned. Those are not DEMO-DATA numbers, and the demo profile has burn off.
- **Screenshots:** all six are 1.4 captures (2 320 left, Level 11, 540 kcal salad). None shows the protein ring. Device frames are inconsistent.
- **Protein story:** three text chips, after four older feature blocks. No 1.7 screen backs them up.
- **CTA:** official badges and the sticky bar work. The rollout notice is honest.
- **Social proof:** the one real item, GoodPick Media "App of the Week", appeared only in the footer.
- **FAQ:** good. The JSON-LD matches the visible text.
- **Speed:** fine, with a light page and system fonts.
- **Mobile:** the counter takes most of the first screen and no product UI is visible.
- **Mascot:** 5 of 6 `lou-*` files were generated from sources identical to the app's v7.1 `cream/3d` set (PNG hashes match). `lou-curious` came from an older render. It is now regenerated from the app file, with the same crop and size, so no HTML changed. Other locales show it too.
- **Store consistency:** the store set leads with "Hit protein. Stay in calories." and uses 620 left and 124 g with the goal reached. The site did not match.

## Store benchmarks (from files)
Top apps show a real device frame or real UI on frame 1, use a 2 to 6 word headline, and put callouts on the product. Cal AI leads with its Today dashboard, then the photo scan. Yazio leads with Today plus a food photo. MacroFactor and MyFitnessPal lead with brand and macros. Cal AI, Lose It! and MyFitnessPal show the food itself in their scan frames.

**Competitor websites: no captures exist yet.** Any claim about competitor sites is from general knowledge and unverified. For example: big headline on the left with phone mockups on the right, and real awards placed near the CTA.

**Captures for the research session:** hero, first screenful and mobile (390 px) of calai.app, macrofactor.com, yazio.com, loseit.com. Also 1 or 2 design-led app sites, for example Duolingo and Finch.

## Prioritised improvements
| # | Pri | Change | Why | Stage 1 |
|---|---|---|---|---|
| 1 | P1 | Hero: protein and calories promise, real 1.7 Today in one device frame, Lou v7.1, fake counter removed | First screen must show the product and the 1.7 story | done |
| 2 | P1 | Every image is a 1.7 capture or approved 1.7 store art with DEMO-DATA numbers | Old numbers contradict the store page | done |
| 3 | P1 | Protein section second on the page: widget render, 72 kg × 1.2 g/kg = 86 g, per-food macros, free barcodes, links to calculator and guide | 1.7 differentiator, and the SEO pages need internal links | done |
| 4 | P1 | GoodPick "App of the Week" next to the hero CTA | The only real social proof | done |
| 5 | P2 | Feature rows: photo scan (Premium, 50 a day, 18+), barcode (free), achievements, shown as crops of the approved 1.7 store art (plate photo, viewfinder). Raw captures not used: the scan and barcode frames are mostly empty, and Progress has challenge counters (0/3, 0/7) that contradict DEMO-DATA | Real product moments instead of text chips | done |
| 6 | P2 | Grid of the smaller features (widgets, water, reminders, export, Health, sync, 41 languages, privacy). Siri dropped (no row in the claims list) | Truthful and scannable | done |
| 7 | P2 | Roll the design out to the other 8 locales once en is approved | Same 1.7 gap | no (stage 2) |
| 8 | P2 | Check og.jpg against the 1.7 design and redo it if it predates 1.7 (not opened in this audit) | Share previews should match the page | no |
| 9 | P3 | Short looping video of the scan flow in the photo-scan row | Motion explains the scan fastest | no |
| 10 | P3 | Compare design against the competitor site captures above | Benchmark is store-only so far | no |

Not done: the page is an unapproved stage-1 unit. Before any publish it needs a design-gate seal and Vladimir's review.
