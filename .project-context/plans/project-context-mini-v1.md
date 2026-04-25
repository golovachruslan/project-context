# Plan: `project-context-mini` plugin — v1

**Created:** 2026-04-21
**Status:** Phases 1-7 Completed (2026-04-21); Phase 8 (manual smoke test) pending user-driven `/reload-plugins` + interactive verification.

## Goal

Ship a sibling plugin that gives an AI agent just enough context to understand a project: architecture (with deps), user flows, patterns/gotchas, current status. Four Mermaid-first (or Mermaid-friendly) files, two skills, two agents, no commands, no hooks.

## Success Criteria

1. Plugin installs from `marketplace.json` and Claude Code discovers both skills.
2. Running `/project-context-mini:update` on a project with no context creates the four files with sensible scaffolds + at least one Mermaid diagram in architecture/flows/status.
3. Running `/project-context-mini:update` on a project with existing files extracts knowledge via the two subagents, presents a ruthlessly-filtered candidate list, and writes only confirmed items.
4. Running `/project-context-mini:load` reads all four files inline and surfaces their Mermaid diagrams to the agent.
5. The refs-split suggestion fires when any of `architecture.md` / `flows.md` / `patterns.md` grows beyond a soft threshold.
6. Total plugin size: ≤ ~10 files of authored markdown (plugin.json, 2 SKILL.md, 2 agent.md, README.md, LICENSE, plus at most one `references/` file per skill).

## Locked Decisions (from brainstorm)

1. **Four artifact files:** `architecture.md`, `flows.md`, `patterns.md`, `status.md`. No `brief.md`, no `progress.md`, no federated `dependencies.json`.
2. **Mermaid-first for architecture/flows/status**; optional/as-needed for `patterns.md` (text-first is fine).
3. **`architecture.md`** — diagrams + components + data model + tech stack + simple inline dependency list.
4. **`flows.md`** — one mermaid diagram per key user flow (H2 sections).
5. **`patterns.md`** — conventions + anti-patterns + gotchas, organized by category. Mermaid only when it genuinely helps (e.g., decision tree).
6. **`status.md`** — current state essentials only; no history log.
7. **Refs-split pattern** — if `architecture.md` / `flows.md` / `patterns.md` grows, split per section into `<file>/refs/<name>.md`, leave pointer in main file.
8. **Two skills only:** `project-context-mini:update`, `project-context-mini:load`.
9. **`update` doubles as init** — detects missing files and creates them on first run.
10. **`update` sources** — chat + scan + input; always confirms; can rewrite wholesale.
11. **`update` quality filter** — ruthless, prefer removing/rewriting over adding.
12. **Proactive trigger** — statusline staleness indicator only (deferred to v2); no hooks in v1.
13. **`load`** — full inline; no digest, no pointers.
14. **Two agents for `update`:** `content-extractor` (parallel extraction) + `update-critic` (ruthless filter pass).
15. **No agents for `load`.**
16. **Plugin location** — new sibling directory `project-context-mini/` in this repo, added to `marketplace.json`.

## Architecture

### Plugin layout

```
project-context-mini/
├── .claude-plugin/
│   └── plugin.json              # version 0.1.0
├── skills/
│   ├── update/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── file-scaffolds.md   # starter templates for 4 files
│   └── load/
│       └── SKILL.md
├── agents/
│   ├── content-extractor/
│   │   └── agent.md
│   └── update-critic/
│       └── agent.md
├── LICENSE
└── README.md
```

Top-level `.claude-plugin/marketplace.json` gets a second entry pointing at `./project-context-mini`.

### Artifact layout in user projects

```
.project-context-mini/
├── architecture.md              # mermaid-first + components + data model + deps list
├── flows.md                     # one H2 + mermaid per flow
├── patterns.md                  # conventions + anti-patterns + gotchas
├── status.md                    # current state essentials
├── architecture/refs/           # optional, created when architecture.md grows
├── flows/refs/                  # optional, created when flows.md grows
└── patterns/refs/               # optional, created when patterns.md grows
```

Kept deliberately separate from parent plugin's `.project-context/` so both can coexist in the same repo.

## Phases

### Phase 1 — Scaffolding

1. Create `project-context-mini/` directory tree.
2. Write `project-context-mini/.claude-plugin/plugin.json` — name, version `0.1.0`, description, author, skills path.
3. Append new plugin entry to root `.claude-plugin/marketplace.json`.
4. Copy `LICENSE` from parent (MIT, same author).
5. Stub `README.md` with install instructions, two-skill summary, and the four-file model.

**Exit:** `/plugin` lists `project-context-mini` and its skills after `/reload-plugins`.

### Phase 2 — File scaffolds reference

Write `skills/update/references/file-scaffolds.md` with four templates:

- **architecture.md scaffold** — `## Diagram` (placeholder Mermaid `graph TD`), `## Components`, `## Data Model`, `## Tech Stack`, `## Dependencies` (plain bullet list).
- **flows.md scaffold** — intro, one example H2 flow with placeholder Mermaid sequence diagram.
- **patterns.md scaffold** — `## Conventions`, `## Anti-patterns`, `## Gotchas`. No required diagram.
- **status.md scaffold** — `## Current Focus`, `## Why it matters`, `## Next Action`. No history.

Each scaffold ~20 lines with TODO markers so `update` knows what to fill.

