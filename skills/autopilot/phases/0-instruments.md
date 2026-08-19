# Phase 0 — Raising the instruments

Everything Phase 0 needs to know about the dashboard, and nothing else. **The rest of the instruments — the full `state.js` shape, the stage table, what the dashboard computes — lives in `phases/7-instruments.md` and is read when the tickets are cut.** Reading it now buys nothing and costs the one context that is never refreshed.

Two files, and the split matters:

- **`.autopilot/state.js`** — the truth, and the only thing you ever write. You read it on resume; the user never opens it.
- **`.autopilot/dashboard.html`** — the only human view. Copied from the template once and **never touched again**. No build step, no dependencies, nothing to generate: in a real browser it opens by double-click, and in an in-app pane it needs one static file server and no more (§3).

The page loads `state.js` from beside it and re-loads that file every ten seconds on its own. So there is exactly one place where state lives, one write per update, and nothing that can drift out of sync — because there is no second copy to drift.

## 1. Find the skill directory, copy the template

**The path matters far beyond this copy.** `prompts/executor.md` and `prompts/craft-review.md` go down to every subagent **as paths** (`phases/5-subagents.md`, `phases/6-review.md`), and there is no way to derive one after a compaction. So resolve it once, here, and put it in `state.js` as `skillDir` — the two contracts that decide how the code is written and how it is judged both hang off this one line.

```bash
A=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)/.autopilot
TPL=$(find -L ~/.claude/skills ~/.agents/skills ~/.claude/plugins .claude/skills .agents/skills \
        -maxdepth 6 -name dashboard-template.html 2>/dev/null | head -1)
[ -n "$TPL" ] && TPL=$(cd "$(dirname "$TPL")" && pwd -P)/dashboard-template.html
echo "skillDir = ${TPL%/phases/*}"
mkdir -p "$A" && cp "$TPL" "$A/dashboard.html" && ln -sfn dashboard.html "$A/index.html"
```

**Every path here is absolute, and the `echo` runs before the copy.** Four ways this used to fail, all measured on 2026-08-19 and all silent: a chained `cp && ln && echo` drops `skillDir` when `ln` refuses; `find` returns a *relative* path when the skill is installed inside the project (`.claude/skills/`), and a relative `skillDir` is one no subagent can open; a run started from a subdirectory built `.autopilot/` in the wrong place; and `cp` onto a directory Phase 0 step 3 had not created yet failed outright. Hence `$A` from the git root, `pwd -P` (which also resolves the symlink skills are installed through), and `mkdir -p`. `ln -sfn`, not `-sf`: on a symlink pointing at a directory BSD `ln` without `-n` writes *inside* it and reports success.

**`find -L`, and no `*` anywhere in it** — both measured on 2026-08-17. Skills are installed as symlinks (`~/.claude/skills/autopilot` → `~/.agents/skills/autopilot`) and a plain `find` will not follow one, so it reports nothing while the file sits right there; a `plugins/*/` glob is worse still, because in zsh an unmatched glob aborts the command before it runs — and the same line works in bash, which is what makes it hard to notice.

Empty output means the skill lives somewhere none of those five roots cover: widen the search once, by hand, and carry on. Never regenerate the template, never read it into context, never edit it after the copy.

**`index.html` is not a second dashboard — it is the name under which the server hands the same file out at `/`.** Without it `python3 -m http.server` answers the directory with a *listing*, and the pane in §3 can only be pointed at an origin, never at a path: one dropped navigation and the user spends the run reading file names (measured 2026-08-18). A symlink, not a copy — a copy is a second dashboard that ages; if `ln` refuses, §3 still navigates to `/dashboard.html`.

**This block runs on every flight that opens the dashboard — new repo, new feature, resume alike.** «Copied once» is about the flight, not the folder: every command here is idempotent, the copy picks up what the skill has learned since, and a `.autopilot/` from before 2026-08-19 has no `index.html` until this line puts one there. The resume that skipped it is exactly how a returning user landed on a directory listing.

## 2. Write `.autopilot/state.js`

First line exactly `window.STATE =`, then the state as ordinary indented JSON. Keeping the assignment on its own line is what lets `tail -n +2 .autopilot/state.js | jq .` work, and what makes an edit further down a small edit.

This is the whole file at the moment it is created — copy it and fill in what you know:

```js
window.STATE =
{
  "slug": "telegram-repair-bot",
  "dir": "2026-08-07-telegram-repair-bot--wip",
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

**`dir` is the run's directory, `slug` is the run's name, and they stopped being the same string.** The directory is `<YYYY-MM-DD>-<slug>--wip` while the flight is in the air and loses the suffix when it lands (`phases/0-preflight.md` step 1, `phases/8-final.md`). Every path goes through `dir`; `slug` is what the dashboard and the report call the run out loud. Rebuilding one from the other is wrong for the whole life of the run — which is exactly when paths are being written.

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

**Wherever it opens, it keeps itself fresh** — you never refresh it or re-open it within a flight. The page appends a new `<script src="state.js?t=…">` every ten seconds rather than reloading itself, because in-app panes silence navigation but not sub-resource loading (measured in the Claude pane 2026-08-13: `location.reload()` and `<meta http-equiv="refresh">` both did nothing). Scroll position survives, and a real browser behaves identically.

**Path A — inside the user's own window (preferred), and it goes over http, not `file://`.** If your harness gives you a way to show a local page in the window the user is already looking at — a preview pane, an in-app browser, a webview — **use it**. The whole point of a dashboard is being glanceable without leaving what you are doing; a separate browser window defeats half of that.

**Handing that pane a `file://` path produces a dashboard that never shows anything.** The pane inlines the HTML into a `data:` URL, and from a `null` origin `state.js` is unreachable by every route — relative `src`, absolute `file://`, `fetch` (measured 2026-08-13). The user stares at «дашборд ещё не прочитал состояние» all run while the state file lies beside it, and the same file opens fine in Chrome — which is what makes it look like a broken dashboard rather than a pane.

So serve the directory and point the pane at http — measured on the same day, `window.STATE` loads and the ten-second poll keeps repainting the page:

```bash
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P); A=$ROOT/.autopilot
G=$ROOT/.gitignore
git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 && ! grep -qs '^\.autopilot/serve\.' "$G" && {
  [ -s "$G" ] && [ -n "$(tail -c1 "$G")" ] && printf '\n' >> "$G"   # файл без \n в конце склеит строки
  printf '.autopilot/serve.*\n' >> "$G"
}
mine()    { ps -p "${1:-0}" -o command= 2>/dev/null | grep -qi -- 'python.* -m http\.server'; }
serving() { ps -Ao pid=,command= | grep -F -- "--directory $1" | awk '{print $1}'; }

PORT= PID=; [ -f "$A/serve.pid" ] && read -r PORT PID < "$A/serve.pid"
curl -sf --noproxy '*' "http://localhost:${PORT:-0}/state.js" | cmp -s - "$A/state.js" || {
  for X in $PID $(serving "$A"); do mine "$X" && kill "$X"; done
  for X in $(serving .autopilot); do        # серверы версий до 2026-08-19: путь у них относительный
    [ "$(lsof -a -p "$X" -d cwd -Fn 2>/dev/null | tail -1)" = "n$ROOT" ] && mine "$X" && kill "$X"
  done
  PORT=                               # прежние серверы этого каталога — иначе они остаются без хозяина
}
if [ -z "$PORT" ]; then
  PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
  python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$A" >/dev/null 2>"$A/serve.log" &
  SRV=$!
  curl -sf --noproxy '*' --retry 5 --retry-delay 1 --retry-connrefused "http://localhost:$PORT/dashboard.html" >/dev/null \
    && printf '%s %s\n' "$PORT" "$SRV" > "$A/serve.pid" \
    || { kill "$SRV" 2>/dev/null; PORT=; echo "сервер не поднялся — иду по Path B"; }
fi
```

**Everything above the `if` answers one question: is a server already up, and is it serving *this* run?** It used to be assumed, and the assumption cost a whole flight — a machine-wide `/tmp/autopilot-serve.pid` handed the second project the first one's port, and the user watched somebody else's build to the end (2026-08-18). Hence a pid file beside the run it describes, addressed from the git root so a phase started in a subdirectory finds this run and not a new one, and an answer taken from **content**: what the server hands out, against the `state.js` §2 has already written. A pid outlives its port and a port can be taken by anyone — a file proves neither.

**What the check rejects, it kills, and it hunts by directory.** A mangled pid file names nobody, and a session that raised two servers recorded only the last; both leave processes nothing references, because the file is about to be overwritten. So `serving` looks for the `--directory` argument itself — `$A` in full for this run, plus one pass for the relative form used before 2026-08-19, narrowed by working directory so it only ever takes this project's — and it greps `-F`, since a path with `+`, `[` or `(` makes a regex search answer nothing. Nothing is killed unidentified: `mine` matches `python… -m http.server`, because the loose form also catches npm's `http-server` and even the `grep` of `serving` itself, and killing a user's dev server is worse than the bug being fixed. Skip all this and the machine collects forgotten servers — five of them by 2026-08-19.

