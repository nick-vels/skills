"""Тесты skills/autopilot/tools/ap.py — учёта прогона Autopilot.

Запуск из корня репозитория:  python3 -m unittest discover -s tests
Каждый тест поднимает временный git-репозиторий с .autopilot/ и зовёт ap.py
как оркестратор — отдельным процессом, без сервера (--no-serve).
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(os.path.dirname(HERE), "skills", "autopilot")
AP = os.path.join(SKILL, "tools", "ap.py")
TEMPLATE = os.path.join(SKILL, "phases", "dashboard-template.html")

MANIFEST = """# Манифест требований

| ID | Из брифа (дословно) | Статус | Основание | Где |
|----|---------------------|--------|-----------|-----|
| R01 | «принимает заявки» | in-spec | — | spec §2 |
| R02 | «складывает в таблицу» | in-spec | — | spec §4 |
| R03 | «SMS» | dropped | «не надо» | — |
| R05 | «цвета студии» | in-spec | — | spec §6 |
"""


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def ticket(tid, title, reqs, deps, zone, wave, review="нет", model="обычная"):
    return ("# %s — %s\n\n**Требования:** %s\n**Зависит от:** %s\n**Зона:** %s\n"
            "**Волна:** %s\n**Ревью:** %s\n**Модель:** %s\n\n## Критерии приёмки\n\n- [ ] что-то\n"
            % (tid, title, reqs, deps, " · ".join("`%s`" % z for z in zone), wave, review, model))


class Run(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-test-")
        self.git("init", "-q")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")
        self.a = os.path.join(self.root, ".autopilot")
        os.makedirs(self.a)
        shutil.copy(TEMPLATE, os.path.join(self.a, "dashboard.html"))
        shutil.copy(AP, os.path.join(self.a, "ap.py"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), capture_output=True, text=True)

    def ap(self, *args):
        env = dict(os.environ, AUTOPILOT_NO_UPDATE_CHECK="1")
        r = subprocess.run([sys.executable, os.path.join(self.a, "ap.py")] + list(args) + ["--no-serve"],
                           capture_output=True, text=True, env=env, cwd=self.root)
        return r.returncode, r.stdout

    def state(self):
        raw = read(os.path.join(self.a, "state.js"))
        return json.loads(raw.split("=", 1)[1])

    def stage(self, sid):
        return next(s for s in self.state()["stages"] if s["id"] == sid)

    def init(self):
        code, out = self.ap("init", "--slug", "repair-bot", "--title", "Бот", "--skill-dir", SKILL)
        self.assertEqual(code, 0, out)
        self.dir = os.path.join(self.a, self.state()["dir"])
        return out

    def write(self, rel, text):
        path = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def manifest(self):
        return read(os.path.join(self.dir, "manifest.md"))

    # ── init ───────────────────────────────────────────────────────────────
    def test_init_creates_run(self):
        self.init()
        s = self.state()
        self.assertTrue(re.match(r"\d{4}-\d{2}-\d{2}-repair-bot--wip$", s["dir"]))
        self.assertTrue(os.path.isdir(os.path.join(self.dir, "tickets")))
        self.assertEqual([x["status"] for x in s["stages"]], ["active"] + ["pending"] * 7)
        self.assertRegex(s["startedAt"], r"T\d\d:\d\d:\d\d[+-]\d\d:\d\d$")
        self.assertIn("в работе", read(os.path.join(self.a, "README.md")))
        self.assertIn(".autopilot/serve.*", read(os.path.join(self.root, ".gitignore")))
        self.assertIn("window.STATE={", read(os.path.join(self.a, "dashboard.html")))

    def test_init_refuses_on_live_run(self):
        self.init()
        code, out = self.ap("init", "--slug", "other")
        self.assertNotEqual(code, 0)
        self.assertIn("продолжение", out)

    def test_init_archives_finished_run(self):
        self.init()
        first = self.state()["dir"]
        self.ap("finish", "--result", "готово")
        code, out = self.ap("init", "--slug", "second")
        self.assertEqual(code, 0, out)
        self.assertTrue(os.path.exists(os.path.join(self.a, first.replace("--wip", ""), "state.js")))
        self.assertTrue(self.state()["dir"].endswith("second--wip"))

    # ── stages ─────────────────────────────────────────────────────────────
    def test_opening_a_stage_closes_the_previous(self):
        self.init()
        self.ap("stage", "manifest")
        self.assertEqual(self.stage("preflight")["status"], "done")
        self.assertEqual(self.stage("manifest")["status"], "active")

    def test_review_closes_build(self):
        self.init()
        self.ap("stage", "build")
        self.ap("stage", "review")
        self.assertEqual(self.stage("build")["status"], "done")

    def test_passed_stage_with_artifact_is_marked_done(self):
        self.init()
        self.write("manifest.md", MANIFEST)
        code, out = self.ap("stage", "spec")
        self.assertEqual(self.stage("manifest")["status"], "done")
        self.assertIn("briefing", out)                     # ни файла, ни отметки — подсказка
        self.assertEqual(self.stage("briefing")["status"], "pending")

    def test_skip_needs_a_reason(self):
        self.init()
        code, _ = self.ap("stage", "briefing", "skip")
        self.assertNotEqual(code, 0)
        self.ap("stage", "briefing", "skip", "--note", "полный автомат — самобрифинг")
        self.assertEqual(self.stage("briefing")["status"], "skipped")

    # ── tickets and the manifest ───────────────────────────────────────────
    def plan(self):
        self.init()
        self.write("manifest.md", MANIFEST)
        self.write("tickets/01-karkas.md", ticket("01", "Каркас", "R01, R05", "—", ["src/core/"], 1, "да — фундамент", "сильная"))
        self.write("tickets/02-priem.md", ticket("02", "Приём", "R01.1, R02, A01", "01", ["src/bot/"], 2))

    def test_tickets_publish_and_move_rows_in_ticket(self):
        self.plan()
        code, out = self.ap("tickets")
        t = {x["id"]: x for x in self.state()["tickets"]}
        self.assertEqual(t["02"]["requirements"], ["R01.1", "R02", "A01"])
        self.assertEqual(t["02"]["blockedBy"], ["01"])
        self.assertEqual(t["01"]["zone"], ["src/core/"])
        self.assertEqual(t["01"]["review"], "да — фундамент")
        self.assertEqual(t["02"]["status"], "pending")
        m = self.manifest()
        self.assertRegex(m, r"\| R01 \|[^\n]*\| in-ticket \|[^\n]*T01, T02")
        self.assertRegex(m, r"\| R03 \|[^\n]*\| dropped \|")
        self.assertEqual(self.state()["requirements"]["inTicket"], 3)

    def test_check_plan_passes_a_sound_plan(self):
        self.plan()
        code, out = self.ap("check-plan")
        self.assertIn("G3: трасса сходится", out)

    def test_check_plan_catches_defects(self):
        self.plan()
        self.write("tickets/03-tablica.md", ticket("03", "Таблица", "R02", "02", ["src/bot/sheets/"], 2))
        self.write("tickets/04-nichei.md", ticket("04", "Ничей", "", "—", [], 1))
        code, out = self.ap("check-plan")
        self.assertIn("в волне 2, но его зависимости позволяют не раньше 3", out)
        self.assertIn("таски 02 и 03 в одной волне пишут в src/bot/sheets/", out)
        self.assertIn("таск 04 ни к чему не привязан", out)
        self.assertIn("у таска 04 нет зоны", out)

    def test_check_plan_catches_a_requirement_in_no_ticket(self):
        self.plan()
        self.write("manifest.md", MANIFEST + "| G01 | «отмена» | in-spec | — | spec §5 |\n")
        code, out = self.ap("check-plan")
        self.assertIn("требование G01", out)

    def test_done_closes_rows_only_when_all_their_tickets_are_done(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "start")
        self.ap("ticket", "01", "done", "--tests", "3/0", "--commit", "1111111aaaa", "--placeholder", "R05")
        m = self.manifest()
        self.assertRegex(m, r"\| R01 \|[^\n]*\| in-ticket \|")     # ещё и в таске 02
        self.assertRegex(m, r"\| R05 \|[^\n]*\| placeholder \|[^\n]*1111111")
        self.ap("ticket", "02", "start")
        self.ap("ticket", "02", "done", "--tests", "5/0", "--commit", "2222222bbbb")
        m = self.manifest()
        self.assertRegex(m, r"\| R01 \|[^\n]*\| done \|")
        self.assertRegex(m, r"\| R02 \|[^\n]*\| done \|")
        s = self.state()
        self.assertEqual(s["requirements"]["done"], 2)
        self.assertEqual(s["requirements"]["placeholder"], 1)
        self.assertEqual(s["tests"], {"passed": 5, "failed": 0})

    def test_ticket_lifecycle_counters(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "02", "start")
        self.ap("ticket", "01", "review")
        self.ap("ticket", "01", "repair", "--note", "ключ схемы — R01")
        self.ap("ticket", "02", "retry")
        t = {x["id"]: x for x in self.state()["tickets"]}
        self.assertEqual(t["01"]["status"], "repair")
        self.assertEqual(t["01"]["repairs"], 1)
        self.assertEqual(t["01"]["repairFindings"], ["ключ схемы — R01"])
        self.assertEqual(t["02"]["retries"], 1)
        self.assertTrue(t["02"]["startedAt"])
        self.ap("ticket", "02", "reset")
        t = {x["id"]: x for x in self.state()["tickets"]}
        self.assertEqual(t["02"]["status"], "pending")
        self.assertNotIn("startedAt", t["02"])

    def test_unknown_ticket_is_an_error(self):
        self.plan()
        self.ap("tickets")
        code, out = self.ap("ticket", "09", "start")
        self.assertNotEqual(code, 0)

    def test_escaped_pipe_in_a_quote(self):
        self.init()
        self.write("manifest.md", MANIFEST.replace("«складывает в таблицу»", "«таблица \\| или база»"))
        self.write("tickets/01-a.md", ticket("01", "A", "R01, R02, R05", "—", ["a/"], 1))
        self.ap("tickets")
        self.assertRegex(self.manifest(), r"\| R02 \| «таблица \\\| или база» \| in-ticket \|")

    def test_d_rows_are_constraints_not_requirements(self):
        self.plan()
        self.write("manifest.md", MANIFEST + "| D01 | схема не держит два адреса | in-spec | таск 02 | spec §3 |\n")
        code, out = self.ap("check-plan")
        self.assertNotIn("D01", out)
        self.assertEqual(self.state()["requirements"]["total"], 4)

    def test_dependencies_accept_a_t_prefix(self):
        self.plan()
        self.write("tickets/03-c.md", ticket("03", "C", "R02", "T1, T02", ["c/"], 3))
        self.ap("tickets")
        t = {x["id"]: x for x in self.state()["tickets"]}
        self.assertEqual(t["03"]["blockedBy"], ["01", "02"])

    def test_empty_tickets_dir_does_not_pass_the_plan(self):
        self.init()
        self.write("manifest.md", MANIFEST)
        self.ap("stage", "build")
        self.assertEqual(self.stage("plan")["status"], "pending")
        self.write("tickets/01-a.md", ticket("01", "A", "R01", "—", ["a/"], 1))
        self.ap()
        self.assertEqual(self.stage("plan")["status"], "done")

    # ── lists and numbers ──────────────────────────────────────────────────
    def test_add_set_and_numbers(self):
        self.init()
        self.ap("add", "concerns", "src/x.ts:4 — два формата даты")
        self.ap("add", "debt.emptyEnv", "TELEGRAM_BOT_TOKEN")
        self.ap("add", "debt.emptyEnv", "TELEGRAM_BOT_TOKEN")      # без дублей
        self.ap("set", "tier=T2", "baseCommit=abc1234")
        self.ap("coverage", "found=2", "fixed=1", "deferred=1", "--item", "R07 — отложено")
        self.ap("add", "report", "два формата даты", "лишний отступ")
        self.ap("blind", "checked=4", "matched=3", "--mismatch", "R02 — не видно")
        s = self.state()
        self.assertEqual(s["concerns"], ["src/x.ts:4 — два формата даты"])
        self.assertEqual(s["debt"]["emptyEnv"], ["TELEGRAM_BOT_TOKEN"])
        self.assertEqual((s["tier"], s["baseCommit"]), ("T2", "abc1234"))
        self.assertEqual(s["coverage"], {"found": 2, "fixed": 1, "deferred": 1, "items": ["R07 — отложено"]})
        self.assertEqual(s["report"], ["два формата даты", "лишний отступ"])
        self.assertEqual(s["blind"], {"checked": 4, "matched": 3, "mismatches": ["R02 — не видно"]})

    def test_every_event_leaves_a_beat(self):
        # updatedAt перезаписывается; журнал хранит каждое событие, чтобы рабочее
        # время считалось и тогда, когда дашборд их не видел (сон, мёртвый сервер)
        self.init()
        first = self.state()["beats"]
        self.assertEqual(first, [self.state()["startedAt"]])
        self.ap("add", "report", "раз")
        self.ap()                                   # синхронизация — не событие
        s = self.state()
        self.assertEqual(s["beats"][-1], s["updatedAt"])
        self.assertLessEqual(len(s["beats"]), 2)
        self.assertEqual(s["beats"], sorted(set(s["beats"])))

    # ── finish ─────────────────────────────────────────────────────────────
    def test_finish_lands_the_run(self):
        self.plan()
        self.git("add", "-A")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "run")
        code, out = self.ap("finish", "--result", "Бот принимает заявки")
        s = self.state()
        self.assertTrue(s["finishedAt"])
        self.assertFalse(s["dir"].endswith("--wip"))
        self.assertTrue(os.path.isdir(os.path.join(self.a, s["dir"])))
        self.assertTrue(all(x["status"] in ("done", "skipped") for x in s["stages"]))
        self.assertIn("| сдан | Бот принимает заявки |", read(os.path.join(self.a, "README.md")))
        self.assertIn("R", self.git("status", "--short").stdout)    # переименование через git mv

    def test_reopen_puts_wip_back(self):
        self.init()
        self.ap("finish", "--result", "готово")
        self.ap("reopen")
        s = self.state()
        self.assertTrue(s["dir"].endswith("--wip"))
        self.assertIsNone(s["finishedAt"])
        self.assertEqual(self.stage("manifest")["status"], "active")
        self.assertEqual(self.stage("final")["status"], "pending")
        self.assertNotIn("finishedAt", self.stage("final"))


class Pure(unittest.TestCase):
    """Функции без процесса: опознание своего сервера и версия навыка."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("ap", AP)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_is_ours(self):
        a = self.m.A
        self.assertTrue(self.m.is_ours("/usr/bin/python3 -m http.server 8000 --bind 127.0.0.1 --directory %s" % a))
        self.assertFalse(self.m.is_ours("python3 -m http.server 8000 --directory %s2" % a))
        self.assertFalse(self.m.is_ours("node http-server --directory %s" % a))

    def test_version(self):
        self.assertEqual(self.m._version('---\nname: x\nmetadata:\n  version: "2.0.1"\n---\nversion: 9'), (2, 0, 1))
        self.assertIsNone(self.m._version("---\nname: x\n---\nversion: 3\n"))

    def test_skill_declares_a_version(self):
        text = read(os.path.join(SKILL, "SKILL.md"))
        self.assertIsNotNone(self.m._version(text))


if __name__ == "__main__":
    unittest.main()
