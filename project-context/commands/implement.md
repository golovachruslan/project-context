---
name: project-context:implement
description: Implement a plan using multi-agent execution with deviation rules. Provide a plan file path or reference a plan from the conversation.
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

**Launch a `context-reader` agent** to produce a condensed project digest covering architecture, patterns, state, and dependencies.

The digest is passed to each `task-implementer` agent so they don't re-read the same files.

**If Agent tool is unavailable**, read directly:
- `.project-context/architecture.md` — Follow existing patterns
- `.project-context/patterns.md` — Respect conventions
- `.project-context/state.md` — Current position
- `.project-context/dependencies.json` — Cross-project boundaries (if present)

If `dependencies.json` exists, the digest should include dependency info for detecting when tasks touch integration boundaries.

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

**CRITICAL: This step is NOT optional. The implement command is NOT complete until all context files are updated. Do NOT present the final summary until this step is fully done.**

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
