# Packet cw1-context-primers: five primers, with figures, on how agentik manages a context window

| item | value |
|---|---|
| from | the owner's ask of 2026-11-16 (quoted in §1); the sources in §1; rulings R1 to R9 (§2) |
| pin | `main` at `d6526b7`; agentik-session `main` at `6ce9266` (plugin 2.0.0-alpha.128); agentik-research `main` at `b6f2a14`; branch and worktree `cw1-context-primers`, off main; a hand-run builder |
| wall | this repo only, and it is public: no private host, person, path, account or private repo's name in any file or commit message. agentik-session and agentik-research are read only. No push, `--amend`, rebase or merge; no `claude` process and no subagent. No read of live state under `~/.local/state`; no write under the live home |
| may touch | `profile/context/` (new: five pages, `figures/*.svg`, `data/*.csv`), `tools/context_figures.py` (new), `profile/README.md` (one line, R6), `.hygiene-allow` (one line at most, R8), `Makefile` (one step at most, R8), this packet |
| acceptance | `ls profile/context/*.md \| wc -l` reads `5` (pin: `0`); `ls profile/context/figures/*.svg \| wc -l` reads `10` (pin: `0`; `11` at the first build); `head -1 profile/context/data/usage_readings_nov.csv` reads `hours_since_first_reading,seven_day_pct` and no row passes hour 25 (fix of review 1); `ls profile/context/data/*.csv \| wc -l` reads `4` (`6` at the first build), and `sittings_summary.csv` names its two counts `sittings_peaking_70_to_90` and `sittings_peaking_at_or_over_100`, which the script checks against the histogram (fix of review 1); `grep -c 'profile/context/README.md' profile/README.md` reads `1` (pin: `0`); `tools/context_figures.py` twice, then `git status --porcelain` is empty; `make check` green; `scripts/hygiene --require-private --commits main..HEAD` exits 0 (pin: the tree scan exits 0) |
| budget | one sitting; a commit per page with its figures |
| verify | `make check` |

## 1. What the source says

The owner's words (2026-11-16): "please create some diagrams and primers as high quality documents on the agentik-dev landing page for how we manage our context window effectively. You can create screenshots of the session banner customizations we've done to show how we use it, how the respawner/launcher works, etc. Point to research we've done on WHY we limit our windows on both orchestrators and workers and why we do 80% of those windows. Show how this smooths out our usage a bit and how it avoids losing work close to the end of a 5 hour or weekly limit."

The makers' rule on public repos: commit no hostname, address, email, person's name, account detail, or private repo's name or path; examples use made-up names.

Sources, all public:
- agentik-session: `README.md` (Profiles, Budget, Priority and pacing, The charter), `plugin/lib/claude_session/profiles.yaml`, `design/window-r1.md`, `design/respawn-r1.md`, `design/admission-r1.md`, `design/mod-r1.md`, `RUNBOOK.md`, and the code that writes the band, the meter line, the usage line, `CHECKPOINT:` and `EXIT:` (`hooks.py`, `mod.py`, `admission.py`, `rules.py`, `budget.py`, `chain.py`, `plugin/hooks/session.ts`).
- agentik-research (served at `https://agentik-dev.github.io/agentik-research/`): `docs/field/length-and-compaction.md` (questions 1 and 2), `docs/field/budgets-and-lanes.md` (question 4), `docs/tools/session.md`, `docs/practices.md`, and two journal posts, of 2026-10-05 and 2026-10-14. A page's address follows `mkdocs.yml`: `site_url`, directory URLs, and the journal's `post_url_format: "{date}/{slug}"`.
- The data: a cut of the makers' own session ledger, numbers only, already prepared for publishing: peak context per sitting as a share of its ceiling (1,867 sittings since 2026-09-24, in two groups: the orchestrator roles' 400k ceiling and every other role's 180k), the launcher's restarts a day, and one seven-day usage reading over 25 hours of November 2026.

## 2. Rulings

1. **The pages.** In `profile/context/`, each 3 to 9 KB, each read in under five minutes by someone who knows Claude Code and not agentik. Each opens with two sentences on what the reader will know at the end, and ends with "Read more" links. `README.md` (the rule in five lines, one lifecycle figure, one table of the numbers, the four pages); `why-a-ceiling.md`; `the-band.md`; `respawn.md`; `usage-windows.md`.
2. **Truth.** Every number and every "why" has a source. A "why" that rests on evidence links to the research page that holds it; one that is the makers' own choice says so. What only advises (the spawn gate's default posture, admission's mode) is said to advise. The ceiling is a signal, and the data shows sittings over it, with the count. No before-and-after claim for usage: no controlled comparison exists, and `usage-windows.md` says so.
3. **The figures.** All SVG in `profile/context/figures/`, none a Mermaid block, each written by `tools/context_figures.py` (stdlib only, `#!/usr/bin/python3`) from the CSVs and constants named at its top; a second run changes no byte. At least: the lifecycle; the two ceilings in their windows with the zones at 80, 90, 92 and 100; the histogram of peak context per sitting for both groups with the 80% line; the launcher's sequence; restarts a day; the November seven-day reading, alone, with no word on where it went after the record ends; one drawing of admission's mechanism, captioned as a drawing.
4. **The band's pictures** are SVG terminal figures whose text is the plugin's own output, captured from agentik-session's code in a temp HOME against made-up fixtures (never the live home, never a `claude` process). Each caption says "drawn from the plugin's output at <version>". Each element is numbered and explained under the figure. No bitmap.
5. **Every SVG** reads on GitHub's light and dark themes (its own background and a `prefers-color-scheme` rule inside it), is 760 px wide by its viewBox, uses text of 12 px or more in a system font stack, and has `<title>` and `<desc>`. The markdown gives each an alt text and a one-line caption.
6. **The landing page.** `profile/README.md` gains one short line linking the primers by absolute address, near where it speaks of the session tool; nothing else there changes. Links among the five pages and to figures are relative.
7. **Voice.** Plain English, short sentences, present tense, second person where it instructs. Unattended work is called unattended, never by a time of day. No hype word; a term is defined at first use.
8. **Hygiene and make.** `.hygiene-allow` may gain exactly `profile/context/*.md: sibling` if the scan asks. A `make` step only where the check has a natural place to rerun the figure script and compare.
9. **Order.** The data and the script with the measured figures; `README.md`; `why-a-ceiling.md`; `the-band.md`; `respawn.md`; `usage-windows.md`; the landing line. One commit per page with its figures.

## 3. Interfaces

- `tools/context_figures.py [--check]`: with no flag it writes every figure under `profile/context/figures/` from `profile/context/data/*.csv` and its own constants; `--check` writes nothing, exits 1 naming each figure whose bytes differ from what it would write, else 0. In both modes it also exits 1 naming any SVG in the folder that it no longer writes, so a dropped figure cannot stay behind (fix of review 1). Its output depends on no clock, locale or environment.
- The band's text in the terminal figures is fixed in the script's constants, captured once from agentik-session at the pin's plugin version. A later plugin version that changes the band changes nothing here until someone recaptures.
- `make check` gains one step, `tools/context_figures.py --check`, after the vendored sums and before the hygiene scan.

## 4. Findings that name this row

None in this repo's records.

## 5. Forbidden reads

Transcripts; anything under `~/.local/state` or `~/.claude/projects`; any private repository.

## 6. Report

The record of the build: each acceptance line's result, the gate's job and result, the capture command, a facts table (each number in the pages, its value and its source), each figure rendered and looked at.
