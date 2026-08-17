# Phase 5 — Repair, failure and amendments

**Read this only when a ticket comes back as anything other than `DONE`** — a review finding, a red suite, `BLOCKED`, `NEEDS_CONTEXT`, or a build that proved the plan wrong. Most tickets return `DONE`, and most runs should never open this file.

It is separate from `phases/5-subagents.md` for the same reason `polish.md` is separate: it is a branch, not a step. Six thousand characters about what to do when things go wrong, resident in the orchestrator's context from the first ticket onward, are paid for on every turn of every ticket that went fine.

The three counters this file spends — `repairs`, `retries`, `handoffs` — are all capped at two, and all three mean the same thing when they run out: the cut was wrong, and that belongs in the report, not in another attempt.

## Repair — two kinds, two addresses

**First: not every finding comes here.** Only what the reviewer put in `BLOCKING` — a requirement not delivered, an invented fact about the user, unrequested surface, a red suite — becomes a дозапрос. Craft judgement calls go to `state.js` under `concerns` and are triaged once, at the end, by the whole-project pass (`phases/6-review.md`, `phases/8-final.md`). Sending every finding down this path is what makes reviewing everything feel unaffordable: thirteen repairs across nine tickets, each adding about forty percent to its ticket's clock.

A ticket comes back imperfect in two very different ways, and telling them apart is the whole of this section:

- **Недоделка** — a red test, a blocking review finding, an acceptance criterion met in letter and dodged in substance. The executor *could* have done it and did not.
- **Отказ** — `BLOCKED`, `NEEDS_CONTEXT`, or a repair that has already failed. The executor tried and could not.

| | Недоделка | Отказ |
|---|---|---|
| Goes to | **the same subagent**, by message, its context intact — a **дозапрос** | a **fresh context**, and only with a changed approach |
| You send | the acceptance criterion, and nothing else | the ticket again, the error, the failing test named, the path now spelled out |
| Because | it holds why the code is the way it is; a cold reader repairs the symptom and breaks the reason | its context *is* the failure — it is stuck in its own groove, and the same request gets the same answer |

**A дозапрос costs one line.** Do not resend `interfaces.md`, the spec sections or the testing contract — it has seen all three. Send the condition:

```
Тест `parses empty address` красный:
<последние 10 строк вывода>

Назови причину одной строкой, потом чини — так, чтобы тест проходил.
Больше ничего не трогай. Верни контракт заново.
```

- **The cause first, then the fix — one line of it, in the дозапрос.** A repair that starts at the symptom fixes the symptom: the same defect returns two tickets later through a different door, and by then the `repairs` counter is spent. If the executor cannot name a cause, that is `BLOCKED`, not a workaround. **A weakened or deleted assertion is not a repair** — the re-review sees the fix's diff and this is the first thing it is looking at.
- **Two дозапроса into one context, then it stops being the cheap option.** By the third the context is no longer the fresh one that made this worth doing, and the repair moves to the right-hand column: new context, changed approach. That is the same rule as for a failed ticket, because by then it is one.
- **State the finding as a condition, never as «поправь».** «Сделай получше» is an invitation to rewrite what already worked. Every repair names something checkable: this test green, this field visible, this error handled.
- **The repair returns the contract block again** — new `FILES`, new `TESTS`. A repair that returns nothing is a ticket you cannot honestly commit.
- **The author repairs; someone else judges.** Sending the finding back to the executor is cheap precisely because it keeps its context — which is also why it cannot review its own repair. Step 4 stays with a subagent that did not write the code.
- **And that second look is scoped to the repair.** Send the reviewer the fix's diff and the findings it was meant to close — not the ticket again. It verdicts each finding addressed or not and flags new breakage inside the fix only. A full re-review costs what the first one cost, to re-derive a verdict you already hold, and it is the difference between a two-round ceiling and an evening.
- **If continuing a subagent is not available in the harness you are running in**, fall back to a fresh context with the full ticket prompt plus the finding, and accept that it costs more. What is not a fallback is taking the keyboard yourself. That option feels like the cheapest one available and is the most expensive thing in the phase.

## When a ticket fails

The right-hand column above, and its rules are the strict ones.

Retry **once**, in a fresh context, with the error attached and the failing test named. If that fails too, one further attempt is allowed **only with a changed approach** — a different design decision, a different library, a path the ticket now names explicitly. Running the same attempt again with more hope is not a retry, and it is the only version of this that is forbidden.

After that the flight stops: tell the user in plain language what is blocking and what you need from them. Do not improvise around a blocker, and do not silently narrow the ticket to whatever happened to work — a quietly reduced ticket is a lost requirement, and this whole design exists to make that impossible.

Mark it `failed` in `state.js` and `placeholder` in the manifest, with the reason.

One failure does not abort its wave-mates — they are independent by construction, so let them land. What it does stop is everything **downstream**: its dependents stay `pending`, and naming which ones are now blocked is part of the sentence you tell the user.

## When the build contradicts the plan

The plan was written before the code existed, so sometimes the code is right and the plan is wrong: a data model that does not hold, an interface the spec assumed cannot exist, two requirements that turn out to be incompatible in practice. This is ordinary, it is not the executor's error, and it needs a path — because without one what actually happens is worse. The executor quietly builds something else, the spec keeps claiming otherwise, and every check downstream measures the build against a document that stopped being true at ticket four.

A subagent that hits this returns `BLOCKED` or `DONE_WITH_CONCERNS` with what it found. **You decide, in the orchestrator's context — never the executor**, and never by letting it stand. Deciding is yours; the code that follows from the decision is still written below you, by dozapros or by a fresh ticket:

1. **Amend the spec section.** Edit the affected part of `spec.md` in place, keep the story marks, and add one line saying what the code proved and at which ticket. From the first ticket onward the spec is a living document; the brief and the manifest quotes are not.
2. **Record a `D##` row in the manifest** — *discovered*. Its Основание is the finding, and it names the requirement it serves. This is not a requirement the user made; it is a constraint reality imposed, and it carries a status and appears in the final report like everything else.
3. **Re-cut only what the change invalidates.** Landed tickets stay landed. Unstarted tickets get their spec references updated; a ticket whose whole point disappeared is cut and its requirements go back to `in-spec` to be re-covered.
4. **Tell the user one line, in every mode including full:** «Схема из плана не держала два адреса на одну заявку — поправил, требование то же». They do not need the reasoning. They do need to know the plan moved, because a plan that moves silently is how the final report and their memory of the project stop matching.

Two things this is not:

- **Not a way to drop a requirement.** A requirement the code proves impossible is a question for the user — in full mode, an ASSUMPTION plus a placeholder — never a `D##` that quietly retires it.
- **Not a route for good ideas.** A discovery is something the code demonstrated, not something you thought of while writing it. Ideas are still `A##`, still need a parent and the proportion limit, and at `strict` are still forbidden.
