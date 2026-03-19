# Challenge Output Formats

## Standard Output (Default)

```markdown
## Challenging: [proposal/plan/code being challenged]

**Context:** [What informed this analysis — architecture docs, patterns, etc.]

### Skeptic
[Challenge from assumptions/evidence perspective]
- Specific concern 1
- Specific concern 2

### Pragmatist
[Challenge from cost/value perspective]
- Specific concern 1
- Specific concern 2

### Chaos Engineer
[Challenge from failure modes perspective]
- Specific concern 1
- Specific concern 2

### Architect
[Challenge from design fit perspective — informed by project-context if available]
- Specific concern 1
- Specific concern 2

### Root Cause
[Challenge from problem diagnosis perspective]
- Specific concern 1
- Specific concern 2

### Future Dev
[Challenge from maintainability perspective]
- Specific concern 1
- Specific concern 2

---

**Key Concerns (Prioritized):**
1. [Critical — what blocks proceeding]
2. [Important — should address before merge/commit]
3. [Worth considering — may defer]

**Recommendation:** [Proceed / Address concerns first / Reconsider approach]

Which of these should we address before proceeding?
```

## Quick Output (`--quick`)

```markdown
## Challenging: [thing]

**Top Concerns:**

1. **[Most critical concern]** (Perspective: [Critic])
   - Why it matters
   - Suggested action

2. **[Second concern]** (Perspective: [Critic])
   - Why it matters
   - Suggested action

3. **[Third concern]** (Perspective: [Critic])
   - Why it matters
   - Suggested action

Address these before proceeding?
```

## Brutal Output (`--brutal`)

Same as standard but:
- Add 2-3 domain-specific critics based on context (see `references/critic-frameworks.md`)
- Assume flawed: "Find what's wrong" mandate for each perspective
- Harsher language, no benefit of the doubt
- Explicitly state: "This analysis assumes the approach has flaws we need to find"

## Challenge Log Format

When logging to `.project-context/plans/challenge-*.md`:

```markdown
# Challenge: [Topic]

**Date:** YYYY-MM-DD
**Status:** Reviewing | Addressed | Accepted as-is | Rejected
**Target:** [What was challenged — plan, code, decision]

## Summary
[1-2 sentence description of what was challenged]

## Key Concerns Raised
1. **[Concern]** (Critic: [Perspective])
   - [Detail]
2. **[Concern]** (Critic: [Perspective])
   - [Detail]

## Resolution
[How concerns were addressed, or why they were accepted as-is]

## Outcome
[What was decided and why]
```
