#!/usr/bin/env python3
"""
wiki_stats.py — growth metrics + scaling-threshold warnings for a project-wiki vault.

Pure standard library, Python 3.10+.

Usage:
    python wiki_stats.py [VAULT] [--project SLUG] [--json]
"""

import argparse
import json
import sys
from pathlib import Path

import _wikilib as wl


def stats_for_project(vault, proj):
    pages = list(wl.iter_wiki_pages(vault, proj.name))
    by_type = {}
    total_links = 0
    inbound = {}

    for page in pages:
        text = wl.read_text(page)
        meta, _ = wl.parse_frontmatter(text)
        ptype = str(meta.get("type", "untyped"))
        by_type[ptype] = by_type.get(ptype, 0) + 1
        links = wl.extract_wikilinks(text)
        total_links += len(links)

    # inbound counts for orphan estimate — count links from ANY markdown
    # in the vault (indexes and hub pages count as inbound), matching lint.
    link_index = wl.build_link_index(vault)
    for src in wl.iter_all_markdown(vault):
        for token in wl.extract_wikilinks(wl.read_text(src)):
            for t in link_index.get(token, ()):
                inbound[t] = inbound.get(t, 0) + 1
    orphans = sum(1 for p in pages if inbound.get(p, 0) == 0)

    raw_dir = proj / "raw"
    raw_count = len(list(raw_dir.glob("*.md"))) if raw_dir.is_dir() else 0
    idx = proj / "index.md"
    index_lines = wl.line_count(idx) if idx.exists() else 0

    # threshold guidance
    near = []
    if len(pages) > wl.INDEX_PAGE_SHARD_COUNT:
        near.append(f"{len(pages)} pages > {wl.INDEX_PAGE_SHARD_COUNT}: shard indexes/")
    if len(pages) > 300:
        near.append("> 300 pages: prefer wiki_search.py (BM25) over index reading")
    if index_lines > wl.BUDGETS["index.md"]["soft"]:
        near.append(f"index.md {index_lines} lines > {wl.BUDGETS['index.md']['soft']}: shard")

    return {
        "project": proj.name,
        "pages": len(pages),
        "by_type": by_type,
        "raw_sources": raw_count,
        "total_links": total_links,
        "link_density": round(total_links / len(pages), 2) if pages else 0,
        "orphans": orphans,
        "index_lines": index_lines,
        "thresholds_near": near,
    }


def main():
    ap = argparse.ArgumentParser(description="Stats for a project-wiki vault.")
    ap.add_argument("vault", nargs="?", default=".", help="Path to the vault root (default: .)")
    ap.add_argument("--project", help="Limit to a single project slug")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    if not wl.projects_dir(args.vault).is_dir():
        print(f"No projects/ directory under {args.vault} — not a project-wiki vault.", file=sys.stderr)
        return 1

    per_project = []
    for proj in wl.iter_projects(args.vault):
        if args.project and proj.name != args.project:
            continue
        per_project.append(stats_for_project(args.vault, proj))

    summary = {
        "vault": str(Path(args.vault).resolve()),
        "projects": len(per_project),
        "total_pages": sum(p["pages"] for p in per_project),
        "total_raw_sources": sum(p["raw_sources"] for p in per_project),
        "per_project": per_project,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Vault: {summary['vault']}")
        print(f"Projects: {summary['projects']}  Total pages: {summary['total_pages']}  "
              f"Raw sources: {summary['total_raw_sources']}\n")
        for p in per_project:
            print(f"  {p['project']}: {p['pages']} pages, {p['raw_sources']} raw, "
                  f"density {p['link_density']}, {p['orphans']} orphan(s)")
            types = ", ".join(f"{k}:{v}" for k, v in sorted(p["by_type"].items()))
            if types:
                print(f"     types: {types}")
            for n in p["thresholds_near"]:
                print(f"     ⚠ {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
