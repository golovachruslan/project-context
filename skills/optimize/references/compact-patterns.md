# Compact Patterns

Detailed rules for compacting project context files.

## Archive Rules (progress.md)

### When to Archive

Archive completed items when:
- 3+ completed items belong to the same feature/phase
- A completed item has detailed sub-items or descriptions
- progress.md exceeds 60 lines

### Archive File Structure

Each feature/phase gets its own file under `progress/`:

```markdown
# [Feature Name] — Archive

**Completed:** YYYY-MM-DD
**Related Plan:** [link to plan if exists]

## Work Completed
- [x] Task 1 — description
- [x] Task 2 — description
- [x] Task 3 — description

## Key Deliverables
- `path/to/created-file.ts` — [purpose]
- `path/to/modified-file.ts` — [what changed]

## Decisions Made
- [Decision]: [choice] — [rationale]

## Notes
- [Any learnings or context worth preserving]
```

### Naming Convention

Archive files use hyphen-case derived from the feature/phase name:
- "User Authentication System" → `progress/user-authentication-system.md`
- "Phase 2: API Endpoints" → `progress/phase-2-api-endpoints.md`
- "PR #38 merged" → too small to archive (single item)

### What Stays in progress.md

After archiving, progress.md keeps:
- One-liner with link per archived feature: `- [Feature Name](progress/feature-name.md) (YYYY-MM-DD)`
- Recent completed items (< 7 days old) — not yet archived
- All "In Progress" and "Upcoming" items (never archive these)
- "Known Issues" section (active issues only)

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
