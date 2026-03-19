#!/usr/bin/env python3
"""
Project context management utility.
Replaces fragile sed operations with reliable Python-based file management.

Usage:
    python manage_context.py status [--dir DIR]
    python manage_context.py validate [--dir DIR]
    python manage_context.py update-sections [--file FILE]
    python manage_context.py deps [--dir DIR]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


CONTEXT_FILES = ["brief.md", "architecture.md", "state.md", "progress.md", "patterns.md", "dependencies.json"]

STALENESS_DAYS = {
    "brief.md": 30,
    "architecture.md": 7,
    "state.md": 1,
    "progress.md": 3,
    "patterns.md": 14,
    "dependencies.json": 30,
}

MANAGED_SECTION_START = "<!-- PROJECT-CONTEXT:START -->"
MANAGED_SECTION_END = "<!-- PROJECT-CONTEXT:END -->"

CLAUDE_MANAGED_CONTENT = """
<!-- PROJECT-CONTEXT:START -->
## Project Context

Always read `.project-context/` files when starting work:
- `brief.md` — Project goals, scope, requirements
- `architecture.md` — System design, tech stack, flows
- `state.md` — Current position, blockers, next action
- `progress.md` — Completed/in-progress/upcoming work
- `patterns.md` — Established patterns and learnings
- `dependencies.json` — Cross-project dependencies (monorepo)

<!-- PROJECT-CONTEXT:END -->
"""

AGENTS_MANAGED_CONTENT = """
<!-- PROJECT-CONTEXT:START -->
## Project Context

Before executing tasks, read `.project-context/` files:
- `brief.md` — Project scope and goals
- `architecture.md` — System design and flows
- `state.md` — Current position and blockers
- `progress.md` — Work status
- `patterns.md` — Established patterns
- `dependencies.json` — Cross-project dependencies (monorepo)

