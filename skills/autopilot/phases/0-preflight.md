# Phase 0 — Preflight

Configure the repo and raise the instruments. What runs here depends on what is already on disk, and there are exactly three cases. Decide which one you are in **before** doing anything else.

| On disk | Case | What Phase 0 does |
|---|---|---|
| no `.autopilot/` | **new repo** | everything below, in order |
| `.autopilot/state.js` with `finishedAt: null` | **resume** | step 3a only — then *Resuming an interrupted flight* at the end of this file |
| `.autopilot/` exists, last run has `finishedAt` set | **new feature in a configured repo** | steps 1, 3, 3a, 5, 7 only |
| the same, but `updatedAt` is **under five minutes old** and a live server is on this `.autopilot/` | **the run is going on in another window** | none — say so and ask which window carries on |

**The fourth case is not a resume, and it is the expensive one to misread.** Both marks have to be there: a `state.js` written in the last five minutes *and* a server still answering for this directory (the check in `phases/0-instruments.md` §3). One without the other is an ordinary interruption — a session that died three minutes ago is a resume, not a second window, and stopping to ask about it wastes the user's time. Two sessions writing one `state.js` overwrite each other's tickets, and the first one to reach Phase 8 sets `finishedAt`, which freezes the other one's dashboard mid-build. Nothing here is recoverable by being clever: say what you see in one line, ask which window should carry on, and stop until the user answers.

**The third case is the one that gets missed**, and missing it is silent. The repo is configured, so the settings work is done — but this flight still needs its own slug directory, its own dated brief, its own manifest and its own fresh instruments. Reuse the previous run's `state.js` and the user spends this build watching a dashboard that describes a project which already shipped.

In that case: derive a new slug and its dated directory name (step 1) and create it (step 3); **archive the finished run** — move `state.js` into the previous run's directory (`dir` inside it — the name still carries `--wip` if that flight never landed), write a fresh one for this flight and re-open the dashboard (step 3, rules in `phases/0-instruments.md`); top up the memory file rather than rewriting it (step 5); close the stage (step 7). Skip the conventions note and the git setup — they are already there, and `.autopilot/README.md` describes the folder, not the run.

**A second brief landing in an existing run's directory is the one case that runs the rename backwards.** When «доделай ещё вот это» continues the previous flight rather than starting a new one — the same slug, a second dated brief inside the same directory (`phases/1-manifest.md`) — the run is open again, so `git mv` puts `--wip` back and the register's row returns to «в работе». **The date in the name does not move**: it is the day the run was born, not the day it was last touched, and shifting it would reshuffle the very ordering the date exists to give. Update `dir` in `state.js` to the name with the suffix, before anything writes a path from it.

**The order inside that sentence is the whole of it: archive, write, then open.** Opening first shows the user the run that already shipped — eight green stages and last month's project name — and it looks exactly like a dashboard that works, so nobody goes looking. The same trap has a second door: a pane or an HTTP server left over from another flight, possibly in another repository on this machine, that answers on a port this run never started. Both are closed by the checks in `phases/0-instruments.md` §3, and neither is closed by looking at the screen.

**Nothing here is a question for the user.** These are process decisions, not product ones. No mode buys the user a say in where ticket files live; asking about it is exactly the kind of question Autopilot exists to remove.

## 1. Name the flight

Derive a **feature-slug** from the dictated idea — short, kebab-case, latin (`telegram-repair-bot`, `nail-studio-landing`). It names the run for the whole flight and never changes mid-flight.

The directory it lives in carries two things the slug cannot — **when the flight started, and whether it has landed**:

```
.autopilot/2026-07-14-nail-studio-landing/          ← сдан
.autopilot/2026-08-07-telegram-repair-bot--wip/     ← ещё в работе
```

`<YYYY-MM-DD>-<feature-slug>`, the date being the day this flight started — today's, from `date +%F`, never a date carried over from an earlier run. The `--wip` suffix is there from the first minute and comes off in Phase 8, with `git mv`, the moment the run lands (`phases/8-final.md`). The whole scheme is built around the file tree the user actually looks at: the date sorts the runs into the order they happened, and the suffix answers «этот ещё делается или уже сдан» without opening anything.

**Marking the unfinished ones rather than the finished ones is what keeps this cheap.** The landed name is the canonical one, so it is written once and never moves again; exactly one rename ever happens, and it happens while the orchestrator still holds the run. An abandoned flight keeps its `--wip` forever — which is the truth about it, and the fastest way to spot it a month later.

