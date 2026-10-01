# Phase 4 — Plan

`ap.py stage plan`. Cut the spec into tickets, each built by its own subagent in a fresh context.

**Every ticket boundary is a cold start** — read the interfaces, explore the code, find the commands: 20–40k tokens before a line is written. A ticket is worth creating only when the work inside it is bigger than that. **Fewer, denser tickets beat more, thinner ones**: each extra boundary is another context re-learning the project and another chance for two executors to disagree about an interface.

## Tier — read from the product, never from the length of the spec

| Tier | The product | Tickets |
|---|---|---|
| **T0** | one surface, one layer, no external service — a page, a form, a script, an endpoint | **one**, built by one executor from the whole spec |
| **T1** | one feature: a few surfaces over one data shape, at most one external service | 2–3 |
| **T2** | several features, or one crossing store, logic, interface and integration | 4–8 |
| **T3** | ≥ 3 genuinely independent subsystems, each with its own data | 9–16 |
| **>16** | — | **not allowed** — justify it in the spec in a line, or split into two runs |

A `deep` spec for a landing page is a long document about one page: still T0. Crossing a tier upward needs a reason written into the spec. State tier and count in one line to the user; `ap.py set tier=T2`.

## How to cut

- **Each ticket is a narrow but complete path through every layer it touches** — data, logic, interface, tests. When it lands, something works end to end that did not before.
- **The shell, the schema, the shared primitives are ticket 01, alone.** Nothing parallelises with it.
- Groundwork that makes later tickets easy goes early. Tickets closing `R` go before tickets closing only `A`.
- Number from `01` in dependency order; each ticket names what it depends on.
- **The payback test:** would its executor spend more flying in than building? Merge it into its neighbour. **The neighbour test:** under three acceptance criteria and the same files as an adjacent ticket? It is a checklist item there.
- **The merge pass**, mandatory, before any file is written: merge adjacent tickets on the same files, thin tickets with a natural parent, and chains where A alone demos nothing. A draft of 14 that merges to 7 was T2 pretending to be T3. A wide change below is the one chain the merge pass leaves alone.

## A wide change — new beside old

In existing code a requirement can change **one shared thing that many zones use**: rename a field, change the type of money, split a name, swap a library. A vertical slice never turns green on it — the first ticket changes the shared thing, every zone it did not touch breaks, and the check stays red. One ticket for all of it overflows its executor. Cut it in three steps, each green on its own:

1. **Expand** — the new thing appears **next to** the old one, and the old one keeps working: both fields, with the data copied and kept in sync; the new function, with the old one delegating to it. `Ревью: да — фундамент`, `сильная`.
2. **Migrate** — one ticket per zone moves its callers to the new thing. The old one is still there, so the zones not yet moved stay green; tickets on different zones fly in one wave. Criterion: «в `<зона>` не осталось обращений к `<старое>`».
3. **Contract** — once nothing calls the old thing, it is removed. Dropping a column with user data in it is `Ревью: да — удаление данных`.

Every ticket of the chain carries the same requirement. It applies when the change crosses more zones than one ticket owns; a shared thing used in one zone is an ordinary ticket. In a project built from scratch there is nothing to migrate — this never comes up.

## Waves and zones

**`wave = 1 + max(wave of what it depends on)`**, no dependencies → wave 1. Then **split each wave by zones**: two tickets writing the same files cannot fly together — the later one moves to the next wave. Every ticket names its **zone** — the directories and modules it owns, tests included. Waves are *discovered* in the dependency graph, never manufactured by splitting a ticket; a wave of one is a normal answer. A wave number, once written, is not renumbered — a real re-cut is said to the user in a line.

## Review and model — decided per ticket, here

**Review** — whether the ticket gets a point review before its commit (`phases/6-review.md`). Everything else is reviewed once, at the end, as part of the whole branch.

- `да — фундамент` — ticket 01, and any ticket building a shared module, the schema, or an interface other tickets call.
- `да — <риск>` — anything touching login and access rights, money, deleting or migrating user data, secrets, or messages sent to third parties.
- `нет` — the rest. Most tickets. **At T0 the one ticket is `нет` too**: the whole-branch review is its review, and a point review would read the same diff twice.

