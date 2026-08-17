#!/usr/bin/env python3
"""Замер прогона Autopilot по логам сессии Claude Code.

Отвечает на три вопроса, ради которых он написан:
  · во что обошёлся прогон и кто именно потратил;
  · насколько выросли контексты — единственная величина, которой можно управлять;
  · соблюдаются ли правила, которые нельзя проверить чтением скилла.

Использование:
    python3 tools/measure-run.py <путь к каталогу проекта>
    python3 tools/measure-run.py ~/Documents/VScode/EDU/share

Каталог логов вычисляется из пути проекта так же, как это делает Claude Code:
разделители пути заменяются дефисами внутри ~/.claude/projects/
(на Windows — обратные слэши и двоеточие диска тоже).

Нормировка стоимости — относительно входного токена:
    output ×5 · cache_write ×1.25 · cache_read ×0.1
Это пропорции, а не деньги: они нужны, чтобы сравнивать прогоны между собой.
"""

import json
import os
import sys
import glob
from datetime import datetime
from collections import Counter

W_OUT, W_WRITE, W_READ = 5.0, 1.25, 0.1
IDLE_GAP_SEC = 300          # пауза длиннее — это простой, а не работа
CEILING_HINT = 120_000      # потолок из phases/5-subagents.md, для колонки «перебор»


def logs_dir_for(project_path):
    p = os.path.abspath(os.path.expanduser(project_path))
    # Все три разделителя, а не только «/»: на Windows путь приходит как C:\Users\x,
    # и «C:\...» осталось бы абсолютным — os.path.join тогда отбрасывает первый аргумент
    # и замер молча уходит искать логи в самой папке проекта.
    slug = p.replace("\\", "-").replace("/", "-").replace(":", "-")
    return os.path.join(os.path.expanduser("~/.claude/projects"), slug)


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def analyse(path, label):
    rows = load(path)
    ctx, tools = [], Counter()
    out = win = rin = cold = 0
    test_edits = code_edits = test_runs = 0
    stamps = []

    for r in rows:
        m = r.get("message") or {}
        ts = parse_ts(r.get("timestamp"))
        if ts:
            stamps.append(ts)
        if (m.get("role") or r.get("type")) != "assistant":
            continue
        u = m.get("usage") or {}
        if u:
            cr = u.get("cache_read_input_tokens", 0) or 0
            cw = u.get("cache_creation_input_tokens", 0) or 0
            ip = u.get("input_tokens", 0) or 0
            out += u.get("output_tokens", 0) or 0
            win += cw
            rin += cr
            if cw > 20_000:
                cold += 1
            if cr + cw + ip:
                ctx.append(cr + cw + ip)
        for c in m.get("content") or []:
            if not isinstance(c, dict) or c.get("type") != "tool_use":
                continue
            name, inp = c.get("name"), c.get("input", {})
            tools[name] += 1
            if name == "Bash":
                cmd = str(inp.get("command", ""))
                if any(k in cmd for k in ("pytest", "npm test", "go test", "cargo test", "unittest")):
                    test_runs += 1
            elif name in ("Edit", "Write", "NotebookEdit"):
                fp = str(inp.get("file_path", ""))
                base = os.path.basename(fp)
                if "/tests/" in fp or "/test/" in fp or base.startswith("test_") or ".test." in base:
                    test_edits += 1
                else:
                    code_edits += 1

    stamps.sort()
    active = idle = 0
    for a, b in zip(stamps, stamps[1:]):
        gap = (b - a).total_seconds()
        if gap <= IDLE_GAP_SEC:
            active += gap
        else:
            idle += gap

    return {
        "label": label, "steps": len(ctx),
        "avg_ctx": sum(ctx) / len(ctx) if ctx else 0,
        "max_ctx": max(ctx) if ctx else 0,
        "over": sum(1 for c in ctx if c > CEILING_HINT),
        "out": out, "write": win, "read": rin, "cold": cold,
        "norm": out * W_OUT + win * W_WRITE + rin * W_READ,
        "active": active, "idle": idle,
        "test_edits": test_edits, "code_edits": code_edits, "test_runs": test_runs,
    }


