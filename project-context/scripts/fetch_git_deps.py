#!/usr/bin/env python3
"""
Fetch .project-context/ from git link dependencies.

Uses git sparse-checkout (--filter=blob:none --sparse) to download only the
.project-context/ directory from remote repos, then copies the context files
into .project-context/.deps-cache/<project>/ and cleans up the temp clone.
No .git/ directories are retained — the cache is plain files.

Usage:
    python fetch_git_deps.py fetch [--dir DIR] [--project NAME]
    python fetch_git_deps.py status [--dir DIR]
    python fetch_git_deps.py clean [--dir DIR] [--project NAME]
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


CACHE_DIR_NAME = ".deps-cache"
META_FILENAME = ".fetch-meta.json"


def find_context_dir(start_dir="."):
    """Find .project-context directory."""
    context_dir = Path(start_dir) / ".project-context"
    if context_dir.is_dir():
        return context_dir
    return None


def get_cache_dir(context_dir):
    """Get or create the .deps-cache directory."""
    cache_dir = context_dir / CACHE_DIR_NAME
    cache_dir.mkdir(exist_ok=True)

    # Ensure .gitignore exists to prevent tracking cached deps
    gitignore = cache_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Auto-generated — cached git dependency contexts\n*\n!.gitignore\n")

    return cache_dir


def parse_git_deps(context_dir):
    """Parse dependencies.json and return only git link entries."""
    deps_file = context_dir / "dependencies.json"
    if not deps_file.exists():
        return []

    try:
        data = json.loads(deps_file.read_text())
    except (json.JSONDecodeError, ValueError):
        return []

    git_deps = []
    for direction in ("upstream", "downstream"):
        for dep in data.get(direction, []):
            if "git" in dep:
                git_deps.append({**dep, "direction": direction})

    return git_deps


def run_git(args, cwd=None, timeout=60):
    """Run a git command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except FileNotFoundError:
        return False, "", "git not found — ensure git is installed"


def fetch_single_dep(dep, cache_dir):
    """Fetch .project-context/ for a single git dependency.

    Uses sparse-checkout (--filter=blob:none --sparse) so only the
    .project-context/ directory is downloaded — no application code.
    Copies context files to cache, then cleans up the temp clone.
    No .git/ is retained — cache contains only plain context files.
    """
    project = dep["project"]
    git_url = dep["git"]
    ref = dep.get("ref", "HEAD")
    dep_cache = cache_dir / project

    result = {
        "project": project,
        "git": git_url,
        "ref": ref,
        "direction": dep["direction"],
    }

    # Clone to temp dir, copy context files out, delete clone
    tmp_dir = None
    try:
        tmp_dir = Path(tempfile.mkdtemp(prefix=f"deps-{project}-"))
        repo_dir = tmp_dir / "repo"

        # Sparse clone — downloads tree objects but no file blobs yet,
        # and initializes sparse-checkout in cone mode (root files only)
        clone_args = ["clone", "--depth", "1", "--filter=blob:none", "--sparse"]
        if ref != "HEAD":
            clone_args += ["--branch", ref]
        clone_args += [git_url, str(repo_dir)]

        ok, _, err = run_git(clone_args, timeout=120)
        if not ok:
            result["status"] = "error"
            result["error"] = f"git clone failed: {err}"
            return result

        # Restrict checkout to only .project-context/ — triggers blob download
        # for that directory only
        ok, _, err = run_git(["sparse-checkout", "set", ".project-context"], cwd=repo_dir)
        if not ok:
            result["status"] = "error"
            result["error"] = f"git sparse-checkout set failed: {err}"
            return result

        # Check if .project-context/ exists in cloned repo
        cloned_context = repo_dir / ".project-context"
        if not cloned_context.is_dir():
            result["status"] = "no_context"
            result["message"] = "Remote repository has no .project-context/ directory"
            return result

        # Collect context files (only files, skip subdirs like plans/)
        context_files = [f.name for f in cloned_context.iterdir() if f.is_file()]
        if not context_files:
            result["status"] = "no_context"
            result["message"] = ".project-context/ exists but contains no files"
            return result

        # Clear old cache and copy fresh files
        if dep_cache.exists():
            shutil.rmtree(dep_cache)
        dep_cache.mkdir(parents=True)

        for f in cloned_context.iterdir():
            if f.is_file():
                shutil.copy2(f, dep_cache / f.name)

        # Write fetch metadata
        fetched_at = datetime.now().isoformat()
        meta = {
            "project": project,
            "git": git_url,
            "ref": ref,
            "fetched_at": fetched_at,
            "files": context_files,
        }
        (dep_cache / META_FILENAME).write_text(json.dumps(meta, indent=2))

        result["status"] = "ok"
        result["cached_path"] = str(dep_cache)
        result["files"] = context_files
        result["fetched_at"] = fetched_at

    finally:
        # Always clean up temp dir
        if tmp_dir and tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return result


