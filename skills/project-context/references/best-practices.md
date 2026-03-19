# Best Practices for Project Context

## Core Principles

1. **Concise** — Scannable bullet points, not encyclopedic prose. Link to detailed docs.
2. **Current** — Stale context is worse than no context. Update after significant changes.
3. **Honest** — Document what IS, not what should be. Include known issues and debt.
4. **Useful** — Write for someone new. Include "why" not just "what". Make it actionable.

## File-Specific Guidelines

| File | Update When | Don't |
|------|-------------|-------|
| `brief.md` | Scope/goals change (rarely) | Include implementation details |
| `architecture.md` | New components/flows added | Document every file/function |
| `state.md` | Every session start/end | Let it grow beyond ~50 lines |
| `progress.md` | Tasks complete/start | Track micro-tasks |
| `patterns.md` | New pattern established | Document obvious patterns |
| `dependencies.json` | Dependencies added/removed | List every import — just key boundaries |

## Staleness Indicators

| File | Stale If |
|------|----------|
| `brief.md` | >30 days + active development |
| `architecture.md` | >7 days + code structure changes |
| `state.md` | >1 day during active development |
| `progress.md` | >3 days during active development |
| `patterns.md` | >14 days + new patterns in code |
| `dependencies.json` | >30 days + new dependencies added |

## Mermaid Diagrams

- One concept per diagram
- Use clear labels (full words, not abbreviations)
- Group related nodes with subgraphs
- **Every diagram MUST have a text description below it**

## Managed Sections in CLAUDE.md / AGENTS.md

project-context uses HTML comment markers to delimit managed sections:
```markdown
<!-- PROJECT-CONTEXT:START -->
[Auto-managed content]
<!-- PROJECT-CONTEXT:END -->
```

- Content between markers is auto-updated by commands
- Content outside markers is never modified
- Safe to run init/update multiple times (idempotent)

## Dependencies (dependencies.json)

### When to Use
- Monorepos with 2+ subprojects that share code, APIs, or types
- Any project that imports from or exports to a sibling project
- Cross-repository dependencies where you need the other project's context (git link)

### Local Path Dependencies

For monorepo siblings that exist on the same filesystem.

| Aspect | Guideline |
|--------|-----------|
| **Upstream/Downstream** | Declare both directions; `/add-dependency` offers reciprocal updates |
| **Paths** | Use relative paths from the project root (`../shared`, `../api`) |
| **Integration Points** | List key files at boundaries, not every import |
| **Impact Rules** | Focus on breaking-change scenarios only |
| **Staleness** | `dependencies.json` changes rarely (30-day threshold) — update when deps change |

### Reciprocal Declarations (Local)

If `api` lists `shared` as upstream, then `shared` should list `api` as downstream. The `/project-context:add-dependency` command handles this automatically by offering to update both sides.

### Git Link Dependencies

For remote repositories not on the local filesystem. Only `.project-context/` is fetched — no application code.

| Aspect | Guideline |
|--------|-----------|
| **When to use** | External services, shared libraries in separate repos, cross-team dependencies |
| **URL format** | HTTPS preferred (`https://github.com/org/repo.git`); SSH also supported |
| **Ref** | Track a stable branch (`main`) or release tag; avoid tracking volatile branches |
| **Fetching** | Run `/project-context:add-dependency --fetch` to refresh stale caches |
| **Cache** | Stored in `.project-context/.deps-cache/<project>/` — auto-gitignored |
| **No reciprocal** | Cannot update remote repos; the other project must independently add a reverse link |

### Context Resolution

When working in a subproject:
1. Read that subproject's `.project-context/` first
2. Check `dependencies.json` for upstream/downstream relationships
3. For local deps: pull in `brief.md` + `architecture.md` when touching integration boundaries
4. For git link deps: read from `.deps-cache/<project>/` (flat files — brief.md, architecture.md, etc.)
5. Never load a dependency's `state.md` or `progress.md` — that's their internal concern

### Monorepo Initialization

Each subproject gets its own `/project-context:init`. The root can also have a `.project-context/` for system-wide architecture and shared patterns.

## Common Mistakes

1. **Too much detail** → Link to docs, keep context high-level
2. **Never updating** → Build updates into workflow
3. **No diagrams** → Add Mermaid for every architectural flow
4. **Diagrams without descriptions** → Always add step-by-step text
5. **Optimistic progress** → Be honest about blockers
6. **Duplicating CLAUDE.md** → Reference context files, don't duplicate
7. **One-way dependency declarations** → Always declare both upstream and downstream
8. **Loading all dependency contexts** → Only load brief + architecture, not state/progress
9. **Forgetting to fetch git deps** → Run `/project-context:add-dependency --fetch` to refresh cached contexts
10. **Tracking volatile branches** → Use stable refs (main, tags) for git link dependencies
