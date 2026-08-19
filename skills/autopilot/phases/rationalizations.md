# Rationalizations and Red Flags — the catalogue

**Read this file at three moments, and not otherwise:** when a gate fails (G1–G4), when you catch yourself building an argument for skipping something, and once before writing the final report. It is a checklist, not an instruction — nothing here tells you how to do a phase, and everything here tells you how a phase goes wrong.

The five rules that never lose are in `SKILL.md` and stay there. This is the long tail.

## Rationalizations — the ones that cost the user the product

Phase-specific mechanics are not here; they live in the phase that owns them. What follows is the short list of excuses that end with the user getting something other than what they asked for.

| Excuse | Reality |
|--------|---------|
| «Пользователь сказал не задавать вопросов» | Он сказал не задавать ЛИШНИХ. Решающие вопросы — часть работы, не обсуждение процесса. |
| «KISS — просто собери» | Простой результат даёт порядок, а не пропуск этапов. Без спецификации каждая правка — «а я имел в виду другое». |
| «Бриф весь в диалоге, зачем его переписывать в файл» | Диалог сжимается, и бриф в нём — самое старое. Через три фазы ты будешь синтезировать по пересказу пересказа. |
| «Требование неважное» / «он про это больше не вспоминал — значит, отменил» | Важность определяет пользователь, а молчание не отменяет. Предложить `deferred` можешь ты; вычеркнуть — только он, своими словами, цитатой в манифест. |
| «Он передумал по ходу — поправлю манифест, бриф трогать нельзя» | Нельзя переписывать сказанное, а дописывать сказанное позже — обязательно: `## Дополнения`, дословно, с датой. Манифест — твоё прочтение, и обе независимые проверки его не видят. Изменение, дошедшее до манифеста и не дошедшее до брифа, для G2 и G4 не существует. |
| «Новое пожелание посреди сборки — брифинг уже кончился, оформлю как `D##`» | `D##` — то, что доказала сборка. Слова пользователя — всегда `G##`, в любой фазе, плюс строка в «Дополнения» и вслух: беру таском, откладываю или в отчёт. Принятое молча — срок, о котором он не договаривался. |
| «Сделаю заглушку, уточнит потом» | Блокирующие неизвестные (оплата, хостинг, аккаунты) решаются в брифинге — в полном автомате в self-briefing, — но всегда до билда. |
| «Пусть пришлёт ключ, я вставлю» / «ключ уже в контексте — значит, можно записать» | Ключи вставляет пользователь и только в `.env`; ты работаешь с именем переменной. Ключ, оказавшийся в контексте, — повод отредактировать и предупредить, а не разрешение. |
| «Быстрее всё сделать в одном контексте» | Быстрее в первый час. Дальше модель ходит кругами и ломает работавшее. |
| «Исполнитель не смог — доделаю сам, я же в контексте» / «тут правки на две строки, гонять субагента дороже» | Дороже этому таску — платят все следующие. Твой контекст тратится один раз и не возвращается: правка твоими руками лежит в нём до конца сборки. Не смог — дозапрос ему или свежий контекст, но не твоя клавиатура. |
| «Бриф краткий — значит, и спецификация краткая» | Бриф — силуэт: пользователь описал happy path и не описал ни пустых состояний, ни ошибок, ни обрывов. На нормальной и максимальной глубине продумать их — твоя работа. |
| «Это и так очевидно, писать не буду» | Очевидное тебе — не зафиксировано, и каждый субагент додумает его по-своему: три исполнителя — три разные «очевидности». Манифест и спецификация — единственные точки сверки. |
| «Придумал полезную фичу, добавлю» | Углубление заказанного (`R##.n`) — да. Новая возможность (`A`) — только с родительским требованием, в пределах пропорции и в отчёт. На `strict` — нельзя вообще. |
| «Полный автомат — значит можно и задеплоить» | Автомат снимает вопросы о продукте, а не право на необратимое. Деплой, оплата, рассылка, удаление — гейт во всех режимах. |
| «В полном автомате можно додумать за пользователя всё» | Решения — да, и все в ASSUMPTIONS. Факты о пользователе (цены, тексты, аккаунты) — нет: заглушка и строка в отчёте. |
| «Напишу "запускаю через 60 секунд"» | Ты не умеешь ждать — обещанной паузы не будет. Честная формулировка: «начинаю, скажи стоп». |
| «В ручном режиме тоже начну и подожду возражений» | В ручном согласование — это явное «ок». Молчание им не является, начатая работа тем более. |
| «Сверю со спецификацией, этого хватит» / «покрытие проверю сам — я же её и писал» | Тот, кто писал, не видит, чего не написал, а спецификация может уже потерять требование. На G2 и G4 читает субагент — по брифу, без спеки и без манифеста, — иначе проверка подтверждает собственную ошибку. |
| «Правило про тесты записано в фазе — значит, оно действует» | Действует только то, что доехало в промпт исполнителя. Фазовый файл читает оркестратор, а код пишет не он. |
| «Интерфейсы устаканятся по ходу — первый таск задаст» | Тогда их задаст тот, кто видел одну восьмую задачи. Границы модулей решаются до нарезки, иначе восемь контекстов договариваются задним числом. |
| «Отчёт напишу по памяти — я же всё это и делал» | К восьмой фазе твой контекст самый загрязнённый за весь прогон. Отчёт собирается из `manifest.md` и `state.js`, перечитанных с диска. |
| «Обоснования решений останутся в спецификации» | Спецификация умирает вместе с прогоном. То, что должно пережить его, уходит в ADR — иначе следующая сессия переоткроет те же решения. |
| «Пользователь сказал "погриль меня" — покажу и спецификацию» | Режим интервью покупает вопросы, а не гейты. Гейты — это «ручной режим», и это отдельное слово, которое он не сказал. |
| «Таски и спецификация видны в чате — зачем файлы» | Файл в `.autopilot/` и есть артефакт; чат — только его пересказ. Диалог умрёт, файлы останутся. |
| «Пользователь не спрашивал про режимы — не буду грузить» | Он и не спросит: в чате нет `--help`. Пять строк в начале — единственное место, где он вообще узнаёт, что у сборки есть ручки. |
| «Просил вылизать — критик разберётся, с чем сравнивать» | Не разберётся: он придумает эталон и погонит сборку к нему. Нет эталона от пользователя — доводка не запускается, и это ответ, а не отказ. |
| «Круг доводки нашёл мелочь — поправлю сам, это же не таск» | Тогда правка идёт без ревью, без зелёного прогона и без точки отката. Доводка — это ещё таски, а не право взять клавиатуру. |
| «Критик всё ещё недоволен — значит, рано останавливаться» | Он будет недоволен всегда: ему за это и платят. Остановка — это отсутствие находок, потолок кругов или слово пользователя. |
| «Проект собран, тесты зелёные — значит, работает» | Тесты писал тот же процесс, что и код. Пока проект никто не запустил, «работает» — это гипотеза, а первым его запустит пользователь. |
| «Таск большой, но я его дотяну в одном контексте» | Дотянешь — и заплатишь за это квадратом: потолок в `phases/5-subagents.md` существует именно потому, что «ещё немного» стоит больше, чем передача эстафеты. |

