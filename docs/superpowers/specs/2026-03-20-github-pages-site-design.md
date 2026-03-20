# definitelyBenny.dev — GitHub Pages Site

**Date:** 2026-03-20
**Status:** Draft

## Overview

A minimal, functional GitHub Pages site at `definitelybenny.dev` serving as a landing page and privacy policy host for Benny's Android apps. Branding is intentionally neutral — the brand identity is unresolved and will be revisited later.

## Architecture

### Multi-repo GitHub Pages strategy

- **This repo (`definitelyBenny`)** is renamed/configured as `byamagata.github.io` (or equivalent username repo) with a custom domain pointing to `definitelybenny.dev`
- Each app gets its **own repo** with GitHub Pages enabled, automatically routed to `definitelybenny.dev/<app-name>/` by GitHub
- This repo only contains the main landing page

### What this repo contains

```
/
├── index.html          # Landing page with app grid
├── style.css           # Shared styles
└── CNAME               # Custom domain config (definitelybenny.dev)
```

### What each app repo contains (future, not in scope)

```
/<app-repo>/
├── index.html          # App landing page (optional)
├── privacy-policy.html # Privacy policy (required for Play Store)
└── style.css           # App-specific styles (or shared via CDN/main site)
```

## Pages & Content

### Landing Page (`index.html`)

**Sections:**
1. **Nav** — "definitelyBenny" text on the left, "Home" and "Apps" links on the right
2. **Hero** — "definitelyBenny" as the heading, "Games & Apps" as subtitle
3. **App Grid** — 2x2 grid of cards, each containing:
   - Placeholder for app icon (grey rounded square for now)
   - App name
   - Category label (Puzzle, Casual, Idle Tycoon, Fitness)
   - Link to privacy policy (will point to `/<app-name>/privacy-policy` once app repos exist)
4. **Footer** — Copyright line

**Apps to display:**
- Hex Flipper (Puzzle)
- Sunday Drive (Casual)
- Board Game Empire (Idle Tycoon)
- Iron Log (Fitness)
- 2048 clone (unnamed, Puzzle — omit for v1, add when named)

### Visual Design

- **Intentionally minimal/neutral** — white/light grey background, dark text, subtle borders
- No brand colors, no mascot, no crest, no motto
- System font stack (`system-ui, -apple-system, sans-serif`)
- Responsive — works on mobile (single column) and desktop (2-column grid)
- App cards: white background, light border, rounded corners, subtle shadow

### Technical Details

- **No build step** — plain HTML, CSS, JS
- **No frameworks** — vanilla everything
- **CNAME file** — contains `definitelybenny.dev` for GitHub Pages custom domain
- **Responsive** via CSS Grid and media queries
- **Dark mode** — not in scope for v1 (can be added later)

## GitHub Pages Setup

1. Rename repo to `byamagata.github.io` (GitHub username: `byamagata`)
2. Enable GitHub Pages in repo settings (deploy from `main` branch, root)
3. Add CNAME file with `definitelybenny.dev`
4. Configure DNS for `definitelybenny.dev` to point to GitHub Pages IPs
5. Enable HTTPS in GitHub Pages settings

## What's NOT in scope

- Branding/visual identity (deferred — actively unresolved)
- Blog functionality
- About page
- Individual app repos and privacy policies (separate task per app)
- Dark mode
- Analytics
- Contact form

## Success Criteria

- `definitelybenny.dev` loads and shows the landing page
- Page is responsive (mobile + desktop)
- App cards are present with placeholder icons
- Privacy policy links exist (can point to `#` or placeholder URLs until app repos are created)
- HTTPS works via GitHub Pages
- Page loads fast (no build step, no JS frameworks, minimal CSS)

## Future Work

- Create per-app repos with privacy policies
- Revisit branding when identity is clearer
- Optionally add blog, about page, or other sections
- Add real app icons and Play Store links as apps launch
