---
name: autopilot
description: Builds an app, site, bot, or feature end-to-end from a dictated idea — requirements, briefing, spec, tickets, subagents, review, acceptance — with a live dashboard, for users who expect a finished result without reviewing specs or code. Starts only on /autopilot; a bare /autopilot resumes an interrupted run.
disable-model-invocation: true
argument-hint: "[full|semi|interview|manual] [strict|deep] что нужно построить или путь к brief.md"
metadata:
  version: "2.0.1"
---

# Autopilot

Autopilot flies a dictated idea from words to a working project **in one dialogue**, without making the user approve each stage. Every rule it needs lives in `phases/` and `prompts/`; no other skill has to be installed.

**The order is the product.** Code is written in the second-to-last phase. Everything before it decides *what* to build; everything after it proves the right thing got built.

**The brief is the contract, not the design.** *Nothing may quietly vanish*: the user's words become a numbered manifest before anything else, and every phase is gated on it — what breaks naive vibecoding is a requirement that stopped existing around the third rewrite. And *the brief is a silhouette*: it describes the happy path and nothing underneath, so working out the empty states, failures and limits is legitimate work. How far to take it is the user's [depth](phases/0-modes.md) dial; depth that **detaches** from the brief is never allowed.

## Reading this skill

This file is the orchestrator: order, gates, the rules that never lose. Each phase's rules are in its own file, **read when that phase starts and not before** — one file at a time, never ahead: a file opened early stays in the one context that is never refreshed for the rest of the run.

| Phase | Read | Produces |
|---|---|---|
| 0 Preflight | `phases/0-modes.md`, `phases/0-preflight.md`, then `0-memory.md`, `0-instruments.md` | mode announced, repo configured, dashboard open |
| 1 Manifest | `phases/1-manifest.md` | `<дата>-brief.md`, `manifest.md` |
| 2 Briefing | `phases/2-briefing.md` (+ `2-adversarial.md` when it runs) | answers recorded into the manifest |
| 3 Spec | `phases/3-spec.md` | `notes.md` in existing code, `spec.md`, the boundaries in `interfaces.md` |
| 4 Plan | `phases/4-plan.md` | `tickets/NN-*.md`, the plan commit |
| 5 Build | `phases/5-subagents.md` | code, one commit per ticket |
| 6 Review | `phases/6-review.md` — at the first point review, and for the whole-branch review | reviewed code |
| 8 Final | `phases/8-final.md`, and `phases/9-memory.md` before spawning | blind acceptance, memory, report |
| — | `phases/0-resume.md` — instead of preflight, when resuming | |
| — | `phases/5-repair.md` — when a ticket comes back anything but a clean `DONE` | |
| — | `phases/9-memory.md` — also in Phase 5, when a ticket discovered something worth keeping | |
| — | `phases/rationalizations.md` — on a failed gate, on catching yourself excusing something, once before the report | |

**After a compaction, re-read the state, not the phases:** `state.js` (it holds `dir` and `skillDir`), `manifest.md`, `interfaces.md`, and the file of the phase you are in. Nothing else.

## The words the user sees

Phase names here are English and never shown. In the chat, on the dashboard and in the report there is **exactly one Russian word per stage**:

| Stage id | Пользователю |
|---|---|
| `preflight` · `manifest` · `briefing` · `spec` | Подготовка · Требования · Брифинг · Спецификация |
| `plan` · `build` · `review` · `final` | План · Разработка · Код-ревью · Приёмка |

**«Сборка» — весь прогон**, поэтому пятый этап — «Разработка». **Единица работы — «таск»**: «задача» — это то, что поставил пользователь.

## The flight

Two dials, decided once in Phase 0 (`phases/0-modes.md`): **the mode** — `full`, `semi` (default), `interview`, `manual`; **the depth** — `strict`, normal (default), `deep`.

| Phase | full | semi | interview | manual |
|---|---|---|---|---|
| 1 Manifest | auto | auto | auto | auto |
| 2 Briefing | self-briefing | only what the brief leaves open | the adversarial pass, then every fork | the same |
| 3 Spec | auto | auto | auto | show → wait for «ок» |
| 4 Plan | auto, notify | auto, stoppable | auto, stoppable | discuss → wait for «ок» |
| 5 Build · 6 Review | auto | auto | auto | auto |
| 8 Final | report + Assumptions | report | report | report |

`interview` and `manual` differ in exactly two cells — the spec gate and the plan gate.

**The manifest gates run in every mode** — they check the build against the user's own words, and cost the user no time:

