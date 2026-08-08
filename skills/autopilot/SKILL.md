---
name: autopilot
description: Use when the user dictates an app, site, bot, or feature to build end-to-end and expects a finished result without reviewing specs, tickets, or code — vibecoding sessions, non-technical users, "собери под ключ", "build it for me", "не задавай лишних вопросов" requests. Also use when the user invokes /autopilot, or asks for a build in a named mode or depth — «полный автомат», «ручной режим», «строго по брифу», «проработай глубоко».
argument-hint: "[full|semi|manual] [strict|deep] что нужно построить или путь к brief.md"
---

# Autopilot

## Overview

Autopilot flies a dictated idea from words to a working project **in one dialogue**, without making the user approve each stage. It is self-contained: every rule it needs lives in `phases/`. No other skill has to be installed.

Two ideas carry the whole design.

**The order is the product.** Code is written in the second-to-last phase. Everything before it exists to decide *what* to build, and everything after it exists to prove the right thing got built.

**The brief is the contract, not the design.** Two obligations follow from it, and they pull in opposite directions on purpose.

*Nothing may quietly vanish.* The user's original words become a numbered manifest before anything else happens, and every phase is gated on it. What breaks naive vibecoding is not bad code — it is a requirement that stopped existing somewhere around the third rewrite.

*The brief is not the design.* It is a silhouette: it describes the happy path and nothing underneath — no empty states, no failures, no interruptions, no limits. Working those out is legitimate work, not scope creep, and it is where much of the value of this process comes from. **How far to take it is the user's dial**, set by the [depth](#depth) parameter. What is never allowed at any setting is depth that **detaches** from the brief.

## Reading this skill

This file is the orchestrator: modes, phase order, gates. The rules for each phase live in `phases/` and are **read at the moment that phase starts, not before** — that is what keeps the working context small.

| Phase | Read | Produces |
|---|---|---|
| 0 Preflight | `phases/0-preflight.md` | repo configured, `.autopilot/` created |
| 1 Manifest | `phases/1-manifest.md` | `brief.md`, `manifest.md` |
| 2 Briefing | `phases/2-briefing.md` | answers recorded into the manifest |
| 3 Spec | `phases/3-spec.md` | `spec.md` |
| 4 Plan | `phases/4-plan.md` | `tickets/NN-*.md` (or none — see tiers) |
| 5 Subagents | `phases/5-subagents.md` | code, commits, `interfaces.md` |
| 6 Review | `phases/6-review.md` | per-ticket review |
| 7 Instruments | `phases/7-instruments.md` | `state.json`, `dashboard.html` (opened for the user) |
| 8 Final | `phases/8-final.md` | blind acceptance, final report |
| 9 Memory | `phases/9-memory.md` | `CLAUDE.md` / `AGENTS.md` — the project as the next session will find it |

## The words the user sees

The phases have English names in this file and the user never sees them. In the chat, on the dashboard and in the final report there is **exactly one Russian word per stage**, and it is this one. Two vocabularies for one process is how a person reads the README and then cannot find any of it on the screen.

| Phase | `stages[].id` | Пользователю |
|---|---|---|
| 0 Preflight | `preflight` | Подготовка |
| 1 Manifest | `manifest` | Требования |
| 2 Briefing | `briefing` | Брифинг |
| 3 Spec | `spec` | Спецификация |
| 4 Plan | `plan` | План |
| 5 Subagents | `build` | Разработка |
| 6 Review | `review` | Код-ревью |
| 8 Final | `final` | Приёмка |

Two rules hold this together:

- **«Сборка» — это весь прогон, а не один этап.** «Сборка идёт», «сборка прервалась», «продолжи сборку» — про процесс целиком. Поэтому пятый этап называется «Разработка»: иначе одно слово означает и часть, и целое. И «сборка» в смысле `npm run build` — тоже не он.
- **Единица работы — «таск».** Не «задача», не «тикет», не «issue». «Задача» — это то, что поставил пользователь (бриф); одно слово на две разные вещи ломает и отчёт, и дашборд.

