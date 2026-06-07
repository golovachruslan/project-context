#!/usr/bin/env python3
"""
wiki_lint.py — structural health check for a project-wiki vault.

Pure standard library, Python 3.10+.

Reports issues in three tiers (critical / warning / suggestion):

  critical    broken [[wikilinks]]; page missing mandatory `sources:`;
              hot file over its hard budget; wiki page over 800 lines;
              missing required project files.
  warning     orphan pages; raw sources never compiled; stale pages;
              wiki page over the 400-line soft cap; index near a shard threshold.
  suggestion  thin pages; missing optional frontmatter.

Usage:
    python wiki_lint.py [VAULT] [--project SLUG] [--stale-days N] [--json]

Exit code is non-zero when any critical issue is found.
"""

import argparse
import json
import sys
from datetime import datetime, date
from pathlib import Path

import _wikilib as wl

REQUIRED_PROJECT_FILES = ["_project.md", "index.md", "progress.md", "refs.md"]
# Files exempt from the mandatory `sources:` rule (they are hubs/pointers, not claims).
SOURCES_EXEMPT_NAMES = {"_project.md", "index.md", "progress.md", "refs.md"}
DEFAULT_STALE_DAYS = 60


def _add(issues, severity, file, message, **extra):
    issues.append({"severity": severity, "file": file, "message": message, **extra})


