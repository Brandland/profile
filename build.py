#!/usr/bin/env python3
"""Build the static bilingual Playground site.

Reads content/en.json, content/pt.json and content/site.json and writes the
complete site to site/ (site/en/..., site/pt/...). Run:  python3 build.py
"""
import json
import shutil
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "site"
LANGS = ["en", "pt"]
SITE = json.loads((ROOT / "content/site.json").read_text(encoding="utf-8"))
C = {l: json.loads((ROOT / f"content/{l}.json").read_text(encoding="utf-8")) for l in LANGS}

NAV = ["index", "expertise", "sectors", "work", "about", "insights", "contact"]
LI_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>'
LINK_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10.6 13.4a1 1 0 0 1 0-1.4l3.5-3.5a3 3 0 1 1 4.2 4.2l-2 2a1 1 0 1 1-1.4-1.4l2-2a1 1 0 1 0-1.4-1.4l-3.5 3.5a1 1 0 0 1-1.4 0zm2.8-2.8a1 1 0 0 1 0 1.4l-3.5 3.5a3 3 0 1 1-4.2-4.2l2-2a1 1 0 0 1 1.4 1.4l-2 2a1 1 0 1 0 1.4 1.4l3.5-3.5a1 1 0 0 1 1.4 0z"/></svg>'


def href(page):
    return "index.html" if page == "index" else f"{page}.html"


def layout(lang, page_key, path, body, title=None, description=None, depth=1, current=None, og_image="hero-space.webp"):
    """Wrap a page body with head, header and footer. `path` is the page path
    relative to the language folder, e.g. 'work.html' or 'work/slug.html'."""
    c = C[lang]
    ui = c["ui"]
    up = "../" * depth          # to site root
    here = "../" * (depth - 1)  # to language root
    meta = c["pages"].get(page_key, {})
    title = title or meta.get("title", "Playground")
    description = description or meta.get("description", "")
    base = SITE["base_url"].rstrip("/")
    current = current or page_key

    alternates = "".join(
        f'<link rel="alternate" hreflang="{l}" href="{base}/{l}/{path}">' for l in LANGS
    ) + f'<link rel="alternate" hreflang="x-default" href="{base}/en/{path}">'

    nav = "".join(
        f'<a {"aria-current=\"page\" " if current == p else ""}href="{here}{href(p)}">{e(ui["nav"][p])}</a>' for p in NAV
    )
    switch = "".join(
        f'<a href="{up}{l}/{path}" hreflang="{l}" lang="{l}"{" aria-current=\"true\"" if l == lang else ""}>{C[l]["label"]}</a>'
        for l in LANGS
    )
    li = SITE["linkedin_url"]
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Playground",
        "url": base,
        "logo": f"{base}/assets/playground-logo.png",
        "sameAs": [li],
        "address": {"@type": "PostalAddress", "addressLocality": "Maputo", "addressCountry": "MZ"},
    }
    pg_cfg = {"linkedinPartnerId": SITE.get("linkedin_insight_partner_id", "")}
    cookie = c["cookie"]

    return f"""<!doctype html>
<html lang="{c['locale'].replace('_', '-')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{base}/{lang}/{path}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{base}/{lang}/{path}">
<meta property="og:image" content="{base}/assets/{og_image}">
<meta property="og:locale" content="{c['locale']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{up}assets/favicon.png">
<link rel="preload" href="{up}assets/hero-space.webp" as="image">
<link rel="stylesheet" href="{up}css/styles.css">
<script type="application/ld+json">{json.dumps(org)}</script>
<script>window.PG={json.dumps(pg_cfg)};</script>
</head>
<body>
<a class="skip" href="#main">{e(ui['skip'])}</a>
<div class="scroll-progress" aria-hidden="true"></div>
<header class="site-header"><div class="nav-wrap">
<a class="brand" href="{here}index.html" aria-label="{e(ui['home_aria'])}"><img src="{up}assets/playground-logo.png" alt="Playground" width="190" height="55"></a>
<nav class="nav-links" aria-label="Primary">{nav}</nav>
<div class="nav-right">
<div class="lang-switch" role="group" aria-label="{e(ui['lang_switch_label'])}">{switch}</div>
<a class="nav-cta desktop magnetic" href="{here}contact.html">{e(ui['cta'])} <span>↗</span></a>
<button class="menu-toggle" aria-label="{e(ui['menu_open'])}" aria-expanded="false"><span></span><span></span></button>
</div>
</div></header>
<main id="main">
{body}
</main>
<footer class="footer"><div class="container"><div class="footer-grid">
<div class="footer-logo"><img src="{up}assets/playground-logo.png" alt="Playground" width="170" height="49"><p style="max-width:310px;margin-top:18px">{e(ui['footer_tagline'])}</p></div>
<div><h4>{e(ui['footer_navigate'])}</h4>{''.join(f'<a href="{here}{href(p)}">{e(ui["nav"][p])}</a>' for p in ['expertise','sectors','work','about'])}</div>
<div><h4>{e(ui['footer_connect'])}</h4><a href="{here}contact.html">{e(ui['nav']['contact'])}</a><a href="{here}insights.html">{e(ui['nav']['insights'])}</a><a class="social" href="{li}" target="_blank" rel="noopener">{LI_SVG} LinkedIn</a></div>
<div><h4>{e(ui['footer_based'])}</h4>{''.join(f'<p>{e(x)}</p>' for x in ui['footer_based_lines'])}</div>
</div>
<div class="footer-bottom"><span>{e(ui['footer_rights'])} · <a href="{here}privacy.html" style="display:inline">{e(ui['footer_privacy'])}</a></span><span>{e(ui['footer_motto'])}</span></div>
</div></footer>
<div class="cookie" role="dialog" aria-live="polite" aria-label="Cookies"><p>{e(cookie['text'])}</p><button type="button">{e(cookie['decline'])}</button><button type="button" class="ok">{e(cookie['accept'])}</button></div>
<script src="{up}js/script.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- components
def page_hero(eyebrow, title, lead, extra=""):
    return f"""<section class="page-hero"><div class="container">
