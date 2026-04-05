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

# Implement Plan

Execute an implementation plan with multi-agent parallelism and automatic deviation handling.

## Usage

```
/project-context:implement [plan-path] [--sequential]
```

**Flags:**
- **`--sequential`** — Force sequential execution, no parallel agents

If no flag is provided, uses `task-implementer` agents for parallel execution.

## Execution Strategy

**Default: Agent-based parallel execution**
1. Launch a `context-reader` agent to produce a project digest
2. For each phase, group tasks by dependencies
3. Launch `task-implementer` agents in parallel for independent tasks within a phase
4. Collect results, handle ASK-level deviations in the main session
5. After all phases complete, launch `context-syncer` agent for post-completion sync

```
Phase 1: task-implementer (A) ──┐
         task-implementer (B) ──┤ parallel (independent tasks)
         task-implementer (C) ──┘
                                ↓
                          Collect, handle deviations
Phase 2: task-implementer (D) ──┐
         task-implementer (E) ──┘
                                ↓
                          context-syncer agent
```

Each `task-implementer` agent receives:
- The specific task (Files, Action, Verify, Done criteria)
- The project context digest from `context-reader`
- Deviation rules and locked decisions from the plan

**Fallback: Sequential execution**
If Agent tool is unavailable or `--sequential` is specified, execute tasks sequentially with direct tool operations in the main session.

## Workflow

### Step 1: Locate the Plan

**If path provided:** Read the specified plan file.

**If no path:**
1. Check conversation for a plan
2. Check `.project-context/plans/` for saved plans
3. If multiple plans, ask user which one
4. If no plans found: "Run `/project-context:plan` first"

### Step 2: Confirm Scope

Present the plan summary and ask:
```
Plan: [Name]
Phases: [N] with [M] total tasks
Execution: [Parallel agents / Sequential]

Options:
1. Implement all phases
2. Implement only Phase [N]
3. Pick specific tasks
4. Cancel
```

**Do not proceed without confirmation.**

### Step 3: Read Project Context

**Context-First (mandatory).** Follow the [Context-First Protocol](../project-context/references/context-first-protocol.md). This step MUST complete before Step 5 (Execute). Do NOT begin implementation until context is loaded.

**Launch a `context-reader` agent** to produce a condensed project digest covering architecture, patterns, state, and dependencies.

The digest is passed to each `task-implementer` agent so they don't re-read the same files.

**If Agent tool is unavailable**, read directly:
- `.project-context/brief.md` — Project scope and goals
- `.project-context/architecture.md` — Follow existing patterns
- `.project-context/patterns.md` — Respect conventions
- `.project-context/state.md` — Current position
- `.project-context/dependencies.json` — Cross-project boundaries (if present — ALWAYS read, do not skip)

If `dependencies.json` exists, the digest should include dependency info for detecting when tasks touch integration boundaries. When Boundary Detection flags a dependency, also load that dependency's cached context files (`brief.md`, `architecture.md`) — see `dependency-loading.md` Steps 1-3.

### Step 4: Initialize Task Tracking

**Use native Tasks** (press `Ctrl+T` to view) for tracking implementation progress:
- Create a task entry for each plan task with proper dependencies
- Tasks persist across sessions — if the session is interrupted, progress is preserved
- Set `CLAUDE_CODE_TASK_LIST_ID=project-[name]` to share task state across sessions

**Fallback:** If native Tasks are not available, use TodoWrite for in-session tracking.

### Step 5: Execute Phase by Phase

For each phase:

1. **Announce the phase** with task list
2. **Group tasks by dependencies**:
   - Independent tasks → launch `task-implementer` agents in parallel
   - Dependent tasks → execute sequentially (wait for dependencies to complete)
3. **For each task**, follow the executable format:
   - Read the **Action** field for what to do
   - Implement the change
   - Run the **Verify** check
   - Confirm against **Done when** criteria
4. **Mark completed tasks** immediately (in native Tasks and plan file)
5. **Handle deviations** using the rules below

### Step 6: Deviation Rules

When encountering unexpected situations during execution:

