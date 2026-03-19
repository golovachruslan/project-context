---
name: project-context:next
description: Smart routing - determines what to do next based on current project state
allowed-tools:
  - Read
  - Bash
  - Glob
---

# What's Next?

Analyze project state and route to the right next action.

## Workflow

### Step 1: Check Context Status

Run the status script to get current state:

```bash
python project-context/scripts/manage_context.py status --dir .
```

If `manage_context.py` is not available, check manually:

```bash
ls .project-context/*.md 2>/dev/null
ls .project-context/plans/*.md 2>/dev/null
```

Also check native Tasks (`Ctrl+T`) for pending/in-progress task items from previous sessions. Native Tasks persist on disk and may contain work items not yet reflected in context files.

### Step 2: Route Based on State

Follow this routing logic in order:

```
No .project-context/ dir?           → "Run /project-context:init to set up project context"
Missing brief.md or architecture.md → "Run /project-context:init — critical files missing"
state.md is stale (>1 day)?         → "Run /project-context:update to refresh state"
Plan exists with Status: Planning?  → "Plan '[name]' is ready. Run /project-context:implement [path]"
Plan exists, partially done?        → "Resume implementation. Run /project-context:implement [path]"
Multiple stale files?               → "Context is stale. Run /project-context:update --scan"
Context is fresh, no active plans?  → "Ready for new work. Run /project-context:brainstorm to brainstorm"
```

### Step 3: Read State File for Context

If `.project-context/state.md` exists, read it for additional routing info:
- Check "Next Action" field for explicit guidance
- Check "Blockers" for impediments
- Check "Active Plan" for current focus

### Step 4: Present Recommendation

```
## Project Status

**Current Phase:** [from state.md or inferred]
**Active Plan:** [plan name or none]
**Context Health:** [fresh / stale files listed]

## Recommended Next Action

→ **[Command to run]**
[Reason why this is the right next step]

## Other Options
- /project-context:brainstorm — Start brainstorming a new feature
- /project-context:plan — Create a plan (if decisions are locked)
- /project-context:update — Refresh context files or extract learnings
- /project-context:pause — Save session state for later
```