| Gate | After | Passes when |
|---|---|---|
| **G1** | Briefing | every requirement has a status; none `open` without a recorded reason |
| **G2** | Spec | zero `open` — **and an independent reader given only the brief and the spec finds nothing missing** |
| **G3** | Plan | every `in-spec` requirement is in a ticket and every ticket traces to one — `ap.py check-plan` |
| **G4** | Final | blind acceptance against the brief, spec withheld, from a clean clone |

G2 and G4 are one check at the two ends of the flight: they measure against the user's words with your paraphrase taken away. Between them everything measures against the spec, because that is the contract the executors were given. A failed gate sends its phase back to be redone.

**The plan may be corrected; the brief may not.** When the build proves the plan wrong, the spec is amended and a `D##` row records what the code demonstrated (`phases/5-repair.md`) — never a way to retire a requirement or to slip in an idea.

## Secrets

Binding on every phase; the phases do not restate it.

- **Never request one.** *Which* provider and *whether* an account exists are questions; the key, token, password or connection string never is.
- **Redact at ingest**, before anything is written — the gate in `phases/1-manifest.md`. «Verbatim» always means «verbatim after redaction».
- **Refer to it by name** — `STRIPE_SECRET_KEY`. The user puts values into `.env` themselves; `.env` is ignored before the first commit; the report lists the names still empty.
- **A leaked secret is a stop condition**: reported at once, in plain words, with the advice to rotate it.

## Files this skill owns

```
.autopilot/
├── <YYYY-MM-DD>-<slug>--wip/   one run; the suffix comes off when it lands
│   ├── <YYYY-MM-DD>-brief.md   the user's words, redacted; later changes appended
│   ├── manifest.md             requirements and their status
│   ├── reference.md            what it should be like — the user's comparables only
│   ├── spec.md                 the specification
│   ├── interfaces.md           the boundaries, the project rules, what finished tickets built
│   ├── notes.md                exploration notes, in an existing codebase
│   ├── memory-proposal.md      what to add to the user's own memory file, if it is theirs
│   └── tickets/NN-<slug>.md
├── README.md        how to read this folder, and the register of runs
├── state.js         the run state — written only by ap.py
├── ap.py            one call per event: state, dashboard, server
├── dashboard.html   the human view; carries a snapshot of the state
└── index.html       → dashboard.html

AGENTS.md (+ CLAUDE.md → @AGENTS.md)   the project memory — or the user's own file, left untouched
docs/architecture.md, docs/adr/        at T2+: how it is built, and why
CONTEXT.md                             at T2+: the project's words — or the user's own, only added to
```

`.autopilot/` is committed — it is the user's record of what was promised and delivered. The memory file is the project as it stands for whoever opens it next; `docs/adr/` is why it stands that way; `CONTEXT.md` is what its words mean; `spec.md` is throwaway once the work ships.

## Judgement

Numbers in this skill — tiers, question counts, wave widths — are **calibration for a first guess, never targets.** The rules are arguments, each paid for, and arguments can lose: where following one would make the result worse for the user, break it deliberately, say so in one line, and carry on. Never quietly, and never keep one only because it is written down.

**The rules that set the run's cost are the exception** — what goes to repair, which tickets get a point review, how many times a fix is re-reviewed. Widening them «for quality» is how a run doubles its bill with nobody having decided to. Break one only by telling the user in one line what it will cost.

**Five rules are not calibration and do not lose** — in every mode, at every depth:

1. **A requirement is removed only by the user**, in their own words, quoted into the manifest and appended to the brief. The same holds for one they add mid-flight.
2. **A secret is never requested, echoed or written** — not into a file, a prompt, a commit or a report.
3. **A fact about the user is never invented.** Prices, texts, addresses, accounts stay visible placeholders.
4. **An irreversible or outward-facing action is a question** — deploy, publish, pay, message a third party, delete data, rewrite history.
5. **The orchestrator does not write the project's code.** Its keyboard reaches `.autopilot/`, the memory files, `.gitignore`, `.env.example` and git; everything else goes to a subagent (`phases/5-subagents.md`).

## When to use it

The user dictates what to build and expects the finished thing; they will not read specs or review code. «Собери под ключ», "just build it". Wanting the idea taken apart question by question and the build done without them is still Autopilot — `interview`; wanting to approve the spec and the tickets is `manual`.

**Not:** co-writing code line by line with the user; a small single-file change (just do it); an idea bigger than one project whose destination is unclear (settle that first).