| Priority | Situation | Action |
|----------|-----------|--------|
| **Auto-fix** | Bugs (null pointers, inverted logic, security holes) | Fix immediately without asking |
| **Auto-add** | Missing validation, error handling, auth checks | Add without asking |
| **Auto-fix** | Blocking issues (missing imports, broken deps) | Fix without asking |
| **ASK** | Architecture changes (new tables, schema changes, framework switches) | **STOP and ask user** |
| **ASK** | Scope expansion (features not in the plan) | **STOP and ask user** |
| **ASK** | Changes that may break contracts with downstream dependencies (e.g., modifying shared types, API responses, exported interfaces listed in a dep's `what`) | **STOP and ask user** |
| **NEVER** | Skip tests, ignore patterns, change unrelated code | Never do this |

**Rule: ASK always supersedes Auto-fix/Auto-add.** When in doubt, ask.

**Agent deviation handling:** `task-implementer` agents report DEVIATION-level situations in their results. The main session (orchestrator) collects these and consults the user before proceeding.

### Step 7: MANDATORY — Sync Context Files

**CRITICAL: This step is NOT optional. The implement workflow is NOT complete until all context files are updated. Do NOT present the final summary until this step is fully done.**

After completing implementation (or after each phase for multi-phase plans), you MUST update these files:

#### 7a. Update plan file status

Edit the plan file to change:
- `**Status:** Planning` → `**Status:** In Progress` (during execution)
- `**Status:** In Progress` → `**Status:** Completed` (when all phases done)
- Mark individual tasks as completed within the plan

#### 7b. Update `.project-context/state.md`

Read current `state.md`, then use Edit to update:

- **Current Focus** → what was just completed or what's in progress
- **Next Action** → next step after implementation (testing, review, deploy, etc.)
- **Blockers** → any issues discovered during implementation

Example after full completion:
```markdown
## Current Focus
Completed: [Feature Name] implementation — all [N] phases done

## Next Action
Run full test suite and review changes before merging

## Recently Completed
- [Feature Name] — implemented via `.project-context/plans/[name].md`
```

Example after partial completion (phase N of M):
```markdown
## Current Focus
Implementing: [Feature Name] — Phase [N] of [M] complete

## Next Action
Continue with Phase [N+1]: [Phase Name]
```

#### 7c. Update `.project-context/progress.md`

Read current `progress.md`, then use Edit to:

- Move completed items from **In Progress** / **Upcoming** to **Completed** section
- Add entries with today's date for each completed phase/feature
- Reference specific deliverables (files created, endpoints added, etc.)

Example:
```markdown
## Completed
- **YYYY-MM-DD**: [Feature Name] — Phase 1: [description], Phase 2: [description]
  - Files: `path/to/new-file.ts`, `path/to/modified-file.ts`
  - Plan: `.project-context/plans/[name].md`
```

#### 7d. Evaluate `.project-context/architecture.md` (if applicable)

Review the implementation and check — did it:
- Add new components, services, or modules?
- Change system flows or data flows?
- Introduce new technology or libraries?
- Modify integration points or API boundaries?
- Change deployment or infrastructure patterns?

**If YES to any:** Read current `architecture.md`, then Edit to add/update:
- New components in the **System Overview** Mermaid diagram with step-by-step description
- Updated flows reflecting the changes
- New entries in **Key Decisions** table with date and rationale
- Updated **Tech Stack** table if new technology was introduced

**If NO to all:** Skip — note "no architectural changes" in the summary.

#### 7e. Evaluate `.project-context/patterns.md` (if applicable)

Review the implementation and check — did it:
- Establish a new coding convention or reusable pattern?
- Discover an anti-pattern to avoid in the future?
- Use a notable error handling or integration approach?
- Adopt a naming convention or organizational structure?
- Find a solution to a recurring problem?

**If YES to any:** Read current `patterns.md`, then Edit to add:
- New pattern in **When / Example / Notes** format
- New anti-pattern in **Problem → Do This Instead** format
- New convention in the appropriate table
- New learning under the **Learnings** section

Only add patterns that are **reusable** — skip one-off implementation details.

**If NO to all:** Skip — note "no new patterns" in the summary.

#### 7f. Verify All Updates

Confirm that:
- [ ] Plan file status is updated
- [ ] `state.md` reflects current position post-implementation
- [ ] `progress.md` has entries for completed work
- [ ] `architecture.md` evaluated — updated if architectural changes occurred
- [ ] `patterns.md` evaluated — updated if new patterns emerged

**Only after completing 7a–7f should you proceed to Step 8.**

### Step 8: Summary

```
Implementation Complete!

Phases: [X/Y] completed
Tasks: [N] completed, [M] skipped
Execution: [Parallel agents / Sequential]

Files created:
- path/to/new-file.ts

Files modified:
- path/to/existing.ts

Context files updated:
- state.md — current focus and next action updated
- progress.md — completed items recorded
- architecture.md — [updated: new components/flows | no architectural changes]
- patterns.md — [new patterns added / no new patterns]
- plans/[name].md — status set to Completed

Dependencies potentially affected:
- [dep name]: [what was touched] — consider coordinating

Next steps:
1. [Testing recommendations]
2. [Consider running /project-context:update --chat to capture additional learnings]
```

### Step 9: Recommend Next Step

After the summary, launch a `next-step-recommender` agent with:
- **Completed skill:** `implement`
- **Summary:** Brief description of what was implemented (plan name, phases completed, key files)

Append the agent's recommendation to your output:

```
**Recommended next step:**
→ [NEXT_STEP from agent]
  [REASON from agent]
```

If Agent tool is unavailable, refer to `references/next-step-recommendations.md` for the recommendation graph and determine the next step manually.

## Context Sync Enforcement

The PostToolUse hook on this skill monitors plan file edits. When a plan's status is changed to "Completed", the hook enforces a two-tier check:

### Tier 1 — Hard enforcement (blocks completion)
- **state.md** must reflect post-implementation state (current focus, next action)
- **progress.md** must have entries for completed work with dates

If either is missing, the hook returns an error and the agent must update them before proceeding.

### Tier 2 — Soft enforcement (warns but doesn't block)
- **architecture.md** — warns if the implementation added components, flows, or technology that aren't reflected
- **patterns.md** — warns if new patterns or conventions were established but not recorded

Soft warnings prompt the agent to evaluate Steps 7d-7e of the workflow.

## Agents

This skill uses the following agents:
- **`task-implementer`** — Executes individual plan tasks in parallel (independent tasks within a phase)
- **`context-syncer`** — Updates context files post-completion (state.md, progress.md, etc.)
- **`context-reader`** — Reads project context once for distribution to task-implementer agents

If the Agent tool is unavailable, tasks execute sequentially and context syncing happens manually.

## Agent Execution Pattern

```
context-reader agent ──────────────────┐ (produces project digest)
                                       ↓
Phase 1 — 3 independent tasks:
  task-implementer (auth middleware) ──┐
  task-implementer (login endpoint) ──┤ parallel
  task-implementer (auth tests) ──────┘
                                       ↓
                                 Collect results, handle deviations
Phase 2 — depends on Phase 1:
  task-implementer (dashboard) ────────┐
  task-implementer (nav update) ───────┘ parallel
                                       ↓
                                 Collect results
                                       ↓
context-syncer agent ──────────────────┘ (updates state.md, progress.md, etc.)
```

Each `task-implementer` agent receives:
- The specific task (Files, Action, Verify, Done criteria)
- The condensed project context digest
- Deviation rules and locked decisions from the plan

## Best Practices

- **Confirm before starting** — Never implement without user approval
- **Follow existing patterns** — Read architecture.md and patterns.md
- **Atomic progress** — Update state after each task, not just at the end
- **Deviation rules** — Auto-fix bugs, ask about architecture changes
- **Fresh context** — Use `task-implementer` agents for independent tasks to avoid context degradation
- **Persistent tracking** — Use native Tasks so progress survives session interruptions
- **Small plans** — For 1-2 tasks, `--sequential` avoids agent overhead
