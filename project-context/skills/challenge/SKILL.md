---
name: project-context:challenge
description: "Force critical evaluation of plans or code changes from adversarial perspectives. Use when Claude accepts a proposal too readily, before committing to significant decisions, when something feels off but is hard to articulate, or when stress-testing an approach. Triggers: 'challenge this', 'critique', 'stress-test', 'play devil''s advocate', 'what could go wrong', 'poke holes in'. Integrates with project-context for codebase-aware analysis."
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - Agent
---

# Challenge-It

Force critical evaluation by analyzing from multiple adversarial perspectives.

## When This Activates

- `/challenge` command
- Requests to "challenge", "critique", or "stress-test" a proposal
- When asked to "play devil's advocate" or "poke holes"
- Questions like "what could go wrong?" or "what am I missing?"
- Before committing to significant decisions

## Modes

**Context Detection (default):**
- Auto-detects whether challenging a plan or code based on conversation context
- User can override: `/challenge plan` or `/challenge code`
- User can provide focus: `/challenge "focus on security implications"`

**Depth Modes:**
- **Standard (default)** — All six perspectives, detailed analysis
- **Quick (`--quick`)** — Top 3 concerns only, faster iteration
- **Brutal (`--brutal`)** — Assume flawed + add domain-specific critics

## Integration with project-context

When `.project-context/` exists:

1. **Read architecture context** before challenging code changes
2. **Check established patterns** to validate architectural fit concerns
3. **Log challenges** to `.project-context/plans/challenge-*.md` for decision documentation
4. **Reference past decisions** that may be relevant

If `.project-context/` doesn't exist, skill works standalone.

## The Six Core Critics

| Critic | Focus | Key Questions |
|--------|-------|---------------|
| **Skeptic** | Assumptions & evidence | What are we assuming without validation? What if our premise is wrong? |
| **Pragmatist** | Cost vs value | Is this the simplest approach? What's the ongoing maintenance cost? Over-engineered? |
| **Chaos Engineer** | Failure modes | What could go wrong? Edge cases? Error handling? What breaks under load? Cross-project cascade failures? What breaks in downstream consumers if this is deployed? Upstream contract changes? |
| **Architect** | Design fit | Does this align with existing architecture? Coupling? SOLID violations? Pattern consistency? Does this break contracts declared in `dependencies.json`? Alignment with upstream APIs? |
| **Root Cause** | Problem diagnosis | Solving symptom or cause? Is the problem correctly identified? Band-aid or real fix? |
| **Future Dev** | Maintainability | Will this make sense in 6 months? Readable? Testable? What context is needed to understand? |

## Workflow

### 1. Gather Context

**Launch a `context-reader` agent** to produce a condensed project digest:
- The agent reads `.project-context/` files (architecture.md, patterns.md, brief.md, dependencies.json)
- Returns a compact digest with Tech Stack, Key Patterns, Current State, Active Dependencies
- If `.project-context/` doesn't exist, skip — the skill works standalone

**If Agent tool is unavailable**, fall back to reading files directly:
```bash
ls .project-context/*.md 2>/dev/null
```
Then read architecture.md, patterns.md, brief.md, and dependencies.json manually.

When reading files manually, read selectively based on what's being challenged:

| Challenge Target | Read |
|-----------------|------|
| Architecture/design decision | `architecture.md` + `brief.md` |
| Code implementation | `architecture.md` + `patterns.md` |
| Plan/proposal | `brief.md` + `architecture.md` |
| Performance/scaling | `architecture.md` |
| Integration/API | `architecture.md` + `dependencies.json` |

Only load `dependencies.json` + build Dependency Digest (see `references/dependency-loading.md`) when the challenge involves cross-project boundaries or integration points.

**Identify what's being challenged:**
- Recent plan discussed in conversation
- Code diff or implementation
- Architecture decision
- User-specified target

### 2. State the Challenge

Clearly identify what's being evaluated:

```
## Challenging: [the thing being challenged]

**Context:** [Brief note on what informed this analysis]
```

