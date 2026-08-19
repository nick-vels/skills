# Phase 7 — Instruments

The user's live view of the build. Not a phase in sequence — raised in Phase 0, updated at every stage transition and after every ticket, read whenever they want to know where things stand.

**Phase 0's share of this file is not here — it is `phases/0-instruments.md`**: copying the template, the state at the moment it is created, opening the page, and the update ritual that carries the rest of the run. This file is read **when the tickets are cut in Phase 4**, and afterwards only when a detail is actually needed. Reading it in Phase 0 costs six thousand characters in the one context that is never refreshed, to answer questions that arrive four phases later.

The split is the one Phase 0 set up: `state.js` is the truth and the only thing you write by hand, `dashboard.html` was copied from the template and is never hand-edited (Phase 0 re-copies it on a later flight, which is not the same thing), and the page re-reads `state.js` by itself every ten seconds. The page also carries a snapshot of the state inside it, written by `python3 .autopilot/sync.py` after each update — that is what the dashboard shows when it is opened with no server behind it.

## state.js — the full shape

One assignment, then plain JSON. The first line is `window.STATE =` and nothing else — keeping it on its own line is what lets `tail -n +2 .autopilot/state.js | jq .` work, and what makes an edit further down a small edit. Indent the JSON normally; it is its own file now, so there is no reason to minify it.

This is the file mid-build, with everything filled in. The starting shape — what Phase 0 writes — is in `phases/0-instruments.md`.

```js
window.STATE =
{
  "slug": "telegram-repair-bot",
  "dir": "2026-08-07-telegram-repair-bot--wip",
  "title": "Телеграм-бот для заявок на ремонт",
  "mode": "semi",
  "depth": "normal",
  "tier": "T2",
  "briefFile": "2026-08-07-brief.md",
  "memoryFile": "AGENTS.md",
  "skillDir": "/Users/x/.claude/skills/autopilot",
  "startedAt": "2026-08-07T14:02:06+03:00",
  "updatedAt": "2026-08-07T15:31:43+03:00",
  "finishedAt": null,
  "stages": [
    { "id": "preflight", "status": "done",    "startedAt": "2026-08-07T14:02:06+03:00", "finishedAt": "2026-08-07T14:05:28+03:00" },
    { "id": "manifest",  "status": "done",    "startedAt": "2026-08-07T14:05:28+03:00", "finishedAt": "2026-08-07T14:11:09+03:00" },
    { "id": "briefing",  "status": "done",    "startedAt": "2026-08-07T14:11:09+03:00", "finishedAt": "2026-08-07T14:26:22+03:00", "note": "6 вопросов" },
    { "id": "spec",      "status": "done",    "startedAt": "2026-08-07T14:26:22+03:00", "finishedAt": "2026-08-07T14:44:13+03:00" },
    { "id": "plan",      "status": "done",    "startedAt": "2026-08-07T14:44:13+03:00", "finishedAt": "2026-08-07T14:50:38+03:00", "note": "5 тасков, ярус T2" },
    { "id": "build",     "status": "active",  "startedAt": "2026-08-07T14:50:38+03:00", "note": "3 из 5 тасков готовы" },
    { "id": "review",    "status": "active",  "startedAt": "2026-08-07T15:04:04+03:00", "note": "проверено 3 из 5" },
    { "id": "final",     "status": "pending" }
  ],
  "requirements": {
    "total": 23, "done": 9, "inTicket": 8, "inSpec": 0,
    "placeholder": 2, "deferred": 1, "dropped": 3
  },
  "tickets": [
    {
      "id": "03",
      "title": "Приём заявки от клиента",
      "requirements": ["R01", "R01.1", "A01"],
      "blockedBy": ["01", "02"],
      "wave": 2,
      "zone": ["src/bot/"],
      "status": "done",
      "startedAt": "2026-08-07T14:35:31+03:00",
      "finishedAt": "2026-08-07T14:53:26+03:00",
      "retries": 0,
      "repairs": 1,
      "repairFindings": ["пустой адрес проходит валидацию — R01.1"],
      "handoffs": 0,
      "files": ["src/bot/intake.ts", "src/bot/validate.ts"],
      "tests": { "passed": 34, "failed": 0 },
      "commit": "a1b2c3d",
      "concerns": []
    }
  ],
  "singlePass": null,
  "tests": { "passed": 34, "failed": 0 },
  "debt": {
    "placeholders": ["R05 — фирменные цвета", "R11 — тексты писем"],
    "assumptions": ["SQLite вместо Postgres — не нужен сервер"],
    "emptyEnv": ["TELEGRAM_BOT_TOKEN", "GOOGLE_SHEETS_ID"]
  },
  "additions": ["Номер заявки в подтверждении — ради R01"],
  "coverage": { "found": 2, "fixed": 2, "deferred": 0 },
  "concerns": ["src/notify.ts:40 — два формата даты в одном модуле"],
  "reviewers": { "manifestSpec": "rev-ms-1", "craft": "rev-craft-1" },
  "blind": null,
  "polish": null
}
```

