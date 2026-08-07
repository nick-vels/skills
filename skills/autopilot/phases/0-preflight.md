# Phase 0 — Preflight

Configure the repo and raise the instruments. Runs once per repo, before anything else. Skip entirely if `.autopilot/` already exists — the repo is configured, go to Phase 1 and reuse it.

**Nothing here is a question for the user.** These are process decisions, not product ones. No mode buys the user a say in where ticket files live; asking about it is exactly the kind of question Autopilot exists to remove.

## 1. Name the flight

Derive a **feature-slug** from the dictated idea — short, kebab-case, latin (`telegram-repair-bot`, `nail-studio-landing`). It names `.autopilot/<feature-slug>/` for the whole run and never changes mid-flight.

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
├── <feature-slug>/
│   ├── brief.md
│   ├── manifest.md
│   ├── spec.md
│   ├── interfaces.md
│   └── tickets/
├── state.json
└── dashboard.html
```

`state.json` and `dashboard.html` are written now, empty-but-valid, per `phases/7-instruments.md`. The dashboard exists from the first minute so the user can watch the build from the start rather than read about it at the end.

## 4. Record the conventions

Write `.autopilot/README.md` — a short note for the human, not for the agent:

```markdown
# Как читать эту папку

- `dashboard.html` — открой двойным кликом. Прогресс, график, что осталось.
- `<проект>/brief.md` — твоя изначальная задача, слово в слово. Не редактируется.
- `<проект>/manifest.md` — список требований и что с каждым стало.
- `<проект>/spec.md` — техзадание.
- `<проект>/tickets/` — задачи, на которые разбита сборка.

Если сборка прервалась — скажи агенту «продолжи автопилот», он поднимет состояние отсюда.
```

## 5. Note the skill in the agent file

If `CLAUDE.md` exists, edit it. Else if `AGENTS.md` exists, edit it. Else create `AGENTS.md`. Never create one when the other already exists. Add or update a single block — in place, never duplicated:

```markdown
## Autopilot

Сборка ведётся навыком `/autopilot`. Требования, спека и задачи — в `.autopilot/`.
Прогресс — `.autopilot/dashboard.html`. Правило: требование из `manifest.md`
может снять только пользователь.
```

Note in the Phase 8 report which file was chosen.

## 6. Git

If there is no git repo, `git init` **now**, not in Phase 5 — the first commit must be able to happen the moment the first ticket lands. Write `.gitignore` before anything else is created, with at least:

```
.env
.env.*
!.env.example
node_modules/
__pycache__/
.DS_Store
```

`.autopilot/` is **not** ignored. It is the record of what was promised.

If a repo already exists and its working tree is dirty, say so in one line and continue — do not stash, reset, or clean the user's uncommitted work.

## Resuming an interrupted flight

`.autopilot/state.json` exists and has unfinished tickets → this is a resume, not a new flight.

1. Read `state.json`, `manifest.md`, `interfaces.md`. Do **not** re-read the whole dialogue; the files are the memory.
2. Tell the user in one line where things stand: «Продолжаю: 7 из 12 задач готовы, следующая — корзина».
3. A ticket marked `in-progress` in `state.json` with no commit behind it was interrupted mid-flight. Reset it to `pending` and run it again from scratch — a half-applied ticket is worse than a fresh one.
4. Re-run the Phase 6 checklist over the whole diff since the last green commit before continuing. Something may have been left broken.
5. Continue from the frontier. Do not redo finished phases; do not re-ask answered questions.
