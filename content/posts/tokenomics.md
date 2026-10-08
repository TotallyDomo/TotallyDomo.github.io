---
title: "Tokenomics - getting the most out of your AI usage"
date: 2026-10-08
description: "Practical ways to reduce AI token costs: trim startup context, manage compaction, and keep prompt caches warm."
image: "/img/posts/tokenomics/context-growth-cost.png"
themeImages:
  - "/img/posts/tokenomics/context-growth-cost.png"
  - "/img/posts/tokenomics/cold-boot-comparison.png"
  - "/img/posts/tokenomics/keep-alive-payoff.png"
draft: false
---

If you find yourself spending too much money on API usage or hitting your Claude or Codex subscription's weekly limits too quickly, this post is for you.
These are my findings and suggestions on how to tokenmax efficiently.



## LLM usage fundamentals

Token costs differ from model to model and from provider to provider, but the general trends stay roughly the same.
Each model has:
- input token cost,
- cached input token cost,
- output token cost.

Cache writes can also have their own rate: [Claude's](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing) one-hour API cache writes cost 2x the regular input token price. [Codex credit billing](https://learn.chatgpt.com/docs/pricing#token-rates) has no separate cache-write charge, but [API cache writes](https://developers.openai.com/api/docs/guides/prompt-caching) for GPT-5.6 and later cost 1.25x.

Since not all tokens are created equal, we will use simplified Token Credits (TC) to make our hypothetical scenarios easier to calculate, using an illustrative one-hour cache pricing model:
- 1 input token = 1 TC,
- 1 cache write token = 2 TC,
- 1 cached input token = 0.1 TC,
- 1 output token = 5 TC.

We can use them to easily calculate combined API cost using [standard Sonnet 5 API rates](https://platform.claude.com/docs/en/models/sonnet-5/overview#pricing) (1 million TC = $2).

For the calculations below, a "turn" means one model request and its response. Every turn submits the entire context back to the agent. A single user message can trigger many turns: the model calls a tool, receives the result, and reasons about what to do next. It's not uncommon for longer agent sessions to reach hundreds or thousands of these turns.
You can see how, while individually cheap, input and cached input tokens can still account for the lion's share of a session's budget.

Output tokens fall into two categories: the visible "work" of the agent - messages, responses, generated code, etc. - and the reasoning traces (chain of thought, CoT), which usually stay hidden from the user because they are not super useful to see.
Effort levels control how much the model thinks and how long the reasoning traces can get. Increasing the effort level can also increase usage costs by generating more reasoning tokens.

Longer reasoning might also lead the model to try more things and call more tools, thus creating more turns. For hard, complex problems, this is a good thing because it allows the model to complete harder tasks, but for simpler problems, this can result in costly overthinking.
Also, once output tokens enter the session context, they become the next turn's "input tokens" and can be billed as cached input tokens when the relevant prefix gets a cache hit.

![Cost per turn rises from 6K to 15.9K TC over 100 turns as cached context grows, while new input and output stay constant.](/img/posts/tokenomics/context-growth-cost.png)

*Illustrative example: a warm 15K-token prefix, 1K new input tokens and 500 output tokens per turn. After the first turn, that 1K includes the previous turn's 500-token response. No compaction or cache expiry.*

You can now see how, as context accumulates in the session, the next turn becomes more and more expensive. Therefore, achieving the goal with the least amount of context and the fewest turns is crucial for optimal usage efficiency.



## Dumb Zone
You may have noticed that as a long chat continues to accumulate context, the agent seems to become dumber and make more mistakes. It's a real phenomenon, and Matt Pocock calls it a ["Dumb Zone"](https://www.aihero.dev/why-the-anthropic-ralph-plugin-sucks). [Chroma's context-rot research](https://www.trychroma.com/research/context-rot) also documents declining reliability as input length grows.

A useful way to think about it is "dilution", or [attention degradation](https://www.aihero.dev/ai-coding-dictionary/attention-degradation): as context grows, important instructions and facts have more "noise" material to compete with. In practice, the gap between what the task requires and what the agent achieves can widen.

For Claude, I try to finish my tasks with under 300K tokens of context, with a hard autocompact limit of 500K (more on compaction later). Codex has a default "short context" window of 258K, so it's less of a problem, but if I see that the task is not getting done by the second compaction, I know that something is wrong.

The "dumb zone" becomes even more apparent when the same session includes several unrelated or only loosely related tasks.
Outdated information creates another problem, which can compound it.
For example, an agent is fixing a bug in a project and scans all the code in one file: the chat now includes that file's code in its context. If another agent (or human) changes the content of that file, the agent may keep working from the previously read version until it rechecks.
This can lead to stale assumptions and incorrect edits.
My rule of thumb is to do one "task" per chat session and to have only one active agent per "project" to avoid agents "stepping on each other's toes".



## Session "Cold Boot" Cost
When you start a new session, you can see that the context does not start at 0. Each new session includes the system prompt, AGENTS.md, auto-memory (if it is enabled), all skill names and descriptions, and MCP server configurations.
If left unchecked, that combined cost can easily reach 40-50K tokens of context, and that is BEFORE you start working on your task. In Claude, you can start a session with `/context` (or `/status` in Codex) to see what your cold boot cost is.

You can ask your agent to help you minimize that quite easily. In your first message of the session, ask it to list everything in the context and explain that you want to minimize your cold boot context. Then you can see how much "dead weight" you are carrying in every session. You will be surprised.
I got my cold boot down to 15K.

![Over 100 turns, a 15K-token startup prefix costs 178.5K TC (about $0.36) and a 45K-token prefix costs 535.5K TC (about $1.07), a difference of 357K TC (about $0.71) at Sonnet 5 API rates.](/img/posts/tokenomics/cold-boot-comparison.png)

*Startup context only: one write at 2 TC per token, then 99 cached reads at 0.1 TC. Both prefixes stay cached; task-specific input and output are excluded. At Sonnet 5 API rates, that's about $0.36 versus $1.07, saving about $0.71 over 100 turns.*



## About Compaction
One simple context-control method is to use compaction. Calling `/compact` tells your agent to summarize the conversation and reduce the context it carries forward, which sounds great.
But the catch is that generating the summary uses output tokens! It also partially breaks the cache: unchanged parts, such as the system prompt and AGENTS.md, can still be reused, but the new "AI summary" enters as a bunch of new input tokens.

In my own Codex sessions, median request input drops from 221K tokens before compaction to 22.6K on the first request afterward. The median cost of generating the summary plus that next request's input, including the cache rewrite, is roughly 80K TC using our rates above. Compaction itself usually takes around a minute.
Also, I've noticed that with every compaction, the agent drifts further and further from the initial instructions, and after a while, it just starts doing God knows what. If the task isn't done by the third compaction,
my bet is that it will never get done at all without more help from a human. The few times I let it run "to completion", it spent something like 10 hours and 13 compactions on the task, and in the end, it just gave up and provided a broken result.
Now I try to split my work into small, clearly defined tasks and do one task per session, and the results are quite good.



## TTL Cache
A cache's time to live (TTL) is how long it stays available for reuse. Claude Code's main conversation normally gets a [one-hour cache](https://code.claude.com/docs/en/prompt-caching) within included subscription usage. [OpenAI's cache lifetime](https://developers.openai.com/api/docs/guides/prompt-caching#cache-lifetime) for GPT-5.6 and later models is at least 30 minutes.
Each request that reuses the cached prefix refreshes its lifetime. The exact behavior depends on the model and setup.
While the cache is "warm", cached inputs are billed at the cached price (0.1 TC per token in our example).

Let's say you have an extremely long session with 800K tokens of context, and the cache has gone cold while you were at lunch.
Using our illustrative 2x-write model, resuming that session costs 1.6 million TC (\~$3.20) just to rewrite the existing context, compared with 80K TC (\~$0.16) to reuse it while warm.

This is why I keep the cache warm until the task is done or I'm ready to sign off and know that I won't resume it later.
If you know that you will be resuming the session after the cache has gone cold, use `/compact` before stepping away to reduce the context you'll need to reload. Better yet, wrap things up and continue in a fresh session when you're back.

The same is true for long-running agent turns. If your build pipeline (or any tool call) runs longer than the cache's TTL and the cache goes cold, the next turn will be billed for cache reinitialization again.
To avoid this, I've made a local "smart-wait" tool - a TTL-aware process-wait command that keeps the cache warm by waking the agent for a quick "boop" before the cache goes cold. It also helps with Codex yapping - I noticed that it would not shut up with "status updates" and would burn through many turns, posting every few minutes just to "keep me updated" about how the build process was going, even when I didn't care about it.

Keep-alive requests aren't completely free, obviously, but it usually takes a long time for them to cost more than the "cold cache" premium. Useful model requests during the task refresh the cache too, so the keep-alive timer only needs to cover the gaps.

![Keeping an 800K-token prefix warm costs 400K TC over a four-hour wait instead of 1.6 million TC for a cold resume. Break-even is around 17 hours and 25 minutes.](/img/posts/tokenomics/keep-alive-payoff.png)

*Illustrative costs for an already-warm 800K-token prefix: 1-hour TTL, keep-alives every 55 minutes, and every read hits. Both strategies include resuming the session; added messages, output overhead and initial warm-up are excluded. At Sonnet 5 API rates, the four-hour wait costs $0.80 with keep-alives versus $3.20 for a cold resume.*

## Preserving the Cache
Certain actions can break the cached prefix and result in re-caching costs. While working in a session, avoid:

- Changing tool definitions (adding, removing, reordering, or modifying tools, including MCP tools),
- Changing early instructions or injected context, such as AGENTS.md,
- Changing the selected model or reasoning effort*,
- Entering or exiting "fast mode",
- Entering or exiting "Cloud/remote session",
- Updating the Claude/Codex client when that changes the prompt or tools,
- Changing settings that change the rendered prompt (verbosity settings, structured-output schemas, parallel-tool-call settings).

*\* GPT-6 models can preserve the cache when effort changes, provided the client uses OpenAI's supported [configuration-update mechanism](https://developers.openai.com/api/docs/guides/reasoning#change-reasoning-mid-conversation). In Claude Code, [Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1](https://code.claude.com/docs/en/prompt-caching#changing-effort-level) also preserve it with an API key or Claude subscription in supported configurations.*

## Takeaway notes

1. One chat per task.
2. Match effort level with task complexity.
3. Keep the cache warm while the task is still in flight.
4. Trim the fat from your local setup and keep it lean (AGENTS.md, auto-memory, skills, MCP servers).
5. Be aware of context size and what's in the context.

*Written by me, edited with AI. [How I write.](/about/)*
