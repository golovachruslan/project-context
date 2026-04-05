---
name: project-context:load
description: "Load project context into the current session as a compact digest with file references. Use at the start of any session or before beginning work to prime the agent with project awareness without reading all files into context. Triggers: 'load context', 'load project', 'onboard me', 'get me up to speed', 'what do I need to know', 'prime context', 'bootstrap session'."
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Load Project Context

Load a compact project digest into the current session. Read the essential context files, produce a structured summary, and provide file references for deeper exploration.

## Purpose

Prime the agent with project awareness at session start. Read context files inline so the digest lands directly in the main agent's working memory, then provide file references for deeper exploration on demand.

## Workflow

### 1. Discover Context Files

```bash
ls .project-context/*.md .project-context/*.json 2>/dev/null
```

If `.project-context/` does not exist: respond with "No project context found. Run `/project-context:init` to set up." and stop.

### 2. Read Core Files

Always read these files in full:
- `.project-context/brief.md` — project scope, goals, constraints
- `.project-context/state.md` — current focus, blockers, next action
- `.project-context/dependencies.json` — cross-project relationships (if present)

### 3. Scan Supporting Files

Read these files but extract only key points:
- `.project-context/architecture.md` — tech stack, key decisions, diagram descriptions
- `.project-context/patterns.md` — established conventions
- `.project-context/progress.md` — recent completed work, in-progress items

### 4. Check for Active Plans

```bash
ls .project-context/plans/*.md 2>/dev/null
```

If plans exist, read only the first 20 lines of each to capture title, status, and overview.

### 5. Produce Digest

Output a structured digest following this format:

```markdown
## Project Context Loaded

### Project
[1-2 sentence overview from brief.md]

### Current Focus
[Current work focus, active plan, blockers from state.md]

### Tech Stack
[Key technologies from architecture.md — one line]

### Key Patterns
[Top 3-5 established conventions from patterns.md — bullet list]

### Recent Progress
[Last 3-5 completed items from progress.md — bullet list]

### Active Dependencies
[Upstream/downstream from dependencies.json, or "None declared"]

### Active Plans
[List plan files with title and status, or "No active plans"]

### Detailed References
For deeper context, read these files:
- `.project-context/brief.md` — full project goals, scope, requirements
- `.project-context/architecture.md` — system diagrams, tech decisions, component design
- `.project-context/patterns.md` — coding conventions, anti-patterns, learnings
- `.project-context/progress.md` — full work history and upcoming items
- `.project-context/state.md` — session state, blockers, decision log
```

## Quality Standards

- **Keep the digest under 400 words** — brevity is the entire point
- **Preserve specifics** — file paths, tech names, pattern names, plan names
- **Skip empty sections** — if patterns.md has no content, omit "Key Patterns"
- **Flag staleness** — if state.md is >3 days old or progress.md is >7 days old, note it:
  `> state.md last updated 5 days ago — may be stale. Run /project-context:update --scan to refresh.`
- **Always include the "Detailed References" section** — this is the key value: pointers for later exploration without loading now

## Edge Cases

### Minimal context (just initialized)
If files exist but are mostly empty templates, output:
```
Project context initialized but sparse. Key files to populate:
- brief.md — add project overview and goals
- architecture.md — add tech stack and system design
Run /project-context:update --input to populate interactively.
```

### Large context files (>100 lines each)
Extract only the most relevant sections. Do not attempt to summarize everything — focus on current state and active work.

### No state.md
If state.md is missing, use progress.md "In Progress" section as the current focus indicator.
