# Organize Patterns

Detailed rules for organizing and restructuring project context files.

## Normalization Rules

### Template Compliance

Each file must match its canonical template from `references/file-templates.md`:

| File | Required Sections | Required Metadata |
|------|-------------------|-------------------|
| brief.md | Overview, Goals, Scope (In/Out) | Last updated timestamp |
| architecture.md | Tech Stack, System Overview (Mermaid), Key Decisions | Last updated timestamp |
| state.md | Current Position, Session Info, Blockers, Decisions Pending, Next Action | Last updated timestamp |
| progress.md | Completed, In Progress, Upcoming, Known Issues | Last updated timestamp |
| patterns.md | Code Patterns, Naming Conventions, Learnings, Anti-Patterns | Last updated timestamp |

### Section Ordering

Sections must appear in the order listed above. If a file has extra sections (project-specific), they go after the template sections.

### Missing Sections

Add missing sections with empty placeholders:
```markdown
## Anti-Patterns
- None documented yet
```

## Deduplication Rules

### Ownership Matrix

When content appears in multiple files, the **owner** keeps it and others get a reference or removal:

| Content Type | Owner | Remove From |
|-------------|-------|-------------|
| Project goals, vision, scope | brief.md | architecture.md, state.md |
| Tech stack, component design | architecture.md | brief.md, patterns.md |
| Architecture decisions ("we chose X") | architecture.md | patterns.md (unless it's a coding pattern) |
| Coding patterns, conventions | patterns.md | architecture.md |
| Current status, blockers | state.md | progress.md (progress tracks tasks, not status) |
| Task completion history | progress.md | state.md (state keeps only "Recently Completed" summary) |
| Known issues | progress.md | state.md (unless it's a blocker) |

### Borderline Cases

- **"We use React with TypeScript"** — architecture.md owns the tech choice; patterns.md can document React-specific coding patterns
- **"Fixed auth bug by adding null check"** — progress.md owns the completion; patterns.md owns the pattern ("always null-check auth tokens")
- **Blocker that's also a known issue** — state.md owns the blocker; progress.md can reference it in Known Issues with a note "see state.md Blockers"

## Semantic Grouping

### patterns.md Grouping

Group patterns by domain rather than chronological order:

```markdown
## Code Patterns

### Authentication
- [Pattern 1]
- [Pattern 2]

### Data Access
- [Pattern 3]

### Error Handling
- [Pattern 4]
```

### architecture.md Grouping

Group decisions by component area:

```markdown
## Key Decisions

### Frontend
| Decision | Choice | Rationale | Date |

### Backend
| Decision | Choice | Rationale | Date |

### Infrastructure
| Decision | Choice | Rationale | Date |
```

### progress.md Grouping

Completed items grouped by feature (especially useful before archiving):

```markdown
## Completed

### Auth System
- [x] JWT middleware (2026-03-01)
- [x] Login endpoint (2026-03-02)
- [x] Token refresh (2026-03-03)

### Dashboard
- [x] Layout component (2026-03-05)
```

## Cross-File Consistency Checks

### Alignment Rules

| Check | How to Verify | Fix |
|-------|--------------|-----|
| state.md "Next Action" vs progress.md | Next action should relate to an "In Progress" or "Upcoming" item | Update state.md to match progress.md, or flag the mismatch |
| state.md "Active Plan" vs plans/ | Referenced plan file must exist | Update state.md if plan was completed/removed |
| architecture.md components vs progress.md | New components in architecture should be reflected in progress | Add missing progress entries, or note "pre-existing" |
| patterns.md conventions vs actual code | Documented conventions should reflect current practice | Flag outdated patterns for user review |
| state.md "Blockers" vs progress.md "Known Issues" | Active blockers should appear in Known Issues | Sync both, or note one references the other |

### Timestamp Consistency

All files should have "Last updated" timestamps. If a file's content has clearly changed (based on git history) but the timestamp is old, update it to today.

## File Splitting Rules

### When to Split

Split a file when:
- It exceeds ~100 lines
- It has 5+ substantial sections (>10 lines each)
- Distinct topics are mixed together (e.g., frontend and backend architecture in one file)

### How to Split

1. **Create subdirectory** with same name as the file (without extension):
   - `architecture.md` → `architecture/`
   - `patterns.md` → `patterns/`
   - `progress.md` → `progress/` (for archives)

2. **Extract detail sections** into individual files:
   - Each file covers one topic
   - Self-contained with its own heading
   - Includes enough context to be useful standalone

3. **Main file becomes summary + index:**
   ```markdown
   ## API Design
   RESTful API with JWT auth, rate limiting, and versioned endpoints.
   See [API Design Details](architecture/api-design.md) for full specification.
   ```

4. **Naming convention:** hyphen-case topic name matching the section it was extracted from

### What NOT to Split

- **state.md** — Must stay compact and single-file (it's read every session)
- **brief.md** — Rarely large enough to warrant splitting
- **Files under 60 lines** — Not worth the indirection
- **dependencies.json** — Single JSON file, not splittable

### Split File Template

```markdown
# [Topic Name]

> Extracted from [parent-file.md] — [Section Name]

[Detailed content moved from parent file]

---
*Last updated: YYYY-MM-DD*
```

## Consolidation: state.md + progress.md

These two files have natural overlap. Organize the boundary:

### state.md owns:
- Current focus (what's happening RIGHT NOW)
- Active plan reference
- Session info (last session context)
- Active blockers
- Pending decisions
- Next action

### progress.md owns:
- Full task history (completed, in progress, upcoming)
- Known issues (including non-blocking ones)
- Feature archive links

### Overlap resolution:
- If state.md lists completed work in "Recently Completed": keep as max 3 one-liners, link to progress.md for full history
- If progress.md has blocker info: move active blockers to state.md, keep only non-blocking issues in progress.md "Known Issues"
