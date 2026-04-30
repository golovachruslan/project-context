# Architecture

**Type:** Pure markdown Claude Code plugin

## Structure

```
.claude-plugin/plugin.json   # Plugin manifest (v2.8.0)
commands/                    # 9 slash command definitions (.md files)
skills/                      # 10 skill directories (SKILL.md + references)
agents/                      # 6 agent definitions (.md files)
scripts/
  manage_context.py          # Python context utility
  fetch_git_deps.py          # Git sparse-checkout utility
```

## How It Works

The plugin manifest (`plugin.json`) declares commands, skills, and agents. Claude Code loads these at session start. No compiled code — all behavior is defined in markdown files that Claude reads and executes as instructions.

## Sibling plugin (built)

`project-context-mini/` lives alongside the main plugin in this repo and ships as a second marketplace entry. It provides a leaner four-file context model (architecture, flows, patterns, status) with only two skills (`update`, `discuss`) and two agents (`content-extractor`, `update-critic`). Pure markdown, no scripts, no hooks. Target user projects write to `.project-context/` — same directory as the parent plugin, so the two are mutually exclusive per project.

### Sibling structure

```
project-context-mini/
├── .claude-plugin/plugin.json   # v0.2.0
├── skills/
│   ├── update/SKILL.md + references/file-scaffolds.md
│   └── discuss/SKILL.md
├── agents/
│   ├── content-extractor/agent.md
│   └── update-critic/agent.md
├── README.md
└── LICENSE
```

Declared in `.claude-plugin/marketplace.json` as the second entry in the `plugins` array.

## Key Decisions

- **2026-04-21** — Adopted a sibling-plugin pattern (new directory + second entry in `marketplace.json`) rather than adding a `--mini` mode to the existing plugin. Keeps the parent unchanged and lets users install only what they need.
- **2026-04-21** — Mini plugin uses two agents (`content-extractor` + `update-critic`) for its `update` skill — the critic pass is what enforces "ruthless quality filtering" without relying on main-context self-policing.
- **2026-04-27** — Mini writes to `.project-context/` (same dir as parent), reversing the v1 separate-dir decision. Trade-off accepted: the two plugins collide on `architecture.md` and `patterns.md`, so users pick one per project. Reduces friction for mini-only users who expect the standard location.
- **2026-04-27** — Renamed `load` skill to `discuss` and added an optional topic argument. Signals intent (priming for a discussion) and the topic shapes the closing framing prompt.
- **2026-04-27** — `discuss` lazy-loads refs: reads the four main files in full, lists `<file>/refs/*.md` paths only, and lets the agent read a specific ref on demand. Prevents context bloat as refs accumulate.
