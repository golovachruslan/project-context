# Dependency Branch Workflows

## Branch A: Add Local Path Dependency

### A3. Resolve Target Project

**If path was provided:** validate it resolves to an existing directory. If not, report the error and stop.

**If path was NOT provided:** discover siblings and ask:

```bash
find .. -maxdepth 3 -name ".project-context" -type d 2>/dev/null
```

Use AskUserQuestion to present discovered siblings:
> "Which project?"
- List each sibling by name and relative path
- "Other" for manual path entry

### A4. Resolve Target Name and Description

1. Read `[target-path]/.project-context/brief.md` -> extract `**Project Name:**` for name, fall back to directory name
2. If `brief.md` exists, synthesize a concise one-line description from its Overview/intro section. Store as `[computed-description]`.
3. If `brief.md` is absent or has no clear overview -> set `[computed-description]` to `null` (omit field)

### A5-A7. Ask Direction, What, Notes

*(Same as shared steps 5-7 below.)*

### A8. Create or Update dependencies.json

Add a **local path entry**:
```json
{
  "project": "[target-name]",
  "path": "[relative-path]",
  "description": "[computed-description]",
  "what": "[what-shared]",
  "note": "[note or empty string]"
}
```

Omit `description` if `[computed-description]` is null.

### A9. Reciprocal Update

Use AskUserQuestion:
> "Update [target]'s dependencies.json with the reverse relationship?"
- **Yes (Recommended)** -- create or append the reverse entry
- **No** -- skip

If yes: apply the same create-or-append logic to `[target-path]/.project-context/dependencies.json` with the reversed direction (upstream <-> downstream) and the current project's name/path.

### A10. Confirmation

```
Added dependency:
  [current] --[direction]--> [target]
  Description: [computed-description]   <- omit line if not computed
  What: [what]

Files modified:
  OK .project-context/dependencies.json
  OK [target-path]/.project-context/dependencies.json (reciprocal)
```

---

## Branch B: Add Git Link Dependency

### B3. Resolve Git URL

**If URL was provided:** validate it looks like a git URL. If invalid, report and stop.

**If URL was NOT provided:** ask with AskUserQuestion:
> "What is the git repository URL?"
- User types the URL

### B4. Ask: Ref / Branch

Use AskUserQuestion:
> "Which branch or ref to track?"

Options:
- **main (Recommended)** -- default branch
- **master** -- legacy default
- **Custom** -- user types a branch name, tag, or commit

### B5. Resolve Project Name

Infer a default name from the git URL (last path segment without `.git`).

Use AskUserQuestion:
> "Project name? (inferred: [name-from-url])"

Options:
- **[name-from-url] (Recommended)** -- use inferred name
- **Custom** -- user types a name

### B6-B8. Ask Direction, What, Notes

*(Same as shared steps 5-7 below.)*

### B9. Create or Update dependencies.json

Add a **git link entry** (without `description` yet -- added in B10b after fetching):
```json
{
  "project": "[project-name]",
  "git": "[git-url]",
  "ref": "[branch-or-ref]",
  "what": "[what-shared]",
  "note": "[note or empty string]"
}
```

The `git` field distinguishes this from a local path dependency (which uses `path`).

### B10. Fetch Remote Project Context

After adding the entry, immediately fetch the remote `.project-context/`:

```bash
python project-context/scripts/fetch_git_deps.py fetch --dir . --project [project-name]
```

The script uses sparse-checkout (`--filter=blob:none --sparse`) to download only `.project-context/` from the remote -- no application code is transferred. It copies the context files into `.project-context/.deps-cache/[project-name]/`, then cleans up the clone. No `.git/` is retained.

### B10b. Auto-Compute Description

After fetching, read `.project-context/.deps-cache/[project-name]/brief.md` if it exists.

Synthesize a concise one-line description from its Overview/intro section. Store as `[computed-description]`.

If the fetch failed, or `brief.md` is absent, or there is no clear overview: set `[computed-description]` to `null`.

If `[computed-description]` is not null: read `dependencies.json`, add `"description": "[computed-description]"` to the entry, write back.

### B11. Confirmation

