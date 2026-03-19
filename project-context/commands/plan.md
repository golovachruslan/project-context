---
name: project-context:plan
description: Start planning a feature or project with structured requirements gathering
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Glob
  - Grep
  - Task
---

# Plan Feature or Project

## Native Plan Mode Integration

This command works best when combined with Claude Code's **native Plan Mode**:

1. **Enter Plan Mode** (`Shift+Tab` twice) to enforce read-only research before planning
2. Plan Mode restricts to research tools only (Read, Glob, Grep, Task) — no edits until the plan is approved
3. After research, use `exit_plan_mode` to present the plan for approval
4. Once approved, switch to execution mode to save the plan file

**For complex plans**, consider using the `opusplan` model (`/model opusplan`) which automatically uses Opus for planning and Sonnet for execution.

## Task Tool Usage

**Check if your available tools include `Task`.** If you have access to the Task tool, use Task subagents for:

- **Codebase exploration**: Use `subagent_type=Explore` to understand existing code structure, find relevant files, and gather technical context
- **Complex research**: Use `subagent_type=Plan` for designing implementation strategies when the feature is architecturally complex

Example usage:
```
Task(subagent_type="Explore", prompt="Find all authentication-related files and understand the current auth patterns in use")
```

Using Task subagents allows parallel exploration of multiple codebase areas, reduces context usage, and provides more thorough analysis for planning.

**If `Task` is not in your available tools**, proceed with direct Glob/Grep/Read operations as fallback.

---

Help me plan this feature or project. Use the `project-context:plan` skill to:

1. Gather requirements through clarifying questions (never assume or guess)
2. Understand technical constraints and preferences
3. Create a structured implementation plan with phases
4. Identify risks, trade-offs, and dependencies
5. Define clear success criteria

If the user has already provided some context in this conversation, incorporate it and ask about what's still unclear.

Force the use of AskUserQuestion tool to clarify any ambiguities before proposing solutions.

## Saving Plans

After creating the plan, **always ask the user** if they want to save it.

### Filename Selection

**If user provided a feature name during planning:**
- Use the provided name directly (convert to hyphen-case)
- Example: "Dark Mode Toggle" → `dark-mode-toggle.md`

**If no explicit feature name was provided:**
- Generate 2-3 descriptive filename options based on the plan content
- Ask user to choose or provide their own

```
Would you like me to save this plan?

Suggested filenames:
1. user-authentication-flow.md
2. auth-feature-implementation.md
3. login-system-plan.md

Options:
- Enter 1, 2, or 3 to use a suggested name
- Type your own filename
- Type "no" to skip saving
```

### Save Process

If the user confirms:
1. Create the `plans/` directory under `.project-context/` if it doesn't exist
2. Save the plan with the selected filename in hyphen-case

Plan verification runs automatically after saving (via skill hook).

## MANDATORY: Sync Context Files After Save

**CRITICAL: After saving the plan file, you MUST update context files before finishing. The plan command is NOT complete until this is done.**

1. **Update `.project-context/state.md`**:
   - Set current focus to the new plan
   - Set next action to implement the plan
   - Reference the plan file path

2. **Update `.project-context/progress.md`**:
   - Add an entry with today's date referencing the new plan
   - Place it in the appropriate section (Upcoming/In Progress)

3. **Evaluate `.project-context/architecture.md`** (if applicable):
   - If the plan introduces new components, changes system flows, or adds technology, update `architecture.md`
   - Add a **Key Decisions** entry with today's date for significant architectural choices made during planning
   - Update the Mermaid diagram if new components or flows are planned

4. **Evaluate `.project-context/patterns.md`** (if applicable):
   - If planning established new conventions or pattern decisions (e.g., "we'll use repository pattern for data access"), add them to `patterns.md`
   - Skip if no new patterns were decided during planning

**Do NOT present a final summary or consider the command finished until all applicable files are updated.** The PostToolUse hook will verify this.
