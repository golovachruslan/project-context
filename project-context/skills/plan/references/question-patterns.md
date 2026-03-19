# Question Patterns for Planning

Frameworks for gathering requirements via AskUserQuestion. Choose the right pattern based on planning type.

## Core Framework: Funnel Approach

1. **Vision** — What are we building and why?
2. **Requirements** — What must it do?
3. **Constraints** — What limits exist?
4. **Details** — Specific implementation preferences

Always ask in rounds of 3-5 questions. Explain why you're asking. Build on previous answers.

## Scenario-Specific Patterns

### New Feature Planning

**Round 1 — Discovery:**
- What problem does this solve, and for whom?
- What does success look like? How will we measure it?
- What's the scope for v1? Must-have vs nice-to-have?
- Any existing solutions you like/dislike?

**Round 2 — Technical (adapt based on Round 1):**
- Performance expectations (response time, load)?
- Integration with existing systems?
- Data storage and privacy requirements?
- Platform/browser support needs?

### Project Planning

**Round 1 — Vision:**
- What's the core problem and who has it?
- What outcomes define success?
- Timeline and hard deadlines?
- Team size, skills, and budget?

**Round 2 — Scope:**
- Core features for MVP?
- What's explicitly out of scope?
- Priority: speed to market vs completeness?
- Must-haves vs nice-to-haves?

### Architecture/System Design

- Scale expectations (users, data volume, growth)?
- Performance requirements (latency, throughput)?
- Availability/consistency requirements?
- Existing stack and team expertise?
- Cloud provider / infrastructure constraints?
- Integration points with other systems?

### Refactoring

- What's not working well? Impact and frequency?
- Previous refactoring attempts — what prevented success?
- Risk tolerance and acceptable downtime?
- Backward compatibility requirements?
- Existing test coverage?

### Performance Optimization

- What's slow? Specific operations, consistent or intermittent?
- Current metrics vs target metrics?
- Scope of allowed changes (architecture, schema, infrastructure)?
- Acceptable trade-offs (speed vs consistency, cost vs performance)?

## Question Strategies

### When Requirements Are Vague
Offer concrete options:
```
To clarify scope, here are common approaches:
- Option A: [Simple version]
- Option B: [Medium version]
- Option C: [Complex version]
Which aligns closest, or something else?
```

### When User Is Uncertain
Provide decision framework:
```
If [condition A], then [approach A] works better because [reason].
If [condition B], then [approach B] works better because [reason].
Which condition applies?
```

### When Trade-offs Exist
Make them explicit:
```
**Option A** (e.g., client-side rendering):
- Pros: faster navigation, better UX
- Cons: slower initial load, SEO challenges

**Option B** (e.g., server-side rendering):
- Pros: faster initial load, better SEO
- Cons: more server load, complex caching

Which aligns with your priorities?
```

### When Scope Needs Bounding
Suggest phased MVP:
```
Phase 1 (MVP): [Core features with immediate value]
Phase 2: [Enhancements once validated]
Phase 3: [Advanced features]
Does this phasing make sense?
```

## Anti-Patterns

- **Too vague**: "What do you want?" → Ask specific, concrete questions
- **Leading**: "You want React, right?" → Offer options without bias
- **Too many**: 15 questions at once → Max 4-5 per round
- **Jargon to non-technical users** → Plain language with context
- **Answerable from docs**: "What framework?" → Read package.json first
- **Not explaining why** → Always say what the answer helps you decide

## Principles

1. Start broad, then narrow
2. Ask in rounds (3-5 questions each)
3. Explain why you're asking
4. Offer options when helpful
5. Build on previous answers
6. Make trade-offs explicit
7. Know when to stop — enough to start, not perfect knowledge
8. Summarize understanding before planning
