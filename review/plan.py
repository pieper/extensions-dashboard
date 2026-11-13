#!/usr/bin/env python3
"""Decide what to review in this run, within the monthly budget.

Order: open extension PRs (full panel) > catalog extensions the first pass flagged (full panel) >
catalog backlog (first-pass panel; developers outside the core community first, newest first).
Catalog work is paced so the month's budget lasts the month; PR reviews may use the whole remainder.

Usage: plan.py --out queue.json [--dashboard-data URL-or-path] [--extension NAME --panel full|triage]
"""

import argparse
import calendar
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HERE, http_json, load_json, write_json  # noqa: E402

ROOT = os.path.dirname(HERE)
INDEX = os.path.join(ROOT, "reviews", "index.json")


def read_list(path):
    try:
        with open(path) as f:
            return {line.split("#", 1)[0].strip().lower() for line in f} - {""}
    except OSError:
        return set()


def owner_of(url):
    m = re.match(r"https?://[^/]+/([^/]+)/", url or "")
    return m.group(1) if m else ""


def catalog():
    """Catalog entries of Slicer/ExtensionsIndex main, with the date each was first added."""
    tmp = tempfile.mkdtemp()
    subprocess.run(["git", "clone", "-q", "--filter=blob:none", "https://github.com/Slicer/ExtensionsIndex.git", tmp],
                   check=True, timeout=600, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    log = subprocess.run(["git", "-C", tmp, "log", "--diff-filter=A", "--name-only", "--format=@%aI", "--", "*.json"],
                         capture_output=True, text=True, check=True).stdout
    added, when = {}, None
    for line in log.splitlines():
        if line.startswith("@"):
            when = line[1:]
        elif line.endswith(".json") and "/" not in line:
            added[line] = when  # log is newest first, so the last assignment is the first addition
    out = []
    for fn in sorted(os.listdir(tmp)):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(tmp, fn)) as f:
                entry = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not entry.get("scm_url"):
            continue
        out.append({"extension": fn[:-5], "scm_url": entry["scm_url"], "revision": entry.get("scm_revision"),
                    "entry": entry, "added": added.get(fn), "source": "catalog", "owner": owner_of(entry["scm_url"])})
    return out


def spent(index, month, day=None):
    total = 0.0
    for runs in index.values():
        for r in runs:
            t = r.get("finished") or ""
            if t.startswith(month) and (day is None or t.startswith(day)):
                total += r.get("cost", 0)
    return total


