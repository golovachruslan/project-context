---
name: project-context-mini:load
description: "Read all four .project-context-mini/ files inline into the current session. Full inline read — no digest, no pointers — because files are tiny by design. Use at the start of a session to prime the agent with project awareness. Triggers: 'load mini', 'load mini context', 'onboard me with mini', 'prime with mini', 'bootstrap session with mini'."
allowed-tools:
  - Read
  - Glob
  - Bash
---

# Load project-context-mini

Read the four `.project-context-mini/` files inline into the session. No agents, no digests, no pointer lists — the files are small enough to load in full. If they aren't, `/project-context-mini:update` will have suggested a refs-split before it got this bad.

## Workflow

### Step 1 — Discover

```bash
ls .project-context-mini/*.md 2>/dev/null
```

If `.project-context-mini/` does not exist or is empty:

> No mini context found. Run `/project-context-mini:update` to create it.

Stop.

### Step 2 — Read the four files

Read in full, in this order:

1. `.project-context-mini/status.md` — current focus lands first so the agent's framing is right
2. `.project-context-mini/architecture.md` — the structural map
3. `.project-context-mini/flows.md` — how users actually move through the system
4. `.project-context-mini/patterns.md` — conventions, anti-patterns, gotchas

If any of the four is missing, note it in the output but continue with the rest.

### Step 3 — Read refs (if any)

```bash
ls .project-context-mini/architecture/refs/*.md .project-context-mini/flows/refs/*.md .project-context-mini/patterns/refs/*.md 2>/dev/null
```

For each ref file that exists, read it in full. Refs exist because a main file grew past the soft threshold — they are still meant to be small and load-friendly.

### Step 4 — Emit structured digest

Output all four sections inline with Mermaid diagrams preserved verbatim. Use this shape:

```markdown
## Project Context Mini — Loaded

### Status
<contents of status.md>

### Architecture
<contents of architecture.md>

<if architecture/refs/ exist:>
**Architecture refs:**
#### <ref name>
<contents of that ref file>
</if>

### User Flows
<contents of flows.md>

<same pattern for flows/refs/>

### Patterns
<contents of patterns.md>

<same pattern for patterns/refs/>
```

Preserve all Mermaid code fences exactly. Do not summarize, do not compress, do not reorder sections within a file.

### Step 5 — Health notes (only when warranted)

At the end, add terse notes only if one of these conditions is true:

- Any main file is empty or has only TODO markers → "`<file>` is empty — run `/project-context-mini:update` to populate."
- Any main file exceeds 120 lines → "`<file>` is getting large (>120 lines). Consider splitting into `<file>/refs/`."
- `status.md` was last modified more than 14 days ago (check with `stat -f %m` / `stat -c %Y`) → "`status.md` is stale — focus may have shifted."

If none of these conditions apply, emit no health notes. Silence is the correct default.

## What this skill does NOT do

- No "Detailed References" section — files are already loaded inline.
- No digest, no compression, no summarization — if you find yourself wanting to summarize, the files are too big and the fix is to refs-split, not to hide content in `load`.
- No subagent dispatch — reading four small files is cheap in the main session.
- No prompts to the user — this skill reads and emits, nothing else.

## Edge cases

- **Only some files exist** — emit what's present, note what's missing, suggest `update`.
- **Files are scaffold-only (TODO markers everywhere)** — emit them anyway, but lead with: "Mini context is bootstrapped but not populated. Consider `/project-context-mini:update --input` to fill in."
- **Refs exist but main file already has the content** — still emit both; the user may be debugging a bad split. Don't try to deduplicate.
