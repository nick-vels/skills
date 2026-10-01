# Phase 3 — Spec

`ap.py stage spec`. Turn the manifest and the answers into `.autopilot/<dir>/spec.md` — the contract the executors and reviewers work from. The user sees two lines; the file is the spec.

**An existing codebase is explored first.** When Phase 0 found code, one subagent on the cheaper model reads the repository once and writes `.autopilot/<dir>/notes.md`: where things live, the conventions in use, the commands that run it, and **the exact names of the entities, fields and functions the work will touch** — so boundaries are decided against the code that exists, and two parallel tickets do not call one field `blockedSince` and `blockedOn`. Every executor reads it later instead of exploring from scratch. A new repo has nothing to explore.

**This phase does not reopen the interview.** What is still unresolved becomes a `placeholder`. One narrow exception: a genuine fork the briefing missed, where the branches are different projects — ask it once, in one line, with a recommendation. In full there is no exception: decide it and record the `ASSUMPTION`.

## Depth — the brief is a silhouette

The user describes what happens when everything goes right. They do not describe the empty list, the dropped network, the double submit, the first launch before any data exists — they do not have those answers, and they are not supposed to. **Working them out is the most valuable thing this phase does**; a spec that restates the brief in tidier words has produced nothing, and the gaps get filled later by whichever executor hits them, differently each time.

How far to take it is the user's setting:

| Depth | The depth pass | `A##` new capabilities |
|---|---|---|
| **strict** | only *Wrong input* and *Failure*, and only where the requirement plainly breaks without them | forbidden — not written at all |
| **normal** | by judgement — the dimensions that plainly matter for that requirement | allowed, with a parent and in proportion |
| **deep** | every dimension of every requirement, or an explicit «не применимо» | encouraged, same limits |

| Dimension | The question the brief never answered |
|---|---|
| **First run** | what does this look like before any data exists? |
| **Empty** | zero items, zero results — what is on screen, and what invites the next step? |
| **Wrong input** | what does the user see, in their language, and what survives of what they typed? |
| **Failure** | network, service, disk — what breaks, what is said, what is retried, what is lost? |
| **Interruption** | closed halfway, refreshed, sent twice — resume, restart or duplicate? |
| **Growth** | ten items versus ten thousand — what has to change, now or later? |
| **Boundaries** | who may do this, and what happens to someone who may not? |
| **Aftermath** | where does the result go, who learns about it, can it be undone? |

Each answer becomes an `R##.n` story with its own acceptance line. The number of stories is an output: seven dimensions that matter give seven stories, two give two, and padding is the same defect as skipping.

**Two roads.** *Propose* when the answer is the user's to give — that was a briefing question. *Decide* when it is craft — error text, retry policy, limits, defaults — write it in and say so in the summary. In full, everything is decided and listed in the report; at strict, nothing is offered beyond what was asked.

## Keeping depth attached

| Mark | Origin | Rule |
|---|---|---|
| `R##` | the brief | untouchable |
| `R##.n` | **deepening** a brief requirement | uncapped — the main work of the phase |
| `G##` | **the user's own words**, later | untouchable, like `R##` |
| `A##` | a **new capability** the brief never implied | names a parent `R##` |
| `D##` | a constraint the **build** proved | only via `phases/5-repair.md` |

Elaborating «принимает заявки» into retry, resume and validation is `R01.n`; a loyalty programme is `A`. Three rules hold at every depth:

- **Parenthood** — every `A##` names the `R##` it serves; one with no parent is a different project and is cut.
- **Proportion** — `A` stories never outnumber `R` + `G` combined.
- **Precedence** — tickets closing `R` fly before tickets closing only `A`, so a run cut short leaves your additions unfinished, never the user's request.

## Boundaries — decided here, written to `interfaces.md`

Several executors in fresh contexts build one project only if the **boundaries between modules are already decided**. Leave them open and ticket 01 decides them, having seen an eighth of the задача, and everything after it obeys that shape or quietly builds a second one.

For every unit the build will have: **what it owns**, **what it exposes** (signatures other units call — names and shapes, not implementations; names in English, never transliterated Russian, unless the existing code does otherwise), **what it hides**. Then the **test seams** — a subset of those same boundaries, the fewer the better, existing ones preferred. Boundaries follow the depth pass, not the requirement list; a boundary no ticket crosses is not a boundary; a few deep modules beat many shallow ones.

