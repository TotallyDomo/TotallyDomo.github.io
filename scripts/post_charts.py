# Charts for the blog posts (one section per post below).
# Regenerate all: python scripts/post_charts.py
# Regenerate one: python scripts/post_charts.py <function-name> [...]
#
# --- shipping-unity-doc-corpus-claude.md (writes static/img/posts/unity-corpus/)
# Data provenance: build times from the four preserved 2026-06-28 build manifests;
# recall lanes from unity-doc-corpus docs/benchmark-6000.3.json reference run;
# spend split from local agent telemetry, final recount 2026-07-13 evening
# (M0028-S6): sessions with 10+ "corpus" mentions in the raw transcript,
# joined against agent_telemetry session_summary rows; Claude env-root
# 136 sessions / 756.6M tokens / $1254 (pre-2026-07-09 UTC: 229.2M, $346;
# after, through 2026-07-13: 527.4M, $908), Codex 33 sessions / 55.7M / ~$29.
# USD is list-price equivalent priced per session from model_mix components
# at the collector's api-pricing-2026-07-02 table (go/cost.go).

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- blog theme (static/css/main.css) ---
BG = "#0d1117"
TEXT = "#e6edf3"
MUTED = "#8b98a9"
LINE = "#2a313c"
BLUE = "#4c8dff"   # baseline series
ORANGE = "#db6d28" # highlighted series (validated pair, dark surface)
FONT = "Segoe UI"

OUT = os.path.join(os.path.dirname(__file__), "..", "static", "img", "posts", "unity-corpus")

plt.rcParams.update({
    "font.family": FONT,
    "text.color": TEXT,
    "axes.edgecolor": LINE,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
    "savefig.transparent": True,
})


def strip_axes(ax, keep_x=False):
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_visible(keep_x)
    if keep_x:
        ax.spines["bottom"].set_color(LINE)


def save(fig, name, out=OUT):
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("wrote", path)


# --- 1. Build shootout: one evening, four builders ------------------------
def build_shootout():
    labels = ["Python (one-shot)", "C++", "Go", "Go, 8 workers"]
    rework = [245.4, 0, 0, 0]           # Python re-reading its own output
    other = [385.7 - 245.4, 67.6, 62.9, 38.0]
    totals = [385.7, 67.6, 62.9, 38.0]

    fig, ax = plt.subplots(figsize=(7.0, 2.5))
    y = range(len(labels))[::-1]
    ax.barh(y, other, height=0.55, color=BLUE, edgecolor=BG, linewidth=1)
    ax.barh(y, rework, left=other, height=0.55, color=ORANGE, edgecolor=BG, linewidth=1)

    for yi, total in zip(y, totals):
        ax.text(total + 6, yi, f"{total:.1f} s", va="center", color=TEXT, fontsize=10)
    ax.annotate(
        "245 s re-reading its own output\njust to hash and count it",
        xy=(140.3 + 122, 3), xytext=(240, 1.95),
        color=ORANGE, fontsize=9.5, ha="left", va="top",
        arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8),
    )

    ax.set_yticks(list(y), labels)
    ax.tick_params(axis="y", length=0, labelsize=10.5)
    ax.tick_params(axis="x", length=0, labelsize=9)
    ax.set_xlim(0, 455)
    ax.set_xlabel("full corpus build, seconds", fontsize=9.5)
    ax.xaxis.grid(True, color=LINE, linewidth=0.8)
    ax.set_axisbelow(True)
    strip_axes(ax)
    save(fig, "build-shootout.png")


