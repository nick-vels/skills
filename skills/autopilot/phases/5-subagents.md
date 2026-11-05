# Phase 5 — Build

`ap.py stage build`. Where the code gets written. **Identical in all four modes, and hands-free**: manual buys control over *what* gets built, not over each edit.

## One ticket, one subagent, one fresh context

Never two tickets in one context — accumulated context is what makes long sessions start breaking what used to work. At T0 the one ticket goes to one executor like any other.

**You dispatch; you do not build.** Your keyboard reaches `.autopilot/**`, the memory files, `.gitignore`, `.env.example`, and git (`add`, `commit`, `status`, `--stat` — never the diff). Every other file is written by someone whose context dies with the ticket. This is rule 5, and it loses to the two arguments that always arrive — «тут две строки» and «исполнитель не смог, доделаю сам»: a diff you read at ticket 02 is still in your context at ticket 08, and your context is the one that is never refreshed.

## What an executor gets — paths, not contents

| | |
|---|---|
| `prompts/executor.md` | by path (`skillDir` in `state.js`), **required reading before the first edit** — the testing contract, what is never allowed, the return format |
| its ticket | by path; it already carries the verbatim brief quotes |
| the spec sections the ticket names | `spec.md` by path **and section headings** — not the whole spec, not pasted |
| `interfaces.md` | by path, read first |
| `notes.md` | by path, in an existing codebase |
| `reference.md` | by path, when the ticket builds something the user will look at |
| the check command and how to run one test file | from `interfaces.md` — so it does not derive them |
| its zone, and what it must not touch | zones of tickets flying beside it included |
| credentials | variable **names**, never a value |

A subagent has a filesystem; pasting what it can read writes the same words twice into the bill, and the second copy stays in your context for the rest of the run. Every rule the executor must follow travels in its prompt or in `prompts/executor.md` — a rule that lives only in a phase file does not exist for the one writing the code.

**The model.** A ticket marked `Модель: сильная` runs on the session's model. `обычная` runs on a cheaper one — in Claude Code, `model: "sonnet"` on the Agent call; a harness without a model choice ignores this silently. A ticket that already failed once is relaunched on the strong model.

**Dependencies.** Ticket 01 installs everything the spec's «Решения по реализации» names. A later ticket that needs something else returns `BLOCKED` with its name; if it fits a decision already made, add it to «Решения», relaunch that ticket with permission to install exactly that — the manifest and lock files join its commit — and fly nothing else that installs at the same time.

## Waves

Phase 4 gave every ticket a wave and a zone. **Launch a whole wave in one message, one subagent call per ticket, in the background** — two calls in two messages run one after the other, and the parallelism computed in the plan is thrown away in the delivery.

- **At most three in flight.** A wave of five goes out as three, then two. A point reviewer reads a commit and writes nothing — it does not count against the three.
- **Zones disjoint** — checked again at launch; same files → serialise. When in doubt, serialise.
- **A wave is not a barrier.** When a ticket returns, first launch the next ticket whose dependencies are all committed, then process the one that landed.
- **A dependent never launches on an uncommitted parent.**
- `ap.py ticket 02 03 start` goes **before** the launch — one call for the whole wave, **in the same message as the Agent calls**: Bash first, the launches after it.
- **One event, one message.** Every call of yours re-reads your whole context — at 200K, one call costs about as much as a small subagent's first steps. What one event needs goes out together: the `ap.py` mark, the commit, the next launch, the line to the user. Never a call that only marks, then a call that only launches.
- **Waiting for the wave is ending your turn** — a background subagent wakes you when it returns. Never spawn an agent, or run a loop, just to wait.

**One working tree, several writers.** Parallel executors share the checkout. Each touches only its zone (and `.env.example`), and you commit by zone. A check that fails **only in files of zones still being written** is a neighbour's unfinished work, not this ticket's defect: the ticket may land on its own tests green, and the full check runs again when the neighbour lands.

## The return contract

Required in the prompt, not suggested — without it you cannot update anything:

