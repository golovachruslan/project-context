---
name: project-context:pause
description: Save session state for later resumption. Creates a handoff document with full context.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
---

# Pause Work

Save current session state so work can be resumed in a new conversation.

## Workflow

### Step 1: Gather Current State

Read all available context:
- `.project-context/state.md` — current position
- `.project-context/progress.md` — what's done/in-progress
- `.project-context/plans/*.md` — active plans and their status
- Current conversation context — what was being discussed/built

### Step 2: Create Continue Document

Write `.project-context/continue.md` with structured handoff:

```markdown
# Continue Here

**Paused:** [YYYY-MM-DD HH:MM]
**Session Focus:** [What this session was about]

## Where We Left Off
[1-3 sentences about exactly what was happening when paused]

## Current State
- **Active Plan:** [plan name and current phase/task, or "none"]
- **Last Completed:** [most recent completed task]
- **In Progress:** [what was mid-flight]
- **Files Modified:** [list of files changed this session]

## Decisions Made This Session
- [Key decision 1]
- [Key decision 2]

## Blockers / Open Questions
- [Any unresolved issues]

## Next Steps (in order)
1. [Immediate next action]
2. [Following action]
3. [After that]

## Context for Next Session
[Any nuance that would be lost without this note — edge cases discovered,
approaches tried and rejected, user preferences expressed, etc.]
```

### Step 3: Export Native Tasks State

If native Tasks are active (`Ctrl+T`), capture the current task list state in `continue.md`:
- List all pending/in-progress tasks with their dependencies
- Note the `CLAUDE_CODE_TASK_LIST_ID` if one was set
- Tasks persist on disk in `~/.claude/tasks/` — the new session can resume from the same task list

Add a "Task List" section to `continue.md`:
```markdown
## Task List State
**Task List ID:** [ID if set, or "default"]
**Pending tasks:** [count]
**In progress:** [task names]
**Blocked by:** [dependency info]

To restore: Set `CLAUDE_CODE_TASK_LIST_ID=[ID]` in the new session.
```

### Step 4: Update State File

Update `.project-context/state.md`:
- Set "Focus" to note paused state
- Set "Next Action" to "Resume from continue.md"
- Update "Last Session" date

### Step 5: Confirm

```
Session state saved to .project-context/continue.md

To resume in a new session:
  /project-context:resume

Or simply tell Claude: "Read .project-context/continue.md and pick up where we left off"

Native Tasks persist automatically in ~/.claude/tasks/ — your task list
will be available in the new session.
```