Ticket `status`: `pending` · `in-progress` · `review` · `repair` · `done` · `failed`.

**Three of those are «идёт прямо сейчас», and the dashboard shows them apart.** A ticket is written, then checked, then sometimes repaired — and since review and repair run while the next ticket is already flying (`phases/5-subagents.md`), collapsing them into one state is what makes the screen answer «готово 2 из 6» while four tickets are in motion. `done` now means one thing only: reviewed, green, committed.

`repairs` counts the дозапросы this ticket needed, the way `retries` counts restarts. Two is the ceiling by rule, and a ticket carrying two is a signal about the cut, not about the executor. `repairFindings` holds what each one was **for**, one line apiece: a repair condition exists nowhere else on disk, so a ticket that gets handed off mid-repair loses the finding while the counter that paid for it stays spent (`phases/5-subagents.md`).

`concerns` at the top level is the deferred Craft findings — the list `phases/8-final.md` triages once, and the reason the loosening in `phases/6-review.md` was affordable. It sits beside the tickets rather than inside them because tier T0 has no tickets and defers findings all the same. `reviewers` holds the two long-lived reviewers' handles (`phases/6-review.md`), and `skillDir` the path the subagent contracts travel by (`phases/0-instruments.md`) — both are things the orchestrator cannot rebuild from the repository after a compaction, which is the only reason they are written down at all.

`handoffs` counts the times the ticket outgrew a context and was relayed to a fresh one (`phases/5-subagents.md`). **It is not a defect count and must not be shown as one** — nothing was found wrong; the ticket was long. The status stays `in-progress` across a handoff, so the user sees one ticket still being written rather than a ticket that failed and restarted. Two is the ceiling here as well, and a ticket carrying two says the same thing `repairs` does: the cut was too coarse.

`finishedAt` goes in at the commit, not at the subagent's return — so the ticket's clock covers everything the ticket cost, review and repair included. A ticket that «finished» in four minutes and then sat in review for twenty did not take four minutes.
`mode`: `full` · `semi` · `interview` · `manual`. `depth`: `strict` · `normal` · `deep`.
`wave` and `zone` come from Phase 4 — the wave decides what flies together, the zone is why it may.
`tests` is the last **full** suite run; `blind` stays `null` until the final phase.
`coverage` is the independent check at gate G2 (`phases/3-spec.md`) — written once, when the spec is done, and read again by the Phase 8 report. `null` means the check has not run yet, **not** that it found nothing: a run that reaches the build with `coverage: null` skipped a gate.
`memoryFile` is the project memory chosen in Phase 0 — `CLAUDE.md` or `AGENTS.md`, see `phases/0-memory.md`. A resume reads that file first.
`polish` stays `null` on every run without the доводка parameter, which is most of them. Its shape and its `P`-prefixed tickets are in `phases/polish.md`.

