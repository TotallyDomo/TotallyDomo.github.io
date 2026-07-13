# Charts for content/posts/shipping-unity-doc-corpus-claude.md
# Regenerate: python scripts/post_charts.py  (writes static/img/posts/unity-corpus/)
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


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
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


if __name__ == "__main__":
    build_shootout()
    ranker_vs_representation()
    spend_split()