<div class="eyebrow orange reveal">{e(eyebrow)}</div>
<h1 class="h1" data-split>{e(title)}</h1>
<p class="lead reveal">{e(lead)}</p>{extra}
</div></section>"""


def work_card(lang, case, size, depth_prefix=""):
    ui = C[lang]["ui"]
    return f"""<a class="work-card {size} {case['media']} reveal-clip" href="{depth_prefix}work/{case['slug']}.html">
<div class="bg"></div><div class="content"><div class="tag">{e(case['tag'])}</div><h3>{e(case['title'])}</h3><p>{e(case['summary'])}</p>
<span class="go">{e(ui['read_case'])} <span>→</span></span></div></a>"""


def case_card(lang, case, prefix=""):
    ui = C[lang]["ui"]
    media = {"space": "space", "light": "light"}.get(case["media"], "")
    style = ' style="background:radial-gradient(circle at 75% 20%,#f08b24 0%,#48220d 20%,#101010 52%,#050505 100%)"' if case["media"] == "orbit" else ""
    return f"""<a class="case-card reveal" href="{prefix}work/{case['slug']}.html" data-category="{case['category']}" data-sector="{case['sector']}">
<div class="case-media {media}"{style}></div>
<div class="case-body"><div class="tag">{e(case['tag'])}</div><h3>{e(case['title'])}</h3><p>{e(case['summary'])}</p>
<div class="case-result"><strong>{e(ui['read_case'])} →</strong></div></div></a>"""


def sector_list(lang, link_prefix=""):
    rows = []
    for i, s in enumerate(C[lang]["sectors"], 1):
        rows.append(f'<a class="sector reveal" href="{link_prefix}work.html#{s["sector"] if "sector" in s else s["slug"]}"><span class="num">{i:02d}</span><span class="name">{e(s["name"])}</span><span class="arr">↗</span></a>')
    return f'<div class="sector-list" data-stagger>{"".join(rows)}</div>'


def linkedin_block(lang, eyebrow, title, lead):
    ui = C[lang]["ui"]
    posts = SITE.get("linkedin_posts") or []
    if posts:
        right = '<div class="li-embeds">' + "".join(
            f'<iframe src="{e(p)}" title="LinkedIn post" loading="lazy" allowfullscreen></iframe>' for p in posts[:3]
        ) + "</div>"
    else:
        items = C[lang]["insights"][:3]
        right = '<div class="li-posts" data-stagger>' + "".join(
            f'<div class="li-post reveal"><img src="../assets/playground-mark.png" alt=""><div><small>Playground · {e(i["tag"])}</small><p>{e(i["excerpt"])}</p></div></div>'
            for i in items
        ) + "</div>"
    return f"""<section class="section"><div class="container"><div class="li-panel reveal">