### 3. Analyze from All Six Perspectives

**Standard and Brutal modes — launch `critic` agents in parallel:**

Launch 6 `critic` agents simultaneously, each receiving:
- Its assigned perspective (Skeptic, Pragmatist, Chaos Engineer, Architect, Root Cause, Future Dev)
- The proposal/plan text being challenged
- The project context digest from Step 1
- Dependency info if relevant

```
Main → context-reader agent ────────────┐
     → critic agent (Skeptic) ───────────┤
     → critic agent (Pragmatist) ────────┤
     → critic agent (Chaos Engineer) ────┤  all parallel
     → critic agent (Architect) ─────────┤
     → critic agent (Root Cause) ────────┤
     → critic agent (Future Dev) ────────┘
                                         ↓
                                   Synthesize results
```

**Brutal mode:** Also launch 2-3 additional `critic` agents with domain-specific perspectives from `references/critic-frameworks.md` (Security, Performance, UX, etc. based on context).

**Quick mode (`--quick`):** Run sequentially in the main session — agent overhead isn't worth it for 3 concerns. Analyze from all perspectives but only report the top 3 concerns.

**Fallback — if Agent tool is unavailable:** Analyze from all six perspectives sequentially in the main session.

For each critic (whether agent or sequential):
- Apply the perspective to find genuine concerns
- Use project context to make concerns specific
- Reference actual patterns/code when relevant
- If no significant concerns from a perspective, state: "No critical concerns from this perspective"

**When dependencies exist:** Explicitly evaluate integration impact for each relevant critic:
- **Chaos Engineer**: Does the change cascade to downstream consumers? What breaks in `[dep]` if this is deployed? Does it depend on an upstream that could change independently?
- **Architect**: Does this change respect the contract described in dependencies.json? (`[dep]` provides `[what]` — does this still hold?)
- If any downstream consumers are affected, raise the concern as **Important** or **Critical** depending on blast radius.

### 4. Synthesize and Prioritize

Rank concerns by severity:
1. **Critical** — Blocks proceeding
2. **Important** — Should address before merge/commit
3. **Worth considering** — May defer with acknowledgment

### 5. Offer to Log (if project-context available)

Ask if user wants to log the challenge and resolution:
```
Would you like me to log this challenge to `.project-context/plans/challenge-[topic].md`?
```

### 6. Ask for Direction

End with: "Which of these should we address before proceeding?"

## Output Format

Three modes: **Standard** (all six critics, detailed), **Quick** (`--quick`, top 3 concerns only), **Brutal** (`--brutal`, assume flawed + domain-specific critics). See `references/output-formats.md` for full templates and challenge log format.

## Critical Rules

**Be genuinely adversarial.** Don't softball. If a perspective finds nothing wrong, say so — but look hard first.

**Challenge the idea, not the person.** Focus on weaknesses in the approach, not who proposed it.

**Be specific and actionable.** Each concern should point to something that can be investigated, tested, or changed. Vague concerns are useless.

**Use project context.** When available, reference actual architecture, patterns, and past decisions. "This violates our established repository pattern in `src/repos/`" is better than "This might not fit the architecture."

**Acknowledge strengths briefly.** If something is well-designed, note it in one line before diving into concerns. Don't dwell on positives — that's not why we're here.

**Prioritize ruthlessly.** Not all concerns are equal. Critical issues come first. Nice-to-haves go last or get cut in quick mode.

**Log decisions.** When project-context is available, offer to log the challenge and resolution for future reference.

## Examples & Edge Cases

For worked examples (plan challenge, quick mode, security-focused) and edge case templates (no clear target, well-designed, user disagreement), see `references/challenge-examples.md`.

## Reference

For domain-specific critics (brutal mode), see:
- `references/critic-frameworks.md` — Index with selection matrix and guidelines
- `references/domain-critics/` — Individual critic files:
  - `security.md`, `performance.md`, `ux.md`, `data.md`
  - `operations.md`, `testing.md`, `cost.md`, `api.md`, `concurrency.md`
