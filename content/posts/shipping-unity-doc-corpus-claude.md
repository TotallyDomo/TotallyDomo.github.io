---
title: "Shipping My First AI Agent Skill: An (Un)expected Journey"
date: 2026-07-13
draft: false
themeImages:
  - "/img/posts/unity-corpus/spend-split.png"
  - "/img/posts/unity-corpus/ranker-vs-representation.png"
  - "/img/posts/unity-corpus/build-shootout.png"
---

When I first started seriously using coding agents, my favorite part was watching the work unroll live - "let me check one thing" turning into a whole chain of searches, edits, tests, and second thoughts. Since I come from gamedev, my first experiments were obviously Unity ones.

One phrase kept showing up in those sessions: "let me check the Unity docs real quick."

Perfectly reasonable behavior. Also the kind of repeated friction that gets my optimizer cogs turning. My project sits on one pinned Unity version. Unity publishes its entire documentation as an offline archive. And here were my agents, paying the web-search tax over and over for answers that never change.

It became [unity-doc-corpus](https://github.com/TotallyDomo/unity-doc-corpus): a small Go tool that turns Unity's official offline documentation into a local, version-pinned search corpus, plus an Agent Skill - a small instruction file coding agents load on demand - that teaches Claude Code or Codex when and how to use it.

The tool itself came together in one evening. Almost everything after that evening was learning how to ship it - and that turned out to be where all the lessons were. My session logs put the whole journey at 169 agent sessions and roughly 800 million billed tokens, cache reads included - which my telemetry prices at about $1,300 of API list-price equivalent.

## One evening, four builders

The build story is short - the pipeline is four steps, none of them Unity-specific:

1. Fetch the official docs for your pinned version (Unity ships a single zip).
2. Strip the page chrome - navigation, headers, footers, scripts, version switchers.
3. Keep the text in a compact, searchable local form.
4. Give the agent a cheap router skill so it checks locally before reaching for the web.

On the evening of June 28 I pointed Codex at this. The first Python builder was a straight one-shot - one prompt, zero iteration: 385.7 seconds for the full build.

The manifest showed *where* the time went: 245.4 of those seconds were spent re-reading the Markdown files it had just written, purely to hash and count them.

A C++ rewrite ran in 67.6 seconds, 5.7x faster - but I watched the agents visibly struggle harder to build and debug it. So I asked for a third implementation in Go: 62.9 seconds single-threaded, 38.0 with eight workers, byte-for-byte identical output.

Go won on the combination that matters here: I can read it, agents iterate on it quickly, and 39k independent pages is exactly what goroutines are for. Public evidence roughly agrees ([Multi-SWE-bench](https://arxiv.org/abs/2504.02605), [Aider's polyglot benchmark](https://aider.chat/2024/12/21/polyglot.html)), though neither proves Go is universally better; it matched what I saw at my desk.

![Full-corpus build times: Python 385.7 s with 245.4 s of it re-reading its own output, C++ 67.6 s, Go 62.9 s, Go with eight workers 38.0 s](/img/posts/unity-corpus/build-shootout.png)

*The four builders of June 28, straight from the preserved manifests.*

All four builds are stamped within one long evening. By the next morning my agents were querying a local corpus: 39,056 pages, 648 MB of HTML down to 123 MiB on disk, about 4 ms per search. Tool done, I figured.

## "There is nothing quite like it online"

Early in the project, an agent confidently assured me that nothing like this existed online. It felt wrong, but I just shrugged. Turns out, it *was* bullshit.

[Context7](https://context7.com/) already indexes Unity documentation as a hosted service. [unity-api-mcp](https://github.com/Codeturion/unity-api-mcp) does agent-facing Unity API lookup. Dash, Zeal, and DevDocs made offline developer docs a solved problem years ago. I only learned all this because I had decided the README needed a real prior-art comparison - and researching one is a very different activity from asking "is my idea unique?" and enjoying the yes.

The trap generalizes: agents mirror your enthusiasm. If you ask an agent to validate your idea, it will. The prompt that actually works is closer to "do a prior-art pass as if your goal is to kill this project."

Mine survived, but in a smaller, more honest shape: a corpus that is version-pinned to *your* project, built locally and deterministically from the zip *you* fetched, works offline with no service or API key, and ships a benchmark you can rerun. The [design doc](https://github.com/TotallyDomo/unity-doc-corpus/blob/main/docs/DESIGN.md) has the detailed comparison.

## Shipping is where the learning started

Publishing small open-source tools and writing about them is something I had wanted to do for a while, and this looked like the easy starter: tiny, self-contained, already working. One day, tops.

The logs disagree. The repo went public on July 9. Over the next five days it accumulated 45 commits and roughly 5 big README rewrites. About 70% of the measured spend on this project - tokens or dollars - happened *after* the tool already worked.

![Build versus validate-and-ship spend in two lanes: 229M versus 527M tokens, 30 to 70 percent, and 346 versus 908 dollars list-price, 28 to 72 percent](/img/posts/unity-corpus/spend-split.png)

*Measured spend through July 13, split at the July 9 public date. The dollar lane is the honest one - token counts are distorted by cheap cache reads. It all ran on flat-rate subscriptions, though - the dollars are list-price equivalents, not money spent.*

Turns out you can put a thing through one planning session, ten build sessions, and two validation passes and it still comes out of the slop-oven with a broken benchmark and instructions nobody can follow.

I blind-tested the install instructions myself on a clean setup and failed at step one, because later steps had comments about how to do step one. After the rewrite, a blind test agent got further, then wrote its own Python SQLite script - the tool it was told to evaluate had no built-in search command. Both failures paid off: the tool now has a dependency-free `search` verb, and the quickstart became something actually useful.

The benchmark was the deeper lesson. The first version reported a very quotable result: 91.9% top-10 recall for the corpus versus 57.1% for grepping the raw HTML. It was broken in two independent ways. The generated test cases were the head of an alphabetically sorted page list - 100% Manual pages (the prose guides) in a corpus that is 91% ScriptReference (the per-API pages). And the comparison changed the representation (what text gets indexed) and the ranker (how matches get scored) at the same time, so the headline could not say which one produced the gap.

The fixed benchmark holds the ranker constant across representations, and the flattering story fell apart: the same search over raw HTML scores 96.9% versus the corpus's 96.8%. Ranking owns recall - swap the naive scan for a proper ranked index and concept-page recall jumps from ~59% to ~96% while queries drop from ~200 ms to ~4 ms, gains you could get over the raw HTML too.

![Top-10 recall for four lanes crossing ranker and representation, on all cases and on concept pages only](/img/posts/unity-corpus/ranker-vs-representation.png)

*Four lanes, two case sets. Change the representation and nothing moves; change the ranker and concept pages jump ~35 points.*

What the corpus itself buys is the part I had originally undersold: an index around a tenth the size, and page reads that put roughly a tenth of the bytes into the agent's context. A harder suite of 100 realistic agent-style questions sits at 59% top-10 recall - an open problem, printed in the repo docs next to an erratum for the original numbers.

## Blind validation

The single most useful thing I learned: the context that makes an agent an excellent builder makes it an awful validator. A session that spent hours constructing a system knows why every weird choice exists, and that knowledge quietly turns into "looks fine." The fix is context separation - hand a *blind* agent the end product plus only the context a real user would have, and tell it to audit.

A fresh chat is not automatically blind, either. One of my supposedly blind self-reviews was contaminated on turn one by project memory helpfully loading the authoring context back in. If your setup persists memory across sessions, a blind review needs an environment that genuinely does not know the project. Cross-model reviews (Claude auditing Codex work, and vice versa) are cheap to add too, though the bigger lever was the context separation, not the model.

The quietest bug of the project shows what this buys. The HTML parser was silently truncating whole sections from some pages while the unit tests, the recall benchmark, and the spot checks all stayed green. It surfaced only through an independent content audit built to share no code - and therefore no assumptions - with the parser it checks.

A final adversarial review explained why. Everything an auditor can check cheaply - published numbers, hashes, the quickstart - came back clean, because my own validation passes had polished exactly those. It broke only where new work was required: baselines nobody had built, commands nobody had run cold. If every reviewer runs the same cheap checks, you have tested your test, not your tool.

## Pointed questions

The other half of the lesson: agents are like cats. Even when the food bowl still has food in it, they will pretend not to see it until you point at the bowl. The first "audit everything" pass finds real issues. The third returns "Audit Pass: Nothing Found". Specific questions keep finding new problem classes long after generic audits go quiet.

My favorite bug of the project: a blind review caught that the README's disk-footprint number was wrong - 62 MB of "logical" Markdown actually occupied about 176 MB on NTFS, because it was spread across 39 thousand tiny files. The review fixed the *accounting* and moved on. No auditor, blind or otherwise, ever questioned the design.

When I asked "could we transform those 39k files into one big file, like a database?", the agent had a small stroke: first a list of tradeoffs defending the structure that already existed, then - once the numbers were in - an attempt to file a 60% cut under "footprint + ergonomics win, not a retrieval one". The consolidation took the active corpus from roughly 300 MB to 123 MiB, with search recall reproduced to the exact case count. One narrow question found a free 60% lever every audit pass had walked straight past.

![Chat screenshot. Me: HOW THE FUCK NO AGENT SAW THAT BEFORE?! We have like 50 sessions and nobody said "Hey let's combine the markdowns". The agent: Fair. And yeah - this should have been caught the first time someone wrote "store the body in FTS and on disk".](/img/posts/unity-corpus/39k-rebuke.png)

*The moment it landed, verbatim. ("Clankers" is affectionate. Mostly.)*

## Security, which I did not order

A local documentation tool does not sound like it needs security thinking. But this one fetches hundreds of megabytes from the internet and feeds them straight into a coding agent's context. That is an injection surface.

A blind review earned its keep immediately: the fetcher validated that the *initial* URL belonged to an allowed Unity host, but left Go's automatic redirect-following unrestricted - an allowed URL could bounce the download anywhere. Every redirect hop is validated now. The same pass caught that `fetch --force` would happily delete any directory you pointed it at; destructive paths now refuse to touch a directory without the tool's own marker file.

The rest of the posture is mostly about not pretending. The repo ships source only - no binaries, a two-line build - and no doc content anywhere in the tree or its history: Unity's documentation stays Unity's. Fetching talks exclusively to pinned Unity hosts. Every derived page carries a SHA-256 back to its source bytes - which proves your local artifacts stayed consistent, and deliberately does *not* claim provenance: Unity publishes no checksum for the archive, so TLS-to-Unity is the actual trust boundary.

I also ran OpenSSF Scorecard - the standard OSS security-posture checklist - exactly once: 3.9/10. The triage split into fixes with real value (SHA-pinned CI actions, Dependabot, secret scanning) and solo-repo theater like requiring a second human reviewer. I landed the former, skipped the badge, and removed the weekly workflow that kept re-publishing a weak score.

## Lessons learned

1. **Separate builders from validators.** A validator is a blind agent: end product, user-level context only.
2. **Ask the narrow question.** Broad audits saturate; "do we even need this?" keeps opening new problem classes.
3. **Make tools emit their own receipts.** Manifests, benchmarks, telemetry - they spot the problems and prove the fixes.
4. **Split the heavy path from the fast path.** Cheap everyday lookup; fetching and rebuilding only on explicit request.
5. **If it feeds an agent, it is attack surface.** Pinned hosts, validated redirects, honesty about what your hashes prove.

The next release will be leaner and more vibes-based - now I know which parts of the process were worth it. The blind reviews and the benchmark stay; most of the rest can go.

*Written by me, structured with AI. [How I write.](/about/)*
