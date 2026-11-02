#!/usr/bin/env python3
"""Write a small HTML page for every question in projects.json that has a "page".

The page body is drawn by assets/site.js from projects.json, so this only bakes in
what has to exist before any JavaScript runs: the title, the description and the
Open Graph tags that Discord and other apps read when someone pastes the link.

  python3 scripts/build_pages.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://definitelybenny.dev/"

TEMPLATE = """<!DOCTYPE html>
<!-- Made by scripts/build_pages.py from projects.json. Edit the data, then run the script. -->
<html lang="en" data-chaos="3">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{name} · definitelyBenny</title>
  <meta name="description" content="{what}">
  <link rel="canonical" href="{url}">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="definitelyBenny">
  <meta property="og:title" content="{question}">
  <meta property="og:description" content="{name}. {what}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="A taped notebook card asking: {question}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#3D7643" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#1D2923" media="(prefers-color-scheme: dark)">

  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Libre+Franklin:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Caveat:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap">
  <script>(function(){{var r=document.documentElement,c=3,t=null;try{{var s=localStorage.getItem('dbd-chaos');if(s!==null&&/^[0-3]$/.test(s))c=+s;t=localStorage.getItem('dbd-theme')}}catch(e){{}}r.setAttribute('data-chaos',c);if(t==='light'||t==='dark')r.setAttribute('data-theme',t)}})();</script>
  <link rel="stylesheet" href="{base}assets/site.css">
</head>
<body data-root="{base}" data-tool="{id}">
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <g id="fav"><rect x="5" y="5" width="54" height="54" rx="14" fill="#3D7643" transform="rotate(-6 32 32)"/><path d="M23 25c0-7 5-12 11-12 7 0 11 5 11 10 0 6-4 8-8 11-3 2-4 4-4 8" fill="none" stroke="#F3F4EE" stroke-width="5.5" stroke-linecap="round"/><circle cx="33" cy="50" r="3.6" fill="#F3F4EE"/><path d="M48 9l3-4M53 15l5-1" stroke="#B4552E" stroke-width="3" stroke-linecap="round"/></g>
</defs></svg>

<header class="top"><div class="wrap">
  <a class="brand" id="brand" href="{base}" aria-label="definitelyBenny home"><svg viewBox="0 0 64 64" aria-hidden="true"><use href="#fav"/></svg>definitelyBenny</a>
  <nav class="nav" aria-label="Pages"><a href="{base}#questions" class="cur">Questions</a><a href="{base}#apps" class="opt">Apps</a><button class="theme" id="theme" type="button">Theme: system</button></nav>
</div></header>

<main class="wrap">
  <a class="crumb" href="{base}#questions">← all questions</a>
  <div id="page">
    <noscript>
      <div class="hero t-hero"><h1 class="qt">{question}</h1><p class="lede">{what}</p></div>
      <p class="noscript"><a href="{primary_href}">{primary_label}</a></p>
    </noscript>
  </div>

  <footer>
    <div class="dial" role="group" aria-label="Chaos level">
      <b>how much chaos?</b>
      <div class="opts" id="dial"><button type="button" data-c="0">Tidy</button><button type="button" data-c="1">Lived in</button><button type="button" data-c="2">Live build</button><button type="button" data-c="3">Unhinged</button></div>
    </div>
    <div class="flinks"><a href="{base}#questions">Questions</a><a href="{base}#apps">Apps</a><a href="https://github.com/definitelybenny" target="_blank" rel="noopener">GitHub</a></div>
    <span>Made by Benny in a notebook that's mostly scribbles · definitelybenny.dev</span>
  </footer>
</main>

<script src="{base}assets/site.js" defer></script>
</body>
</html>
"""


def main():
    data = json.loads((ROOT / "projects.json").read_text())
    for q in data.get("questions", []):
        page = q.get("page")
        if not page:
            continue
        page = page.strip("/") + "/"
        out = ROOT / page / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        depth = page.count("/")
        image = SITE + page + "og.png" if (ROOT / page / "og.png").exists() else SITE + "assets/og.png"
        primary = next((l for l in q.get("links", []) if l.get("primary")), {"href": "../../", "label": "Back to all questions"})
        e = lambda s: html.escape(str(s), quote=True)
        out.write_text(TEMPLATE.format(
            id=e(q["id"]), name=e(q["name"]), question=e(q["question"]), what=e(q["what"]),
            url=e(SITE + page), image=e(image), base="../" * depth,
            primary_href=e(primary["href"]), primary_label=e(primary["label"]),
        ))
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