def cmd_fetch(args):
    """Fetch .project-context/ from all git link dependencies."""
    context_dir = find_context_dir(args.dir)
    if not context_dir:
        print(json.dumps({
            "error": "No .project-context/ directory found.",
            "hint": "Run /project-context:init first"
        }))
        return 1

    git_deps = parse_git_deps(context_dir)
    if not git_deps:
        print(json.dumps({
            "fetched": 0,
            "message": "No git link dependencies found in dependencies.json",
            "hint": "Run /project-context:add-dependency <git-url> to add one"
        }))
        return 0

    # Filter by project name if specified
    if args.project:
        git_deps = [d for d in git_deps if d["project"] == args.project]
        if not git_deps:
            print(json.dumps({
                "error": f"No git dependency named '{args.project}' found"
            }))
            return 1

    cache_dir = get_cache_dir(context_dir)
    results = []

    for dep in git_deps:
        result = fetch_single_dep(dep, cache_dir)
        results.append(result)

    ok_count = sum(1 for r in results if r["status"] == "ok")
    err_count = sum(1 for r in results if r["status"] == "error")
    no_ctx_count = sum(1 for r in results if r["status"] == "no_context")

    print(json.dumps({
        "fetched": ok_count,
        "errors": err_count,
        "no_context": no_ctx_count,
        "total": len(results),
        "cache_dir": str(cache_dir),
        "results": results,
    }, indent=2))

    return 0 if err_count == 0 else 1


def cmd_status(args):
    """Show status of cached git dependencies."""
    context_dir = find_context_dir(args.dir)
    if not context_dir:
        print(json.dumps({"error": "No .project-context/ directory found."}))
        return 1

    cache_dir = context_dir / CACHE_DIR_NAME
    if not cache_dir.is_dir():
        print(json.dumps({
            "cached": 0,
            "message": "No .deps-cache/ directory — no git dependencies fetched yet"
        }))
        return 0

    git_deps = parse_git_deps(context_dir)
    git_dep_map = {d["project"]: d for d in git_deps}

    cached = []
    for item in cache_dir.iterdir():
        if not item.is_dir() or item.name.startswith("."):
            continue

        meta_file = item / META_FILENAME
        entry = {"project": item.name, "cache_path": str(item)}

        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
                entry.update(meta)
            except (json.JSONDecodeError, ValueError):
                pass

        # Check if still declared in dependencies.json
        entry["declared"] = item.name in git_dep_map

        # List cached context files (excluding metadata)
        context_files = [f.name for f in item.iterdir() if f.is_file() and f.name != META_FILENAME]
        entry["has_context"] = len(context_files) > 0
        entry["context_files"] = context_files

        cached.append(entry)

    # Find declared but not fetched
    cached_names = {c["project"] for c in cached}
    not_fetched = [
        {"project": d["project"], "git": d["git"], "status": "not_fetched"}
        for d in git_deps
        if d["project"] not in cached_names
    ]

    print(json.dumps({
        "cached": len(cached),
        "not_fetched": len(not_fetched),
        "entries": cached,
        "missing": not_fetched,
    }, indent=2))
    return 0


def cmd_clean(args):
    """Remove cached git dependencies."""
    context_dir = find_context_dir(args.dir)
    if not context_dir:
        print(json.dumps({"error": "No .project-context/ directory found."}))
        return 1

    cache_dir = context_dir / CACHE_DIR_NAME
    if not cache_dir.is_dir():
        print(json.dumps({"cleaned": 0, "message": "No cache to clean"}))
        return 0

    if args.project:
        # Clean specific project
        dep_cache = cache_dir / args.project
        if dep_cache.is_dir():
            shutil.rmtree(dep_cache)
            print(json.dumps({"cleaned": 1, "project": args.project}))
        else:
            print(json.dumps({"cleaned": 0, "error": f"No cache for '{args.project}'"}))
            return 1
    else:
        # Clean all
        count = 0
        for item in cache_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                shutil.rmtree(item)
                count += 1
        print(json.dumps({"cleaned": count}))

    return 0


def main():
    parser = argparse.ArgumentParser(description="Fetch .project-context/ from git link dependencies")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch/update git dependency contexts")
    fetch_parser.add_argument("--dir", default=".", help="Project root directory")
    fetch_parser.add_argument("--project", help="Fetch only this project (by name)")

    # status command
    status_parser = subparsers.add_parser("status", help="Show cached dependency status")
    status_parser.add_argument("--dir", default=".", help="Project root directory")

    # clean command
    clean_parser = subparsers.add_parser("clean", help="Remove cached dependencies")
    clean_parser.add_argument("--dir", default=".", help="Project root directory")
    clean_parser.add_argument("--project", help="Clean only this project cache")

    args = parser.parse_args()

    commands = {
        "fetch": cmd_fetch,
        "status": cmd_status,
        "clean": cmd_clean,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
