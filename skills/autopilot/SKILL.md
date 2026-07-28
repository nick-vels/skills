---
name: autopilot
description: Use when the user dictates an app, site, bot, or feature to build end-to-end and expects a finished result without reviewing specs, tickets, or code — vibecoding sessions, non-technical users, "собери под ключ", "build it for me", "не задавай лишних вопросов" requests. Also use when the user explicitly invokes /autopilot, optionally with a mode — full ("полный автомат", no questions at all), semi (default, grilling only), manual ("ручной режим", approve spec and tickets by hand).
---

# Autopilot

## Overview

Autopilot drives a dictated idea through the mattpocock/skills pipeline — setup → grill → spec → tickets → implement — **in one dialogue**, without making the user approve each stage. By default the user answers questions once at the start and receives a working project at the end. Core principle: **the order is the product** — code is written only in the last phase, and every ticket is implemented by a separate subagent with a fresh, isolated context.

This skill only orchestrates — the phases below **invoke the pipeline skills and follow their rules**; nothing here restates them. What Autopilot adds: which human gates to remove — the [mode](#modes) decides how many — and how to run implementation hands-free.

**Prerequisite:** the pipeline skills must already be installed — `setup-matt-pocock-skills`, `grilling`, `to-spec`, `to-tickets`, `implement`. If any is missing, **stop and ask the user to install it themselves**; the README lists the command. Never install packages, fetch remote code, or run network commands on the user's behalf.

## Modes

Everything typed after `/autopilot` splits into two parts: **the mode** (optional, a bare word — `full`, `semi`, `manual`, no dashes) and **the brief** (the idea plus any extra instructions). Text that is not a mode trigger is always brief, never a mode.

| Mode | Triggers | Human gates |
|---|---|---|
| **full** — полный автомат | `/autopilot full`, «полный автомат», «полностью сам», «ничего не спрашивай», "fully automatic", "don't ask me anything" | none |
| **semi** — полуавтомат **(default)** | `/autopilot semi`, «полуавтомат», nothing specified | grilling only |
| **manual** — ручной | `/autopilot manual`, «ручной режим», «согласовывай каждый шаг», "ask me everything", "approve every step" | grilling + spec + tickets |

- **Announce the resolved mode in one line before Phase 1** — «Режим: полуавтомат — задам 5–8 вопросов, дальше соберу сам». The user must never discover the mode by noticing questions that did or did not arrive.
- **Ambiguity resolves to semi.** A mode word contradicting the rest of the sentence («ручной режим, но не спрашивай») → the explicit mode word wins; two mode words → ask which one, in one line.
- **The mode can be switched mid-run** («переключись в ручной») — it applies from the next phase onward. Phases already passed are not replayed.
- **Extra instructions in the brief** (stack, language, budget, «без базы данных», deadline) go into the spec verbatim as hard requirements, in every mode. They constrain the build; they never replace a phase.
- **No mode removes the safety gates.** Irreversible or outward-facing actions — deploy, publish, pay, send messages to third parties, delete data, rewrite git history — stay a question in **all three** modes, including full.

## When to Use

- User dictates what to build and expects the finished thing, not a collaboration on process.
- User is non-technical: will not read specs, judge ticket granularity, or review code.
- "Собери под ключ", "just build it", "не задавай лишних вопросов".
- User wants to approve the spec and the tickets but not to run the pipeline by hand — that is **manual** mode, still Autopilot.

**When NOT to use:** the user wants to co-author the code itself, not just approve spec and tickets (use the underlying skills manually); the task is a small single-file change (just do it); the idea is huge and foggy — bigger than one project, destination unclear (run skill `/wayfinder` first, then return here).

## The Pipeline

| Phase | full | semi (default) | manual |
|---|---|---|---|
| 0 Setup | auto — local tracker | auto — local tracker | auto — local tracker |
| 1 Grill | skipped → self-brief | 5–8 questions | questions until clear, no cap |
| 2 Spec | auto | auto | show → wait for explicit «ок» |
| 3 Tickets | auto, notify only | auto, stoppable | quiz on → wait for explicit «ок» |
| 4 Implement | auto | auto | auto |
| 5 Finish | report + Assumptions | report | report |

### Phase 0 — Setup (once per repo, before everything)

Run skill `/setup-matt-pocock-skills` — unless `docs/agents/issue-tracker.md` already exists in the repo, in which case skip this phase entirely: the repo is already configured.

The setup skill is interactive, but Autopilot answers its questions for the user — identically in all three modes. These are process decisions, not product ones; no mode buys the user a say in where ticket files live:

- **Issue tracker → local markdown.** Specs and tickets live as files in the repo under `.scratch/<feature-slug>/` — visible to the user, no GitHub/GitLab account, no network. Record it from the setup skill's `issue-tracker-local.md` template into `docs/agents/issue-tracker.md`.
- **Triage labels → the defaults, unchanged** (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). Asked only when the `triage` skill is installed — answer «yes, keep defaults» and move on.
- **Domain docs → single-context.** One `CONTEXT.md` + `docs/adr/` at the repo root; a fresh vibecoding project is never a monorepo. The setup skill itself says to write this without asking.
- **File to edit → `CLAUDE.md` if it exists, else `AGENTS.md` if it exists, else create `AGENTS.md`.** The setup skill says to ask the user here; Autopilot instead creates `AGENTS.md` and notes the choice in the Phase 5 report.

Derive the **feature-slug** from the dictated idea (short kebab-case) at this point — it names the `.scratch/` directory for the whole run.

### Phase 1 — Grill (the human gate in semi and manual)

Run skill `/grilling` on the dictated idea. Autopilot adds three rules:

- **Blocking unknowns first.** Anything the build depends on but the user hasn't decided (payment provider, hosting, which accounts exist) goes into the first three questions — never the finish line.
- **Decisions, never secrets.** Ask *which* provider and *whether* an account exists. Never ask for a key, token, password, or connection string — see [Secrets](#secrets).
- **Never answer for the user.** No silent assumptions, no fabricated content. Forced to proceed past an unknown → mark it `PLACEHOLDER — уточнить у пользователя`. In **full** the decisions do get made for the user — labelled, never silent; the self-brief below draws the line.
- **Cap: 5–8 questions** — in **manual** the cap is lifted: keep asking until nothing blocking is left. Record the decisions verbatim — Phase 2 synthesizes from this transcript.

**In full mode there is no interview.** Run the same checklist against yourself and write a **self-brief** in place of the transcript — every blocking unknown gets an answer, and the answer is labelled by kind:

- **Decisions are yours to make.** Stack, structure, provider, data model: pick the option that runs on the user's machine **without a third-party account and without money**, and record it as `ASSUMPTION — принято за пользователя: ...`. That list is a required section of the Phase 5 report.
- **Facts about the user are not yours to invent.** Their prices, texts, accounts, business rules — never fabricated. They become `PLACEHOLDER` in the spec, filler content in the code, and a line in the final report.
- **A paid or account-bound service becomes an adapter**, not a guess: one interface, a local stub behind it, the real key an empty variable name in `.env.example`.

### Phase 2 — Spec

Run skill `/to-spec` on the grilling transcript (in full — on the self-brief). No new questions to the user — anything still open becomes a PLACEHOLDER in the spec, not an interview.

**The spec is written to `.scratch/<feature-slug>/spec.md`** — a file in the repo, per the local-tracker convention from Phase 0. What the user sees in the dialogue is a summary; the file is the spec.

**In manual mode the spec is a gate:** show it, stop, wait for an explicit «ок», rewrite on every objection, ask again. Silence is not agreement, and neither is work already started.

### Phase 3 — Tickets

Run skill `/to-tickets`, with one override in **full** and **semi**: **skip the user quiz** — a vibecoder cannot judge granularity or blocking edges. Validate the breakdown yourself against the skill's own slicing rules, then show the user **one screen of plain-language lines** (what each ticket delivers, no technical detail).

**Tickets are published to the local tracker, not left in the dialogue** — one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first), each carrying its `Blocked by:` line and `Status: ready-for-agent`, per the template in `docs/agents/issue-tracker.md`. **A ticket that exists only in the dialogue is not a ticket** — the screen shown to the user is a summary of files already written.

- **semi** — attach a default: «Показываю список и начинаю сборку. Скажи "стоп", если что-то не так». Then start — do not wait for approval, waiting is the failure mode this skill exists to remove. **Never promise a countdown**: you cannot hold a pause, so a stated delay is a promise you will break. The user's window to object is their own reaction, and saying so plainly is the honest version of it.
- **full** — the same screen as a notification, no pause; move straight into Phase 4.
- **manual** — the quiz stays **on**, the screen carries technical detail, and the tickets are a gate: wait for an explicit «ок», adjust boundaries and order on request, ask again. Phase 4 starts only on agreed tickets.

### Phase 4 — Implement (subagent per ticket)

**Identical in all three modes — this phase is always hands-free.** Manual mode buys the user control over *what* gets built, not over each edit; once the tickets are agreed, the subagents run to the end without further approvals.

**One ticket = one subagent = one fresh context.** Each subagent runs skill `/implement` on a single ticket and gets: the ticket **file path** (`.scratch/<feature-slug>/issues/<NN>-<slug>.md`) and body, the relevant spec sections, and paths to existing code. Never two tickets in one context — context pollution is exactly what breaks naive vibecoding.

- **No git repo yet → `git init` at the start of this phase**, and write `.gitignore` with `.env` in it before the first commit. One commit per ticket — commits are the user's rollback points.
- **`PROGRESS.md` is created at the repo root at the start of this phase** — one line per ticket: number, plain-language title, status (`pending` / `in progress` / `done` / `failed`). Update it after every ticket. It is the user's live picture of the build, readable even if the dialogue is lost, and it is what a restarted run resumes from.
- **A finished ticket gets `Status: done` in its `.scratch/` file** (a failed one — `Status: failed` after the retry), so the tracker files always reflect reality.
- A subagent prompt carries the ticket, the spec sections, and file paths — **never a secret value**, only variable names.
- Unblocked tickets may run in parallel **only when they touch disjoint files**; same files → serialize.
- After each ticket, report **one plain-language line** («Можно загрузить клиентов из файла — 3 из 8 готово»). No diffs, no jargon.
- Ticket failed → retry **once** in a fresh context with the error attached. Second failure → stop, tell the user in plain language what is blocking and what you need.

### Phase 5 — Finish

Full test suite once, then a final report in the user's language: what was built and the exact command to run it; what was NOT built (the spec's Out of Scope list); open items — placeholders, environment variables the user still has to fill in (**names only**), manual steps left. The report names the artifacts by path: `.scratch/<feature-slug>/spec.md`, the `.scratch/<feature-slug>/issues/` tickets, and `PROGRESS.md`.

