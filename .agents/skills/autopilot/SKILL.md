---
name: autopilot
description: Use when the user dictates an app, site, bot, or feature to build end-to-end and expects a finished result without reviewing specs, tickets, or code — vibecoding sessions, non-technical users, "собери под ключ", "build it for me", "не задавай лишних вопросов" requests. Also use when the user explicitly invokes /autopilot.
---

# Autopilot

## Overview

Autopilot drives a dictated idea through the mattpocock/skills pipeline — grill → spec → tickets → implement — **in one dialogue**, without making the user approve each stage. The user answers questions once at the start and receives a working project at the end. Core principle: **the order is the product** — code is written only in the last phase, and every ticket is implemented by a separate subagent with a fresh, isolated context.

This skill only orchestrates — the phases below **invoke the pipeline skills and follow their rules**; nothing here restates them. What Autopilot adds: which human gates to remove, and how to run implementation hands-free.

**Prerequisite:** the pipeline skills must be installed — `grilling`, `to-spec`, `to-tickets`, `implement` (mattpocock/skills pack). If any is missing, install first:

```bash
npx skills add mattpocock/skills
```

## When to Use

- User dictates what to build and expects the finished thing, not a collaboration on process.
- User is non-technical: will not read specs, judge ticket granularity, or review code.
- "Собери под ключ", "just build it", "не задавай лишних вопросов".

**When NOT to use:** the user wants to co-design step by step (use the underlying skills manually); the task is a small single-file change (just do it); the idea is huge and foggy — bigger than one project, destination unclear (run `/wayfinder` first, then return here).

## The Pipeline

### Phase 1 — Grill (the only human gate)

Run `/grilling` on the dictated idea. Autopilot adds three rules:

- **Blocking unknowns first.** Anything the build depends on but the user hasn't decided (payment provider, hosting, API keys, accounts) goes into the first three questions — never the finish line.
- **Never answer for the user.** No silent assumptions, no fabricated content. Forced to proceed past an unknown → mark it `PLACEHOLDER — уточнить у пользователя`.
- **Cap: 5–8 questions.** Record answers verbatim — Phase 2 synthesizes from this transcript.

### Phase 2 — Spec

Run `/to-spec` on the grilling transcript. No new questions to the user — anything still open becomes a PLACEHOLDER in the spec, not an interview.

### Phase 3 — Tickets

Run `/to-tickets`, with one override: **skip the user quiz** — a vibecoder cannot judge granularity or blocking edges. Validate the breakdown yourself against the skill's own slicing rules, then show the user **one screen of plain-language lines** (what each ticket delivers, no technical detail) with a default: «Запускаю через 60 секунд, если не скажешь стоп». Do not wait for explicit approval — waiting is the failure mode this skill exists to remove.

### Phase 4 — Implement (subagent per ticket)

**One ticket = one subagent = one fresh context.** Each subagent runs `/implement` on a single ticket and gets: the ticket body, the relevant spec sections, and paths to existing code. Never two tickets in one context — context pollution is exactly what breaks naive vibecoding.

- **No git repo yet → `git init` at the start of this phase.** One commit per ticket — commits are the user's rollback points.
- Unblocked tickets may run in parallel **only when they touch disjoint files**; same files → serialize.
- After each ticket, report **one plain-language line** («Можно загрузить клиентов из файла — 3 из 8 готово»). No diffs, no jargon.
- Ticket failed → retry **once** in a fresh context with the error attached. Second failure → stop, tell the user in plain language what is blocking and what you need.

### Phase 5 — Finish

Full test suite once, then a final report in the user's language: what was built and the exact command to run it; what was NOT built (the spec's Out of Scope list); open items — placeholders, keys to add, manual steps left.

## Rationalizations — STOP

| Excuse | Reality |
|--------|---------|
| «Пользователь сказал не задавать вопросов» | Он сказал не задавать ЛИШНИХ. Решающие вопросы — часть работы, не обсуждение процесса. |
| «KISS — просто собери» | Простой результат даёт порядок, а не пропуск этапов. Без спеки каждая правка — «а я имел в виду другое». |
| «Сделаю заглушку, уточнит потом» | Блокирующие неизвестные (оплата, ключи, хостинг) решаются в grilling, до билда. |
| «И так понятно, что делать» | Понятно тебе — не зафиксировано. Спека — единственная точка сверки. |
| «Быстрее всё сделать в одном контексте» | Быстрее в первый час. Дальше модель ходит кругами и ломает работавшее. |

## Red Flags — start the phase over

- Writing code before the spec exists.
- Asking the user to review tickets, granularity, or code.
- Two tickets in one subagent context.
- Parallel subagents editing the same files.
- Silent assumption not marked as PLACEHOLDER.
- Payment/keys/hosting first mentioned at the finish line.

**Violating the letter of these rules is violating their spirit.**
