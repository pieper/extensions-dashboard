#!/usr/bin/env python3
"""List OpenRouter models that can act as tool-using reviewers, with prices, and check panels.json against them.

Usage: list_models.py [--out models.json]   (no API key needed)
"""

import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HERE, OPENROUTER, http_json, load_json, write_json  # noqa: E402

VENDORS = ["anthropic", "openai", "google", "mistralai", "qwen", "deepseek", "moonshotai", "z-ai", "x-ai", "meta-llama"]
SKIP = ("image", "audio", "tts", "embed", "search", "deep-research", "realtime", "vision", ":free", "-preview-")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="models.json")
    args = ap.parse_args()
    models = http_json(OPENROUTER + "/models", timeout=60)["data"]
    rows = []
    for m in models:
        vendor = m["id"].split("/")[0]
        params = m.get("supported_parameters") or []
        if vendor not in VENDORS or "tools" not in params or any(k in m["id"] for k in SKIP):
            continue
        p = m.get("pricing") or {}
        rows.append({"id": m["id"], "vendor": vendor, "name": m.get("name"), "created": m.get("created", 0),
                     "context": m.get("context_length"), "in_per_m": round(float(p.get("prompt") or 0) * 1e6, 3),
                     "out_per_m": round(float(p.get("completion") or 0) * 1e6, 3),
                     "cache_read_per_m": round(float(p.get("input_cache_read") or 0) * 1e6, 3),
                     "structured_outputs": "structured_outputs" in params})
    rows.sort(key=lambda r: (r["vendor"], -r["created"]))
    write_json(args.out, rows)

    lines = ["| model | released | context | $ in / M | $ out / M |", "|---|---|---|---|---|"]
    per_vendor = {}
    for r in rows:
        per_vendor[r["vendor"]] = per_vendor.get(r["vendor"], 0) + 1
        if per_vendor[r["vendor"]] <= 6:
            lines.append(f"| `{r['id']}` | {dt.datetime.fromtimestamp(r['created'], dt.timezone.utc):%Y-%m-%d} | "
                         f"{r['context']} | {r['in_per_m']} | {r['out_per_m']} |")
    known = {r["id"]: r for r in rows}
    panels = load_json(os.path.join(HERE, "panels.json"), {}) or {}
    problems = []
    for name, panel in (panels.get("panels") or {}).items():
        for rv in panel.get("reviewers", []):
            if rv["model"] not in known:
                problems.append(f"panel {name}: `{rv['model']}` is not available with tool calling")
    text = "## Tool-capable OpenRouter models (newest six per vendor)\n\n" + "\n".join(lines)
    if problems:
        text += "\n\n## Problems with panels.json\n\n" + "\n".join(f"- {p}" for p in problems)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(text + "\n")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
