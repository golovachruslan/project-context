---
name: project-context:validate
description: Validate project context files for completeness, freshness, and Mermaid syntax
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

# Validate Project Context

Check project context files for completeness, accuracy, and potential staleness.

## Workflow

### Step 1: Check Files Exist

```bash
ls -la .project-context/*.md 2>/dev/null
```

**Expected files:**
- `.project-context/brief.md`
- `.project-context/architecture.md`
- `.project-context/progress.md`
- `.project-context/patterns.md`

Report any missing files.

### Step 1b: Check Dependencies (if present)

If `.project-context/dependencies.json` exists:

```bash
cat .project-context/dependencies.json
```

Validate:
- Valid JSON with `upstream` and `downstream` arrays
- Each entry has `project`, `what`, and either `path` or `git` (never both)
- If `description` is present, it must be a non-empty string
- For local path deps: path exists and target directory has `.project-context/`
- For git link deps: `.project-context/.deps-cache/<project>/` exists
- No orphaned cache entries (directories in `.deps-cache/` not declared in `dependencies.json`)

Check git dep cache freshness:
```bash
cat .project-context/.deps-cache/*/.fetch-meta.json 2>/dev/null
```
Warn if any `fetched_at` timestamp is >7 days old.

### Step 2: Check File Content

For each file, verify:

#### brief.md
- [ ] Has "Overview" section with content
- [ ] Has "Goals" section with at least 1 goal
- [ ] Has "Scope" section

#### architecture.md
- [ ] Has "Tech Stack" section with content
- [ ] Has at least 1 Mermaid diagram
- [ ] Each diagram has a description/steps section
- [ ] Has "Key Decisions" section

#### progress.md
- [ ] Has "Current Focus" with content
- [ ] Has "Status" section
- [ ] Has "Completed" or "In Progress" items

#### patterns.md
- [ ] Has at least one pattern or learning documented

### Step 3: Validate Mermaid Syntax

Read architecture.md and check each Mermaid code block:

```bash
# Extract mermaid blocks and validate basic syntax
grep -A 20 '```mermaid' .project-context/architecture.md
```

**Common Mermaid issues to check:**
- Unclosed code blocks
- Missing diagram type declaration (graph, sequenceDiagram, etc.)
- Invalid arrow syntax
- Unbalanced brackets/parentheses

### Step 4: Check Freshness

For each file, extract "Last updated" timestamp and compare to:
- Current date
- Recent git commits

```bash
# Get file modification times
stat -f "%Sm" .project-context/*.md 2>/dev/null || stat -c "%y" .project-context/*.md

# Get recent commit dates
git log --oneline -5 --format="%ci" 2>/dev/null | head -5
```

**Freshness thresholds:**
- `progress.md` - Warn if >3 days old
- `architecture.md` - Warn if >7 days old with code changes
- `patterns.md` - Warn if >14 days old
- `brief.md` - OK if stable

### Step 5: Check for Stale References

Look for potential stale content:

```bash
# Find files/directories mentioned in context
grep -oE '\b[A-Za-z0-9_-]+\.(ts|js|py|md|json)\b' .project-context/*.md | sort -u

# Check if they still exist
# Compare against actual codebase
```

Report any referenced files that no longer exist.

### Step 6: Generate Report

Output a validation report:

```markdown
## Project Context Validation Report

### File Status
| File | Exists | Content | Last Updated | Status |
|------|--------|---------|--------------|--------|
| brief.md | ✓ | ✓ | 2024-01-15 | OK |
| architecture.md | ✓ | ✓ | 2024-01-10 | ⚠️ Stale |
| progress.md | ✓ | ✓ | 2024-01-14 | OK |
| patterns.md | ✓ | ✗ | 2024-01-01 | ⚠️ Empty |

### Dependencies
*(Omit section if no `dependencies.json`)*
| Dependency | Type | Direction | Status |
|---|---|---|---|
| shared | local | upstream | ✓ Path valid, has `.project-context/` |
| auth-service | git | upstream | ⚠️ Cache stale (12 days) — run `--fetch` |
| web-app | local | downstream | ✓ Path valid |

### Issues Found
1. **architecture.md**: Last updated 5 days ago, but 12 files changed since
2. **patterns.md**: No patterns documented yet

### Mermaid Diagrams
- Found 2 diagrams in architecture.md
- Syntax: ✓ Valid

### Recommendations
1. Run `/project-context:update architecture --scan` to refresh architecture
2. Add patterns to patterns.md based on recent work
```

## Validation Levels

### Critical Issues (must fix)
- Missing required files
- Empty files
- Invalid Mermaid syntax

### Warnings (should address)
- Stale content (outdated timestamps)
- Missing recommended sections
- Referenced files that don't exist

### Suggestions (nice to have)
- Add more diagrams
- Document more patterns
- Update progress more frequently

## Exit Codes

For scripting purposes:
- All valid: "✓ All context files valid"
- Has warnings: "⚠️ Context valid with warnings"
- Has errors: "✗ Context validation failed"