**The second `curl` is why the launch is four lines and not two.** The port can be taken between measuring and binding it, a sandbox may refuse the socket, `python3` may be too old for `--directory` — all fail instantly and silently, leaving a recorded pid for a dead process and a pane pointed at nothing. **Checking is not retrying**: it says which path you are on. The failure branch kills what it started and clears `PORT`, since the alternative is an unreferenced server plus an address serving nobody. `--noproxy '*'` stops a proxy-configured environment from failing the check on a healthy server; `serve.log` holds the request-per-poll noise, so there is something to read when `curl` comes back empty.

Run it **in the background** — a foreground server blocks the whole build. Then open the pane at `http://localhost:$PORT` and go to `/dashboard.html`. In Claude Code that is `preview_start({url: "http://localhost:PORT"})` followed by a `navigate` to `/dashboard.html`: a bare `navigate` to a localhost port **without** `preview_start` first is refused by pane policy, and `127.0.0.1` in the URL is refused where `localhost` is accepted.

**The `navigate` is the second half of one move.** The pane must end on `/dashboard.html` — that is the address the user copies out of it. **Always re-point it**, on a resume and on a second flight in the same repo too: a pane left over shows the old flight, and on a re-used port the page it holds has already stopped polling (`finishedAt` freezes it — `phases/8-final.md`), so a live server sits behind a screen full of green. Then glance at what it shows — a stage list and a running clock, not a file listing and not another project's title.

**If `preview_start` is not in your tool list, look for it before concluding there is no pane** — in some sessions the browser tools load on demand, and «no viewer here» sends a run to Path B on a machine that had one.

**Say the address in the chat as well, on Path A too.** How the client presents the pane varies — sometimes it opens beside the chat, sometimes the same call comes back as a card with an «Open» button and nothing on screen until it is pressed (seen in Claude Desktop on 2026-08-19). You cannot tell which from the tool's own answer, and it is not worth a second call to find out: one printed line covers both, keeps the user independent of a button, and lets them keep the dashboard in a real browser window beside the chat.

**Path B — the system browser.** No in-app viewer, or no `python3` → hand the file to the OS, no server involved:

```bash
A=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)/.autopilot
open "$A/dashboard.html" 2>/dev/null \
  || xdg-open "$A/dashboard.html" 2>/dev/null \
  || start "" "$A\dashboard.html" 2>/dev/null \
  || echo "открой вручную: $A/dashboard.html"
```

A real browser opens `file://` as a page and lets it load `state.js` from the same directory, so the poll works there without a server. A background tab may be throttled to about one poll per minute — the data lags by a minute at worst, it does not freeze. An IDE is Path B, not Path A: `code file.html` opens the *source* in an editor tab, and rendering it needs an extension this skill does not install on the user's behalf.

**Rules for both paths:**

- **Opened exactly once per flight.** Both paths keep themselves current. Within one flight neither ever opens a second window or tab.
- **A new feature in a configured repo is a new flight** (`phases/0-preflight.md`, third case): archive, write the fresh `state.js`, *then* open. Reversed, the user is shown the run that already shipped — all green, last project's title — and nothing on screen says otherwise.
- **On a resume the pane is always re-pointed; only the *server* is conditionally reused.** The two used to be one rule, which read as «do not open it again if a window is already open» — never true on a resume, since a tab does not outlive its session, and the returning user got no dashboard at all. Run §1, run the block above, then `preview_start` + `navigate` exactly as on a first flight.
- **A live server here plus a `state.js` written in the last five minutes is the run going on in another window** — `phases/0-preflight.md`, fourth case. Say what you see and ask which window carries on; one mark without the other is an ordinary resume.
- **A failure is not an error.** Headless machine, no default browser, no pane — print the path in one line and carry on. Do not retry, do not install anything, do not try a second launcher.
- **Do not open it in a remote session.** If `$SSH_CONNECTION` or `$CI` is set, skip opening entirely and print the path — a browser window on someone else's machine helps nobody, and neither does a port.
- **One static server, and only for the pane.** `python3 -m http.server` over `.autopilot`, bound to `127.0.0.1` and nothing wider, started once and killed in Phase 8 (`phases/8-final.md`). It serves the run's own directory — briefs, tickets, manifest — so binding it to `0.0.0.0` would publish them to the network. No build step, no bundler, no second page to maintain — `index.html` is a symlink onto the same file: the dashboard stays one static page that a browser can also open directly.

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
- **The clocks subtract idle time by themselves.** A gap between marks longer than 45 minutes is counted as 45 and no more, so a night or a weekend away does not inflate the run's hours; the header shows working time with the calendar figure under it. You write nothing extra for this, you correct nothing, and you never explain the difference in the chat — see `phases/7-instruments.md`.
- **Never touch `dashboard.html` after copying it**, and never hand-maintain a progress table in prose.

That is all of Phase 0's business with the instruments. When the tickets are cut, read `phases/7-instruments.md` for the ticket shape and the rest of the reasoning.
