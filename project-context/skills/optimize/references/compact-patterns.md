# Compact Patterns

Detailed rules for compacting project context files.

## Per-Feature Progress Files

### Structure

Each feature gets its own `progress/<feature-name>.md` file, created when the plan is saved (not retroactively). The main `progress.md` is a lightweight index.

### Per-Feature File Template

```markdown
# [Feature Name] — Progress

**Status:** Planning | In Progress | Completed
**Plan:** [plans/feature-name.md](../plans/feature-name.md)
**Started:** YYYY-MM-DD
**Completed:** YYYY-MM-DD (when done)

## Completed
- [x] Task 1 — description (YYYY-MM-DD)
- [x] Task 2 — description (YYYY-MM-DD)

## In Progress
- [ ] **Task 3** — [status]

## Upcoming
- [ ] Task 4

## Key Deliverables
- `path/to/created-file.ts` — [purpose]

## Decisions Made
- [Decision]: [choice] — [rationale]

## Notes
- [Learnings, blockers resolved, etc.]
```

### Naming Convention

Per-feature files use hyphen-case derived from the feature/plan name:
- "User Authentication System" → `progress/user-authentication-system.md`
- "Phase 2: API Endpoints" → `progress/phase-2-api-endpoints.md`

### What Stays in progress.md (index)

The index contains only:
- **Active Features**: one-liner + link per in-progress feature
- **Completed Features**: one-liner + link + completion date per done feature
- **Known Issues**: active cross-feature issues only

### Legacy Migration

If `progress.md` has inline completed items (pre-per-feature structure):
- Group by feature/phase
- Extract into `progress/<feature-name>.md` files
- Replace inline items with one-liner links in the index
- Only migrate groups of 3+ items; single items can stay inline

## Pruning Rules (state.md)

### Remove
- Resolved blockers (blocker text contains "resolved", "fixed", or is crossed out)
- Completed decisions from "Decisions Pending" (moved to architecture.md or patterns.md)
- Old session info (keep only the most recent session)
- "Recently Completed" items older than 7 days

### Keep
- All active blockers
- All pending decisions
- Current position and focus
- Next action

### state.md Target Size
state.md should stay under 50 lines. If it exceeds this after pruning, escalate to user.

## Summarization Rules

### When to Summarize
- A section has 5+ lines of prose describing a single concept
- Bullet points repeat similar information with slight variations
- Explanations include obvious context ("As we discussed earlier...")

### How to Summarize
1. Extract the core fact or decision
2. Remove filler words and obvious context
3. Preserve specifics: names, versions, dates, file paths
4. Keep "why" alongside "what"

### Examples

**Before:**
```
We decided to use PostgreSQL for the database because it has good support for JSON columns
which we need for storing user preferences, and it also has great performance for the kind
of queries we'll be running. MySQL was considered but rejected because of its weaker JSON
support. MongoDB was also considered but we wanted ACID guarantees.
```

**After:**
```
Database: PostgreSQL — needed JSON column support for user preferences + ACID guarantees. Rejected MySQL (weaker JSON) and MongoDB (no ACID).
```

### Never Summarize
- Mermaid diagrams (modify diagram content, not format)
- Code examples in patterns.md
- File paths and version numbers
- Decision rationale (compress wording but keep the reasoning)
