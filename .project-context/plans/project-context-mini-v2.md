# Plan: `project-context-mini` v2 — dir consolidation, lazy refs, discuss rename

**Created:** 2026-04-27
**Status:** Implemented on branch `project-context-mini-v2`; awaiting PR + smoke test.

## Goal

Three follow-up changes after v1 (PR #13, merged):

1. Use `.project-context/` instead of `.project-context-mini/` for artifact storage.
2. Lazy refs loading in the load-equivalent skill.
3. Rename `load` → `discuss` and add an optional topic argument.

Outcome: mini ships at v0.2.0, writes to `.project-context/`, reads main files only on prime, and is invoked as `/project-context-mini:discuss [topic]`.

## Locked Decisions

1. **Collision policy:** Mini owns `.project-context/` and overwrites freely. No code-level guard. README states "use one plugin per project."
2. **Refs loading:** `discuss` reads the four main files in full, then emits a manifest of `refs/<name>.md` paths it discovered. The agent reads them with the Read tool on demand.
3. **Discuss scope:** Rename + brief framing prompt + optional topic argument. No interactive Q&A loop.
4. **Topic argument:** does not filter which files are loaded; only shapes the closing framing prompt.

## Files Modified

### Renamed
- `project-context-mini/skills/load/` → `project-context-mini/skills/discuss/` (preserved via `git mv`)

### Edited
| File | Changes |
|---|---|
| `project-context-mini/skills/discuss/SKILL.md` | Full rewrite: name, description, paths, lazy refs, topic argument, framing prompt |
| `project-context-mini/skills/update/SKILL.md` | All `.project-context-mini/` paths migrated; Step 2 exit message now points at `:discuss` |
| `project-context-mini/skills/update/references/file-scaffolds.md` | Description path migrated |
| `project-context-mini/.claude-plugin/plugin.json` | Version 0.1.0 → 0.2.0; description updated |
| `project-context-mini/README.md` | Coexistence rewritten (collision warning); skills section updated; tree examples migrated; install caveat retained |
| `.project-context/architecture.md` | Sibling section updated; three new Key Decisions dated 2026-04-27 |
| `.project-context/state.md` | Phase + Focus + Next Action reflect v2 work |
| `.project-context/progress.md` | v2 entry added under Completed; Phase 8 (smoke test) replaced with v2 smoke-test entry |

### Untouched
- `project-context-mini/agents/content-extractor/agent.md` — references `project-context-mini` plugin name only; no embedded paths.
- `project-context-mini/agents/update-critic/agent.md` — same.
- `.claude-plugin/marketplace.json` — entry already points at the right directory.
- Parent `project-context/` plugin — unchanged.

## Verification

Static checks (passed at implementation time):
- `python3 -c "import json; json.load(open('project-context-mini/.claude-plugin/plugin.json'))"` — manifest valid.
- `grep -rn "\.project-context-mini" project-context-mini/` — no hits.
- `grep -rn "project-context-mini:load" project-context-mini/` — no hits.

Manual smoke test (pending PR):
1. `/reload-plugins` → confirm `/project-context-mini:discuss` appears and `:load` is gone.
2. `/project-context-mini:update` (bootstrap) → creates `.project-context/` (not `.project-context-mini/`) with the four files.
3. `/project-context-mini:discuss` → four files emitted inline; refs section says "no refs found" or absent.
4. Manually create `.project-context/architecture/refs/data-model.md`, run discuss → manifest lists `data-model.md` *path*; content is **not** in the output.
5. `/project-context-mini:discuss "data model"` → framing prompt at end mentions `data model`; refs still only listed.

## Risks & Trade-offs

- **Collision with parent plugin** — accepted. Documented; mini and parent are mutually exclusive per project.
- **Lazy refs may surprise users** who expect everything loaded — mitigated by an explicit "read on demand" line in the manifest output.
- **Topic argument is documentation-only** (does not filter loads) — kept simple to avoid scope creep into interactive Q&A.

## Out of Scope

- No changes to parent plugin.
- No marketplace.json changes.
- No new commands, hooks, or statusline work.
- No interactive Q&A loop in `discuss`.
