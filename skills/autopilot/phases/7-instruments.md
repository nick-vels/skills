# Phase 7 — Instruments

The user's live view of the build. Not a phase in sequence — raised in Phase 0, updated after every ticket, read whenever they want to know where things stand.

Two files, and the split matters:

- **`.autopilot/state.json`** — the truth, machine-readable. You read it on resume; the user never opens it.
- **`.autopilot/dashboard.html`** — the only human view. Self-contained, opens by double-click, no server, no build step.

They are separate because on resume you need the state in twenty lines, not buried in two hundred lines of markup. They cannot drift because they are written together, in that order, every time.

## Raising the instruments (Phase 0)

Copy the template — do not regenerate it, do not read it into context:

```bash
cp <skill-dir>/phases/dashboard-template.html .autopilot/dashboard.html
```

Then write `state.json` and mirror it into the dashboard. From then on, updating is two small edits.

## state.json

```json
{
  "slug": "telegram-repair-bot",
  "title": "Телеграм-бот для заявок на ремонт",
  "mode": "semi",
  "depth": "normal",
  "tier": "T2",
  "startedAt": "2026-08-07T14:02:00+03:00",
  "updatedAt": "2026-08-07T15:31:00+03:00",
  "finishedAt": null,
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
`blind` stays `null` until the final phase, then holds the blind-acceptance result.

**Never put a secret value in here.** `emptyEnv` holds names only — the whole point of the list.

## Updating — two edits, not a rewrite

After each ticket:

1. Edit the ticket's object in `state.json` and the `requirements` counts. Change the rows that changed; do not rewrite the file.
2. In `dashboard.html`, replace the single line beginning `const STATE =` with `const STATE = ` + the new JSON + `;`.

That is roughly thirty tokens per ticket. **Never rewrite the dashboard**, and never hand-maintain a progress table in prose: a rewritten table grows quadratically in cost and invites tidying up history that should not be tidied.

## What the dashboard shows

The template computes all of this from `STATE`. You supply the facts; it does the arithmetic.

| Metric | Why it earns its place |
|---|---|
| **Покрытие брифа, %** | *The* completion number. Ticket progress measures effort; brief coverage measures value. They diverge, and when they do, this one is right |
| Задачи готовы, % | familiar progress, honest about effort |
| Прошло времени | fact |
| **Осталось по критическому пути** | remaining time is `median × longest remaining chain of blockers`, **not** the sum of what is left. With parallel waves the sum overstates by two or three times |
| **Долг: заглушки · допущения · пустые переменные** | decides whether the result is *usable*. 100% of tickets with eight placeholders is not a finished project, and this is the number that says so |
| Тесты и их дельта по тикетам | catches a regression at ticket 3 instead of at the end |
| Повторы | a ticket that needed a retry is a signal the cut was wrong, not that luck was bad |
| **Минут на задачу** | over-cutting made visible: a ticket that took forty minutes of context to produce forty lines should not have existed |
| Пересечения по файлам | validates parallel waves — an overlap is visible before it becomes a conflict |
| Расхождения слепой приёмки | at the end: what the manifest calls done and an independent check does not |

## About the estimate

Say what is true: the estimate is the observed median of finished tickets multiplied by the remaining critical path, shown as a range. Agents are bad at predicting wall-clock time up front, and a precise-looking number would be a fabrication. A range built from what actually happened is not.

With fewer than two finished tickets there is no median — the dashboard says «рано считать» rather than guessing.

## The one-line report to the user

After each ticket, in the chat: what became possible, and the count.

> Бот принимает заявки — 3 из 8 готово.

Not: file lists, diffs, test names, ticket IDs. Those are in the instruments, for anyone who wants them.

Mention the dashboard once, when it first has something to show:

> Прогресс видно тут: `.autopilot/dashboard.html` — открой двойным кликом.
