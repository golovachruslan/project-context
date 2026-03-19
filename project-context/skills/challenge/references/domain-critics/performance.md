# Performance Critic

**Activates when:** Database operations, API endpoints, loops, data processing, caching discussions, scale requirements mentioned.

**Focus:** Speed, resource usage, scalability bottlenecks

## Questions

- What's the time complexity? O(n), O(n²), worse?
- Database query efficiency? N+1 problems?
- Memory allocation patterns?
- Network round trips?
- Blocking operations in async code?
- Resource leaks (connections, file handles)?
- How does this behave at 10x, 100x current load?
- Are there hot paths that will be called frequently?
- Caching opportunities or cache invalidation risks?
- Index usage in database queries?

## Output Format

```markdown
### Performance Critic
Bottleneck analysis:
- [Bottleneck 1] — Impact: [description]
- [Bottleneck 2] — Impact: [description]

Scale concerns (at 10x load):
- [Issue]

**Optimization priority:** [High/Medium/Low]
```
