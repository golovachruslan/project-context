#!/usr/bin/env python3
"""
wiki_search.py — search a project-wiki vault.

Pure standard library, Python 3.10+. Two backends, chosen automatically:

  cli   — the official Obsidian CLI (`obsidian search ... format=json`), used
          when the `obsidian` binary is on PATH AND a running instance answers
          for *this* vault. Gives the same ranked, index-backed results you see
          in the Obsidian search pane.
  bm25  — a built-in BM25 ranker over the markdown. Zero-dependency, headless,
          deterministic. Always available; the fallback when the CLI isn't.

This keeps `ask`/`wiki-explorer` working everywhere (web, CI, a freshly cloned
vault with no GUI) while transparently using Obsidian's better index when a
human has the app open. No embeddings, no vector DB either way.

Environment:
  PROJECT_WIKI_USE_OBSIDIAN=0     disable the CLI backend entirely
  PROJECT_WIKI_OBSIDIAN_VAULT=NAME  registered Obsidian vault name to target

Usage:
    python wiki_search.py "query terms" [VAULT] [--project SLUG]
        [--type concept] [--tag billing] [--since 2026-01-01]
        [--limit 10] [--backend auto|cli|bm25] [--json]
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import _wikilib as wl

TOKEN_RE = re.compile(r"[a-z0-9]+")
K1 = 1.5
B = 0.75
CLI_TIMEOUT_SEC = 8


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
        if str(meta.get("type", "")).lower() != args.type.lower():
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


# ---------------------------------------------------------------------------
# Backend: BM25 (always available)
# ---------------------------------------------------------------------------
def bm25_search(vault, query, args):
    docs = []  # (path, tokens, summary)
    for page in wl.iter_wiki_pages(vault, args.project):
        text = wl.read_text(page)
        meta, body = wl.parse_frontmatter(text)
        if not passes_filters(meta, args):
            continue
        title = page.stem.replace("-", " ")
        tokens = tokenize(title) * 3 + tokenize(body)   # weight the title
        docs.append((page, tokens, first_summary(body)))

    if not docs:
        return []

    q_terms = tokenize(query)
    N = len(docs)
    avgdl = sum(len(d[1]) for d in docs) / N
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
            results.append({"path": wl.relpath(vault, path), "score": round(score, 4), "summary": summary})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[: args.limit]


# ---------------------------------------------------------------------------
# Backend: Obsidian CLI (used when available; verified against THIS vault)
# ---------------------------------------------------------------------------
def cli_available():
    if os.environ.get("PROJECT_WIKI_USE_OBSIDIAN", "").lower() in ("0", "false", "no"):
        return False
    return shutil.which("obsidian") is not None


def cli_search(vault, query, args):
    """Return result list, or None to signal 'unavailable — fall back to BM25'.

    Returning [] means the CLI answered for our vault and found nothing (trusted).
    Returning None means the CLI is missing, errored, timed out, or answered for
    a *different* vault (none of its paths exist under <vault>).
    """
    exe = shutil.which("obsidian")
    if not exe:
        return None

    cmd = [exe, "search", f"query={query}", "format=json",
           f"limit={max(args.limit * 5, 50)}"]
    vault_name = os.environ.get("PROJECT_WIKI_OBSIDIAN_VAULT")
    if vault_name:
        cmd.append(f"vault={vault_name}")
    if args.project:
        cmd.append(f"path=projects/{args.project}")

    try:
        # Obsidian CLI hangs if no instance is running — the timeout is load-bearing.
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=CLI_TIMEOUT_SEC)
    except (subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        data = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, list):
        # tolerate {"results": [...]} shapes
        data = data.get("results", []) if isinstance(data, dict) else []

    vroot = Path(vault)
    mapped_any = False
    results = []
    for item in data:
        if isinstance(item, dict):
            p = item.get("path") or item.get("file")
            score = item.get("score")
            snippet = item.get("snippet") or item.get("excerpt") or ""
        elif isinstance(item, str):
            p, score, snippet = item, None, ""
        else:
            continue
        if not p:
            continue
        abs_p = (vroot / p)
        if not abs_p.is_file():
            continue                     # path belongs to a different vault
        mapped_any = True
        if "/wiki/" not in abs_p.as_posix():
            continue                     # ignore raw/index/hub hits
        meta, body = wl.parse_frontmatter(wl.read_text(abs_p))
        if not passes_filters(meta, args):
            continue
        results.append({
            "path": wl.relpath(vault, abs_p),
            "score": score,
            "summary": first_summary(body) or snippet[:160],
        })

    if not mapped_any:
        return None                      # CLI talked about another vault entirely
    # Preserve Obsidian's own ranking order; just cap.
    return results[: args.limit]


def run(vault, query, args):
    if args.backend == "bm25":
        return "bm25", bm25_search(vault, query, args)
    if args.backend == "cli":
        res = cli_search(vault, query, args)
        return "cli", (res if res is not None else [])
    # auto
    if cli_available():
        res = cli_search(vault, query, args)
        if res is not None:
            return "cli", res
    return "bm25", bm25_search(vault, query, args)


def main():
    ap = argparse.ArgumentParser(description="Search a project-wiki vault (Obsidian CLI when available, else BM25).")
    ap.add_argument("query", help="Search terms")
    ap.add_argument("vault", nargs="?", default=".", help="Path to the vault root (default: .)")
    ap.add_argument("--project", help="Limit to a single project slug")
    ap.add_argument("--type", help="Filter by frontmatter type (e.g. concept, decision)")
    ap.add_argument("--tag", help="Filter by frontmatter tag")
    ap.add_argument("--since", help="Only pages updated on/after this YYYY-MM-DD")
    ap.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    ap.add_argument("--backend", choices=["auto", "cli", "bm25"], default="auto",
                    help="Search backend (default: auto — Obsidian CLI if reachable, else BM25)")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    if not wl.projects_dir(args.vault).is_dir():
        print(f"No projects/ directory under {args.vault} — not a project-wiki vault.", file=sys.stderr)
        return 1

    backend, results = run(args.vault, args.query, args)
    if args.json:
        print(json.dumps({"query": args.query, "backend": backend, "results": results}, indent=2))
    else:
        print(f"# backend: {backend}")
        if not results:
            print("No matches.")
        for r in results:
            score = r.get("score")
            score_s = f"{score:>8}" if isinstance(score, (int, float)) else f"{'-':>8}"
            print(f"{score_s}  {r['path']}")
            if r.get("summary"):
                print(f"          {r['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
