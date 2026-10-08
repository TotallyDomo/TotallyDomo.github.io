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
#
# --- tokenomics.md (writes static/img/posts/tokenomics/)
# Illustrative calculations designed 2026-10-04, rates verified 2026-10-08:
# cache writes 2 TC/token, cache reads 0.1 TC/token, output 5 TC/token.
# Standard global Sonnet 5 API: $2/MTok input, $4/MTok one-hour writes,
# $0.20/MTok cached reads, $10/MTok output; hence 1 million TC = $2.
# https://platform.claude.com/docs/en/models/sonnet-5/overview#pricing
# Context growth: a warm 15K prefix plus 1K new input per turn, including the
# previous 500-token response; 500 output tokens per turn; no cache expiry.
# Startup comparison: one prefix write plus 99 reads; task work excluded.
# Keep-alive: warm 800K prefix, 1h TTL, reads every 55 minutes; all reads hit.
# Both waiting strategies include resume; new messages/output are excluded.
# At an exact timer boundary, the plotted resume follows the keep-alive.
# These figures use closed-form arithmetic, not measured session totals.

import math
import os
from pathlib import Path
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
    # Attribution is billed-at-emission, one bucket per rate - that is what reconciles to
    # the CLI's own cost_usd, and why cache write stays at the 1h 2.00 rate the run was
    # actually billed at (1.25 would land 15% under). Deliberately NOT lifetime/marginal
    # attribution: an emitted output token is also cached once and re-read on later turns,
    # so the visible text's marginal cost exceeds its bar - 2.9% -> 3.4% of dollars for
    # the style-off session; the vibemax session's visible text is all on the last API
    # turn, so its 0.9% is already exact. The post's "Not all output tokens cost the same"
    # section carries that view; the chart stays on billed buckets so totals reconcile.
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


OUT_TOKENOMICS = os.path.join(os.path.dirname(__file__), "..", "static", "img",
                            "posts", "tokenomics")
TOKENOMICS_STYLE = {
    "font.family": "DejaVu Sans", "font.size": 15,
    "text.color": TEXT, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": LINE, "axes.facecolor": BG,
    "figure.facecolor": BG, "svg.fonttype": "none",
    "svg.hashsalt": "tokenomics",
}
TOKENOMICS_ORANGE = "#de7422"


def _save_tokenomics(fig, stem, dpi=180):
    os.makedirs(OUT_TOKENOMICS, exist_ok=True)
    for extension in ("png", "svg"):
        path = os.path.join(OUT_TOKENOMICS, f"{stem}.{extension}")
        metadata = {"Date": None} if extension == "svg" else None
        fig.savefig(path, dpi=dpi, transparent=True, metadata=metadata)
        if extension == "svg":
            # WHY: Matplotlib path whitespace otherwise fails the commit's whitespace check.
            svg = Path(path)
            clean = "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())
            svg.write_text(clean + "\n", encoding="utf-8", newline="\n")
        print("wrote", path)
    plt.close(fig)


@plt.rc_context(TOKENOMICS_STYLE)
def tokenomics_context_growth():
    """Render the warm-context per-turn cost example as PNG and SVG."""
    turns = [1, 50, 100]
    rows = [2, 1, 0]
    reads = [(15_000 + (turn - 1) * 1_000) * 0.1 / 1000 for turn in turns]
    totals = [cached + 2 + 2.5 for cached in reads]
    assert totals == [6.0, 10.9, 15.9]

    fig, ax = plt.subplots(figsize=(11, 5.8))
    fig.subplots_adjust(left=0.16, right=0.98, top=0.71, bottom=0.18)
    fig.text(0.055, 0.915, "Cost per turn as context grows", fontsize=23, weight="bold")
    ax.barh(rows, reads, height=0.52, color="#31517e", label="Cached input")
    ax.barh(rows, [2] * 3, left=reads, height=0.52, color=BLUE, label="Cache writes")
    ax.barh(rows, [2.5] * 3, left=[value + 2 for value in reads], height=0.52,
            color=TOKENOMICS_ORANGE, label="Output")
    for row, cached, total in zip(rows, reads, totals):
        ax.text(cached / 2, row, f"{cached:g}K", ha="center", va="center",
                color="#f5f8fc", fontsize=15, weight="bold")
        ax.text(cached + 1, row, "2K", ha="center", va="center", color=BG,
                fontsize=15, weight="bold")
        ax.text(cached + 3.25, row, "2.5K", ha="center", va="center", color=BG,
                fontsize=15, weight="bold")
        ax.text(total + 0.28, row, f"{total:g}K TC", ha="left", va="center",
                fontsize=16, weight="bold")
    ax.set_xlim(0, 18.5)
    ax.set_ylim(-0.55, 2.55)
    ax.set_xticks([0, 5, 10, 15])
    ax.set_yticks(rows, [f"Turn {turn}" for turn in turns])
    ax.set_xlabel("Cost per turn (thousand TC)", fontsize=14, labelpad=14)
    ax.tick_params(axis="x", length=0, pad=10, labelsize=13)
    ax.tick_params(axis="y", colors=TEXT, length=0, pad=14, labelsize=16)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=LINE, linewidth=0.8)
    ax.spines[:].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.005, 1.08), ncol=3,
              frameon=False, fontsize=14, labelcolor=TEXT,
              handlelength=1.3, columnspacing=1.7)
    _save_tokenomics(fig, "context-growth-cost")