**Write this straight into `.autopilot/<dir>/interfaces.md`** under «Границы, решённые в спецификации» — it is the file every executor reads first — and keep in the spec only a pointer to it. In manual this is the part of the spec gate worth discussing: it is the one decision expensive to change later.

## The file

**A small product** — one surface, one feature, what Phase 4 will call T0 or T1 — gets a short spec: Задача; Решение with one line per live requirement saying what the user gets, depth included; Решения по реализации; Вне рамок; Открытые места. No stories table — the acceptance criteria are written once, in the ticket.

**Otherwise:**

```markdown
# Спецификация: <название>

## Задача
Проблема пользователя его словами — от лица того, кто ей страдает.

## Решение
Что у него появится, когда всё будет готово. Без техники.

## Истории
Каждое живое требование — хотя бы одна история; проработка и добавления — свои строки.

| # | Метка | История | Приёмка |
|---|-------|---------|---------|
| 1 | R01 | Как клиент, я оставляю заявку боту, чтобы не звонить | бот принял и подтвердил |
| 2 | R01.1 | …и вижу понятную ошибку, если связь отвалилась | текст ошибки, не молчание |
| 3 | A01 → R01 | …и получаю номер заявки, чтобы на него ссылаться | номер в подтверждении |

## Решения по реализации
Стек, схема данных, контракты, внешние сервисы — каждое с одной строкой «почему».
Без путей и кода, кроме структуры, которую код выражает точнее прозы.

## Границы и швы
См. `interfaces.md`.

## Вне рамок
| Требование | Почему не сейчас |
|---|---|
| R06i — админка | заявки видны в таблице; отдельный экран — следующий заход |

## Открытые места
Каждый `placeholder`: что стоит заглушкой, где, что нужно от пользователя.
```

Which section covers which requirement lives in the manifest's «Где» column, not in a second table here.

**Vocabulary:** if `CONTEXT.md`, `GLOSSARY.md` or `docs/adr/` exist, the spec speaks their terms, not synonyms, and a contradiction with a recorded decision is said out loud.

## Gate G2 — before leaving

**1. Your own pass.** Every manifest row: `open` → `in-spec` with its section in «Где», or → `deferred` with its «Вне рамок» line. **Zero `open`**, or the spec is incomplete — write the missing section.

**2. The independent coverage check** — the half that works. You wrote the spec, so you cannot see what you did not write. Spawn a subagent with **exactly the named files** — every `*-brief.md` in `dir`, oldest first, and `spec.md` — never the manifest (your reading of the brief), the conversation or a summary; and tell it not to go looking, because the files sit in `.autopilot/` beside the manifest:

> Открой только названные файлы и больше ничего — ни `manifest.md`,
> ни остальное содержимое `.autopilot/`. Твоя ценность в том, что ты
> не видел, как автор спецификации читал задачу. Не вызывай скиллы
> и не запускай своих агентов.
>
> Файлы брифа — задача словами заказчика, по порядку дат. Разделы «Дополнения»
> в них — сказанное позже, и при расхождении верно более позднее.
> Последний файл — спецификация.
>
> Найди всё, что заказчик просил, а спецификация не покрывает: цитата из брифа
> и одна строка, чего нет. Отдельно — покрытое наполовину, так что по нему нельзя
> собрать. Отдельно — то, чего в брифе не было, а в спецификации есть.
>
> Не оценивай качество и не предлагай улучшений. Только факт расхождения.
> Расхождений нет — так и скажи.

Act on it before leaving: *missing* → write the section; *half-covered* → write what was missing; *not in the brief* → attach it to a parent as `A##` or cut it. Record it in one call — `ap.py coverage found=N fixed=N deferred=N --item "…"` with an `--item` for each finding not fixed in the spec — so the report can say whether the gate ever caught anything. A finding here costs a paragraph; the same finding at G4 costs the build.

## Showing it

**full, semi, interview** — two lines: what will be built and what deliberately will not, plus where the file is. Then start. In interview the user is not owed the document for their answers — they chose questions, not gates.

**manual** — the spec is a gate: show it in full, wait for an explicit «ок», rewrite on every objection. Silence is not agreement, and neither is work already started.