# --- 2. Recall: ranker vs representation ----------------------------------
def ranker_vs_representation():
    lanes = ["naive scan\nraw HTML", "naive scan\nderived Markdown",
             "bm25 index\nraw HTML", "bm25 index\nthe corpus"]
    all_cases = [93.8, 95.0, 96.9, 96.8]
    manual = [59.1, 62.4, 95.7, 95.7]

    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    x = range(len(lanes))
    w = 0.36
    ax.bar([i - w / 2 for i in x], all_cases, width=w, color=BLUE,
           edgecolor=BG, linewidth=1, label="all 1,008 cases")
    ax.bar([i + w / 2 for i in x], manual, width=w, color=ORANGE,
           edgecolor=BG, linewidth=1, label="concept (Manual) pages only")

    for i, v in zip(x, all_cases):
        ax.text(i - w / 2, v + 2, f"{v:.0f}", ha="center", color=TEXT, fontsize=9)
    for i, v in zip(x, manual):
        ax.text(i + w / 2, v + 2, f"{v:.0f}", ha="center", color=TEXT, fontsize=9)

    ax.set_xticks(list(x), lanes, fontsize=9.5)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 108)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.tick_params(axis="y", labelsize=9, length=0)
    ax.set_ylabel("top-10 recall, %", fontsize=9.5)
    ax.yaxis.grid(True, color=LINE, linewidth=0.8)
    ax.set_axisbelow(True)
    leg = ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=2,
                    fontsize=9, frameon=False, columnspacing=1.6)
    for t in leg.get_texts():
        t.set_color(TEXT)
    strip_axes(ax)
    save(fig, "ranker-vs-representation.png")


# --- 3. Token spend: building vs shipping ----------------------------------
def spend_split():
    # Claude-side split at the 2026-07-09 public date, data through 2026-07-13.
    # USD = API list-price equivalent from per-session model mix (input/output/
    # cache-read/cache-write at api-pricing-2026-07-02 rates) - tokens alone
    # flatten the picture because cache reads dominate volume but not cost.
    build_tok, ship_tok = 229.2, 527.4  # millions of tokens
    build_usd, ship_usd = 346, 908      # list-price USD

    lanes = [
        ("tokens", f"{build_tok:.0f}M", f"{ship_tok:.0f}M", build_tok / (build_tok + ship_tok)),
        ("list-price USD", f"${build_usd}", f"${ship_usd}", build_usd / (build_usd + ship_usd)),
    ]

    fig, ax = plt.subplots(figsize=(7.0, 1.9))
    for y, (label, btxt, stxt, bfrac) in zip([1, 0], lanes):
        ax.barh([y], [bfrac], height=0.62, color=BLUE, edgecolor=BG, linewidth=1)
        ax.barh([y], [1 - bfrac], left=[bfrac], height=0.62, color=ORANGE, edgecolor=BG, linewidth=1)
        head_b = "building the tool\n" if y == 1 else ""
        head_s = "validating + shipping it\n" if y == 1 else ""
        ax.text(bfrac / 2, y, f"{head_b}{btxt} ({bfrac * 100:.0f}%)",
                ha="center", va="center", color=BG, fontsize=9.5, fontweight="bold")
        ax.text(bfrac + (1 - bfrac) / 2, y, f"{head_s}{stxt} ({(1 - bfrac) * 100:.0f}%)",
                ha="center", va="center", color=BG, fontsize=9.5, fontweight="bold")

    ax.set_yticks([1, 0], [lane[0] for lane in lanes])
    ax.tick_params(axis="y", length=0, labelsize=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.55, 1.55)
    ax.xaxis.set_visible(False)
    strip_axes(ax)
    save(fig, "spend-split.png")


# --- vibemax-output-style-wont-save-you-money.md
#     (writes static/img/posts/vibemax-output-style-wont-save-you-money/)

OUT_VIBEMAX = os.path.join(os.path.dirname(__file__), "..", "static", "img", "posts",
                           "vibemax-output-style-wont-save-you-money")