Write the directory name into `state.js` as `dir`, beside `slug`. **Everything that builds a path uses `dir`**; `slug` stays what it always was — the short name of the run, for the dashboard and the report. Do not rebuild the path from `slug` and `startedAt` instead: it gives the wrong answer for the whole life of the run, from the first minute until the suffix comes off.

**Directories from before 2026-08-19 are left exactly as they are.** A run that shipped under a bare slug is referred to by that name in commits, in reports the user has already read, and possibly in their own notes; renaming it retroactively buys a tidy listing and costs every one of those references. New flights get the new name, old ones keep theirs.

## 2. Look before writing

Read what is already here; assume nothing:

- `git rev-parse --git-dir` — is this a repo at all?
- `CLAUDE.md`, `AGENTS.md` at the root — does either exist?
- `.autopilot/` — a previous run? Then this is a **resume**, see below.
- `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` — is there an existing stack to respect?
- `CONTEXT.md`, `docs/adr/` — existing domain vocabulary and decisions. If present, the spec and the tickets must use that vocabulary rather than inventing synonyms, and must flag anything that contradicts a recorded decision instead of silently overriding it.

## 3. Create the flight directory

```
.autopilot/
├── <YYYY-MM-DD>-<feature-slug>--wip/     ← the suffix goes in Phase 8
│   ├── <YYYY-MM-DD>-brief.md
│   ├── manifest.md
│   ├── reference.md        (only if the briefing collects one — `phases/2-briefing.md`)
│   ├── spec.md
│   ├── interfaces.md
│   └── tickets/
├── README.md
├── state.js
├── dashboard.html
└── index.html          → dashboard.html, symlinked so the pane's `/` is the dashboard
```

The brief carries **the date it was dictated in its filename** — `2026-08-07-brief.md` — even though the directory now carries a date too, and the two are not the same date. The directory's is the day the flight started; the brief's is the day *this* brief was dictated. A run directory outlives one conversation: the user comes back a month later with «доделай», a second brief gets appended, and a file called `brief.md` gives no way to tell which sitting is which.

**Then add the run to the register** — one row in `.autopilot/README.md`, under `## Прогоны`:

```markdown
| 2026-08-07 | `2026-08-07-telegram-repair-bot--wip` | в работе | — |
```

Newest at the bottom, so the table reads in the order the runs happened. Phase 8 closes the row (`phases/8-final.md`); until then it says «в работе» and nothing else, because there is nothing true to say yet.

**On a new repo there is no README yet — step 4 writes it, and its template already carries this row.** Append here only when the file exists, which is every flight after the first: that case skips step 4, which *writes* the README, but not this, which *appends* to it — and skipping both is how a configured repo ends up with a register that stopped at the first run. If the file exists but has no `## Прогоны` section (a repo configured before 2026-08-19), add the heading and the table header above the row, and leave the rest of the README untouched.

The register is what the folder itself cannot say. A directory name tells you when a run started and whether it landed; it never tells you what came out of it — and after the dashboard has moved on to the next flight, that row is the only place a finished run says what it delivered.

`state.js` and `dashboard.html` are written now, empty-but-valid, per `phases/0-instruments.md`. The initial `stages` array lists all eight stages — `preflight` as `active`, the rest `pending` — so the dashboard shows the whole road from the first minute instead of a blank page.

## 3a. Raise the instruments

Copy the template, write the starting `state.js`, open the page once. **Read `phases/0-instruments.md`** — it is Phase 0's whole share of the dashboard, including the update ritual you will use for the rest of the run.

Do **not** read `phases/7-instruments.md` here. It answers questions that arrive in Phase 4, and reading it now spends six thousand characters of the one context that is never refreshed.

## 4. Record the conventions

Write `.autopilot/README.md` — a short note for the human, not for the agent:

```markdown
# Как читать эту папку

- `dashboard.html` — открывается сам в начале сборки; можно и двойным кликом.
  Этапы, прогресс, время, что осталось. Обновляется сам, пока сборка идёт.
  `index.html` рядом — тот же файл под другим именем, чтобы дашборд открывался
  по короткому адресу. Отдельно его открывать не нужно.
- `<дата>-<проект>/` — папка одной сборки. Дата в имени — день, когда сборка началась,
  поэтому папки идут по порядку сверху вниз. Суффикс `--wip` значит «ещё делается»;
  когда сборка сдана, суффикс снимается. Внутри:
  - `<дата>-brief.md` — твоя изначальная задача, слово в слово. Не редактируется.
  - `manifest.md` — список требований и что с каждым стало.
  - `spec.md` — спецификация.
  - `tickets/` — таски, на которые разбита сборка (если сборка мелкая, их нет).

Если сборка прервалась — скажи агенту «продолжи автопилот», он поднимет состояние отсюда.

## Прогоны

| Начат | Папка | Статус | Итог |
|---|---|---|---|
| 2026-08-07 | `2026-08-07-telegram-repair-bot--wip` | в работе | — |
```