<!-- PROJECT-CONTEXT:END -->
"""


def find_context_dir(start_dir="."):
    """Find .project-context directory."""
    context_dir = Path(start_dir) / ".project-context"
    if context_dir.is_dir():
        return context_dir
    return None


def parse_dependencies(context_dir):
    """Parse dependencies.json and return structured dependency data.

    Returns dict with upstream, downstream lists, or None if file missing.
    """
    deps_file = context_dir / "dependencies.json"
    if not deps_file.exists():
        return None

    try:
        data = json.loads(deps_file.read_text())
    except (json.JSONDecodeError, ValueError):
        return None

    # Ensure expected keys exist with defaults
    return {
        "upstream": data.get("upstream", []),
        "downstream": data.get("downstream", []),
    }


def cmd_status(args):
    """Show current project context status."""
    context_dir = find_context_dir(args.dir)
    if not context_dir:
        print(json.dumps({
            "exists": False,
            "message": "No .project-context/ directory found. Run /project-context:init to create."
        }))
        return 1

    now = datetime.now()
    files = {}
    missing = []

    for fname in CONTEXT_FILES:
        fpath = context_dir / fname
        if fpath.exists():
            stat = fpath.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            age_days = (now - mtime).days
            stale_threshold = STALENESS_DAYS.get(fname, 7)
            is_stale = age_days > stale_threshold
            size_lines = len(fpath.read_text().splitlines())

            files[fname] = {
                "exists": True,
                "lines": size_lines,
                "last_modified": mtime.isoformat(),
                "age_days": age_days,
                "stale": is_stale,
                "stale_threshold_days": stale_threshold,
            }
        else:
            missing.append(fname)
            files[fname] = {"exists": False}

    # Check for plans
    plans_dir = context_dir / "plans"
    plans = []
    if plans_dir.is_dir():
        plans = [f.name for f in plans_dir.glob("*.md")]

    # Parse dependencies if present
    deps = parse_dependencies(context_dir)

    # Determine suggested next action
    next_action = _determine_next_action(files, plans, context_dir)

    result = {
        "exists": True,
        "files": files,
        "missing": missing,
        "plans": plans,
        "next_action": next_action,
    }

    if deps:
        all_deps = deps["upstream"] + deps["downstream"]
        git_deps = [d for d in all_deps if "git" in d]
        local_deps = [d for d in all_deps if "git" not in d]
        result["dependencies"] = {
            "upstream_count": len(deps["upstream"]),
            "downstream_count": len(deps["downstream"]),
            "upstream": [d["project"] for d in deps["upstream"]],
            "downstream": [d["project"] for d in deps["downstream"]],
            "git_link_count": len(git_deps),
            "local_count": len(local_deps),
        }
        if git_deps:
            # Check cache status for git deps
            cache_dir = context_dir / ".deps-cache"
            cached = [d["project"] for d in git_deps if (cache_dir / d["project"]).is_dir()]
            result["dependencies"]["git_cached"] = cached
            result["dependencies"]["git_not_cached"] = [d["project"] for d in git_deps if d["project"] not in cached]

    print(json.dumps(result, indent=2))
    return 0


def _determine_next_action(files, plans, context_dir):
    """Determine what the user should do next (used by /project-context:next)."""
    # Check if state.md exists and has content
    state_file = context_dir / "state.md"
    state_content = ""
    if state_file.exists():
        state_content = state_file.read_text()

    # Missing critical files
    missing_critical = [f for f in ["brief.md", "architecture.md"] if not files.get(f, {}).get("exists")]
    if missing_critical:
        return {"action": "init", "reason": f"Missing critical files: {', '.join(missing_critical)}"}

    # Check for stale state
    if files.get("state.md", {}).get("stale"):
        return {"action": "update", "reason": "state.md is stale — update current position"}

    # Check for active plans not yet implemented
    if plans:
        # Look for plans with "Planning" status
        for plan_name in plans:
            plan_path = context_dir / "plans" / plan_name
            content = plan_path.read_text()
            if "**Status:** Planning" in content:
                return {"action": "implement", "reason": f"Plan '{plan_name}' is ready for implementation", "plan": plan_name}

    # Check if any files are stale
    stale_files = [f for f, info in files.items() if info.get("stale")]
    if stale_files:
        return {"action": "update", "reason": f"Stale files: {', '.join(stale_files)}"}

    # Default
    return {"action": "discuss", "reason": "Context is up to date. Ready for new work."}


def cmd_validate(args):
    """Validate project context files."""
    context_dir = find_context_dir(args.dir)
    if not context_dir:
        print(json.dumps({"valid": False, "error": "No .project-context/ directory found."}))
        return 1

    issues = []

    for fname in CONTEXT_FILES:
        fpath = context_dir / fname
        if not fpath.exists():
            # dependencies.md is optional
            if fname == "dependencies.json":
                continue
            if fname == "state.md":
                issues.append({"file": fname, "severity": "warning", "message": "state.md missing — add for session continuity"})
            elif fname in ("brief.md", "architecture.md"):
                issues.append({"file": fname, "severity": "error", "message": f"{fname} missing — critical context file"})
            continue

        content = fpath.read_text()

        # JSON file validation (dependencies.json)
        if fname.endswith(".json"):
            try:
                data = json.loads(content)
                if not data.get("upstream") and not data.get("downstream"):
                    issues.append({"file": fname, "severity": "warning", "message": f"{fname} has no upstream or downstream dependencies"})
            except (json.JSONDecodeError, ValueError) as e:
                issues.append({"file": fname, "severity": "error", "message": f"{fname} is invalid JSON: {e}"})
            continue

        # Markdown file validation
        lines = content.splitlines()

        # Check if file is essentially empty (only template markers)
        non_empty = [l for l in lines if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("---") and not l.strip().startswith("*Last")]
        if len(non_empty) < 3:
            issues.append({"file": fname, "severity": "warning", "message": f"{fname} appears to be mostly empty template"})

        # Check for TODO/placeholder markers
        if re.search(r'\[.*\.\.\.\]|\[TODO\]|\[TBD\]', content):
            issues.append({"file": fname, "severity": "info", "message": f"{fname} contains unfilled placeholders"})

        # Check for stale timestamps
        timestamp_match = re.search(r'\*Last updated: (\d{4}-\d{2}-\d{2})', content)
        if timestamp_match:
            try:
                last_updated = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d")
                threshold = STALENESS_DAYS.get(fname, 7)
                if (datetime.now() - last_updated).days > threshold:
                    issues.append({"file": fname, "severity": "warning", "message": f"{fname} timestamp is stale (>{threshold} days)"})
            except ValueError:
                pass

        # architecture.md specific: check for Mermaid diagrams
        if fname == "architecture.md":
            if "```mermaid" not in content:
                issues.append({"file": fname, "severity": "warning", "message": "architecture.md has no Mermaid diagrams"})

    # Validate dependency entries if present
    deps = parse_dependencies(context_dir)
    if deps:
        project_root = Path(args.dir).resolve()
        all_deps = deps["upstream"] + deps["downstream"]
        for dep in all_deps:
            if "git" in dep:
                # Git link dependency — validate git URL and cache status
                git_url = dep["git"]
                if not git_url:
                    issues.append({
                        "file": "dependencies.json",
                        "severity": "error",
                        "message": f"Git dependency '{dep['project']}' has empty git URL"
                    })
                elif not any(git_url.startswith(p) for p in ("https://", "git@", "ssh://")) and not git_url.endswith(".git"):
                    issues.append({
                        "file": "dependencies.json",
                        "severity": "warning",
                        "message": f"Git dependency '{dep['project']}' URL may be invalid: {git_url}"
                    })

                # Check if cached context exists
                cache_path = context_dir / ".deps-cache" / dep["project"]
                if not cache_path.is_dir():
                    issues.append({
                        "file": "dependencies.json",
                        "severity": "info",
                        "message": f"Git dependency '{dep['project']}' context not cached — run /project-context:add-dependency --fetch"
                    })
            elif "path" in dep:
                # Local path dependency — validate path exists
                dep_path = (context_dir.parent / dep["path"]).resolve()
                if not dep_path.is_dir():
                    issues.append({
                        "file": "dependencies.json",
                        "severity": "warning",
                        "message": f"Dependency '{dep['project']}' path not found: {dep['path']}"
                    })
                else:
                    # Check if the dependency target also has a .project-context/
                    dep_context = dep_path / ".project-context"
                    if not dep_context.is_dir():
                        issues.append({
                            "file": "dependencies.json",
                            "severity": "info",
                            "message": f"Dependency '{dep['project']}' at {dep['path']} has no .project-context/ — consider initializing it"
                        })
            else:
                # Missing both git and path
                issues.append({
                    "file": "dependencies.json",
                    "severity": "error",
                    "message": f"Dependency '{dep['project']}' has neither 'path' nor 'git' field"
                })

    # Check plans directory
    plans_dir = context_dir / "plans"
    if plans_dir.is_dir():
        for plan_file in plans_dir.glob("*.md"):
            content = plan_file.read_text()
            # Check for executable task format
            if "**Action:**" not in content and "- **Action:**" not in content:
                issues.append({"file": f"plans/{plan_file.name}", "severity": "info", "message": "Plan lacks executable task format (Action/Verify/Done)"})

    valid = not any(i["severity"] == "error" for i in issues)
    print(json.dumps({"valid": valid, "issues": issues}, indent=2))
    return 0 if valid else 1


def cmd_update_sections(args):
    """Update managed sections in CLAUDE.md or AGENTS.md."""
    file_path = Path(args.file)
    if not file_path.exists():
        print(json.dumps({"updated": False, "reason": f"{args.file} not found"}))
        return 1

    content = file_path.read_text()

    # Determine which content to use
    if file_path.name == "AGENTS.md":
        new_section = AGENTS_MANAGED_CONTENT
    else:
        new_section = CLAUDE_MANAGED_CONTENT

    if MANAGED_SECTION_START in content:
        # Replace existing managed section
        pattern = re.compile(
            re.escape(MANAGED_SECTION_START) + r".*?" + re.escape(MANAGED_SECTION_END),
            re.DOTALL
        )
        new_content = pattern.sub(new_section.strip(), content)
    else:
        # Append managed section
        new_content = content.rstrip() + "\n" + new_section

    file_path.write_text(new_content)
    print(json.dumps({"updated": True, "file": str(file_path)}))
    return 0


def cmd_deps(args):
    """Show parsed dependencies for a single project."""
    context_dir = find_context_dir(args.dir)
    if not context_dir:
        print(json.dumps({
            "error": "No .project-context/ directory found.",
            "hint": "Run /project-context:init first, then /project-context:add-dependency"
        }))
        return 1

    deps = parse_dependencies(context_dir)
    if not deps:
        print(json.dumps({
            "has_dependencies": False,
            "message": "No dependencies.json found.",
            "hint": "Run /project-context:add-dependency to declare cross-project relationships"
        }))
        return 0

    # Resolve paths and check if dependency contexts exist
    for dep_list_key in ("upstream", "downstream"):
        for dep in deps[dep_list_key]:
            if "git" in dep:
                # Git link dependency — check flat cache
                cache_path = context_dir / ".deps-cache" / dep["project"]
                dep["type"] = "git"
                dep["cached"] = cache_path.is_dir()
                dep["cache_path"] = str(cache_path) if cache_path.is_dir() else None
                dep["has_context"] = cache_path.is_dir()
                if cache_path.is_dir():
                    dep["context_files"] = [
                        f.name for f in cache_path.iterdir()
                        if f.is_file() and f.name != ".fetch-meta.json"
                    ]
            else:
                # Local path dependency
                dep_abs = (context_dir.parent / dep["path"]).resolve()
                dep["type"] = "local"
                dep["resolved_path"] = str(dep_abs)
                dep["exists"] = dep_abs.is_dir()
                dep["has_context"] = (dep_abs / ".project-context").is_dir()

    result = {
        "project_dir": str(Path(args.dir).resolve()),
        "has_dependencies": True,
        "git_deps_count": sum(
            1 for d in deps["upstream"] + deps["downstream"] if "git" in d
        ),
        **deps,
    }

    print(json.dumps(result, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Project context management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status command
    status_parser = subparsers.add_parser("status", help="Show context status")
    status_parser.add_argument("--dir", default=".", help="Project root directory")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate context files")
    validate_parser.add_argument("--dir", default=".", help="Project root directory")

    # update-sections command
    sections_parser = subparsers.add_parser("update-sections", help="Update managed sections in CLAUDE.md/AGENTS.md")
    sections_parser.add_argument("--file", required=True, help="Path to CLAUDE.md or AGENTS.md")

    # deps command
    deps_parser = subparsers.add_parser("deps", help="Show parsed dependencies for current project")
    deps_parser.add_argument("--dir", default=".", help="Project directory")

    args = parser.parse_args()

    commands = {
        "status": cmd_status,
        "validate": cmd_validate,
        "update-sections": cmd_update_sections,
        "deps": cmd_deps,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
