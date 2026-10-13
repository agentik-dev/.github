<p align="center"><img src="https://raw.githubusercontent.com/agentik-dev/.github/main/assets/agentik-dark-1024.png" width="112" alt="agentik: a pixel-art agent with a visor"></p>

<h1 align="center">agentik</h1>

<p align="center">Guardrails for long, unattended Claude Code work.</p>

agentik is five Claude Code plugins, with their command line tools, for agent work that runs for hours with nobody watching.
They give each session a budget and a hard stop, and they merge overnight work only when its checks pass.
You read one report in the morning, and every stopped session leaves a way back in.

## A short tour

You write each task as a packet: a short file that says what to build and how to check it.
relay works through a queue of packets overnight.
Each packet gets its own branch, its own copy of the repo and its own Claude Code session.
A branch merges only when its checks pass, and nothing is pushed.

session watches each of those sessions.
It counts context and turns, warns at 80%, and at 100% tells the session to finish its current step and exit.
Before it exits, the session brings a short charter up to date: what it was for, how it ended, what comes next.
A fresh session starts from that charter, so long work continues without compacting the old context.

decisions keeps what a project has already settled in one file, `DECISIONS.md`.
It copies the few rules every session needs into `CLAUDE.md`.
Agents may draft questions, but only you settle them.

respeak lets agents write to each other in short, agreed shorthand, and writes a version for you in one of three modes: `eli5`, `bluf` or `technical`.
Everything it writes for people passes a check against a list of banned phrases.

agents runs side work, such as a read-only code review, outside your interactive session.
It bills that work to an Anthropic API key, or runs it on a local model, and reports what it cost.

## The five repos

### [agentik-session](https://github.com/agentik-dev/agentik-session)

A plugin and a `claude-session` tool that give each Claude Code session a profile, a budget with a hard stop, and a written charter.
Use it so a session winds down at a known point and leaves a record you can read.

```sh
claude plugin marketplace add agentik-dev/agentik-session
claude plugin install session@claude-code-session
make install    # from a clone: the claude-session CLI, Python 3.11 or newer
```

Then run `claude-session doctor` to check the setup.

### [agentik-relay](https://github.com/agentik-dev/agentik-relay)

A Go binary, `relay`, and a plugin, `agent-relay`, that run a queue of packets overnight with no one at the keyboard.
Each queue row merges into `main` only when its gate passes, and `relay resume <row>` reopens any row that stopped.

```sh
claude plugin marketplace add agentik-dev/agentik-relay
claude plugin install agent-relay@agent-relay
go install github.com/agentik-dev/agentik-relay/cmd/relay@latest
```

Then run `relay doctor` to check the machine for a night.

### [agentik-decisions](https://github.com/agentik-dev/agentik-decisions)

A plugin and a `decisions` tool that keep a repository's settled decisions in one short `DECISIONS.md`.
Use it so every session finds the rules it must follow without reading a long file whole.

```sh
uv tool install .    # from a clone: the decisions tool
claude plugin marketplace add agentik-dev/agentik-decisions
claude plugin install decisions@claude-code-decisions
```

Then run `decisions doctor` to check the setup.

### [agentik-respeak](https://github.com/agentik-dev/agentik-respeak)

A plugin where agents write to each other in ratified shorthand and each person reads a narrative written for them.
Use it to read your agents' work in `eli5`, `bluf` or `technical` mode without learning their dialect.

```sh
claude plugin marketplace add agentik-dev/agentik-respeak
claude plugin install respeak@claude-code-respeak
```

It needs Claude Code 2.1.196 or newer and a python3 with PyYAML.
Translation works at once; run `/respeak:init` once per project to set up the lexicon and the style gate.

### [agentik-agents](https://github.com/agentik-dev/agentik-agents)

Tools and a plugin that run delegated Claude Code work on an Anthropic API key or a local model.
Use it to fan out read-only reviews under one hard dollar cap and see what each lane cost.

```sh
git clone https://github.com/agentik-dev/agentik-agents.git
cd agentik-agents && make install                    # links the tools into ~/.local/bin
claude plugin marketplace add agentik-dev/agentik-agents
claude plugin install claude-code-agents@claude-code-agents
```

The API lane needs a key, which `claude-api-agent --setup-key` stores encrypted with sops and age; the local lane needs none.

## How they fit

| Plugin | Its job | With the others |
|---|---|---|
| session | A budget, a hard stop and a charter for each session | Writes one resolved configuration that relay, decisions and respeak read |
| relay | An overnight queue, one branch per packet, a gated merge | Starts each packet as a `builder` session; renders its morning report through respeak |
| decisions | One ledger of settled decisions | Renders its open questions through respeak |
| respeak | Shorthand for agents, plain reading for people | Takes the session's tone from session |
| agents | Delegated work on an API key or a local model, with costs | Its status view lists the sessions that session tracks |

Each one installs and works alone; a link in the last column turns on when the other plugin is installed.

## Status

agentik is early and built for the author's own daily use, so expect breaking changes between versions.
Issues are welcome on each repo, and each repo is MIT-licensed.

agentik is unofficial and not affiliated with Anthropic.
Claude and Claude Code are Anthropic's products.
