---
name: project-context:update
description: "Extract knowledge from conversations, code changes, or user input into project context. Triggers: 'update context', 'capture learnings', 'retro', 'retrospective', 'what did we learn', 'extract learnings', 'sync context', 'summarize our work', 'capture insights'. Focuses on reusable knowledge (patterns, architecture, decisions) — status tracking (state/progress) is handled automatically by implement and CLAUDE.md sync rules."
context: fork
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
---

# Update Project Context

Extract reusable knowledge from conversations, code changes, or user input into `.project-context/` files.

**Focus:** Knowledge capture (patterns, architecture decisions, gotchas) — not status tracking. State and progress updates are handled by the implement skill and CLAUDE.md sync rules.

## Arguments

- `file` (optional): Specific file to update
  - `brief` — Project goals and scope
  - `architecture` — System diagrams and flows
  - `patterns` — Patterns and learnings
  - `state` — Current position (manual override only — skipped in auto-detection)
  - `progress` — Work status (manual override only — skipped in auto-detection)
  - If omitted: Smart update of knowledge files (brief, architecture, patterns)

- `--source` (optional): Where to get update information
  - `--chat` — Deep analysis of current conversation history
  - `--scan` — Scan codebase for changes (git diff, new files)
  - `--input` — Interactive input from user
  - Default: Smart detection (chat if recent discussion, else scan)

## Workflow

**Context-First (mandatory).** Follow the [Context-First Protocol](../project-context/references/context-first-protocol.md) before any codebase scanning. Read `.project-context/` files and `dependencies.json` (if present) FIRST.

### Step 1: Verify Context Exists

```bash
ls .project-context/*.md 2>/dev/null
```

If not found: "Run `/project-context:init` first."

### Step 2: Determine Update Source

**Smart Detection:**
1. Meaningful conversation context (decisions, learnings, completed work) → use `--chat`
2. Git status shows changes but no meaningful conversation → use `--scan`
3. Otherwise → prompt for `--input`

---

## --chat Mode: Knowledge Extraction

### 2a. Analyze Conversation

**Launch a `conversation-analyzer` agent** to extract knowledge candidates. The agent receives signal recognition patterns and the current context digest. It runs in parallel with Step 2b.

**If Agent tool is unavailable**, analyze manually in the main session.

Scan conversation for knowledge signals:
- **Decisions:** Technology choices, architecture decisions, trade-offs accepted
- **Patterns:** Coding conventions established, anti-patterns identified
- **Gotchas:** Bugs with non-obvious root causes, debugging insights, things that "almost worked"
- **Architecture changes:** New components, flows, integration points

**Do NOT extract:**
- Progress/status updates (handled by implement + CLAUDE.md sync rules)
- Trivial fixes (typos, missing imports, obvious bugs)
- One-off implementation details unlikely to recur

### 2b. Check Existing Context (Selective)

**Launch a `context-reader` agent** to condense existing context into a digest. This runs in parallel with Step 2a.

```
Main → conversation-analyzer agent ───┐
     → context-reader agent ───────────┤ parallel
                                       ↓
                                 Merge results → Steps 2c-2e
```

**If Agent tool is unavailable**, read selectively — only the knowledge files you intend to update (brief.md, architecture.md, patterns.md).

### 2c. Rank and Filter

Apply the **"new teammate" test**: Would you tell a new teammate joining this project about this? If not, drop it.

From all candidates that pass:
1. Rank by impact (affects more code/decisions = higher rank)
2. **Keep only top 5** — ruthlessly cut the rest
3. Drop anything already captured in existing context

### 2d. Propose Updates

Present the ranked top 5 as terse bullet entries:

```markdown
## Proposed Updates (5 items, ranked by impact)

### patterns.md
- **Redis pub/sub for cross-service events**
  REST polling caused 3s latency in order notifications; pub/sub solved it.

- **Prisma migrate deploy in CI**
  `migrate dev` resets the DB; always use `migrate deploy` in non-local environments.

### architecture.md
- **Added event bus between Order and Notification services**
  Replaces direct REST calls; enables async processing and retry.

Questions:
1. Approve all, or modify/remove any items?
```

