# Phase 0 — Compute routing

Autopilot's quality gates stay fixed; the compute used to reach them does not have to. Use the
least expensive native model/effort setting that can still pass the same gate, and raise it when
the cost or proof burden of the outcome rises.

This is an optional host capability, never an Autopilot dependency. Before doing product work,
inspect only trusted host metadata and callable controls. Determine whether the host can:

1. report the exact current thread/request, model and reasoning effort;
2. apply an orchestrator effort change immediately, on a distinct next request, or not at all;
3. set a model on a fresh subagent;
4. set reasoning effort on a fresh subagent;
5. confirm delivered settings and request identity rather than merely acknowledge a request.

If a control is known to be missing before any override attempt, leave that part of routing off
and continue the flight unchanged. After an attempted spawn, however, an error, mismatch or
missing delivered confirmation is not a graceful fallback: stop product work, report requested
and observed settings, and require restoration or explicit user choice. Do not emulate effort
with «think harder» text, identify a thread by title or recency, or install another skill.
Autopilot remains self-contained.

## The five bands

Use the host's nearest supported native value, never a lower one:

| Band | Common effort value | Use |
|---|---|---|
| light | `low` | direct read-only lookup, obvious extraction |
| working | `medium` | manifest, ordinary briefing, bookkeeping, bounded reversible work |
| engineering | `high` | specification, planning, non-trivial code, integration, independent review |
| critical | `xhigh` | auth, permissions, money, database mutation, private data, concurrency, external writes |
| maximum | `max` / host equivalent | historical or irreversible data, several critical domains, difficult release audit |

The highest triggered risk wins. A small diff is not a light outcome. When two adjacent bands
remain equally plausible after the minimum inspection needed to tell, use the higher one.

## Keep one orchestrator floor for the flight

Hosts that activate an effort selector only on a distinct next request make phase-by-phase
orchestrator switching slower, not cheaper. Choose one sticky floor before substantive flight
work: `engineering` for an ordinary full build, `critical` when its contract includes a critical
domain, and `maximum` for several critical domains or irreversible/historical release work.

Preserve the orchestrator's exact current model. If its confirmed effort is below the floor,
request one upward transition. Do not downshift it during the flight. Phase 5 orchestration,
Phase 7 bookkeeping and Phase 8 reporting stay at the floor; fresh executors, reviewers and
acceptance agents carry the fine-grained savings.

For a host whose effort mode is `next-request`, use its authoritative immutable identifier for
the currently executing request (`turn_id` in Codex Desktop) as `sourceExecutionId`. Before
requesting the transition, persist the complete `pendingEffortTransition` below. If that write
cannot be completed, do not request the transition; stop and report the persistence failure.
A native continuation error or confirmed delivery failure leaves that pending boundary intact:
stop, report requested versus observed state, and never retry from the source execution.
A selector update or a continuation delivered inside that same source execution is pending, not
confirmed and not failed. Stop product work and yield. On the next execution, require the stored
thread, preserved exact model, a different authoritative execution ID, and the exact requested
native effort before clearing the pending transition and writing product state. If that distinct
execution mismatches or lacks confirmation, apply the stop rule. Never retry from the source
execution.

```json
"pendingEffortTransition": {
  "sourceThreadId": "opaque-host-thread-id",
  "sourceExecutionId": "opaque-host-turn-or-request-id",
  "sourceModel": "native-model-id",
  "requestedEffort": "high",
  "targetBand": "engineering"
}
```

The native continuation handoff carries the minimum live work state. The pending object is the
only temporary exception to the provider-neutral state rule: exact native values are required to
verify the boundary after interruption or compaction, and are removed as soon as the distinct
execution is confirmed.

An external controller may route an idle thread without a user-visible pause. A host with
`immediate` mode may continue directly after authoritative confirmation. A host with
`unavailable` mode keeps the current setting; a project policy may still require manual elevation
before a protected action.

Record the capability result in the `state.js` created immediately before this phase. The cache
is advisory and session-scoped: re-probe on every fresh, compacted, or resumed agent session, and
never trust a previous result as proof that the current caller exposes the same controls.

```json
"computeRouting": {
  "orchestratorEffortMode": "next-request",
  "subagentModel": true,
  "subagentEffort": true,
  "values": ["low", "medium", "high", "xhigh", "max"],
  "confirmedEffortBand": "engineering",
  "pendingEffortTransition": null
}
```

Use only values the current session actually reported. `unavailable` is a valid mode and means
graceful fallback, not a failed preflight. Compute routing changes no requirement, mode,
approval, testing rule, review axis or acceptance condition.
