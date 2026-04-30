---
name: project-context-mini:update
description: "Create or refresh the four lean context files in .project-context/ — architecture.md, flows.md, patterns.md, status.md. Bootstraps missing files on first run. Refreshes existing files via two-agent extraction + critic pipeline. Triggers: 'update mini context', 'refresh mini', 'capture in mini', 'bootstrap mini context', 'mini init'."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Update project-context-mini

Create or refresh the four context files in `.project-context/`. One skill handles both bootstrap (missing files) and refresh (existing files).

**Core discipline:** ruthlessly filter additions. Prefer rewriting to adding. Prefer removing stale content over leaving it. Mini is for essentials only.

**Clarify before acting:** if anything is ambiguous — which file to target, which mode to run, how to interpret a candidate, which of conflicting signals to trust, or which option to pick at any branching step — use the `AskUserQuestion` tool to ask the user before proceeding. Prefer one batched question with concrete options over guessing or asking one-at-a-time. Do not fabricate intent.

## Arguments

- `file` (optional) — target a single file
  - `architecture` / `flows` / `patterns` / `status`
  - If omitted: all four files are candidates
- `--source` (optional) — where to pull candidates from
  - `--chat` — analyze current conversation
  - `--scan` — scan `git diff` and changed files
  - `--input` — interactive user input
  - Default: auto-detect (chat if recent discussion, else scan, else input)
- `--bootstrap` / `--refresh` — force a specific mode (auto-detected otherwise)

## Workflow

### Step 1 — Detect mode

```bash
ls .project-context/*.md 2>/dev/null
```

- If directory missing or no `.md` files → **bootstrap mode** (Step 2)
- If all four files exist → **refresh mode** (Step 3)
- If some files exist: ask user whether to finish bootstrap or treat as refresh

### Step 2 — Bootstrap mode

Goal: create `.project-context/` + the four files with seeded scaffolds.

1. **Read** `references/file-scaffolds.md` for templates and seed questions.
2. **Ask the user** the five seed questions (project goal, tech stack, core user flow, current focus, upfront conventions/gotchas). Keep it one batch, not one-at-a-time.
3. **Draft** the four files by merging scaffolds with user answers:
   - `architecture.md` — fill tech stack + one starter component from answer 2; leave Mermaid diagram as a minimal placeholder graph the user can expand.
   - `flows.md` — one H2 section using the core user flow from answer 3, with a minimal mermaid sequenceDiagram skeleton.
   - `patterns.md` — if answer 5 yielded conventions/gotchas, add them; otherwise leave empty categories with TODO markers.
   - `status.md` — fill current focus + why + next action from answer 4.
4. **Confirm** — show the user all four drafts together, ask for approval or edits.
5. **Write** the approved versions to `.project-context/`.
6. **Skip** the agent pipeline entirely on bootstrap — extraction is meaningless against empty files.

Exit bootstrap with a short summary and a suggestion to run `/project-context-mini:discuss` to verify.

### Step 3 — Refresh mode

Goal: surface new knowledge from chat or code, ruthlessly filter, update files.

#### 3a. Determine source

Auto-detect priority:
1. Conversation shows decisions, fixes, architectural shifts, or pattern discoveries → `--chat`
2. `git status` / `git diff HEAD~5` shows substantive changes → `--scan`
3. Neither → fall back to `--input` and ask the user what changed

#### 3b. Dispatch `content-extractor` agent

Launch the agent with:
- **Source mode** (`--chat` / `--scan` / `--input`)
- **Conversation digest** (if `--chat`)
- **Current contents** of the four files (Read them and pass inline)
- **Target file filter** if `file` argument was provided

The agent returns ranked candidates in this shape:

```json
[
  {
    "file": "patterns.md",
    "section": "Gotchas",
    "proposed_content": "...",
    "signal_type": "gotcha",
    "impact_score": 8,
    "action": "add" | "rewrite-section" | "replace-bullet"
  }
]
```

#### 3c. Dispatch `update-critic` agent

Launch with:
- The extractor's candidate list
- The current file contents
- The ruthless filter rules (see `agents/update-critic/agent.md`)

The critic returns a reduced list with rejection reasons for everything it cut:

```json
{
  "kept": [...],
  "rejected": [{ "candidate": {...}, "reason": "..." }]
}
```

Cap per file: **3 items maximum**. If the critic keeps more, trim to 3 highest impact.

#### 3d. Present to user

Group kept candidates by target file. For each: show the action (add / rewrite / replace), the proposed content, and a one-line rationale. Include a compact summary of what the critic rejected so the user sees the filter working.

Ask the user to approve all / approve some / reject all.

#### 3e. Apply approved updates

For each approved candidate:
- **add** → Edit tool, append to the named section
- **rewrite-section** → Edit tool, replace the section content in full
- **replace-bullet** → Edit tool, swap a specific bullet

Preserve Mermaid diagrams verbatim unless the candidate explicitly modifies one.

#### 3f. Refs-split suggestion

After writes, check file sizes:

```bash
wc -l .project-context/architecture.md .project-context/flows.md .project-context/patterns.md
```

For any file > 75 lines, emit a non-blocking suggestion:

> `architecture.md` is 92 lines. Consider splitting sections into `.project-context/architecture/refs/<section>.md` and leaving pointers in the main file. (This is a suggestion only — not auto-applied.)

Do not auto-create refs/. User runs the split manually or asks in a follow-up turn.

`status.md` is exempt — if it grows beyond a paragraph or two, that's a signal the scope itself drifted and should be recompressed, not split.

### Step 4 — Summary

Emit a terse summary:

```
Updated .project-context/:
  architecture.md — 1 addition (new Kafka topic)
  patterns.md — 1 rewrite (retry convention)
Rejected 4 candidates (see above)
Files > 75 lines: none
```

No follow-up propagation, no CLAUDE.md sync, no commit prompt. Mini stays minimal.

## Quality gates

These are hard gates, not suggestions. The critic enforces them; the skill should double-check:

1. **New-teammate test** — would you tell a new teammate joining this project about this?
2. **Not a framework default** — don't capture things that are already standard in the stack.
3. **Not already present** — redundancy checks against current file contents.
4. **Mermaid-first respected** — architecture/flows/status: if adding non-trivial content, consider whether a diagram would communicate it better.
5. **Patterns stay categorized** — every `patterns.md` addition lands under `## Conventions`, `## Anti-patterns`, or `## Gotchas`.

## Edge cases

- **Files partially exist** (e.g., only `status.md`) — ask the user which mode they want. Don't silently overwrite.
- **No recent conversation signal and clean git** — skip to `--input` and ask "what changed?" rather than fabricating extractions.
- **Critic rejects everything** — show the rejections and exit gracefully with "no updates worth capturing." That is a valid outcome for a ruthless filter.
- **Agent tool unavailable** — fall back to inline extraction in the main session, but preserve the two-pass discipline: first gather candidates, then harshly filter before presenting.
