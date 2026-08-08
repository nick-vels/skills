# Phase 2 — Briefing

The only phase where the user is needed in semi mode. Its job is not to collect wishes — it is to **close the requirements that cannot be built as written**.

The manifest already exists. Every question here exists to move a row in it.

## The rules of the interview

**One question at a time.** Wait for the answer before asking the next. A wall of questions is bewildering and gets answered badly, which is worse than not asking.

**Every question names its requirement.** Internally, each question is «this asks about R07». A question that closes no row is a question you invented for your own comfort — drop it.

**Recommend an answer with every question.** «Заявки складывать в Google-таблицу или сразу в базу? Я бы взял таблицу — тебе её видно и не нужен сервер.» The user can accept in one word. Never ask an open question where a recommended default would do.

**Look facts up, ask only decisions.** Anything discoverable in the filesystem, the repo, or a tool is not a question. What stack the repo already uses is a fact. What payment provider the user has an account with is a decision.

**Blocking unknowns go first.** Payment, hosting, which accounts already exist, where data lives, who the user is authenticated as — these decide the shape of everything. In the first three questions, never at the finish line. A payment question asked at the end costs half the project.

**Decisions, never secrets.** *Which* provider, *whether* an account exists — yes. The key, the token, the password, the connection string — never. If the user volunteers one anyway, the redaction gate in `phases/1-manifest.md` handles it.

**Never answer for the user.** No silent assumptions, no invented content. Forced past an unknown → mark the row `placeholder` and move on. In **full** mode decisions do get made for the user — labelled, never silent. See below.

**Usually five to eight questions in semi** — that is what an interview costs, not a quota to fill or a wall to stop at. Stop the moment the remaining unknowns are cosmetic, even at three; an extra question is not free, it is the user's attention. And if a brief genuinely carries more blocking unknowns than eight — several external services, an existing system to fit into — ask them and say why in one line. An unasked blocking question costs the project more than an extra question ever costs the user. In **manual** there is no cap at all.

## What to ask about

In priority order. Ask only what is actually unresolved for *this* brief; skip anything the brief already settled.

1. **Blocking externals** — payment, hosting, domain, third-party accounts, existing data to import.
2. **Implicit requirements** (`R##i` rows) — the things the brief assumed. «Заявки будут падать в таблицу — тебе нужен ещё экран, чтобы их смотреть, или таблицы хватит?» These are the rows most likely to sink the project silently.
3. **Depth the user alone can settle.** The brief describes the happy path; the interesting decisions live under it. Some of those are craft and you decide them yourself in Phase 3 — error wording, retry policy, defaults. Others are genuinely the user's preference, and those are among the best questions you can spend a slot on: «Клиент отменил заявку через час — деньги возвращаем сами или мастер решает?» A question like this buys a whole branch of the spec that would otherwise be guessed.

   At **deep** depth these questions come first, right after the blocking externals. At **strict** they narrow to clarifying what the user already said — never to offering them something extra.
4. **Untestable requirements** — «красиво», «удобно», «быстро». Turn one into something checkable, or accept it as a matter of taste and record that. Do not spend three questions here.
5. **Contradictions inside the brief** — quote both halves and ask which wins.
6. **Scope edges** — what is explicitly *not* needed. Answers here become `dropped` rows and save whole tickets.

## Recording answers

After each answer, update the manifest row immediately — not at the end of the interview.

- Answer resolves a requirement → note the decision in Основание.
- Answer **cancels** a requirement → `dropped`, with the user's own words quoted. This is the only path to `dropped`, and it is why the answers are recorded verbatim (after redaction).
- Answer raises something new → **a new row**, `G##`, quoting the user's phrasing. This is the only phase where the manifest grows on the user's words. Afterwards it grows for exactly one reason — a `D##` row for something the build proved, per `phases/5-subagents.md` — and never for an idea of yours.
- Answer is «не знаю» → `placeholder`, and the build gets a stub with a visible label.

## Full mode — the self-briefing

**No interview happens.** The `briefing` stage in `state.json` is marked `skipped` with the note «полный автомат — самобрифинг», not left `pending`: the user has to see that the step was a decision, not a stall.

Run the same checklist against yourself and write the answers into the manifest, each labelled by kind. The line between the two kinds is the whole discipline of this mode:

**Decisions are yours to make.** Stack, structure, provider, data model, layout. Pick the option that runs on the user's own machine **without a third-party account and without money**, and record it as `ASSUMPTION — принято за пользователя: …` in the manifest's Основание column. Every one of these is a required line in the Phase 8 report — the user never asked for them and has the right to see all of them in one place.

**Facts about the user are not yours to invent.** Their prices, texts, addresses, business rules, accounts, brand colours. These become `placeholder` in the manifest, visibly labelled filler in the code (`[ЦЕНА — впиши]`, not `4990 ₽`), and a line in the final report. A plausible invented price is worse than an obvious blank: the blank gets fixed, the price gets shipped.

**A paid or account-bound service becomes an adapter, not a guess.** One interface, a local stub behind it, the real credential an empty variable name in `.env.example`. The user swaps the stub for the real thing when they have the account — the build does not wait for it and does not pretend to have it.

## Manual mode

Same rules, no cap. Keep asking until nothing blocking remains, then say so plainly: «Вопросов больше нет, пишу спецификацию».

## Closing

Before leaving this phase, check **gate G1**: every manifest row has a status; nothing is `open` without a recorded reason. Then announce the transition in one line — «Понял. Пишу спецификацию» — and go to Phase 3.

Do not summarise the interview back to the user. The manifest holds it, and the spec is about to say it better.