The register starts with this flight's own row and grows by one row per run. The example line is not an example to copy — it is the row you have just written in step 3, with this run's real date and directory.

## 5. Raise the project memory

The repo needs a file that tells the **next** session what this project is — `CLAUDE.md` or `AGENTS.md`. Which one is decided by detection, never by a question; the skeleton is written now and finished in Phase 8. **Read `phases/0-memory.md`** — the detection table and the skeleton, and nothing else applies until the build is over.

Two things happen here: pick the file, write the skeleton between the `<!-- autopilot:start -->` markers. Announce the choice in one line inside the opening block, together with the mode — and do not wait for a reply.

Record the chosen file in `state.js` as `memoryFile`, and note it in the Phase 8 report. Do **not** read `phases/9-memory.md` here — everything in it belongs to Phase 5 and Phase 8.

## 6. Git

If there is no git repo, `git init` **now**, not in Phase 5 — the first commit must be able to happen the moment the first ticket lands. Write `.gitignore` before anything else is created, with at least:

```
.env
.env.*
!.env.example
node_modules/
__pycache__/
.DS_Store
.autopilot/serve.*
```

`.autopilot/` is **not** ignored. It is the record of what was promised. The one exception is the last line — the running server's pid and log, which describe this machine at this minute and nothing else; §3 of `phases/0-instruments.md` adds it too, so a repo configured before 2026-08-19 gets it on the next flight.

If a repo already exists and its working tree is dirty, say so in one line and continue — do not stash, reset, or clean the user's uncommitted work.

## 7. Close the stage

Leaving any phase means the same two marks, here and everywhere after: the stage you are leaving goes `done` with `finishedAt`, the stage you are entering goes `active` with `startedAt`, `updatedAt` moves, and the dashboard line is replaced. Two edits, per `phases/0-instruments.md`. **A run whose stage list never moves is a run the user cannot see** — and that is the same as no dashboard at all.

## Resuming an interrupted flight

`.autopilot/state.js` exists with `finishedAt` still `null` → this is a resume, not a new flight. (A run that finished is the third case at the top of this file, not this one — and at tier T0 there are no tickets to be unfinished, so `finishedAt` is the only reliable test.)

1. Read the project memory file first (`memoryFile` in `state.js` — `CLAUDE.md` or `AGENTS.md`), then `state.js`, `manifest.md`, `interfaces.md`. Do **not** re-read the whole dialogue; the files are the memory. The brief is `<dir>/*-brief.md` — `dir` from `state.js`, and the newest brief inside it if there is more than one.
2. Tell the user in one line where things stand: «Продолжаю: 7 из 12 тасков готовы, следующий — корзина».
   **Re-open the dashboard — always**, which means running **both** §1 and §3 of `phases/0-instruments.md`, not only the second: §1 is what puts `index.html` beside the dashboard, and a `.autopilot/` created before 2026-08-19 does not have one, so the pane lands on a directory listing exactly as it used to. A tab does not outlive the session that opened it, so on a resume there is never a window to preserve; assuming there is leaves the user watching nothing for the rest of the run. What *is* conditional is the server: the content check in `phases/0-instruments.md` §3 reuses the port when the interrupted session left a server on **this** directory, and raises a new one when it did not. Then point the pane at it and say the address, exactly as on a first flight.
3. A ticket marked `in-progress` in `state.js` with no commit behind it was interrupted mid-flight. Reset it to `pending` and run it again from scratch — a half-applied ticket is worse than a fresh one.
   **Unless its `handoffs` is above zero.** Then the work has a written seam: read `.autopilot/<dir>/handoff-<NN>-*.md`, oldest first, and launch the successor from the last one instead of starting over. That file exists precisely so an interruption costs the current context and not the whole ticket — throwing it away is the most expensive mistake available on a resume, because a relayed ticket is by definition one of the long ones. Check the tree first (`git status`, then the full suite): uncommitted edits from the interrupted context are the successor's starting material, and if the suite is red, say so in the successor's prompt so it does not read the breakage as its own.
4. Re-run the Phase 6 checklist over the whole diff since the last green commit before continuing. Something may have been left broken.
5. Continue from the frontier. Do not redo finished phases; do not re-ask answered questions.
