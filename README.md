# pctx

CLI tool for managing [project-context](https://github.com/golovachruslan/project-context) cross-project dependencies.

Run without installing:

```sh
npx pctx <command>
```

Or install globally:

```sh
npm install -g pctx
```

The binary is `pc`.

## Requirements

- Node.js 18+
- git 2.25+ (for `fetch-deps`)

## Commands

### `pc list-deps`

List all declared dependencies with their type, direction, and status.

```sh
pc list-deps
pc list-deps --json        # machine-readable output
pc list-deps --dir ./app   # specify project root
```

**Output example:**
```
Dependencies (2)
┌────────────────┬─────────────────┬───────┬──────────────────────────────┬──────────────┐
│ Project        │ Direction       │ Type  │ Location                     │ Status       │
├────────────────┼─────────────────┼───────┼──────────────────────────────┼──────────────┤
│ shared-types   │ ↑ upstream      │ local │ ../shared-types              │ ok           │
│ auth-service   │ ↓ downstream    │ git   │ github.com/org/auth @main    │ cached       │
└────────────────┴─────────────────┴───────┴──────────────────────────────┴──────────────┘
```

---

### `pc add-dep [path-or-url]`

Add a new dependency interactively. Detects local paths vs git URLs automatically.

```sh
pc add-dep                                          # fully interactive
pc add-dep ../shared-types                          # local sibling project
pc add-dep https://github.com/org/auth-service.git  # remote git repo
```

**Local dependency flow:**
1. Discovers sibling projects with `.project-context/`
2. Prompts for direction (upstream/downstream), what is shared, and notes
3. Writes to `dependencies.json`
4. Optionally updates the target project's `dependencies.json` (reciprocal)

**Git dependency flow:**
1. Prompts for branch/ref to track
2. Confirms/overrides inferred project name
3. Prompts for direction, what is shared, and notes
4. Writes to `dependencies.json`
5. Auto-fetches `.project-context/` from the remote and caches it
6. Computes description from remote `brief.md`

---

### `pc fetch-deps [project]`

Fetch (or refresh) `.project-context/` files from git dependencies using git sparse-checkout. Only the `.project-context/` directory is downloaded — no application code.

```sh
pc fetch-deps                     # fetch all git dependencies
pc fetch-deps auth-service        # fetch a specific dependency
pc fetch-deps --json              # JSON output
```

Cached files are stored at `.project-context/.deps-cache/<project>/`.
A `.fetch-meta.json` file tracks the fetch timestamp and file list.
Cache entries older than 7 days are flagged as stale in `list-deps`.

---

## `dependencies.json` Format

`pc` reads and writes `.project-context/dependencies.json`:

```json
{
  "upstream": [
    {
      "project": "shared-types",
      "path": "../shared-types",
      "description": "Shared TypeScript types used across services",
      "what": "Types, interfaces, schemas",
      "note": ""
    }
  ],
  "downstream": [
    {
      "project": "auth-service",
      "git": "https://github.com/org/auth-service.git",
      "ref": "main",
      "description": "Authentication microservice",
      "what": "API endpoints",
      "note": ""
    }
  ]
}
```

This format is 100% compatible with the [project-context Claude Code plugin](https://github.com/golovachruslan/project-context).
