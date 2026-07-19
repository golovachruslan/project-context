---
name: update
description: "Create or refresh the four lean context files in .project-context/ — architecture.md, flows.md, patterns.md, status.md. Bootstraps missing files on first run. Refreshes existing files via inline chat extraction and/or a scan agent, filtered by a critic agent. Triggers: 'update mini context', 'refresh mini', 'capture in mini', 'bootstrap mini context', 'mini init'."
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

Arguments arrive as free-form text in `$ARGUMENTS`. Parse loosely — match tokens, don't require exact syntax or ordering.

- `architecture` / `flows` / `patterns` / `status` — target a single file. If omitted, all four files are candidates.
- `--chat` — extract from the current conversation only
- `--scan` — extract from git history and changed files only
- `--input` — ask the user what changed
- Source default: auto-detect (chat if the conversation has substance, plus scan if git shows changes; else input)
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
2. **Scan the repo first** to prefill what the code already answers — do not ask the user things the repo can tell you:
   - Tech stack: manifest files (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, …), lockfiles, framework config files
   - Components: top-level directory layout, entry points
   - Project goal hints: `README.md` first paragraph
3. **Ask the user** only what the scan cannot answer: confirm/correct the prefilled stack and components, plus current focus, core user flow, and any day-one conventions/gotchas. One batched `AskUserQuestion`, not one-at-a-time.
4. **Draft** the four files by merging scaffolds, scan results, and user answers:
   - `architecture.md` — prefilled tech stack + components from the scan; minimal placeholder Mermaid graph the user can expand.
   - `flows.md` — one H2 section for the core user flow, with a minimal mermaid sequenceDiagram skeleton.
   - `patterns.md` — if the user gave conventions/gotchas, add them; otherwise leave empty categories with TODO markers.
   - `status.md` — current focus + why + next action from the user's answer.
5. **Confirm** — show the user all four drafts together, ask for approval or edits.
6. **Write** the approved versions to `.project-context/`.
7. **Skip** the agent pipeline entirely on bootstrap — extraction is meaningless against empty files.

Exit bootstrap with a short summary and a suggestion to run `/project-context-mini:discuss` to verify.

### Step 3 — Refresh mode

Goal: surface new knowledge from chat or code, ruthlessly filter, update files.

Pipeline shape: **chat extraction runs inline** (you already have the conversation — a subagent cannot see it better than you can), **scan extraction runs in the `content-extractor` agent** (git diff reading is noisy; isolate it), and **filtering always runs in the `update-critic` agent** (fresh context, no attachment to the candidates).

#### 3a. Determine sources

Both sources can be active in one run:

1. Conversation shows decisions, fixes, architectural shifts, or pattern discoveries → include **chat**
2. Git shows substantive changes since the last context update → include **scan**
3. Neither → fall back to `--input` and ask the user what changed

For the git check, anchor to the last context update, not an arbitrary commit count:

```bash
LAST=$(git log -1 --format=%H -- .project-context 2>/dev/null)
git diff --stat ${LAST:-HEAD~5}..HEAD 2>/dev/null || git diff --stat HEAD
```

(`HEAD~5` is only the fallback when `.project-context/` has no git history yet.)

#### 3b. Extract candidates

**Chat source — extract inline, in the main session.** Read the four current files first so you know what's already captured. Then scan the conversation for these cues:

- **Decision:** "let's use X", "decided on Y", "chose X over Y because", "going with"
- **Pattern:** "always", "never", "convention is", "be careful with", "don't do X because"
- **Architecture:** "added service", "new component", "refactored into", "migrated from X to Y"
- **Flow:** "user flow", "journey", "sequence", "when the user"
- **Gotcha:** "turned out", "surprisingly", "subtle bug", "almost worked but", "watch out for"
- **Status:** "now working on", "focus shifted", "blocked on", "next up is"

Over-generate deliberately — the critic filters. Do not extract: trivial fixes, framework defaults, one-off details, progress updates, or anything already in the files.

**Scan source — dispatch the `content-extractor` agent** with:
- The anchor commit / diff range from 3a
- Current contents of the four files (Read them and pass inline)
- Target file filter if a file argument was provided

