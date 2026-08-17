# Phase 5 — Crew

Where the code gets written. **Identical in all four modes — this phase is always hands-free.** Manual mode buys the user control over *what* gets built, not over each edit; once the tickets are agreed, the crew flies to the end without further approvals.

At tier T0 there are no tickets: you are the crew, working straight from the spec in the current context. Everything below about contracts and returns still applies to you — top up `interfaces.md` with what you actually built, run the Phase 6 checklist, commit once.

**T0 does not excuse empty instruments.** Mark the `build` stage `active` before you start and `done` when you finish, record the pass in `state.js` under `singlePass` (files, tests, commit, both timestamps), and update the `requirements` counts exactly as a ticket would. A run that finished the whole project and left the user a dashboard showing nothing but a running clock has failed at the one job the dashboard has. See `phases/7-instruments.md`.

## One ticket, one subagent, one fresh context

Never two tickets in one context. Accumulated context is precisely what makes long vibecoding sessions start breaking things that used to work — the model stops reading and starts remembering, and its memory is worse than the files.

The corollary is that a subagent knows **nothing** except what you hand it. Hand it the right things.

## The context ceiling — when one ticket outgrows one context

Freshness is not smallness. A subagent that starts clean and then runs three hundred steps ends up in exactly the context this design exists to avoid; it just took an hour to get there.

**Doubling the ceiling doubles the bill.** A run pays `число шагов × средний контекст`, and the average is half of whatever ceiling the executor may reach; splitting the same work across two contexts costs one extra cold start instead. Measured on a T3 run: nine executors averaging 200 K spent 392 M tokens on reading, where a 120 K ceiling would have spent 161 M.

**Count what the executor can count** — its own tool calls, not its edits. A ticket that reads forty files and edits nine is far past any ceiling while the edit count says otherwise. One call costs about 1 900 tokens, so **fifty calls is roughly 120 K**, and the spread across tickets (29 to 68) is why the number permits rather than commands.

The rule itself — the count, the handoff format, the path, and what to do when green cannot be reached — is written for the executor in **`prompts/executor.md`**, and it goes down as a **path**. Nothing about a handoff may live only in this file: the executor writing that file has never read it.

**The count permits; the green run decides.** A hard stop at a counter lands mid-edit, and the successor spends its first twenty calls working out what was going on — which is the whole cost this was meant to remove. A ticket that has just gone green is a seam: the suite passes, and everything unfinished is named in the acceptance criteria instead of in someone's head. A ticket that finishes at thirty calls simply never reaches the ceiling, and most do.

**A handoff without `РЕШЕНИЯ`, `ТУПИКИ` and `ДАЛЬШЕ` produces a second design of the same thing** — *Reinvention*, arriving through a door this section opened. The code on disk says what was built; only those three say why, what is already ruled out, and where the seam is. The format is the executor's (`prompts/executor.md`); your part is noticing a handoff that came back without them.

**At tier T0 the ceiling does not apply to you** — you are the crew and there is nobody to relay to, and rule 5 forbids the only alternative. That is one more cost of T0, affordable for the same reason the rest of it is: a T0 run ends before the context fills. If it does not — if you are fifty calls in and the end is not in sight — the tier was read wrong, and the honest move is to say so and cut tickets, not to keep typing.

**Two handoffs per ticket, then stop relaying.** The third context finishes the ticket or returns `BLOCKED` — it does not relay again. A ticket that needs a fourth is not an executor's failure but a Phase 4 cut that was too coarse: record it in `state.js` under `concerns` and carry it to the final report as a note on the plan, the same way a structural Craft finding travels (`phases/6-review.md`). Without a ceiling on the ceiling a badly cut ticket relays forever and nobody finds out why the run cost what it did.

## Your hands

You dispatch; you do not build. Through the whole of Phase 5 your keyboard reaches exactly three things:

