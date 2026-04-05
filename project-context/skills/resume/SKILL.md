---
name: project-context:resume
description: "Resume work from a previous session using the continue.md handoff document. Triggers: 'resume', 'pick up where we left off', 'continue from last session', 'what were we doing', 'restore session'. Reads .project-context/continue.md and project context to restore full session state."
allowed-tools:
  - Read
  - Glob
  - Grep
  - AskUserQuestion
---

# Resume Work

Pick up where a previous session left off by reading the continue.md handoff document and project context.

## Workflow

### Step 1: Read Handoff Document

```bash
ls .project-context/continue.md 2>/dev/null
```

If `continue.md` exists, read it to understand:
- What was being worked on
- Where exactly work stopped
- Decisions already made
- Next steps planned

If `continue.md` does NOT exist:
- Read `.project-context/state.md` for last known position
- Read `.project-context/progress.md` for current status
- Inform user: "No handoff document found. Here's what I can see from project context..."

### Step 2: Restore Native Tasks

If `continue.md` references a Task List ID:
- Set `CLAUDE_CODE_TASK_LIST_ID` to the referenced ID
- Native Tasks persist in `~/.claude/tasks/` — the full task DAG with dependencies and status is automatically available
- Press `Ctrl+T` to view the restored task list
- Tasks that were "in progress" when paused should be re-examined

If no Task List ID is referenced, check if native Tasks have pending items from a previous session.

### Step 3: Read Full Context

Read all context files to rebuild understanding:
- `.project-context/brief.md` — project goals
- `.project-context/architecture.md` — system design
- `.project-context/state.md` — current position
- `.project-context/progress.md` — work status
- `.project-context/patterns.md` — conventions

If an active plan is referenced, read it too:
```bash
ls .project-context/plans/*.md 2>/dev/null
```

### Step 4: Present Status

```
## Resuming Session

**Previous Session:** [date from continue.md]
**Focus:** [what was being worked on]

**Where we left off:**
[Summary from continue.md]

**Next steps (from handoff):**
1. [Step 1]
2. [Step 2]

Shall I continue with step 1, or would you like to adjust the plan?
```

### Step 5: Get Confirmation

Use AskUserQuestion to confirm the user wants to continue as planned, or if priorities have changed.

### Step 6: Clean Up

After resuming, update state.md with current session info and remove or archive continue.md:
- Update "Last Session" date
- Update "Focus" to current work
- Optionally delete continue.md (it's served its purpose)

### Step 7: Recommend Next Step

Launch a `next-step-recommender` agent with:
- **Completed skill:** `resume`
- **Summary:** Brief description of session resumed (what was the focus, what continue.md indicated)

Append the agent's recommendation to your status presentation:

```
**Recommended next step:**
→ [NEXT_STEP from agent]
  [REASON from agent]
```

If Agent tool is unavailable, refer to `../project-context/references/next-step-recommendations.md` for the recommendation graph and determine the next step manually.
