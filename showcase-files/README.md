# Showcase files to copy into each repo

Each folder here is named after one of my repos and holds the `showcase.json` that repo
needs. Copy it to the root of that repo's default branch, then tag the repo with the topic
`showcase`.

| Repo | File | Shows as |
|---|---|---|
| `pokopia-roommate-calc` | `pokopia-roommate-calc/showcase.json` | First question, page at `/tools/pokopia/` |
| `mock-regional-helper` | `mock-regional-helper/showcase.json` | Second question, page at `/tools/mock-regional/`, uses `docs/screenshots/report-card.png` |
| `showdown-restyler` | `showdown-restyler/showcase.json` | Third question, page at `/tools/showdown-restyler/`, uses `docs/screenshots/before.jpg` and `after-dark.jpg` |
| `showdown-analyzer` | `showdown-analyzer/showcase.json` | Optional. A blurred coming-soon teaser. Skip it to keep the analyzer off the site. |

The pull request check builds the site from these copies, so they also serve as working
examples for a new project. Once the files are in their repos, this folder is only examples.
