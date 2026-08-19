#!/usr/bin/env python3
"""Зеркалит state.js в саму страницу дашборда и держит сервер живым.

Вызывается после каждой правки .autopilot/state.js — одной строкой, без аргументов:

    python3 .autopilot/sync.py

Делает ровно три вещи, в этом порядке:

  1. Проверяет, что state.js разбирается. Битый файл не идёт дальше: снимок на
     странице остаётся прежним, а не затирается мусором.
  2. Вписывает состояние внутрь dashboard.html между маркерами — атомарно, через
     временный файл рядом. Оборвётся на середине — на месте останется целая
     прежняя страница. Отсюда дашборд показывает данные, даже когда его открыли
     файлом, из панели через data:, с мёртвым сервером или через месяц после
     прогона.
  3. Смотрит, жив ли статический сервер этого прогона, и поднимает на прежнем
     порту, если нет. Прежний порт — чтобы ссылка, которую пользователь уже
     скопировал, продолжала работать.

Ничего не печатает в чат сама по себе: одна строка на stdout, её видит агент.
"""

import json
import os
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.request

A = os.path.dirname(os.path.abspath(__file__))          # .autopilot этого прогона
STATE = os.path.join(A, "state.js")
PAGE = os.path.join(A, "dashboard.html")
PIDF = os.path.join(A, "serve.pid")
LOG = os.path.join(A, "serve.log")
BEGIN, END = "/*STATE-BEGIN*/", "/*STATE-END*/"


def fail(msg):
    print(msg)
    sys.exit(1)


def read_state():
    try:
        raw = open(STATE, encoding="utf-8").read()
    except FileNotFoundError:
        fail("state.js ещё нет — снимок не вписан, сервер не тронут")
    body = raw.split("=", 1)[1] if "=" in raw.split("\n", 1)[0] else raw
    try:
        return json.loads(body.strip().rstrip(";"))
    except json.JSONDecodeError as e:
        # Здесь и был режим отказа «файл помялся»: раньше он был виден только по
        # пустой странице, теперь — строкой с номером строки, сразу после записи.
        fail("state.js не разбирается (строка %d: %s) — снимок оставлен прежним" % (e.lineno, e.msg))


def write_snapshot(state):
    """Снимок внутрь страницы. Возвращает текст для отчёта."""
    try:
        page = open(PAGE, encoding="utf-8").read()
    except FileNotFoundError:
        return "страницы нет — перекопируй dashboard.html из навыка"
    i, j = page.find(BEGIN), page.find(END)
    if i < 0 or j < 0:
        return "страница без маркеров снимка — перекопируй dashboard.html из навыка"
    # </ внутри <script> закрыл бы тег и порвал страницу; < безопасен в JSON.
    payload = "window.STATE=" + json.dumps(state, ensure_ascii=False).replace("</", "<\\/") + ";"
    new = page[: i + len(BEGIN)] + payload + page[j:]
    if new == page:
        return "снимок уже совпадал"
    tmp = PAGE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new)
    os.replace(tmp, PAGE)                                # атомарно: битой страницы не бывает
    return "снимок вписан"


def http_ok(port, path="/dashboard.html"):
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d%s" % (port, path), timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


def cmdline(pid):
    try:
        return subprocess.run(["ps", "-p", str(pid), "-o", "command="],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def is_ours(cmd):
    """Наш ли это процесс. Узкая проверка намеренно: широкая уже убивала чужое."""
    return "-m http.server" in cmd and "--directory " + A in cmd


def recorded():
    try:
        port, pid = open(PIDF).read().split()
        return int(port), int(pid)
    except (OSError, ValueError):
        return None, None


def free_port(prefer):
    """Прежний порт, если свободен, иначе любой. Стабильный адрес важнее случайного."""
    for p in ([prefer] if prefer else []) + [0]:
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", p))
            return s.getsockname()[1]
        except OSError:
            continue
        finally:
            s.close()
    return None


def serve(state):
    if state.get("finishedAt"):
        return "прогон закрыт — сервер не поднимаю"     # Phase 8 его уже убила
    if os.environ.get("SSH_CONNECTION") or os.environ.get("CI"):
        return "удалённая сессия — без сервера"

    port, pid = recorded()
    if port and http_ok(port) and (not pid or is_ours(cmdline(pid))):
        return "сервер жив: http://localhost:%d/dashboard.html" % port

    # Осиротевшие серверы этого же каталога: их никто не убьёт, кроме нас, и
    # только их — по полному --directory, никогда по «все http.server, кроме...».
    for line in subprocess.run(["ps", "-Ao", "pid=,command="], capture_output=True,
                               text=True).stdout.splitlines():
        num, _, cmd = line.strip().partition(" ")
        if is_ours(cmd) and num.isdigit():
            try:
                os.kill(int(num), 15)
            except OSError:
                pass

    port = free_port(port)
    if not port:
        return "порт не нашёлся — дашборд открывается файлом: %s" % PAGE
    try:
        log = open(LOG, "a")
        srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port),
                                "--bind", "127.0.0.1", "--directory", A],
                               stdout=subprocess.DEVNULL, stderr=log,
                               start_new_session=True)     # переживает конец сессии агента
    except OSError as e:
        return "сервер не запустился (%s) — дашборд открывается файлом: %s" % (e, PAGE)
    for _ in range(10):
        if http_ok(port):
            open(PIDF, "w").write("%d %d\n" % (port, srv.pid))
            return "сервер поднят: http://localhost:%d/dashboard.html" % port
        try:
            srv.wait(timeout=0.5)
            break
        except subprocess.TimeoutExpired:
            continue
    srv.terminate()
    return "сервер не ответил — дашборд открывается файлом: %s" % PAGE


def main():
    state = read_state()
    snap = write_snapshot(state)
    srv = "сервер не проверялся" if "--no-serve" in sys.argv else serve(state)
    print("%s · %s · обновлено %s" % (snap, srv, (state.get("updatedAt") or "?")[11:19]))


if __name__ == "__main__":
    main()