**Never put a secret value in here.** `emptyEnv` holds names only — the whole point of the list.

## Stages — the answer to «где мы сейчас»

Eight ids, fixed, in this order: `preflight` · `manifest` · `briefing` · `spec` · `plan` · `build` · `review` · `final`. The dashboard knows them all and shows the ones you did not write as `pending`, so the user sees the whole road from the first minute, not just the piece already travelled.

| Stage status | When |
|---|---|
| `pending` | not reached yet — the default, no timestamps |
| `active` | entered: set `startedAt` **when you enter the phase**, not when you finish it |
| `done` | left: set `finishedAt` |
| `skipped` | consciously not run — **always with a `note` saying why** |
| `failed` | the phase stopped on a blocker the user has to resolve |

- **`note` is one short human phrase**, not a log line: «6 вопросов», «ярус T0 — без разбивки на таски», «полный автомат — самобрифинг», «проверено 3 из 5».
- **`build` and `review` may both be `active`.** Reviews run per ticket inside the build, and pretending otherwise would make the timings lie. This is also the one exception to the closing rule below.
- **You open stages; `sync.py` closes them.** Nothing earlier than the active stage stays `active`: the one you left is set to `done` at the moment the next one opened. Write `startedAt` on entry and nothing else — no `finishedAt` on the stage you are leaving, no second edit, no cleanup pass later.
- **`skipped` is normal and must be visible.** Briefing in full mode, `plan` at tier T0 — a stage silently left `pending` forever reads as «сборка застряла».

## Tickets appear when they are cut, not when they start

**The whole ticket array is written at the end of Phase 4**, every ticket `pending`, with its `blockedBy`, `wave` and `zone`. Everything the dashboard says about the build reads from that array, and an array that is still empty makes the dashboard state three things that are all false at once:

- «таски ещё не нарезаны» on the Таски card, with no count — while the tickets are on disk and the build is running;
- no «Ход сборки» block at all — the block only exists when there are tickets, so the one screen that answers «на каком этапе разработка» is missing exactly during the build;
- a progress bar that cannot move with the work, because the share of finished tickets is `0 / 0`.

None of that is a template bug — the dashboard shows what it was given. Publish the tickets when they are cut, then edit their rows as they run: `in-progress` + `startedAt` before the launch, `done` + `finishedAt` + tests + commit when the ticket returns.

## What «ход сборки» needs to be honest

The build block earns its place only if the rows are true at a glance, which takes three fields and no more:

- **`status`** — a filled bar is a ticket that has started, coloured by status: green done, amber being written, blue in review, purple in repair, red failed, dashed outline for what has not begun. Review and repair also carry the phase as a word on the bar — the colour says a ticket is not ordinary work, the word says which kind. A ticket left `pending` while its subagent is flying shows as «не начат» and makes the screen a lie — and a ticket left `in-progress` through its whole review does the same thing more quietly.
- **`startedAt` at launch, `finishedAt` at return** — that is where every per-ticket duration comes from, live for the running ones. The header line («Сейчас: 04 …») is built from the same marks.
- **`wave`** — rows group by wave, and a wave with more than one ticket is labelled «2 таска параллельно». This is the user's only view of parallelism actually happening.

## The numbers are computed, not written

Every percentage and every clock is derived from the fields above: nothing is stored as a duration and there is no metric here for you to calculate. Two consequences are worth holding on to — **a stalled progress bar means a stage nobody marked**, not a build that is stuck; and «прогресс» and «покрытие брифа» are different numbers on purpose, one measuring the road travelled and the other the value delivered.

## Updating — two failure modes

The ritual itself is in `phases/0-instruments.md`. What belongs here is what to do when the page disagrees with you — neither of these loses a run:

