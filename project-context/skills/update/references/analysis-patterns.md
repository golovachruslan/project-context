# Analysis Patterns

Patterns for extracting learnings from conversations, organized by conversation type.

## Extraction Decision Tree

```
Is this learning about...
├─ Project goals/scope/vision?         → brief.md
├─ Tech choices/components/flows?      → architecture.md
├─ Coding patterns/conventions?        → patterns.md
├─ Work completed/in-progress?         → progress.md
├─ Current position/blockers/focus?    → state.md
└─ Unclear/spans multiple?             → Ask user
```

## Signal Recognition

### Learning Signals
- "I learned that...", "It turns out...", "The solution was..."
- "This works better than...", "We should always/never..."
- **Extract to:** patterns.md

### Decision Signals
- "We decided to...", "Going with X because..."
- "Chose X over Y due to...", "The trade-off is..."
- **Extract to:** architecture.md (tech decisions) or brief.md (scope decisions)

### Pattern Signals
- "This pattern works well...", "Consistently using..."
- "Standard approach is...", "Following convention of..."
- **Extract to:** patterns.md

### Error Signals
- "The bug was caused by...", "Fixed by...", "Watch out for..."
- **Extract to:** patterns.md (as anti-patterns with solutions)

### Progress Signals
- "Completed...", "Finished implementing...", "Now working on..."
- **Extract to:** progress.md and state.md

## Pattern Types

### Feature Implementation → Extract:
- **patterns.md**: Code patterns, libraries used, design patterns applied
- **progress.md**: Feature completion, dependencies
- **architecture.md**: New components, integration points, data flow changes

### Debugging Session → Extract:
- **patterns.md**: Root causes, solutions, anti-patterns, preventive measures
- **progress.md**: Bug status, remaining issues

### Architecture Decision → Extract:
- **architecture.md**: Tech choices with rationale, alternatives considered
- **brief.md**: Scope changes if scope-impacting

### Refactoring → Extract:
- **patterns.md**: New patterns, code organization principles
- **progress.md**: Tech debt addressed, quality improvements

### Configuration/Setup → Extract:
- **architecture.md**: Build tools, CI/CD, third-party integrations
- **patterns.md**: Configuration patterns, environment management

## Quality Checklist

Before proposing an update, verify:
- **Specific**: Includes concrete examples/code?
- **Actionable**: Can be applied in future work?
- **Contextual**: Explains when/why it applies?
- **Non-redundant**: Doesn't duplicate existing content?
- **Valuable**: Worth preserving for future reference?
- **Right level of detail**: Not too granular ("added semicolon") or too vague ("made code better")

## Common Mistakes

| Bad | Good |
|-----|------|
| "Added semicolon to line 42" | "Established convention: Use semicolons consistently (enforced by ESLint)" |
| "Made the code better" | "Refactored error handling to use centralized error boundary" |
| "Use Redux for state" | "Use Redux for state management. Rationale: complex shared state, need time-travel debugging, team familiar with Redux" |
| "Use composition pattern" | "Use composition pattern: `<Button><Icon name='save'/>Save</Button>` instead of `<Button icon='save' label='Save'/>`" |
