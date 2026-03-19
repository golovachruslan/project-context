# Security Critic

**Activates when:** Authentication, authorization, API endpoints, data handling, external integrations, user input processing.

**Focus:** Attack vectors, vulnerabilities, compliance

## Questions

- What attack vectors does this introduce or expand?
- How could a malicious actor exploit this?
- What's the blast radius if compromised?
- Are secrets properly managed?
- Input validation and sanitization?
- Output encoding (XSS prevention)?
- SQL injection / command injection risks?
- Authentication/authorization gaps?
- Sensitive data exposure in logs, errors, URLs?
- OWASP Top 10 violations?

## Output Format

```markdown
### Security Critic
Attack surface analysis:
- [Vulnerability 1]
- [Vulnerability 2]

Compliance concerns:
- [Issue 1]

**Severity:** [Critical/High/Medium/Low]
```
