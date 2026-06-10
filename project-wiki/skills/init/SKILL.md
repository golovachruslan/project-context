---
name: project-wiki:init
description: "Scaffold a project-wiki vault, or add a new project to an existing one. Creates the Karpathy LLM-wiki layout (index, log, dependencies, typed wiki folders), and inserts a managed schema block into the vault's CLAUDE.md / AGENTS.md without clobbering user content. Triggers: 'init wiki', 'set up knowledge base', 'create project wiki', 'add project to wiki', 'new wiki project'."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - AskUserQuestion
---

# Initialize project-wiki

Scaffold a vault, or add a project to one. Templates and the canonical schema block live in `references/vault-scaffolds.md` — **read it first**.

**Clarify before acting:** if the vault path, project name, or dependency wiring is ambiguous, ask with `AskUserQuestion` (one batched question, concrete options). Never overwrite an existing file you didn't just create.

## Step 0 — Resolve the vault path

The vault is a **separate git repo** from any code project. Resolve in order:
1. `--vault <path>` argument.
2. `PROJECT_WIKI_VAULT` environment variable.
3. A `.project-wiki` marker file in the current directory (read the path from it).
4. Otherwise `AskUserQuestion`: ask where the vault is / should be created.

## Mode A — Scaffold a new vault (`init`)

Run when the resolved path has no `index.md` / `projects/`.

1. Read `references/vault-scaffolds.md`.
2. Create the structure: `index.md`, `log.md`, `dependencies.md`, `_templates/{project,wiki-page,raw-source,person}.md`, `people/index.md` (people catalog), and an empty `projects/` directory.
3. **CLAUDE.md and AGENTS.md (managed sections):** for each, insert/refresh the `<!-- PROJECT-WIKI:START -->…<!-- PROJECT-WIKI:END -->` block from the scaffolds reference.
   - If the file exists: replace only the block between the markers (or append the block if absent). **Everything outside the markers is left byte-for-byte intact.**
   - If the file doesn't exist: create it containing just the block.
   - Use the same approach as `project-context/scripts/manage_context.py update-sections` (regex replace between markers).
4. Suggest `git init` in the vault if it isn't already a repo, and offer to write a `.project-wiki` marker in the user's working dir so future runs auto-resolve the path.
5. Print the layout and suggest `init --project <name>` next.

## Mode B — Add a project (`init --project <name>`)

Run to add `projects/<slug>/` (slug = kebab-cased name).

1. If the slug already exists, stop and say so (offer to `ingest` into it instead).
2. **Ask the five seed questions** (from the scaffolds reference) in one batch: name & summary, source repo(s), Slack channel(s), docs, dependencies (upstream/downstream).
3. Create `projects/<slug>/` with `_project.md` (from the project template, prefilled), `index.md`, `progress.md`, `refs.md` (prefill repo/Slack/docs — these are the router's signals), and empty `raw/` + `wiki/{sources,concepts,entities,poc,decisions,notes}/`.
4. Add the project to the global `index.md` (`- [[projects/<slug>/_project]] — <summary>`).
5. **Wire dependencies (Obsidian-native):** for each declared upstream/downstream, add a `[[projects/<other>/_project]]` link under the `## Dependencies` section of this project's `_project.md`, and add the reciprocal link to the other project's `_project.md` if it exists. Then regenerate `dependencies.md` (or run `/project-wiki:lint --fix` to rebuild the graph).
6. Append a line to `log.md`.

## Step — Confirm

Show what was created. For Mode B, suggest `/project-wiki:ingest` to start adding knowledge.

## Edge cases

- **Partial vault** (some vault files missing) — create only what's missing; never overwrite existing files.
- **CLAUDE.md/AGENTS.md already managed by another tool** (e.g. project-context uses `PROJECT-CONTEXT` markers) — that's fine; our `PROJECT-WIKI` markers are independent. Touch only our block.
- **Dependency target project doesn't exist yet** — add the link anyway (lint will flag it until the project is created) and note it to the user.
