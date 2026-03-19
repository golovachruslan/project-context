# Dependency Loading Pattern

Standard pattern for loading and reasoning about cross-project dependencies.
Reference this document from any skill that reads project context.

## When to Load

Check for `.project-context/dependencies.json`. If absent, skip entirely — no dependency awareness needed.

```bash
ls .project-context/dependencies.json 2>/dev/null
```

## Step 1: Build Dependency Digest

Read and parse `dependencies.json`. Produce a concise summary for your working context:

```
Dependency Map:
↑ upstream: shared (local: ../shared) — "Shared library for domain types and validation" — provides: Types, validation utilities
↑ upstream: auth-service (git, cached) — "Authentication microservice handling OAuth2 and JWT" — provides: Auth API types, JWT schemas
↓ downstream: web-app (local: ../web-app) — consumes: REST API endpoints
```

Format rules:
- `↑ upstream` — projects this project depends on (consumes from)
- `↓ downstream` — projects that depend on this project (consume from us)
- Include `local: <path>` or `git, cached` / `git, not cached` in parens
- If `description` is present, include it in quotes immediately after the location — this gives instant orientation without loading any files
- Show the `what` field verbatim — it's the key boundary routing signal

## Step 2: Boundary Detection

Compare the feature/plan/topic at hand against each dependency's `what` field.

A **boundary is crossed** when the current work involves:
- Concepts explicitly named in a dep's `what` (e.g., "auth tokens" ↔ `"Auth API types, JWT schemas"`)
- Files typically owned by that dep (types, shared utilities, APIs)
- Changes that would affect what the dep provides or consumes

When a boundary is detected, flag it explicitly so it informs the rest of the workflow.

## Step 3: Selective Context Loading

Load dep context **only for relevant dependencies**, not all of them.

**If `description` is present:** the digest already provides basic orientation — skip loading `brief.md` unless the task requires detailed architectural understanding (internal structure, data flow, decision rationale).

**For local path dependencies:**
```
Read <path>/.project-context/brief.md
Read <path>/.project-context/architecture.md
```

**For git link dependencies:**
```
Read .project-context/.deps-cache/<project>/brief.md
Read .project-context/.deps-cache/<project>/architecture.md
```

**Always:**
- Never load a dependency's `state.md` or `progress.md` — those are their internal concern
- Load at most 1-2 dependencies per session to protect context budget
- Prioritize upstream deps that provide what we're changing

**If git dep cache is missing:** Warn that context is unavailable. Suggest running `/project-context:add-dependency --fetch` to populate it.

## Step 4: Stale Cache Warning (Git Deps Only)

Check `.project-context/.deps-cache/<project>/.fetch-meta.json` for `fetched_at` timestamp.

If cache is older than 7 days:
```
⚠️ Dependency context for `[project]` was last fetched [N] days ago.
   Consider running: /project-context:add-dependency --fetch
```

This warning is informational — do not block the workflow.

## Dependency-Aware Behaviors by Skill

### discuss — Surface integration gray areas

When the feature description matches a dep's `what` field:
- For upstream deps: "This touches [what] provided by `[project]` — do we need to coordinate changes upstream first?"
- For downstream deps: "Downstream `[project]` consumes [what] from us — will this be a breaking change for them?"
- If the dep's context is cached, load it and ask more specific questions based on its architecture

### project-context:plan — Include cross-project coordination

When a plan task involves a dep boundary:
- Add "Cross-Project Impact" section to the plan (see plan/SKILL.md template)
- Add explicit coordination tasks: "Update shared types in [dep path]", "Verify [downstream] still builds"
- Mark coordination tasks as dependencies of implementation tasks in the DAG

### project-context:challenge — Evaluate integration risks

When deps exist, each critic should explicitly evaluate:
- **Chaos Engineer**: "What breaks in downstream `[dep]` if this change is deployed?"
- **Architect**: "Does this change respect the contract declared in dependencies.json (`[dep]` provides `[what]`)?"

### implement — Flag boundary-crossing changes

During execution, when modifying files that relate to a dep's `what` field:
- Warn before making the change: "This may affect `[dep]` which depends on [what]"
- After completion, note affected deps in the summary
- Add to deviation rules: ASK before making changes that may break downstream contracts

### info — Load dep context for integration queries

When the question is about integration, dependencies, or a topic matching a dep's `what` field:
- Load the relevant dep's `brief.md` + `architecture.md`
- Answer the question using both local and dep context

### validate — Check dependency health

For each declared dependency:
- Local: verify path exists and target has `.project-context/`
- Git: verify cache exists in `.deps-cache/<project>/` and is not stale

### plan-verification — Check cross-project coverage

When a plan touches dep boundaries (based on `what` field matching):
- Verify plan includes cross-project coordination (Impact section or explicit tasks)
- Flag as Warning if missing
