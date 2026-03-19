# Step 5: Propagate to Downstream Dependencies

After applying updates, check if any downstream local-path dependencies exist and if changes are relevant to them.

## 5a. Check for Downstream Deps

Read `.project-context/dependencies.json` (if it exists):

```bash
cat .project-context/dependencies.json 2>/dev/null
```

If no `downstream` entries exist, or all downstream entries are git URLs (have a `git` field) → skip this step entirely.

Only local-path downstream deps (entries with a `path` field) are eligible for propagation.

## 5b. Determine What Changed

Compare the files that were just updated against each downstream dep's `what` field to assess relevance.

**Relevance mapping:**

| Changed file | Relevant if `what` mentions |
|---|---|
| `architecture.md` | API, endpoints, schema, interface, contract, integration, architecture, structure |
| `brief.md` | requirements, goals, scope, vision, purpose |
| `patterns.md` | patterns, conventions, standards, practices |
| `progress.md` | *(rarely relevant to downstream — skip unless `what` mentions milestones)* |
| `state.md` | *(rarely relevant — skip)* |

If no changed files are relevant to any downstream dep's `what` field → skip propagation silently.

## 5c. Ask User Confirmation

Present only the downstream deps with relevant changes:

```
Your context changes may affect downstream projects:

  [package] web — consumes: API types, REST endpoints
     Relevant changes: architecture.md (new /users/bulk endpoint)

  [package] mobile — consumes: API types, push notification schemas
     Relevant changes: architecture.md (new /users/bulk endpoint), brief.md (scope change)

Propagate upstream changes to these projects?
```

Use AskUserQuestion with options:
- **Yes, all** — propagate to all listed projects
- **Pick** — ask per-project (Yes/No for each)
- **Skip** — do not propagate

## 5d. Build Propagation Entry

For each confirmed downstream project, compose a concise entry summarizing what changed and what action may be needed:

```markdown
## Upstream Changes (from: {current-project-name}, {YYYY-MM-DD})

- **{changed-file}**: {brief description of what changed}
- **Action needed**: {what the downstream project may need to update}
```

Infer the current project name from `.project-context/brief.md` (`**Project Name:**` field) or fall back to the current directory name.

## 5e. Append to Downstream state.md

For each confirmed downstream project:

1. Check the target path exists:
   ```bash
   ls {dep-path}/.project-context/state.md 2>/dev/null
   ```
   If `state.md` does not exist → skip with a warning: `"{dep-path} has no state.md — skipping propagation"`

2. Read the current `state.md`

3. Check if an `## Upstream Changes` section already exists:
   - If yes → append new entry below the existing ones (keep history)
   - If no → append a new `## Upstream Changes` section at the end of the file

4. Use Edit tool to apply the change.
