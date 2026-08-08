# Phase 7 — Instruments

The user's live view of the build. Not a phase in sequence — raised in Phase 0, updated at every stage transition and after every ticket, read whenever they want to know where things stand.

Two files, and the split matters:

- **`.autopilot/state.json`** — the truth, machine-readable. You read it on resume; the user never opens it.
- **`.autopilot/dashboard.html`** — the only human view. Self-contained, opens by double-click, no server, no build step.

They are separate because on resume you need the state in twenty lines, not buried in two hundred lines of markup. They cannot drift because they are written together, in that order, every time.

## Raising the instruments (Phase 0)

Copy the template — do not regenerate it, do not read it into context:

```bash
cp <skill-dir>/phases/dashboard-template.html .autopilot/dashboard.html
```

Then write `state.json` and mirror it into the dashboard.

## Opening it — once, by you, at the start

The user should not have to be told where a file is and then go find it. **Open the dashboard yourself, immediately after the first write**, before Phase 1 asks anything.

Where it opens decides how it stays fresh, and the two paths are not interchangeable.

### Path A — inside the user's own window (preferred)

If your harness gives you a way to show a local page in the window the user is already looking at — a preview pane, an in-app browser, a webview — **use it**. The whole point of a dashboard is being glanceable without leaving what you are doing; a separate browser window defeats half of that.

In Claude Desktop that is the browser/preview pane: open it at the dashboard's `file://` path.

**A page opened this way does not refresh itself.** Measured, not assumed: inside the pane a `file://` page runs its JavaScript and its clocks tick, but it never re-reads the file — two minutes with a ten-second timer produced zero reloads, and an explicit `location.reload()` was ignored. Re-pointing the pane at the same path does load the new content.

So the pane shows the numbers as of the moment it was opened, with the clocks running on top of them. **That is not a lie the user can walk into**: the footer says «обновлено N назад» about exactly the data on screen, and turns warning-coloured after five silent minutes.

Do **not** re-point the pane after every state write — that is a tool call per ticket for a picture nobody is looking at most of the time. Refresh it at two moments only:

- **when the user asks where things stand** — «как там?», «покажи прогресс». Refresh first, answer second, so the screen and your sentence agree;
- **once when the run ends**, together with `finishedAt`, so the final numbers are what stays on the screen.

### Path B — the system browser

No in-app viewer → hand it to the OS:

```bash
open .autopilot/dashboard.html 2>/dev/null \
  || xdg-open .autopilot/dashboard.html 2>/dev/null \
  || start "" .autopilot\dashboard.html 2>/dev/null \
  || echo "открой вручную: .autopilot/dashboard.html"
```

Here the page **does** refresh itself every ten seconds until `finishedAt` is set, so you do nothing further. In a real browser a background tab may be throttled to about one refresh per minute — the data lags by a minute at worst, it does not freeze.

An IDE is Path B, not Path A. `code file.html` opens the *source* in an editor tab, and rendering it needs an extension — which this skill does not install on the user's behalf.

### Rules for both paths

- **Opened exactly once.** Path A is refreshed in place at the two moments named above; Path B refreshes itself. Neither ever opens a second window or tab.
- **Never on resume into a window that is already open.** On a resume, open it again only if the previous session ended (`finishedAt` was set).
- **A failure is not an error.** Headless machine, no default browser, no pane — print the path in one line and carry on. Do not retry, do not install anything, do not try a second launcher.
- **Do not open it in a remote session.** If `$SSH_CONNECTION` or `$CI` is set, skip opening entirely and print the path — a browser window on someone else's machine helps nobody.
- **No servers.** The dashboard is one static file, by design. Do not start an HTTP server to serve it, and do not add a build step.

Say it in one line, once:

> Дашборд открыл — `.autopilot/dashboard.html`, обновляется сам.

## state.json

```json
{
  "slug": "telegram-repair-bot",
  "title": "Телеграм-бот для заявок на ремонт",
  "mode": "semi",
  "depth": "normal",
  "tier": "T2",
  "briefFile": "2026-08-07-brief.md",
  "memoryFile": "AGENTS.md",
  "startedAt": "2026-08-07T14:02:00+03:00",
  "updatedAt": "2026-08-07T15:31:00+03:00",
  "finishedAt": null,
  "stages": [
    { "id": "preflight", "status": "done",    "startedAt": "2026-08-07T14:02:00+03:00", "finishedAt": "2026-08-07T14:05:00+03:00" },
    { "id": "manifest",  "status": "done",    "startedAt": "2026-08-07T14:05:00+03:00", "finishedAt": "2026-08-07T14:11:00+03:00" },
    { "id": "briefing",  "status": "done",    "startedAt": "2026-08-07T14:11:00+03:00", "finishedAt": "2026-08-07T14:26:00+03:00", "note": "6 вопросов" },
    { "id": "spec",      "status": "done",    "startedAt": "2026-08-07T14:26:00+03:00", "finishedAt": "2026-08-07T14:44:00+03:00" },
    { "id": "plan",      "status": "done",    "startedAt": "2026-08-07T14:44:00+03:00", "finishedAt": "2026-08-07T14:50:00+03:00", "note": "5 тасков, ярус T2" },
    { "id": "build",     "status": "active",  "startedAt": "2026-08-07T14:50:00+03:00", "note": "3 из 5 тасков готовы" },
    { "id": "review",    "status": "active",  "startedAt": "2026-08-07T15:04:00+03:00", "note": "проверено 3 из 5" },
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
      "status": "done",
      "startedAt": "2026-08-07T14:35:00+03:00",
      "finishedAt": "2026-08-07T14:53:00+03:00",
      "retries": 0,
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
  "blind": null
}
```