```
STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
FILES: созданные и изменённые — только пути
TESTS: команда проверки → результат и сколько было до тебя (`npm run check` → 34 passed, было 21)
REDPROOF: новый тест → чем он падал до кода (одна строка на тест, до пяти)
INTERFACES: публичные сигнатуры, схемы, форматы событий, которые ты выставил
REQUIREMENTS: R01 done | R01.1 placeholder — <чего не хватило>
CONCERNS: что сделано с оговоркой и почему
BLOCKERS: чего не хватило (зависимость, решение, доступ)
```

**No more than 25 lines, no code, no diffs, no account of the work.** A block longer than that is not read: ask for it again in one line — an essay skimmed once is re-read on every remaining turn of your context.

## After each ticket

In this order:

1. **Read the contract and its status.** No block → the ticket is not finished; ask for it. `BLOCKED` or `NEEDS_CONTEXT` → `phases/5-repair.md` now. A `CONCERNS` line saying the plan does not hold — a data model, an interface, two requirements colliding — is the build contradicting the plan: `phases/5-repair.md` too. Two `NEEDS_CONTEXT` in one run mean the tickets are too thin across the board.
2. **Nothing outside the zone.** `git status --porcelain`: a changed file outside this ticket's zone, `.env.example` and the zones still in flight is a дозапрос — put it back or say why it had to change.
3. **Append its `INTERFACES` to `interfaces.md`** — you, never the executors; parallel writers collide. Two returns claiming one interface is a plan defect: keep the one that fits and re-cut the other.
4. **Run the check**, full, truncated: `<check> 2>&1 | tail -30`, **and read it before anything else happens** — green or red, the names of what failed, and the count. Compare the count with the contract: a `DONE` that added criteria and no tests is a дозапрос, and a suite reporting zero tests is red however it exits.
5. **Red → `phases/5-repair.md`.** Nothing is committed on red, and nothing is repaired by you.
6. **Commit and record — one call, only its zone:**

   ```bash
   git add -A -- src/bot/ tests/bot/ .env.example && git commit -qm "T03: приём заявки" \
     --trailer "Autopilot-Run: 2026-10-10-repair-bot" --trailer "Requirements: R01, R02" -- src/bot/ tests/bot/ .env.example \
     && python3 .autopilot/ap.py ticket 03 done --tests 34/0 --commit "$(git rev-parse --short HEAD)"
   ```

   **`done` without `--commit` is refused, and git refusing the commit is never worked around** — `index.lock`, `Permission denied`, a sandbox error: that is the machine, so `phases/5-repair.md`, «Fail early». The `&&` stays: a ticket is done when its commit exists.

   The paths are every path of its zone that exists, plus `.env.example` if the ticket changed it — git refuses a path that matches nothing; `--tests` is what step 4 actually printed; `--placeholder R05` for each row the contract reports as a stub. One commit per ticket — the user's rollback points. **The trailers make the history searchable after the run is gone**: `Autopilot-Run` is `dir` without `--wip` (ticket numbers restart every run, so `T03` alone names several tickets), `Requirements` the ticket's rows. `git log --grep="R02"` then finds every change a requirement ever caused.
7. **Point review, if the ticket says `Ревью: да`**, or the contract reports one of its requirements as not done: `ap.py ticket NN review`, the reviewer in the background, and straight on to the next step and the next wave (`phases/6-review.md`). Its `BLOCKING` lines, when they come, go to `phases/5-repair.md`.
8. **The ledger.** Each stub the contract names → `ap.py add debt.placeholders`; each new variable → `add debt.emptyEnv NAME`; each `A##` that reached the code → `add additions`; each `CONCERNS` line about craft → `add concerns`. Project memory only if something was discovered (`phases/9-memory.md`, Moment 2) — most tickets add nothing.
9. **One plain line to the user**: «Бот принимает заявки — 3 из 8 готово».

**Two tickets returning together are processed one at a time**, each through the whole list: one commit each, a check after each — otherwise a red has two possible authors.

## When the build is over

Every ticket is `done`, or `failed` with its dependents named to the user as waiting — point reviews included: none still running, every repair they asked for landed. Then `ap.py stage review` and `phases/6-review.md` — the whole-branch review.
