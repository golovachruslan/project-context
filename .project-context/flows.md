# User Flows

## Update — bootstrap or refresh context

```mermaid
sequenceDiagram
  actor User
  participant Skill as update skill
  participant Extractor as content-extractor
  participant Critic as update-critic
  participant Files as .project-context/

  User->>Skill: /project-context-mini:update
  Skill->>Files: detect bootstrap vs refresh
  alt bootstrap
    Skill->>User: 5 seed questions
    Skill->>Files: write 4 scaffolds
  else refresh
    Skill->>Extractor: chat / scan / input
    Extractor-->>Skill: ranked candidates
    Skill->>Critic: filter candidates
    Critic-->>Skill: kept + rejected
    Skill->>User: approve updates
    Skill->>Files: apply edits
  end
```

Bootstrap creates the four files from seeded scaffolds. Refresh runs the two-agent extractor+critic pipeline to ruthlessly filter new knowledge before writing.

## Discuss — prime agent for project conversation

```mermaid
sequenceDiagram
  actor User
  participant Skill as discuss skill
  participant Files as .project-context/

  User->>Skill: /project-context-mini:discuss [topic]
  Skill->>Files: read 4 main files inline
  Skill->>Files: list refs/*.md paths only (lazy)
  Skill-->>User: framing prompt scoped to topic
```

Lazy-loads `refs/*.md` — the agent reads a specific ref on demand to prevent context bloat as refs accumulate.