- `.autopilot/**` — state, manifest, interfaces, tickets, dashboard
- the project memory file, between its markers
- git — `add`, `commit`, `--stat`; never the diff itself

Every other file in the repository is written by someone whose context dies with the ticket. **This is rule 5 of the five in `SKILL.md`, and it loses to no argument** — least of all to the two that always arrive: «тут править две строки» and «исполнитель не смог, доделаю я».

The reason is arithmetic, not taste. A subagent spends its context and throws it away; you spend yours and keep it — a diff read at ticket 02 is still sitting there at ticket 08, competing for room with the requirement you are checking. It is the mechanism the whole framework is built against, and here it cannot be escaped by starting fresh, because starting fresh means losing the run.

So the material never reaches you. What reaches you is a verdict, a list of names, one contract block per ticket.

**At tier T0 you are the crew**, so the rule cannot apply — there is nobody to hand the keyboard to. That is a cost of T0, not an exemption pattern: it is affordable only because a T0 run ends before the context fills. The moment there are tickets, there is someone else to type.

## What a subagent gets

| | |
|---|---|
| `interfaces.md` | by path — the boundaries from the spec, plus what previous tickets built; read in full, first |
| its ticket | **by path only.** The ticket file already contains the verbatim brief quotes; sending the body as well means the run pays for the same words twice |
| the spec sections its ticket names | by path **and section headings** — `spec.md`, разделы «Приём заявки», «Валидация». Not the whole spec, and not the sections pasted: naming them is what keeps the executor out of the rest of the document |
| the test command and how to run one file | so it does not have to derive them |
| **`prompts/executor.md`, by path** | the testing contract, the context ceiling and the return contract — **require it read before the first edit.** The path is `skillDir` in `state.js`, resolved in Phase 0 and read from there rather than remembered. Without the ceiling the ticket runs until it stops, which is the single most expensive thing in the flight |
| the working directory and stack constraints | including what it must not touch |
| variable **names** for any credential | never a value, ever |
| the return contract | the block below, as a requirement, not a suggestion |
| the paths to `handoff-<NN>-*.md` | **only when continuing a handed-off ticket** — all of them, oldest first, as paths, never pasted |

**Paths, not contents — for everything on this list that lives in a file.** The ticket, the spec sections, `interfaces.md`, a handoff: a subagent has a filesystem and can read. Pasting the material instead writes it twice into the run's bill — once as your output, then on every subsequent turn of your own context, which is the one that is never refreshed. The exceptions are the two verbatim blocks above, which exist nowhere the executor can reach, and any harness where a subagent genuinely cannot open a file.

**This is a rule about executors, and it does not reach the blind checks.** G2 and G4 work because a subagent has *not seen* the spec — and «can read» cuts both ways: `.autopilot/` is committed and sits in the repository the checker is pointed at, so not sending a file is no longer the same as withholding it. A blind check therefore needs the prohibition stated to it, not merely honoured by you: **«не открывай `.autopilot/` — ни спецификацию, ни манифест, ни таски»**, in its own prompt (`phases/3-spec.md`, `phases/8-final.md`). Independence you can only observe is independence you have already lost.

**A rule that lives only in this file does not exist.** These phase files are read by the orchestrator; the code is written by someone who never sees them. Anything the executor must do travels in its prompt or not at all.

## What the executor is judged by — `prompts/executor.md`

Two conditions decide whether a returned ticket is acceptable, and neither of them is about what the ticket asked for: **how its tests are written**, and **when it stops and hands the ticket on**. Both live in `prompts/executor.md`, and both go down as a **path** in the prompt — with reading it required before the first edit, exactly as the Craft reviewer is given `prompts/craft-review.md`.

They are there and not here because they are the executor's material — an orchestrator that reads them keeps them for the rest of the run and gains nothing, since it does not write code — and because a paraphrase is a weaker check than the one that was written. The testing contract is the rule left behind most often, since it reads like guidance rather than an input.

