# Update Examples & Edge Cases

## Edge Cases

### No .project-context Directory
```
No .project-context directory found. Run `/project-context:init` first to set up context files.
```

### Uncertain Categorization
```
This could go in either:
- patterns.md (as a coding pattern)
- architecture.md (as an architectural decision)

Which makes more sense for your project?
```

### More Than 5 Candidates
```
I found 9 knowledge candidates. Here are the top 5 ranked by impact:

[Top 5 entries]

Dropped (lower impact):
- [Name] — [one-line reason it was cut]
- [Name] — [one-line reason it was cut]

Want to swap any in?
```

### Conflicting Information
```
This conflicts with existing content in [file]:

**Existing:** [Current content]
**New:** [Proposed content]

Should I:
1. Replace (knowledge evolved)
2. Skip (keep existing)
```

### User Explicitly Targets state.md or progress.md
```
Note: state.md and progress.md are auto-managed by the implement skill
and CLAUDE.md sync rules. Updating manually — proceed with your input.
```

## Examples

### Example 1: After Implementing a Feature

**User:** `/update --chat` (after completing event-driven notifications)

**Proposed Updates (3 items, ranked by impact):**

```markdown
### architecture.md
- **Event bus between Order and Notification services**
  Replaces direct REST calls; enables async processing with retry and dead-letter queue.

### patterns.md
- **Redis pub/sub for cross-service events**
  REST polling caused 3s latency in order notifications; pub/sub solved it.

- **Idempotency keys on event handlers**
  Redis pub/sub can deliver duplicates; use event ID as idempotency key to prevent double-processing.
```

### Example 2: After Debugging Session

**User:** `/update --chat` (after fixing race condition)

**Proposed Updates (2 items, ranked by impact):**

```markdown
### patterns.md
- **AbortController for stale request cancellation**
  Race condition in useEffect when deps change fast; cancel previous fetch with AbortController.

- **Prisma migrate deploy in CI**
  `migrate dev` resets the DB; always use `migrate deploy` in non-local environments.
```

### Example 3: Architecture Decision

**User:** `/update --chat` (after choosing database)

**Proposed Updates (1 item):**

```markdown
### architecture.md
- **PostgreSQL over MongoDB for primary datastore**
  Complex relational queries + ACID compliance required; Prisma ORM for type-safe access. Trade-off: rigid schema.
```
