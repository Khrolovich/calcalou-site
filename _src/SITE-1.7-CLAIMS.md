# Site 1.7: claim list with evidence

Branch `site-1.7` (on top of `ai-acquisition`). App source: `~/Projects/Calcalou/worktrees/calcaloo-app-1.7` (branch `release/1.7`, HEAD b0589b2). Checked 2026-11-17.
All paths below are in that worktree unless marked `site`.

## Product claims (checked against the app)

| Site claim | Evidence |
|---|---|
| AI photo scan estimates protein, fat and carbs per food | docs/DECISIONS.md 2026-11-13 «Scan results prefill grams, kcal, protein, fat and carbs for every item», 2026-11-14 «Add ingredient / Add item» fields |
| AI scans are Premium, 50 a day, 3 free scans once | functions/src/quota/daily_quota.ts:58 (`DAILY_LIMIT = 50`); DECISIONS 2026-11-12 «3 free AI scans per account, once»; 2026-11-13 «Premium = only AI scans + no ads» |
| AI scans and Premium purchases are 18+ | DECISIONS 2026-11-14 legal lines (under 18: AI and Premium off) |
| Barcode scanning is free | DECISIONS 2026-11-14 «Barcodes stay FREE»; 2026-11-13 premium line |
| Manual calorie and protein logging is free | DECISIONS 2026-11-12 «Manual logging (kcal + protein) is always free» |
| Protein goal from body weight, calculation shown | lib/l10n/app_en.arb `proteinGoal_weightFormula` = «{weight} ({source}) × {factor}/kg = {grams}»; docs/specs/1.7-protein-goal.md |
| 1.2 g/kg default, 0.8–2.0 g/kg in 0.1 steps, own goal, 100 kg cap | docs/specs/1.7-protein-goal.md lines 5–10, 27; DECISIONS 2026-11-13 «Protein goal stepper 0.8–2.0» |
| Weight from the profile or, if connected, Apple Health / Health Connect | arb `proteinGoal_profileSource`, `proteinGoal_healthOptional` («{healthApp} is optional. You can enter your weight here.») |
| Water: glass or a custom amount in ml, glass size unchanged | arb `water_customAmount*`; DECISIONS 2026-11-14 water rework, 2026-11-15 «WATER DROP PLUS» |
| Several reminders, own time and days | arb `reminders_*`; lib/models/reminder.dart (`ReminderType { meal, water, custom }`); DECISIONS 2026-11-15 reminders |
| Widgets, metric = calories or protein | ios/CalorieWidget (home + accessory families), android `CalorieGlanceWidget.kt`; arb `widget_todayProtein`; DECISIONS line «widgets choose their metric» |
| 41 interface languages | `ls lib/l10n/*.arb` = 41 files |
| Streaks | arb `streak_*`, `streak_infoBody`; DECISIONS 2026-11-13 |
| Export by period (month, quarter, year, all time) | lib/screens/profile_screen.dart `DiaryExportPeriod`; arb `period_*`; DECISIONS 2026-11-15 «CSV export» |
| Sign-in required, never «no account needed» | DECISIONS 2026-11-13 auth + copy lines; site grep for «no account / without signing» is empty |
| Continue with Apple (iPhone/iPad), Google or email | lib/screens/auth/auth_screen.dart (Apple button hidden on Android, email on both) |
| 13+ | DECISIONS 2026-10-09 «Calcalou is 13+» |
| Provider-neutral AI wording | no AI vendor named anywhere on the new pages (grep) |

## Protein reference ranges (calculator and landing)

Sources confirmed in «Verification 17.11» below (section B).

| Claim | Source |
|---|---|
| Adult baseline 0.83 g/kg a day | EFSA, Dietary Reference Values for protein, EFSA Journal 2012;10(2):2557, doi:10.2903/j.efsa.2012.2557 |
| Weight loss 1.2–1.6 g/kg a day | ISSN position stand: Aragon AA et al., J Int Soc Sports Nutr 2026;23(1):2740266, doi:10.1080/15502783.2026.2740266 (point 6, general population) |
| Strength training 1.6–2.2 g/kg a day | same ISSN 2026 stand, «with resistance training» |
| Cap at 100 kg | app heuristic (spec line 27), stated as «as in Calcalou» |

The 2017 ISSN stand (1.4–2.0 g/kg, doi:10.1186/s12970-017-0177-8) is not used on the pages. The GLP-1-therapy advisory and the US RDA line are not on any public page. All ranges are shown as general guidance, not medical advice. The app's own default (1.2 g/kg) and stepper (0.8–2.0) are product facts, not claims about needs.

## Open for a research session (web checks this session may not do)

