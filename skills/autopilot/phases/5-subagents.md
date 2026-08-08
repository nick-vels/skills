# Phase 5 — Crew

Where the code gets written. **Identical in all three modes — this phase is always hands-free.** Manual mode buys the user control over *what* gets built, not over each edit; once the tickets are agreed, the crew flies to the end without further approvals.

At tier T0 there are no tickets: you are the crew, working straight from the spec in the current context. Everything below about contracts and returns still applies to you — write `interfaces.md`, run the Phase 6 checklist, commit once.

**T0 does not excuse empty instruments.** Mark the `build` stage `active` before you start and `done` when you finish, record the pass in `state.json` under `singlePass` (files, tests, commit, both timestamps), and update the `requirements` counts exactly as a ticket would. A run that finished the whole project and left the user a dashboard showing nothing but a running clock has failed at the one job the dashboard has. See `phases/7-instruments.md`.

## One ticket, one subagent, one fresh context

Never two tickets in one context. Accumulated context is precisely what makes long vibecoding sessions start breaking things that used to work — the model stops reading and starts remembering, and its memory is worse than the files.

The corollary is that a subagent knows **nothing** except what you hand it. Hand it the right things.

## What a subagent gets

| | |
|---|---|
| `interfaces.md` | what previous tickets actually built — read in full, first |
| its ticket file path and body | including the verbatim brief quotes |
| the spec sections its ticket names | not the whole spec |
| the test command and how to run one file | so it does not have to derive them |
| the working directory and stack constraints | including what it must not touch |
| variable **names** for any credential | never a value, ever |

## interfaces.md — the shared contract

The file that keeps eight independent contexts building one coherent project instead of eight incompatible halves. Without it, ticket 06 invents a second version of what ticket 03 already built, and nobody notices until the end.

Created empty in Phase 0. **You** — the orchestrator — append to it after each ticket returns, from that ticket's contract block. Subagents never write to it: parallel writers would collide, and a subagent cannot know what the others produced.

```markdown
# Что уже построено

Читается каждым исполнителем до начала работы. Не изобретай заново то, что здесь есть.

## Общие правила проекта

- Стек и версии, команды запуска и тестов
- Что менять запрещено (файл конфигурации, схема, общий модуль и его владелец)
- Если не хватает зависимости — не добавляй сам, верни `BLOCKED` с названием

## Из таска 01 — каркас

- `db.connect(path) -> Connection` — единственная точка подключения
- Таблицы `requests`, `clients`; миграции в `migrations/`, владелец — таск 01
- Тесты: `npm test`, один файл — `npm test -- <path>`

## Из таска 02 — приём заявок

- `createRequest({phone, address, problem}) -> {id, createdAt}`
- Валидация телефона — `validatePhone(raw) -> {ok, normalized}`, не пиши свою
```

Keep it to interfaces and rules. It is not a log — the log is `state.json`.

## The return contract

Every subagent ends by returning exactly this. Put it in the prompt as a requirement, not a suggestion: without it you cannot update the instruments or the manifest, and the next ticket flies blind.

```
STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
FILES: созданные и изменённые
TESTS: команда → результат (например, `npm test` → 34 passed)
INTERFACES: публичные сигнатуры, схемы, форматы событий, которые ты выставил
            — то, чем будут пользоваться следующие таски
REQUIREMENTS: R01 done | R01.1 placeholder — <чего не хватило>
CONCERNS: что сделано с оговоркой и почему
BLOCKERS: чего не хватило (зависимость, решение, доступ)
```

`NEEDS_CONTEXT` means the ticket was under-specified — the executor could not tell what was wanted. Treat it as a defect in Phase 4, not in the executor: re-cut the ticket with the missing detail and run it again. Two `NEEDS_CONTEXT` in one flight means the tickets are too thin across the board — go back and merge.

## Order of flight

Work the **frontier**: any ticket whose blockers are all done.

Unblocked tickets may run in parallel **only when they touch disjoint files**. Same files → serialise, no exceptions. Two subagents editing one file overwrite each other and the loss is silent.

Cap parallelism at three. Beyond that the orchestrator's own context fills with returns it cannot usefully hold, and the whole point of the design leaks away.

## Before each ticket

Set the ticket's `status` to `in-progress` and its `startedAt` to now **before** launching the subagent, and mirror it into the dashboard. It costs one edit, and it is the difference between the user watching a ticket run and the user watching nothing happen for eighteen minutes.

## After each ticket

In this order, every time:

1. **Read the contract block.** No block → the ticket is not finished; ask the subagent for it.
2. **Append to `interfaces.md`.**
3. **Update the manifest** — `in-ticket` → `done` or `placeholder`, commit noted.
4. **Run the Phase 6 checklist** over the diff (`phases/6-review.md`).
5. **Run the full test suite**, not just the ticket's own tests. A regression introduced now costs minutes; found eight tickets later it costs the evening. Red → fix before moving on.
6. **Commit** — one commit per ticket, the ticket number in the subject. These are the user's rollback points.
7. **Update the instruments** (`phases/7-instruments.md`) — one line of state, one line of the dashboard: the ticket's `finishedAt`, tests and commit, the `requirements` counts, the `build` and `review` stage notes («3 из 5 тасков готовы»), `updatedAt`.
8. **Top up the project memory — only if something was discovered.** The real test command, a gotcha that cost time, a new variable in `.env.example`. One line appended between the markers, never a rewrite; the architecture is written once, at the end. Most tickets add nothing, and that is the correct rate. Rules in `phases/9-memory.md`.
9. **Tell the user one plain-language line**: «Бот принимает заявки — 3 из 8 готово». No diffs, no jargon, no file lists.

## When a ticket fails

Retry **once**, in a fresh context, with the error attached and the failing test named. A second failure stops the flight: tell the user in plain language what is blocking and what you need from them. Do not improvise around a blocker, and do not silently narrow the ticket to whatever happened to work — a quietly reduced ticket is a lost requirement, and this whole design exists to make that impossible.

Mark it `failed` in `state.json` and `placeholder` in the manifest, with the reason.

## Testing

Test at the seams the spec named, not everywhere. Write the test before the code that satisfies it, one behaviour at a time — test, implementation, next. Tests written in bulk up front verify imagined behaviour and go numb to real changes.

A test asserts through the public interface and stays green through a refactor. If it breaks when the internals move but the behaviour did not, it is testing the wrong thing. And an expected value must come from somewhere other than the code under test — a known-good literal, a worked example, the spec. An assertion that recomputes the answer the way the code does can never disagree with it.
