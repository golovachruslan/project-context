---
name: project-context:quick
description: Quick ephemeral mode for ad-hoc tasks. Skips brainstorming, creates minimal plan, executes immediately.
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
---

# Quick Mode

Streamlined path for ad-hoc tasks. Skips brainstorming phase, creates a minimal plan, and executes immediately. No files saved — purely ephemeral.

## When to Use

- Small features or bug fixes (< 1 day of work)
- Tasks where the approach is obvious
- Quick prototypes or spikes
- When full discuss → plan → implement is overkill

## Workflow

### Step 1: Read Project Context (if exists)

```bash
ls .project-context/*.md 2>/dev/null
```

If context exists, quickly read `architecture.md` and `patterns.md` to follow existing conventions.

### Step 2: Clarify the Task

Ask 1-2 focused questions if anything is ambiguous. Skip if the task is clear.

Keep it to essentials only:
- What exactly needs to happen?
- Any constraints or preferences?

### Step 3: Create Mental Plan

Internally create a plan of 1-3 tasks. Present it briefly:

```
Quick plan for [task]:
1. [Task] — [files affected]
2. [Task] — [files affected]
3. [Task] — [files affected]

Proceeding unless you want to adjust.
```

Wait for user acknowledgment (don't require formal approval — a simple "go" or no objection is fine).

### Step 4: Execute

Implement the tasks following existing project patterns. For each task:
- Make the change
- Verify it works (run tests, check output)
- Move to next task

### Step 5: Quick Summary

```
Done! Here's what changed:
- [File]: [What changed]
- [File]: [What changed]

[Any follow-up suggestions if relevant]
```

## Task Tool Usage

**If `Task` is available**, use subagents for:
- Parallel implementation of independent tasks
- `subagent_type=Explore` for quick codebase reconnaissance
- Run independent verification steps as background tasks (`run_in_background=true`)

## Rules

- **No files saved** to `.project-context/plans/` — this is ephemeral
- **Update state.md** if it exists (note what was done)
- **Update progress.md** if it exists (mark task as completed)
- **Follow deviation rules**: Auto-fix bugs, auto-add validation, ASK about architecture changes
- **Atomic commits per task** if the user wants commits
