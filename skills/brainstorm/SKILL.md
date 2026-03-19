---
name: project-context:brainstorm
description: "Use when users want to brainstorm, discuss requirements, or explore ideas BEFORE planning. Triggers: 'let's discuss', 'brainstorm', 'think through', 'what should we consider', 'before we plan'. Captures decisions as locked constraints that flow into planning."
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Glob
  - Grep
  - Task
---

# Brainstorm & Discuss Skill

Separate brainstorming from planning. This skill captures decisions and resolves gray areas BEFORE creating a plan. Output is locked decisions that constrain the planner.

## Core Principle

**Clarify HOW to implement, never expand WHAT to implement.** The discuss phase resolves ambiguity within existing scope — it does not add new scope.

## Workflow

### 1. Read Existing Context

Check for project context to ask informed questions:

```bash
ls .project-context/*.md 2>/dev/null
```

If exists, read selectively:
- **Always:** `brief.md` (project scope/goals — essential for scoping discussion)
- **If feature involves architecture:** `architecture.md` (tech stack, existing design)
- **Defer:** `patterns.md` — only read if discussion reveals pattern-related gray areas

**Dependencies:** Only check `dependencies.json` if the feature description mentions integration, APIs, cross-project, or shared services. If it does, build a Dependency Digest (see `references/dependency-loading.md`) for Step 3.

### 2. Understand the Feature

Ask the user to describe what they want to build. Listen for:
- The core problem being solved
- Who benefits
- Initial ideas about approach

### 3. Identify Gray Areas

Based on the feature description and project context, identify 3-5 domain-specific gray areas — things that could go multiple ways and would affect the plan.

**Adapt questions by feature type:**

| Feature Type | Gray Areas to Surface |
|-------------|----------------------|
| UI/Visual | Layout, density, interactions, responsive behavior, accessibility |
| API/Backend | Response format, error handling, auth model, rate limiting, versioning |
| Data/Storage | Schema design, consistency, retention, migration strategy |
| Integration | Sync vs async, error recovery, data mapping, auth flow |
| Performance | Caching strategy, trade-offs, acceptable latency, fallback behavior |
| Cross-project / Dep boundary | API contract changes, coordination timing, breaking changes, shared type updates, version sync |

**When dependencies exist:** Compare the feature description against each dep's `what` field. If there's overlap (e.g., the feature involves "auth tokens" and an upstream dep provides "Auth API types, JWT schemas"), flag an integration gray area:
- Upstream dep: "This touches [what] provided by `[project]` — do we need to coordinate changes upstream first?"
- Downstream dep: "Downstream `[project]` consumes [what] from us — will this be a breaking change for them?"

If the relevant dep has cached context, load its `brief.md` + `architecture.md` to ask more specific questions (see `dependency-loading.md` Step 3 for loading rules).

**Present gray areas clearly:**
```
I've identified [N] areas where the approach could go multiple ways:

1. **[Gray Area Name]**: [Brief description of the ambiguity]
   - Option A: [approach] — [pros]
   - Option B: [approach] — [pros]

2. **[Gray Area Name]**: [Brief description]
   ...

Let's discuss each one to lock in decisions before planning.
```

### 4. Deep-Dive Each Gray Area

For each gray area, ask 2-4 focused questions:
- What's the preferred approach and why?
- Are there constraints that rule out options?
- What trade-offs are acceptable?
- How does this interact with existing architecture?

**Keep rounds short** — 2-3 questions per gray area, not 10 questions at once.

### 5. Lock Decisions

After resolving each gray area, summarize the locked decision:

```
**Locked Decision:** [Area]
- **Choice:** [What was decided]
- **Rationale:** [Why]
- **Trade-offs accepted:** [What we're giving up]
```

### 6. Produce Decisions Summary

After all gray areas are resolved, present the complete decisions summary:

```markdown
## Decisions Summary for [Feature Name]

### Locked Decisions

1. **[Decision Area]**: [Choice] — [Rationale]
2. **[Decision Area]**: [Choice] — [Rationale]
3. **[Decision Area]**: [Choice] — [Rationale]

### Constraints for Planning
- [Constraint derived from decisions]
- [Constraint derived from decisions]

### Out of Scope (confirmed)
- [Items explicitly excluded during discussion]
```

### 7. Save or Hand Off

Ask the user:
```
These decisions are ready to flow into planning.

Options:
1. Append decisions to a plan file (I'll create the plan next)
2. Save decisions separately for later
3. Continue directly to planning now (/project-context:plan)
```

If saving, append to the plan file in `.project-context/plans/` or create a new one.

## Key Principles

1. **Never expand scope** — Discuss HOW, not WHETHER to add more
2. **Lock decisions explicitly** — Vague agreements cause plan drift
3. **Adapt to domain** — UI features need different questions than API features
4. **Keep rounds short** — 2-4 questions per gray area, not a wall of text
5. **Reference existing context** — Show you've read the architecture/patterns
6. **Decisions flow downstream** — The planner MUST honor locked decisions

## Integration with Planning

The project-context:plan skill should:
1. Check for locked decisions before creating a plan
2. Include a "Decisions" section in the plan referencing these
3. Never override locked decisions without re-discussing