**Entry format:** Bold name + one context line (when/why it applies). Max 2 lines per entry.

### 2e. Apply Approved Updates

After user confirms:
1. Read the target file
2. Identify the correct section (or create if needed)
3. Use Edit tool to add content in the terse bullet format
4. Maintain existing formatting and structure

---

## --scan Mode: Codebase Analysis

```bash
git diff --stat HEAD~5 2>/dev/null || git status --short
```

Analyze for knowledge signals only:
- New components or architectural changes → `architecture.md`
- New patterns or conventions → `patterns.md`
- Scope changes → `brief.md`

Apply the same rank-and-filter (top 5, "new teammate" test).

---

## --input Mode: Interactive

Ask user focused questions based on the target file. Apply the same budget — capture up to 5 items in terse format.

---

## Step 3: Refresh Managed Sections

After any mode completes, sync configuration files:

```bash
python project-context/scripts/manage_context.py update-sections --file CLAUDE.md
python project-context/scripts/manage_context.py update-sections --file AGENTS.md
```

## Step 3.5: Suggest Optimization (if needed)

After applying updates, check if context files have grown significantly:
- Any file exceeds ~100 lines → suggest: "[file] is getting large. Run `/project-context:optimize` to split into focused files."

This is a suggestion only — do not auto-run optimize.

## Step 4: Show Summary

```markdown
Updates applied to .project-context files:

- **patterns.md**: +2 entries (Redis pub/sub, Prisma migrate)
- **architecture.md**: +1 entry (event bus)

Configuration files refreshed: CLAUDE.md, AGENTS.md
```

---

## Step 5: Propagate to Downstream Dependencies

If local-path downstream deps exist in `dependencies.json`, propagate relevant changes. See `references/propagation-workflow.md` for the full workflow.

## Step 6: Commit Changes

After all updates and propagations, offer to commit. See `references/commit-workflow.md` for the full workflow.

## Knowledge Capture Rules

### The "New Teammate" Test
Only capture knowledge that passes: "Would I tell a new teammate joining this project about this?"

### Budget
- **Max 5 items per update session**, ranked by impact
- Each item: bold name + one context line (max 2 lines)
- If more than 5 candidates pass the test, cut the lowest-impact ones

### Quality Filters (hard gate, not suggestion)
- **Reusable** — applies beyond this one instance
- **Specific** — includes concrete context (when/why)
- **Not redundant** — not already in context files
- **Not trivial** — skip obvious fixes and one-off details

### What to Capture vs Skip

| Capture | Skip |
|---------|------|
| Architecture decisions with rationale | "Added file X" |
| Patterns that prevent future bugs | Typo/import fixes |
| Non-obvious gotchas and workarounds | Obvious error handling |
| Technology choices and trade-offs | Minor refactoring |
| Conventions that affect multiple files | One-off implementation details |

## File-Specific Guidelines

### brief.md
Update when: Project goals/vision change, target users evolve, scope expands/contracts.

### architecture.md
Update when: New technology adopted, components added/modified, flows change.
**Always use Mermaid diagrams** with clear titles and step-by-step descriptions.

### patterns.md
Update when: Reusable pattern established, anti-pattern discovered, convention adopted.
**Organize by category** (Error Handling, State Management, etc.)

## Step 7: Recommend Next Step

After the summary, launch a `next-step-recommender` agent with:
- **Completed skill:** `update`
- **Summary:** Brief description of what was updated (files modified, source mode used)

Append the agent's recommendation to your output:

```
**Recommended next step:**
→ [NEXT_STEP from agent]
  [REASON from agent]
```

If Agent tool is unavailable, refer to `references/next-step-recommendations.md` for the recommendation graph and determine the next step manually.

## Edge Cases & Examples

For edge case templates and worked examples, see `references/update-examples.md`.