- Competitor claims (a research session is checking; remove or soften what it cannot confirm) on the four `/compare/` pages and `/best-protein-tracker/` (written by the Codex run, 2026-11-16): each must match its linked official page. Pairs: MyFitnessPal plan page (barcode scanner under Premium, Meal Scan under Premium, macros by gram, Premium+ meal planning), Lose It! Snap It (Premium and English device language), Cronometer Basic (unlimited barcode scanning, up to 95 nutrients), Cal AI home page (photo estimates, barcodes). Plain `curl` gets 403/429 from MyFitnessPal, Lose It!, EFSA and doi.org; Cronometer and Cal AI answer 200.
- GoodPick Media «App of the Week»: added to the home-page footer (edition 2026-11-16, URL from marketing/video-pipeline/ep51-goodpick-aotw); verified live by the video session.

## Verification 17.11

Checked 2026-11-17 in a real browser (Chrome) against each competitor's own site / help centre; source text: `_src/acquisition.py` `COMPARISONS` + `/best-protein-tracker/` sections. Result: **16 distinct claims — 16 confirmed, 0 wrong, 0 unverifiable.** `/best-protein-tracker/` repeats M3, M5, C1, C2, L3, A1 (no new claims). App-store listings were not needed: every claim is stated on the official page the site links.

### A. Competitor claims