Phases 7 and 9 are not sequential. The instruments are written and opened in Phase 0, then updated at every stage transition and after every ticket. The project memory is raised in Phase 0, topped up when the build discovers something, and written in full in Phase 8 by a subagent reading the finished code.

## Modes

Everything typed after `/autopilot` splits into three parts: **the mode** (optional bare word — `full`, `semi`, `manual`), **the depth** (optional bare word — `strict`, `deep`), and **the brief** (everything else). No dashes on either parameter. Text that is not a recognised parameter is always brief.

`/autopilot full deep интернет-магазин керамики` — full mode, deep elaboration. Order does not matter; both parameters are optional and independent.

| Mode | Triggers | Human gates |
|---|---|---|
| **full** — полный автомат | `/autopilot full`, «полный автомат», «полностью сам», «ничего не спрашивай», "fully automatic", "don't ask me anything" | none |
| **semi** — полуавтомат **(default)** | `/autopilot semi`, «полуавтомат», nothing specified | questions only |
| **manual** — ручной | `/autopilot manual`, «ручной режим», «согласовывай каждый шаг», "ask me everything", "approve every step" | questions + spec + tickets |

- **Announce the resolved mode and offer the others, once, before Phase 1.** The user must never discover the mode by noticing questions that did or did not arrive — and they cannot ask for a mode they do not know exists. In a chat client there is no `--help` to read: this block is the only place the dials are ever named, so it is not optional.

  ```
  Режим: полуавтомат · глубина: обычная — спрошу только то, что в задаче не определено, дальше соберу сам.
  Дашборд открыл: .autopilot/dashboard.html — обновляется сам.
  Память проекта — AGENTS.md (+ CLAUDE.md со ссылкой). Скажи, если нужен другой.

  Можно переключить в любой момент, просто скажи:
  • «полный автомат» — не спрашиваю вообще ничего
  • «ручной режим» — согласуешь со мной спецификацию и список тасков
  • «строго по брифу» / «проработай глубоко» — меньше или больше проработки сверх сказанного
  ```

  One short block, once, at the start. **It is a hint, not a question** — say it and go straight into Phase 1; waiting for a reply to it is exactly the pause this skill exists to remove. Do not repeat it later, do not restate it after a mid-run switch (one line is enough there: «Понял, дальше ручной режим»).
- **Ambiguity resolves to semi.** A mode word contradicting the rest of the sentence («ручной режим, но не спрашивай») → the explicit mode word wins; two mode words → ask which one, in one line.
- **The mode can be switched mid-run** («переключись в ручной») — it applies from the next phase onward. Phases already passed are not replayed.
- **Extra instructions in the brief** (stack, language, budget, «без базы данных», deadline) are manifest requirements like any other. They constrain the build; they never replace a phase.
- **No mode removes the manifest gates or the safety gates.** Irreversible or outward-facing actions — deploy, publish, pay, send messages to third parties, delete data, rewrite git history — stay a question in **all three** modes, including full.

## Depth

How far past the brief's own words the spec is allowed to go. The mode decides *how much the user is asked*; depth decides *how much is worked out for them*. They are independent.

| Depth | Triggers | Deepening a requirement (`R##.n`) | New capabilities (`A##`) |
|---|---|---|---|
| **strict** | `/autopilot strict`, «строго по брифу», «только то, что сказал», «ничего не добавляй», "strictly as written", "nothing extra" | only what the requirement cannot work without | **not allowed** |
| **normal** **(default)** | nothing specified | freely, by judgement — as much as the feature warrants | allowed, with a parent, within proportion |
| **deep** | `/autopilot deep`, «проработай глубоко», «максимальная глубина», «продумай за меня», "go deep", "think it through" | the full depth pass, every dimension, every requirement | actively encouraged, same two limits |

- **Default is normal, and normal means permitted.** The agent elaborates where elaboration obviously helps and does not chase every edge of every requirement. This is the setting most briefs should run on.
- **`strict` does not mean careless.** Errors and empty states are still handled — a build that crashes on bad input does not satisfy the requirement it was written for. What `strict` removes is anything the user did not ask for: no extra capabilities, no anticipating needs, no "пока я тут, добавлю".
- **`deep` does not lift the attachment rules.** Every `A##` still names its parent requirement; the proportion limit still holds. `deep` buys thoroughness, never a different project.
- **Depth is announced with the mode**, in the same opening block: «Режим: полуавтомат · глубина: максимальная».
- **Depth can be changed mid-run** («поменьше отсебятины», «продумай глубже») — applies from the next phase. Already-written spec sections are not retroactively trimmed unless the user asks.

