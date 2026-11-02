#!/usr/bin/env python3
"""Build definitelybenny.dev into _site/.

Projects are not listed in this repo. Every public repo of the owner in site.json that
carries the GitHub topic in site.json ("showcase") is a project, and its own
showcase.json (at the root of its default branch) holds everything the site says about
it: the card question, the follow-up questions, links and the tool page. See README.md.

  python3 scripts/build.py                          # read the tagged repos on GitHub
  python3 scripts/build.py --local showcase-files   # read <dir>/<repo>/showcase.json instead

Set GITHUB_TOKEN to avoid GitHub's anonymous rate limit (the Actions workflow does).
A tagged repo whose showcase.json is missing or invalid is skipped with a warning; the
build fails if no project is left, so a bad run never replaces the live site with an
empty one.
"""
import argparse
import html
import io
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://definitelybenny.dev/"
STATIC = ["index.html", "404.html", "favicon.svg", "favicon.ico", "apple-touch-icon.png",
          "CNAME", ".nojekyll", "showcase.schema.json", "assets/site.css", "assets/site.js", "assets/og.png"]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
problems = 0


def warn(repo, msg):
    """Shows in the run log, and as a yellow annotation on the Actions run."""
    global problems
    problems += 1
    print(f"::warning title={repo}::{msg}")


# ---------- reading GitHub ----------

def gh(path, raw=False):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "definitelybenny.dev-build",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
    return body if raw else json.loads(body)