```
Added git dependency:
  [current] --[direction]--> [target] (via git)
  Git:  [git-url]
  Ref:  [ref]
  Description: [computed-description]   <- omit line if not computed
  What: [what]

Fetched remote context to .deps-cache/[project-name]/:
  OK brief.md
  OK architecture.md
  OK ...

Files modified:
  OK .project-context/dependencies.json
```

---

## Branch C: Fetch / Refresh Git Dependencies

Re-fetch cached context files for existing git link dependencies. Useful when the remote project has updated its `.project-context/`.

### C3. Run fetch script

**If a project name was provided after `--fetch`:** fetch only that one.

```bash
python project-context/scripts/fetch_git_deps.py fetch --dir . --project [name]
```

**If no project name:** fetch all git link dependencies.

```bash
python project-context/scripts/fetch_git_deps.py fetch --dir .
```

### C4. Report results

Show fetch results from the script output:

```
Fetched git dependencies:
  OK auth-service (3 files, ref: main)
  OK shared-types (4 files, ref: v2.1.0)
  FAIL payment-api -- git clone failed: ...
```

If no git link dependencies exist in `dependencies.json`:
> "No git link dependencies to fetch. Add one with `/project-context:add-dependency <git-url>`."

---

## Branch D: Clean Cache

Remove cached git dependency contexts.

### D3. Run clean

**If a project name was provided after `--clean`:** clean only that project.

```bash
python project-context/scripts/fetch_git_deps.py clean --dir . --project [name]
```

**If no project name:** clean all cached deps.

```bash
python project-context/scripts/fetch_git_deps.py clean --dir .
```

### D4. Confirm

```
Cleaned cached contexts:
  OK auth-service
  OK shared-types
```

---

## Shared Steps (Branches A and B)

### 5. Ask: Direction

Use AskUserQuestion:
> "What is the relationship between [current] and [target]?"

Options:
- **[current] consumes [target] (upstream)** -- "we import/use from them"
- **[target] consumes [current] (downstream)** -- "they import/use from us"

### 6. Ask: What is Shared

Use AskUserQuestion:
> "What does [current] [consume from / expose to] [target]?"

Options (common patterns -- user can pick or type custom):
- **Types / interfaces / schemas**
- **API endpoints (REST, GraphQL, gRPC)**
- **Shared utilities / helpers**
- **Database schemas / migrations**

### 7. Ask: Notes (optional)

Use AskUserQuestion:
> "Any additional notes for this dependency?"

Options:
- **No notes**
- **Custom** (user types)

### 8. Create or Update dependencies.json

#### If dependencies.json doesn't exist -- create it:

```json
{
  "upstream": [],
  "downstream": []
}
```

Then add the new entry to the correct array.

#### If dependencies.json exists -- read, append, write:

1. Read and parse the existing JSON
2. Append the new entry to the correct array (`upstream` or `downstream`)
3. Write back with `indent=2`

**Important:** Use the Write tool to write the full JSON file. Do NOT use Edit for JSON -- always read, modify in memory, write the whole file to avoid formatting issues.

---

## Edge Cases

### Target has no .project-context/ (local only)
> "The target has no `.project-context/`. Create one with just `dependencies.json`, or skip reciprocal?"

### Remote has no .project-context/ (git only)
> "The remote repository has no `.project-context/` directory. The entry was added to `dependencies.json`, but no context files were fetched. The remote project needs to run `/project-context:init` first."

### Duplicate dependency
If target already in the same direction's array (match by `project` field, or by `git` URL):
> "[target] is already listed as [direction]. Update the existing entry instead?"

### Self-dependency
Reject: "A project cannot depend on itself."

For git links: if the URL matches `.git/config` remote URL, suggest using local path instead.

### Invalid path
> "Path `[path]` doesn't exist. Check the path and try again."

### Network failure (git only)
> "Failed to fetch from [url]. The entry was added to `dependencies.json` but context was not fetched. Run `/project-context:add-dependency --fetch` to retry later."

### No reciprocal for git links
Git link dependencies do NOT offer reciprocal updates -- you cannot write to a remote repository.
