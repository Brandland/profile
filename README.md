# Playground website

Bilingual (English and European Portuguese) website for Playground, in two forms:

- **`site/`** is the static version, ready to preview or host on any web server. Open `site/index.html`; it sends visitors to `/en/` or `/pt/` based on their browser language.
- **`wordpress/playground/`** is the WordPress theme for publishing. See [`wordpress/README.md`](wordpress/README.md). An installable zip is at `wordpress/playground-theme.zip`.

The review of the original site and the list of open items is in [`IMPROVEMENTS.md`](IMPROVEMENTS.md).

## Editing

All copy lives in `content/en.json` and `content/pt.json`. Site settings (base URL, LinkedIn URL, Insight Tag ID, form endpoint) are in `content/site.json`. Styles, scripts and images are in `src/`.

After any change, run:

```
python3 build.py
```

This regenerates `site/` and refreshes the assets and content inside the WordPress theme. Then rebuild the zip:

```
cd wordpress && rm -f playground-theme.zip && zip -rq playground-theme.zip playground
```

## Preview locally

```
cd site && python3 -m http.server 8000
```

Then open http://localhost:8000.

## Pages

Home, Expertise, Sectors, Work, four case studies, About, Insights, one article, Contact and Privacy, in each language.

## Notes

The case studies, leadership names, phone number and LinkedIn URL are placeholders and must be confirmed before launch. On the static site the contact form only shows a thank you message unless `contact_endpoint` in `content/site.json` points to a form service (for example Formspree). The WordPress version sends real emails.
