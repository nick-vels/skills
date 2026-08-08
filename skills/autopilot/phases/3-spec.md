# Phase 3 — Flightplan

Turn the manifest and the briefing answers into a specification. **This phase does not reopen the interview** — what is still unresolved becomes a `placeholder` row, not another round of questions.

One exception, and it is narrow: a genuine fork the briefing missed, where the two branches are different projects and a placeholder would only defer the same question to the build. Ask it, once, in one line, with a recommended answer. In **full** mode there is no exception — decide it and record the `ASSUMPTION`.

Write to `.autopilot/<slug>/spec.md`. What the user sees in the dialogue is a two-line summary; the file is the spec.

## Depth

**The brief is a silhouette.** The user describes what happens when everything goes right, at the level of «принимает заявки и складывает в таблицу». They do not describe what the third screen says when the network drops, what an empty list looks like, what happens on a double submit, or what the very first launch shows before any data exists. They are not withholding those answers — they do not have them, and they are not supposed to.

Working them out is the most valuable thing this phase can do. A spec that merely restates the brief in tidier words has produced nothing, and it guarantees the gaps get filled during implementation by whichever subagent hits them first, differently each time.

**How far to take it is the user's setting, not yours.** Read it from the announced depth:

| Depth | The depth pass below | `A##` new capabilities |
|---|---|---|
| **strict** | not run. Only *Wrong input* and *Failure*, and only where the requirement plainly breaks without them | **forbidden** — cut them, do not write them |
| **normal** *(default)* | run by judgement — the dimensions that plainly matter for that requirement, skipping the ones that do not | allowed, with parent and proportion |
| **deep** | run in full — every dimension, every requirement, or an explicit «не применимо» | encouraged, same parent and proportion |

At **strict**, an idea you had that the brief did not ask for does not become a spec section and does not become a note. It is simply not written. The user chose this setting to get exactly what they asked for, and a spec that argues with that choice has ignored an instruction.

At **normal**, use judgement rather than a checklist. Elaborate where the gap would obviously cause a bad build; do not chase every edge of every requirement. Most briefs belong here.

At **deep**, the pass is mechanical and exhaustive — that is what was asked for.

### The depth pass

Run at **normal** and **deep** (see the table above for how completely). Every `R##` requirement goes through this list.

At **deep**, skipping a dimension because a requirement «и так понятная» is exactly the mistake this pass exists to prevent — write «не применимо» instead of skipping silently.

| Dimension | The question the brief never answered |
|---|---|
| **First run** | what does this look like before any data exists? |
| **Empty** | zero items, zero results, zero history — what is on screen, and what invites the next step? |
| **Wrong input** | what does the user see, in their language, and what survives of what they typed? |
| **Failure** | the network, the service, the disk — what breaks, what is said, what is retried, what is lost |
| **Interruption** | closed halfway, refreshed, sent twice — does it resume, restart, or duplicate? |
| **Growth** | ten items versus ten thousand — what has to change, and does it now or later? |
| **Boundaries** | who may do this, and what happens to someone who may not? |
| **Aftermath** | where does the result go, who learns about it, can it be undone? |

Each answer becomes an `R##.n` story with its own acceptance line. `R##.n` never counts against any limit — it is the requirement the user actually made, worked out properly.

**The number of stories is an output, not a target.** A requirement that genuinely has seven dimensions gets seven stories; one that has two gets two, and padding it to look thorough is the same defect as skipping it. What is always wrong is twelve requirements producing twelve stories — that is the brief copied out rather than worked through.

### Two roads for depth

**Propose it** — when the answer is genuinely the user's to give (which of two behaviours they want, what tone the messages take, whether something is worth its cost). That is a briefing question, and one of the best a briefing can spend itself on.

**Decide it** — when the answer is craft, not preference. Error text, retry policy, empty-state copy, sensible limits, sane defaults. Decide, write it into the spec, and say so plainly in the summary. Asking the user which HTTP status to return is a wasted question; asking whether a cancelled order should refund automatically is not.

In **full** mode both roads collapse into the second — decide everything, and list what you decided in the final report. At **strict** depth, the first road narrows too: a question exists to clarify what the user asked for, never to sell them something extra.

### Keeping depth attached

The one failure mode worth guarding: depth that **floats free of the brief** — a beautiful subsystem grows while a plain requirement from line 2 quietly never gets a section. So every story carries a mark saying where it came from.

