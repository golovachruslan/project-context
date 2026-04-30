# `dependencies.json` schema

The shared manifest used by `project-context-mini:dependency:add` (writes) and `project-context-mini:dependency:load` (reads + fetches).

## Location

`.project-context/dependencies.json` — committed to the project's repo.

## Top-level shape

```json
{
  "dependencies": [
    { ... entry ... },
    { ... entry ... }
  ]
}
```

A flat array. No upstream/downstream split — encode direction in `note` if needed.

## Entry fields

| Field | Required | Applies to | Description |
|-------|----------|------------|-------------|
| `name` | yes | all | Slug used as the subdirectory under `dependencies/`. Lowercase, dashes, no spaces. Must be unique within the manifest. |
| `type` | yes | all | One of `git`, `path`, `url`. Discriminates how `load` fetches. |
| `source` | yes | all | Git URL, relative path (from repo root), or HTTP(S) URL. |
| `ref` | optional | `git` only | Branch, tag, or commit. Default `main`. |
| `what` | optional | all | One-line description of what's shared / why it's a dependency. |
| `note` | optional | all | Free-form note. |

Drop optional fields entirely when empty — do not write `"what": ""` or `"note": null`.

## Examples

### `git` — remote repository

```json
{
  "name": "shared-types",
  "type": "git",
  "source": "https://github.com/org/shared-types.git",
  "ref": "main",
  "what": "Domain types and validation schemas",
  "note": "upstream"
}
```

`load` will sparse-checkout only the remote's `.project-context/` directory, copy its top-level `*.md` files into `.project-context/dependencies/shared-types/`, and discard the clone. No source code is transferred.

### `path` — monorepo sibling

```json
{
  "name": "sibling-app",
  "type": "path",
  "source": "../sibling-app",
  "what": "Shared auth helpers"
}
```

`load` resolves `<source>` relative to the repo root (the parent of `.project-context/`), reads `<source>/.project-context/`, and copies top-level `*.md` files into `.project-context/dependencies/sibling-app/`. No symlinks.

### `url` — single doc

```json
{
  "name": "rfc-001",
  "type": "url",
  "source": "https://example.com/rfcs/001-event-format.md",
  "what": "Event envelope spec"
}
```

`load` `WebFetch`-es the URL and saves the body to `.project-context/dependencies/rfc-001/001-event-format.md` (basename from the URL).

## Directory layout after `load`

```
.project-context/
├── dependencies.json                      ← committed
└── dependencies/                          ← gitignored (auto)
    ├── .gitignore                         ← committed (single line: !.gitignore)
    ├── shared-types/
    │   ├── architecture.md                ← copied from remote
    │   ├── flows.md
    │   ├── patterns.md
    │   ├── status.md
    │   └── .fetch-meta.json
    ├── sibling-app/
    │   ├── architecture.md
    │   ├── ...
    │   └── .fetch-meta.json
    └── rfc-001/
        ├── 001-event-format.md
        └── .fetch-meta.json
```

The `.gitignore` inside `dependencies/` is auto-written by `load`:

```
*
!.gitignore
```

This treats fetched content as a cache: not committed, regenerable, gitignored as a whole.

## `.fetch-meta.json` (per dep)

Written by `load` on every fetch attempt:

```json
{
  "name": "shared-types",
  "type": "git",
  "source": "https://github.com/org/shared-types.git",
  "ref": "main",
  "fetched_at": "2026-04-30T12:00:00Z",
  "result": "ok",
  "files": ["architecture.md", "flows.md", "patterns.md", "status.md"]
}
```

`result` is one of `ok`, `no_context` (target had no `.project-context/`), or `error` (with an additional `error` field carrying the message).

## Reading the manifest from skills

Both skills `Read` this reference at the start of their workflow. Mini does not ship a Python helper — `load` parses `dependencies.json` inline (e.g., via `jq` over `Bash` or via `Read` + JSON parse in the agent's reasoning).
