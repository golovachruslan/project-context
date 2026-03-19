---
name: project-context:project-context
description: "Use this skill when users ask about project context, project goals, current progress, architecture, technical decisions, project status, or current state. Triggers: 'what is this project', 'project goals', 'current progress', 'architecture', 'tech stack', 'what are we working on', 'project status', 'where are we'."
---

# Project Context Skill

Provide informed responses about project state by reading structured context files from `.project-context/`.

## Context Files (5+1 file model)

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `brief.md` | Project goals, scope, requirements | Rarely (on pivots) |
| `architecture.md` | Tech stack, Mermaid diagrams, system design | On architecture changes |
| `state.md` | Current position, blockers, next action | Every session |
| `progress.md` | Completed/in-progress/upcoming work | Multiple times per week |
| `patterns.md` | Established patterns and learnings | As patterns emerge |
| `dependencies.json` | Cross-project dependencies (monorepo, optional) | On dependency changes |

## Workflow

### 1. Check for Context Files

```bash
ls .project-context/*.md .project-context/*.json 2>/dev/null
```

If not found: "No project context found. Run `/project-context:init` to set up."

### 2. Read Relevant Files

| Query Type | Primary File | Secondary |
|------------|--------------|-----------|
| "What is this project?" | brief.md | architecture.md |
| "Current status/progress" | state.md | progress.md |
| "Where are we?" | state.md | progress.md |
| "Architecture/how it works" | architecture.md | patterns.md |
| "Tech stack" | architecture.md | - |
| "What patterns do we use?" | patterns.md | architecture.md |
| "What depends on this?" | dependencies.json | architecture.md |
| "Cross-project impact?" | dependencies.json | state.md |
| General context | brief.md + state.md | architecture.md (only if needed) |

### 3. Synthesize Response

- **Be concise** — Extract key points, don't dump files
- **Reference diagrams** — Describe flows from Mermaid diagrams
- **Note currency** — Check timestamps, warn if stale
- **Connect dots** — Link related info across files

### 4. Handle Missing Context

1. Answer with available information
2. Note what's missing
3. Suggest: "Run `/project-context:update [file]` to add this"

### 5. Staleness Detection

If context seems stale (state.md >1 day, progress.md >3 days during active dev):
- Suggest: "Context may be outdated. Run `/project-context:update --scan` to refresh."

## Monorepo Support

For monorepos with multiple subprojects, each subproject can have its own `.project-context/` with an optional `dependencies.json` declaring cross-project relationships.

### Context Resolution (Federated Model)

1. Always load local `.project-context/`
2. When touching integration boundaries, check `dependencies.json` for upstream/downstream
3. On-demand: read a dependency's `brief.md` + `architecture.md` for cross-project context

### Adding Dependencies

Use `/project-context:add-dependency` to interactively declare a relationship. It handles:
- Discovering sibling projects
- Creating or updating `dependencies.json`
- Offering reciprocal updates to the target project

### Viewing Dependencies

```bash
# Show parsed deps for current project
python manage_context.py deps --dir .
```

## Reference

- `references/file-templates.md` — Template structures for each file (including dependencies.json)
- `references/best-practices.md` — Guidelines for maintaining context
