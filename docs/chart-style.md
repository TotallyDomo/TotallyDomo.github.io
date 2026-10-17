# Blog chart defaults

These are the defaults for all new and revised blog graphics, settled in the
October 2026 review. Apply them without reopening the style choice for each post.
A later explicit author instruction overrides them. The README and post archetype
point here so this remains the single authoring reference.

## Direction

Use the site's original dark and light backgrounds, Segoe UI, lining numerals,
and copper emphasis established in the Tokenomics review. Match the site's font
fallbacks. Preserve Consolas for figure numbers and existing monospaced axis ticks.
No branding header, slogans, obvious takeaways, semicolons, decorative badges,
glow, or filler footers. Put relevant assumptions beside the graphic.
Do not add routine caption paragraphs beneath every figure. Keep necessary model
details in the graphic and its accessible description.

Choose the visual form from the claim. Preserve visual magnitude and composition
through shapes, color, and area. A recolored default chart is not enough. A table
is not a substitute for a visual comparison. Use direct labels where they fit.

Titles name the subject. Subtitles carry only useful units, scope, or assumptions.
Avoid commentary such as "same prefix", "tokenomics example", or "not A/B
averages" when the surrounding article already explains it. Keep essential
limitations in the article and accessible description, not as repeated fine print.
Use Segoe UI for titles too, not the earlier Georgia prototype. Keep units and
delta symbols on the same typographic baseline as their numbers. Figure numbers
are compact, top-right, and sequential within the post.

## Choose the graphic from the claim

| What the reader needs to see | Default approach | Reference in the generator |
| --- | --- | --- |
| A changing total and its components | Area-scaled pies with exact slice geometry | `_context()` |
| Accumulation and a difference | Lines, direct endpoint labels, a delta bracket | `_startup()` |
| Spent versus avoided cost | One budget pie with a clear whole and labeled shares | `_keepalive()` |
| Duration differences and one run's breakdown | Shared time axis plus a separate composition pie | `_builds()` |
| Composition in different units | Equal-sized pies with separately named units | `_spend()` |
| Two measurements across categories | Paired dots on a shared axis | `_recall()` |
| A tiny component of a large total | True-scale slices with external callouts | `_vibemax()` |

These are examples, not a mandate to turn everything into pies. Prefer position
or length when comparing magnitude is the main task. Do not enlarge a tiny slice
to make it visible. Do not substitute a number table for the visual explanation.
Avoid dashboard cards, shadows, glows, generic recolored stacked bars, and novelty
shapes that make comparison harder. The block towers, block grids, and repeated
"4h" icons were rejected for the waiting-cost graphic.

## Precision and approved examples

Scale pie and circle **area**, never radius, with magnitude. Compare area only
within a common unit and scale. Fixed-cost slices must retain equal areas.
Use a zero baseline for magnitudes. Preserve precision from the evidence.
For the four-hour keep-alive comparison, use the approved D2 budget split. The
whole circle is the 1.6M TC cold-resume budget. Keeping warm spends one quarter
(400K TC) and avoids the other three quarters (1.2M TC). Keep the longer-wait
curve beside it. Do not return to block grids or the rejected repeated-wait icons.
For builder durations, use a shared seconds axis and a separate pie for the Python
breakdown, not competing circle areas. Build/shipping pies compare shares in their
own units. Keep the recall dot plot and the Vibemax pies, with separate area scales
for tokens and dollars. Label the Vibemax samples "Two demo runs." Keep the
statistical qualification in the article and SVG description, not the subtitle.

## Sources and rendering

`tools/build-charts.py` owns the recorded values, calculations, labels and SVG
geometry. It generates one dark/light pair per entry in `tools/chart-manifest.json`.
`tools/render-charts.cjs` renders their 2x PNG exports with an installed Electron
runtime. It checks that labels stay within the canvas and blocks network access.

Articles embed the SVG for sharp text at browser zoom. PNG exports remain the
social-card assets. Each SVG has a `.light.svg` companion. The image hook and CSS
select the pair using the site's theme, including the full-size link. Backgrounds
and neutral ink match the Hugo palette. Data fills stay consistent, while direct
labels use darker ink in light mode. Pie interior ink remains dark in both modes.
Do not list vector pairs under `themeImages`, reserved for legacy transparent
charts. Avoid card borders around charts so they blend into the page.

Reuse the palette and typography constants in the generator. Backgrounds must
match the site's dark and light page colors, not the discarded warm-charcoal
prototype. Support the site's manual toggle, not just the operating-system theme.
Reference locally installed fonts with fallbacks. Do not bundle font files.

## Adding a chart to a future post

1. Identify the claim, units, source values, and necessary assumptions. Preserve
   measured precision and distinguish measurements from illustrative models.
2. Add its drawing function to `tools/build-charts.py` and register it in `main()`.
   Reuse `_Svg` and its `save()` method so both themes and the manifest are generated.
   Store the data and formulas in code, not in hand-edited SVG or raster labels.
3. Generate the SVGs, then use `tools/render-charts.cjs` with an installed Electron
   runtime for PNG exports and text-bound checks. Keep local previews under `Temp`.
4. Embed the dark SVG path as a standalone Markdown image with useful alt text.
   Its `.light.svg` companion is selected automatically. Use the PNG for the post's
   social `image` when appropriate. Do not add a caption paragraph by default.
5. Check arithmetic, totals, ratios, and geometry against the source data. For
   proportional pies, verify area scaling and equal areas for fixed components.
   Label comparisons that use separate units or scales. Do not invent precision.
6. Inspect the actual article in both themes and at a narrow viewport. Check text
   contrast, labels and leader lines, number/unit alignment, clipping, and the
   theme-matched full-size link. Also inspect the PNG export used for sharing.
7. Build Hugo and run the repository's metadata and chart-theme checks. For a
   redesign, retain local before/after previews without publishing scratch files.

Chart changes do not authorize rewriting the author's prose, quoted transcripts,
or screenshots. Update nearby wording only when the new graphic makes it stale.

## Data provenance

- Tokenomics: the illustrative TC model and assumptions in the post. The warm
  prefix grows by 1K tokens per turn, including the previous output after turn one.
  Keep-alive steps count scheduled requests plus resume, as in the original model.
- Build times: the post's preserved-manifest figures, including the 245.4-second
  reread component of the 385.7-second Python build.
- Build/shipping spend: the published 229M/527M tokens and $346/$908 list-price
  equivalents. Units differ, so the two pies compare composition, not total area.
- Recall: the original chart's whole-percent labels. Do not infer exact equality
  from the two BM25 rows. The article retains the more precise headline values.
- Vibemax: benchmark records `grid-haiku-t1-blind-r02` and
  `grid-haiku-t1-vibemax-r06` in the public project's `benchmarks/results/grid.jsonl`.
  The generator records only numeric usage, not transcripts or machine paths.
  Visible tokens are estimates from characters divided by four. Dollar slices
  use the historical illustrative rates stated in the SVG description, not the
  harness's aggregate cost field. Comparisons are within each unit row only.

The chat screenshot in the Unity article is evidence, not a chart. Preserve it.
