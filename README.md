# TotallyDomo.github.io

Personal site, built with [Hugo](https://gohugo.io/) and deployed to GitHub Pages via GitHub
Actions. Hand-written minimal theme (plain CSS, no external theme, no SCSS, no committed binaries).
Dark by default with a light-mode toggle; the only JavaScript is one progressive-enhancement file.

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
- `layouts/`  - Hugo templates (minimal hand-written theme; `_partials/` for partials,
  `_markup/` for the heading and image render hooks).
- `static/`   - Assets served as-is (`static/css/main.css`, `static/js/site.js`).
- `tools/`    - Repo maintenance scripts.
- `.github/workflows/deploy.yml` - CI build + Pages deploy (Hugo version pinned).

`static/css/syntax.css` is generated - it carries the dark Chroma theme plus a light override
scoped to `:root[data-theme="light"]`. Regenerate it after changing either style in `hugo.toml`:

    python tools/gen-syntax-css.py

Images written as a standalone `![alt](src)` become a `<figure>`; the italic paragraph that
follows one is styled as its caption.

## Authoring posts

    hugo new posts/my-post.md

New posts scaffold from `archetypes/posts.md`, which seeds the one-line writing note that every
post carries (linking to the `/about/` page, which describes the process once). Write the draft
yourself and keep that line; reword it if a post's process differed.

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the site and publishes it
to GitHub Pages. One-time repo setup: **Settings -> Pages -> Build and deployment -> Source =
GitHub Actions**.
