---
name: project-context:plan
description: "Use when users request feature planning, project planning, or implementation planning. Triggers: 'plan this feature', 'help me plan', 'how should I implement'. Creates structured executable plans from locked decisions. Run /project-context:brainstorm first to brainstorm."
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Glob
  - Grep
hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: agent
          prompt: |
            Check if the file just written is a plan in .project-context/plans/.
            Input: $ARGUMENTS

            If it's NOT a plan file, return {"ok": true}.

            If it IS a plan file:
            1. Use the project-context:plan-verification skill to validate plan structure.
            2. Then check if .project-context/state.md and .project-context/progress.md
               have been updated to reference this plan. Read both files and look for
               a reference to the plan filename.
               - If BOTH files reference the plan → return {"ok": true}
               - If either file is MISSING the plan reference → return {"ok": false,
                 "reason": "Context files not synced. You MUST update state.md (set current focus and next action to reference the plan) and progress.md (add plan entry with date) before finishing. This is mandatory per Step 7 of the planning workflow."}
            Return {"ok": true} if everything passes, or {"ok": false, "reason": "..."} if not.
          statusMessage: "Validating plan and context sync..."
          timeout: 90
---

# Feature & Project Planning Skill

Create structured, executable implementation plans. **Plans should flow from locked decisions** produced by the discuss skill.

## Core Principles

1. **Ask, don't assume** — Use AskUserQuestion when information is missing
2. **Plans are executable prompts** — Every task must have: Files, Action, Verify, Done
3. **Context-first** — Always read project context before planning
4. **Decisions before details** — Check for locked decisions from /project-context:brainstorm
5. **Leverage native features** — Use Plan Mode for research, native Tasks for tracking

## Planning Workflow

### 1. Read Project Context

**Always do this first.** Launch a `context-reader` agent to produce a condensed project digest, or read files directly if Agent tool is unavailable:

```bash
ls .project-context/*.md 2>/dev/null
```

If context exists, read selectively:
- **Always:** `brief.md` (goals/scope) + `state.md` (current position, existing plans)
- **If feature involves architecture:** `architecture.md` (tech stack, system design)
- **If feature involves coding patterns:** `patterns.md` (established conventions)
- **If cross-project:** `dependencies.json` → build Dependency Digest (see `references/dependency-loading.md`)
- **Check:** `plans/*.md` for existing discussions/decisions on this topic

Skip files not relevant to the feature being planned. You'll read `state.md` and `progress.md` again in Step 7, but their content from Step 1 is already in conversation context — use Edit directly without re-reading.

Use context to ask **informed** questions (reference specific tech, patterns, decisions).

### 2. Check for Locked Decisions

Look for decisions from a prior `/project-context:brainstorm` session:
- In conversation history
- In plan files with a "Decisions" section
- In `state.md` referencing a discuss session

If locked decisions exist, honor them. Do not re-ask resolved questions.

### 3. Gather Missing Requirements

If no prior discuss session, ask clarifying questions (max 4-5 per round):

**Good format:**
```
I need to understand [aspect] to plan this effectively.

1. [Specific question]?
2. [Specific question]?
3. [Specific question]?

This will help me [why it matters].
```

Refer to `references/question-patterns.md` for scenario-specific patterns.

### 4. Create Executable Plan

Use templates from `references/planning-templates.md`. Key structure:

```markdown
# [Feature Name] Plan

**Status:** Planning
**Created:** YYYY-MM-DD

## Overview
**Problem:** [What this solves]
**Solution:** [High-level approach]

## Decisions
[From discuss phase or gathered during planning]

## Implementation Phases

### Phase 1: [Name]
**Goal:** [What this achieves]

#### Task 1: [Name]
- **Files:** [exact paths]
- **Action:** [Concrete steps — what to build, which patterns to follow]
- **Verify:** [Command or check to confirm it works]
- **Done when:** [Observable acceptance criteria from user's perspective]

#### Task 2: [Name]
[Same structure]

## Cross-Project Impact
*(Include only when plan touches a dependency boundary — omit if no dependencies)*
| Dependency | Direction | What's Affected | Action Needed |
|---|---|---|---|
| [project] | upstream/downstream | [from `what` field] | [coordinate / update / verify] |

## Risks & Mitigation
[Key risks with strategies]

## Next Steps
[What to do after planning]
```

**Dependency coordination tasks** — when a plan task crosses a boundary from `dependencies.json`:
- Add an explicit task: "Update shared types in `[dep path]`" or "Verify `[downstream]` still builds after API change"
- Mark coordination tasks as dependencies of implementation tasks in the DAG
- For git link deps with stale cache: add "Fetch latest `[dep]` context" as a prerequisite task

**Task rules:**
- 2-4 tasks per phase (keeps context fresh if using subagents or Agent Teams)
- Specify exact file paths
- Verification must be executable (a command, URL check, or test)
- "Done when" describes observable behavior, not code details
- Mark task dependencies explicitly — these map to native Tasks DAG dependencies

### 5. Register in Native Tasks

After creating the plan, **register tasks in Claude Code's native task system** (`Ctrl+T` to view):
- Create task entries with proper dependency chains matching the plan phases
- Set `CLAUDE_CODE_TASK_LIST_ID=plan-[feature-name]` for cross-session persistence
- Tasks persist on disk — safe to `/clear` or `/compact` without losing the plan roadmap
- When Agent Teams are used for implementation, teammates share the same task list

**Fallback:** If native Tasks are not available, use TodoWrite for in-session tracking.

### 6. Save Plan

**Always ask the user** if they want to save:
- Propose hyphen-case filename from feature name
- Save to `.project-context/plans/[name].md`

Plan verification runs automatically after saving (via skill hook).

### 7. MANDATORY: Sync Context Files

**CRITICAL: This step is NOT optional. The plan command is NOT complete until context files are updated.**

After saving the plan file, you MUST update these `.project-context/` files before presenting any summary:

**Context files were already read in Step 1 — do NOT re-read them. Use Edit directly.**

#### 7a. Update `state.md`
Use Edit to update **Current Focus**, **Next Action**, and **Active Plan** to reference the new plan.

#### 7b. Update `progress.md`
Use Edit to add a dated plan entry to the **Upcoming** or **In Progress** section.

#### 7c. Evaluate `architecture.md` (only if plan introduces new components, flows, or tech)
If applicable, use Edit to add planned components to diagrams and a **Key Decisions** entry. If architecture.md was not read in Step 1, read it now. Skip otherwise.

#### 7d. Evaluate `patterns.md` (only if plan established new conventions)
If applicable, use Edit to add new patterns. If patterns.md was not read in Step 1, read it now. Skip otherwise.

#### 7e. Verify
Confirm state.md and progress.md reference the plan. The PostToolUse hook enforces this.

**Alternative:** Launch a `context-syncer` agent for Steps 7a-7d to update all files in one pass. The agent receives the plan summary and handles state.md, progress.md, architecture.md, and patterns.md updates. If Agent tool is unavailable, perform each update manually as described above.

**Only after completing Steps 7a-7e should you present the final summary.**

## Reference

- `references/planning-templates.md` — Full plan templates
- `references/question-patterns.md` — Question frameworks by scenario
