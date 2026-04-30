---
name: project-context-mini:dependency:add
description: "Register a dependency in .project-context/dependencies.json. Accepts a git URL, a relative monorepo path, or a raw HTTP(S) doc URL. Does NOT fetch — use project-context-mini:dependency:load to pull content. Triggers: 'add dependency', 'depends on', 'link source', 'add upstream', 'register dep', 'point to repo', 'add doc link', 'add sibling project'."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# Add a project-context-mini dependency

Append an entry to `.project-context/dependencies.json` describing an external source this project relies on. **This skill never makes network calls** — it only updates the manifest. Run `/project-context-mini:dependency:load` afterwards to fetch content.

**Clarify before acting:** if the source string is ambiguous (e.g., a GitHub HTTPS URL with no `.git` suffix that could be either a repo to clone or a single doc to fetch), the inferred name doesn't fit, or any field is unclear, use the `AskUserQuestion` tool to ask the user before proceeding. Prefer one batched question with concrete options over guessing or asking one-at-a-time. Do not fabricate intent.

## Arguments

- `<source>` (positional, optional) — git URL, relative path, or raw HTTP(S) URL. If omitted, the skill prompts.
- `--name <name>` (optional) — override the inferred name.
- `--ref <ref>` (optional, git only) — branch/tag/commit. Default `main`.
- `--what "<text>"` (optional) — one-line description of what's shared.
- `--note "<text>"` (optional) — free-form note.

## Workflow

### Step 1 — Verify context exists

```bash
ls .project-context/*.md 2>/dev/null
```

If `.project-context/` is missing or empty, exit with:

> No project-context-mini context found. Run `/project-context-mini:update` first to bootstrap.

### Step 2 — Resolve source

If `<source>` was not provided, ask the user (`AskUserQuestion`):

- "What kind of dependency are you adding?" — git repo / local path / raw doc URL
- "What is the source?" — free-form

### Step 3 — Detect type

Apply these rules in order to the source string:

| Rule | Match | Type |
|------|-------|------|
| Ends in `.git` | `*.git` | `git` |
| Starts with `git@` or `ssh://` | SSH form | `git` |
| Host is `github.com`, `gitlab.com`, or `bitbucket.org` AND path looks like `/<owner>/<repo>` (no file extension) | inferred repo | `git` (confirm) |
| Starts with `http://` or `https://` AND ends in a file extension (`.md`, `.txt`, `.pdf`, `.json`, `.yaml`, etc.) | doc URL | `url` |
| Starts with `./`, `../`, or `/`, OR is an existing directory on disk | path | `path` |
| Otherwise | ambiguous | ask |

**Ambiguous cases** (e.g., `https://github.com/org/repo` with no `.git`, or a bare host URL): use `AskUserQuestion` with options `git` and `url` and a one-line description of each.

### Step 4 — Infer a default name

- `git`: last path segment of the URL, stripped of `.git` (e.g., `https://github.com/org/shared-types.git` → `shared-types`).
- `path`: basename of the resolved path (e.g., `../shared` → `shared`).
- `url`: filename without extension (e.g., `.../001-events.md` → `001-events`).

Fall back to asking if the inferred name is empty or non-slug-friendly.

### Step 5 — Gather details (one batched question)

Use a single `AskUserQuestion` call to collect:

1. **Name** — present the inferred default; allow override.
2. **Ref** — only if type is `git`. Default `main`.
3. **What** — what's shared / why it's a dependency. Optional, free-form. Skip the question if `--what` was passed.
4. **Note** — optional. Skip if `--note` was passed.

Keep prompts terse. If the user gave the source as a CLI arg with `--name`/`--what`/`--note`/`--ref` flags, skip questions for those fields entirely.

### Step 6 — Read or initialize the manifest

```bash
cat .project-context/dependencies.json 2>/dev/null
```

If missing, initialize:

```json
{ "dependencies": [] }
```

### Step 7 — Check for duplicates

If an entry with the same `name` already exists, ask (`AskUserQuestion`): overwrite, rename, or abort.

If an entry with the same `source` exists under a different name, surface it as an info note before continuing.

### Step 8 — Append and write

Build the entry with these required fields plus any optional ones provided:

```json
{
  "name": "<name>",
  "type": "git" | "path" | "url",
  "source": "<source>",
  "ref": "<ref>",          // git only
  "what": "<text>",        // optional
  "note": "<text>"         // optional
}
```

Drop optional fields entirely when empty (do not write `"what": ""` or `"note": null`).

Write `.project-context/dependencies.json` with 2-space indent, trailing newline.

### Step 9 — Summary

Emit a terse confirmation:

```
Added dependency: <name> (<type>) → <source>
Run /project-context-mini:dependency:load <name> to fetch its context.
```

If type is `path`, mention that local paths still need `load` to copy the dep's `.project-context/` files into `.project-context/dependencies/<name>/`.

## Schema reference

Read `references/dependencies-schema.md` for the full schema, examples per type, and directory layout details.

## Edge cases

- **`.project-context/` missing** — exit with the bootstrap hint, do not create the directory.
- **`dependencies.json` exists but is malformed JSON** — show the parse error, do not overwrite. Ask the user to fix or to allow re-initialization.
- **Source is a path that doesn't exist on disk** — warn but allow the user to proceed (path may exist later when `load` runs).
- **Source is a git URL with auth required** — accept it as-is. `add` does not validate. `load` will surface the auth failure.
- **User passes a name with whitespace or special characters** — slugify (lowercase, dashes for spaces) and confirm the slug with the user before writing.
- **Manifest empty after duplicate-overwrite cancel** — exit cleanly with no changes.

## What this skill does NOT do

- No network calls. No `git ls-remote`, no `curl`, no `WebFetch`.
- No reading of the dep's content. (`load` does that.)
- No reciprocal updates to a sibling project's manifest. (Mini stays one-way.)
- No upstream/downstream split. Mini keeps a flat list; encode direction in `note` if it matters.
- No `--clean` or removal flag. Edit `dependencies.json` directly to remove an entry.
