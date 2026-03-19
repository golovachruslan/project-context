---
name: project-context:implement
description: "Use when users want to execute an implementation plan. Triggers: 'implement this plan', 'start implementing', 'execute the plan', 'build this'. Executes plans with multi-agent parallelism and enforces context file updates on completion."
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - Agent
hooks:
  PostToolUse:
    - matcher: "Edit"
      hooks:
        - type: agent
          prompt: |
            Check if the file just edited is a plan in .project-context/plans/.
            Input: $ARGUMENTS

            If it's NOT a plan file, return {"ok": true}.

            If it IS a plan file, check if the edit changed the Status field to "Completed".
            To determine this, read the plan file and look for "**Status:** Completed".

            If status is NOT being set to Completed → return {"ok": true} (implementation still in progress).

            If status IS set to Completed, verify that context files were updated:
            1. Read .project-context/state.md — it should reflect post-implementation state
               (should NOT still reference "Planning" or "Implementing" as current focus
               without noting completion).
            2. Read .project-context/progress.md — it should have a recent entry referencing
               the completed feature/plan.

            If BOTH files appear updated with completion info, continue to step 3.
            If either file is missing completion info → return {"ok": false,
              "reason": "Implementation marked complete but context files not synced. You MUST update state.md (set current focus to completed feature, set next action) and progress.md (add completed items with date) before finishing. This is mandatory per Step 7 of the implement workflow."}

            3. Check architecture.md and patterns.md (soft check — warning, not blocking):
               Read .project-context/architecture.md and .project-context/patterns.md.
               Read the plan file to understand what was implemented.

               Build a warning message if applicable:
               - If the plan added new components, services, tech, or changed flows AND
                 architecture.md doesn't appear to reflect these → add warning:
                 "Consider updating architecture.md — implementation added new components/flows."
               - If the plan established new patterns or conventions AND
                 patterns.md doesn't appear to reflect these → add warning:
                 "Consider updating patterns.md — implementation established new patterns."

               If warnings exist → return {"ok": true,
                 "warning": "[warnings joined]. Run Step 7d-7e of the implement workflow to evaluate whether these files need updating."}
               If no warnings → return {"ok": true}
          statusMessage: "Verifying context sync..."
          timeout: 120
---

# Implementation Skill

This skill enforces context file synchronization when plans are implemented. It works alongside the `/project-context:implement` command.

## Agents

This skill uses the following agents:
- **`task-implementer`** — Executes individual plan tasks in parallel (independent tasks within a phase)
- **`context-syncer`** — Updates context files post-completion (state.md, progress.md, etc.)
- **`context-reader`** — Reads project context once for distribution to task-implementer agents

If the Agent tool is unavailable, tasks execute sequentially and context syncing happens manually.

## Context Sync Enforcement

The PostToolUse hook on this skill monitors plan file edits. When a plan's status is changed to "Completed", the hook enforces a two-tier check:

### Tier 1 — Hard enforcement (blocks completion)
- **state.md** must reflect post-implementation state (current focus, next action)
- **progress.md** must have entries for completed work with dates

If either is missing, the hook returns an error and the agent must update them before proceeding.

### Tier 2 — Soft enforcement (warns but doesn't block)
- **architecture.md** — warns if the implementation added components, flows, or technology that aren't reflected
- **patterns.md** — warns if new patterns or conventions were established but not recorded

Soft warnings prompt the agent to evaluate Steps 7d-7e of the implement workflow.

## Required Updates on Plan Completion

When marking a plan as completed, you MUST:

1. **state.md** — Update current focus, next action, recently completed
2. **progress.md** — Add completed items with dates and deliverables

And you MUST evaluate (update only if applicable):

3. **architecture.md** — If new components, flows, tech, or integration points were added
4. **patterns.md** — If new coding patterns, conventions, or anti-patterns were discovered

See the `/project-context:implement` command Steps 7a-7f for full workflow details.
