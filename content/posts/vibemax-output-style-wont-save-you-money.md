---
title: "Vibemax - Your Agent's Output Style Won't Save You Money"
date: 2026-07-28
description: "I built a low-narration response style to cut my agent's output-token bill. The measured answer: that lever barely exists. What it buys instead is reading time."
image: "/img/posts/vibemax-output-style-wont-save-you-money/session-cost-composition.png"
themeImages:
  - "/img/posts/vibemax-output-style-wont-save-you-money/session-cost-composition.png"
draft: false
---

I was vibecoding a weekend project - a custom keyboard RGB controller daemon - when I
noticed one annoying habit of my agent. While working, Claude narrates the process ("now
I'm doing this", "next step - implementing the controller...", etc.). That narration is
useful when you are monitoring closely and waiting to steer the agent where you want it to
go, but it was useless noise for me. I didn't want to know how the implementation works,
or the process in general - I just wanted the end result (and also to test what an AI
agent can and can't do on its own). That's when I got the idea of the "vibemaxing" style -
for when you just want to lie back and enjoy the vibe ride. The idea is simple: drop all
narration and explanation output and go straight to the core. Fewer agent output tokens
spent, less text on screen - overall better vibes.

The end result is [Vibemax](https://github.com/TotallyDomo/vibemax) - a tiny
skill for Claude Code, a single markdown file that drops all unnecessary narration. (A
skill, to be precise - the "output style" in the title is plain English, not Claude
Code's retired output-styles setting.) A neat at-least-do-no-harm microskill, with the
exact cost math below: I've been using it
for weeks in my own sessions, and I barely remember it is there - the output just got shorter.
Also, a quieter agent doesn't mean a more autonomous one - every question the agent
would normally raise is still raised; in three weeks of daily use I never caught it
swallowing one.

Visual example taken from the benchmarking run: same model, same prompt, one run with
the style off and one with it on. The exact prompt both runs got:

```text
Add a --level flag to logsift: filter entries to those at or above a minimum severity,
ordering debug < info < warn < error, and treat entries with an unknown or missing level
as info. Update the README usage section to document it. Everything else stays as is.
```

Everything the agent printed to the screen, verbatim (lines wrapped for width):

**Style off - 308 visible tokens:**

```text
I'll help you add a `--level` flag to logsift. Let me first explore the repository
structure to understand the current implementation.
Now I'll add the `--level` flag functionality. First, I'll add a filter function to handle
level-based filtering.
Now I'll update the CLI to add the `--level` flag and integrate it with the filter:
Finally, I'll update the README to document the new flag:
Let me verify the changes are correct:
Done! I've added the `--level` flag to logsift with the following changes:

**filters.py:**
- Added `LEVEL_ORDER` constant defining the severity hierarchy (debug=0, info=1, warn=2,
  error=3)
- Created `by_level()` filter function that yields entries at or above the specified level,
  treating missing/unknown levels as info

**cli.py:**
- Added `--level` argument with choices: debug, info, warn, error
- Integrated the filter into main() to apply it when the flag is provided

**README.md:**
- Added usage example and documentation explaining the level hierarchy and how missing
  levels are handled

The implementation respects the severity ordering (debug < info < warn < error), treats
unknown/missing levels as info, and only activates when the flag is specified. All other
functionality remains unchanged.
```

**Vibemax on - 156 visible tokens:**

```text
Done. I've added the `--level` flag to filter log entries by minimum severity:

**Changes:**
- **filters.py**: Added `LEVEL_ORDER` constant (debug=0, info=1, warn=2, error=3),
  `get_level_value()` to extract entry severity (defaulting to info), and `by_level()`
  filter function
- **cli.py**: Added `--level` argument accepting debug/info/warn/error; applied filter
  in main when specified
- **README.md**: Added usage example and documented level behavior

The implementation treats missing/unknown levels as info, filters only when `--level` is
specified (preserving backward compatibility), and handles case-insensitive input.
```

Both examples are their arm's median run by visible output, over ten runs each
(Claude Haiku 4.5, my A/B harness, 2026-07-28). Across those ten runs per side,
total API output tokens (reasoning included) showed no detectable difference: the
means landed about 6% apart - the styled arm slightly higher, and the gap well
inside the run-to-run spread.
The narration halved, the token bill did not move. Why?

## Tokenomics, and why focusing on the output is the wrong idea

The expensive part of every model is the output tokens (Claude prices them at 5x input),
so cutting as much output as possible might seem like the correct move when trying to
optimize token usage. But the report the agent prints when it finishes is only a small
slice of what the model actually emits. 

Most of the real cost sits in the tool-call loop and in reasoning tokens (billed as output too). 
Each tool call is a turn, and every turn re-reads the whole prompt - which is mostly the 
fixed system prompt and tool schemas rather than the part that grows; in the style-off 
session below, about three quarters of the cache-read bill is that unchanging prefix, 
re-read twelve times. Even at the cached-input multiplier of 0.1x those re-reads add up, 
and whatever each turn appends gets written into the cache at a premium (2x input, 
at the one-hour cache TTL these sessions used). That cache traffic is what dominates 
the bars in the chart below. 

Reasoning cost can be controlled with the agent's effort setting, but set it too low and the 
quality of the end result suffers. It is a hard balance between efficiency and quality, and it 
stays mostly invisible unless you go looking for it. What is always visible is the text the
agent prints when it finishes - and the instinct is to cut the fat from the things you can see.

![Cost composition of the two demo sessions in two lanes each, tokens and list-price USD: cache reads and cache writes dominate both, the output tokens you never read come next, and the text a human actually reads is an orange sliver - 0.2% and 0.04% of tokens, about 3% and 1% of the dollars ($0.0015 and $0.0008). Bar-end figures are each session's total work: 182K and 392K tokens, $0.054 and $0.088](/img/posts/vibemax-output-style-wont-save-you-money/session-cost-composition.png)

Those are the exact two sessions from the demo above, priced at API list rates. The
figure at the end of each bar is that session's total work - all tokens in, all tokens
out, and the full cost of it. The orange sliver is the only part a human
ever reads: 0.2% and 0.04% of the tokens, about 3% and 1% of the dollars - $0.0015 and
$0.0008 out of the $0.054 and $0.088 the sessions cost. 

Uncached input is in the totals but too small to draw at all - 66 and 130 tokens. 
The Vibemax run happened to do more verification work - 21 API turns against 12 - which is 
why its bars are longer; run-to-run work volume swamps any style effect on totals, and that 
is exactly the point. 

Haiku drew the demo, but the picture is not Haiku-specific: the repo's grid
runs the same A/B on four Claude models, and the human-read slice is marginal on all
of them.

## Not all output tokens cost the same

An output token is not billed once. It costs the output rate the moment it is emitted, and
then it **stays** in the context: written into the cache once, then re-read on every remaining
turn of the session. So its real price depends on *when* it was emitted. Emitted on the
first of twelve turns, a token costs about 1.6x its face output rate; in a fifty-turn
session, 2.4x; in a hundred-turn one, 3.4x. Emitted in the closing message it costs face
value exactly - the session ends, and nothing ever reads it again.

That is precisely the difference between the two kinds of text in the demo. The style-off
run's five "now I'll..." lines sit on turns 1 through 9 of 12, so they cost about 1.5x
face. Every visible token of the Vibemax run is in the closing report, on the last turn,
at 1.0x. Mid-task narration is the most expensive shape of output an agent produces and
the closing report is the cheapest - so the style deletes the expensive kind and keeps the
cheap one, and the gap widens the longer the session runs. In an interactive session the
closing report is not really final either, since it sits in context for every later user
turn, so there the same amplification applies to nearly all of what the style cuts.

It is still a rounding error. Priced this way, the human-read sliver goes from 2.9% to
3.4% of the style-off session's dollars, and the Vibemax one does not move at all. The
chart puts every token in the bucket it was billed in, which is what makes it reconcile
against the invoice. The higher figure is the marginal one - what you would actually stop
paying if the text were never printed.

## About output compression

Not all agent output is strictly human-facing. When you send a new message in a session,
the agent re-reads the entire session history to orient itself. Certain words and phrases
help the future next-turn agent know where the process stands. Markers like "verified",
"assumption", or "confidence: low" ground it in what is proven versus what is merely
inferred - one of the guardrails that stops agents from hallucinating and serving garbage
as truth. If your agent starts acting stupid, the current context may be rotten (full of
contradictions) and it might be time to start a fresh session.

A compressed, [caveman-like](https://github.com/JuliusBrussee/caveman) output omits
exactly that agent-guiding information. Future turns get more confused and produce worse
output, and the slop snowballs. The same deletion burns the human too: a dropped hedge
hides uncertainty. Compressed output reads more confident than the model actually is,
and you can no longer tell audited claims from guesses.

On top of that, extra styling restrictions introduce a "thinking tax" - reasoning tokens
spent on "how am I supposed to output this" instead of just outputting the thing.
That same tax is why most language-compression styles (leetspeak, dropped grammar,
abbreviation schemes) don't actually pay off: the model spends reasoning tokens translating
itself into the compressed register, and burns what the shorter text saved.

The other tempting shortcut is a one-line "be concise". That hands the cutting decision
to the model, and the model cuts whatever looks like filler - which, statistically, is
the hedges, the assumptions, and the mid-paragraph questions. The exact lines you needed
to see go first. Vibemax spells out both lists instead - what gets dropped and what
always gets through - so brevity never gets to negotiate against the important stuff.

## Output selection

[Vibemax](https://github.com/TotallyDomo/vibemax) does selection instead of
compression. The agent suppresses the pre-determined narration output and leaves the core
untouched. Dropping the play-by-play is safe because it is redundant: the tool calls
and diffs already sit in the session history, so the future-turn agent loses nothing.

The hedges and assumptions have no such backup channel - the report is the only place
they exist, which is why selection keeps them. Four things are always guaranteed airtime: questions, caveats, assumptions,
and a short result - exactly the categories you shouldn't skim past. It still pays
a bit of thinking tax, but my benchmarking shows it roughly pays
for itself: in day-to-day telemetry the net effect on the bill is a rounding error
(well under a percent), and the controlled grid leaned the same direction or better -
the receipts, and the caveats that keep me from quoting the grid's effect sizes as
fact, are in the repo's [benchmarks](https://github.com/TotallyDomo/vibemax/tree/main/benchmarks)
and the tokenomics section of
[DESIGN.md](https://github.com/TotallyDomo/vibemax/blob/main/DESIGN.md). The
bigger win is the terseness, and the user's saved reading time.

However, within design discussions (like [grill-me](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md)
process, spec creation, etc.) the narration is the steering wheel - Vibemax is built for 
execution-shaped work, not for thinking out loud together. And it optimizes your reading time, 
so an unattended pipeline nobody reads gains nothing from it.

## Lessons learned

1. Part of an agent's output is aimed at future agents, to help them navigate the
   context.
2. Chasing token savings through a style guide is aiming at the wrong target.
3. A style's token tax is twofold: input tokens for the contract itself, and
   reasoning/output tokens spent following it.
4. An output token's price depends on when it was emitted. Early narration keeps getting
   re-read for the rest of the session; the closing report never does.
5. The real style savings are in user attention and reading time.

After this project, I started experimenting with my own "agent report" style. It is still
in progress, but I already feel that a familiarly-shaped report is faster to parse, which
helps me stay focused when working with multiple agents on multiple problems at the same
time. The next blog post will be a summary of those findings, and will not include a
GitHub repo. Report styles are very subjective - I think the best one is the one you
create yourself.

*Written by me, structured with AI. [How I write.](/about/)*
