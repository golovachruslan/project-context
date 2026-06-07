#!/usr/bin/env python3
"""
wiki_search.py — BM25 keyword search over a project-wiki vault.

Pure standard library, Python 3.10+. No embeddings, no vector DB — this is the
scale fallback for /project-wiki:ask when index-first navigation isn't enough.

Frontmatter filters (--type / --tag / --since) narrow the candidate set WITHOUT
reading bodies, then BM25 ranks the remainder.

Usage:
    python wiki_search.py "query terms" [VAULT] [--project SLUG]
        [--type concept] [--tag billing] [--since 2026-01-01] [--limit 10] [--json]
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

import _wikilib as wl

TOKEN_RE = re.compile(r"[a-z0-9]+")
K1 = 1.5
B = 0.75


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def first_summary(body):
    """First non-blank, non-heading line — used as the result snippet."""
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("```"):
            return s[:160]
    for line in body.splitlines():
        s = line.lstrip("# ").strip()
        if s:
            return s[:160]
    return ""


def passes_filters(meta, args):
    if args.type:
        t = meta.get("type", "")
        if str(t).lower() != args.type.lower():
            return False
    if args.tag:
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        tags = [str(t).lower() for t in tags]
        if args.tag.lower() not in tags:
            return False
    if args.since:
        upd = meta.get("updated", "")
        try:
            if datetime.strptime(str(upd), "%Y-%m-%d") < datetime.strptime(args.since, "%Y-%m-%d"):
                return False
        except ValueError:
            return False  # no/invalid date can't satisfy a --since floor
    return True


def search(vault, query, args):
    docs = []  # (path, tokens, summary)
    for page in wl.iter_wiki_pages(vault, args.project):
        text = wl.read_text(page)
        meta, body = wl.parse_frontmatter(text)
        if not passes_filters(meta, args):
            continue
        # weight the title (filename + first heading) by repeating it
        title = page.stem.replace("-", " ")
        tokens = tokenize(title) * 3 + tokenize(body)
        docs.append((page, tokens, first_summary(body)))

    if not docs:
        return []

    q_terms = tokenize(query)
    N = len(docs)
    avgdl = sum(len(d[1]) for d in docs) / N

    # document frequency
    df = {}
    for _, tokens, _ in docs:
        for term in set(tokens):
            df[term] = df.get(term, 0) + 1

    results = []
    for path, tokens, summary in docs:
        dl = len(tokens)
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        score = 0.0
        for term in q_terms:
            if term not in tf:
                continue
            idf = math.log(1 + (N - df[term] + 0.5) / (df[term] + 0.5))
            freq = tf[term]
            denom = freq + K1 * (1 - B + B * dl / avgdl)
            score += idf * (freq * (K1 + 1)) / denom
        if score > 0:
            results.append({
                "path": wl.relpath(vault, path),
                "score": round(score, 4),
                "summary": summary,
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[: args.limit]


def main():
    ap = argparse.ArgumentParser(description="BM25 search over a project-wiki vault.")
    ap.add_argument("query", help="Search terms")
    ap.add_argument("vault", nargs="?", default=".", help="Path to the vault root (default: .)")
    ap.add_argument("--project", help="Limit to a single project slug")
    ap.add_argument("--type", help="Filter by frontmatter type (e.g. concept, decision)")
    ap.add_argument("--tag", help="Filter by frontmatter tag")
    ap.add_argument("--since", help="Only pages updated on/after this YYYY-MM-DD")
    ap.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    if not wl.projects_dir(args.vault).is_dir():
        print(f"No projects/ directory under {args.vault} — not a project-wiki vault.", file=sys.stderr)
        return 1

    results = search(args.vault, args.query, args)
    if args.json:
        print(json.dumps({"query": args.query, "results": results}, indent=2))
    else:
        if not results:
            print("No matches.")
        for r in results:
            print(f"{r['score']:>8}  {r['path']}")
            if r["summary"]:
                print(f"          {r['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
