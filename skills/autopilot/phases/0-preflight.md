# Phase 0 — Preflight

Configure the repo, pick the project memory, raise the instruments. Decide which case you are in **before** doing anything else — first match wins:

| On disk | Case | What happens |
|---|---|---|
| `state.js` with `finishedAt: null`, `updatedAt` under five minutes old **and** the server in `.autopilot/serve.pid` answering | **the run is going on in another window** | nothing — say so in one line and ask which window carries on |
| `state.js` with `finishedAt: null` | **resume** | read `phases/0-resume.md` and follow it instead of this file |
| `state.js` with `finishedAt` set | **new feature in a configured repo** | everything below; `init` archives the finished run's state into its own directory |
| no `.autopilot/state.js` | **new run** | everything below, in order |

The first case needs both marks: two sessions writing one `state.js` overwrite each other, and the first to finish freezes the other's dashboard. One mark alone is an ordinary interruption — a resume.

**«Доделай ещё вот это» for a flight that already landed**, continuing it rather than starting a new one: the new brief is a new dated file in the same run directory (`phases/1-manifest.md`), and `python3 .autopilot/ap.py reopen` puts the `--wip` back and reopens the stages from Требования. Phases 1–8 then run for the new brief: its requirements are appended to the manifest with the next free numbers, the spec is amended, new tickets are numbered after the last one — landed tickets stay landed. §5 below runs for it too: small fixes may have landed between the two briefs.

**Nothing here is a question for the user.** Where files live is a process decision.

## 1. Look before writing

- `git rev-parse --git-dir` — is this a repo?
- `CLAUDE.md`, `AGENTS.md` — for `phases/0-memory.md`.
- `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` — an existing stack to respect.
- **Existing code at all** — an existing codebase is explored before the spec (`phases/3-spec.md`).
- `CONTEXT.md`, `GLOSSARY.md`, `docs/adr/` — the project's vocabulary and settled decisions. The spec and tickets speak that vocabulary and flag, not silently override, anything that contradicts a recorded decision.
- `.autopilot/PROGRESS.md` — what the last run left open and what the user settled; §5.

## 2. Git

No repo → `git init` now. Write `.gitignore` before anything else is created, with at least `.env`, `.env.*`, `!.env.example`, `node_modules/`, `__pycache__/`, `.DS_Store`. `.autopilot/` is **committed**, not ignored — it is the user's record of what was promised and delivered; only its `serve.*` files are ignored, and `init` adds that line. The first commit happens at the end of Phase 4 (`phases/4-plan.md`).

**Git must be able to write here, and that is checked now, not at the first ticket:** `git add -- .gitignore`. A refusal — `.git/index.lock: Permission denied`, a sandbox saying no — stops the run before the briefing: `ap.py ask stop --note "git не пишет: <что ответил>"` and one plain sentence to the user. Every rollback point and the blind checker's clean clone depend on commits. Never turn a sandbox off or widen a permission on your own to get past it.

A dirty working tree → say so in one line and continue; never stash, reset or clean the user's work, and never commit it: every commit this skill makes names its paths.

## 3. Project memory

**Read `phases/0-memory.md`**: it picks the file — `AGENTS.md` with a `CLAUDE.md` pointer, or the user's own file, which the run does not write into — and holds the skeleton. Do **not** read `phases/9-memory.md` here.

## 4. Instruments

**Read `phases/0-instruments.md`**: copy the template and `ap.py`, run `init` with the memory choice from §3, open the dashboard. The command table there is the whole of the instruments for the rest of the run.

The **slug** is short, kebab-case, latin (`telegram-repair-bot`) and never changes mid-flight. `init` names the run directory `<YYYY-MM-DD>-<slug>--wip` — the date the flight started, the suffix until it lands — and records it as `dir` in `state.js`. **Every path is built from `dir`**, never rebuilt from the slug.

## 5. What the last run left

Only when a run has landed here before — `PROGRESS.md` exists, or a commit «Autopilot: сборка сдана» does. A first run skips this section.

**Read the progress file whole, then the history since the landing**, the code only, not Autopilot's own files:

```bash
L=$(git log -1 --format=%h --grep='^Autopilot: сборка сдана')
git log --oneline --no-merges "$L"..HEAD -- . ':(exclude).autopilot'
```

Never the whole log — the run needs only what changed after it was last sure of the code. A commit named in «Правки без автопилота» is accounted for; one that is not has a message and `git show --stat <sha>`, nothing more. **Past about thirty commits**, one subagent on the cheaper model reads them and returns ten lines — what changed, where, and anything that reads like a decision — and that list is what you keep.

**Write `.autopilot/<dir>/carried.md`** — the progress file's four sections as they stand, plus «Изменено после сборки»: one line per change from the log. It is this run's copy of what came before: the progress file is rewritten at landing, and your context will not survive the run.

Then it is used, each part once:

| Part | Where it goes |
|---|---|
| Договорились | binds the spec like an ADR — Phase 3 copies it into `interfaces.md` as project rules; a new brief that contradicts it is flagged to the user, not silently obeyed or ignored |
| Не доделано · Известные баги | **offered, never taken by you** — Phase 2 asks in its first round; in full nothing is taken, and the progress file carries them on |
| Изменено после сборки | to the exploring subagent of Phase 3, so `notes.md` describes the code as it is now |

A part with nothing in it is not mentioned.

## 6. Announce and go

The opening block from `phases/0-modes.md` — mode, depth, dashboard address, memory file, and the `↑` line if `init` printed one. After a landed run, one more line from `carried.md`: «С прошлой сборки: 2 пункта не доделано, 1 баг, 3 правки без автопилота — спрошу на брифинге»; in full, «… — в эту сборку не беру, остаются в списке». It is a hint, not a question: say it, then `python3 .autopilot/ap.py stage manifest` and go straight into Phase 1.