<div><div class="li-mark">{LI_SVG}</div><div class="eyebrow orange">{e(eyebrow)}</div>
<h2 class="h2" style="margin-top:14px">{e(title)}</h2><p class="copy">{e(lead)}</p>
<a class="btn linkedin magnetic" href="{SITE['linkedin_url']}" target="_blank" rel="noopener">{LI_SVG} {e(ui['follow_linkedin'])}</a></div>
{right}</div></div></section>"""


def share_bar(lang):
    ui = C[lang]["ui"]
    return f"""<div class="share-bar"><a class="share-btn" data-share="linkedin" href="#">{LI_SVG} <span>{e(ui['share_linkedin'])}</span></a>
<button class="share-btn" type="button" data-copy data-copied="{e(ui['copied'])}">{LINK_SVG} <span>{e(ui['copy_link'])}</span></button></div>"""


def cta_panel(lang):
    h = C[lang]["home"]
    return f"""<section class="section"><div class="container"><div class="cta-panel reveal">
<div><div class="eyebrow orange">{e(h['cta_eyebrow'])}</div><h2 class="h2" style="margin-top:18px">{e(h['cta_title'])}</h2></div>
<div><p class="lead" style="color:#c9c9c9">{e(h['cta_lead'])}</p><a class="btn primary magnetic" style="background:#fff;color:#111;border-color:#fff" href="contact.html">{e(h['cta_button'])} <span class="arrow">↗</span></a></div>
</div></div></section>"""


# ---------------------------------------------------------------- pages
def home(lang):
    c = C[lang]; h = c["home"]
    proof = "".join(
        f'<div class="proof"><strong data-count="{p["value"]}" data-suffix="{e(p["suffix"])}">{p["value"]}{e(p["suffix"])}</strong><span>{e(p["label"])}</span></div>'
        for p in h["proof"]
    )
    marquee_items = "".join(f'<span><b>{e(m)}</b></span><span class="dot">✦</span>' for m in h["marquee"])
    services = "".join(
        f'<a class="service-card spot reveal" href="expertise.html#{s["slug"]}"><div><div class="service-index">{i:02d}</div><h3 class="h3" style="font-size:24px;margin-top:40px">{e(s["title"])}</h3><p>{e(s["text"])}</p></div><div class="more">{e(c["ui"]["read_more"])} <span>→</span></div></a>'
        for i, s in enumerate(c["services"], 1)
    )
    cases = c["cases"]
    sizes = ["large", "small", "small", "large"]
    work = "".join(work_card(lang, cs, sizes[i % 4]) for i, cs in enumerate(cases[:4]))
    metrics = "".join(
        f'<div class="metric"><strong data-count="{m["value"]}" data-suffix="{e(m["suffix"])}">{m["value"]}{e(m["suffix"])}</strong><span>{e(m["label"])}</span></div>'
        for m in h["metrics"]
    )
    feat = c["insights"][0]
    body = f"""<section class="hero">