What you still decide, and what does not fit in a shared file:

- **The test command and how to run one file** — so the executor does not derive them.
- **What the ticket must not touch** — zones from Phase 4, and anything a parallel ticket owns.
- **The tier.** At T0 you are the executor: read that file and apply it to yourself, minus the ceiling — there is nobody to relay to (above).

**A green suite is evidence only if the tests could have been red**, and that is not checkable from a pass count. Your part is two moves: see that the file's path went down with the executor, and treat what the Craft reviewer finds about the tests as a finding of kind *silent narrowing*, fixed in this ticket if it is blocking. A bad test is worse than a missing one — the missing one is visible.

## interfaces.md — the shared contract

The file that keeps eight independent contexts building one coherent project instead of eight incompatible halves. Without it, ticket 06 invents a second version of what ticket 03 already built, and nobody notices until the end.

Created in Phase 0, **seeded in Phase 4 from the spec's boundaries** — so the first subagent already reads the module map instead of inventing it. **You** — the orchestrator — append to it after each ticket returns, from that ticket's contract block. Subagents never write to it: parallel writers would collide, and a subagent cannot know what the others produced.

```markdown
# Что уже построено

Читается каждым исполнителем до начала работы. Не изобретай заново то, что здесь есть.

## Границы, решённые в спецификации

- `intake` — владеет заявками. `createRequest({phone, address, problem}) -> {id, createdAt}`
- `notify` — владеет отправкой. `send(channel, template, payload) -> {ok}`
- Швы для тестов: `intake` и `notify`, только через эти сигнатуры

## Общие правила проекта

- Стек и версии, команды запуска и тестов
- Что менять запрещено (файл конфигурации, схема, общий модуль и его владелец)
- Если не хватает зависимости — не добавляй сам, верни `BLOCKED` с названием

## Из таска 01 — каркас

- `db.connect(path) -> Connection` — единственная точка подключения
- Таблицы `requests`, `clients`; миграции в `migrations/`, владелец — таск 01
- Тесты: `npm test`, один файл — `npm test -- <path>`

## Из таска 02 — приём заявок

- `createRequest({phone, address, problem}) -> {id, createdAt}`
- Валидация телефона — `validatePhone(raw) -> {ok, normalized}`, не пиши свою
```

Keep it to interfaces and rules. It is not a log — the log is `state.js`.

## The return contract

Every subagent ends by returning exactly this. Put it in the prompt as a requirement, not a suggestion: without it you cannot update the instruments or the manifest, and the next ticket flies blind.

```
STATUS: DONE | DONE_WITH_CONCERNS | HANDOFF | BLOCKED | NEEDS_CONTEXT
FILES: созданные и изменённые
TESTS: команда → результат и сколько было до тебя (`npm test` → 34 passed, было 21)
INTERFACES: публичные сигнатуры, схемы, форматы событий, которые ты выставил
            — то, чем будут пользоваться следующие таски
REQUIREMENTS: R01 done | R01.1 placeholder — <чего не хватило>
CONCERNS: что сделано с оговоркой и почему
BLOCKERS: чего не хватило (зависимость, решение, доступ)
```

**Demand it short, in the prompt: не больше 25 строк, без кода, без диффов, без пересказа хода работы.** `FILES` is paths only; `INTERFACES` is signatures, not explanations of them. A subagent left to its own judgement returns an essay — it has just spent an hour on the work and wants credit for it — and eight essays cost you exactly what eight diffs would, arriving through a different door. A concern or a blocker that genuinely needs more gets one sentence; the detail stays in the code, where the next reader is anyway.

`NEEDS_CONTEXT` means the ticket was under-specified — the executor could not tell what was wanted. Treat it as a defect in Phase 4, not in the executor: re-cut the ticket with the missing detail and run it again. Two `NEEDS_CONTEXT` in one flight means the tickets are too thin across the board — go back and merge.

