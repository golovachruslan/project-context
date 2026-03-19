---
name: project-context:optimize
description: "Optimize project context files for efficient AI agent consumption. Triggers: 'optimize context', 'compact context', 'organize context', 'clean up context', 'context too large', 'shrink context files', 'tidy context', 'split large files'. Supports compact (summarize + archive), organize (normalize + dedup + split), or both."
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Optimize Project Context

Optimize `.project-context/` files for efficient AI agent consumption. Two operations available:

- **Compact** — Summarize verbose sections, archive completed work to per-feature files
- **Organize** — Normalize structure, deduplicate, ensure cross-file consistency, split large files

## Workflow

### Step 1: Verify Context Exists

```bash
ls .project-context/*.md 2>/dev/null
```

If not found: "No project context found. Run `/project-context:init` to set up."

### Step 2: Ask User What to Do

Use AskUserQuestion:

```
What would you like to optimize?

1. **Compact** — Summarize verbose text, archive completed features from progress.md
2. **Organize** — Normalize structure, deduplicate across files, split large files
3. **Both** — Full optimization pass (compact first, then organize)
```

### Step 3: Analyze Current State

Read all context files and assess:

```bash
ls -la .project-context/*.md .project-context/*/*.md 2>/dev/null
```

For each file, evaluate:
- **Size** (line count, approximate token count)
- **Staleness** (last updated timestamp vs today)
- **Structure** (does it match canonical template?)
- **Redundancy** (content duplicated across files?)

Present a brief health report:

```
Context Health Report:
- brief.md: 25 lines, current, well-structured
- architecture.md: 180 lines, large — candidate for splitting
- state.md: 45 lines, current
- progress.md: 95 lines, 12 completed items — candidate for archiving
- patterns.md: 60 lines, current
```

### Step 4: Execute Operation

---

## Compact Operation

### 4C-1: Archive Completed Work (progress.md)

Scan `progress.md` for completed items. Group by feature/phase.

For each completed feature/phase with substantial content (3+ items or detailed descriptions):

1. Create `progress/<feature-name>.md` with the archived content:

```markdown
# [Feature Name] — Archive

**Completed:** YYYY-MM-DD

## Work Completed
- [Detailed items moved from progress.md]

## Key Deliverables
- [Files created/modified]

## Decisions Made
- [Any decisions captured during this work]
```

2. Replace the detailed items in `progress.md` with a one-liner + link:

```markdown
## Completed
- [Feature Name](progress/feature-name.md) (YYYY-MM-DD)
```

### 4C-2: Prune State (state.md)

- Remove resolved blockers (keep only active ones)
- Remove completed decisions from "Decisions Pending"
- Condense "Session Info" to latest session only
- If "Recently Completed" section exists and items are >7 days old, remove them

### 4C-3: Summarize Verbose Sections

For any file with sections that are overly verbose:
- Condense long-form paragraphs into bullet points
- Replace detailed explanations with concise summaries
- Preserve all factual content — only reduce wordiness

### 4C-4: Show Compact Diff

Present changes per file:

```
## Compact Changes

### progress.md
- Archived 8 completed items to 3 feature archives:
  - progress/auth-system.md (4 items)
  - progress/plugin-marketplace.md (3 items)
  - progress/v2-migration.md (1 item)
- Kept 2 recent completed items inline

### state.md
- Removed 3 resolved blockers
- Condensed session info

Approve these changes? (yes / no / modify)
```

Wait for explicit approval before applying.

---

## Organize Operation

### 4O-1: Normalize to Canonical Templates

Compare each file against its template (from `references/file-templates.md`):
- Missing sections → add with empty placeholder
- Wrong section order → reorder to match template
- Missing frontmatter (timestamps, etc.) → add

### 4O-2: Deduplicate Across Files

Check for content that appears in multiple files:

| Overlap | Resolution |
|---------|-----------|
| Goals in both brief.md and architecture.md | Keep in brief.md, remove from architecture.md |
| Tech decisions in both architecture.md and patterns.md | Architecture owns decisions, patterns owns conventions |
| Status info in both state.md and progress.md | State owns current focus/blockers, progress owns task lists |
| Completed work repeated in state.md and progress.md | Keep in progress.md, state.md gets only "Recently Completed" summary |

### 4O-3: Semantic Grouping

Within each file, group related items together:
- In patterns.md: group patterns by domain (auth, data, UI, etc.)
- In architecture.md: group decisions by component area
- In progress.md: group completed items by feature/phase

### 4O-4: Cross-File Consistency

Verify alignment:
- state.md "Next Action" should relate to progress.md "In Progress" or "Upcoming"
- state.md "Active Plan" should reference an existing plan in `plans/`
- architecture.md components should reflect what's in progress.md
- Flag inconsistencies for user review

### 4O-5: Split Large Files

When a file exceeds ~100 lines or has 5+ substantial sections:

1. Propose splitting into a subdirectory structure:

```
architecture.md (summary + links)  ← keeps ~30-40 lines
architecture/
  api-design.md                    ← extracted detail
  data-model.md                    ← extracted detail
  auth-flow.md                     ← extracted detail
```

2. The main file keeps:
   - Section headings with 1-2 line summaries
   - Relative links: `See [API Design](architecture/api-design.md) for details`
   - Any Mermaid overview diagram

3. Detail files are self-contained with clear scope headers.

Applies to: `architecture.md`, `patterns.md`, `progress.md` (via archive), `brief.md` (rare).

`state.md` should NOT be split — it must stay compact by nature.

### 4O-6: Show Organize Diff

Present all proposed changes:

```
## Organize Changes

### architecture.md
- Reordered sections to match template
- Removed duplicated goal text (kept in brief.md)
- Proposed split: 3 detail files under architecture/

### patterns.md
- Grouped patterns by domain: auth (2), data (3), UI (1)
- Removed duplicate convention also in architecture.md

### Cross-file fixes:
- state.md "Next Action" updated to match progress.md "In Progress"

Approve these changes? (yes / no / modify)
```

Wait for explicit approval before applying.

---

## Step 5: Apply Approved Changes

After user approves:

1. Create any new directories (`progress/`, `architecture/`, etc.)
2. Create archive/detail files first
3. Edit main files (replace content with summaries + links)
4. Update timestamps on all modified files

### Step 6: Refresh Managed Sections

```bash
python project-context/scripts/manage_context.py update-sections --file CLAUDE.md
python project-context/scripts/manage_context.py update-sections --file AGENTS.md
```

### Step 7: Summary

```
Optimization complete!

Operation: [Compact / Organize / Both]

Changes applied:
- [List of files modified]
- [List of new files created]
- [List of content removed/archived]

Context size: [before] → [after] lines ([X]% reduction)
```

## Edge Cases

### First run — no archive directories exist
Create `progress/`, `architecture/`, etc. as needed. No special handling.

### Very small context files
If all files are under 30 lines and well-structured, report: "Context files are already lean. No optimization needed."

### Mixed approval
User can approve some changes and reject others. Apply only approved changes.

### Files already have subdirectories
Respect existing structure. Don't re-split already-split files. Check if existing detail files need compacting themselves.

## Integration Points

This skill is suggested by:
- **`update` skill** — after adding new content, if files have grown significantly
- **`init` command** — when initializing context for an existing project with pre-existing files
