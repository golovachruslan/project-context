#!/usr/bin/env python3
"""
Shared helpers for the project-wiki scripts (wiki_lint, wiki_search, wiki_stats).

Pure standard library, Python 3.10+. No external dependencies.

A "vault" is a directory laid out as:

    <vault>/
      index.md, log.md, dependencies.md, CLAUDE.md, AGENTS.md
      people/+<name>.md             (vault-level person profiles)
      people/index.md               (people catalog)
      projects/<slug>/
        _project.md, index.md, progress.md, refs.md
        indexes/<type>.md           (optional, sharded indexes)
        raw/<date>-<slug>.md        (immutable sources)
        wiki/<type>/<page>.md       (compiled knowledge pages)

People are linked with a `+` prefix, e.g. `[[+jane-smith]]`, which resolves to
`people/+jane-smith.md` (the `+` is part of the filename, so the existing
basename index resolves it with no special handling).
"""

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Size budgets (lines). Mirrors the schema documented in the vault CLAUDE.md.
# ---------------------------------------------------------------------------
BUDGETS = {
    "_project.md": {"hard": 60},
    "progress.md": {"hard": 80},
    "index.md": {"soft": 300},          # shard threshold
}
WIKI_PAGE_SOFT = 400
WIKI_PAGE_HARD = 800
INDEX_PAGE_SHARD_COUNT = 150            # shard once a project exceeds this many pages

PEOPLE_DIR = "people"                   # vault-level person profiles: people/+<name>.md

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def is_person_link(token):
    """True if a wikilink token addresses a person profile (e.g. `+jane-smith`)."""
    return token.startswith("+")


def person_slug(token):
    """Strip the leading `+` person marker from a link token / filename stem."""
    return token.lstrip("+")


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------
def parse_frontmatter(text):
    """Parse a leading YAML frontmatter block.

    Returns (meta: dict, body: str). Supports scalars, inline lists
    (`k: [a, b]`), block lists (`- item`), and block lists of mappings
    (used by `sources:`). Values are str | list; mapping items become dicts.
    Good enough for lint/search/stats — not a full YAML parser.
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    # first line is the opening '---'
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text

    meta = {}
    cur_key = None
    cur_list = None
    cur_map = None  # in-progress mapping item within a list

    def close_list():
        nonlocal cur_list, cur_map, cur_key
        if cur_key is not None and cur_list is not None:
            meta[cur_key] = cur_list
        cur_list = None
        cur_map = None

    for raw in lines[1:end]:
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()

        if indent == 0 and re.match(r"^[\w.\-]+:", stripped):
            close_list()
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "":
                cur_key = key
                cur_list = []          # may stay [] if nothing follows
                meta[key] = ""         # provisional
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                meta[key] = [v.strip().strip("'\"") for v in inner.split(",") if v.strip()] if inner else []
                cur_key = None
            else:
                meta[key] = val.strip("'\"")
                cur_key = None
        elif stripped.startswith("- ") and cur_key is not None:
            item = stripped[2:].strip()
            if cur_list is None:
                cur_list = []
            # mapping item like `- raw: ...`
            m = re.match(r"^([\w.\-]+):\s*(.*)$", item)
            if m:
                cur_map = {m.group(1): m.group(2).strip().strip("'\"")}
                cur_list.append(cur_map)
            else:
                cur_map = None
                cur_list.append(item.strip("'\""))
            meta[cur_key] = cur_list
        elif cur_map is not None and re.match(r"^[\w.\-]+:\s*", stripped):
            # continuation key of a mapping item
            k2, _, v2 = stripped.partition(":")
            cur_map[k2.strip()] = v2.strip().strip("'\"")

    close_list()
    body = "\n".join(lines[end + 1:])
    return meta, body


def has_value(meta, key):
    """True if `key` is present and non-empty."""
    if key not in meta:
        return False
    v = meta[key]
    if v is None or v == "":
        return False
    if isinstance(v, list) and len(v) == 0:
        return False
    return True


# ---------------------------------------------------------------------------
# Vault traversal
# ---------------------------------------------------------------------------
def projects_dir(vault):
    return Path(vault) / "projects"


def iter_projects(vault):
    """Yield Path for each project directory under <vault>/projects/."""
    pdir = projects_dir(vault)
    if not pdir.is_dir():
        return
    for child in sorted(pdir.iterdir()):
        if child.is_dir():
            yield child


def iter_wiki_pages(vault, project=None):
    """Yield Path for every compiled wiki page (projects/*/wiki/**/*.md)."""
    for proj in iter_projects(vault):
        if project and proj.name != project:
            continue
        wiki = proj / "wiki"
        if not wiki.is_dir():
            continue
        for p in sorted(wiki.rglob("*.md")):
            yield p


def iter_people(vault):
    """Yield Path for each vault-level person profile (people/+*.md), skipping
    the catalog (people/index.md)."""
    pdir = Path(vault) / PEOPLE_DIR
    if not pdir.is_dir():
        return
    for p in sorted(pdir.glob("*.md")):
        if p.name == "index.md":
            continue
        yield p


def iter_all_markdown(vault):
    """Yield every .md file in the vault (skips _templates/)."""
    for p in sorted(Path(vault).rglob("*.md")):
        if "_templates" in p.parts:
            continue
        yield p


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def line_count(path):
    return len(read_text(path).splitlines())


def extract_wikilinks(text):
    """Return list of link targets, alias/heading stripped, frontmatter removed."""
    _, body = parse_frontmatter(text)
    out = []
    for raw in WIKILINK_RE.findall(body):
        target = raw.split("|", 1)[0]      # drop alias
        target = target.split("#", 1)[0]    # drop heading anchor
        target = target.strip()
        if target.endswith(".md"):
            target = target[:-3]
        if target:
            out.append(target)
    return out


def build_link_index(vault):
    """Map link tokens -> set of resolvable page paths.

    Indexes each markdown file by both its vault-relative path (no extension,
    posix) and its bare basename, so Obsidian-style `[[basename]]` and
    `[[projects/foo/_project]]` both resolve.
    """
    index = {}
    vault = Path(vault)
    for p in iter_all_markdown(vault):
        rel = p.relative_to(vault).with_suffix("").as_posix()
        base = p.stem
        for token in (rel, base):
            index.setdefault(token, set()).add(p)
    return index


def relpath(vault, path):
    return Path(path).relative_to(Path(vault)).as_posix()