**Exit:** `file-scaffolds.md` exists and is referenced by `update` skill.

### Phase 3 — `update` skill

Write `skills/update/SKILL.md` workflow:

1. **Detect `.project-context-mini/` state** — missing → bootstrap mode; present → refresh mode.
2. **Bootstrap mode** — create directory + four files from scaffolds. Ask user 4-6 seed questions (project goal, core user flow, any upfront conventions/gotchas, current focus). Confirm before writing.
3. **Refresh mode** — determine source (auto: chat if recent discussion, else scan; flags `--chat` / `--scan` / `--input`).
4. **Dispatch `content-extractor` agent** — receives conversation + current file contents, returns ranked candidates per target file.
5. **Dispatch `update-critic` agent** — receives extractor output, applies ruthless filter, returns minimal pre-filtered set (cap 3 per file).
6. **Present candidates to user** — grouped by target file, critic's reasoning inline. User approves/rejects per item.
7. **Apply approved updates** — Edit tool, preserve Mermaid diagrams, rewrite sections when rewriting makes file smaller.
8. **Refs-split suggestion** — if any of architecture/flows/patterns now exceeds ~75 lines, emit suggestion (not auto-run) to split into `<file>/refs/<section>.md`.
9. **Summary** — which files updated, which items added/rewritten.

**Exit:** `update` skill installs, handles both bootstrap and refresh, delegates extraction + filtering to the two agents.

### Phase 4 — `content-extractor` agent

Write `agents/content-extractor/agent.md`:

- Tools: `Read`, `Grep`, `Bash` (for `git diff`)
- Model: inherit
- Input: conversation digest + current file contents
- Output: ranked candidates per file with `{file, section, proposed_content, signal_type, impact_score}`
- Runs chat analysis + code scan in a single pass inside isolated context
- Scans for: architecture signals (components, tech, data model changes), flow signals (new journeys or changes), **pattern signals (conventions, anti-patterns, gotchas)**, status signals (focus shift, blockers)

**Exit:** Agent returns structured candidate list consumed by `update-critic`.

### Phase 5 — `update-critic` agent

Write `agents/update-critic/agent.md`:

- Tools: `Read` only
- Model: inherit
- Input: candidate list + current file contents
- Output: minimal filtered set + per-item rejection reasons
- Filter rules: "new teammate" test, redundancy check against current files, **detect "restating a framework default" for patterns and drop those**, prefer rewriting existing sections over adding new ones, cap 3 items per file, drop anything whose removal wouldn't reduce agent understanding
- Designed harsh — its job is to cut, not add

**Exit:** Agent returns ruthlessly-filtered candidate set with rejection reasons.

### Phase 6 — `load` skill

Write `skills/load/SKILL.md`:

1. Check for `.project-context-mini/` — if missing, "No mini context found. Run `/project-context-mini:update` to create." and stop.
2. Read all four files in full (they're tiny by design).
3. If `architecture/refs/`, `flows/refs/`, or `patterns/refs/` exist, read those too.
4. Emit content inline as structured digest with Mermaid diagrams preserved verbatim.
5. No agents, no pointers, no external references section.

**Exit:** Skill dumps all four files (plus any refs) into session context with diagrams intact.

### Phase 7 — Plugin docs

Update `project-context-mini/README.md`:

- Install via marketplace
- When to use mini vs parent (`project-context`)
- The four-file model with one-sentence purpose each
- Mermaid-first rule applies to architecture/flows/status; `patterns.md` is text-first
- Two-skill list with examples
- Coexistence note: `.project-context-mini/` is separate from `.project-context/`; both can live in same project

### Phase 8 — Smoke test

Manual verification in this repo:

1. `/reload-plugins` → both plugins load
2. `/project-context-mini:update` bootstrap on scratch dir → creates four files with scaffolds
3. `/project-context-mini:load` → reads them back inline
4. Make code change, `/project-context-mini:update` refresh → extractor + critic fire, present candidates (including at least one pattern/gotcha candidate), apply 1-2 updates
5. Verify refs-split suggestion fires when a file passes ~75 lines

## Risks & Trade-offs

- **No init skill means `update` carries bootstrap complexity.** Clean-branch in Step 1. Split into `init` skill later if gnarly.
- **Two agents for a "mini" plugin adds files.** Accepted — critic pass is what enforces "ruthless" without main-context agent policing itself.
- **`load` is single read pass — vulnerable to files drifting large.** Refs-split suggestion in `update` nudges users before `load` gets heavy.
- **Statusline staleness indicator deferred.** Manual trigger covers core use case; add in v2 if needed.
- **Parent `.project-context/` and mini `.project-context-mini/` can diverge if both used.** Accepted — different problems; documented coexistence is the fix.
- **`patterns.md` without a required diagram may grow prose-heavy fast.** Refs-split handles it.

## Dependencies

- None external. Pure markdown plugin, mirrors parent architecture.
- No Python scripts (parent has `manage_context.py`; mini doesn't manage CLAUDE.md).

## Out of Scope (reaffirmed)

- No `init`, `brainstorm`, `plan`, `implement`, `challenge`, `resume`, `save`, `next` skills
- No `brief.md`, no `progress.md`, no federated `dependencies.json`
- No hooks, no statusline work, no CLAUDE.md/AGENTS.md sync
- No hard line-budget caps (soft threshold only triggers refs-split suggestion)
