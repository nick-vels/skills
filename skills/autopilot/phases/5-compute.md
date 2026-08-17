# Phase 5 — Executor compute

Read this after the tickets are cut and before the first wave launches. It routes fresh executor
contexts; it does not change ticket contents, waves, zones, return contracts or review.

Re-confirm fresh-subagent model and effort capabilities separately in the current agent session
before launch and refresh `state.js.computeRouting`. Apply only the controls confirmed for this
caller: if both are false, omit all overrides; if only effort is available, preserve the
current/default model; if only model is available, preserve the current/default effort. Then
follow `5-subagents.md` unchanged. A missing optimization is cheaper than pretending an override
worked.

## Route each ticket once

Choose the highest band triggered by the ticket's outcome, not by line count:

| Ticket shape | Model role | Effort band |
|---|---|---|
| mechanical, narrow, reversible, direct test | balanced | working |
| ordinary bounded implementation | balanced | engineering |
| architecture, cross-cutting contract, difficult diagnosis | flagship | engineering |
| auth, money, database migration, private data, concurrency, external side effect | flagship | critical |
| historical/irreversible data or several critical domains | flagship | maximum |

`balanced` and `flagship` are roles, not model names. Map them only when the current caller exposes
a confirmed fresh-subagent model override; otherwise preserve the host's current/default model.
Set the effort band only when its separate fresh-subagent effort override is confirmed. Use native
spawn arguments. Never place the routing request in the executor prompt: it is not a requirement
the executor can verify, and it consumes the context the routing is meant to save.

The acceptance criteria decide the floor. Repetition does not raise it: use deterministic scripts
or the existing wave orchestration for repeated work. Ambiguity, coupled ownership, difficult
proof or high consequence does raise it. Project instructions may raise any floor.

Write the delivered, confirmed choice into the ticket row after launch; use `default` for any
dimension the host preserved:

```json
"compute": { "modelRole": "balanced", "effortBand": "engineering" }
```

Record roles and bands, not provider-specific model IDs, so state survives on another host. If
an attempted spawn returns an error, mismatch or missing delivered confirmation, do not let that
executor edit and do not silently fall back: stop product work and report the requested and
observed dimensions. Graceful omission applies only when absence was known before the attempt.

Handoffs keep the ticket's band. A repair keeps it or raises it when the finding reveals a higher
risk; it never lowers it. The same tests, context ceiling and return contract apply at every band.
