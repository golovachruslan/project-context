---
name: project-context:challenge
description: Challenge a plan or code change from adversarial perspectives to find weaknesses
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - Agent
---

# Challenge Plan or Code

Force critical evaluation of the current plan or code change using the `project-context:challenge` skill.

## Modes

Parse the arguments to determine mode:

- **No arguments** — Standard mode, auto-detect target from conversation
- **`plan`** — Challenge a plan specifically
- **`code`** — Challenge code/implementation specifically
- **`--quick`** — Quick mode, top 3 concerns only, sequential (no agents)
- **`--brutal`** — Brutal mode, assume flawed + add domain critics
- **Quoted text** — Focus on specific aspect (e.g., `"focus on security"`)

Arguments can be combined: `/challenge code --quick`, `/challenge --brutal "security focus"`

## Execution Strategy

**Standard and Brutal modes** use `critic` agents for parallel analysis:
1. Launch a `context-reader` agent to produce a project digest
2. Launch 6 `critic` agents in parallel (one per perspective)
3. In brutal mode, launch 2-3 additional domain-specific `critic` agents
4. Synthesize all results in the main session

**Quick mode** runs sequentially in the main session — agent overhead isn't worth it for 3 concerns.

**Fallback:** If Agent tool is unavailable, run all perspectives sequentially in the main session.

## Workflow

1. **Parse mode and flags** from arguments
2. **Identify target** — What's being challenged (from conversation or user specification)
3. **Gather context** — Launch `context-reader` agent (or read files directly if Agent unavailable)
4. **Launch critics** — Launch 6 `critic` agents in parallel (standard/brutal) or analyze sequentially (quick/fallback)
5. **In brutal mode** — Also launch 2-3 domain-specific `critic` agents from `references/critic-frameworks.md`
6. **Synthesize** — Collect all critic results, merge, prioritize concerns by severity
7. **Offer to log** — If project-context available, offer to save to `.project-context/plans/challenge-*.md`
8. **Ask direction** — "Which of these should we address before proceeding?"

## If No Clear Target

If there's no clear plan or code to challenge in the conversation:

```
I don't see a clear plan or code change to challenge. Could you:
1. Share what you'd like me to critique
2. Reference a specific proposal from our conversation
3. Share a code diff or implementation plan
```

## Output

Use the output format from the project-context:challenge skill:
- Standard mode: All six perspectives (from critic agents) + prioritized concerns + recommendation
- Quick mode: Top 3 concerns with actions (sequential, no agents)
- Brutal mode: Six core + domain critic agents, harsher analysis, synthesized assessment

Always end with: "Which of these should we address before proceeding?"