- **The page says «дашборд ещё не прочитал состояние».** Neither the snapshot nor `state.js` gave it anything — on a live run that means Phase 0 has not written the state yet, and the page will fill itself in on its own. Mid-build it means the file got mangled *and* was never synced: rewrite `state.js` whole from what you know and run `sync.py`, which says on the spot whether it parses. You will normally hear about a mangled file from `sync.py` long before the page can show this.

- **The page shows data but the clock is not moving.** The state it is showing came from the snapshot: no server behind the page, or it was opened as a file. Nothing is broken and nothing is lost — the next `sync.py` puts the server back on its old address, and the numbers were true as of `updatedAt`, which the page states out loud.
- **A write caught mid-flight.** If the poll reads the file while you are writing it, the load simply fails and the last good state stays on screen until the next poll ten seconds later. Nothing to handle, nothing to announce.

## Tier T0 — the dashboard still has to say something

At T0 there are no tickets by design, and a dashboard that shows only a running clock is the failure this section exists to prevent. **A small build is not an excuse for empty instruments.** Fill in:

- **stages** — `plan` as `skipped` with the reason, everything else with real timestamps. This alone is most of what the user wants to know.
- **`requirements` counts** — updated when the build lands, exactly as they would be after a ticket. This is what makes «покрытие брифа» a number instead of a zero.
- **`singlePass`** — the one build pass, in the shape a ticket would have had:

```json
"singlePass": {
  "startedAt": "2026-08-07T14:26:43+03:00",
  "finishedAt": "2026-08-07T14:40:06+03:00",
  "files": ["index.html", "styles.css", "script.js"],
  "tests": { "passed": 6, "failed": 0 },
  "commit": "9f8e7d6"
}
```

- **`debt`, `additions`, `blind`** — same as any other run. A T0 build has placeholders and assumptions like any other, and they are what the user actually has to act on.

## What the dashboard shows

Everything, from `STATE`: progress and brief coverage, the stage strip, live clocks per stage and per ticket, waves and their width, the debt, the retries and repairs, the chips for «пишутся · на ревью · в ремонте». You supply the facts and it does the arithmetic — there is no metric here for you to compute, and none worth repeating in the chat.

**The clocks show working time, not the calendar, and this costs you nothing.** A run that a person left for a day should not report a day of work. The page has no need of extra records to know that: `state.js` is full of timestamps — the run's start, every stage, every ticket, `updatedAt` — and a gap between two of them longer than **45 minutes** is a person being away, not the build being slow. Each gap is counted up to that ceiling and no further, so an overnight pause adds 45 minutes and a two-day one adds the same. Measured on the runs of 2026-08-19: working intervals between marks fit inside an hour, real pauses ran 444, 4207 and 7814 minutes, so the crude ceiling lands within about a tenth of the truth. The same subtraction applies to each ticket's duration, hence to the median and the estimate. The header carries both numbers — «в работе 6:01», and under it «календарных 10:22» — and while the clock is stopped it says so, so a frozen timer never reads as a broken page.

Nothing about this is your job: **do not adjust timestamps, do not record pauses, do not explain the difference in the chat.** Write the marks you already write. (If a run ever wants exact accounting, the page also reads an optional `beats` array — a list of ISO stamps — and the page itself remembers every `updatedAt` it has seen, which is what keeps the counter from stepping backwards when you return from a pause.)

One number is worth knowing, because it is the one you might be tempted to improve on: **«осталось» is the median of finished tickets times the remaining critical path, shown as a range**, and below two finished tickets it says «рано считать» instead of guessing. Do not offer the user a sharper number than the dashboard's. A precise-looking wall-clock prediction is a fabrication; a range built from what already happened is not.

## The one-line report to the user

After each ticket, in the chat: what became possible, and the count.

> Бот принимает заявки — 3 из 8 готово.

Not: file lists, diffs, test names, ticket IDs. Those are in the instruments, for anyone who wants them.

The dashboard is mentioned **once**, when you open it in Phase 0. After that it speaks for itself.
