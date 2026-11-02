# definitelybenny.dev

Benny's lab notebook: every tool on the site is introduced by the question it answers.

The project list is not kept here. Any public repo of mine tagged with the GitHub topic
**`showcase`** shows up on the site, and everything the site says about it lives in that
repo's own `showcase.json`. A GitHub Actions workflow reads them, builds the site and
publishes it to GitHub Pages: on every push to `main`, every 6 hours, and whenever I press
**Run workflow**.

## Show a project on the site

1. Add a `showcase.json` to the root of the repo's default branch. Start from one in
   [`showcase-files/`](showcase-files/), and keep the `$schema` line so your editor checks
   the fields and explains each one ([`showcase.schema.json`](showcase.schema.json)).
2. Tag the repo with the topic `showcase` (repo page, the gear next to **About**, **Topics**).
3. Wait for the next scheduled run, or open **Actions > Build and publish the site > Run workflow**.

Images the project page uses (`detail.what.figure`) are paths to files in that repo, like
`docs/screenshots/before.jpg`. The build copies and shrinks them.

To tease something that isn't ready, give it `"status": "soon"` and just a `question`
and `note`. It shows as a blurred card.

## What a showcase.json holds

| Field | Shown as |
|---|---|
| `question` | The card's headline. Required. |
| `name`, `what` | The tool's name and two or three sentences on what it is. Required. |
| `useWhen` | "Reach for it when" list. Required. |
| `thenAsk` | The follow-up questions. Required. |
| `links` | Buttons. One can be `"primary": true`. A "See the code" link to the repo is added if missing. |
| `game`, `note`, `tilt` | Label above the question, the handwritten aside, and how crooked the card sits. |
| `order`, `next` | Position on the home page, and which project's question comes next. |
| `detail` | The tool's own page at `/tools/<id>/`: `status`, `lede`, and the `what`, `how`, `works` and `ideas` sheets. |
| `id` | The page address and what `next` points at. Defaults to the repo name. |

If a tagged repo has no `showcase.json`, or it's missing a required field, the build skips
that project and leaves a yellow warning on the Actions run. If nothing at all can be shown,
the build fails and the live site stays as it was.

## What lives in this repo

| File | What it is |
|---|---|
| `site.json` | Site-wide content: the GitHub owner and topic, the secret question, the generic coming-soon teaser, and the apps on the bench. |
| `index.html`, `404.html`, `assets/` | The pages, the look and the toys (chaos dial, theme button, drag, secret question, the `?` key). |
| `scripts/build.py` | Finds the tagged repos, checks each `showcase.json`, and writes the site to `_site/` with a page and a link preview for each project. |
| `scripts/make_images.py` | Draws the favicon, the phone icon and the home page's link preview. |
| `showcase.schema.json` | The format of `showcase.json`. Also published on the site so editors can use it. |
| `.github/workflows/pages.yml` | Builds and publishes. On a pull request it only checks the build against `showcase-files/`. |
| `CNAME` | The custom domain. Leave it alone. |

## Run it locally

```
python3 -m pip install pillow
python3 scripts/build.py --local showcase-files    # or with no flag to read GitHub
python3 -m http.server 8000 --directory _site
```

then visit http://localhost:8000.

## Easter eggs

Open every question and a secret one appears. Tap the logo five times to cycle the chaos
level. Press `?` for a random question. On a computer you can drag the question cards around.
