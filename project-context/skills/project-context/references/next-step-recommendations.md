# Next-Step Recommendations

After completing a skill or command, proactively recommend the single best next action to the user. This keeps the workflow flowing without the user needing to remember which command comes next.

## How It Works

At the end of your skill's output, launch a `next-step-recommender` agent to determine the best next action based on what just completed and current project state.

### Invoking the Recommender

Add this to your skill's final summary step:

```
Launch a `next-step-recommender` agent with:
- **Completed skill:** [skill-name]
- **Summary:** [brief description of what just happened]
```

The agent reads `state.md`, `progress.md`, and `plans/*.md`, then returns:

```
NEXT_STEP: /project-context:<command> [args]
REASON: One sentence explaining why.
NOTE: Optional secondary suggestion.
```

### Formatting the Output

Append the recommendation as the last block in your summary:

```markdown
**Recommended next step:**
→ /project-context:implement .project-context/plans/auth.md
  Plan is saved and verified — ready to begin implementation.
```

If the agent returns a NOTE, include it on the next line:

```markdown
**Recommended next step:**
→ /project-context:update --chat
  Implementation is complete — capture learnings from this session.
  Note: progress.md has 12 completed items — also consider /project-context:optimize after updating.
```

If the agent returns `NEXT_STEP: none`, omit the recommendation block entirely.

## Fallback: Manual Recommendation

If the Agent tool is unavailable, use this quick-reference graph to determine the next step manually:

| Completed Skill | Default Next Step | Condition for Override |
|---|---|---|
| `init` | `/project-context:brainstorm` | — |
| `brainstorm` | `/project-context:plan` | If concerns exist → `/project-context:challenge` |
| `plan` | `/project-context:implement <path>` | If plan has concerns → `/project-context:challenge` |
| `challenge` | `/project-context:implement <path>` | If critical issues → `/project-context:plan` (revise) |
| `implement` | `/project-context:update --chat` | If pausing → `/project-context:pause` |
| `update` | `/project-context:brainstorm` | If files grew large → `/project-context:optimize` |
| `optimize` | `/project-context:brainstorm` | If active plan exists → `/project-context:implement` |
| `quick` | `/project-context:update --chat` | If minor change → omit |
| `validate` | `/project-context:update` | If all valid → omit |
| `resume` | Follow `continue.md` next steps | If active plan → `/project-context:implement` |

### State Overrides (check these first)

1. If `state.md` has an explicit "Next Action" with a command → use that command
2. If a plan exists with `Status: Planning` → recommend `/project-context:implement <path>`
3. If `progress.md` has 10+ completed items → add note about `/project-context:optimize`
4. If context files are >1 day stale → add note about `/project-context:update --scan`

## Skills That Skip Recommendations

These skills do NOT include a next-step recommendation:
- **`info`** — Read-only query, not a workflow step
- **`project-context`** — Informational skill
- **`pause`** — Session is ending
- **`next`** — This IS the recommendation engine
