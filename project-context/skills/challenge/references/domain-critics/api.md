# API Critic

**Activates when:** API design, endpoint changes, contract changes, versioning, integrations.

**Focus:** Contract stability, usability, compatibility

## Questions

- Is this a breaking change?
- Versioning strategy?
- Backward compatibility maintained?
- API contract documented?
- Error responses consistent and useful?
- Rate limiting considered?
- Authentication/authorization correct?
- Idempotency for unsafe operations?
- Pagination for list endpoints?
- Response size and performance?
- SDK/client impact?

## Output Format

```markdown
### API Critic
Contract concerns:
- [Issue 1]

Compatibility risks:
- [Risk]

Consumer impact:
- [Impact]

**API stability risk:** [High/Medium/Low]
```