The rules for each level live in `phases/3-spec.md`.

## When to Use

- User dictates what to build and expects the finished thing, not a collaboration on process.
- User is non-technical: will not read specs, judge ticket granularity, or review code.
- "Собери под ключ", "just build it", "не задавай лишних вопросов".
- User wants to approve the spec and the tickets but not to run the pipeline by hand — that is **manual** mode, still Autopilot.

**When NOT to use:** the user wants to co-author the code itself line by line (work with them directly); the task is a small single-file change (just do it); the idea is bigger than one project and its destination is unclear (settle the destination first, then return here).

## The flight

| Phase | full | semi (default) | manual |
|---|---|---|---|
| 0 Preflight | auto | auto | auto |
| 1 Manifest | auto | auto | auto |
| 2 Briefing | skipped → self-briefing | only what the brief leaves open — sometimes none | the same, with more patience |
| 3 Spec | auto | auto | show → wait for explicit «ок» |
| 4 Plan | auto, notify only | auto, stoppable | discuss → wait for explicit «ок» |
| 5 Subagents | auto | auto | auto |
| 6 Review | auto | auto | auto |
| 8 Final | report + Assumptions | report | report |

**The manifest gates run in every mode.** They are checks against the user's own words, not requests for the user's time — no mode buys the right to skip them.

| Gate | After phase | Condition to pass |
|---|---|---|
| **G1** | 2 Briefing | every requirement has a status; none left `open` without a reason recorded |
| **G2** | 3 Spec | every live requirement is `in-spec`, `deferred`, or `dropped`. Zero `open` |
| **G3** | 4 Plan | every `in-spec` maps to ≥1 ticket, **and every ticket traces back to ≥1 requirement** |
| **G4** | 8 Final | blind acceptance run; every disagreement with the manifest reported |

A failed gate is not a warning. It sends the phase back to be redone — see `phases/1-manifest.md`.

**The plan may be corrected; the brief may not.** When the build proves the plan wrong — a data model that does not hold, an assumed interface that cannot exist — the spec is amended and a `D##` row records what the code demonstrated and when. That is the one thing allowed into the manifest after the briefing, it never retires a requirement, and it is never a route for an idea you had. Rules in `phases/5-subagents.md`.

## Secrets

Credentials are the user's to hold, not the agent's to handle. This section binds every phase; the phases do not restate it.

- **Never request one.** No key, token, password, connection string, or card number is ever a question. *Which* provider is a question. *Whether* an account exists is a question. The credential is not.
- **Redact at ingest, before anything is written.** The brief, every user answer, and every pasted fragment pass the redaction gate in `phases/1-manifest.md` *before* they reach a file. A detected secret becomes `[REDACTED:<VAR_NAME>]` — the variable name survives, the value does not.
- **"Verbatim" always means "verbatim after redaction."** Wherever this skill asks for the user's exact words, it asks for them redacted. The two rules are one rule.
- **Refer to it by name.** `STRIPE_SECRET_KEY`, not the value. The user puts the value in `.env` themselves; `.env` is in `.gitignore` before the first commit; the final report lists which names are still empty.
- **A leaked secret is a stop condition.** A secret that reached a file or a commit is reported immediately, in plain language, with the advice to rotate it. Before the first commit, run the redaction gate over the whole of `.autopilot/`.

## Files this skill owns

```
.autopilot/
├── <feature-slug>/
│   ├── <YYYY-MM-DD>-brief.md   the user's original words, redacted, never edited again
│   ├── manifest.md      R01…Rnn — requirements and their status
│   ├── spec.md          the specification
│   ├── interfaces.md    what finished tickets built, for the tickets that follow
│   └── tickets/NN-<slug>.md
├── README.md            how to read this folder — for the human, written once in Phase 0
├── state.json           machine-readable run state: stages, tickets, timings, debt
└── dashboard.html       the human view — opened automatically in Phase 0, refreshes itself

CLAUDE.md | AGENTS.md   the project memory — what the next session reads first
```