<svg class="hero-orbit" viewBox="0 0 1440 800" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<path d="M-40 760 C 340 520, 820 380, 1500 300"/>
<path class="thin" d="M120 820 C 420 560, 900 420, 1480 380"/>
<path d="M760 180 C 1000 120, 1260 180, 1400 330"/>
<circle cx="1180" cy="210" r="4"/>
</svg>
<div class="container hero-grid"><div class="hero-copy">
<div class="hero-kicker eyebrow reveal">{e(h['kicker'])}</div>
<h1 class="display" data-split>{h['title_html']}</h1>
<p class="lead reveal" style="margin-top:28px">{e(h['lead'])}</p>
<div class="hero-actions reveal"><a class="btn primary magnetic" href="contact.html">{e(h['cta_primary'])} <span class="arrow">↗</span></a><a class="btn ghost magnetic" href="work.html">{e(h['cta_secondary'])} <span class="arrow">→</span></a></div>
<div class="hero-proof reveal">{proof}</div>
</div></div><span class="orbit-float" aria-hidden="true"></span></section>
<div class="band" aria-hidden="true"><div class="marquee">{marquee_items}{marquee_items}</div></div>
<section class="section"><div class="container">
<div class="section-head"><div><div class="eyebrow orange reveal">{e(h['services_eyebrow'])}</div><h2 class="h2" data-split style="margin-top:14px">{e(h['services_title'])}</h2></div><p class="lead reveal">{e(h['services_lead'])}</p></div>
<div class="service-grid" data-stagger>{services}</div></div></section>
<section class="section soft"><div class="container">
<div class="section-head"><div><div class="eyebrow orange reveal">{e(h['work_eyebrow'])}</div><h2 class="h2" data-split style="margin-top:14px">{e(h['work_title'])}</h2></div><div><p class="lead reveal">{e(h['work_lead'])}</p><a class="btn ghost magnetic reveal" style="margin-top:22px" href="work.html">{e(c['ui']['view_all_work'])} <span class="arrow">→</span></a></div></div>
<div class="work-grid">{work}</div></div></section>
<section class="section dark"><div class="container">
<div class="eyebrow orange reveal">{e(h['metrics_eyebrow'])}</div><h2 class="h2" data-split style="margin-top:14px;max-width:900px">{e(h['metrics_title'])}</h2>
<div class="metrics reveal">{metrics}</div></div></section>
<section class="section"><div class="container">
<div class="section-head"><div><div class="eyebrow orange reveal">{e(h['sectors_eyebrow'])}</div><h2 class="h2" data-split style="margin-top:14px">{e(h['sectors_title'])}</h2></div><p class="lead reveal">{e(c['sectors_page']['intel_lead'])}</p></div>
{sector_list(lang)}</div></section>
<section class="section soft"><div class="container">
<div class="section-head"><div><div class="eyebrow orange reveal">{e(h['insights_eyebrow'])}</div><h2 class="h2" data-split style="margin-top:14px">{e(h['insights_title'])}</h2></div></div>
{insights_grid(lang)}</div></section>
{linkedin_block(lang, h['linkedin_eyebrow'], h['linkedin_title'], h['linkedin_lead'])}
{cta_panel(lang)}"""
    return layout(lang, "index", "index.html", body)


def insights_grid(lang):
    c = C[lang]; ui = c["ui"]
    feat = c["insights"][0]
    side = "".join(
        f'<article class="insight-card reveal"><div><div class="eyebrow orange">{e(i["tag"])}</div><h3>{e(i["title"])}</h3><p>{e(i["excerpt"])}</p></div><span>{i["minutes"]} {e(ui["min_read"])}</span></article>'
        for i in c["insights"][1:3]
    )
    return f"""<div class="insights-grid"><a class="insight-feature reveal" href="insights/{feat['slug']}.html"><div class="eyebrow orange">{e(feat['tag'])}</div><h2>{e(feat['title'])}</h2><p>{e(feat['excerpt'])}</p><div style="margin-top:20px;font-size:13px">{feat['minutes']} {e(ui['min_read'])} · {e(ui['read_more'])} ↗</div></a>
