# Challenge Examples & Edge Cases

## Examples

### Example 1: Challenging a Plan (with project-context)

**User:** "I'm planning to add Redis caching. /challenge"

**Output:**

```markdown
## Challenging: Add Redis caching layer to improve API response times

**Context:** Reviewed `.project-context/architecture.md` — current stack is Express + PostgreSQL. No caching infrastructure exists. Team size: 3 developers per `brief.md`.

### Skeptic
What evidence shows caching will help?
- No profiling data referenced in the proposal
- Have we confirmed slow responses are from repeated computations vs. DB queries vs. network?
- Adding cache without measurements is optimizing blind

### Pragmatist
Redis adds significant operational complexity for a 3-person team:
- New service to deploy, monitor, scale
- Cache invalidation logic to maintain
- Simpler alternatives exist:
  - In-memory LRU cache (no new infrastructure)
  - HTTP cache headers (leverage existing CDN)
  - Database query optimization

### Chaos Engineer
Cache failure modes are notoriously subtle:
- Stale data after writes — what's the business impact?
- Cache stampede after restart — cold cache + traffic spike
- No cache warming strategy mentioned
- Degradation behavior when Redis is down?

### Architect
Per `architecture.md`, project follows "minimal infrastructure" principle:
- Redis would be first external stateful service besides PostgreSQL
- No existing team expertise in Redis operations
- Alternative: PostgreSQL materialized views align with existing stack

### Root Cause
Caching treats a symptom, not the cause:
- What queries are slow? Missing indexes?
- N+1 query patterns in the API layer?
- Caching may mask problems that compound as data grows

### Future Dev
Cache-related bugs are hard to debug:
- "Works locally" because cache state differs
- How will new devs understand what's cached?
- Invalidation logic becomes tribal knowledge

---

**Key Concerns (Prioritized):**
1. No profiling data — guessing at root cause
2. May be masking real issues (query optimization, N+1s)
3. Operational complexity high for team size

**Recommendation:** Address concerns first — profile API, check queries, then decide if caching needed.

Which of these should we address before proceeding?
```

### Example 2: Quick Mode

**User:** "/challenge --quick"

**Context:** Reviewing a PR with retry logic.

**Output:**

```markdown
## Challenging: Retry logic with exponential backoff in HttpClient

**Top Concerns:**

1. **No maximum retry limit visible** (Chaos Engineer)
   - Could retry indefinitely on persistent failures
   - Causes resource exhaustion, blocks other requests
   - **Action:** Add `maxRetries` parameter with sensible default (3-5)

2. **Duplicates existing pattern** (Architect)
   - Similar retry logic exists in `src/clients/external_api.py:45-62`
   - Violates DRY, creates maintenance burden
   - **Action:** Extract to shared `RetryPolicy` utility

3. **Magic numbers without context** (Future Dev)
   - `backoff_multiplier=2`, `base_delay_ms=100` are hardcoded
   - Future devs won't know why these values
   - **Action:** Extract to config or add comments explaining choices

Address these before merging?
```

### Example 3: User-Specified Focus

**User:** "/challenge 'focus on security implications'"

**Output:**

```markdown
## Challenging: Webhook endpoint for third-party integrations

**Focus:** Security implications (user-specified)

### Skeptic (Security Lens)
- How do we verify webhook payloads are from legitimate sources?
- No mention of signature verification (HMAC, etc.)
- What data is exposed in webhook payloads? PII? Credentials?

### Chaos Engineer (Security Lens)
- Webhook endpoints are common DDoS vectors
- Rate limiting strategy?
- Replay attacks — are webhooks idempotent?

### Architect (Security Lens)
- Where does webhook secret storage live?
- Webhook logs may contain sensitive data — retention policy?

### Future Dev (Security Lens)
- How do developers test webhooks locally without exposing secrets?
- Documentation for secure webhook setup?

---

**Key Concerns (Prioritized):**
1. No payload signature verification — anyone can send fake webhooks
2. No rate limiting — trivial DDoS target
3. Secret storage approach undefined

**Recommendation:** Address security concerns first — this is attack surface expansion.

Which of these should we address before proceeding?
```

## Edge Cases

### No Clear Target
If unclear what to challenge:
```
I don't see a clear plan or code change to challenge. Could you:
1. Share what you'd like me to critique
2. Reference a specific proposal from our conversation
3. Share a code diff or implementation plan
```

### Already Well-Designed
If genuinely well-designed after thorough analysis:
```
After analyzing from all six perspectives, this approach is solid:

**Strengths noted:**
- [Strength 1]
- [Strength 2]

**Minor considerations (not blocking):**
- [Minor point]

**Recommendation:** Proceed — no significant concerns found.
```

### User Disagrees with Concerns
If user pushes back on a concern:
```
I understand. Let me clarify my reasoning:

[Explain the concern more specifically]

If you've already considered this and have mitigations in place, that addresses my concern.
Would you like me to document this in the challenge log as "accepted with mitigation"?
```
