---
name: project-context:ask
description: "Answer questions about the current project by combining structured context files with live codebase exploration. Use when users ask about project goals, architecture, tech stack, progress, status, how something works, where something is implemented, or any project question. Triggers: 'what is this project', 'project goals', 'current progress', 'architecture', 'tech stack', 'what are we working on', 'project status', 'where are we', 'how does', 'where is', 'what is', 'explain', 'show me', 'find where', 'why does'."
context: fork
---

# Ask

Research and answer questions about the current project by combining structured context files with live codebase exploration.

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

### 1. Gather Context Layer

**Context-First (mandatory).** Follow the [Context-First Protocol](../project-context/references/context-first-protocol.md) before any codebase scanning. Read `.project-context/` files and `dependencies.json` (if present) FIRST. Complete this step before proceeding to Step 2.

```bash
ls .project-context/*.md .project-context/*.json 2>/dev/null
```

If not found: "No project context found. Run `/project-context:init` to set up."

If found, always read `brief.md` and `dependencies.json` (if present), then read additional files based on the question:

| Question About | Read |
|---------------|------|
| Project purpose, goals, "what is this project?" | `brief.md` |
| Tech stack, system design, architecture | `architecture.md` |
| Current status, blockers, "where are we?" | `state.md`, `progress.md` |
| What's done / in progress | `progress.md` |
| Code conventions, learnings, patterns | `patterns.md` |
| Dependencies, integrations, cross-project | `dependencies.json` + relevant dep's cached `brief.md` / `architecture.md` |

When `dependencies.json` exists, always build a Dependency Digest, run Boundary Detection, and load context files for boundary-detected dependencies (see `project-context/skills/project-context/references/dependency-loading.md` Steps 1-3). This must happen before any codebase scanning in Step 2.

Also check for `CLAUDE.md`, `README.md`, or similar project docs at the repo root.

### 2. Research the Codebase (if context files don't fully answer the question)

If the question is fully answered by context files alone, skip to Step 3. Otherwise, use targeted codebase exploration.

For complex questions, launch a `context-reader` agent and a `codebase-explorer` agent in parallel — context-reader provides project background while codebase-explorer digs into the code.

Choose strategy based on question type:

**"Where is X?"** — Find files/symbols
- Glob for file patterns matching the concept
- Grep for class/function/variable names
- Report file paths with line numbers

**"How does X work?"** — Trace execution flow
- Launch a `codebase-explorer` agent with the question and relevant directories
- Or manually: find entry point, read implementation, follow dependencies one level deep
- Summarize the flow

**"What does this project do?"** — High-level overview
- Read project root files (package.json, Cargo.toml, pyproject.toml, go.mod, etc.)
- Scan directory structure
- Read main entry points
- Combine with context files if available

**"Why does X?"** — Understand rationale
- Read the relevant code
- Check git log for the file/function (`git log --oneline -10 -- <file>`)
- Look for comments, docs, or ADRs explaining the decision

**General / complex questions** — Use parallel research
- Launch a `codebase-explorer` agent for broad codebase research
- Optionally launch `context-reader` agent in parallel for project context
- Combine findings from both agents
- Fallback: if Agent tool unavailable, use Glob/Grep/Read directly

### 3. Synthesize the Answer

- **Lead with the direct answer** — don't bury it under context
- **Be concise** — extract key points, don't dump files
- **Cite specific files and line numbers** — use `file_path:line_number` format
- **Reference diagrams** — describe flows from Mermaid diagrams when relevant
- **Include short code snippets** when they clarify the answer
- **Note gaps** — if something is unclear or undocumented, say so
- **Note staleness** — if context seems stale (state.md >1 day, progress.md >3 days), warn:
  "Context may be outdated. Run `/project-context:update --scan` to refresh."

### 4. Suggest Follow-ups (only when natural)

If the research revealed related useful information:
- Mention it briefly ("Related: the caching layer at `src/cache.ts` also touches this")
- Do NOT suggest running commands or initializing things unless directly relevant

## Monorepo Support

For monorepos with multiple subprojects, each subproject can have its own `.project-context/` with an optional `dependencies.json` declaring cross-project relationships.

### Context Resolution (Federated Model)

1. Always load local `.project-context/`
2. When touching integration boundaries, check `dependencies.json` for upstream/downstream
3. On-demand: read a dependency's `brief.md` + `architecture.md` for cross-project context

## Reference

- `../project-context/references/file-templates.md` — Template structures for each file
- `../project-context/references/best-practices.md` — Guidelines for maintaining context
- `../project-context/references/dependency-loading.md` — Cross-project dependency loading