def tagged_repos(owner, topic):
    repos, page = [], 1
    while True:
        batch = gh(f"/users/{owner}/repos?type=owner&per_page=100&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    return [r for r in repos if topic in (r.get("topics") or []) and not r.get("private")]


class GitHubSource:
    def __init__(self, owner, topic):
        self.repos = tagged_repos(owner, topic)

    def items(self):
        for r in sorted(self.repos, key=lambda r: r["name"]):
            yield r["name"], r["html_url"], r["default_branch"]

    def read(self, repo, branch, path):
        try:
            return gh(f"/repos/{OWNER}/{repo}/contents/{path}?ref={branch}", raw=True)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise


class LocalSource:
    """For trying things out: <dir>/<repo>/showcase.json, images fetched from GitHub."""
    def __init__(self, folder):
        self.folder = Path(folder)

    def items(self):
        for d in sorted(p for p in self.folder.iterdir() if p.is_dir()):
            yield d.name, f"https://github.com/{OWNER}/{d.name}", "main"

    def read(self, repo, branch, path):
        local = self.folder / repo / path
        if local.exists():
            return local.read_bytes()
        try:
            req = urllib.request.Request(f"https://raw.githubusercontent.com/{OWNER}/{repo}/{branch}/{path}", headers={"User-Agent": "definitelybenny.dev-build"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError:
            return None


# ---------- checking a showcase.json ----------

def text_list(v):
    return isinstance(v, list) and v and all(isinstance(x, str) and x.strip() for x in v)


def check(repo, url, data, seen):
    """Return a cleaned entry, or None after warning about what is wrong."""
    if not isinstance(data, dict):
        warn(repo, "showcase.json must hold one JSON object")
        return None
    pid = str(data.get("id") or repo).lower()
    if not ID_RE.match(pid):
        warn(repo, f'id "{pid}" may only use a-z, 0-9 and hyphens')
        return None
    if pid in seen:
        warn(repo, f'id "{pid}" is already used by {seen[pid]}; skipped')
        return None
    status = data.get("status", "live")
    if status not in ("live", "soon"):
        warn(repo, f'status must be "live" or "soon", not "{status}"')
        return None
    if not isinstance(data.get("question"), str) or not data["question"].strip():
        warn(repo, "question is missing")
        return None
    entry = dict(data, id=pid, status=status, repo=url)
    entry.pop("$schema", None)
    if status == "soon":
        return entry
    missing = [k for k in ("name", "what") if not isinstance(data.get(k), str) or not data[k].strip()]
    missing += [k for k in ("useWhen", "thenAsk") if not text_list(data.get(k))]
    if missing:
        warn(repo, "missing or empty: " + ", ".join(missing) + "; not shown")
        return None
    links = [l for l in data.get("links") or [] if isinstance(l, dict) and l.get("label") and str(l.get("href", "")).startswith("https://")]
    if len(links) != len(data.get("links") or []):
        warn(repo, "dropped links that need a label and an https:// href")
    if not any(l["href"].rstrip("/") == url for l in links):
        links.append({"label": "See the code", "href": url})
    entry["links"] = links
    return entry


# ---------- images a project ships in its own repo ----------

def bring_image(src, source, repo, branch, out_dir, pid):
    """A relative src is a file in the project's repo: copy it next to the tool page."""
    if not src or re.match(r"^https?://", src):
        return src
    raw = source.read(repo, branch, src.lstrip("/"))
    if raw is None:
        warn(repo, f"image {src} was not found in the repo")
        return None
    from PIL import Image
    name = Path(src).stem + ".jpg"
    img = Image.open(io.BytesIO(raw))
    img.thumbnail((1200, 1200))
    if img.mode in ("LA", "P"):
        img = img.convert("RGBA")
    if img.mode == "RGBA" and img.getchannel("A").getextrema()[0] < 255:  # really transparent: keep PNG
        name = Path(src).stem + ".png"
        img.save(out_dir / name, optimize=True)
    else:
        img.convert("RGB").save(out_dir / name, quality=86, optimize=True, progressive=True)
    return f"tools/{pid}/{name}"


def localize_figure(entry, source, repo, branch, out_dir):
    fig = ((entry.get("detail") or {}).get("what") or {}).get("figure")
    if not isinstance(fig, dict):
        return
    if fig.get("type") == "image":
        fig["src"] = bring_image(fig.get("src"), source, repo, branch, out_dir, entry["id"])
        if not fig["src"]:
            entry["detail"]["what"].pop("figure")
    elif fig.get("type") == "beforeafter":
        for side in ("before", "after"):
            part = fig.get(side) or {}
            part["src"] = bring_image(part.get("src"), source, repo, branch, out_dir, entry["id"])
        if not (fig["before"].get("src") and fig["after"].get("src")):
            entry["detail"]["what"].pop("figure")


# ---------- pages ----------

TEMPLATE = """<!DOCTYPE html>
<!-- Built by scripts/build.py from this project's showcase.json. -->
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


def e(s):
    return html.escape(str(s), quote=True)


def main():
    global OWNER
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "_site"))
    ap.add_argument("--local", help="read <dir>/<repo>/showcase.json instead of GitHub")
    ap.add_argument("--strict", action="store_true", help="fail on any warning")
    args = ap.parse_args()

    site = json.loads((ROOT / "site.json").read_text())
    OWNER = site["owner"]
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    source = LocalSource(args.local) if args.local else GitHubSource(OWNER, site["topic"])
    print(f"Projects: {'folder ' + args.local if args.local else 'repos of ' + OWNER + ' tagged ' + site['topic']}")

    live, soon, seen = [], [], {}
    for repo, url, branch in source.items():
        raw = source.read(repo, branch, "showcase.json")
        if raw is None:
            warn(repo, f"tagged {site['topic']} but has no showcase.json on {branch}; not shown")
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as err:
            warn(repo, f"showcase.json is not valid JSON ({err}); not shown")
            continue
        entry = check(repo, url, data, seen)
        if not entry:
            continue
        seen[entry["id"]] = repo
        if entry["status"] == "soon":
            soon.append({"question": entry["question"], "note": entry.get("note") or "WIP, don’t look yet"})
            print(f"  {repo}: coming soon")
            continue
        tool_dir = out / "tools" / entry["id"]
        tool_dir.mkdir(parents=True, exist_ok=True)
        entry["_branch"] = branch
        entry["_repo"] = repo
        localize_figure(entry, source, repo, branch, tool_dir)
        entry["page"] = f"tools/{entry['id']}/"
        live.append(entry)
        print(f"  {repo}: {entry['question']}")

    if not live:
        print("::error::No project could be shown, so the site was not built. Tag a repo and give it a showcase.json.")
        sys.exit(1)

    live.sort(key=lambda q: (q.get("order", 999), q["name"].lower()))
    ids = [q["id"] for q in live]
    for i, q in enumerate(live):
        if q.get("next") not in ids or q.get("next") == q["id"]:
            if q.get("next"):
                warn(q["_repo"], f'next "{q["next"]}" is not a shown project; using the following one')
            q["next"] = ids[(i + 1) % len(ids)]

    # the data the pages render from
    for q in live:
        q.pop("_branch"); q.pop("_repo")
    data = {"questions": live, "secret": site.get("secret"), "soon": soon + site.get("soon", []), "bench": site.get("bench", [])}
    (out / "projects.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))

    # static files
    for f in STATIC:
        src = ROOT / f
        if src.exists():
            (out / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out / f)
    links = " · ".join(f'<a href="{e(q["page"])}">{e(q["name"])}</a>' for q in live)
    idx = out / "index.html"
    idx.write_text(idx.read_text().replace("<!--TOOL_LINKS-->", links))

    # one page and one link preview per project
    sys.path.insert(0, str(ROOT / "scripts"))
    from make_images import og_image
    for q in live:
        page = q["page"]
        primary = next((l for l in q["links"] if l.get("primary")), q["links"][0])
        (out / page / "index.html").write_text(TEMPLATE.format(
            id=e(q["id"]), name=e(q["name"]), question=e(q["question"]), what=e(q["what"]),
            url=e(SITE + page), image=e(SITE + page + "og.png"), base="../../",
            primary_href=e(primary["href"]), primary_label=e(primary["label"]),
        ))
        og_image(q["question"], q["name"]).save(out / page / "og.png", optimize=True)

    print(f"Built {out}: {len(live)} projects, {len(soon)} coming soon from repos, {problems} warnings")
    if args.strict and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