**In full mode the report opens with «Решения, принятые за вас»** — every `ASSUMPTION` from the self-brief, in plain language, each with the one-line reason it was chosen. The user never asked for these; they have the right to see all of them in one place.

## Secrets

Credentials are the user's to hold, not the agent's to handle.

- **Never request one.** No key, token, password, connection string, or card number is ever an interview question — the choice of provider is, the credential is not.
- **Never store one.** If the user volunteers a secret anyway, it does not go into the transcript, the spec, a ticket, a subagent prompt, the code, a commit, or the final report.
- **Refer to it by name.** `STRIPE_SECRET_KEY`, not the value. The user puts the value in `.env` themselves; `.env` stays in `.gitignore`; the final report lists which names are still empty.
- **A leaked secret is a stop condition.** A secret that has already reached a file or a commit is reported to the user immediately, in plain language, with the advice to rotate it.

## Rationalizations — STOP

| Excuse | Reality |
|--------|---------|
| «Пользователь сказал не задавать вопросов» | Он сказал не задавать ЛИШНИХ. Решающие вопросы — часть работы, не обсуждение процесса. |
| «KISS — просто собери» | Простой результат даёт порядок, а не пропуск этапов. Без спеки каждая правка — «а я имел в виду другое». |
| «Сделаю заглушку, уточнит потом» | Блокирующие неизвестные (оплата, хостинг, аккаунты) решаются в grilling — в полном автомате в self-brief, — но всегда до билда. |
| «Пусть пришлёт ключ, я вставлю в код» | Ключи вставляет пользователь и только в `.env`. Ты работаешь с именем переменной. |
| «И так понятно, что делать» | Понятно тебе — не зафиксировано. Спека — единственная точка сверки. |
| «Быстрее всё сделать в одном контексте» | Быстрее в первый час. Дальше модель ходит кругами и ломает работавшее. |
| «Полный автомат — значит можно и задеплоить» | Автомат снимает вопросы о продукте, а не право на необратимое. Деплой, оплата, рассылка, удаление — гейт во всех режимах. |
| «В полном автомате можно додумать за пользователя всё» | Решения — да, и все в ASSUMPTIONS. Факты о пользователе (цены, тексты, аккаунты) — нет: заглушка и строка в отчёте. |
| «Напишу "запускаю через 60 секунд"» | Ты не умеешь ждать — обещанной паузы не будет. Честная формулировка: «начинаю, скажи стоп». |
| «В ручном режиме тоже начну и подожду возражений» | В ручном согласование — это явное «ок». Молчание им не является, начатая работа тем более. |
| «Режим не назвали — спрошу, какой» | Не назвали — полуавтомат. Вопрос о режиме сам по себе лишний вопрос. |
| «Тикеты и спека видны в чате — зачем файлы» | Файл в `.scratch/` и есть тикет; чат — только его пересказ. Диалог умрёт, файлы останутся. |
| «Спрошу, какой трекер настроить» | Вопросы setup-скилла автопилот решает сам: локальный трекер, дефолтные лейблы, single-context. Это про процесс, не про продукт. |

## Red Flags — start the phase over

- Writing code before the spec exists.
- Spec or tickets exist only in the dialogue — nothing written under `.scratch/`.
- `PROGRESS.md` missing, or stale against what has actually been built.
- Phase 0 questions leaked to the user (which tracker, which labels, which doc file) — Autopilot answers those itself.
- The announced mode and the actual behaviour diverge: questions in full, a start-and-see instead of «ок» in manual, a skipped grilling in semi.
- Promising the user a wait — a countdown, «через минуту», «если не ответишь за N секунд» — that you have no way to honour.
- Starting without announcing the mode at all.
- In full: an invented fact about the user standing where an ASSUMPTION, a stub, or a PLACEHOLDER belongs.
- Asking the user to review tickets, granularity, or code (outside manual, where spec and tickets are gates by design).
- Two tickets in one subagent context.
- Parallel subagents editing the same files.
- Silent assumption not marked as PLACEHOLDER — or, in full, as ASSUMPTION in the final report.
- Payment, hosting, or accounts first mentioned at the finish line.
- A secret value asked for, repeated back, or written into any file, prompt, commit, or report.
- Installing a package or fetching remote code instead of asking the user to do it.

**Violating the letter of these rules is violating their spirit.**
