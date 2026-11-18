# Store badges still needed

The site needs 9 localized App Store badges and 1 Google Play badge (uk). Every page shows the English App Store badge, and uk also shows the English Play badge. Checked 18.11.2026 against `assets/img` and `_src/vendor/badges`; nothing was downloaded.

## What exists and what to add

| Locale | App Store now | App Store needed | Google Play now | Google Play needed |
|---|---|---|---|---|
| en | English (`app-store-en.svg`) | none | English | none |
| pl | English copy | Polish SVG | Polish ("Pobierz z") | none |
| de | English copy | German SVG | German ("Jetzt bei") | none |
| es | English copy | Spanish (Spain) SVG | Spanish ("Disponible en") | none |
| fr | English copy | French SVG | French ("Disponible sur") | none |
| it | English copy | Italian SVG | Italian ("Disponibile su") | none |
| pt-BR | English copy | Portuguese (Brazil) SVG | Portuguese (Brazil) ("Disponível no") | none |
| ru | English copy | Russian SVG | Russian ("Скачать из") | none |
| tr | English copy | Turkish SVG | Turkish ("İndirin") | none |
| uk | English copy | Ukrainian SVG | **English copy** (`HOME_LOCALES` maps uk to `en`) | **Ukrainian PNG** |

## Official sources

- **Apple:** the "Download on the App Store" badge, black, localized SVG. Guidelines: https://developer.apple.com/app-store/marketing/guidelines/. Download page: the App Store badge download page linked from those guidelines (Marketing Resources).
- **Google:** the "Get it on Google Play" badge, localized PNG. Source: https://play.google.com/intl/en_us/badges/ (choose the language and download the PNG).

Neither URL was opened on 18.11.2026 (no web access in that session): confirm both are live before downloading.

## Where to put the files

Drop the files into `_src/vendor/badges/`, then run `python3 _src/make_assets.py`. It writes the site files to `assets/img/` and the widths to `_src/assets.json`.

- **Google Play, uk:** `google-play-uk.png`, the official PNG as downloaded. `make_assets.py` crops the transparent margin and writes `badge-google-play-uk-50.webp` and `-100.webp` (50 and 100 px high). It also records `assets.json["googlePlay"]["uk"] = [width at 50 px, 50]`; today every Play badge is `[168, 50]`. Then change uk's badge code from `"en"` to `"uk"` in `HOME_LOCALES` in `_src/build.py`.
- **App Store:** `app-store-<code>.svg` for pl, de, es, fr, it, pt-br, ru, tr, uk (lowercase, the same codes as the Play files). The pipeline cannot use them yet:
  - `make_assets.py` copies only `app-store-en.svg` to `assets/img/badge-app-store.svg`.
  - Templates hard-code `width="150" height="50"` in `template_home2.html`, `calc.html`, `food.html`, `go.html` and the static `i/index.html`.
  - Localized Apple badges have different widths. Wiring them needs per-locale files `badge-app-store-<code>.svg` and an `assets.json["appStore"]` width table, like `googlePlay`. That is a small follow-up code change once the files are in.