| # | Site claim (page) | Status | Official source | Quote |
|---|---|---|---|---|
| M1 | MFP: broad food diary, partner integrations, paid planning and analysis tools (vs-myfitnesspal summary) | confirmed | [MFP plans](https://support.myfitnesspal.com/hc/en-us/articles/34889191368077-The-difference-between-Free-Premium-and-Premium) | Free: «Linking to Partner Apps ✓✓✓»; Premium: «Food Analysis»; Premium+: «Meal Plan Builder» |
| M2 | MFP free: food and exercise logging, recipes, macro tracking | confirmed | same | «Food & Exercise Logging ✓✓✓», «Create Foods, Meals & Recipes ✓✓✓», «View Macronutrients ✓✓✓» |
| M3 | MFP barcode scanner listed under Premium (also best-protein-tracker) | confirmed | same | «Premium adds faster logging tools like Meal Scan and the barcode scanner»; table «Barcode Scanner ✓✓» (Premium, Premium+) |
| M4 | MFP Meal Scan under Premium | confirmed | same | «Meal Scan ✓✓» (Premium, Premium+) |
| M5 | MFP Premium: macros by gram, different goals by day (also best-protein-tracker) | confirmed | same | «Macros by Gram ✓✓», «Different Goals by Day ✓✓» |
| M6 | MFP Premium+: meal planning and grocery lists | confirmed | same | «Premium+ includes everything in Premium, plus meal planning, meal prep tools, diet preferences, and grocery lists.» |
| L1 | Lose It! help lists food search, Scan It, Snap It, Say It | confirmed | [How to Log Food](https://loseit.zendesk.com/hc/en-us/articles/49210381551380-How-to-Log-Food-in-Lose-It) | «Search for a food by keyword, use Scan It to scan a barcode, use Snap It to take a photo of your food, or use Say It to search for a food by voice*» |
| L2 | Scan It documented as a way to log packaged food; «check the current plan» | confirmed | same + [About Lose It!](https://loseit.zendesk.com/hc/en-us/articles/54516668028564-About-Lose-It) | «Scan It (Barcode Scanner): Scan food packaging directly from your mobile device for instant logging.» |
| L3 | Snap It suggests database matches from a photo (also best-protein-tracker) | confirmed | [How to Use Snap It](https://loseit.zendesk.com/hc/en-us/articles/47771695186580-How-to-Use-Snap-It) | «Lose It! will analyze the photo to find and suggest the best matches in our food database for you to log.» |
| L4 | Snap It needs Premium and English device language | confirmed | same | «This feature is exclusively available to Premium members, and is currently only available if your device's language is set to English.» |
| C1 | Cronometer Basic: calories, macros, vitamins, minerals (also best-protein-tracker) | confirmed | [Cronometer Basic](https://cronometer.com/features/free-nutrition-tracking-app.html) | «Everything you need to track your food, track your macros and track your vitamins and minerals is included in a Cronometer Basic account» |
| C2 | Unlimited barcode scanning in Basic (also best-protein-tracker FAQ) | confirmed | same | «Unlimited use of our Barcode Scanner is included in a Basic account.» |
| C3 | Basic advertises up to 95 nutrients and compounds | confirmed | same | «Track all of your calories and up to 95 nutrients and compounds completely free of charge.» |
| C4 | Basic: custom meals, recipes, connections to other apps and devices | confirmed | same | «Custom Meals and Recipes are included with a Basic account»; «*All apps and device integrations are included in the free version, with the exception of our ChatGPT plugin.» |
| A1 | Cal AI: photo estimates of calories, protein, carbs, fat (also best-protein-tracker) | confirmed | [calai.app](https://www.calai.app/) | «Our AI then analyzes and breaks down your meal to determine calories, protein, carbs, and fat.» |
| A2 | Cal AI lists barcodes, meal descriptions, custom foods, recipes | confirmed | same | «Snap a photo, scan a barcode, or describe your meal»; «You can also add your own foods and recipes.» |

Notes (no change required):
- Lose It! plan status for barcodes is inconsistent across its own help centre: [Unlocking the Barcode Scanner](https://loseit.zendesk.com/hc/en-us/articles/47773984823700-Unlocking-the-Barcode-Scanner-Scan-It) (updated 1 Apr 2026) «We are also in the process of moving the barcode scanner (Scan It) and nutrition label scanner to part of our Premium features. Some free members will still have access as we transition» vs [About Lose It!](https://loseit.zendesk.com/hc/en-us/articles/54516668028564-About-Lose-It) (updated 12 Oct 2026) «The free version includes core calorie logging, barcode scanning…». The page's «check the current plan in Lose It!» hedge is the right wording; do not state either way.
- Lose It! Scan It and Say It are English-only too («*Scan It, Snap It, and Say It are currently only available in English»). Optional: add «English device language» to the Barcodes row.
- C4: the ChatGPT plugin is the one integration Cronometer keeps in Gold; «connections to other apps and devices» stays accurate.

### B. Protein guidance sources (calculator)

| Source | Exact citation | Quoted range |
|---|---|---|
| EFSA PRI (adults) | EFSA Panel on Dietetic Products, Nutrition and Allergies (NDA). «Scientific Opinion on Dietary Reference Values for protein». EFSA Journal 2012;10(2):2557. Adopted 19 Jan 2012, published 9 Feb 2012. doi:[10.2903/j.efsa.2012.2557](https://doi.org/10.2903/j.efsa.2012.2557) · press release [efsa.europa.eu/en/press/news/120209](https://www.efsa.europa.eu/en/press/news/120209) | Abstract: «the PRI for adults of all ages was estimated to be 0.83 g protein/kg body weight per day and is applicable both to high quality protein and to protein in mixed diets»; AR «0.66 g protein/kg body weight per day»; «Intakes up to twice the PRI are regularly consumed from mixed diets by some physically active and healthy adults in Europe and are considered safe.» Press release: «Adults (including older adults) – 0.83 g per kg of body weight per day.» |
| ISSN protein stand (active people, muscle) | Jäger R, Kerksick CM, Campbell BI, et al. «International Society of Sports Nutrition Position Stand: protein and exercise». J Int Soc Sports Nutr. 2017;14:20. doi:[10.1186/s12970-017-0177-8](https://doi.org/10.1186/s12970-017-0177-8) · PMID [28642676](https://pubmed.ncbi.nlm.nih.gov/28642676/) · PMC5477153 | «For building muscle mass and for maintaining muscle mass through a positive muscle protein balance, an overall daily protein intake in the range of 1.4-2.0 g protein/kg body weight/day (g/kg/d) is sufficient for most exercising individuals»; «Higher protein intakes (2.3-3.1 g/kg/d) may be needed to maximize the retention of lean body mass in resistance-trained subjects during hypocaloric periods.» |
| ISSN weight-reduction stand (newer; weight loss + muscle gain) | Aragon AA, Campbell BI, Schoenfeld BJ, et al. «International Society of Sports Nutrition position stand: diets for body weight reduction». J Int Soc Sports Nutr. 2026;23(1):2740266. Published online 13 Oct 2026, open access. doi:[10.1080/15502783.2026.2740266](https://doi.org/10.1080/15502783.2026.2740266) | Position statement point 6: «For the general population, a daily protein intake of 1.2–1.6 g/kg BW is appropriate for supporting total body weight and fat loss, physical activity, and imparting benefits to musculoskeletal and cardiometabolic health.» «Daily protein intakes ranging 1.6–2.2 g/kg BW combined with resistance training may optimize muscle anabolism, while higher intakes of 1.9–3.2 g/kg BW can maximize lean mass retention in lean, resistance-trained individuals sustaining hypocaloric conditions.» |

Notes:
- 18.11 correction: the pages now cite the 2026 ISSN weight-reduction stand (three bands, see 60d5c43); the 2017 stand is not cited. Lines below that say «removed» or «2017» are the earlier state.
- The ISSN row in «Protein reference ranges» above (marked «written from memory, not opened») is now **confirmed**: title, journal, 2017;14:20, DOI and the «1.4–2.0 g/kg/d … sufficient for most exercising individuals» wording all match PubMed 28642676. The EFSA row (0.83 g/kg, press release 120209) is confirmed too; the journal DOI above is the citable primary.
- S2 and the 1.2–1.6 band were already removed in 5e5b9bf. If a weight-loss or muscle-gain band comes back, the 2026 ISSN weight-reduction stand covers both (1.2–1.6; 1.6–2.2 with resistance training). Its title names no drug, and it puts «pharmacotherapy (i.e. GLP-1RAs)» out of scope. Team decision.
- ⚠️ Not checked in the primary text: the guidance to base intake on ideal/target body weight in obesity. It was seen only in a secondary news summary (news-medical.net, 14 Oct 2026). Re-check before citing.
- Calculator copy should keep «a starting point, not medical advice»; these are population/athlete ranges.
