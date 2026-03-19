---
name: project-context:add-dependency
description: "Use when users want to add, declare, connect, fetch, or refresh cross-project dependencies — local paths (monorepo) or git URLs (remote repos). Triggers: 'add dependency', 'depends on', 'consumed by', 'this project uses', 'connect projects', 'add upstream', 'add downstream', 'link projects', 'git dependency', 'remote dependency', 'fetch deps', 'refresh deps', 'update deps', 'sync deps'."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - AskUserQuestion
---

# Cross-Project Dependency Management

Single command for all dependency operations: add new dependencies (local path or git URL), fetch/refresh cached git contexts, and clean stale caches.

## Parameter

One optional parameter: a path, git URL, or action keyword.

```
/project-context:add-dependency ../shared
/project-context:add-dependency https://github.com/org/auth-service.git
/project-context:add-dependency --fetch
/project-context:add-dependency --fetch auth-service
/project-context:add-dependency --clean
/project-context:add-dependency              # no argument — interactive
```

## Workflow

### 1. Detect Current Subproject

```bash
ls .project-context/*.md .project-context/*.json 2>/dev/null
```

If no `.project-context/` exists:
> "No project context found. Run `/project-context:init` first."

Read `brief.md` if available to get the current project name.

### 2. Determine Intent

**If argument starts with `--fetch`:**  → Branch C (fetch/refresh git deps)
**If argument starts with `--clean`:**  → Branch D (clean cache)
**If argument is a git URL** (starts with `https://`, `git@`, `ssh://`, or ends with `.git`): → Branch B (add git link)
**If argument is a path:** → Branch A (add local path)

**If no argument was provided**, ask with AskUserQuestion:
> "What do you want to do?"

Options:
- **Add local dependency (Recommended)** — "Sibling project in this monorepo"
- **Add git dependency** — "Remote repository — only .project-context/ will be fetched"
- **Fetch/refresh git deps** — "Update cached contexts from remote repos"

Then proceed to the matching branch below.

---

## Branch Workflows

For detailed step-by-step instructions for each branch (A: local path, B: git link, C: fetch/refresh, D: clean cache), shared steps (direction, what, notes, dependencies.json management), and edge cases, see `references/branch-workflows.md`.
