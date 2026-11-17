# Why a ceiling below the window

Every agentik sitting stops well below its model's window: at a ceiling of 180k tokens on most roles, or 400k for an orchestrator on a 1M window, with a checkpoint at 80% of that.
At the end of this page you will know which reasons for this rest on outside evidence, which are the makers' own choice, and what 1,867 measured sittings show.

## Two ceilings, two windows

The model decides the window. The role decides the ceiling inside it.
Every role gets 180,000 tokens and 400 turns, on a 200k window and on a 1M window alike.
Only the two orchestrator roles get more: 400,000 tokens, and only on a 1M window.
A helper, the subagent a sitting starts, resolves as a builder, with 180,000 tokens unless a user or project layer sets its own ceilings.

![Three bars drawn to scale: a 180k ceiling inside a 200k window, a 180k ceiling inside a 1M window, and a 400k ceiling inside a 1M window, with a dashed mark where Claude Code compacts near 967k. Below, a bar of zones from 0 to 100% of a ceiling, and a table of each zone's token figure for both ceilings.](figures/ceilings.svg)

*The two ceilings to scale inside their windows, and the zones the meter reads as a share of either ceiling.*

On a 1M window, Claude Code compacts the conversation on its own near 967k tokens.
A sitting that keeps to its ceiling never comes near that point.

## Why stop below the window

Four reasons. The first three rest on outside evidence; the fourth is the makers' design.

1. **A long context does worse.** Studies find that accuracy falls as the input grows, even when the fact the model needs is in the window. One found falls of 13.9 to 85 percent with perfect retrieval. Anthropic's documentation names the effect *context rot*. No study measures a Claude 5.x model inside a Claude Code session as it fills. See [Length and compaction, question 1](https://agentik-dev.github.io/agentik-research/field/length-and-compaction/#question-1-what-changes-as-context-grows).
2. **A summary drops the specifics.** Compaction keeps the gist and loses exact values. In one run of Anthropic's cookbook, a compaction kept 3 of 3 high-level facts and lost 3 of 3 obscure values. In a vendor's test of three compressors, the record of which files were touched scored lowest for all three, 2.19 to 2.45 out of 5. So agentik restarts from a written charter instead of compacting. No controlled study compares the two in a coding session. See [Length and compaction, question 2](https://agentik-dev.github.io/agentik-research/field/length-and-compaction/#question-2-compaction-or-restart).
3. **Every turn pays for the whole context.** Each turn resends the whole conversation, so a turn costs more as the context grows, and it draws more from your usage limits. A sitting held to 400k never pays for a turn at 600k or 900k. The prices are documented; the arithmetic is the research site's. See [the cost model](https://agentik-dev.github.io/agentik-research/field/budgets-and-lanes/#the-cost-model).
4. **The handoff needs room.** The makers' own reason, from the budget module of agentik-session: a session that runs to 100% "dies mid-thought". It has no budget left to write down what it was doing, commit, or hand off. So the ceiling sits below the window, and the checkpoint sits below the ceiling.

Helpers get a ceiling for the same reasons.
Their context grows the same way, and their requests count toward the same usage limits as the main conversation.

The figures themselves, 180,000 and 400,000 tokens and 400 turns, are the makers' rulings, not measurements.
The research site says so: [the repo gives no derivation for them](https://agentik-dev.github.io/agentik-research/tools/session/#the-parts).

## Why the checkpoint is at 80%

The 80% checkpoint is the makers' rule, not a finding; the research site marks it as their own use and a conjecture ([Practices, budgets and pacing](https://agentik-dev.github.io/agentik-research/practices/#budgets-and-pacing-question-4)).

The code says what the rest of the ceiling is for.
The budget module holds back a reserve for the wrap-up and sets its marks below it:

- **notice, from 80%**: the first warning. The meter prints `CHECKPOINT:` at the first crossing, then on every tenth tool call.
- **wind-down, from 90%**: stop starting things you cannot finish.
- **reserve, from 92%**: the last 8% is held back for the wrap-up.
- **exhausted, at 100%**: the meter prints `EXIT:` on every tool call.

At 80%, an orchestrator still has 80,000 tokens of its ceiling left, and a builder 36,000.
That is the room for bringing the charter up to date, committing and closing.

## What the record shows

The makers' own sittings since 2026-09-24, cut to numbers only, give each sitting's peak context as a share of its ceiling.

![Two histograms of peak context per sitting. The orchestrator panel, 1,107 sittings, peaks sharply in the 70 and 80 buckets, with 54 sittings that reached or passed the ceiling. The panel for every other role, 760 sittings, is wider, with 151 that reached or passed the ceiling and 48 at 150% or more.](figures/peak-context.svg)

*Peak context per sitting, as a share of its ceiling, with the checkpoint and the ceiling marked; from [the data](data/sittings_hist.csv).*

- **Orchestrators.** The median sitting peaks at 79.5% of its ceiling. 672 of 1,107 peak within ten points of the checkpoint, between 70% and 90%. 54 (4.9%) reach or pass the ceiling.
- **Every other role.** The median is 80.0%, but the 90th percentile is 127%. 151 of 760 (19.9%) reach or pass the ceiling, and 48 reach 150% or more.

The ceiling is a signal.
The meter speaks; it does not end the sitting, so a sitting can run on past it.
A 1M window leaves room for that: 150% of a 180k ceiling is 270k tokens, far below the window.
The record does not say which sittings ran on, or why.

## Read more

- [Length and compaction](https://agentik-dev.github.io/agentik-research/field/length-and-compaction/): the studies on length, compaction and restarts, with their limits.
- [Budgets, pacing and cost lanes](https://agentik-dev.github.io/agentik-research/field/budgets-and-lanes/#question-4-budgets-and-pacing): usage limits, the prompt cache and the cost of a turn.
- [Restart, don't compact](https://agentik-dev.github.io/agentik-research/journal/2026/10/05/restart-dont-compact/): the journal entry on the choice to restart.
- [agentik-session, Profiles and Budget](https://github.com/agentik-dev/agentik-session#profiles): the ceilings, the zones and the lines, as the tool documents them.
- Next: [Reading the band](the-band.md), or back to [the overview](README.md).
