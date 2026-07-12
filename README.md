# TotallyDomo.github.io

Personal site, built with [Hugo](https://gohugo.io/) and deployed to GitHub Pages via GitHub
Actions. Hand-written minimal theme (plain CSS, no external theme, no SCSS, no committed binaries).

## Local development

Requires Hugo v0.164.0+. Install the standard edition from source (pure Go, no C toolchain):

    CGO_ENABLED=0 go install github.com/gohugoio/hugo@latest

Serve locally with drafts:

    hugo server -D

Production build (output in `public/`, gitignored):

    hugo --gc --minify

Note: CI builds with the Hugo *extended* edition (a superset); the theme uses plain CSS only,
so extended vs. standard produces identical output.

## Structure

- `content/`  - Markdown content; `content/posts/` holds blog posts.
- `layouts/`  - Hugo templates (minimal hand-written theme; `_partials/` for partials).
- `static/`   - Assets served as-is (`static/css/main.css`).
- `.github/workflows/deploy.yml` - CI build + Pages deploy (Hugo version pinned).

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the site and publishes it
to GitHub Pages. One-time repo setup: **Settings -> Pages -> Build and deployment -> Source =
GitHub Actions**.
