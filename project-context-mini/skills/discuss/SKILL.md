---
name: project-context-mini:discuss
description: "Prime the agent for a discussion of this project. Reads the four .project-context/ mini files inline and lists any refs/ files (lazy — content not loaded). Optional topic argument focuses the framing prompt. Triggers: 'discuss the project', 'prime me on this project', 'load mini context to discuss', 'onboard me with mini'."
allowed-tools:
  - Read
  - Glob
  - Bash
---

# Discuss project-context-mini

Read the four `.project-context/` mini files inline so the agent is primed to discuss the project. Refs are *listed*, not read — the agent reads a specific ref on demand if the conversation requires that detail.

## Arguments

- `topic` (optional, free-form) — what the user wants to discuss. Examples: `architecture`, `onboarding flow`, `auth gotchas`. Used only in the closing framing prompt; does not filter which files are loaded.

## Workflow

### Step 1 — Discover

```bash
ls .project-context/*.md 2>/dev/null
```

If `.project-context/` does not exist or is empty:

> No project-context-mini context found. Run `/project-context-mini:update` to create it.

Stop.

### Step 2 — Read the four main files

Read in full, in this order:

1. `.project-context/status.md` — current focus lands first so framing is right
2. `.project-context/architecture.md` — the structural map
3. `.project-context/flows.md` — how users actually move through the system
4. `.project-context/patterns.md` — conventions, anti-patterns, gotchas

If any of the four is missing, note it in the output but continue with the rest.

### Step 3 — List refs (do not read)

```bash
ls .project-context/architecture/refs/*.md .project-context/flows/refs/*.md .project-context/patterns/refs/*.md 2>/dev/null
```

For each ref file found, **list its path only**. Do not read the contents.

If a ref's H1 is cheap to fetch (e.g., `head -1 <path>`), include it as a one-line hint. Otherwise show the bare path.

Group refs under their parent file (architecture / flows / patterns). If no refs exist, omit the section entirely.

### Step 4 — Emit structured digest

Output the four main files inline with Mermaid diagrams preserved verbatim. Then a refs manifest. Then a framing prompt.

```markdown
## Project Context Mini — Loaded

### Status
<contents of status.md>

### Architecture
<contents of architecture.md>

### User Flows
<contents of flows.md>

### Patterns
<contents of patterns.md>

<if any refs were found:>
### Available refs (lazy — read on demand)

**architecture/**
- `.project-context/architecture/refs/<name>.md` — <H1 hint or filename>

**flows/**
- `.project-context/flows/refs/<name>.md` — <hint>

**patterns/**
- `.project-context/patterns/refs/<name>.md` — <hint>

Read any of these with the Read tool when the conversation requires that detail.
</if>
```

Preserve all Mermaid code fences exactly. Do not summarize, compress, or reorder sections within a file.

### Step 5 — Framing prompt

End the output with one short framing line:

- **Without topic:** `Primed on this project. Ask about architecture, flows, patterns, or status.`
- **With topic:** `Primed on this project, focused on \`<topic>\`. What do you want to know?`

Where `<topic>` is the literal `$ARGUMENTS` value as the user passed it.

### Step 6 — Health notes (only when warranted)

Emit terse notes only if one of these conditions is true:

- Any main file is empty or has only TODO markers → "`<file>` is empty — run `/project-context-mini:update` to populate."
- Any main file exceeds 120 lines → "`<file>` is getting large (>120 lines). Consider splitting into `<file>/refs/`."
- `status.md` was last modified more than 14 days ago (check with `stat -f %m` / `stat -c %Y`) → "`status.md` is stale — focus may have shifted."

If none apply, emit no health notes. Silence is the default.

## What this skill does NOT do

- Does not read refs/ contents — listing only. The agent reads a specific ref via the Read tool when it needs that detail.
- No digest, no compression, no summarization of main files.
- No subagent dispatch — reading four small files is cheap in the main session.
- No interactive Q&A loop — emit the framing prompt and stop.
- Topic argument does **not** filter which files are loaded; it only shapes the framing line.

## Edge cases

- **Only some main files exist** — emit what's present, note what's missing, suggest `update`.
- **Files are scaffold-only (TODO markers everywhere)** — emit them anyway, but lead with: "Mini context is bootstrapped but not populated. Consider `/project-context-mini:update --input` to fill in."
- **Refs exist but the corresponding main file is missing** — list the refs anyway; the agent decides whether to read them.
- **Topic argument is multi-word** — pass it through verbatim; do not parse or interpret it.
