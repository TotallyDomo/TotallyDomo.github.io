# Blog graphics

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
geometry. It generates the seven files listed in `tools/chart-manifest.json`.
`tools/render-charts.cjs` renders their 2x PNG exports with an installed Electron
runtime. It checks that labels stay within the canvas and blocks network access.

Articles embed the SVG for sharp text at browser zoom. PNG exports remain the
social-card assets. Each SVG has a `.light.svg` companion. The image hook and CSS
select the pair using the site's theme, including the full-size link. Backgrounds
and neutral ink match the Hugo palette. Data fills stay consistent, while direct
labels use darker ink in light mode. Pie interior ink remains dark in both modes.
Do not list vector pairs under `themeImages`, reserved for legacy transparent
charts. Avoid card borders around charts so they blend into the page.

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
