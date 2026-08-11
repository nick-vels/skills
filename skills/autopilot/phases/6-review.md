# Phase 6 — Checklist

Review of each ticket's diff along three axes. Not sequential — it runs inside Phase 5, after every ticket.

Three axes, because a change can pass one and fail another:

| Axis | Question | Fails when |
|---|---|---|
| **Manifest** | does the diff deliver what the user asked for, in their words? | a requirement quietly shrank |
| **Spec** | does it implement what the spec decided? | the executor improvised |
| **Craft** | is the code fit to build on? | it works today and blocks tomorrow |

Report them **separately**. Merging or ranking findings across axes lets one mask another — clean code implementing the wrong thing looks fine until you read the axes apart.

## Which axis a finding belongs to

One question decides it: **could the executor have known?**

It saw its ticket, the spec sections that ticket named, and `interfaces.md`. Nothing else.

- **Yes, it could have known** → axis Spec or Craft. This is a defect of the code, and it is fixed in this ticket.
- **No, it could not have known** → axis Manifest. The requirement was lost on the way down, and the defect is in the spec or in the cut — **not in the executor**. It still gets fixed, but do not re-run the subagent against words it was never given: repair the ticket first, or the spec, then run it.

This is the same line the whole framework runs on, seen from close up. Between the gates everything measures against the spec, because the spec is the contract the crew actually received; only at G2 and G4 does anything measure against the brief, and there the subject is the plan, not the code. **The manifest is what lets axis 1 exist at all** — without it the brief is prose and cannot be checked one ticket at a time.

## Scale to the ticket

Cheap early, delegated once it starts costing. A review that costs more than the ticket is its own kind of waste — and so is a review that quietly spends the one context the run cannot replace.

| Where the run is | How |
|---|---|
| tier T0 — no tickets at all | all three axes yourself, inline: there is nobody to delegate to, and the run ends before it matters |
| the first two tickets, diff under ~150 changed lines | inline still allowed |
| every ticket after that, and anything touching shared modules | Manifest+Spec in one subagent, Craft in another, in parallel |
| the final whole-project pass at the end | separate subagents, per `phases/8-final.md` |

**Why the threshold is not diff size alone.** A hundred-line diff costs the same to read whenever it arrives; what changes is what you have left to spend it from. The orchestrator's context is the only one in the run that is never refreshed (`phases/5-subagents.md`), and inline review is how it fills — undramatically, one ticket at a time, until ticket 08 is being judged by a reader who has been awake since the brief. The concession for the first two tickets is there because a reviewer's setup cost is real and early context is cheap. It expires because neither stays true.

**The reviewer gets the testing check, verbatim.** «A green suite is evidence only if the tests could have been red» — the assertion-level reading in `phases/5-subagents.md`. It is part of the Craft axis, it goes into the prompt, and it is the instruction most often dropped on the way down, because a pass count looks like it already answered the question.

## Axis 1 — Manifest

The axis that does not exist in ordinary code review, and the one this framework is built around.

Take the ticket's `Требования` line, pull those rows from `manifest.md`, and read the **verbatim brief quotes** — not the spec's version, not the ticket's summary. Then, for each:

- Is it delivered end to end, or only the easy half?
- Was it narrowed on the way down? A requirement that entered as «клиент видит статус» and left as a status stored in the database but shown nowhere is a shrunk requirement, not a done one.
- Does a `placeholder` sit exactly where a user fact belongs — and is it visibly a placeholder, not a plausible invention?

Verdict per requirement: `done` / `partial` / `missing`, and `partial` or `missing` means the ticket is not finished.

## Axis 2 — Spec

Against the spec sections the ticket named:

- **Missing** — a decision the spec made that the diff does not implement.
- **Extra** — behaviour in the diff that no one asked for. Scope creep is not a bonus; it is untested surface with no requirement behind it and nobody to maintain it.
- **Wrong** — implemented, but not the way the spec decided. Especially: a second version of something `interfaces.md` already provides.

A diff that departs from the spec because the spec turned out to be wrong is **not** a finding on this axis — but it is only legitimate once the spec has been amended and a `D##` row exists. An undocumented departure is `Wrong`, however good the reason: see `phases/5-subagents.md`.

Quote the spec line for every finding.

## Axis 3 — Craft

Whatever the repo documents about how code should be written wins over everything below. Skip anything tooling already enforces — a linter finding is not a review finding.

On top of that, a fixed baseline of smells worth naming. These are Fowler's, from *Refactoring* ch. 3, and each is a **judgement call** — "possible Feature Envy" — never a hard violation:

- **Mysterious name** — the name does not say what it does or holds → rename; if no honest name comes, the design is murky.
- **Duplicated code** — the same shape in more than one place in the diff → extract it, call it from both.
- **Feature envy** — a function reaching into another object's data more than its own → move it to the data.
- **Data clumps** — the same few parameters always travelling together → a type wants to be born.
- **Primitive obsession** — a string standing in for a domain concept → give the concept its own small type.
- **Repeated switches** — the same branch cascade on the same type, more than once → one map both sites share, or polymorphism.
- **Shotgun surgery** — one logical change scattered across many files → gather what changes together.
- **Divergent change** — one module edited for several unrelated reasons → split it.
- **Speculative generality** — abstraction for needs the spec does not have → delete it.
- **Message chains** — `a.b().c().d()` the caller should not know about → hide the walk.
- **Middle man** — a layer that mostly delegates onward → call the real target.

Plus three that matter specifically here, because subagents cause them:

- **Reinvention** — the diff builds something `interfaces.md` already provides. The most common defect of parallel crews, and the most expensive.
- **Silent narrowing** — an acceptance criterion satisfied in letter and dodged in substance (an empty catch, a hardcoded happy path, a test asserting the code back to itself).
- **Invented fact** — a real-looking price, address, name, or phone number where the user's actual data belongs. Always a defect, never a placeholder.

## What to do with findings

**Every "fix" below happens in the ticket, not in the orchestrator and not in the reviewer.** A finding goes back to the executor that wrote the code, as a **дозапрос** stating the condition — `phases/5-subagents.md`. The reviewer judged and is done; a reviewer that also repairs is a check that has stopped being one. Two дозапроса is the ceiling, after which the finding becomes a failed ticket and takes that path instead.

- **Manifest `partial`/`missing`, or Craft "invented fact"** → repaired now, in this ticket, before the commit.
- **Spec "extra"** → removed, unless it is genuinely required for the rest to work — then say so in one line in the commit message.
- **Craft judgement calls** → repaired if the fix is small and local. If it is structural, note it in `state.js` under `concerns` and carry it to the final report. Do not start a refactor inside a ticket that was not about refactoring.

Refactoring belongs here, not inside the red-green loop. Cleaning up while chasing a failing test is how both jobs get done badly.

## Reporting

To yourself, structured, per axis. **To the user, nothing** — unless something is being carried to the final report as a concern. The user gets one plain line per ticket from Phase 5, not a review.
