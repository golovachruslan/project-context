# Step 6: Commit Changes

After all context updates and propagations are applied, offer to commit.

## 6a. Detect Git Roots

```bash
# Your project's git root
git rev-parse --show-toplevel

# Each downstream dep's git root (for propagated deps only)
git -C {dep-path} rev-parse --show-toplevel 2>/dev/null
```

Group downstream deps by whether their git root matches yours:
- **Same root** → can be included in one commit with your changes
- **Different root** → requires a separate branch + commit in their repo

## 6b. Ask Commit Confirmation

Present a summary of what will be committed:

```
Commit context changes?

  This repo:
    .project-context/architecture.md
    .project-context/progress.md
    ../web/.project-context/state.md   <- same git root

  ../mobile/ (separate repo):
    .project-context/state.md          <- will create branch context/upstream-{name}-{date}
```

Use AskUserQuestion:
- **Yes** — commit all
- **Skip** — leave files modified, do not commit

If user skips → show summary of modified files and exit.

## 6c. Commit Same-Root Changes

Stage and commit all same-root files together:

```bash
git add .project-context/ {same-root-dep-paths...}
git commit -m "chore(context): update {project-name} context + propagate to {dep-names}"
```

## 6d. Commit Different-Root Deps

For each separate-repo downstream dep that was propagated to:

```bash
# Determine branch name
BRANCH="context/upstream-{current-project-name}-{YYYY-MM-DD}"

# Check if branch already exists
git -C {dep-path} branch --list {BRANCH}
# If exists → reuse it (checkout, amend or add new commit)
# If not → create it

git -C {dep-path} checkout -b {BRANCH}   # or: checkout {BRANCH} if already exists
git -C {dep-path} add .project-context/state.md
git -C {dep-path} commit -m "chore(context): upstream changes from {current-project-name} ({YYYY-MM-DD})"
git -C {dep-path} checkout -   # return to their previous branch
```

If the downstream repo has a conflict on checkout (rare — only if state.md has staged/conflicting changes):
```
Could not create branch in ../mobile — working tree has conflicts on .project-context/state.md.
File was modified but not committed. Please commit or stash changes in ../mobile first.
```

## 6e. Final Summary

```markdown
## Done

Context updates applied:
  [check] .project-context/architecture.md
  [check] .project-context/progress.md

Propagated to:
  [check] web — state.md updated
  [check] mobile — state.md updated

Commits:
  [check] This repo — "chore(context): update api context + propagate to web"
  [check] ../mobile — branch context/upstream-api-2026-02-21 created
```
