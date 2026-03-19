---
name: project-context:plan-verification
description: "Use to verify plan quality. Triggers: 'verify this plan', 'check the plan', 'validate plan'. Checks completeness, actionability, scope clarity, and risk coverage."
allowed-tools:
  - Read
  - Glob
---

# Plan Verification Skill

Validate plans to ensure they are complete, actionable, and ready for implementation.

## When to Use

- **On demand** when user asks to verify/validate a plan
- **Before implementation** to confirm plan readiness
- **Automatically** via project-context:plan skill hook after saving a plan

## Verification Criteria

### Required Sections

| Section | Purpose |
|---------|---------|
| Overview | What and why |
| Requirements | Functional/non-functional needs |
| Technical Approach | How it will be built |
| Implementation Phases | Phased tasks with checkboxes |
| Success Criteria | How to measure done |

### Quality Checks

1. **Completeness** - No empty sections, no `[TODO]`/`[TBD]` placeholders
2. **Actionability** - Tasks have checkboxes `- [ ]`, are specific not vague
3. **Scope clarity** - Has in-scope/out-of-scope boundaries
4. **Risk awareness** - At least one risk with mitigation (or explicit "no risks")
5. **Measurability** - Success criteria are specific, not vague
6. **Dependency awareness** - If `.project-context/dependencies.json` exists and plan tasks involve concepts matching a dependency's `what` field, verify the plan includes cross-project coordination: either a "Cross-Project Impact" section or explicit tasks like "Update shared types", "Verify downstream builds". Flag as Warning if absent.

### Red Flags

- Vague tasks: "do the thing", "implement stuff", "fix issues"
- Vague success: "works well", "users are happy", "looks good"
- Unfilled placeholders: `[TODO]`, `[TBD]`, `[placeholder]`, `XXX`
- Plan modifies shared API/types/utilities consumed by a downstream dependency but includes no coordination step

## Workflow

1. **Locate the plan** - Use provided path or find most recent:
   ```bash
   ls -t .project-context/plans/*.md | head -1
   ```

2. **Read and analyze** the plan content. Also check `dependencies.json` if present — needed for Quality Check #6.

3. **Report findings**:
   - PASS: Plan is ready for implementation
   - ISSUES: List specific problems with suggestions to fix

4. **Offer to help fix** any issues found

## Example Output

```
Plan Verification: PASSED
✓ All required sections present
✓ 12 actionable tasks defined
✓ 2 risks identified with mitigations
✓ Clear success criteria

Plan is ready for implementation.
```

Or:

```
Plan Verification: NEEDS ATTENTION

Issues found:
1. Missing section: Success Criteria
2. Phase 2 has no tasks defined
3. Placeholder found: [TBD] in Technical Approach

Would you like me to help fix these?
```
