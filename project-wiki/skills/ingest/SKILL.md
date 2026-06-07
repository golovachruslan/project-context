---
name: project-wiki:ingest
description: "The heart of project-wiki — provide raw info and it gets properly organized. Accepts any source (pasted text, Slack export, email .eml, PDF, doc, screenshot), routes it to the right project, archives it immutably to raw/, then compiles it into cross-linked wiki pages via an extractor→critic pipeline. Enforces size budgets and logs the operation. Triggers: 'ingest this', 'add to wiki', 'file this info', 'capture this', 'add this slack thread/email/doc to the wiki'."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Ingest into project-wiki

Provide raw information; it ends up archived and compiled into the right project's wiki. Source-agnostic: Slack, email, PDF, doc, note, or plain paste.

**Clarify before acting:** if routing is ambiguous, the source is unclear, or a candidate could go multiple ways, use `AskUserQuestion`. Never fabricate content not supported by the source.

## Arguments

- `[content | path]` — pasted text, or a path to a file (`.md/.txt/.eml/.pdf/.docx/.html/image`).
- `--source slack|email|pdf|doc|note|paste` — auto-detected from extension / shape; defaults to `paste`.
- `--project <slug>` — skip routing and ingest directly into this project.
- `--vault <path>` — see Step 0.

## Step 0 — Resolve vault + extract content

Resolve the vault path (`--vault` → `PROJECT_WIKI_VAULT` → `.project-wiki` marker → ask). If the input is a **file**, use the `Read` tool to extract its text first (Read handles PDFs and images); for `.eml`, treat headers as `origin`/`date` metadata and the body as content. From here everything is text.

## Step 1 — Route to a project

If `--project` was given, skip to Step 2. Otherwise launch the **`router`** agent with the content (or a representative excerpt) and the vault path. It returns ranked candidates + a `suggested_slug`.

- High-confidence single match → use it (tell the user which project and why).
- Tie, low confidence, or `__new__` → `AskUserQuestion`: offer the top candidates plus "Create new project". If the user picks new, run the `init --project` flow first.

## Step 2 — Archive the raw source (immutable)

Write the content verbatim to `projects/<slug>/raw/<YYYY-MM-DD>-<short-slug>.md` with frontmatter (`source`, `origin`, `date`, `project`) per the raw-source template. **Never edit a raw file after writing it.**

## Step 3 — Source summary page

Create `projects/<slug>/wiki/sources/<YYYY-MM-DD>-<short-slug>.md`: a short summary of the source with `sources:` frontmatter citing the raw file. This is the page the index/search surfaces for "what did that thread/doc say?".

## Step 4 — Extract candidates

Launch the **`wiki-extractor`** agent with the archived raw path, the project slug, and the vault path. It reads the raw file + existing project wiki/index and returns ranked candidate pages (create/update), each with `[[wikilinks]]`, frontmatter, and a grounding `sources:` quote.

## Step 5 — Critic gate

Launch the **`wiki-critic`** agent with the candidate list, the project slug, and the vault path. It returns `{kept, rejected}` — ruthlessly filtered, with `create`→`update` downgrades and `requires_relocation` flags.

## Step 6 — Present + approve

Group kept candidates by target page. For each show: action (create/update), the proposed content, its source quote, and a one-line rationale. Include a compact summary of what the critic rejected (so the filter is visible). Ask via `AskUserQuestion`: approve all / approve some / reject all.

## Step 7 — Apply (surgical, drift-safe)

For each approved candidate:
- **create** → `Write` a new page under the correct typed folder with full frontmatter (including `sources:` and `updated: <today>`).
- **update** → **re-read the target page AND its cited raw source**, then `Edit` the specific section. Do not rewrite the whole page.
- Add/refresh the page's one-line entry in the project `index.md` (or the matching `indexes/<type>.md` if sharded).
- If a new project page was created, add it to the global `index.md`.
- If a candidate carried `cross_project`, add the `[[projects/<other>/_project]]` link to both `_project.md` files' `## Dependencies` sections and note that `dependencies.md` should be regenerated (lint `--fix`).

## Step 8 — Enforce budgets on touched files

For each `_project.md` / `progress.md` / wiki page you touched, check line count (`wc -l` or the `wiki_lint.py` output). If over budget, relocate per the schema:
- wiki page > 800 lines → split a section into `<type>/<topic>/refs/*.md`, leave a `[[link]]`.
- `_project.md` > 60 → move prose detail to a wiki page, leave a `[[link]]`.
- `progress.md` > 80 → move older completed items to `progress/archive.md`, leave a one-line summary.
The touched file must end under its cap. Nothing is deleted — `raw/` retains everything.

## Step 9 — Log + commit

Append one line to `log.md`: `<date> | ingest | <project> | <source> | pages: [[...]]`. Then suggest a vault commit (do not commit without the user asking).

## Edge cases

- **Spans two projects** — archive raw to the primary; create/update pages in both if the critic kept cross-project candidates; record the dependency link.
- **Nothing worth compiling** (critic kept zero) — still keep the archived raw + source summary page; say "no durable pages this time." That's valid.
- **Agent tool unavailable** — fall back to doing extraction + filtering inline in the main session, but keep the two-pass discipline (gather broadly, then cut hard) and the mandatory source quotes.
- **Duplicate source** — if a near-identical raw file already exists, ask before re-ingesting.
