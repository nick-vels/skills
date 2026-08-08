---
name: autopilot
description: Use when the user dictates an app, site, bot, or feature to build end-to-end and expects a finished result without reviewing specs, tickets, or code — vibecoding sessions, non-technical users, "собери под ключ", "build it for me", "не задавай лишних вопросов" requests. Also use when the user explicitly invokes /autopilot, optionally with a mode — full ("полный автомат", no questions at all), semi (default, questions only), manual ("ручной режим", approve spec and tickets by hand) — and optionally a depth — strict ("строго по брифу", nothing beyond what was asked) or deep ("проработай глубоко", full elaboration of every requirement).
argument-hint: "[full|semi|manual] [strict|deep] что нужно построить"
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
  Режим: полуавтомат · глубина: обычная — задам 5–8 вопросов, дальше соберу сам.
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
| 2 Briefing | skipped → self-briefing | 5–8 questions | questions until clear, no cap |
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
├── state.json           machine-readable run state: stages, tickets, timings, debt
└── dashboard.html       the human view — opened automatically in Phase 0, refreshes itself

CLAUDE.md | AGENTS.md   the project memory — what the next session reads first
```

The brief is dated in its filename because a slug directory outlives one sitting. The dashboard is opened for the user, not described to them: it shows the eight stages of the cycle, where the run is now, and a live clock on the run, the current stage and the current ticket.

`.autopilot/` is the record of **this** run; the memory file at the root is the project as it stands, for whoever opens the repo next. Autopilot's content there lives between `<!-- autopilot:start -->` markers — everything the user wrote outside them is untouchable. See `phases/9-memory.md`.

`.autopilot/` is committed, not ignored — it is the user's record of what was promised and what was delivered. A run that leaves nothing under `.autopilot/` did not happen.

## Rationalizations — STOP

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
| «И так понятно, что делать» | Понятно тебе — не зафиксировано. Манифест и спецификация — единственные точки сверки. |
| «Быстрее всё сделать в одном контексте» | Быстрее в первый час. Дальше модель ходит кругами и ломает работавшее. |
| «Задача маленькая, но таски положено делать» | Не положено. Ярус T0 — ноль тасков. Граница таска стоит дороже мелкой работы внутри неё. |
| «Нарежу помельче, так надёжнее» | Каждая лишняя граница — ещё один свежий контекст, который заново въезжает в проект. Дробление покупает не надёжность, а расход. |
| «Бриф краткий — значит, и спецификация краткая» | Бриф — силуэт: пользователь описал happy path и не описал ни пустых состояний, ни ошибок, ни обрывов. На нормальной и максимальной глубине продумать их — твоя работа. |
| «Это и так очевидно, писать не буду» | Очевидное, не записанное в спецификацию, каждый субагент додумает по-своему. Три исполнителя — три разные «очевидности». |
| «Придумал полезную фичу, добавлю» | Углубление заказанного (`R##.n`) — да. Новая возможность (`A`) — только с родительским требованием, в пределах пропорции и в отчёт. На `strict` — нельзя вообще. |
| «Глубина strict — значит, можно не обрабатывать ошибки» | `strict` убирает лишнее, а не обязательное. Падение на неверном вводе не выполняет требование, ради которого писалось. |
| «Глубина deep — можно строить что хочу» | `deep` покупает тщательность, а не другой проект. Родитель и пропорция действуют на всех уровнях. |
| «Полный автомат — значит можно и задеплоить» | Автомат снимает вопросы о продукте, а не право на необратимое. Деплой, оплата, рассылка, удаление — гейт во всех режимах. |
| «В полном автомате можно додумать за пользователя всё» | Решения — да, и все в ASSUMPTIONS. Факты о пользователе (цены, тексты, аккаунты) — нет: заглушка и строка в отчёте. |
| «Напишу "запускаю через 60 секунд"» | Ты не умеешь ждать — обещанной паузы не будет. Честная формулировка: «начинаю, скажи стоп». |
| «В ручном режиме тоже начну и подожду возражений» | В ручном согласование — это явное «ок». Молчание им не является, начатая работа тем более. |
| «Режим не назвали — спрошу, какой» | Не назвали — полуавтомат. Вопрос о режиме сам по себе лишний вопрос. |
| «Сверю результат со спецификацией, этого хватит» | Спецификация может уже потерять требование. Финальная сверка идёт с брифом и без спецификации — иначе она подтвердит собственную ошибку. |
| «Таски и спецификация видны в чате — зачем файлы» | Файл в `.autopilot/` и есть артефакт; чат — только его пересказ. Диалог умрёт, файлы останутся. |
| «Перепишу дашборд целиком, так проще» | Дашборд обновляется заменой одной строки состояния. Перезапись — расход на пустом месте и потеря истории. |
| «Панель сама перезагрузит страницу, как браузер» | Не перезагрузит: внутри встроенной панели `file://` не перечитывается вообще. Поэтому её переоткрывают в двух местах — когда пользователь спросил про прогресс и когда прогон закончился. Не после каждой записи. |
| «Подниму сервер, чтобы дашборд жил в панели» | Дашборд — один статический файл, в этом половина его ценности. Фоновый процесс ради обновления, которое стоит один вызов инструмента, — плохая сделка. |
| «Скажу, где лежит дашборд, — сам откроет» | Не откроет. Файл в скрытой папке, который надо найти, — это не приборная панель. Открывается он один раз, командой, в самом начале. |
| «Проект маленький, тасков не было — заполнять нечего» | Этапы, требования, тесты, коммит и заглушки есть всегда. Дашборд с одним тикающим таймером — это не «нечего показать», это несделанная работа. |
| «Отмечу этапы в конце, разом» | Этапы нужны, пока сборка идёт: «где мы сейчас» на готовом проекте никому не нужно. Метка ставится на входе в фазу, а не по памяти после. |
| «Проставлю время, когда закончу» | Таймер считается из `startedAt`. Не проставил на старте — пользователь смотрел на замерший ноль ровно тогда, когда шла работа. |
| «CLAUDE.md — это уже детали, спрошу пользователя, какой файл создать» | Имя служебного файла — процессное решение, как и всё в Phase 0. Детект отвечает сам, вслух, одной строкой. Слот брифинга стоит вопроса про оплату, а не про расширение файла. |
| «Опишу проект в CLAUDE.md по спецификации — так быстрее» | Спецификация — это план. Память проекта, написанная по плану, врёт ровно там, где сборка отклонилась, и следующая сессия ей верит. Описание пишется по коду. |
| «Допишу в CLAUDE.md заодно пару полезных советов» | Общие советы про тесты и имена переменных верны везде и бесполезны нигде. В файл идёт только то, что выяснилось здесь и стоило времени. |
| «Перепишу CLAUDE.md целиком, там уже каша» | То, что вне маркеров, написал человек. Переписывать это ты не вправе — как и требование из манифеста. |
| «Пользователь не спрашивал про режимы — не буду грузить» | Он и не спросит: в чате нет `--help`. Пять строк в начале — единственное место, где он вообще узнаёт, что у сборки есть ручки. |

