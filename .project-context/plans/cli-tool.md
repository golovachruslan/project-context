# Plan: `pc` CLI Tool for Project-Context Dependency Management

**Status:** Completed
**Created:** 2026-03-19

## Overview

Standalone Node.js CLI tool (`npx pc`) that replaces the existing Python scripts (`fetch_git_deps.py`, `manage_context.py`) and provides interactive dependency management for the project-context ecosystem. Users can list, add, and fetch cross-project dependencies without being inside a Claude Code session.

## Commands

| Command | Description | Interactive |
|---------|-------------|-------------|
| `pc list-deps` | List all dependencies (upstream + downstream) with status | No (table output) |
| `pc add-dep` | Add a new dependency (local path or git URL) | Yes (prompts) |
| `pc add-dep <path-or-url>` | Add dependency with path/URL argument | Partially |
| `pc fetch-deps` | Fetch/refresh all git dependency caches | No (progress output) |
| `pc fetch-deps <project>` | Fetch specific git dependency | No |

Future commands (out of scope for now):
- `pc status` - context file health
- `pc validate` - full context validation

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | TypeScript | Type safety, same ecosystem as consumers |
| CLI framework | citty (UnJS) | Lightweight, modern, subcommands, auto-help |
| Interactive prompts | @inquirer/prompts | Mature, arrow-key selection, checkboxes |
| Output formatting | chalk + cli-table3 | Colored output, table formatting |
| Git operations | execa | Shell out to git (sparse-checkout) |
| Build | unbuild (UnJS) | Pairs with citty, produces CJS+ESM |
| Package manager | pnpm | Matches UnJS ecosystem conventions |

## Project Structure

```
cli/
  package.json          # name: "pc", bin: { "pc": "./bin/pc.mjs" }
  tsconfig.json
  build.config.ts       # unbuild configuration
  bin/
    pc.mjs              # Entry point (shebang + import)
  src/
    index.ts            # Main CLI definition (citty app)
    commands/
      list-deps.ts      # pc list-deps
      add-dep.ts        # pc add-dep [path-or-url]
      fetch-deps.ts     # pc fetch-deps [project]
    lib/
      context.ts        # Find .project-context/, read context files
      deps.ts           # Parse/write dependencies.json
      git.ts            # Git operations (sparse-checkout fetch)
      cache.ts          # .deps-cache management, .fetch-meta.json
      display.ts        # Shared formatting (tables, colors, spinners)
      prompts.ts        # Shared prompt helpers (direction, what, notes)
    types.ts            # Shared types (Dependency, DepsConfig, etc.)
```

## Implementation Phases

### Phase 1: Project Scaffold + Core Library
**Goal:** Working project structure with core dependency parsing

1. Initialize package.json with citty, TypeScript, unbuild
2. Create tsconfig.json, build.config.ts
3. Implement `src/types.ts` - dependency types from dependencies.json schema
4. Implement `src/lib/context.ts` - find .project-context/, read files
5. Implement `src/lib/deps.ts` - parse/write dependencies.json
6. Implement `src/index.ts` - citty main command with subcommand routing
7. Create `bin/pc.mjs` entry point

**Verify:** `npx tsx src/index.ts --help` shows help with subcommands

### Phase 2: Read-Only Command (list-deps)
**Goal:** Users can inspect their dependency state

1. Implement `pc list-deps` - table of all deps with direction, type (local/git), status
2. Implement `src/lib/display.ts` - shared table/color formatting

**Verify:** Running against a project with dependencies.json shows correct output

### Phase 3: Git Operations (fetch-deps)
**Goal:** Replace fetch_git_deps.py with Node.js implementation

1. Implement `src/lib/git.ts` - exec git sparse-checkout clone, copy context files
2. Implement `src/lib/cache.ts` - manage .deps-cache/, .fetch-meta.json, .gitignore
3. Implement `pc fetch-deps` - fetch all or single git dependency with progress

**Verify:** `pc fetch-deps` clones remote .project-context/ and caches it identically to Python script

### Phase 4: Interactive Command (add-dep)
**Goal:** Users can add dependencies interactively

1. Implement `src/lib/prompts.ts` - reusable prompt flows (direction, what, notes)
2. Implement `pc add-dep` - full add workflow:
   - Detect intent from argument (path vs URL vs interactive)
   - Local: discover siblings, prompt direction/what/notes, write deps.json, offer reciprocal
   - Git: prompt ref/name, write deps.json, auto-fetch, compute description from brief.md
3. Handle edge cases: duplicates, self-dependency, missing .project-context/

**Verify:** `pc add-dep ../sibling` and `pc add-dep https://github.com/org/repo.git` both work end-to-end

### Phase 5: Build, Publish Config, Polish
**Goal:** Ready for `npx pc` usage

1. Configure unbuild for proper CJS+ESM output
2. Test `npx .` works locally
3. Add --json flag to list-deps for machine-readable output
4. Add --help descriptions for all commands and flags
5. Error handling polish (friendly messages, exit codes)
6. README with usage examples

**Verify:** `npm pack` + `npx ./pc-*.tgz list-deps` works correctly

## Key Design Decisions

1. **Explicit `-dep`/`-deps` suffix on commands** - Makes it clear these are dependency operations, leaves room for future non-dep commands (status, validate, init).
2. **Minimal command set** - Only three commands (list-deps, add-dep, fetch-deps). update-dep and clean-deps dropped — users can edit JSON or rm the cache directory for those rare operations.
3. **No Python dependency** - Full Node.js rewrite, not a wrapper. Users only need Node.js.
4. **Git via execa** - Shell out to git rather than using a JS git library (isomorphic-git). Keeps the CLI lightweight and uses the user's git config/credentials.
5. **Same dependencies.json format** - 100% compatible with existing Python scripts and Claude Code skill. No migration needed.
6. **Same cache structure** - `.deps-cache/<project>/` with `.fetch-meta.json` - identical to Python output.
7. **Interactive by default, scriptable with flags** - `--json` for CI, interactive prompts for humans.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Git sparse-checkout behavior differs across versions | Test with git 2.25+ (when sparse-checkout was added), document minimum version |
| Package name `pc` may be taken on npm | Check npm registry, fall back to `pctx` or `@project-context/cli` |
| citty is less mature than commander/yargs | citty is actively maintained by UnJS team, simple API surface reduces risk |
| Large repos slow to sparse-checkout | Use `--depth 1 --filter=blob:none` (same as Python), add timeout |

## Success Criteria

- [ ] `npx pc list-deps` shows dependencies in a formatted table
- [ ] `npx pc add-dep ../sibling` adds a local dependency interactively
- [ ] `npx pc add-dep https://github.com/org/repo.git` adds a git dependency and fetches context
- [ ] `npx pc fetch-deps` refreshes all git caches (same output as Python script)
- [ ] Zero Python dependency
- [ ] dependencies.json format is 100% compatible with existing system
