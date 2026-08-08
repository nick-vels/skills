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

**Ask what the brief actually leaves open — however many that is, including none.**

The count is an outcome, not a setting. A two-line brief about a marketplace can leave eight real forks; a careful brief for a landing page, with the copy already written and the stack named, can leave zero. Both are correct interviews. What is never correct is producing a question because a number implied there should be one: a manufactured question is answered badly, teaches the user that the interview is a formality, and spends the attention you will need for the one question that matters.

In priority order:

- **Every blocking unknown is asked, always.** Payment, hosting, accounts, where the data lives, an existing system to fit into. No count and no mode makes one of these skippable — an unasked blocking question costs the project far more than an extra question ever costs the user.
- **A fork only the user can settle is asked** when the two branches lead to visibly different products.
- **Everything else you decide yourself** and record it. Error wording, retry policy, sane defaults, naming, layout — that is craft, and Phase 3 is where it belongs.

  «Everything else» is narrower than it sounds, and getting the line wrong in this direction is the expensive mistake. A decision belongs back in the interview, not in your hands, if it **costs the user money or ties them to a vendor**, if it **changes what they see or what they can do**, if **undoing it later means rebuilding rather than editing**, or if it **encodes a rule about their business** — prices, deadlines, who may do what, what happens to someone's data. None of those are craft, however obvious the answer looks from here. When you cannot tell which side a decision falls on, that uncertainty *is* the signal: ask.
- **Nothing left open? Say so and go.** «Вопросов нет — в задаче всё однозначно, пишу спецификацию.» Mark the `briefing` stage `skipped` in `state.json` with the note «вопросов не потребовалось», so the user sees a decision rather than a step that quietly did not happen.

Most briefs land somewhere between two and eight questions. That is an observation about briefs, not a target for you — **and there is no ceiling any more than there is a floor.** A three-line brief for a marketplace, a project that has to fit into someone's existing system, a business with rules you cannot guess: fifteen questions there is not an interrogation, it is the cheapest part of the whole build. Ask them, and say once why there are so many — «задача большая и многое не определено, вопросов будет больше обычного». What makes a long interview bad is padding, never length.

In **manual** the same rules hold with more patience: keep going while genuine forks remain.

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
