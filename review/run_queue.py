#!/usr/bin/env python3
"""Run the reviews plan.py queued, stopping before the OpenRouter key runs out of credit.

Usage: run_queue.py --queue queue.json --out OUTDIR
"""

import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HERE, key_status, load_json, write_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--queue", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    queue = load_json(args.queue, []) or []
    budget = load_json(os.path.join(HERE, "panels.json"))["budget"]
    failures = 0
    for q in queue:
        status = key_status()
        if status["remaining"] is not None and status["remaining"] < budget["reserve_usd"]:
            print(f"Stopping: ${status['remaining']:.2f} left on the OpenRouter key", file=sys.stderr)
            break
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            item_path = f.name
        write_json(item_path, q["item"])
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "run_review.py"), "--item", item_path,
                            "--panel", q["panel"], "--out", args.out])
        os.unlink(item_path)
        if r.returncode == 3:
            print("Stopping: OpenRouter credit or limit reached", file=sys.stderr)
            break
        if r.returncode:
            failures += 1
            print(f"Review of {q['item']['extension']} failed (exit {r.returncode})", file=sys.stderr)
    sys.exit(1 if failures and failures == len(queue) else 0)


if __name__ == "__main__":
    main()