# --- 4. Session cost composition: the two demo sessions --------------------
def session_cost_composition():
    # Data provenance: vibemax/benchmarks/results/grid.jsonl, M0027-S10 grid run of
    # 2026-07-28, model claude-haiku-4-5-20251001, jobs grid-haiku-t1-blind-r02 and
    # grid-haiku-t1-vibemax-r06 (the two transcripts shown in the post; both sit at
    # their arm's median visible tokens over n=10). Per-session token components from
    # the stored turn accounting; "visible" = visible_chars/4 (308 and 156 tok).
    # USD lane priced per component at the collector's list table (agent-telemetry
    # go/cost.go claudePrice(1.00, 5.00): input 1.00, cache read 0.10, cache write
    # 2.00 (1h), output 5.00 per MTok); component sums land within 1.3% of the
    # harness's stored cost_usd (0.0537 vs 0.0543; 0.0877 vs 0.0883). The vibemax
    # session ran more verification (21 api turns vs 12), so its absolute totals are
    # larger; the chart's claim is composition, not arm totals. Fresh uncached input
    # (66 and 130 tokens, ~$0.0001) is folded into the totals but not drawn as its
    # own segment - it is sub-pixel at this scale; the caption says so.
    sessions = [
        # label, cache_read, cache_write, fresh_in, output_hidden, visible
        ("Style off", 168_145, 10_017, 66, 3_352 - 308, 308),
        ("Vibemax on", 374_142, 13_473, 130, 4_637 - 156, 156),
    ]
    rates = {"cache_read": 0.10e-6, "cache_write": 2.00e-6, "fresh_in": 1.00e-6,
             "output": 5.00e-6}
    seg_colors = ["#2f4f7d", "#3d6cb3", BLUE, ORANGE]
    seg_labels = ["cache reads", "cache writes",
                  "output you never read (reasoning, tool calls)", "the text you read"]

    rows = []  # (ylabel, [four drawn segment values], total_label, total_sublabel)
    for label, cr, cw, fi, oh, vis in sessions:
        tok = [cr, cw, oh, vis]
        usd = [cr * rates["cache_read"], cw * rates["cache_write"],
               oh * rates["output"], vis * rates["output"]]
        tok_total = sum(tok) + fi
        usd_total = sum(usd) + fi * rates["fresh_in"]
        rows.append((f"{label}\ntokens", tok, f"{tok_total / 1000:.0f}K",
                     "total work"))
        rows.append((f"{label}\nlist-price USD", usd, f"${usd_total:.3f}",
                     "total work cost"))

    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ys = [3, 2, 0.8, -0.2]
    for y, (label, vals, total, sub) in zip(ys, rows):
        total_v = sum(vals)
        left = 0.0
        for v, c in zip(vals, seg_colors):
            ax.barh([y], [v / total_v], left=[left], height=0.6, color=c,
                    edgecolor=BG, linewidth=1)
            left += v / total_v
        ax.text(1.015, y + 0.03, total, va="bottom", color=TEXT, fontsize=9.5)
        ax.text(1.015, y - 0.03, sub, va="top", color=MUTED, fontsize=7.5)

    # visible-share callouts, one per lane pair (token lanes: sliver is subpixel);
    # arrows land ON the orange USD segment (style off: 0.971-1.0 at y=2,
    # vibemax: 0.991-1.0 at y=-0.2). Dollar figures = visible tok * output rate
    # (308 -> $0.0015, 156 -> $0.0008).
    ax.annotate("the text you read: 0.2% of tokens, 2.9% of dollars ($0.0015)",
                xy=(0.985, 1.9), xytext=(0.44, 1.42),
                color=ORANGE, fontsize=9, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("0.04% of tokens, 0.9% of dollars ($0.0008)",
                xy=(0.9955, -0.3), xytext=(0.58, -1.05),
                color=ORANGE, fontsize=9, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

    ax.set_yticks(ys, [r[0] for r in rows])
    ax.tick_params(axis="y", length=0, labelsize=9.5, labelcolor=TEXT)
    ax.set_xlim(0, 1)
    ax.set_ylim(-1.35, 3.8)
    ax.xaxis.set_visible(False)
    leg = ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in seg_colors],
                    labels=seg_labels, loc="lower center", bbox_to_anchor=(0.5, 1.0),
                    ncols=2, fontsize=8.2, frameon=False, columnspacing=1.4,
                    handlelength=1.1, handleheight=1.1)
    for t in leg.get_texts():
        t.set_color(TEXT)
    strip_axes(ax)
    save(fig, "session-cost-composition.png", out=OUT_VIBEMAX)


if __name__ == "__main__":
    import sys
    all_charts = {f.__name__: f for f in
                  [build_shootout, ranker_vs_representation, spend_split,
                   session_cost_composition]}
    picked = sys.argv[1:] or list(all_charts)
    for name in picked:
        all_charts[name]()