Ticket `status`: `pending` · `in-progress` · `done` · `failed`.
`tests` is the last **full** suite run; `blind` stays `null` until the final phase.
`memoryFile` is the project memory chosen in Phase 0 — `CLAUDE.md` or `AGENTS.md`, see `phases/9-memory.md`. A resume reads that file first.

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
- **`build` and `review` may both be `active`.** Reviews run per ticket inside the build, and pretending otherwise would make the timings lie.
- **`skipped` is normal and must be visible.** Briefing in full mode, `plan` at tier T0 — a stage silently left `pending` forever reads as «сборка застряла».

## Timestamps are the clock

Every timer on the dashboard is computed from these fields — total elapsed, per stage, per ticket, all ticking in real time from the marks you wrote. Nothing is stored as a duration.

- **ISO 8601 with the offset** (`2026-08-07T14:50:00+03:00`). A bare `14:50` gives an invalid date and a dead dash on the dashboard.
- **`startedAt` goes in when the thing starts, not when it ends.** An interval with a start and no end is what makes the timer run; filling both in at the end means the user watched a frozen clock while the work was happening.
- **`updatedAt` moves on every write.** The dashboard shows «обновлено N назад» from it and marks it in warning colour after five silent minutes — that is the user's only way to tell «идёт работа» from «агент умер».

## Updating — two edits, not a rewrite

At every stage transition, and after every ticket:

1. Edit the affected rows of `state.json` — the stage object, the ticket object, the `requirements` counts, `updatedAt`. Change the rows that changed; do not rewrite the file.
2. In `dashboard.html`, replace the single line beginning `const STATE =` with `const STATE = ` + the new JSON + `;`.

That is roughly thirty tokens per update. **Never rewrite the dashboard**, and never hand-maintain a progress table in prose: a rewritten table grows quadratically in cost and invites tidying up history that should not be tidied.

Nothing else is needed here. In the system browser the page refreshes itself every ten seconds until `finishedAt` is set, with a toggle in the header to stop it; in an in-app pane it waits for one of the two moments above.

## Tier T0 — the dashboard still has to say something

At T0 there are no tickets by design, and a dashboard that shows only a running clock is the failure this section exists to prevent. **A small build is not an excuse for empty instruments.** Fill in:

- **stages** — `plan` as `skipped` with the reason, everything else with real timestamps. This alone is most of what the user wants to know.
- **`requirements` counts** — updated when the build lands, exactly as they would be after a ticket. This is what makes «покрытие брифа» a number instead of a zero.
- **`singlePass`** — the one build pass, in the shape a ticket would have had:

```json
"singlePass": {
  "startedAt": "2026-08-07T14:26:00+03:00",
  "finishedAt": "2026-08-07T14:40:00+03:00",
  "files": ["index.html", "styles.css", "script.js"],
  "tests": { "passed": 6, "failed": 0 },
  "commit": "9f8e7d6"
}
```

- **`debt`, `additions`, `blind`** — same as any other run. A T0 build has placeholders and assumptions like any other, and they are what the user actually has to act on.

## What the dashboard shows

The template computes all of this from `STATE`. You supply the facts; it does the arithmetic.

| Metric | Why it earns its place |
|---|---|
| **Покрытие брифа, %** | *The* completion number. Ticket progress measures effort; brief coverage measures value. They diverge, and when they do, this one is right |
| **Этап сейчас, N из 8** | where the run is in the cycle, and how long it has been there. The first thing a person looks for and the last thing a ticket count answers |
| **Лента этапов** | the whole cycle at once — what is done, what was skipped and why, what has not started. Works when there are no tickets at all |
| **Прошло времени** | live, to the second, from `startedAt` |
| **Осталось по критическому пути** | remaining time is `median × longest remaining chain of blockers`, **not** the sum of what is left. With parallel waves the sum overstates by two or three times |
| Таски готовы, % | familiar progress, honest about effort. At T0 it says «без разбивки» instead of a fake zero |
| **Долг: заглушки · допущения · пустые переменные** | decides whether the result is *usable*. 100% of tickets with eight placeholders is not a finished project, and this is the number that says so |
| Тесты и их дельта по таскам | catches a regression at ticket 3 instead of at the end |
| Повторы | a ticket that needed a retry is a signal the cut was wrong, not that luck was bad |
| **Время на каждый таск и каждый этап** | over-cutting made visible: a ticket that took forty minutes of context to produce forty lines should not have existed |
| Пересечения по файлам | validates parallel waves — an overlap is visible before it becomes a conflict |
| Расхождения слепой приёмки | at the end: what the manifest calls done and an independent check does not |

## About the estimate

Say what is true: the estimate is the observed median of finished tickets multiplied by the remaining critical path, shown as a range. Agents are bad at predicting wall-clock time up front, and a precise-looking number would be a fabrication. A range built from what actually happened is not.

With fewer than two finished tickets there is no median — the dashboard says «рано считать» rather than guessing.

## The one-line report to the user

After each ticket, in the chat: what became possible, and the count.

> Бот принимает заявки — 3 из 8 готово.

Not: file lists, diffs, test names, ticket IDs. Those are in the instruments, for anyone who wants them.

The dashboard is mentioned **once**, when you open it in Phase 0. After that it speaks for itself.
