---
name: project-wiki:ask
description: "Answer a question from the project-wiki vault, with citations. Routes to the relevant project, navigates index-first (catalog → candidate pages), falls back to BM25 search (wiki_search.py) at scale, and synthesizes a cited answer from compiled wiki pages. Optionally files a valuable synthesized answer back as a new page. Triggers: 'ask the wiki', 'what does the wiki say about', 'how does X work in <project>', 'find info on', 'query the knowledge base'."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
  - AskUserQuestion
---

# Ask project-wiki

Answer questions from the compiled wiki. **Compilation over retrieval:** read the maintained pages, not every raw source.

## Arguments

- `[question]` — the question (free-form).
- `--project <slug>` — restrict to one project (otherwise routed).
- `--vault <path>` — see Step 0.

## Step 0 — Resolve vault

Resolve the vault path (`--vault` → `PROJECT_WIKI_VAULT` → `.project-wiki` marker → ask). Read the vault's `CLAUDE.md` schema block and the global `index.md`.

## Step 1 — Route

If `--project` is set, use it. Otherwise infer the project(s) from the global `index.md` summaries and the question. If genuinely ambiguous across projects, either search the top 2 candidates or ask the user which project.

## Step 2 — Explore

Launch the **`wiki-explorer`** agent with the question, the vault path, the target project slug(s), and the path to `wiki_search.py`. It navigates **index-first** (catalog summaries → read only the candidate pages), and falls back to BM25:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/wiki_search.py "<terms>" <vault> --project <slug> [--type T] [--tag G] [--since YYYY-MM-DD]
```

For a simple, single-project question you may navigate inline instead of dispatching the agent — reading a couple of small pages is cheap.

## Step 3 — Answer with citations

Present the explorer's synthesized answer. **Every claim cites a `[[page]]`**; load-bearing facts also surface the underlying `raw/` source. If the wiki lacks the answer, say so and point to the nearest pages (and suggest `/project-wiki:ingest` to add the missing info) — never fabricate.

## Step 4 — Offer to file the answer (optional)

If the synthesis produced genuinely reusable new knowledge (not already on a page), offer to file it as a new `wiki/notes/` or `wiki/concepts/` page citing the pages it drew from (Karpathy "query → page"). Only on user approval; then update the project `index.md` and append to `log.md`.

## Edge cases

- **Contradictions** — if two pages disagree, surface both and flag it as a lint issue.
- **Stale answer** — if the most relevant page's `updated` is old, note it.
- **Empty vault / project** — say there's nothing ingested yet and suggest `ingest`.