def lint(vault, project=None, stale_days=DEFAULT_STALE_DAYS):
    vault = Path(vault)
    issues = []

    if not wl.projects_dir(vault).is_dir():
        _add(issues, "critical", str(vault),
             "No projects/ directory found — is this a project-wiki vault? Run /project-wiki:init.")
        return issues

    link_index = wl.build_link_index(vault)
    # Aggregate the full text of every index file once (for orphan / missing-entry checks).
    index_blob = ""
    for p in vault.rglob("index.md"):
        index_blob += wl.read_text(p)
    for p in vault.rglob("indexes/*.md"):
        index_blob += wl.read_text(p)

    inbound = {}  # page path -> inbound link count

    # ---- per-project structural checks -----------------------------------
    for proj in wl.iter_projects(vault):
        if project and proj.name != project:
            continue
        for req in REQUIRED_PROJECT_FILES:
            if not (proj / req).exists():
                _add(issues, "critical", wl.relpath(vault, proj / req),
                     f"Required project file missing: {req}")

        # hot-file budgets
        for fname, rule in (("_project.md", wl.BUDGETS["_project.md"]),
                            ("progress.md", wl.BUDGETS["progress.md"])):
            fpath = proj / fname
            if fpath.exists():
                n = wl.line_count(fpath)
                if n > rule["hard"]:
                    _add(issues, "critical", wl.relpath(vault, fpath),
                         f"{fname} is {n} lines, over its hard budget of {rule['hard']} — "
                         f"relocate overflow (run /project-wiki:lint --fix).", lines=n)

        # index shard thresholds
        idx = proj / "index.md"
        if idx.exists():
            n = wl.line_count(idx)
            if n > wl.BUDGETS["index.md"]["soft"]:
                _add(issues, "warning", wl.relpath(vault, idx),
                     f"index.md is {n} lines (> {wl.BUDGETS['index.md']['soft']}) — "
                     f"shard into indexes/<type>.md.", lines=n)
        page_count = sum(1 for _ in wl.iter_wiki_pages(vault, proj.name))
        if page_count > wl.INDEX_PAGE_SHARD_COUNT:
            _add(issues, "warning", wl.relpath(vault, proj),
                 f"{page_count} wiki pages (> {wl.INDEX_PAGE_SHARD_COUNT}) — "
                 f"consider sharded indexes and BM25 search (wiki_search.py).", pages=page_count)

    # ---- per-page checks --------------------------------------------------
    for page in wl.iter_wiki_pages(vault, project):
        rel = wl.relpath(vault, page)
        text = wl.read_text(page)
        meta, body = wl.parse_frontmatter(text)
        n = len(text.splitlines())

        # size
        if n > wl.WIKI_PAGE_HARD:
            _add(issues, "critical", rel,
                 f"page is {n} lines, over hard cap {wl.WIKI_PAGE_HARD} — split into refs/.", lines=n)
        elif n > wl.WIKI_PAGE_SOFT:
            _add(issues, "warning", rel,
                 f"page is {n} lines, over soft cap {wl.WIKI_PAGE_SOFT} — consider splitting.", lines=n)

        # mandatory sources (anti-drift guard)
        if page.name not in SOURCES_EXEMPT_NAMES and not wl.has_value(meta, "sources"):
            _add(issues, "critical", rel,
                 "missing mandatory `sources:` frontmatter — every wiki page must cite a raw source.")

        # frontmatter completeness
        for field in ("type", "updated", "project"):
            if not wl.has_value(meta, field):
                _add(issues, "suggestion", rel, f"missing optional frontmatter field `{field}`.")

        # staleness
        if wl.has_value(meta, "updated"):
            try:
                upd = datetime.strptime(str(meta["updated"]), "%Y-%m-%d").date()
                age = (date.today() - upd).days
                if age > stale_days:
                    _add(issues, "warning", rel,
                         f"not updated in {age} days (> {stale_days}) — may be stale.", age_days=age)
            except ValueError:
                _add(issues, "suggestion", rel, f"`updated` is not a YYYY-MM-DD date: {meta['updated']}")

        # thin page
        if len(body.strip().splitlines()) < 3:
            _add(issues, "suggestion", rel, "page body is very thin (< 3 lines).")

        # broken links + accumulate inbound counts
        for token in wl.extract_wikilinks(text):
            targets = link_index.get(token)
            if not targets:
                _add(issues, "critical", rel, f"broken wikilink: [[{token}]]")
            else:
                for t in targets:
                    inbound[t] = inbound.get(t, 0) + 1

    # ---- broken links from hub files (dependencies live in _project.md) ----
    hub_files = [vault / "dependencies.md", vault / "index.md"]
    for proj in wl.iter_projects(vault):
        if project and proj.name != project:
            continue
        hub_files += [proj / "_project.md", proj / "index.md"]
    for hub in hub_files:
        if not hub.exists():
            continue
        rel = wl.relpath(vault, hub)
        for token in wl.extract_wikilinks(wl.read_text(hub)):
            targets = link_index.get(token)
            if not targets:
                sev = "critical" if hub.name == "_project.md" else "warning"
                _add(issues, sev, rel, f"broken wikilink: [[{token}]]")
            else:
                for t in targets:
                    inbound[t] = inbound.get(t, 0) + 1

    # ---- orphans + uncompiled raw ----------------------------------------
    for page in wl.iter_wiki_pages(vault, project):
        rel = wl.relpath(vault, page)
        listed = page.stem in index_blob or rel in index_blob
        if inbound.get(page, 0) == 0 and not listed:
            _add(issues, "warning", rel, "orphan page — no inbound links and absent from any index.")

    for proj in wl.iter_projects(vault):
        if project and proj.name != project:
            continue
        raw_dir = proj / "raw"
        if not raw_dir.is_dir():
            continue
        # gather all raw-link tokens referenced anywhere in the project's wiki
        referenced = set()
        for page in wl.iter_wiki_pages(vault, proj.name):
            for token in wl.extract_wikilinks(wl.read_text(page)):
                referenced.add(Path(token).stem)
        for rawfile in sorted(raw_dir.glob("*.md")):
            if rawfile.stem not in referenced:
                _add(issues, "warning", wl.relpath(vault, rawfile),
                     "raw source never referenced by any wiki page — not yet compiled.")

    return issues


def main():
    ap = argparse.ArgumentParser(description="Lint a project-wiki vault.")
    ap.add_argument("vault", nargs="?", default=".", help="Path to the vault root (default: .)")
    ap.add_argument("--project", help="Limit to a single project slug")
    ap.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS,
                    help=f"Days before a page is flagged stale (default: {DEFAULT_STALE_DAYS})")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    issues = lint(args.vault, args.project, args.stale_days)
    counts = {"critical": 0, "warning": 0, "suggestion": 0}
    for i in issues:
        counts[i["severity"]] = counts.get(i["severity"], 0) + 1

    if args.json:
        print(json.dumps({"ok": counts["critical"] == 0, "counts": counts, "issues": issues}, indent=2))
    else:
        if not issues:
            print("OK — no issues found.")
        else:
            order = {"critical": 0, "warning": 1, "suggestion": 2}
            for i in sorted(issues, key=lambda x: order[x["severity"]]):
                print(f"[{i['severity'].upper():10}] {i['file']}: {i['message']}")
            print(f"\n{counts['critical']} critical, {counts['warning']} warning, "
                  f"{counts['suggestion']} suggestion")

    return 1 if counts["critical"] else 0


if __name__ == "__main__":
    sys.exit(main())
