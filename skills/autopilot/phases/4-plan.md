# Phase 4 — Waypoints

Cut the spec into units of work, each built by its own subagent in its own fresh context.

Before cutting anything, understand what a cut costs.

## The cost of a boundary

Every ticket boundary is a fresh context that has to fly in from nothing: read the interfaces, explore the code, work out the stack, find the test command. Call it 20–40k tokens of pure re-orientation before a single line gets written. And the subagent runs a review at the end, which is more contexts again.

So a ticket is worth creating **only when the work inside it is bigger than its own boundary**. A ticket carrying eighty words of instruction pays full price for a boundary and delivers a fraction of the value.

This is the mistake to avoid, and it is not the obvious one. Cutting too fine feels careful. It is the opposite: each extra boundary is another chance for two subagents to disagree about an interface, and another whole context spent re-learning the project. **Fewer, denser tickets beat more, thinner ones** — every time.

## The tier budget

Decide the tier from the spec, then cut to it. State the tier and the count in one line to the user.

| Tier | When | Tickets |
|---|---|---|
| **T0** | spec ≤ ~800 words, ≤ 3 files, one layer, no external service | **none — build straight from the spec in one context** |
| **T1** | spec ≤ ~2000 words, one coherent feature | 2–3 |
| **T2** | spec ≤ ~5000 words, several features or several layers | 4–8 |
| **T3** | ≥ 3 genuinely independent subsystems, or waves that can truly run in parallel | 9–16 |
| **>16** | — | **not allowed.** Either justify it in a line in the spec, or split the work into two Autopilot runs |

**T0 is real and it is common.** A landing page, a form, a script, a single endpoint — cut nothing, build it in one pass, review once, done. Skipping tickets here is not a shortcut; creating them would be the waste. Say so plainly: «Задача небольшая — собираю сразу, без разбивки».

Crossing a tier upward needs a reason written into the spec, not a feeling.

## How to cut

Each ticket is a **narrow but complete path through every layer** it touches — data, logic, interface, tests. Not a horizontal slice of one layer. When it is done, something works end to end that did not work before, and you can show it.

- Anything that has to exist before the rest — the shell, the shared primitives, the schema — is ticket 01, alone. Nothing parallelises with it.
- Groundwork that makes later tickets easy goes early. Make the change easy, then make the easy change.
- Give each ticket its **blocking edges** — the tickets that must finish before it can start. No blockers means it can start immediately.
- Number from `01` in dependency order, blockers first.
- **Tickets closing `R` requirements come before tickets closing only `A`.** If the run is cut short, what is missing must be your additions, never the user's request.

## The floor — two tests every ticket must pass

**The payback test.** Would its subagent spend more effort flying in than building? Then it is not a ticket. Merge it into the neighbour it depends on.

**The neighbour test.** Fewer than three acceptance criteria, touching the same files as an adjacent ticket, and not separated from it by a wave boundary? Then it is a checklist item inside that neighbour, not a ticket of its own.

## The merge pass — mandatory

After the draft, before writing any files, go through the list once more and merge:

- adjacent tickets touching the same files with no wave between them;
- any ticket under three acceptance criteria that has a natural parent;
- chains where B is blocked by A, nothing else is blocked by A, and A alone demos nothing.

Then re-check the tier. A draft that lands at 14 and merges to 7 was a T2 job pretending to be T3 — normal, and the reason this pass exists.

## Density — the other half of the rule

Cutting fewer tickets only helps if each one carries what its subagent needs. The failure mode is a ticket so thin that the executor fills the gaps by guessing.

Every ticket file:

```markdown
# 03 — Приём заявки от клиента

**Требования:** R01, R01.1, A01
**Blocked by:** 01, 02
**Status:** ready

## Что должно заработать

Клиент пишет боту, отвечает на три вопроса — что сломалось, адрес, телефон —
и получает подтверждение с номером заявки. Если сеть отвалилась на середине,
следующее сообщение продолжает с того же места, а не начинает заново.

## Из брифа, дословно

> «принимает заявки на ремонт техники»
> «чтобы клиент видел статус»

## Разделы спеки

Истории 1–5, Решения §2 и §4, Швы §1.

## Критерии приёмки

- [ ] Диалог из трёх шагов доходит до подтверждения
- [ ] Номер заявки уникален и виден клиенту
- [ ] Прерванный диалог продолжается, а не сбрасывается
- [ ] Незаполненный телефон даёт понятную ошибку, а не падение
- [ ] Тест на шве §1 покрывает полный путь и обрыв
```

The verbatim brief quotes are not decoration. They are the last thing standing between a fresh context and a plausible reinterpretation of what was ordered — and they cost about forty tokens.

Avoid file paths and code snippets: they go stale faster than the ticket does. The exception is a structure that prose states worse than code — a schema, a state machine, a type shape. Then inline just that.

## Gate G3 — before publishing

**Forward:** every `in-spec` requirement appears in at least one ticket's Требования line. A requirement in no ticket does not get built.

**Backward:** every ticket names at least one requirement. **A ticket tracing to nothing is work nobody ordered** — cut it, or attach it to what it actually serves. This direction catches the invented subsystem that would otherwise consume three contexts and confuse the acceptance run.

Then update the manifest: `in-spec` → `in-ticket`, with the ticket number.

## Showing the plan

Write the files first. **A ticket that exists only in the dialogue is not a ticket** — what the user sees is a summary of files already on disk.

**semi** — one screen, plain language, no technical detail, one line per ticket saying what the user will be able to do when it lands. Then: «Показываю план и начинаю. Скажи "стоп", если что-то не так». Then start. Do not wait for approval — waiting is the failure mode this skill exists to remove. **Never promise a countdown:** you cannot hold a pause, so a stated delay is a promise you will break. The user's window to object is their own reaction, and saying so plainly is the honest version of it.

**full** — the same screen as a notification. No pause.

**manual** — the plan is a gate. Show it with technical detail, discuss granularity and order, adjust on request, wait for an explicit «ок». Phase 5 starts only on agreed tickets.
