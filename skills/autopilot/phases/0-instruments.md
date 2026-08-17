# Phase 0 — Raising the instruments

Everything Phase 0 needs to know about the dashboard, and nothing else. **The rest of the instruments — the full `state.js` shape, the stage table, what the dashboard computes — lives in `phases/7-instruments.md` and is read when the tickets are cut.** Reading it now buys nothing and costs the one context that is never refreshed.

Two files, and the split matters:

- **`.autopilot/state.js`** — the truth, and the only thing you ever write. You read it on resume; the user never opens it.
- **`.autopilot/dashboard.html`** — the only human view. Copied from the template once and **never touched again**. No build step, no dependencies, nothing to generate: in a real browser it opens by double-click, and in an in-app pane it needs one static file server and no more (§3).

The page loads `state.js` from beside it and re-loads that file every ten seconds on its own. So there is exactly one place where state lives, one write per update, and nothing that can drift out of sync — because there is no second copy to drift.

## 1. Find the skill directory, copy the template

**The path matters far beyond this copy.** `prompts/executor.md` and `prompts/craft-review.md` go down to every subagent **as paths** (`phases/5-subagents.md`, `phases/6-review.md`), and there is no way to derive one after a compaction. So resolve it once, here, and put it in `state.js` as `skillDir` — the two contracts that decide how the code is written and how it is judged both hang off this one line.

```bash
TPL=$(find -L ~/.claude/skills ~/.agents/skills ~/.claude/plugins .claude/skills .agents/skills \
        -maxdepth 6 -name dashboard-template.html 2>/dev/null | head -1)
cp "$TPL" .autopilot/dashboard.html && echo "skillDir = ${TPL%/phases/*}"
```

**`find -L`, and no `*` anywhere in it** — both parts are load-bearing, and each was measured on 2026-08-17. Skills are installed as symlinks (`~/.claude/skills/autopilot` → `~/.agents/skills/autopilot`), and a plain `find` does not follow one, so it reports nothing while the file sits right there. A `plugins/*/` glob is worse: in zsh an unmatched glob aborts the whole command before it runs, so the search never happens and `skillDir` comes out empty — in bash the same line works, which is exactly what makes it hard to notice.

Empty output means the skill lives somewhere none of those five roots cover: widen the search once, by hand, and carry on. Never regenerate the template, never read it into context, never edit it after the copy.

## 2. Write `.autopilot/state.js`

First line exactly `window.STATE =`, then the state as ordinary indented JSON. Keeping the assignment on its own line is what lets `tail -n +2 .autopilot/state.js | jq .` work, and what makes an edit further down a small edit.

This is the whole file at the moment it is created — copy it and fill in what you know:

```js
window.STATE =
{
  "slug": "telegram-repair-bot",
  "title": "Телеграм-бот для заявок на ремонт",
  "mode": "semi",
  "depth": "normal",
  "polish": null,
  "tier": null,
  "briefFile": "2026-08-07-brief.md",
  "memoryFile": "AGENTS.md",
  "skillDir": "/Users/x/.claude/skills/autopilot",
  "startedAt": "2026-08-07T14:02:06+03:00",
  "updatedAt": "2026-08-07T14:02:06+03:00",
  "finishedAt": null,
  "stages": [
    { "id": "preflight", "status": "active", "startedAt": "2026-08-07T14:02:06+03:00" },
    { "id": "manifest",  "status": "pending" },
    { "id": "briefing",  "status": "pending" },
    { "id": "spec",      "status": "pending" },
    { "id": "plan",      "status": "pending" },
    { "id": "build",     "status": "pending" },
    { "id": "review",    "status": "pending" },
    { "id": "final",     "status": "pending" }
  ],
  "requirements": {
    "total": 0, "done": 0, "inTicket": 0, "inSpec": 0,
    "placeholder": 0, "deferred": 0, "dropped": 0
  },
  "tickets": [],
  "singlePass": null,
  "tests": null,
  "debt": { "placeholders": [], "assumptions": [], "emptyEnv": [] },
  "additions": [],
  "coverage": null,
  "concerns": [],
  "reviewers": { "manifestSpec": null, "craft": null },
  "blind": null
}
```

Three of those fields exist because the orchestrator's context does not survive a compaction and these are the things it cannot rebuild from the repository:

