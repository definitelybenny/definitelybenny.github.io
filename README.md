# definitelybenny.dev

Benny's lab notebook: every tool on the site is introduced by the question it answers.
Plain static files served by GitHub Pages. No build step is needed to deploy.

## How it fits together

| File | What it is |
|---|---|
| `projects.json` | Everything the site lists: the questions (tools), the coming-soon teasers, the apps on the bench and the secret question. |
| `index.html` | Home. The question list, the teasers and the bench are drawn from `projects.json` by `assets/site.js`. |
| `tools/<id>/index.html` | One page per tool. Generated, so each has its own title and Discord preview. The body is drawn from `projects.json`. |
| `assets/site.css`, `assets/site.js` | The look and the toys (chaos dial, theme button, drag, the secret question, the "?" key). |
| `assets/og.png`, `tools/<id>/og.png` | Link preview images (1200x630), drawn by a script. |
| `favicon.svg`, `favicon.ico`, `apple-touch-icon.png` | Tab and home-screen icons. |
| `404.html` | Shown by GitHub Pages for any missing page. |
| `CNAME` | The custom domain. Leave it alone. |

## Add a tool

1. Add an entry to `questions` in `projects.json`. Copy an existing one; `id`, `question`, `game`, `name`, `what`, `links` and `next` are the core. `detail` fills the tool's own page and is optional.
2. If it has a `page`, run `python3 scripts/build_pages.py` to write `tools/<id>/index.html`.
3. Run `python3 scripts/make_images.py` to draw its link preview (needs `pip install pillow`; fonts download on first run).
4. Point another question's `next` at it so the chain of questions reaches it.

To tease something that isn't ready, add it to `soon` (shown blurred) or `bench` (apps, with a progress bar).

## Run it locally

`fetch` needs a server, so open it through one:

```
python3 -m http.server 8000
```

then visit http://localhost:8000.

## Easter eggs

Open every question and a secret one appears. Tap the logo five times to cycle the chaos level. Press `?` for a random question. On a computer you can drag the question cards around.