<div class="insight-side" data-stagger>{side}</div></div>"""


def expertise(lang):
    c = C[lang]; p = c["expertise_page"]
    meta = '<div class="page-meta reveal">' + "".join(f'<div><strong>{e(m["strong"])}</strong>{e(m["text"])}</div>' for m in p["meta"]) + "</div>"
    rows = "".join(
        f'<div class="expert-row reveal" id="{s["slug"]}"><span class="num">{i:02d}</span><h3>{e(s["title"])}</h3><p>{e(s["detail"])}</p></div>'
        for i, s in enumerate(c["services"], 1)
    )
    steps = "".join(f'<div class="step reveal"><h3>{e(m["title"])}</h3><p>{e(m["text"])}</p><span class="bar"></span></div>' for m in p["method"])
    body = f"""{page_hero(p['eyebrow'], p['title'], p['lead'], meta)}
<section class="section"><div class="container"><div class="stack">{rows}</div></div></section>
<section class="section soft"><div class="container"><div class="eyebrow orange reveal">{e(p['method_eyebrow'])}</div><h2 class="h2" data-split style="margin:14px 0 40px">{e(p['method_title'])}</h2><div class="method" data-stagger>{steps}</div></div></section>
{cta_panel(lang)}"""
    return layout(lang, "expertise", "expertise.html", body)


def sectors(lang):
    c = C[lang]; p = c["sectors_page"]
    rows = "".join(
        f'<a class="sector reveal" href="work.html#{s["slug"]}"><span class="num">{i:02d}</span><span class="name">{e(s["name"])}</span><span class="arr">↗</span><span class="sector-text">{e(s["text"])}</span></a>'
        for i, s in enumerate(c["sectors"], 1)
    )
    body = f"""{page_hero(p['eyebrow'], p['title'], p['lead'])}
<section class="section soft"><div class="container"><div class="sector-list" data-stagger>{rows}</div></div></section>
<section class="section"><div class="container"><div class="intro-split"><div class="sticky-title"><div class="eyebrow orange reveal">{e(p['intel_eyebrow'])}</div><h2 class="h2" data-split style="margin-top:14px">{e(p['intel_title'])}</h2></div>
<div class="reveal"><p class="lead">{e(p['intel_lead'])}</p><p class="copy">{e(p['intel_copy'])}</p><div class="quote"><p>{e(p['quote'])}</p><span>{e(p['quote_by'])}</span></div></div></div></div></section>
{cta_panel(lang)}"""
    return layout(lang, "sectors", "sectors.html", body)


def work(lang):
    c = C[lang]; p = c["work_page"]; ui = c["ui"]
    filters = f'<button class="filter-btn active" data-filter="all" aria-pressed="true">{e(ui["filter_all"])}</button>' + "".join(
        f'<button class="filter-btn" data-filter="{f["key"]}" aria-pressed="false">{e(f["label"])}</button>' for f in p["filters"]
    )
    cards = "".join(case_card(lang, cs) for cs in c["cases"])
    body = f"""{page_hero(p['eyebrow'], p['title'], p['lead'])}
<section class="section soft"><div class="container"><div class="filters reveal" role="group">{filters}</div>
<div class="case-grid" data-stagger aria-live="polite">{cards}</div></div></section>
{cta_panel(lang)}"""
    return layout(lang, "work", "work.html", body)


def case_page(lang, idx):
    c = C[lang]; ui = c["ui"]; L = c["case_labels"]
    cs = c["cases"][idx]
    nxt = c["cases"][(idx + 1) % len(c["cases"])]
    sector_name = next((s["name"] for s in c["sectors"] if s["slug"] == cs["sector"]), cs["sector"])
    media_cls = {"space": "space", "light": "light"}.get(cs["media"], "")
    media_style = {
        "dark": "background:linear-gradient(135deg,#101010 0%,#252525 48%,#e78d39 160%)",
        "orbit": "background:radial-gradient(circle at 75% 20%,#f08b24 0%,#48220d 20%,#101010 52%,#050505 100%)",
    }.get(cs["media"], "")
    draft = f'<div class="draft-badge">● {e(ui["draft_note"])}</div>' if cs.get("draft") else ""
    results = "".join(f'<div><strong>{e(r["value"])}</strong><span>{e(r["label"])}</span></div>' for r in cs["results"])
    delivered = "".join(f"<li>{e(d)}</li>" for d in cs["delivered"])
    quote = f'<div class="quote reveal" style="margin:0 0 20px"><p>“{e(cs["quote"])}”</p><span>{e(cs["quote_by"])}</span></div>' if cs.get("quote") else ""
    body = f"""<section class="case-hero"><div class="container">