- **`skillDir`** — resolved in §1. Without it the two subagent contracts stop travelling and the run quietly degrades into ordinary vibecoding.
- **`concerns`** — the deferred Craft findings, at the top level and not only inside a ticket: at tier T0 there are no tickets, and the triage in `phases/8-final.md` was the entire justification for deferring them.
- **`reviewers`** — the handles of the two long-lived reviewers (`phases/6-review.md`). Lose them and every ticket gets a fresh reviewer, which is affordable; what is not is that the cross-ticket findings then never happen at all.

**All eight stages are listed from the first minute**, the seven unreached ones as `pending`. That is what makes the dashboard show the whole road instead of a blank page — the template renders every stage it is given and nothing it is not.

`tier` is `null` until Phase 4 decides it. `polish` stays `null` unless the доводка parameter was requested — see `phases/polish.md`, and do not add the block here on speculation.

**Never put a secret value in here.** `emptyEnv` holds names only — the whole point of the list.

**ISO 8601 with the offset**, always: `2026-08-07T14:02:06+03:00`. A bare `14:50` gives an invalid date and a dead dash on the dashboard. Read the clock with `date -Iseconds` at the moment the thing happens — **seconds are part of the answer**, and a column of times all ending in `:00` is the visible tell that they were written from memory.

## 3. Open it once, by you

The user should not have to be told where a file is and then go find it. **Open the dashboard yourself, immediately after the first write**, before Phase 1 asks anything.

**Wherever it opens, it keeps itself fresh** — you never have to refresh it, re-open it or re-point it. The page re-loads `state.js` every ten seconds, and the reason that works everywhere is worth knowing, because the obvious mechanism does not. In-app panes (Claude Desktop, IDE viewers) **silence navigation**: measured, not assumed — `location.reload()` did nothing, and `<meta http-equiv="refresh">` did nothing either. What those panes do *not* touch is sub-resource loading, so the page appends a fresh `<script src="state.js?t=…">` instead of reloading itself. It costs nothing, keeps scroll position intact, and works identically in a real browser.

**Path A — inside the user's own window (preferred), and it goes over http, not `file://`.** If your harness gives you a way to show a local page in the window the user is already looking at — a preview pane, an in-app browser, a webview — **use it**. The whole point of a dashboard is being glanceable without leaving what you are doing; a separate browser window defeats half of that.

**Handing that pane a `file://` path produces a dashboard that never shows anything.** Measured in the Claude pane on 2026-08-13: the pane inlines the HTML into a `data:` URL, and from there `state.js` cannot be reached at all — a relative `src` resolves to nothing, an absolute `file://` one is refused to a `null` origin, and `fetch` is cut by CORS. The user gets the «дашборд ещё не прочитал состояние» screen for the whole run, with a perfectly good state file lying beside it. The same file in Chrome works, which is what makes this look like a broken dashboard instead of a pane.

So serve the directory and point the pane at http — measured on the same day, `window.STATE` loads and the ten-second poll keeps repainting the page:

```bash
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory .autopilot >/dev/null 2>/tmp/autopilot-serve.log &
SRV=$!
curl -sf --retry 5 --retry-delay 1 --retry-connrefused "http://localhost:$PORT/dashboard.html" >/dev/null \
  && printf '%s %s\n' "$PORT" "$SRV" > /tmp/autopilot-serve.pid \
  || echo "сервер не поднялся — иду по Path B"
```

**The `curl` is the whole reason this block is three lines and not two.** The port was free when it was measured and can be taken by the time the server binds it; a sandbox may refuse the socket outright; `python3` may be too old for `--directory`. All three fail the same way — instantly, into `/dev/null` — and without the check the run writes a pid file for a process that is already dead and points the pane at nothing. **Checking is not retrying**: the rule below says do not try a second launcher, and this does not; it says which path you are on. The pid file goes to `/tmp` because `.autopilot/` is committed, and a dead pid in the user's repository is litter with a plausible-looking name. `stderr` goes to a log file rather than to `/dev/null` or to your terminal: `http.server` logs every request, so a run that leaves it attached pays for one line of noise per poll for the rest of the flight, and a run that discards it has nothing to read when the `curl` comes back empty.

Run it **in the background** — a foreground server blocks the whole build. Then open the pane at `http://localhost:$PORT` and go to `/dashboard.html`. In Claude Code that is `preview_start({url: "http://localhost:PORT"})` followed by a `navigate` to `/dashboard.html`: a bare `navigate` to a localhost port **without** `preview_start` first is refused by pane policy, and `127.0.0.1` in the URL is refused where `localhost` is accepted.

**Path B — the system browser.** No in-app viewer, or no `python3` → hand the file to the OS, no server involved:

