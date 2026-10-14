# Packet agentik-r1-profile: the org profile page names the `agentik` surface

| item | value |
|---|---|
| from | agentik-commons `design/agentik-r1.md` §3, §4.1, §4.3, §5.1–§5.2, §6.1, §6.2 (this repo's row), §8.1–§8.2, §9 (A9), §10 (D2 D4); step 0 landed in the owner's ledger (2026-10-13). The builder reads THIS packet, those sections and §5; nothing else |
| pin | `main` at `6476f3a` or later; agentik-commons `main` after agentik-r1-commons merges; branch and worktree `agentik-r1-profile`, off main; a hand-run builder |
| wall | this repo only, and it is public: no private host, person, path or machine fact in any file. agentik-commons read-only (its `scripts/sync` writes here). No push, `--amend`, rebase or network; no `claude` command. Never write in `~/.local/state` or `~/.config`, read a transcript, or build or run a relay binary or verb |
| may touch | `profile/README.md`, `Makefile` (new), `.gitignore` (new), `.hygiene-allow` (new), `scripts/{agentik,hygiene,bounded,vendored.sha256}` by sync only; under `design/`, only this packet's §6 report. Nothing under `assets/` or `tools/` |
| acceptance | `grep -c 'marketplace add' profile/README.md` reads `1`; `grep -c 'claude plugin install [a-z]*@agentik$' profile/README.md` reads `5`; `test -f .hygiene-allow; echo $?` reads `0` |
| budget | 40 turns, 80k context; commit per act; checkpoint at 80% |
| verify | `make check` |

## 1. What the source says

- **§3, §4.1.** One front door, `agentik <tool> args…`, runs `agentik-<tool>` from PATH; the tools are `agentik-session`, `agentik-relay`, `agentik-agents` and the ledger tool, each installed by `make install` from a clone, which also installs `agentik` (D3). D4: one plugin has no command in r1. The old command names stay as aliases until 2026-12-31 (§4.3), and the page does not teach them.
- **§4.3.** Printed lines read `agentik relay resume <row>` and `agentik session run --chain <name>`.
- **§5.1–§5.2, D2.** Every plugin installs from one marketplace, `agentik`, in agentik-commons: `claude plugin marketplace add agentik-dev/agentik-commons`, then `<p>@agentik` for each of the five; relay's plugin is `relay` (`/relay:status`, `relay:builder`), agents' is `agents` (`/agents:status`). No per-repo marketplace remains.
- **§6.2, this row.** (b) `profile/README.md`, the only live file with an old name. **A9:** commons is the tools' shared ground and builds no tool.
- **§8.2.** The scope is the org profile README; the test that fails before: `renamed` counts 0. Every packet vendors `scripts/{agentik,hygiene,bounded}` by commons' `scripts/sync` and has `renamed` 0 as an acceptance line; this repo has no `marketplace.json` to delete.

**Live hits today** (lines per file). Clear 1: `profile/README.md` 13 (the session, ledger, relay, plugin and agents install lines; the old CLI names in three `doctor` lines, the resume line and the key line; the old plugin name `agent-relay`). Allow 0.

## 2. Rulings (decided inside the record, one sentence each)

1. A new `Makefile` holds one target, `check`: `shasum -a 256 -c --status scripts/vendored.sha256`, then `scripts/hygiene`; no `install`, since the repo builds nothing.
2. A new `.hygiene-allow` holds `profile/README.md: sibling` and `design/packets/*.md: sibling`, each with its reason (the page and its packets name the five public tools), and `scripts/hygiene: renamed` only if the vendored copy hits its own patterns (§6.1); no other `renamed` row.
3. A new `.gitignore` ignores `.DS_Store`, so the tree reads clean.
4. The page gains an `agentik-commons` entry ahead of the five (the marketplace, the front door, the guide; it builds no tool), and its install block runs `claude plugin marketplace add agentik-dev/agentik-commons` once.
5. Each tool's block keeps `make install` from a clone and one `claude plugin install <p>@agentik` line; the relay block uses `make install`, so the page does not depend on relay's `cmd/` path.
6. Each tool with a command closes its section with `agentik <tool> doctor`; the relay text reads `agentik relay resume <row>`; the agents key line reads `agentik agents setup-key`.
7. Executables are named `agentik-<tool>` in prose and plugins by their plugin names; the table "How they fit" keeps its rows, its first column the five plugin names.
8. The page stays one file under the size it has today plus the commons entry; the push waits until the tool packets and the commons marketplace are public, which is the owner's call, not this packet's.

Any further fork: decide inside the record; log it in §6.

## 3. Interfaces

| item | contract |
|---|---|
| `make check` | ruling 1; exit 0 clean, non-zero on a drifted copy or a hit outside `.hygiene-allow` |
| `profile/README.md` | rulings 4–7; links stay `https://github.com/agentik-dev/<repo>` |

## 4. Findings that name this row

None. The table below is the whole acceptance (the header row holds its read-only subset; `verify` is the gate line). Run in the worktree after the last commit.

| # | line | reads |
|---|---|---|
| 1 | `make check >/dev/null 2>&1; echo $?` | `0` |
| 2 | `scripts/hygiene --json \| python3 -c 'import json,sys;print(sum(f["group"]=="renamed" for f in json.load(sys.stdin)["files"]))'` | `0` |
| 3 | `grep -c 'claude plugin marketplace add agentik-dev/agentik-commons$' profile/README.md; grep -c 'marketplace add' profile/README.md` | `1`, `1` |
| 4 | `grep -c 'claude plugin install [a-z]*@agentik$' profile/README.md` | `5` |
| 5 | `grep -cE 'agentik [a-z]+ doctor' profile/README.md` | `4` |
| 6 | `grep -c 'agentik relay resume <row>' profile/README.md` | `1` |
| 7 | `shasum -a 256 -c scripts/vendored.sha256 \| grep -c ': OK$'` | `3` |
| 8 | `C="$(git rev-parse --path-format=absolute --git-common-dir)/../../agentik-commons"; cmp -s scripts/hygiene "$C/scripts/hygiene" && cmp -s scripts/agentik "$C/bin/agentik" && echo same` | `same` |
| 9 | `test -e .claude-plugin/marketplace.json; echo $?` | `1` |
| 10 | `git status --short \| wc -l` | `0` |

Fails before: line 2 (no `scripts/hygiene`; 13 old-name lines in `profile/README.md` today), and lines 1, 3–8.

## 5. Forbidden reads

Read-only outside this repo: `$C` (line 8): `design/agentik-r1.md` (the sections in `from`), `GUIDE.md`; run `"$C/scripts/sync" .` once. Each tool's README is not read: the record names every line the page needs.

Forbidden: transcripts, `~/.local/state`, `~/.config` (hygiene reads its private list; never print it), the owner's ledger, other repos.

## 6. Report (under 1,500 words)

Each acceptance line's output; the commits; each ruling beyond §2; anything left open.

### 6.1 Charter (the builder's, kept current at each commit)

The may-touch row allows only this §6 under `design/` and no `history/` path, so the charter lives here.

- **Goal.** The org profile page names the `agentik` surface: one marketplace, `agentik <tool>`, the new plugin names; `renamed` counts 0.
- **Budget.** 60 turns, 80k context (the caller's word, over the header's 40); checkpoint at 80%.
- **Pin.** Branch `agentik-r1-profile` off `main` at `c9e6a4a`; agentik-commons `main` at `e456f4b`.
- **Acts.**
  1. Vendor `scripts/{agentik,hygiene,bounded,vendored.sha256}` by `$C/scripts/sync .`; add `Makefile`, `.gitignore`, `.hygiene-allow` (rulings 1–3). Done: `make check` runs, red only on the page's 13 `renamed` lines.
  2. Rewrite `profile/README.md` (rulings 4–8). Done: one marketplace line, five `@agentik` installs, four `agentik <tool> doctor` lines, `renamed` 0; the page outside the commons entry is 5,821 bytes against 5,827 before.
  3. Run the acceptance lines and `scripts/hygiene --require-private`; fill §6.2. Pending.
- **Handover.** None yet.
- **Exit.** Open.