## Red Flags — start the phase over

Every line here means something the user asked for is at risk. Phase mechanics — instruments, timestamps, wave bookkeeping, memory-file detection — are checked in the phase files that own them, not here.

- Writing code before the spec exists.
- The brief was never written to its file — the run is anchored to nothing.
- A requirement left the manifest without a status, or was marked `dropped` without a quote of the user saying so.
- Past gate G3: a ticket that traces to no requirement, or a requirement that traces to no ticket.
- Spec or tickets that exist only in the dialogue — nothing written under `.autopilot/`.
- Instruments that disagree with the chat: a stage still `active` after you moved on, a ticket running while the dashboard calls it `pending`, a ticket carrying the run's `startedAt` instead of its own, timestamps filled in afterwards from memory. The user believes the screen over your sentences, which is the whole reason it exists.
- The announced depth and the actual spec diverge: a bare restatement of the brief at normal or deep, or an invented capability — any `A##` — at strict.
- G2 or G4 judged by you instead of by a subagent: your own reading of your own spec, or a final acceptance measured against the spec rather than blind against the brief.
- A blind checker, coverage checker or memory subagent handed `spec.md`, the manifest or the tickets — or left free to open `.autopilot/` for itself. Independence is the entire mechanism; without it each confirms the plan instead of the thing.
- The final report composed from memory instead of from `manifest.md`, `state.js` and the two subagents' returns, re-read from disk.
- A T2+ run that ended with no ADR: every `D##` and every load-bearing implementation decision left to die with `.autopilot/`.
- The finished project was never actually run — accepted on green tests and a reading of the code.
- Starting without announcing mode and depth, or announcing one and behaving as another: questions in full, a spec put up for approval in interview, a start-and-see instead of «ок» in manual.
- With `polish` on: a доводка round run against no reference, its findings applied outside the ticket path, a fourth round, or a round that broke something and was patched instead of reverted.
- A comparable in `reference.md` that the user never named — your taste entered as though it were theirs, and everything downstream now judges the build against it.
- The adversarial pass skipped in `interview` because the brief «выглядел продуманным» — or used to argue the user out of a requirement instead of into a decision.
- A blocking unknown — payment, hosting, an account, where the data lives — left unasked in semi, interview or manual because the brief «выглядел понятным». Asking nothing is legitimate only when nothing is open; a manufactured question and a skipped blocking one are both defects, in opposite directions.
- Promising the user a wait — a countdown, «через минуту», «если не ответишь за N секунд» — that you have no way to honour.
- In full: an invented fact about the user standing where an ASSUMPTION, a stub, or a PLACEHOLDER belongs.
- Asking the user a process question — which tracker, which doc file, which memory file, ticket granularity, code review — outside manual, where spec and tickets are gates by design.
- A requirement quietly narrowed to whatever happened to work, or the spec amended mid-build with no `D##` row recording why.
- Two tickets in one subagent context, or two tickets in one commit.
- The orchestrator editing a file outside `.autopilot/`: a fix «на две строки», a red test, a review finding applied by hand instead of sent down. One such edit is the whole failure — the diff stays in its context for the rest of the run.
- A ticket's diff, or the raw output of a full test run, read into the orchestrator's context. It needs a verdict and the names of what failed, not the material.
- A repair started from an empty context when the ticket's own executor was still reachable — or the mirror failure, a third дозапрос into an executor that has already failed to do it twice.
- Parallel subagents editing the same files — or the mirror failure, independent tickets flown one at a time with the plan's parallelism thrown away in the delivery.
- A subagent launched without `interfaces.md`, or finishing without returning the contract block.
- The first wave launched with `interfaces.md` still empty — module boundaries left for whichever ticket happens to reach them first.
- A subagent prompt with no testing rules or no context ceiling in it: the discipline written in the phase file the orchestrator reads, and absent from the handoff to the one who writes the code.
- A ticket relayed to a fresh context on a red suite, or a relay whose handoff file has no `РЕШЕНИЯ` / `ТУПИКИ` / `ДАЛЬШЕ` — the successor then rebuilds what was already ruled out.
- A resume that reset a ticket with `handoffs > 0` to `pending`, throwing away the written seam and re-running the longest ticket of the flight from zero.
- Payment, hosting, or accounts first mentioned at the finish line.
- A secret value asked for, repeated back, or written into any file, prompt, commit, or report.
- Installing a package or fetching remote code without the user asking for it.
- Text outside the `autopilot` markers edited, moved or dropped, or the run ending with no project memory file at all.
