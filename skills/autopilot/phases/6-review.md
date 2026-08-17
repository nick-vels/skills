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

## The reviewer outlives the ticket

**Do not spawn a new reviewer per ticket.** Keep one for Manifest+Spec and one for Craft, and send each subsequent ticket to the same pair by message. The setup — `interfaces.md`, the spec sections, the manifest rows, the repo's conventions — is most of what a review costs and almost none of what it produces. Paid once per crew, it is cheap. Paid once per ticket, it is the reason reviewing everything felt unaffordable in the first place.

The second gain is the one that is hard to buy any other way. A reviewer that saw ticket 02 can see that ticket 05 quietly contradicts it — a whole class of defect that no per-ticket reviewer can reach, because nothing in its inputs mentions ticket 02 at all. **This is the panoramic view the orchestrator used to have and can no longer afford**, relocated to the one context where accumulation is safe: a reviewer writes nothing, so a tired reviewer misses findings but cannot break the build, and unlike you it can be replaced.

- **Refresh it at wave boundaries, or whenever its judgement starts drifting** — repeating findings, hedging, reviewing the previous ticket instead of this one. A fresh reviewer rebuilds everything it needs from `interfaces.md`; the only thing lost is the cross-ticket memory, and that is exactly what has already gone stale.
- **Each reviewer keeps its own axes for the whole run.** Swapping which one holds Manifest halfway through gives you two reviewers with half a picture each.
- **The Craft reviewer is the one worth keeping longest.** Reinvention and divergent change are visible only to someone who remembers what the earlier tickets built.
- **If continuing a subagent is not available in the harness**, fall back to a fresh reviewer per ticket. It works; it just costs what this section exists to avoid, and the cross-ticket findings do not happen at all.

## What a reviewer gets

A reviewer knows nothing you do not hand it — the same rule as for an executor, and it bites harder here, because **axis Manifest is built entirely out of words the subagent has never seen.** A reviewer sent off with just the diff will quietly review two axes and report three.

| | Manifest + Spec | Craft |
|---|---|---|
| the diff — `git diff` over the ticket's range, or the files its contract block named | ✓ | ✓ |
| **the manifest rows the ticket names, with the verbatim brief quotes** | ✓ | — |
| the spec sections the ticket named — the same ones the executor got | ✓ | — |
| `interfaces.md` | ✓ | ✓ — the only way Reinvention is visible |
| the ticket body and its acceptance criteria | ✓ | ✓ |
| whatever the repo documents about how code is written | — | ✓ |
| **`prompts/craft-review.md`, by path** — the smells, the assertion-level testing check, the return format | — | ✓ |
| what it must not do: repair nothing, refactor nothing, open no files outside the diff to «понять получше» | ✓ | ✓ |

**Give each one only its own axes.** A reviewer handed material for an axis it was not asked to judge will judge it anyway, badly and without saying so — and two overlapping half-reviews are what the separation of axes exists to prevent.

**That table is the first ticket only.** A reviewer you are keeping (above) already holds the standing material; from the second ticket onward it gets the diff, the ticket body, this ticket's manifest rows, and whatever `interfaces.md` has grown since — nothing else. Resending what it already has is not harmless: it reads as new material, and a reviewer re-reading yesterday's interfaces as though they arrived today is how a ticket gets judged against the wrong contract.

**Give the Craft reviewer the path, and require it to read the file before the first diff.** A path is not a delivery: what makes the check exist is the reviewer having read it, so say so as a requirement and expect the return format from that file. If the harness gives you no way to have a subagent read a file, paste the contents once, into the first ticket's prompt only — the reviewer keeps them for the run.

### What a reviewer returns

```
AXIS: manifest | spec | craft
VERDICT: clean | findings
FINDINGS: <ось> · <файл:строка> · что не так · какое условие должно выполняться
          — одно предложение на находку, условием, а не пожеланием
BLOCKING: только требование не доставлено, выдуманный факт о пользователе,
          лишняя поверхность из спеки или красный прогон — и ничего больше.
          Нечего блокировать — пиши `нет`, это нормальный и частый ответ.
```

**Не больше 20 строк, без кусков кода и без диффа.** A finding phrased as a condition can be forwarded to the executor as a дозапрос unchanged; a finding phrased as «стоило бы аккуратнее» has to be rewritten by you before it can go anywhere, and rewriting it means reading the diff — which is the whole thing this arrangement exists to avoid.

