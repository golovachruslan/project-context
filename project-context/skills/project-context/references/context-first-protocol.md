# Context-First Protocol

**MANDATORY for all project-context skills.** This protocol MUST be followed before any codebase scanning, exploration, or code reading.

## Rule

Before using Glob, Grep, or Read on codebase files (anything outside `.project-context/`), you MUST:

1. Check if `.project-context/` exists
2. If it exists, read the relevant context files (see File Selection below)
3. If `dependencies.json` exists, ALWAYS read it and build a Dependency Digest (see `dependency-loading.md`)

Only after completing these steps may you scan or explore the codebase.

## File Selection

At minimum, always read:
- `brief.md` — project scope and goals
- `dependencies.json` — cross-project boundaries (if present)

Then read selectively based on task:

| Task Type | Also Read |
|-----------|-----------|
| Planning, brainstorming | `architecture.md`, `state.md` (for existing plans) |
| Implementation, code changes | `architecture.md`, `patterns.md`, `state.md` |
| Research, info queries | Relevant files per query topic (see info skill) |
| Challenge, review | `architecture.md`, `patterns.md` |
| Context management (update, optimize) | All files as needed by operation |

## Dependencies Are Non-Optional

When `dependencies.json` exists, ALWAYS:
1. Read it
2. Build a Dependency Digest (see `dependency-loading.md` Step 1)
3. Run Boundary Detection (see `dependency-loading.md` Step 2) against the current task

Do NOT conditionally skip based on keyword matching in the user's request. Users may describe features that cross boundaries without using terms like "integration" or "API."

## Agent Callers

When launching agents that will explore code (e.g., `codebase-explorer`), ALWAYS:
- First produce a project context digest (via `context-reader` agent or manual reading)
- Pass the digest to the agent — do not treat it as optional
- The `codebase-explorer` agent should receive the digest before it begins any file exploration

## Skill Preamble

Skills referencing this protocol should include this preamble at the start of their workflow:

> **Context-First (mandatory).** Follow the [Context-First Protocol](../project-context/references/context-first-protocol.md) before any codebase scanning. Read `.project-context/` files and `dependencies.json` (if present) FIRST.
