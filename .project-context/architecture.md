# Architecture

**Type:** Pure markdown Claude Code plugin

## Structure

```
.claude-plugin/plugin.json   # Plugin manifest (v2.8.0)
commands/                    # 9 slash command definitions (.md files)
skills/                      # 10 skill directories (SKILL.md + references)
agents/                      # 6 agent definitions (.md files)
scripts/
  manage_context.py          # Python context utility
  fetch_git_deps.py          # Git sparse-checkout utility
```

## How It Works

The plugin manifest (`plugin.json`) declares commands, skills, and agents. Claude Code loads these at session start. No compiled code — all behavior is defined in markdown files that Claude reads and executes as instructions.