@plt.rc_context(TOKENOMICS_STYLE)
def tokenomics_cold_boot():
    """Render startup-prefix TC totals and matching Sonnet 5 API equivalents."""
    turns = list(range(1, 101))
    small = [15_000 * (2 + (turn - 1) * 0.1) for turn in turns]
    large = [45_000 * (2 + (turn - 1) * 0.1) for turn in turns]
    usd_per_tc = 2 / 1_000_000
    assert round(small[-1]) == 178_500 and round(large[-1]) == 535_500
    assert round(large[-1] - small[-1]) == 357_000
    assert round((large[-1] - small[-1]) * usd_per_tc, 3) == 0.714

    fig, ax = plt.subplots(figsize=(11, 6.4))
    fig.subplots_adjust(left=0.12, right=0.96, top=0.72, bottom=0.18)
    fig.text(0.065, 0.935, "15K vs. 45K startup context", fontsize=24, weight="bold")
    fig.text(0.065, 0.88, "The setup cost keeps accumulating after the first turn.",
             fontsize=14, color=MUTED)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=LINE, linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(length=0, pad=9)
    ax.set_xlim(1, 100)
    ax.set_xticks([1, 20, 40, 60, 80, 100])
    ax.set_xlabel("Model turns", labelpad=12)
    ax.fill_between(turns, [value / 1000 for value in small],
                    [value / 1000 for value in large], color=BLUE, alpha=0.07)
    ax.plot(turns, [value / 1000 for value in large], color=TOKENOMICS_ORANGE,
            linewidth=3, label="45K startup context")
    ax.plot(turns, [value / 1000 for value in small], color=BLUE,
            linewidth=3, label="15K startup context")
    ax.set_ylim(0, 625)
    ax.set_yticks([0, 150, 300, 450, 600])
    ax.set_ylabel("Cumulative setup cost (thousand TC)", labelpad=12)
    ax.annotate(f"535.5K TC\n(~${large[-1] * usd_per_tc:.2f})",
                xy=(100, large[-1] / 1000), xytext=(-7, 10),
                textcoords="offset points", color=TOKENOMICS_ORANGE,
                ha="right", va="bottom", fontsize=14, weight="bold")
    ax.annotate(f"178.5K TC\n(~${small[-1] * usd_per_tc:.2f})",
                xy=(100, small[-1] / 1000), xytext=(-7, -10),
                textcoords="offset points", color=BLUE,
                ha="right", va="top", fontsize=14, weight="bold")
    ax.text(48, 183, f"357K TC saved (~${(large[-1] - small[-1]) * usd_per_tc:.2f})\nover 100 turns",
            fontsize=15, weight="bold", color=BLUE)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.015), ncol=2,
              frameon=False, fontsize=13)
    fig.text(0.54, 0.027,
             "Standard Sonnet 5 API, 1h caching | 1 million TC = $2 | Rates checked 2026-10-08",
             ha="center", fontsize=10, color=MUTED)
    _save_tokenomics(fig, "cold-boot-comparison")