<a class="crumb" href="../work.html">← {e(ui['back_to_work'])}</a>
<div class="eyebrow orange reveal">{e(cs['tag'])}</div>
<h1 class="h1" data-split style="margin-top:16px">{e(cs['title'])}</h1>
<p class="lead reveal" style="margin-top:24px">{e(cs['summary'])}</p>
{draft}
<div class="case-meta reveal">
<div><small>{e(L['client'])}</small><strong>{e(cs['client'])}</strong></div>
<div><small>{e(L['sector'])}</small><strong>{e(sector_name)}</strong></div>
<div><small>{e(L['year'])}</small><strong>{e(cs['year'])}</strong></div>
<div><small>{e(L['location'])}</small><strong>{e(cs['location'])}</strong></div>
</div></div></section>
<section><div class="container"><div class="case-cover"><div class="case-media {media_cls}" style="{media_style}"></div></div></div></section>
<section class="section tight"><div class="container">
<div class="case-section reveal"><h2>{e(L['challenge'])}</h2><p>{e(cs['challenge'])}</p></div>
<div class="case-section reveal"><h2>{e(L['approach'])}</h2><div>{quote}<p>{e(cs['approach'])}</p></div></div>
<div class="case-section reveal"><h2>{e(L['delivered'])}</h2><ul class="deliver-list">{delivered}</ul></div>
<div class="case-section reveal"><h2>{e(L['services'])}</h2><div class="pill-row" style="margin-top:0">{''.join(f'<span class="pill">{e(s)}</span>' for s in cs['services'])}</div></div>
</div></section>
<section class="section dark tight"><div class="container"><div class="eyebrow orange reveal">{e(L['results'])}</div><div class="case-results reveal" style="margin-top:24px">{results}</div></div></section>
<section class="section tight"><div class="container">{share_bar(lang)}
<a class="case-next reveal" style="margin-top:40px" href="{nxt['slug']}.html"><div><div class="eyebrow orange">{e(ui['next_case'])}</div><h2 class="h3" style="margin-top:12px">{e(nxt['title'])}</h2></div><span class="arrow-big">↗</span></a>
</div></section>"""
    title = f"{cs['title'].rstrip('.')} | Playground"
    html = layout(lang, "work", f"work/{cs['slug']}.html", body, title=title, description=cs["summary"], depth=2, current="work")
    return html


def about(lang):
    c = C[lang]; p = c["about_page"]
    values = "".join(f'<div class="value spot reveal" style="position:relative"><span class="num">{i:02d}</span><h3>{e(v["title"])}</h3><p>{e(v["text"])}</p></div>' for i, v in enumerate(p["values"], 1))
    leaders = "".join(f'<div class="leader reveal"><div class="ph"></div><h3>{e(l["name"])}</h3><div class="role">{e(l["role"])}</div><p>{e(l["bio"])}</p></div>' for l in p["leaders"])
    metrics = "".join(
        f'<div class="metric"><strong data-count="{m["value"]}" data-suffix="{e(m["suffix"])}">{m["value"]}{e(m["suffix"])}</strong><span>{e(m["label"])}</span></div>'
        for m in c["home"]["metrics"]
    )
    body = f"""{page_hero(p['eyebrow'], p['title'], p['lead'])}
