# Domain-Specific Critic Frameworks

Extended perspectives for `--brutal` mode. These critics activate based on the context being challenged.

## When to Add Domain Critics

In brutal mode, add 2-3 domain-specific critics based on:
- The nature of what's being challenged
- Project context (tech stack, domain, constraints)
- User-specified focus areas

## Available Domain Critics

| Critic | File | Focus |
|--------|------|-------|
| Security | [security.md](domain-critics/security.md) | Attack vectors, vulnerabilities, compliance |
| Performance | [performance.md](domain-critics/performance.md) | Speed, resource usage, scalability |
| UX | [ux.md](domain-critics/ux.md) | User experience, accessibility, clarity |
| Data | [data.md](domain-critics/data.md) | Data integrity, consistency, compliance |
| Operations | [operations.md](domain-critics/operations.md) | Deployability, observability, reliability |
| Testing | [testing.md](domain-critics/testing.md) | Testability, coverage, confidence |
| Cost | [cost.md](domain-critics/cost.md) | Financial impact, resource efficiency |
| API | [api.md](domain-critics/api.md) | Contract stability, usability, compatibility |
| Concurrency | [concurrency.md](domain-critics/concurrency.md) | Race conditions, deadlocks, consistency |

## Selection Matrix

Use this matrix to select domain critics based on challenge context:

| Challenge Type | Primary Domain Critics |
|----------------|------------------------|
| API endpoint | Security, API, Performance |
| Database schema | Data, Performance, Operations |
| UI feature | UX, Testing, Performance |
| Authentication | Security, Data, Testing |
| Infrastructure | Operations, Cost, Security |
| Integration | API, Security, Operations |
| Data pipeline | Data, Performance, Cost |
| Refactoring | Testing, Performance, Future Dev |
| Scaling | Performance, Cost, Operations |
| User flow | UX, Testing, Accessibility |

## Brutal Mode Guidelines

When using `--brutal` mode:

1. **Assume flawed** — Start with the premise that something is wrong
2. **Add 2-3 domain critics** — Select based on context using the matrix above
3. **No benefit of the doubt** — If something could go wrong, it will
4. **Specific failures** — Describe exactly how it will break
5. **Worst-case scenarios** — Consider Murphy's Law
6. **Question everything** — Even "obvious" decisions

**Brutal mode opener:**
```markdown
## Challenging: [target]

**Mode:** Brutal — This analysis assumes the approach has flaws we need to find.

**Domain critics activated:** [Critic 1], [Critic 2], [Critic 3]

[Standard six critics with harsher lens...]

[Domain-specific critics...]
```
