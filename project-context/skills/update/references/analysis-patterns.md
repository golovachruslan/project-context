# Analysis Patterns

Patterns for extracting reusable knowledge from conversations. Focused on what passes the "new teammate" test.

## Extraction Decision Tree

```
Is this knowledge...
├─ Reusable across multiple situations?
│  ├─ Tech choice / architecture change?    → architecture.md
│  ├─ Coding pattern / convention?          → patterns.md
│  ├─ Gotcha / anti-pattern?               → patterns.md
│  ├─ Scope / goals change?                → brief.md
│  └─ Unclear / spans multiple?            → Ask user
├─ Status update (completed/in-progress)?  → SKIP (handled by implement + CLAUDE.md sync)
└─ One-off / trivial?                      → SKIP
```

## Signal Recognition

### Decision Signals
- "We decided to...", "Going with X because..."
- "Chose X over Y due to...", "The trade-off is..."
- **Extract to:** architecture.md (tech decisions) or brief.md (scope decisions)

### Pattern Signals
- "This pattern works well...", "Consistently using..."
- "Standard approach is...", "Following convention of..."
- **Extract to:** patterns.md

### Gotcha Signals
- "The bug was caused by...", "Watch out for..."
- "This almost worked but...", "Turns out..."
- **Extract to:** patterns.md (as anti-patterns with solutions)

### Architecture Signals
- "Added a new service for...", "Changed the flow to..."
- "Introduced X for...", "Replaced Y with Z"
- **Extract to:** architecture.md

### Skip Signals (do NOT extract)
- "Fixed the typo", "Added missing import"
- "Completed feature X", "Now working on Y"
- "Updated tests", "Refactored for readability"

## Entry Format

Each entry uses the terse bullet format:

```markdown
- **Bold name describing the knowledge**
  One line of context: when/why it applies, what it prevents.
```

**Good entries:**
| Entry | Why it's good |
|-------|--------------|
| **Redis pub/sub for cross-service events** / REST polling caused 3s latency in order notifications. | Specific, reusable, includes the "why" |
| **Prisma migrate deploy in CI** / `migrate dev` resets DB; always use `migrate deploy` in non-local environments. | Gotcha that prevents real damage |
| **Use composition over config props for UI** / `<Button><Icon/>Save</Button>` not `<Button icon='save' label='Save'/>` | Convention with concrete example |

**Bad entries (skip these):**
| Entry | Why it's bad |
|-------|-------------|
| "Added semicolon to line 42" | Trivial, not reusable |
| "Made the code better" | Vague, not actionable |
| "Completed auth system" | Status update, not knowledge |
| "Use Redux for state" | No context — when/why? |

## Quality Checklist

Before including a candidate:
- [ ] **Reusable** — applies beyond this one instance?
- [ ] **Specific** — includes concrete context (when/why)?
- [ ] **Not redundant** — not already in context files?
- [ ] **"New teammate" test** — would you tell them about this?