The brief is dated in its filename because a slug directory outlives one sitting. The dashboard is opened for the user, not described to them: it shows the eight stages of the cycle, where the run is now, and a live clock on the run, the current stage and the current ticket.

`.autopilot/` is the record of **this** run; the memory file at the root is the project as it stands, for whoever opens the repo next. Autopilot's content there lives between `<!-- autopilot:start -->` markers — everything the user wrote outside them is untouchable. See `phases/9-memory.md`.

`.autopilot/` is committed, not ignored — it is the user's record of what was promised and what was delivered. A run that leaves nothing under `.autopilot/` did not happen.

## Judgement

This skill describes a process, not the product. Its numbers — tiers, question counts, story counts, wave widths — are **calibration for a first guess, never targets to hit.** A spec written to reach a story count, or a plan cut to land inside a tier, has optimised for the rule instead of for the person who asked.

The rules below are the same kind of thing. Each one is here because it was paid for, and each is an argument — arguments can lose. Where following one would make the result worse for the user, break it deliberately, say so in one line, and carry on. That is a decision, and decisions get recorded. What is never acceptable is breaking one quietly, or keeping one because it is written down.

**Four rules are not calibration and do not lose.** They hold in every mode, at every depth, at every tier:

1. **A requirement is removed only by the user**, in their own words, quoted into the manifest.
2. **A secret is never requested, echoed, or written** — not into a file, a prompt, a commit, or a report.
3. **A fact about the user is never invented.** Prices, texts, addresses, accounts stay visible placeholders until they supply them.
4. **An irreversible or outward-facing action is a question** — deploy, publish, pay, message a third party, delete data, rewrite history.

Everything else is argument.

## Rationalizations — the ones that cost the user the product

Phase-specific mechanics are not here; they live in the phase that owns them. What follows is the short list of excuses that end with the user getting something other than what they asked for.

| Excuse | Reality |
|--------|---------|
| «Пользователь сказал не задавать вопросов» | Он сказал не задавать ЛИШНИХ. Решающие вопросы — часть работы, не обсуждение процесса. |
| «KISS — просто собери» | Простой результат даёт порядок, а не пропуск этапов. Без спецификации каждая правка — «а я имел в виду другое». |
| «Бриф весь в диалоге, зачем его переписывать в файл» | Диалог сжимается, и бриф в нём — самое старое. Через три фазы ты будешь синтезировать по пересказу пересказа. |
| «Это требование явно неважное, пропущу» | Важность требований определяет пользователь. Ты можешь предложить `deferred` — вычеркнуть может только он. |
| «Пользователь про это больше не вспоминал — значит, отменил» | Молчание не отменяет. Отмена — это его слова, записанные в манифест цитатой. |
| «Сделаю заглушку, уточнит потом» | Блокирующие неизвестные (оплата, хостинг, аккаунты) решаются в брифинге — в полном автомате в self-briefing, — но всегда до билда. |
| «Пусть пришлёт ключ, я вставлю в код» | Ключи вставляет пользователь и только в `.env`. Ты работаешь с именем переменной. |
| «Ключ уже в контексте, значит, можно записать» | Наоборот: значит, надо отредактировать и предупредить. Контекст — не разрешение. |
| «Быстрее всё сделать в одном контексте» | Быстрее в первый час. Дальше модель ходит кругами и ломает работавшее. |
| «Бриф краткий — значит, и спецификация краткая» | Бриф — силуэт: пользователь описал happy path и не описал ни пустых состояний, ни ошибок, ни обрывов. На нормальной и максимальной глубине продумать их — твоя работа. |
| «Это и так очевидно, писать не буду» | Очевидное тебе — не зафиксировано, и каждый субагент додумает его по-своему: три исполнителя — три разные «очевидности». Манифест и спецификация — единственные точки сверки. |
| «Придумал полезную фичу, добавлю» | Углубление заказанного (`R##.n`) — да. Новая возможность (`A`) — только с родительским требованием, в пределах пропорции и в отчёт. На `strict` — нельзя вообще. |
| «Полный автомат — значит можно и задеплоить» | Автомат снимает вопросы о продукте, а не право на необратимое. Деплой, оплата, рассылка, удаление — гейт во всех режимах. |
| «В полном автомате можно додумать за пользователя всё» | Решения — да, и все в ASSUMPTIONS. Факты о пользователе (цены, тексты, аккаунты) — нет: заглушка и строка в отчёте. |
| «Напишу "запускаю через 60 секунд"» | Ты не умеешь ждать — обещанной паузы не будет. Честная формулировка: «начинаю, скажи стоп». |
| «В ручном режиме тоже начну и подожду возражений» | В ручном согласование — это явное «ок». Молчание им не является, начатая работа тем более. |
| «Сверю результат со спецификацией, этого хватит» | Спецификация может уже потерять требование. Финальная сверка идёт с брифом и без спецификации — иначе она подтвердит собственную ошибку. |
| «Таски и спецификация видны в чате — зачем файлы» | Файл в `.autopilot/` и есть артефакт; чат — только его пересказ. Диалог умрёт, файлы останутся. |
| «Пользователь не спрашивал про режимы — не буду грузить» | Он и не спросит: в чате нет `--help`. Пять строк в начале — единственное место, где он вообще узнаёт, что у сборки есть ручки. |
| «Проект собран, тесты зелёные — значит, работает» | Тесты писал тот же процесс, что и код. Пока проект никто не запустил, «работает» — это гипотеза, а первым его запустит пользователь. |