**Model** — who builds it.

- `сильная` — every ticket with review `да`, and any ticket whose core is a genuinely hard algorithm or an unfamiliar integration.
- `обычная` — the rest: a well-specified slice over decided boundaries. It runs on a cheaper model (`phases/5-subagents.md`).

## The ticket file

`.autopilot/<dir>/tickets/NN-<slug>.md`. The header lines are read by `ap.py` — keep their names:

```markdown
# 03 — Приём заявки от клиента

**Требования:** R01, R01.1, A01
**Зависит от:** 01, 02
**Зона:** `src/bot/` · `tests/bot/`
**Волна:** 2
**Ревью:** нет
**Модель:** обычная

## Что должно заработать

Клиент пишет боту, отвечает на три вопроса — что сломалось, адрес, телефон —
и получает подтверждение с номером заявки. Если сеть отвалилась на середине,
следующее сообщение продолжает с того же места.

## Из брифа, дословно

> «принимает заявки на ремонт техники»

## Разделы спецификации

Истории 1–5, Решения §2 и §4.

## Критерии приёмки

- [ ] Диалог из трёх шагов доходит до подтверждения
- [ ] Номер заявки уникален и виден клиенту
- [ ] Прерванный диалог продолжается, а не сбрасывается
- [ ] Незаполненный телефон даёт понятную ошибку, а не падение
```

- **The verbatim brief quotes are not decoration** — they are the last thing standing between a fresh context and a plausible reinterpretation, and the point reviewer judges the Manifest axis from them.
- **Every criterion is checkable and false at the commit the executor starts from.** A criterion already true tests nothing; the executor proves each one red before building it (`prompts/executor.md`).
- No file paths or code snippets except a structure prose states worse — a schema, a state machine.
- `Зависит от` lists ticket numbers only — `01, 02`, or `—`.

## Before the first ticket flies

**`interfaces.md` carries more than the boundaries** Phase 3 wrote there. Add the project rules an executor cannot derive: stack and versions; how to install, run, and **one check command** — tests, types and lint together — plus how to run a single test file (ticket 01 creates the check command if the project has none); what must not be touched. **Ticket 01 installs every dependency «Решения по реализации» names**; any other one comes back from an executor as `BLOCKED` (`phases/5-repair.md`).

## Gate G3, publishing, and the plan commit

`python3 .autopilot/ap.py tickets` publishes every ticket to the dashboard and moves their manifest rows to `in-ticket`; `python3 .autopilot/ap.py check-plan` is the gate. It checks both directions — every live requirement in some ticket, every ticket tracing to a requirement — and that every ticket has a zone and a wave, waves respect the dependencies, and no two tickets in one wave write the same zone. Each `!` line is a plan defect: fix the ticket files and run both again.

**Then the plan commit** — the run's first, and the base every later diff is measured from. Run the redaction gate over `.autopilot/` (`phases/1-manifest.md`), then commit exactly the files this skill wrote so far — never anything else in the tree:

```bash
git add -A -- .autopilot .gitignore AGENTS.md CLAUDE.md .env.example && git commit -qm "Autopilot: план сборки" -- .autopilot .gitignore AGENTS.md CLAUDE.md .env.example \
  && python3 .autopilot/ap.py set baseCommit="$(git rev-parse --short HEAD)"
```

Leave out of both lists any file that does not exist, and the memory file if it is the user's own.

A ticket that exists only in the dialogue is not a ticket — the user is shown a summary of files already on disk.

## Showing the plan

**Parallelism gets one line, and only if it is true**: «6 тасков в 4 волны, часть пойдёт параллельно».

- **semi, interview** — one screen, one plain line per ticket saying what the user will be able to do when it lands, then «Показываю план и начинаю. Скажи "стоп", если что-то не так» — and start. Never promise a countdown you cannot hold.
- **full** — the same screen as a notification.
- **manual** — a gate: technical detail, granularity and order discussed, an explicit «ок» before Phase 5.