<section class="section"><div class="container"><div class="intro-split"><div class="sticky-title"><div class="eyebrow orange reveal">{e(p['story_eyebrow'])}</div><h2 class="h2" data-split style="margin-top:14px">{e(p['story_title'])}</h2></div>
<div>{''.join(f'<p class="copy reveal">{e(s)}</p>' for s in p['story'])}</div></div>
<div class="about-visual reveal-clip" style="margin-top:60px;min-height:460px"></div></div></section>
<section class="section dark"><div class="container"><div class="metrics reveal" style="margin-top:0">{metrics}</div></div></section>
<section class="section"><div class="container"><div class="eyebrow orange reveal">{e(p['values_eyebrow'])}</div><h2 class="h2" data-split style="margin:14px 0 40px">{e(p['values_title'])}</h2><div class="values" data-stagger>{values}</div></div></section>
<section class="section soft"><div class="container"><div class="eyebrow orange reveal">{e(p['leadership_eyebrow'])}</div><h2 class="h2" data-split style="margin:14px 0 40px">{e(p['leadership_title'])}</h2><div class="leaders" data-stagger>{leaders}</div></div></section>
{cta_panel(lang)}"""
    return layout(lang, "about", "about.html", body)


def insights(lang):
    c = C[lang]; p = c["insights_page"]
    body = f"""{page_hero(p['eyebrow'], p['title'], p['lead'])}
<section class="section soft"><div class="container">{insights_grid(lang)}</div></section>
{linkedin_block(lang, p['newsletter_eyebrow'], p['newsletter_title'], p['newsletter_lead'])}"""
    return layout(lang, "insights", "insights.html", body)


def article(lang, item):
    c = C[lang]; ui = c["ui"]
    paras = "".join(f"<p>{e(x)}</p>" for x in item["body"])
    body = f"""<section class="case-hero"><div class="container">
<a class="crumb" href="../insights.html">← {e(ui['nav']['insights'])}</a>
<div class="eyebrow orange reveal">{e(item['tag'])} · {item['minutes']} {e(ui['min_read'])}</div>
<h1 class="h1" data-split style="margin-top:16px;max-width:1000px">{e(item['title'])}</h1>
<p class="lead reveal" style="margin-top:24px">{e(item['excerpt'])}</p></div></section>
<section class="section tight"><div class="container"><div class="article reveal">{paras}{share_bar(lang)}</div></div></section>
{linkedin_block(lang, c['insights_page']['newsletter_eyebrow'], c['insights_page']['newsletter_title'], c['insights_page']['newsletter_lead']).replace('../assets/', '../../assets/')}"""
    return layout(lang, "insights", f"insights/{item['slug']}.html", body, title=f"{item['title'].rstrip('.')} | Playground", description=item["excerpt"], depth=2, current="insights", og_image="section-space.webp")


def contact(lang):
    c = C[lang]; p = c["contact_page"]; f = p["form"]
    lines = ""
    for ln in p["lines"]:
        h = SITE["linkedin_url"] if ln["href"] == "LINKEDIN" else ln["href"]
        val = f'<a href="{e(h)}"{" target=\"_blank\" rel=\"noopener\"" if h.startswith("http") else ""}>{e(ln["value"])}</a>' if h else f'<span style="font-size:18px">{e(ln["value"])}</span>'
        lines += f"<div><small>{e(ln['label'])}</small>{val}</div>"
    opts = "".join(f"<option>{e(o)}</option>" for o in f["interest_options"])
    endpoint = SITE.get("contact_endpoint", "")
    body = f"""{page_hero(p['eyebrow'], p['title'], p['lead'])}