Both paths produce candidates in the same shape:

```json
[
  {
    "file": "patterns.md",
    "section": "Gotchas",
    "proposed_content": "...",
    "signal_type": "gotcha",
    "impact_score": 8,
    "action": "add" | "rewrite-section" | "replace-bullet",
    "rationale": "One sentence: why this matters enough to capture."
  }
]
```

If both sources ran, merge the two candidate lists before 3c. When a chat candidate and a scan candidate point at the same thing, merge them into one and raise its impact score — corroboration across sources is a strong signal.

#### 3c. Dispatch `update-critic` agent

Launch with:
- The merged candidate list
- The current file contents
- The ruthless filter rules (see `agents/update-critic/agent.md`)

The critic returns a reduced list with rejection reasons for everything it cut:

```json
{
  "kept": [...],
  "rejected": [{ "candidate": {...}, "reason": "..." }]
}
```

**Parse agent output leniently.** Agents sometimes wrap JSON in code fences or a sentence of prose despite instructions — strip any wrapper and parse the first JSON value found. Only re-dispatch if no JSON can be recovered at all.

Cap per file: **3 items maximum**. If the critic keeps more, trim to 3 highest impact.

#### 3d. Present to user

Group kept candidates by target file. For each: show the action (add / rewrite / replace), the proposed content, and its one-line rationale. Include a compact summary of what the critic rejected so the user sees the filter working.

Then ask for approval with a single `AskUserQuestion` call using `multiSelect: true` — one option per kept candidate (label: file + short summary), so the user can approve any subset in one interaction.

#### 3e. Apply approved updates

For each approved candidate:
- **add** → Edit tool, append to the named section (insert before the next H2, or at end of file if it's the last section)
- **rewrite-section** → Edit tool, replace the section content in full
- **replace-bullet** → Edit tool, swap a specific bullet

Preserve Mermaid diagrams verbatim unless the candidate explicitly modifies one.

#### 3f. Refs-split suggestion

After writes, check file sizes:

```bash
wc -l .project-context/architecture.md .project-context/flows.md .project-context/patterns.md
```

For any file > 75 lines, emit a non-blocking suggestion:

> `architecture.md` is 92 lines. Consider splitting sections into `.project-context/architecture/refs/<section>.md` and leaving pointers in the main file. Say "split architecture" and I'll do it.

Do not auto-create refs/. Split only when the user asks (procedure below).

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

## Refs-split procedure (on request only)

When the user asks to split a file (e.g. "split architecture"):

1. Pick the largest self-contained H2 section(s) that push the file over 75 lines — never split `status.md`.
2. Create `.project-context/<file-stem>/refs/<section-slug>.md` with the section's full content under an H1.
3. In the main file, replace the moved section body with a one-line pointer: `See [.project-context/<file-stem>/refs/<section-slug>.md] for details.` Keep the H2 heading.
4. Keep the main file's Mermaid overview diagram in place — diagrams stay in the main file; only prose detail moves to refs.
5. Confirm the main file is back under 75 lines; report old → new line counts.

## Quality gates

These are hard gates, not suggestions. The critic enforces them; the skill should double-check:

1. **New-teammate test** — would you tell a new teammate joining this project about this?
2. **Not a framework default** — don't capture things that are already standard in the stack.
3. **Not already present** — redundancy checks against current file contents.
4. **Mermaid-first respected** — architecture/flows: if adding non-trivial content, consider whether a diagram would communicate it better. `status.md` and `patterns.md` are text-first.
5. **Patterns stay categorized** — every `patterns.md` addition lands under `## Conventions`, `## Anti-patterns`, or `## Gotchas`.

## Edge cases

- **Files partially exist** (e.g., only `status.md`) — ask the user which mode they want. Don't silently overwrite.
- **No recent conversation signal and clean git** — skip to `--input` and ask "what changed?" rather than fabricating extractions.
- **Critic rejects everything** — show the rejections and exit gracefully with "no updates worth capturing." That is a valid outcome for a ruthless filter.
- **Agent tool unavailable** — run scan extraction and filtering inline, but preserve the two-pass discipline: first gather candidates, then harshly filter against the quality gates before presenting.