## Red Flags — start the phase over

- Writing code before the spec exists.
- The brief was never written to `brief.md` — the run is anchored to nothing.
- A requirement left the manifest without a status, or was marked `dropped` without a quote of the user saying so.
- A ticket that traces to no requirement, or a requirement that traces to no ticket, past gate G3.
- At normal or deep: a spec that restates the brief without deepening it — no empty states, no failures, roughly one story per requirement.
- At strict: an invented capability the brief never asked for, or an `A##` story of any kind.
- The announced depth and the actual spec diverge — every dimension exhaustively covered on strict, or a bare restatement on deep.
- Final acceptance run with the spec in hand instead of blind against the brief.
- Spec or tickets exist only in the dialogue — nothing written under `.autopilot/`.
- `state.json` missing, or stale against what has actually been built.
- The dashboard was never opened — the user was handed a path instead of a window.
- An in-app pane left un-refreshed when the user asked how things stand, or at the end of the run.
- A pane re-opened after every state write — a tool call per ticket for a screen nobody is watching.
- A server started to serve the dashboard.
- A stage list that never moved: everything `pending` while the build is halfway, or `active` on a run that ended.
- A finished run at tier T0 whose dashboard shows only a clock — no stages, no requirement counts, no `singlePass`.
- A ticket running with no `startedAt`, or timestamps written in bulk at the end.
- The run started without the mode-and-depth hint — the user cannot ask for a dial nobody named.
- The run ended without a project memory file, or with one still holding only the Phase 0 skeleton.
- The memory subagent was handed `spec.md` or the tickets — it now documents the plan instead of the code.
- A command or a path in the memory file that was never checked against the repository.
- Text outside the `autopilot` markers edited, moved, or dropped.
- Which memory file to create was asked as a question — in any mode.
- Phase 0 questions leaked to the user (which tracker, which labels, which doc file) — Autopilot answers those itself.
- The announced mode and the actual behaviour diverge: questions in full, a start-and-see instead of «ок» in manual, skipped questions in semi.
- Promising the user a wait — a countdown, «через минуту», «если не ответишь за N секунд» — that you have no way to honour.
- Starting without announcing the mode at all.
- In full: an invented fact about the user standing where an ASSUMPTION, a stub, or a PLACEHOLDER belongs.
- Asking the user to review tickets, granularity, or code (outside manual, where spec and tickets are gates by design).
- Ticket count crossing a tier boundary with no justification line in the spec.
- Two tickets in one subagent context.
- Parallel subagents editing the same files.
- A subagent launched without `interfaces.md`, or finishing without returning the contract block.
- Payment, hosting, or accounts first mentioned at the finish line.
- A secret value asked for, repeated back, or written into any file, prompt, commit, or report.
- Installing a package or fetching remote code without the user asking for it.

**Violating the letter of these rules is violating their spirit.**
