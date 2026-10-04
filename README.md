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

Verify the homepage and vibemax social metadata, including malformed-value fallbacks:

    python tools/check-head-metadata.py

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

Transparent charts opt into theme-aware labels by listing their image URLs under
`themeImages` in the post's front matter. The renderer switches neutral text and grids
between the site's dark and light palettes without changing colored data or transparency.
Screenshots and photographs should not be listed. Chart sources use `#e6edf3` for
theme-dependent text, `#8b98a9` for secondary text, and `#2a313c` for grids. Use `#f5f8fc`
for text that must stay pale inside a dark-colored bar. Original images remain the dark
sources; the browser caches each light rendering once. If conversion is unavailable,
the source gets a dark backing in light mode so it remains readable.

CI checks theme switching and palette preservation in `tools/check-theme-charts.cjs`.

## Authoring posts

    hugo new posts/my-post.md

New posts scaffold from `archetypes/posts.md`, which seeds the one-line writing note that every
post carries (linking to the `/about/` page, which describes the process once). Write the draft
yourself and keep that line; reword it if a post's process differed.

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the site and publishes it
to GitHub Pages. One-time repo setup: **Settings -> Pages -> Build and deployment -> Source =
GitHub Actions**.
