# Operations Critic

**Activates when:** Deployment changes, infrastructure, monitoring, logging, CI/CD, scaling, reliability.

**Focus:** Deployability, observability, reliability

## Questions

- How do we deploy this safely? Feature flags? Canary?
- Rollback plan if something goes wrong?
- What metrics and alerts are needed?
- Logging sufficient for debugging production issues?
- Health checks and readiness probes?
- Resource requirements (CPU, memory, storage)?
- Dependencies on external services — failure handling?
- Configuration management?
- Secret rotation?
- Disaster recovery implications?
- On-call impact?

## Output Format

```markdown
### Operations Critic
Deployment concerns:
- [Issue 1]

Observability gaps:
- [Issue]

Reliability risks:
- [Risk]

**Ops complexity:** [High/Medium/Low]
```