### `HANDOFF` — the ticket continues in the next context

`HANDOFF` is not a failure and not a repair. The work is sound as far as it got, the suite is green, and the ticket is simply longer than one context should be. The executor's side of it — when to stop, what to write, where — is the ceiling block at the top of this file, and it goes out **in the prompt**. What follows is your side.

**Verify the green before you relay.** The executor's word is the only evidence you have that the tree is clean, and it ran the suite from inside the context that just spent fifty calls. Run the full suite yourself, truncated as in step 5 below, *before* launching the successor. A red tree relayed forward is the worst thing this section can produce: the successor inherits a failure it did not cause, spends its fresh context hunting it in its own code, and the regression surfaces two tickets later with three possible authors.

**The successor is a normal executor, not a repair.** It gets everything the first one got — `interfaces.md`, the ticket, its spec sections, the testing contract, the ceiling — plus the path to the handoff file. Its counter starts at zero. Nothing is pasted into your context: you forward a path, the same way you forward `prompts/craft-review.md`.

**Each relay writes its own file** — `handoff-05-1.md`, then `handoff-05-2.md` — and the successor gets **all** of them, oldest first. One file per ticket lets the second relay overwrite the first, and with it every dead end the first executor paid to find; the third context then rediscovers them at full price.

**`INTERFACES` from a handoff is provisional.** Append it as usual, but a successor may legitimately change a signature its predecessor declared mid-work — that declaration was made at a seam, not at a finish. When the successor's block contradicts it, **replace the block instead of appending a second one**: two «Из таска 05» sections with different signatures is a file that contradicts itself, and every parallel ticket reads it. This is the one place where a later return overwrites an earlier one rather than accumulating.

**A дозапрос carries the ceiling too.** A repair request landing in a context already near the ceiling may itself come back `HANDOFF` — and then the successor needs the finding as well as the paths, because a repair condition exists nowhere on disk. Send the условие verbatim along with the handoff paths, or the successor finishes the ticket honestly and never fixes what review found, while `repairs` has already been spent.

In `state.js` the ticket stays `in-progress` across a handoff and its `handoffs` count goes up by one; `startedAt` is **not** rewritten — the ticket's clock covers the whole ticket, and resetting it on relay hides exactly the coarse cut the counter exists to expose. It is not `repair`: nothing was found wrong, and a run that counts handoffs as repairs reads its own dashboard as a quality problem.

**Review still judges the whole ticket, not the last context.** When the final context returns `DONE`, what goes to review is the diff since the last commit — not the `FILES` of the returning executor, which lists only its own share. One ticket, one commit, one review: the handoffs are invisible to the reviewer by design, and a reviewer shown only the last third would pass a ticket whose first two thirds nobody read.

## Order of flight — waves, not one at a time

Phase 4 left every ticket with a `wave` and a `zone`. Fly wave by wave, and inside a wave fly everything at once: **launch the whole wave in a single message, one subagent call per ticket.**

That last sentence is the whole section. Two subagent calls sent in two messages run one after the other — the parallelism was computed in the plan and then quietly thrown away in the delivery. This is the default failure, not a rare one: a serial flight looks exactly like a correct one from the inside, and the only visible symptom is a user waiting an hour for work that took twenty minutes of real dependency.

- **Cap at three in flight.** Beyond that the orchestrator's own context fills with returns it cannot usefully hold, and the whole point of the design leaks away. A wave of five goes out as three, then two.
- **Zones must be disjoint.** Phase 4 guarantees it within a wave; check again at launch, because a re-cut ticket may have moved into someone else's files. Overlap → the second one waits for the next slot. **Same files → serialise, no exceptions.**
- **A wave is not a barrier.** The moment one ticket returns, launch the next ticket whose blockers are all done — **and only then** process the one that came back. That order matters: bookkeeping, review and repair all happen while the crew is flying, not while it waits. Waiting for the slowest ticket of a wave gives back exactly what the wave bought.
- **Nothing parallelises with ticket 01.** The shell, the schema, the shared primitives: everything else reads what it built.
- **When in doubt, serialise.** A wrong guess about disjoint files costs silent lost work; a serial run costs minutes.
- **In manual mode the flight is still hands-free.** Waves change how the agreed tickets are ordered, never which tickets get built.