## Red Flags — start the phase over

Every line here means something the user asked for is at risk. Phase mechanics — instruments, timestamps, wave bookkeeping, memory-file detection — are checked in the phase files that own them, not here.

- Writing code before the spec exists.
- The brief was never written to its file — the run is anchored to nothing.
- A requirement left the manifest without a status, or was marked `dropped` without a quote of the user saying so.
- Past gate G3: a ticket that traces to no requirement, or a requirement that traces to no ticket.
- Spec or tickets that exist only in the dialogue — nothing written under `.autopilot/`.
- Instruments that disagree with the chat: a stage still `active` after you moved on, a ticket running while the dashboard calls it `pending`, a ticket carrying the run's `startedAt` instead of its own, timestamps filled in afterwards from memory. The user believes the screen over your sentences, which is the whole reason it exists.
- The announced depth and the actual spec diverge: a bare restatement of the brief at normal or deep, or an invented capability — any `A##` — at strict.
- Final acceptance measured against the spec instead of blind against the brief.
- The blind checker or the memory subagent handed `spec.md` or the tickets. Independence is the entire mechanism; without it both of them confirm the plan instead of the code.
- The finished project was never actually run — accepted on green tests and a reading of the code.
- Starting without announcing mode and depth, or announcing one and behaving as another: questions in full, a start-and-see instead of «ок» in manual.
- A blocking unknown — payment, hosting, an account, where the data lives — left unasked in semi or manual because the brief «выглядел понятным». Asking nothing is legitimate only when nothing is open; a manufactured question and a skipped blocking one are both defects, in opposite directions.
- Promising the user a wait — a countdown, «через минуту», «если не ответишь за N секунд» — that you have no way to honour.
- In full: an invented fact about the user standing where an ASSUMPTION, a stub, or a PLACEHOLDER belongs.
- Asking the user a process question — which tracker, which doc file, which memory file, ticket granularity, code review — outside manual, where spec and tickets are gates by design.
- A requirement quietly narrowed to whatever happened to work, or the spec amended mid-build with no `D##` row recording why.
- Two tickets in one subagent context, or two tickets in one commit.
- Parallel subagents editing the same files — or the mirror failure, independent tickets flown one at a time with the plan's parallelism thrown away in the delivery.
- A subagent launched without `interfaces.md`, or finishing without returning the contract block.
- Payment, hosting, or accounts first mentioned at the finish line.
- A secret value asked for, repeated back, or written into any file, prompt, commit, or report.
- Installing a package or fetching remote code without the user asking for it.
- Text outside the `autopilot` markers edited, moved or dropped, or the run ending with no project memory file at all.