| Mark | Origin | Rule |
|---|---|---|
| `R##` | straight from the brief | untouchable |
| `R##.n` | **deepening** a brief requirement | uncapped — this is the main work of the phase |
| `G##` | decided in the briefing | the user confirmed it |
| `A##` | a **new capability** the brief never implied | must name a parent `R##` |
| `D##` | a constraint the **build** proved, added mid-flight | only from `phases/5-subagents.md`, never from an idea |

Note the line between the last two, because it is the one that gets blurred: elaborating «принимает заявки» into retry, resume and validation is `R01.n` — the same requirement, understood properly. Adding a loyalty programme is `A`. Depth is not scope creep, and treating it as if it were is how specs end up thin.

Three rules keep additions attached. They hold at **every** depth — `deep` relaxes none of them, and `strict` removes `A##` entirely:

- **Parenthood.** An `A##` story names the `R##` it serves. A free-floating invention gets cut — not because inventions are bad, but because one with no parent is a different project.
- **Proportion.** `A` stories may not outnumber `R` + `G` combined. `R##.n` never counts toward this — deepening what was ordered is unlimited by construction.
- **Precedence.** Recorded here, enforced in Phase 4: tickets closing `R` come before tickets closing only `A`. If time or patience runs out, what goes unfinished is your addition, never the user's request.

Every `A##` that survives into the build is listed in the final report under «что я добавил сверх заказанного», so the user learns about it from the report rather than from the code.

## The template

```markdown
# Спецификация: <название>

## Задача

Проблема пользователя своими словами — от лица того, кто ей страдает,
не от лица кода.

## Решение

Что появится у пользователя, когда всё будет готово. Тоже без техники.

## Пользовательские истории

| # | Метка | История | Приёмка |
|---|-------|---------|---------|
| 1 | R01 | Как клиент, я оставляю заявку боту, чтобы не звонить | бот принял и подтвердил |
| 2 | R01.1 | …и вижу понятную ошибку, если связь отвалилась | текст ошибки, не молчание |
| 3 | A01 → R01 | …и получаю номер заявки, чтобы на него ссылаться | номер в подтверждении |

Каждая история — «Как <кто>, я <что>, чтобы <зачем>» плюс то,
по чему видно, что она работает.

## Решения по реализации

Стек, модули и их границы, схема данных, контракты API, внешние сервисы.
Каждое решение — с одной строкой «почему так».
Без путей к файлам и без кода: они устареют раньше спецификации.

Исключение: если структура (схема, тип, конечный автомат) выражается
точнее кодом, чем прозой — вставь только её, без обвязки.

## Швы для тестов

Где проверяется поведение — через публичные границы, не через внутренности.
Предпочитай существующие швы новым. Чем меньше швов, тем лучше;
идеал — один. Назови их явно: Phase 5 тестирует только здесь.

## Вне рамок

Что осознанно НЕ строим. Каждая строка ссылается на требование манифеста,
которое она откладывает, и говорит почему.

| Требование | Почему не сейчас |
|---|---|
| R06i — админка для заявок | заявки видны в таблице; отдельный экран — следующий заход |

## Открытые места

Каждый `placeholder` из манифеста: что стоит заглушкой, где именно в коде,
и что от пользователя нужно, чтобы её закрыть.

## Покрытие манифеста

| Требование | Раздел спецификации |
|---|---|
| R01 | Истории 1–3, Решения §2 |
| R02 | Истории 4–5, Решения §4 |

Строк ровно столько, сколько живых требований в манифесте. Ни одной пропущенной.
```

## The vocabulary rule

If `CONTEXT.md` or `docs/adr/` exist, the spec speaks the project's language — the terms already defined there, not synonyms. A concept you need that the glossary lacks is a signal: either you are inventing language the project does not use, or there is a real gap worth noting. If a decision here contradicts a recorded one, say so out loud in the spec rather than overriding it silently.

## Gate G2 — before leaving this phase

Update every manifest row: `open` → `in-spec` with its section, or → `deferred` with its Out of Scope line.

Then check: **zero `open` rows.** An `open` row means the spec does not cover something the user asked for. That is not a note for later — it is an incomplete spec. Go back and write the missing section.

This is the single most valuable check in the whole flight. Everything downstream trusts the spec; this is the last moment the spec is still comparable to the words the user actually said.

## Showing it

**semi and full** — two lines in the chat: what will be built, and what deliberately will not. Then move on.

**manual** — the spec is a gate. Show it in full, stop, wait for an explicit «ок». Rewrite on every objection and ask again. Silence is not agreement, and neither is work already started.