**Tell the reviewer what `BLOCKING` costs, in its prompt.** It is not a severity rating for its own use: everything it lists there becomes a дозапрос plus a re-review, and everything it leaves out still reaches the user in the report. A reviewer that does not know this hedges upward — listing anything it feels strongly about — and the run pays a repair cycle per feeling.

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

**The whole of what this reviewer judges by is `prompts/craft-review.md`, and it goes down as a path, not as your retelling of it.** The list of smells, the assertion-level testing check and the return format live there because they are the subagent's material, not yours: an orchestrator that reads them keeps them until the end of the run and gains nothing, and an orchestrator that paraphrases them ships a weaker version of the check than the one that was written.

What stays here is the part you decide:

- Whatever the repo documents about how code is written **wins over that file** — hand the reviewer the repo's conventions too, and say which wins.
- Everything in it is a **judgement call** — "possible Feature Envy", never a hard violation — and anything tooling already enforces is out of scope: a linter finding is not a review finding.
- Three of its entries exist because subagents cause them — *Reinvention*, *Silent narrowing*, *Invented fact* — and the first is the reason the Craft reviewer gets `interfaces.md`. Without it that whole class of finding is invisible.
- The testing check in it is the line most often lost on the way down, because a pass count looks like it already answered the question. Handing over the file is what makes it arrive; nothing about it is checkable from the count.

## What to do with findings

**Every "fix" below happens in the ticket, not in the orchestrator and not in the reviewer.** A finding goes back to the executor that wrote the code, as a **дозапрос** stating the condition — `phases/5-repair.md`. The reviewer judged and is done; a reviewer that also repairs is a check that has stopped being one. Two дозапроса is the ceiling, after which the finding becomes a failed ticket and takes that path instead.

### `BLOCKING` decides, and it is a short list

**Only findings the reviewer put in `BLOCKING` hold up the commit.** That line exists in the return format for this and nothing else; a run that treats every finding as blocking has turned a three-line verdict into a repair queue, and it pays for that queue twice — once in the дозапрос, once in the re-review that follows it.

What is always blocking, no judgement involved:

- **Manifest `partial` or `missing`** — a requirement the user asked for is not delivered. This is the one category no ослабление ever touches: the whole framework exists to catch it, and «поправим потом» is how it stops being caught.
- **Craft *invented fact*** — a plausible-looking price, address or text standing where the user's own fact belongs. It ships as truth if it ships at all.
- **Spec *extra*** that adds surface nobody asked for — removed, unless the rest genuinely needs it, and then one line in the commit message says so.
- **A red suite.** Nothing is committed on red, ever.

Everything else — Craft judgement calls, style, structure, a test set that is bigger than its seams — goes to `state.js` under `concerns` with its file and line, and travels to the final report. **It is not a дозапрос and does not delay the commit.**

**This is a deliberate loosening, and here is what it costs.** Deferred findings accumulate, and a list nobody reads is a silent discard — so the list has one reader by construction: the whole-project pass in `phases/8-final.md` triages it, and what it decides is worth fixing becomes a ticket like any other, reviewed and committed the same way. What is not fixed is named in the report. The alternative — repairing every judgement call inside the ticket that surfaced it — was measured at thirteen repairs across nine tickets, each adding roughly forty percent to its ticket's clock, for findings that were mostly not what the run was at risk from.

**Structural findings were already exempt** («if it is structural, note it in `concerns`») — this rule keeps that exemption and stops relying on «small and local», which is the phrase that quietly pulled everything back into the loop.

### The re-review is scoped to the fix

When a дозапрос comes back, **review the fix, not the ticket again.** Send the reviewer the diff of the repair alone and the list of findings it was supposed to close; it verdicts each one addressed or not, and flags new breakage inside the fix only. Re-reading the whole ticket costs what the first review cost and re-derives a verdict you already have — and it is how a two-round ceiling turns into an evening.

Refactoring belongs here, not inside the red-green loop. Cleaning up while chasing a failing test is how both jobs get done badly.

## Reporting

To yourself, structured, per axis. **To the user, nothing** — unless something is being carried to the final report as a concern. The user gets one plain line per ticket from Phase 5, not a review.
