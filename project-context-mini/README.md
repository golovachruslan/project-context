# project-context-mini

Minimal project context for Claude Code. Four lean, Mermaid-friendly files and two skills. Companion to the full [`project-context`](../project-context) plugin.

## When to use

Use **`project-context-mini`** when you want just enough context for an AI agent to understand a project:

- what the system looks like (architecture)
- how users move through it (flows)
- what conventions and gotchas matter (patterns)
- where you are right now (status)

No session-state tracking, no brainstorming workflow, no planning pipeline, no CLAUDE.md sync — just the essentials an incoming agent needs to be useful.

Use the full [`project-context`](../project-context) plugin when you need session continuity, planning workflows, federated dependency graphs, brainstorm/challenge/implement cycles, or CLAUDE.md management.

Both plugins can live side-by-side in the same project — they write to separate directories.

## Install

This plugin is published via the same marketplace manifest as `project-context`. Once the marketplace is added in Claude Code, enable the plugin:

```
/plugin install project-context-mini
```

Then reload:

```
/reload-plugins
```

You should see `/project-context-mini:update` and `/project-context-mini:load` in the skill list.

## Files

The plugin writes to `.project-context-mini/` in your project root:

| File | Purpose | Style |
|------|---------|-------|
| `architecture.md` | Mermaid diagram + components + data model + tech stack + dependencies list | Mermaid-first |
| `flows.md` | One Mermaid diagram per key user flow, H2 per flow | Mermaid-first |
| `patterns.md` | Conventions + anti-patterns + gotchas, organized by category | Text-first (Mermaid optional) |
| `status.md` | Current focus + why + next action | Mermaid-first if useful; usually prose |

When `architecture.md`, `flows.md`, or `patterns.md` grows past a soft threshold (~75 lines), `update` will suggest a refs-split:

```
.project-context-mini/
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

`status.md` is exempt — if it grows, the fix is to recompress the focus statement, not to split the file.

## Skills

### `/project-context-mini:update`

Creates or refreshes the four files.

**Bootstrap (first run):** detects missing files, asks 5 seed questions (project goal, tech stack, core user flow, current focus, any upfront conventions/gotchas), and writes scaffolds you can approve or edit.

**Refresh (subsequent runs):** runs two subagents:

1. **`content-extractor`** — scans the current conversation + recent `git diff` for signals worth capturing. Over-generates deliberately.
2. **`update-critic`** — ruthlessly filters the candidates. Its default stance is rejection. It enforces a hard cap of 3 items per file and zero redundancy with existing content.

You see only the filtered set, with the critic's rejection reasons for anything cut, and you approve per-item before writes happen.

Flags: `--chat` / `--scan` / `--input` to pick the source explicitly, `--bootstrap` / `--refresh` to force a mode.

### `/project-context-mini:load`

Reads all four files in full, inline into the session. No digest, no pointer list — the files are small enough that "full load" is the correct strategy. Emits sections in the order `status → architecture → flows → patterns` with Mermaid diagrams preserved verbatim.

Also reads any `<file>/refs/*.md` you've split out.

Run it at the start of a session to prime the agent.

## Agents

Both agents are for the `update` skill's refresh mode:

- **`content-extractor`** — scans for signals (architecture shifts, flow changes, new patterns, gotchas, status pivots) across conversation + git. Returns ranked candidates as JSON.
- **`update-critic`** — applies a 7-rule hard filter (new-teammate test, not-a-framework-default, not-already-captured, generalizes-beyond-one-instance, prefer-rewriting-to-adding, Mermaid-first respected, patterns categorized). Returns kept set + rejection reasons.

No agents are involved in `load` — reading four small files is cheap in the main session.

## Coexistence with the full plugin

| | `project-context` | `project-context-mini` |
|---|---|---|
| Context directory | `.project-context/` | `.project-context-mini/` |
| Files | brief, architecture, patterns, state, progress, dependencies, plans/ | architecture, flows, patterns, status |
| Skills | 14 (brainstorm, plan, implement, update, load, challenge, resume, save, next, optimize, init, ask, project-context, add-dependency) | 2 (update, load) |
| Agents | 7 | 2 |
| CLAUDE.md sync | yes | no |
| Hooks | optional | none |

They don't interfere. Install both if you want full workflow on one project and lean context on another.

## License

MIT. See [LICENSE](./LICENSE).