def estimate(index, panel, default):
    costs = [r["cost"] for runs in index.values() for r in runs if r.get("panel") == panel and r.get("cost")]
    return max(default, sum(costs[-20:]) / len(costs[-20:])) if costs else default


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--dashboard-data", help="data.json of the dashboard (for open PRs)")
    ap.add_argument("--extension", help="Review this extension now (from a PR if one is open, else the catalog)")
    ap.add_argument("--panel", choices=["full", "triage", "auto"], default="auto")
    ap.add_argument("--drain", action="store_true",
                    help="Queue everything outstanding (PRs, then the catalog first pass, then escalations); "
                         "only the OpenRouter key's limit stops the work")
    args = ap.parse_args()

    panels = load_json(os.path.join(HERE, "panels.json"))
    budget = panels["budget"]
    index = load_json(INDEX, {}) or {}
    today = dt.datetime.now(dt.timezone.utc)
    month, day = today.strftime("%Y-%m"), today.strftime("%Y-%m-%d")
    days_left = calendar.monthrange(today.year, today.month)[1] - today.day + 1
    month_left = budget["monthly_usd"] - spent(index, month)
    daily_allowance = max(0.0, month_left / days_left) - spent(index, month, day) + 0.0
    run_cap = budget["per_run_usd"]
    est = {"full": estimate(index, "full", budget["estimate_full_usd"]),
           "triage": estimate(index, "triage", budget["estimate_triage_usd"])}
    print(f"month left ${month_left:.2f}, today's allowance ${daily_allowance:.2f}, estimates {est}", file=sys.stderr)

    def done(ext, panel, commit=None, within_hours=None):
        for r in index.get(ext, []):
            if r.get("panel") != panel:
                continue
            if commit and r.get("commit") == commit:
                return True
            if within_hours and r.get("finished"):
                age = today - dt.datetime.fromisoformat(r["finished"].replace("Z", "+00:00"))
                if age.total_seconds() < within_hours * 3600:
                    return True
        return False

    prs = []
    if args.dashboard_data:
        try:
            data = http_json(args.dashboard_data) if re.match(r"https?://", args.dashboard_data) else load_json(args.dashboard_data)
        except Exception as e:  # noqa: BLE001
            print(f"no dashboard data ({e})", file=sys.stderr)
            data = None
        for p in (data or {}).get("prs", []):
            src = p.get("src") or {}
            if p.get("draft") or p.get("turn") == "hold" or not src.get("head_sha") or not (p.get("entry") or {}).get("scm_url"):
                continue
            prs.append({"extension": p["name"], "scm_url": p["entry"]["scm_url"], "revision": p["entry"].get("scm_revision"),
                        "commit": src["head_sha"], "pr": p["number"], "entry": p["entry"], "hints": p.get("hints", [])[:20],
                        "source": "pr", "owner": owner_of(p["entry"]["scm_url"])})

    failed_recently = set()
    for f in load_json(os.path.join(ROOT, "reviews", "failures.json"), []) or []:
        try:
            if (today - dt.datetime.fromisoformat(f["when"].replace("Z", "+00:00"))).days < 3:
                failed_recently.add((f["extension"], f.get("panel")))
        except (KeyError, ValueError):
            pass
    newest = {}
    for p in prs:  # an extension can have more than one open PR; review the newest
        if p["extension"] not in newest or p["pr"] > newest[p["extension"]]["pr"]:
            newest[p["extension"]] = p
    prs = [p for p in newest.values() if (p["extension"], "full") not in failed_recently]
    if args.drain:
        run_cap = daily_allowance = month_left = float("inf")

    queue, cost = [], 0.0
    if args.extension:
        item = next((p for p in prs if p["extension"].lower() == args.extension.lower()), None)
        if item is None:
            item = next((c for c in catalog() if c["extension"].lower() == args.extension.lower()), None)
        if item is None:
            sys.exit(f"{args.extension} is neither an open PR nor in the catalog")
        panel = args.panel if args.panel != "auto" else ("full" if item["source"] == "pr" else "triage")
        if est[panel] > month_left:
            sys.exit(f"not enough budget left this month (${month_left:.2f})")
        queue.append({"item": item, "panel": panel})
    else:
        for p in sorted(prs, key=lambda p: -p["pr"]):
            if done(p["extension"], "full", commit=p["commit"]) or done(p["extension"], "full", within_hours=panels["settings"].get("recheck_open_pr_hours", 72)):
                continue
            if cost + est["full"] <= min(run_cap, month_left):
                queue.append({"item": p, "panel": "full"})
                cost += est["full"]
        cat = None
        blocks = ["triage", "escalate"] if args.drain else ["escalate", "triage"]
        for block in blocks:
            if block == "escalate":
                for ext, runs in sorted(index.items()):
                    esc = [r for r in runs if r.get("panel") == "triage" and r.get("escalate")]
                    if (esc and (ext, "full") not in failed_recently
                            and not any(r.get("panel") == "full" and r.get("commit") == esc[-1]["commit"] for r in runs)):
                        if any(q["item"]["extension"] == ext for q in queue):
                            continue
                        cat = cat if cat is not None else {c["extension"]: c for c in catalog()}
                        c = cat.get(ext)
                        if c and cost + est["full"] <= min(run_cap, daily_allowance):
                            queue.append({"item": dict(c, commit=esc[-1]["commit"], hints=[]), "panel": "full"})
                            cost += est["full"]
            else:
                if cost + est["triage"] <= min(run_cap, daily_allowance):
                    cat = cat if cat is not None else {c["extension"]: c for c in catalog()}
                    core = read_list(os.path.join(HERE, "core_owners.txt")) | read_list(os.path.join(ROOT, "dashboard", "maintainers.txt"))
                    todo = [c for c in cat.values() if not index.get(c["extension"]) and (c["extension"], "triage") not in failed_recently
                            and not any(q["item"]["extension"] == c["extension"] for q in queue)]
                    todo.sort(key=lambda c: (c["owner"].lower() in core, -(dt.datetime.fromisoformat(c["added"]).timestamp() if c.get("added") else 0)))
                    for c in todo:
                        if cost + est["triage"] > min(run_cap, daily_allowance):
                            break
                        queue.append({"item": c, "panel": "triage"})
                        cost += est["triage"]
    write_json(args.out, queue)
    print(f"{len(queue)} item(s), estimated ${cost:.2f}: " + ", ".join(f"{q['item']['extension']} ({q['panel']})" for q in queue),
          file=sys.stderr)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"count={len(queue)}\n")


if __name__ == "__main__":
    main()
