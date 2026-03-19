# Planning Templates

Use these as starting points. Remove irrelevant sections, add domain-specific ones.

## Feature Plan Template

```markdown
# [Feature Name] Plan

**Status:** Planning | In Progress | Completed
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD

## Overview
**Problem:** [What problem does this solve?]
**Solution:** [High-level approach]
**Success Metrics:** [How we'll measure success]

## Requirements

### Functional
1. **[Requirement]** — [User story or description]
   - [ ] Acceptance criterion 1
   - [ ] Acceptance criterion 2

### Non-functional
- **Performance:** [Expectations]
- **Security:** [Requirements]
- **Scalability:** [Needs]

### Out of Scope
- [Explicitly deferred items]

## Decisions

Locked decisions from brainstorming (from /project-context:brainstorm):

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [What] | [Chosen option] | [Why] |

## Technical Design

### Architecture
[Mermaid diagram or description]

### Key Components
1. **[Component]**
   - Purpose: [What it does]
   - Files: [Exact paths]
   - Dependencies: [What it needs]

## Implementation Phases

### Phase 1: [Name] (MVP)
**Goal:** [What this achieves]

#### Task 1: [Name]
- **Files:** [exact paths]
- **Action:** [Concrete implementation steps]
- **Verify:** [Command or check to confirm it works]
- **Done when:** [Observable acceptance criteria]

#### Task 2: [Name]
[Same structure]

### Phase 2: [Name]
[Same structure]

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Description] | High/Med/Low | High/Med/Low | [Strategy] |

## Dependencies
- [External/internal dependencies]

## Next Steps
1. [Immediate action]
2. [Following action]
```

## Quick Plan Template

For smaller features or spikes:

```markdown
# [Feature] Quick Plan

**Goal:** [One sentence]

## What & Why
- **What:** [Brief description]
- **Why:** [Problem it solves]

## Tasks
1. **[Task name]**
   - Files: [paths]
   - Action: [what to do]
   - Verify: [how to check]
   - Done: [acceptance criteria]

2. **[Task name]**
   [Same structure]

## Risks
- [Risk]: [Mitigation]
```

## Choosing Templates

- **Feature Plan**: Single feature (1-4 weeks scope)
- **Quick Plan**: Small feature, spike, POC (<1 week)
- For larger projects, use Feature Plan template but add a Roadmap section with multiple phases

## Template Principles

- Fill only relevant sections — don't pad empty ones
- Tasks must be executable: files, action, verify, done
- Keep plans as prompts, not documentation
- Update plans as you learn — they're living documents
