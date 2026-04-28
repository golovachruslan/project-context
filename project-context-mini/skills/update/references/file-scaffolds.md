# File scaffolds

Starter templates for the four `.project-context/` files. Used by the `update` skill in bootstrap mode. Keep each scaffold short — users see `<TODO>` markers and fill them in.

---

## `architecture.md`

```markdown
# Architecture

## Diagram

\`\`\`mermaid
graph TD
  A[<TODO: entry point>] --> B[<TODO: core component>]
  B --> C[<TODO: data store>]
\`\`\`

## Components

- **<TODO: component name>** — <TODO: one-line purpose>

## Data Model

- **<TODO: entity>** — <TODO: key fields, relationships>

## Tech Stack

- Language: <TODO>
- Framework: <TODO>
- Storage: <TODO>
- Deploy: <TODO>

## Dependencies

- <TODO: external service or library the project leans on>
```

---

## `flows.md`

```markdown
# User Flows

## <TODO: Primary flow name>

\`\`\`mermaid
sequenceDiagram
  actor User
  participant App
  participant <TODO: service>

  User->>App: <TODO: trigger>
  App->>+<TODO: service>: <TODO: call>
  <TODO: service>-->>-App: <TODO: response>
  App-->>User: <TODO: result>
\`\`\`

<TODO: one-sentence description of what this flow accomplishes>
```

---

## `patterns.md`

```markdown
# Patterns

## Conventions

- **<TODO: convention name>** — <TODO: rule and rationale>

## Anti-patterns

- **<TODO: what NOT to do>** — <TODO: why it bites>

## Gotchas

- **<TODO: non-obvious behavior>** — <TODO: how to handle it>
```

Mermaid diagrams are optional here — use only when genuinely helpful (e.g., a decision tree for "which pattern to apply when").

---

## `status.md`

```markdown
# Status

## Current Focus

<TODO: one sentence on what's actively being worked on>

## Why it matters

<TODO: one sentence on why this focus is the priority now>

## Next Action

<TODO: the next concrete step>
```

No history log. No blockers section unless a blocker is load-bearing for the current focus.

---

## Bootstrap seed questions

When `update` runs in bootstrap mode, ask the user these to pre-fill scaffolds:

1. **Project goal** — one sentence on what this project is and who uses it.
2. **Tech stack** — primary language, framework, storage.
3. **Core user flow** — the single most important journey a user takes.
4. **Current focus** — what are you actively working on right now?
5. **Upfront conventions or gotchas** (optional) — anything an incoming teammate should know on day one?

Keep follow-ups minimal. If the user answers briefly, accept brief scaffolds — the `update` skill can deepen them later.
