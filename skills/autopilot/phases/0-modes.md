# Phase 0 — Mode and depth

Read in Phase 0 with `phases/0-preflight.md`. Both dials are decided once, from what the user typed, announced in one block, and only *applied* from then on.

Everything after `/autopilot` splits into **the mode** (`full`, `semi`, `interview`, `manual`), **the depth** (`strict`, `deep`) and **the brief** — everything else. Bare words, any order, both optional; anything unrecognised is brief. `/autopilot full deep интернет-магазин керамики` — full mode, deep elaboration.

## Mode — how much the user is asked

| Mode | Triggers | Human gates |
|---|---|---|
| **full** — полный автомат | `full`, «полный автомат», «полностью сам», «ничего не спрашивай», "fully automatic", "don't ask me anything" | none |
| **semi** — полуавтомат **(default)** | `semi`, «полуавтомат», nothing said | questions, on genuine forks only |
| **interview** — режим интервью | `interview`, «режим интервью», «погриль меня», «допроси», «задай все вопросы», «разбери задачу со мной», "interview me", "ask me everything" | questions, all of them |
| **manual** — ручной | `manual`, «ручной режим», «согласовывай каждый шаг», "approve every step" | the same questions + the spec + the tickets |

`interview` asks about the *product*; `manual` is `interview` plus approval of the two *process* artifacts, and nothing else.

- **Ambiguity resolves to semi.** A mode word contradicting the rest of the sentence → the mode word wins; two mode words → ask which, in one line.
- **Switchable mid-run** («переключись в ручной») — applies from the next phase; one line of acknowledgement, nothing replayed.
- **Instructions in the brief** — stack, budget, «без базы данных», a deadline — are requirements in the manifest. They constrain the build; they never replace a phase.
- **No mode removes the manifest gates or the safety gates.** Deploy, publish, pay, message a third party, delete data, rewrite history — a question in all four modes, full included, with `ap.py ask action --note "…"` before it goes out.

## Depth — how much is worked out for the user

| Depth | Triggers | Deepening a requirement (`R##.n`) | New capabilities (`A##`) |
|---|---|---|---|
| **strict** | `strict`, «строго по брифу», «только то, что сказал», «ничего не добавляй», "strictly as written" | only what the requirement cannot work without | **not allowed** |
| **normal** **(default)** | nothing said | by judgement, where it plainly helps | allowed, with a parent, within proportion |
| **deep** | `deep`, «проработай глубоко», «продумай за меня», "go deep", "think it through" | every dimension of every requirement | encouraged, same limits |

- `strict` does not mean careless: errors and empty states are still handled; what goes is anything not asked for.
- `deep` never lifts the attachment rules — every `A##` names its parent, the proportion holds.
- **The adversarial pass** (`phases/2-adversarial.md`) runs at `deep` in every mode, and in `interview` and `manual` at every depth.
- Changeable mid-run («поменьше отсебятины», «продумай глубже») — from the next phase; written spec sections are not retroactively trimmed unless asked.

The rules for each level live in `phases/3-spec.md`.

## The opening block

Once, before Phase 1, together with the dashboard and the memory file. **A hint, not a question** — say it and go; in a chat there is no `--help`, so this is the only place the user learns the dials exist.

```
Режим: полуавтомат · глубина: обычная — спрошу только то, что в задаче не определено, дальше соберу сам.
Дашборд открыл — обновляется сам: http://localhost:PORT/dashboard.html
Память проекта — AGENTS.md (+ CLAUDE.md со ссылкой).
↑ Вышла версия Autopilot 2.2.1 (у тебя 2.2.0): npx skills update autopilot -g   ← только если init её напечатал

Можно переключить в любой момент, просто скажи:
• «полный автомат» — не спрашиваю вообще ничего
• «режим интервью» — разберу задачу вопросами до конца, дальше соберу сам
• «ручной режим» — то же плюс согласуешь спецификацию и список тасков
• «строго по брифу» / «проработай глубоко» — меньше или больше проработки сверх сказанного
```

No server → the dashboard line names the file: «Дашборд открыл — `.autopilot/dashboard.html`, обновляется сам.» Never repeated later; a mid-run switch gets one line: «Понял, дальше ручной режим».
