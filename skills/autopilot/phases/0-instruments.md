# Phase 0 — Instruments

The user's live view of the run: `.autopilot/dashboard.html`, a copy of the template, showing `.autopilot/state.js`. **You never edit either by hand.** Every event of the run is one call to `.autopilot/ap.py`, which stamps the time, recounts the requirements from `manifest.md`, closes the stages the run has passed, writes a snapshot of the state into the page and keeps a static server alive for it. This file is read once, in Phase 0; the command table in §4 is what you use for the rest of the run.

## 1. Copy the template and the tool

Runs on every flight — new repo, new feature, resume alike. Every line is idempotent and the copy picks up whatever the installed skill has learned since.

```bash
A=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)/.autopilot
TPL=$(find -L ~/.claude/skills ~/.agents/skills ~/.claude/plugins .claude/skills .agents/skills \
        -maxdepth 6 -name dashboard-template.html 2>/dev/null | head -1)
[ -n "$TPL" ] && TPL=$(cd "$(dirname "$TPL")" && pwd -P)/dashboard-template.html
command -v cygpath >/dev/null && TPL=$(cygpath -m "$TPL")   # Windows: C:/…, а не /c/…
echo "skillDir = ${TPL%/phases/*}"
mkdir -p "$A" && cp "$TPL" "$A/dashboard.html" && ln -sfn dashboard.html "$A/index.html"
cp "${TPL%/phases/*}/tools/ap.py" "$A/ap.py"
```

- **`skillDir` is what every subagent contract hangs on** — `prompts/executor.md` and `prompts/review.md` go down as paths built from it. It goes into `init` below and lives in `state.js`, never only in your context.
- `find -L` and no `*` in it: skills are installed through symlinks, which a plain `find` does not follow, and an unmatched glob aborts the whole line in zsh. Empty output → widen the search once by hand and carry on.
- **`python3` not a working interpreter** — on Windows it can be the Microsoft Store stub → use `python` or `py -3` wherever this skill says `python3`.
- `index.html` is a symlink so the server answers `/` with the dashboard instead of a directory listing.
- Never regenerate the template, never read it into context, never edit it.

## 2. Start the run

```bash
python3 .autopilot/ap.py init --slug telegram-repair-bot --title "Телеграм-бот для заявок на ремонт" \
  --mode semi --depth normal --memory-file AGENTS.md --memory-owner autopilot \
  --skill-dir "<skillDir>" --check-update
```

It creates the run directory `<YYYY-MM-DD>-<slug>--wip/` with `tickets/` inside, writes `state.js` with all eight stages (`preflight` active), adds the run's row to `.autopilot/README.md` (writing the file on a new repo), puts `.autopilot/serve.*` into `.gitignore`, raises the server and prints its address. A finished run's `state.js` is archived into that run's directory first; an unfinished one means this is a resume, and `init` refuses (`phases/0-resume.md`).

A line starting with **`↑`** means a newer Autopilot is out: put it into the opening block as it is — one line, not a question, never an update mid-run.

## 3. Open it once, yourself

Immediately after `init`, before Phase 1 asks anything.

**Path A — the pane beside the chat (preferred), over http.** In Claude Code: `preview_start({url: "http://localhost:PORT"})`, then `navigate` to `/dashboard.html`. A bare `navigate` to localhost without `preview_start` is refused, and so is `127.0.0.1`. Never hand the pane a `file://` path: it loads the page as `data:`, which cannot fetch `state.js` — the snapshot shows, the clocks never move. If `preview_start` is not in your tool list, search for it before concluding there is no pane.

**Say the address in the chat too** — some clients show the pane only as a card with an «Open» button.

**Path B — no pane:** `open`, `xdg-open` or `start` on `.autopilot/dashboard.html`; a real browser polls `state.js` from `file://` by itself.

**No working python at all** means no `ap.py` and no dashboard. Say so in one line, skip the dashboard, keep the manifest's statuses by hand, and check G3 yourself against the ticket files. Everything else in the run is unchanged.

- Opened **once per flight**; on a resume **always re-pointed** — a tab does not outlive its session.
- `$SSH_CONNECTION` or `$CI` set → print the path, open nothing.
- A failure to open is not an error: print the path in one line and carry on.
- The server binds `127.0.0.1` only — it serves the run's own files.
- **«Дашборд отвалился», «подними дашборд»** — the machine slept or the server died. One bare `python3 .autopilot/ap.py`: it raises the server on the same port, and the open tab comes back by itself. Re-point the pane only if the printed address changed. One line in the chat, no investigation.

## 4. One call per event

| Event | Call |
|---|---|
| entering a phase | `stage <id>` — the stage before it closes itself |
| a phase consciously not run | `stage <id> skip --note "причина"` |
| tier decided | `set tier=T2` |
| ticket files written | `tickets` — publishes every ticket; manifest rows `in-spec` → `in-ticket` |
| gate G3 | `check-plan` |
| the plan commit is made | `set baseCommit=<sha>` — chained with it (`phases/4-plan.md`) |
| a ticket or a whole wave launched | `ticket 02 03 start` — **before** the subagents go out |
| a ticket goes to point review | `ticket 02 review` |
| a blocking finding goes back | `ticket 02 repair --note "условие одной строкой"` |
| a failed ticket restarts | `ticket 02 retry` |
| committed | `ticket 02 done --tests 34/0 --commit <sha>` (+ `--placeholder R05` for a stubbed row) — closes the manifest rows whose tickets are all done |
| failed for good | `ticket 02 fail --note "что блокирует"` |
| a deferred finding | `add concerns "файл:строка — что не так"` |
| a stub, an assumption, an empty variable | `add debt.placeholders "…"` · `add debt.assumptions "…"` · `add debt.emptyEnv NAME` |
| an `A##` that reached the code | `add additions "что — ради R01"` |
| a finding for the final report | `add report "…"` |
| G2 result | `coverage found=2 fixed=1 deferred=1 --item "R07 — отложено: …"` |
| blind acceptance | one call: `blind checked=12 matched=11 --mismatch "R07 — статус не виден" --mismatch "…"` |
| a full check outside a ticket | `tests 34/0` |
| the run lands | `finish --result "одна строка: что теперь есть"` |

All are `python3 .autopilot/ap.py …`, and `add` takes several values in one call. **Chain a call with the command it belongs to**, so one event is one turn — the commit of a ticket and its `done` go together (`phases/5-subagents.md`, step 7). Never chain a commit after a check whose result you have not read: `| tail` always exits 0.

- **Two kinds of `!` lines.** From ordinary calls — a stage skipped in the books, a ticket without a start — they are bookkeeping: fixed in the same turn, one call, not investigated. From `check-plan` they are defects of the plan, and gate G3 does not pass until they are gone.
- Manifest rows the tool cannot know — `in-spec`, `deferred`, `dropped`, a new `G##` or `D##` — you edit in `manifest.md` yourself; `in-ticket`, `done` and `placeholder` are the tool's. The counts on the dashboard follow on the next call.
- **Never a secret value** in any call: `emptyEnv` holds names.
- The page repaints every ten seconds, counts working time rather than calendar time, and freezes at `finish`. Mention it **once**, in the opening block, and never explain it in the chat.

After each ticket the user gets one plain line in the chat — what became possible, and the count: «Бот принимает заявки — 3 из 8 готово». No file lists, no ticket numbers.
