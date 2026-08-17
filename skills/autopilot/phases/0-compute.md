# Phase 0 — Compute routing

Autopilot's quality gates stay fixed; the compute used to reach them does not have to. Use the
least expensive native model/effort setting that can still pass the same gate, and raise it when
the cost or proof burden of the outcome rises.

This is an optional host capability, never an Autopilot dependency. Before doing product work,
inspect only trusted host metadata and callable controls. Determine whether the host can:

1. report the exact current thread, model and reasoning effort;
2. continue that same thread with a different effort while preserving the exact model;
3. set a model on a fresh subagent;
4. set reasoning effort on a fresh subagent;
5. confirm the delivered settings rather than merely acknowledge a request.

If a control is known to be missing before any override attempt, leave that part of routing off
and continue the flight unchanged. After an attempted continuation or spawn, however, an error,
thread/model/effort mismatch or missing delivered confirmation is not a graceful fallback: stop
product work, report requested and observed settings, and require restoration or explicit user
choice. Do not emulate effort with «think harder» text, identify a thread by title or recency, or
install another skill. Autopilot remains self-contained.

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

## The orchestrator

Phase 0–2 normally use `working`; deep/adversarial briefing uses `engineering`. Phase 3–4 use
`engineering`, raised to `critical` when the product contract itself contains a critical domain.
Phase 5 orchestration is `working` because executors are routed separately. Phase 8 reporting is
`working`; acceptance agents are routed in `8-final.md`.

Preserve the current exact model for a same-thread effort change. Continue the same thread at
most once per meaningful transition/gate, then confirm exact thread, model and effort before product
writes. Do not switch merely because a phase number changed, and do not downshift for a short
closeout. If capability is known to be absent before an attempt, keep flying at the current
setting; if an attempted continuation cannot be confirmed exactly, apply the stop rule above.

Record the capability result in the `state.js` created immediately before this phase. The cache
is advisory and session-scoped: re-probe on every fresh, compacted, or resumed agent session, and
never trust a previous result as proof that the current caller exposes the same controls.

```json
"computeRouting": {
  "sameThreadEffort": false,
  "subagentModel": true,
  "subagentEffort": true,
  "values": ["low", "medium", "high", "xhigh", "max"],
  "confirmedEffortBand": "working"
}
```

Use only values the current session actually reported. `false` is a valid result and means graceful
fallback, not a failed preflight. Compute routing changes no requirement, mode, approval,
testing rule, review axis or acceptance condition.