## Before each ticket

Set the ticket's `status` to `in-progress` and its `startedAt` to now in `state.js` **before** launching the subagent. It costs one edit, and it is the difference between the user watching a ticket run and the user watching nothing happen for eighteen minutes.

For a wave, that is **one state write for the whole wave**, before the launch message — all of its tickets flipped together. Two clocks running side by side on the dashboard is what parallel work looks like; two tickets marked `in-progress` an edit apart is the same thing and costs half as much.

## After each ticket

In this order, every time:

1. **Read the contract block.** No block → the ticket is not finished; ask the subagent for it. A block longer than the limit it was given is not read either: ask for it again in one line, because an essay you skim once you then re-read on every remaining turn of the run.
   **`HANDOFF` takes a different path — steps 5, 1 and 2 only:** run the full suite yourself (step 5) to confirm the tree really is green, append whatever interfaces were declared, bump `handoffs` in `state.js`, and launch the successor with the handoff paths. No review, no commit, no user line, and the ticket stays `in-progress`. The ticket is mid-flight: a third of a ticket has nothing a reviewer can judge against acceptance criteria, and its review happens once, on the whole diff, when the last context returns `DONE`.
2. **Append to `interfaces.md`.**
3. **Update the manifest** — `in-ticket` → `done` or `placeholder`, commit noted.
4. **Send the diff to review** — the ticket goes to `review` in `state.js` first, then the Phase 6 checklist runs, by someone who did not write the code (`phases/6-review.md`). What comes back to you is a verdict and a list of findings. The diff itself does not.
5. **Run the full test suite**, not just the ticket's own tests — and truncate the output: `<тестовая команда> 2>&1 | tail -30`. You need two things from it, green-or-red and the names of what failed, and both survive the truncation; the other two hundred lines are pure leak. A regression introduced now costs minutes; found eight tickets later it costs the evening.
   **Read the count, not just the colour.** The contract block reports what the suite ran and what it ran before this ticket, and the two numbers are the only floor there is: a `DONE` that added acceptance criteria and no tests is a дозапрос, and a suite reporting zero tests is red however it exits. A green run proves nothing about tests that were never written.
6. **Red test, or a finding the reviewer marked `BLOCKING` → repair:** the ticket goes to `repair` and its `repairs` count goes up by one, then re-run 4 and 5 over the repair alone — the re-review sees the fix's diff, not the ticket again. Findings *not* marked blocking do not come here: they go to `concerns` in `state.js` and are triaged once in `phases/8-final.md`. **Nothing is committed on red**, and nothing is repaired by you. The rules — which findings go back to whom, what a дозапрос may contain, when a ticket has failed instead, and what to do when the build proves the plan wrong — are in **`phases/5-repair.md`**, opened now and not before: most tickets return `DONE` and never need it.
7. **Commit** — one commit per ticket, the ticket number in the subject, and only now does the ticket become `done`. These are the user's rollback points.
8. **Update the instruments** (`phases/7-instruments.md`) — one line of state, one line of the dashboard: the ticket's `finishedAt`, tests and commit, the `requirements` counts, the `build` and `review` stage notes («3 из 5 тасков готовы»), `updatedAt`.
9. **Top up the project memory — only if something was discovered.** The real test command, a gotcha that cost time, a new variable in `.env.example`. One line appended between the markers, never a rewrite; the architecture is written once, at the end. Most tickets add nothing, and that is the correct rate. Rules in `phases/9-memory.md`.
10. **Tell the user one plain-language line**: «Бот принимает заявки — 3 из 8 готово». No diffs, no jargon, no file lists.