@plt.rc_context({**TOKENOMICS_STYLE, "font.size": 11})
def tokenomics_keep_alive():
    """Render the four-hour wait and idealized keep-alive break-even example."""
    from matplotlib.ticker import FuncFormatter

    prefix, interval = 800_000, 55
    read_cost, cold_cost = prefix * 0.1, prefix * 2
    break_even_requests = 19
    break_even_hours = break_even_requests * interval / 60
    hours = [minute / 60 for minute in range(61, 1201)]
    requests = [math.floor(hour * 60 / interval + 1e-9) for hour in hours]
    warm_costs = [(count + 1) * read_cost for count in requests]
    assert cold_cost == 1_600_000 and (4 + 1) * read_cost == 400_000
    assert (break_even_requests + 1) * read_cost == cold_cost

    fig, (left, right) = plt.subplots(1, 2, figsize=(14, 6.2),
                                     gridspec_kw={"width_ratios": [0.9, 1.25]})
    fig.subplots_adjust(left=0.14, right=0.965, top=0.74, bottom=0.17, wspace=0.38)
    fig.text(0.06, 0.935, "Keep the cache warm while the task is still in flight.",
             fontsize=21, weight="bold")
    fig.text(0.06, 0.875,
             "Illustrative model: 800K-token prefix | 2 TC/write | 0.1 TC/read | keep-alive every 55 minutes",
             fontsize=11, color=MUTED)
    left.set_title("A four-hour wait", loc="left", fontsize=15, weight="bold", pad=19)
    left.barh(1, cold_cost / 1000, height=0.46, color=TOKENOMICS_ORANGE)
    left.barh(0, 5 * read_cost / 1000, height=0.46, color=BLUE)
    left.set_yticks([0, 1], ["Keep warm\nthen resume", "Let expire\nthen resume"])
    left.set_xlim(0, 1950)
    left.set_ylim(-0.7, 1.65)
    left.set_xticks([0, 400, 800, 1200, 1600])
    left.set_xlabel("Prefix cost (thousand TC)", labelpad=12)
    left.text(1630, 1, "1,600K", va="center", fontsize=11, weight="bold")
    left.text(435, 0, "400K", va="center", fontsize=11, weight="bold", color=BLUE)
    left.text(0.02, 0.93, "75% lower cost", transform=left.transAxes,
              color=BLUE, fontsize=15, weight="bold")

    right.set_title("How long until keep-alives cost as much?", loc="left",
                    fontsize=15, weight="bold", pad=19)
    right.axhline(cold_cost / 1_000_000, color=TOKENOMICS_ORANGE, linewidth=2, linestyle="--")
    right.step(hours, [cost / 1_000_000 for cost in warm_costs],
               where="post", color=BLUE, linewidth=2.5)
    right.text(1.5, 1.67, "Cold resume", color=TOKENOMICS_ORANGE, fontsize=11)
    right.text(9, 0.60, "Keep-alives + resume", color=BLUE, fontsize=11)
    right.fill_between(hours, [cost / 1_000_000 for cost in warm_costs], cold_cost / 1_000_000,
                        where=[cost < cold_cost for cost in warm_costs],
                        step="post", color=BLUE, alpha=0.07)
    right.plot([4], [0.4], "o", color=BLUE, markersize=6)
    right.annotate("4h: 400K TC", xy=(4, 0.4), xytext=(5, 0.2), fontsize=10, color=BLUE)
    right.plot([break_even_hours], [1.6], "o", color=TEXT, markersize=6)
    right.annotate("19 keep-alives + resume\n~17h 25m: break-even",
                   xy=(break_even_hours, 1.6), xytext=(8, 1.93), fontsize=10,
                   arrowprops={"arrowstyle": "-", "color": MUTED, "linewidth": 1})
    right.set_xlim(1, 20)
    right.set_ylim(0, 2.2)
    right.set_xticks([1, 4, 8, 12, 16, 20])
    right.set_yticks([0, 0.4, 0.8, 1.2, 1.6, 2.0])
    right.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    right.set_xlabel("Hours without a useful model request", labelpad=12)
    right.set_ylabel("Prefix cost (million TC)", labelpad=10)
    for axis in (left, right):
        axis.set_axisbelow(True)
        axis.grid(axis="x" if axis is left else "y", color=LINE, linewidth=0.8)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.tick_params(axis="both", length=0, pad=8)
    _save_tokenomics(fig, "keep-alive-payoff", dpi=160)


if __name__ == "__main__":
    import sys
    all_charts = {f.__name__: f for f in
                  [build_shootout, ranker_vs_representation, spend_split,
                   session_cost_composition, tokenomics_context_growth,
                   tokenomics_cold_boot, tokenomics_keep_alive]}
    picked = sys.argv[1:] or list(all_charts)
    for name in picked:
        all_charts[name]()