<section class="section"><div class="container"><div class="contact-grid">
<div class="contact-card reveal"><img src="../assets/playground-logo-white.png" alt="Playground" style="width:170px"><p style="margin-top:22px">{e(p['card_text'])}</p><div class="contact-lines">{lines}</div></div>
<form id="contact-form" class="form reveal" data-endpoint="{e(endpoint)}" data-sending="{e(f['sending'])}" data-thanks="{e(f['thanks'])}" novalidate>
<div class="field"><label for="f-name">{e(f['name'])}</label><input id="f-name" name="name" autocomplete="name" required></div>
<div class="field"><label for="f-company">{e(f['company'])}</label><input id="f-company" name="company" autocomplete="organization"></div>
<div class="field"><label for="f-email">{e(f['email'])}</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
<div class="field"><label for="f-phone">{e(f['phone'])}</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="field full"><label for="f-interest">{e(f['interest'])}</label><select id="f-interest" name="interest">{opts}</select></div>
<div class="field full"><label for="f-message">{e(f['message'])}</label><textarea id="f-message" name="message" required></textarea></div>
<div class="field full checkbox"><input id="f-consent" name="consent" type="checkbox" required><label for="f-consent">{e(f['consent'])}</label></div>
<div class="hp" aria-hidden="true"><input name="website" tabindex="-1" autocomplete="off"></div>
<div class="field full"><button class="btn primary magnetic" type="submit">{e(f['submit'])} <span class="arrow">↗</span></button><p class="form-note"><a href="privacy.html" style="text-decoration:underline">{e(f['note'])}</a></p></div>
</form></div></div></section>"""
    return layout(lang, "contact", "contact.html", body)


def privacy(lang):
    p = C[lang]["privacy_page"]
    body = f"""<section class="page-hero"><div class="container"><div class="eyebrow orange">{e(p['eyebrow'])}</div><h1 class="h1">{e(p['title'])}</h1></div></section>
<section class="section tight"><div class="container"><div class="article">{''.join(f'<p>{e(x)}</p>' for x in p['body'])}</div></div></section>"""
    return layout(lang, "privacy", "privacy.html", body.replace('class="article"', 'class="article plain"'))


ROOT_INDEX = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Playground</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" hreflang="en" href="{base}/en/"><link rel="alternate" hreflang="pt" href="{base}/pt/"><link rel="alternate" hreflang="x-default" href="{base}/en/">
<script>(function(){{var l=null;try{{l=localStorage.getItem('pg-lang')}}catch(e){{}}
if(!l){{l=(navigator.language||'en').toLowerCase().indexOf('pt')===0?'pt':'en'}}
location.replace(l+'/index.html');}})();</script>
<noscript><meta http-equiv="refresh" content="0;url=en/index.html"></noscript></head>
<body><p><a href="en/index.html">English</a> · <a href="pt/index.html">Português</a></p></body></html>
"""


def write(path, html):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "src/assets", OUT / "assets")
    shutil.copytree(ROOT / "src/css", OUT / "css")
    shutil.copytree(ROOT / "src/js", OUT / "js")
    for lang in LANGS:
        d = OUT / lang
        write(d / "index.html", home(lang))
        write(d / "expertise.html", expertise(lang))
        write(d / "sectors.html", sectors(lang))
        write(d / "work.html", work(lang))
        write(d / "about.html", about(lang))
        write(d / "insights.html", insights(lang))
        write(d / "contact.html", contact(lang))
        write(d / "privacy.html", privacy(lang))
        for i, _ in enumerate(C[lang]["cases"]):
            write(d / "work" / f"{C[lang]['cases'][i]['slug']}.html", case_page(lang, i))
        for item in C[lang]["insights"]:
            if item.get("body"):
                write(d / "insights" / f"{item['slug']}.html", article(lang, item))
    write(OUT / "index.html", ROOT_INDEX.format(base=SITE["base_url"].rstrip("/")))
    # Shared content for the WordPress theme
    theme_content = ROOT / "wordpress/playground/content"
    if theme_content.parent.exists():
        theme_content.mkdir(exist_ok=True)
        for f in ["en.json", "pt.json", "site.json"]:
            shutil.copy(ROOT / "content" / f, theme_content / f)
        for sub in ["assets", "css", "js"]:
            dst = ROOT / "wordpress/playground" / sub
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(ROOT / "src" / sub, dst)
    n = len(list(OUT.rglob("*.html")))
    print(f"Built {n} pages into {OUT}")


if __name__ == "__main__":
    main()