Steps 4 through 6 are where the run is usually lost. Done as written, one ticket costs you a verdict, thirty lines of test output and a contract block. Done by hand — «посмотрю дифф сам, тут же немного» — the same ticket costs you the diff, the test log and every file you opened to fix it, and you pay that eight times.

**Ten steps, but not ten writes to `state.js`.** The list is an order of operations, not a count of edits: batch the state changes the way a wave launch is already batched (`phases/0-instruments.md`). Two writes per ticket is the target — one when it goes to `review`, one at the commit that carries `finishedAt`, the tests, the counts and the stage notes together. Every extra write is a turn, and a turn costs the whole of your context re-read; nine tickets at six writes each is a hundred and thirty turns spent on bookkeeping, which on a T3 run is a quarter of everything you do. The user cannot see the difference — the screen follows either way — so the only thing the extra writes buy is the bill. **Everything batches except `startedAt`**, which is worthless in arrears: written together with `finishedAt` it gives the user a clock that never ran, on work that took twenty minutes (`phases/0-instruments.md`). It is the one write that has to happen when the thing starts.

**Steps 4–7 hold up the commit, not the crew.** The list is the order for *this* ticket; it is not a queue the rest of the flight waits in. The moment a ticket returns, the next launchable ticket goes out — and only then do you walk the list for the one that landed. Its review runs while the next ticket is being written, and the wall-clock cost of reviewing everything drops to roughly nothing.

**Step 4 is sent in the same breath as the launch, not at your convenience.** «Отправлю на ревью, как разгребу» costs twice over: the ticket sits finished-but-uncommitted while its dependents wait, and the reviewer you are keeping alive (`phases/6-review.md`) goes cold — woken after forty minutes it rebuilds its whole prefix at write prices instead of read prices. Measured on the run behind this section: the two reviewers were busy six percent of their lives and paid four to seven times the orchestrator's rate for the privilege of waiting.

So the front of the list is: **launch the next ticket, append `interfaces.md`, send the review** — and the manifest, the instruments and the user's line come after. Appending stays ahead of the review because `interfaces.md` is «the only way Reinvention is visible» (`phases/6-review.md`), and from the second ticket onward the reviewer is sent only what the file has grown since: send the review first and it judges this ticket against a map that does not contain it.

What this does not buy is a shortcut: the ticket is still committed only after its review and a green suite. Nothing lands unreviewed because something else was in flight; the review simply stopped being the thing everyone waits for. The one ordering that stays strict is a ticket whose dependents are pending — do not launch a dependent on an unreviewed parent, because a finding there invalidates the ground the dependent is standing on.

### When two tickets return together

Process them **one at a time, each through the whole list above**. Two returns are not one event.

- **One commit per ticket, always.** A shared commit takes away a rollback point the user paid for, and blames two tickets for one regression.
- **Run the full suite after each**, not once after both. Otherwise a red test has two possible authors and you have to bisect what you could simply have known.
- **`interfaces.md` is appended by you, in return order**, one block per ticket. Subagents never write to it — parallel writers collide.
- **Two returns claiming the same interface is a plan defect, not a merge problem.** It means the zones overlapped: keep the one that fits `interfaces.md`, and re-cut the other rather than reconciling two versions of the same thing by hand.

## Testing — who checks that the tests are worth anything

Not you, and not the executor. Reading assertions is the Craft reviewer's job, and the three questions it reads them with are written out in `prompts/craft-review.md` — the file that reviewer is handed by path. It is the review instruction most easily lost on the way down, because it looks like something a pass count already answered; handing over the file is what makes it arrive.

So your part is one move, and it is upstream: see that both files went down — `prompts/executor.md` with the executor, `prompts/craft-review.md` with the reviewer. Everything else about tests happens in those two contexts, not in yours.
