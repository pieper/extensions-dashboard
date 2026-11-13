#!/usr/bin/env python3
"""Run the reviews plan.py queued, stopping before the OpenRouter key runs out of credit.

Usage: run_queue.py --queue queue.json --out OUTDIR
"""

import argparse
import datetime as dt
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HERE, key_status, load_json, write_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--queue", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-minutes", type=float, default=0, help="Start no new review after this long (0 = no limit)")
    args = ap.parse_args()
    queue = load_json(args.queue, []) or []
    budget = load_json(os.path.join(HERE, "panels.json"))["budget"]
    start, processed, failures, stopped = time.time(), 0, [], "done"
    for q in queue:
        if args.max_minutes and time.time() - start > args.max_minutes * 60:
            stopped = "time"
            break
        status = key_status()
        print(f"key usage so far ${status['usage'] or 0:.3f}, limit remaining {status['remaining']}", file=sys.stderr)
        if status["remaining"] is not None and status["remaining"] < budget["reserve_usd"]:
            print(f"Stopping: ${status['remaining']:.2f} left on the OpenRouter key", file=sys.stderr)
            stopped = "budget"
            break
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            item_path = f.name
        write_json(item_path, q["item"])
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "run_review.py"), "--item", item_path,
                            "--panel", q["panel"], "--out", args.out])
        os.unlink(item_path)
        processed += 1
        if r.returncode == 3:
            print("Stopping: OpenRouter credit or limit reached", file=sys.stderr)
            stopped = "budget"
            break
        if r.returncode:
            failures.append({"extension": q["item"]["extension"], "panel": q["panel"], "error": f"exit {r.returncode}",
                             "when": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            print(f"Review of {q['item']['extension']} failed (exit {r.returncode})", file=sys.stderr)
    if failures:
        write_json(os.path.join(args.out, "_failures.json"), failures)
    more = stopped == "time" or (stopped == "done" and len(queue) > 0 and processed > len(failures))
    print(f"{processed} of {len(queue)} processed, {len(failures)} failed, stopped: {stopped}", file=sys.stderr)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"stopped={stopped}\nmore={'true' if more else 'false'}\n")


if __name__ == "__main__":
    main()