```bash
open .autopilot/dashboard.html 2>/dev/null \
  || xdg-open .autopilot/dashboard.html 2>/dev/null \
  || start "" .autopilot\dashboard.html 2>/dev/null \
  || echo "открой вручную: .autopilot/dashboard.html"
```

A real browser opens `file://` as a page and lets it load `state.js` from the same directory, so the poll works there without a server. A background tab may be throttled to about one poll per minute — the data lags by a minute at worst, it does not freeze. An IDE is Path B, not Path A: `code file.html` opens the *source* in an editor tab, and rendering it needs an extension this skill does not install on the user's behalf.

**Rules for both paths:**

- **Opened exactly once.** Both paths keep themselves current. Neither ever opens a second window or tab, and neither is ever re-pointed.
- **Never on resume into a window that is already open.** On a resume, open it again only if the previous session ended (`finishedAt` was set). If `/tmp/autopilot-serve.pid` names a live process, reuse that port instead of starting a second server.
- **A failure is not an error.** Headless machine, no default browser, no pane — print the path in one line and carry on. Do not retry, do not install anything, do not try a second launcher.
- **Do not open it in a remote session.** If `$SSH_CONNECTION` or `$CI` is set, skip opening entirely and print the path — a browser window on someone else's machine helps nobody, and neither does a port.
- **One static server, and only for the pane.** `python3 -m http.server` over `.autopilot`, bound to `127.0.0.1` and nothing wider, started once and killed in Phase 8 (`phases/8-final.md`). It serves the run's own directory — briefs, tickets, manifest — so binding it to `0.0.0.0` would publish them to the network. No build step, no bundler, no second file: the dashboard stays one static page that a browser can also open directly.

Say it in one line, once, inside the opening block — Path A names the address, since the user may want it in a real browser too:

> Дашборд открыл — обновляется сам: http://localhost:PORT/dashboard.html

> Дашборд открыл — `.autopilot/dashboard.html`, обновляется сам.

## 4. The update ritual — the same three moves for the rest of the run

This is here rather than in `phases/7-instruments.md` because **you will need it long after that file would have left your context**, and it is the whole of what most updates require:

| When | What |
|---|---|
| entering a phase | that stage → `active` + `startedAt`; the one you left → `done` + `finishedAt` |
| launching a ticket (or a whole wave) | those tickets → `in-progress` + `startedAt` **before** the subagent goes out |
| a ticket returns, review starts | that ticket → `review` |
| a finding goes back for repair | → `repair`, and `repairs` + 1 |
| a ticket is handed off to a fresh context | stays `in-progress`, and `handoffs` + 1 |
| committed | → `done` + `finishedAt` + tests + commit |

Every one of them: **edit the affected rows** of `state.js` and move `updatedAt`. Not a rewrite of the file — roughly thirty tokens, one tool call, and the screen follows within ten seconds wherever it is open. No mirroring, no second file, no re-opening anything.

- **Anchor every edit on the `"id"` line above the field you are changing.** `"status": "pending"` appears once per stage and once per ticket, and at the moment the file is created `updatedAt`, the run's `startedAt` and `stages[0].startedAt` are three identical lines. An edit anchored on the field alone matches the wrong row or refuses to match at all — and `replace_all` here rewrites every ticket in one stroke, so it is never the answer. Not matching means the file moved since you last read it: re-read `state.js` and redo the edit against what is actually there.
- **`startedAt` on a ticket is that ticket's own launch time** — not the run's, not the build stage's. Copying the run's `startedAt` into a ticket is the one mistake that looks harmless and makes every per-ticket duration on the dashboard wrong from the first row.
- **`startedAt` goes in when the thing starts, not when it ends.** An interval with a start and no end is what makes the timer run; filling both in at the end means the user watched a frozen clock while the work was happening.
- **`updatedAt` moves on every write.** The dashboard shows «обновлено N назад» from it and turns the line warning-coloured when the silence runs long — that is the user's only way to tell «идёт работа» from «агент умер». The template knows that a ticket in flight means no writes for tens of minutes and holds the warning back until three quarters of an hour; between tickets it goes back to five. So the warning means what it says, and you do not need to invent keep-alive writes to silence it.
- **Never touch `dashboard.html` after copying it**, and never hand-maintain a progress table in prose.

That is all of Phase 0's business with the instruments. When the tickets are cut, read `phases/7-instruments.md` for the ticket shape and the rest of the reasoning.