def main():
    # Отчёт — кириллица и «█»; на Windows консоль по умолчанию не utf-8,
    # и печать полосы расхода падала бы UnicodeEncodeError на готовых цифрах.
    # stderr — потому что подсказки и «нет логов» уходят туда через sys.exit.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = logs_dir_for(sys.argv[1])
    if not os.path.isdir(d):
        sys.exit(f"нет логов: {d}")

    sessions = glob.glob(os.path.join(d, "*.jsonl"))
    if not sessions:
        sys.exit(f"в {d} нет .jsonl")

    def weight(p):
        """Прогон Autopilot узнаётся по субагентам, а не по свежести:
        последняя по времени сессия — обычно та, в которой смотрят результат."""
        n = len(glob.glob(os.path.join(p[:-6], "subagents", "*.jsonl")))
        return (n, os.path.getsize(p))

    if len(sys.argv) > 2:                       # явный выбор: id сессии
        picked = [p for p in sessions if sys.argv[2] in os.path.basename(p)]
        if not picked:
            sys.exit(f"сессия {sys.argv[2]} не найдена в {d}")
        main_log = picked[0]
    else:
        main_log = max(sessions, key=weight)

    if len(sessions) > 1:
        print(f"\nСессий в каталоге: {len(sessions)}. Взята {os.path.basename(main_log)[:8]}"
              f" ({len(glob.glob(os.path.join(main_log[:-6], 'subagents', '*.jsonl')))} субагентов)."
              f"\nДругую — вторым аргументом: measure-run.py <проект> <id сессии>")
    sub_dir = main_log[:-6]

    metas = {}
    for mf in glob.glob(os.path.join(sub_dir, "subagents", "*.meta.json")):
        with open(mf, encoding="utf-8") as f:
            metas[os.path.basename(mf)[:-10]] = json.load(f)

    results = [analyse(main_log, "Оркестратор")]
    for jf in sorted(glob.glob(os.path.join(sub_dir, "subagents", "*.jsonl"))):
        key = os.path.basename(jf)[:-6]
        results.append(analyse(jf, metas.get(key, {}).get("description", key)))
    results.sort(key=lambda r: -r["norm"])

    total = sum(r["norm"] for r in results) or 1
    print(f"\nПрогон: {sys.argv[1]}   контекстов: {len(results)}\n")
    print(f"{'контекст':<38}{'шагов':>7}{'ср.ctx':>9}{'макс':>9}{'>120K':>7}{'норм.ед':>11}{'доля':>7}")
    print("-" * 88)
    for r in results:
        print(f"{r['label'][:37]:<38}{r['steps']:>7}{r['avg_ctx']/1000:>8.0f}K"
              f"{r['max_ctx']/1000:>8.0f}K{r['over']:>7}{r['norm']/1e6:>10.2f}M"
              f"{r['norm']/total*100:>6.1f}%")
    print("-" * 88)

    o = sum(r["out"] for r in results)
    w = sum(r["write"] for r in results)
    rd = sum(r["read"] for r in results)
    steps = sum(r["steps"] for r in results)
    print(f"{'ИТОГО':<38}{steps:>7}{'':>9}{'':>9}{'':>7}{total/1e6:>10.2f}M\n")

    print("Структура расхода")
    for name, val in (("чтение кэша", rd * W_READ), ("запись кэша", w * W_WRITE), ("генерация", o * W_OUT)):
        bar = "█" * round(val / total * 46)
        print(f"  {name:<14}{val/total*100:>5.1f}%  {bar}")
    print(f"\n  прочитано на каждый написанный токен: {(rd + w) / o:.0f}:1" if o else "")

    print("\nСоблюдение правил")
    hot = [r for r in results if r["avg_ctx"] > CEILING_HINT * 1.5]
    print(f"  контекстов выше полуторного потолка: {len(hot)}"
          + (f" — {', '.join(r['label'][:24] for r in hot[:4])}" if hot else " — нет"))
    te = sum(r["test_edits"] for r in results)
    ce = sum(r["code_edits"] for r in results)
    print(f"  правки тестов к правкам кода: {te}/{ce}"
          + (f" ({te/(te+ce)*100:.0f}%)" if te + ce else ""))
    print(f"  прогонов тестов: {sum(r['test_runs'] for r in results)}")
    cold_agents = [r for r in results if r["read"] and r["write"] / r["read"] > 0.10]
    print(f"  контекстов с протухшим кэшем (запись/чтение > 10%): {len(cold_agents)}"
          + (f" — {', '.join(r['label'][:24] for r in cold_agents[:4])}" if cold_agents else " — нет"))

    act = sum(r["active"] for r in results)
    idl = sum(r["idle"] for r in results)
    print(f"\nВремя по всем контекстам: активно {act/60:.0f} мин · простой {idl/60:.0f} мин"
          f" ({act/(act+idl)*100:.0f}% активного)" if act + idl else "")


if __name__ == "__main__":
    main()
