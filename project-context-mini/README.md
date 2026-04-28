# project-context-mini

Minimal project context for Claude Code. Four lean, Mermaid-friendly files and two skills. Companion to the full [`project-context`](../project-context) plugin — pick one per project, not both.

## When to use

Use **`project-context-mini`** when you want just enough context for an AI agent to discuss a project:

- what the system looks like (architecture)
- how users move through it (flows)
- what conventions and gotchas matter (patterns)
- where you are right now (status)

No session-state tracking, no brainstorming workflow, no planning pipeline, no CLAUDE.md sync — just the essentials an incoming agent needs to be useful.

Use the full [`project-context`](../project-context) plugin when you need session continuity, planning workflows, federated dependency graphs, brainstorm/challenge/implement cycles, or CLAUDE.md management.

> **Important:** Both plugins write to `.project-context/`. They will overwrite each other's `architecture.md` and `patterns.md`. **Use one or the other per project.**

## Install

> **Status:** This plugin is published from the same repo as `project-context`. Until it's pushed to a public marketplace, install it from the local marketplace manifest in this repo (`.claude-plugin/marketplace.json`).

Once published, installation will be:

```
/plugin install project-context-mini
/reload-plugins
```

You should then see `/project-context-mini:update` and `/project-context-mini:discuss` in the skill list.

## Files

The plugin writes to `.project-context/` in your project root:

| File | Purpose | Style |
|------|---------|-------|
| `architecture.md` | Mermaid diagram + components + data model + tech stack + dependencies list | Mermaid-first |
| `flows.md` | One Mermaid diagram per key user flow, H2 per flow | Mermaid-first |
| `patterns.md` | Conventions + anti-patterns + gotchas, organized by category | Text-first (Mermaid optional) |
| `status.md` | Current focus + why + next action | Mermaid-first if useful; usually prose |

When `architecture.md`, `flows.md`, or `patterns.md` grows past a soft threshold (~75 lines), `update` will suggest a refs-split:

```
.project-context/
├── architecture.md              ← keeps the overview + pointers
├── architecture/refs/
│   ├── data-model.md
│   └── deployment.md
├── flows.md
├── flows/refs/
│   └── onboarding.md
├── patterns.md
└── patterns/refs/
    └── error-handling.md
```

`discuss` reads only the four main files. Refs are listed by path and read on demand by the agent — see below.

`status.md` is exempt from refs-split — if it grows, the fix is to recompress the focus statement, not to split the file.

## Skills

### `/project-context-mini:update`

Creates or refreshes the four files.

**Bootstrap (first run):** detects missing files, asks 5 seed questions (project goal, tech stack, core user flow, current focus, any upfront conventions/gotchas), and writes scaffolds you can approve or edit.

**Refresh (subsequent runs):** runs two subagents:

1. **`content-extractor`** — scans the current conversation + recent `git diff` for signals worth capturing. Over-generates deliberately.
2. **`update-critic`** — ruthlessly filters the candidates. Its default stance is rejection. It enforces a hard cap of 3 items per file and zero redundancy with existing content.

You see only the filtered set, with the critic's rejection reasons for anything cut, and you approve per-item before writes happen.

Flags: `--chat` / `--scan` / `--input` to pick the source explicitly, `--bootstrap` / `--refresh` to force a mode.

### `/project-context-mini:discuss [topic]`

Primes the agent for a discussion of the project.

- Reads all four main files in full, inline into the session.
- Lists any `<file>/refs/*.md` paths it discovers, but does **not** read their contents — refs are lazy. The agent reads a specific ref via the Read tool when the conversation calls for that detail.
- Optional `topic` argument (free-form) shapes the closing framing line. It does not filter which main files are loaded.

Examples:

```
/project-context-mini:discuss
/project-context-mini:discuss architecture
/project-context-mini:discuss "auth gotchas"
```

Run it at the start of a session, or whenever you want to focus the agent on a specific area.

## Agents

Both agents are for the `update` skill's refresh mode:

- **`content-extractor`** — scans for signals (architecture shifts, flow changes, new patterns, gotchas, status pivots) across conversation + git. Returns ranked candidates as JSON.
- **`update-critic`** — applies a 7-rule hard filter (new-teammate test, not-a-framework-default, not-already-captured, generalizes-beyond-one-instance, prefer-rewriting-to-adding, Mermaid-first respected, patterns categorized). Returns kept set + rejection reasons.

No agents are involved in `discuss` — reading four small files is cheap in the main session.

## Coexistence with the full plugin

| | `project-context` | `project-context-mini` |
|---|---|---|
| Context directory | `.project-context/` | `.project-context/` (same!) |
| Files | brief, architecture, patterns, state, progress, dependencies, plans/ | architecture, flows, patterns, status |
| Overlapping filenames | `architecture.md`, `patterns.md` | `architecture.md`, `patterns.md` |
| Skills | 14 (brainstorm, plan, implement, update, load, challenge, resume, save, next, optimize, init, ask, project-context, add-dependency) | 2 (update, discuss) |
| Agents | 7 | 2 |
| CLAUDE.md sync | yes | no |
| Hooks | optional | none |

**They collide on `architecture.md` and `patterns.md`.** Pick one plugin per project. If you start with mini and outgrow it, run `project-context:init` and re-author from the existing files. If you start with the full plugin and want to slim down, the four mini files are subsets of what the full plugin already produces.

## License

MIT. See [LICENSE](./LICENSE).
