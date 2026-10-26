# Playground WordPress theme

A classic WordPress theme built from the static prototype. It uses the same stylesheet, scripts, images and bilingual copy (`content/en.json`, `content/pt.json`), so the two versions stay consistent.

Tested on WordPress 6.5 with PHP 8.3. Requires WordPress 6.3 or newer and PHP 7.4 or newer.

## Installation

1. Upload `playground-theme.zip` in **Appearance → Themes → Add New → Upload**, then activate it.
2. Install and activate **Polylang** (free). In **Languages**, add English (`en`) and Português (`pt_PT`, slug `pt`). Set the URL option to "The language is set from the directory name" so addresses look like `/en/...` and `/pt/...`.
3. In Polylang settings, under **Custom post types and taxonomies**, make sure *Case studies*, *Sectors* and *Work type* are ticked (the theme registers them automatically).
4. Go to **Tools → Playground setup** and click **Import content**. This creates every page, the four case studies and the first insight article in both languages, links each translation and sets the home and insights pages.
5. Go to **Settings → Permalinks** and click Save once.
6. Go to **Appearance → Customize → Playground: LinkedIn & contact** and fill in the LinkedIn company URL and the email that should receive contact form messages.
7. Install **WP Mail SMTP** so contact form emails are delivered reliably.

## How the team publishes

| Content | Where in WordPress | Notes |
| --- | --- | --- |
| Insights | Posts | Add a category (shown as the tag), an excerpt and a featured image. Translate with the Polylang "+" icon. |
| Case studies | Case studies | Title, excerpt, featured image, plus the *Case study details* box: client, year, location, challenge, approach, deliverables, results (`value | label` per line), quote. Assign a Sector and Work type. Use *Order* to control position. |
| Pages | Pages | Expertise, Sectors, About and Contact use their own templates. Text in the editor is added below the designed sections. |
| Fixed marketing copy | `content/en.json` and `content/pt.json` | Hero text, services, sectors, values. Change through a developer, or move to custom fields in a later phase. |

Work filters on the case study archive use the Work type slugs `strategy`, `engagement`, `campaigns` and `events`. Portuguese terms use the same slug with `-pt`.

## LinkedIn integration

What is included:

- **Share buttons** on every case study and article ("Share on LinkedIn" and "Copy link"). Also available anywhere with the `[linkedin_share]` shortcode.
- **Correct LinkedIn previews.** Each page outputs absolute `og:title`, `og:description` and `og:image`. Featured images are used when present. Check any URL with LinkedIn's Post Inspector before sharing.
- **"Follow the conversation" block** on the home page, Insights and articles, with a Follow button. By default it lists the latest insights. To show real LinkedIn posts instead, paste up to three post URLs (or embed URLs, from the post's "Embed this post" menu) in the Customizer field. Also available with the `[playground_linkedin]` shortcode.
- **LinkedIn Insight Tag** for campaign measurement and retargeting. Add the partner ID in the Customizer. It only loads after the visitor accepts the cookie banner.
- Company page linked in the footer, contact page and structured data (`sameAs`), which helps Google connect the site with the LinkedIn page.

What is not included, and why:

- **An automatic live feed of the company page.** LinkedIn only allows this through its Community Management API, which requires an approved developer application. The practical options are pasting post URLs (included), or a paid widget such as SociableKIT, Elfsight or Juicer, which can be dropped into the block if you want it fully automatic.
- **Automatic posting from WordPress to LinkedIn.** Jetpack Social, Buffer or Zapier can publish new posts to the company page. I recommend keeping a person in the loop: publish on the site, then write the LinkedIn post by hand with the link. It reads better and brings traffic back to the site.

## Files

```
playground/
  style.css, theme.json, functions.php
  inc/content.php        language helpers and JSON content
  inc/case-studies.php   case study post type, sectors, work types, fields
  inc/linkedin.php       Customizer settings, embeds, shortcodes
  inc/contact.php        contact form handler (nonce, honeypot, consent)
  inc/setup-content.php  Tools → Playground setup importer
  front-page.php, page-*.php, archive-case_study.php, single-case_study.php,
  home.php (insights), single.php, page.php, 404.php
  template-parts/        hero, CTA, LinkedIn block, share bar, cards
  css/, js/, assets/, content/   copied from the static build by build.py
```

Do not edit `css/`, `js/`, `assets/` or `content/` inside the theme directly. Edit `src/` and `content/` at the repository root, then run `python3 build.py`, which updates both the static site and the theme.
