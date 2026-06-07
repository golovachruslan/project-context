---
name: project-wiki:lint
description: "Health-check a project-wiki vault and keep it self-maintaining. Wraps wiki_lint.py + wiki_stats.py: finds broken [[wikilinks]], orphan pages, pages missing mandatory sources, over-budget files, uncompiled raw sources, and shard thresholds. With --fix, relocates over-budget content, prunes dead links, shards oversized indexes, and regenerates the dependencies.md graph. Triggers: 'lint the wiki', 'check wiki health', 'wiki stats', 'clean up the wiki', 'fix the wiki'."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Lint project-wiki

Check vault health and optionally repair it. Findings are presented as proposed edits — the wiki is never rewritten silently.

## Arguments

- `--fix` — apply mechanical fixes + budget enforcement (with approval).
- `--stats` — show growth metrics + scaling-threshold warnings.
- `--project <slug>` — limit to one project.
- `--vault <path>` — see Step 0.

## Step 0 — Resolve vault

Resolve the vault path (`--vault` → `PROJECT_WIKI_VAULT` → `.project-wiki` marker → ask).

## Step 1 — Run the checks

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/wiki_lint.py <vault> [--project <slug>] --json
```

The script reports three tiers:
- **critical** — broken `[[wikilinks]]`; page missing mandatory `sources:`; hot file over hard budget; wiki page > 800 lines; required project file missing.
- **warning** — orphan pages; uncompiled raw sources; stale pages; wiki page > 400-line soft cap; index/page-count near a shard threshold.
- **suggestion** — thin pages; missing optional frontmatter.

Present grouped by tier. If `--stats` (or always, briefly), also run:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/wiki_stats.py <vault> [--project <slug>]
```

## Step 2 — `--fix` (only with approval)

The script reports; the skill repairs. Show the planned fixes and get approval (`AskUserQuestion`) before writing. Apply only mechanical, safe fixes:

- **Dead links** — remove or, when an obvious rename target exists, repoint the `[[link]]`.
- **Missing index entries** — add the page's one-line summary to the project `index.md`.
- **Over-budget files** — relocate per the schema (split big wiki pages into `<type>/<topic>/refs/`; move old `progress.md` items to `progress/archive.md`; push `_project.md` detail to a wiki page), leaving `[[link]]` pointers.
- **Oversized index** — shard `index.md` into `indexes/<type>.md` and leave a pointer.
- **Dependency graph** — regenerate `dependencies.md` from every `_project.md`'s `## Dependencies` section (mermaid graph + edge list).

**Do NOT** auto-fix things that need judgment: a missing `sources:` (the content may be fabricated — flag it for the user/`ingest` to resolve), contradictions, or orphan pages whose deletion is a content decision. Surface these for the user.

## Step 3 — Summary + log

Print a terse summary (counts per tier, what was fixed). Append a `lint` line to `log.md` if fixes were applied.

## Edge cases

- **`sources:` missing on many pages** — likely the wiki was hand-edited or imported. Don't bulk-delete; report and suggest re-ingesting those sources.
- **Broken link is a typo of a real page** — propose the repoint rather than deletion.
- **Not a vault** — if `wiki_lint.py` reports no `projects/`, tell the user to run `/project-wiki:init`.
