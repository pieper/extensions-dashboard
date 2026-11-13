#!/usr/bin/env python3
"""Validate review results produced by run_review.py, file them under reviews/, and open or update issues.

Runs in a job that has write access to this repository but never sees the extension source or the
OpenRouter key. Everything it reads from the review job is treated as untrusted data: names are checked,
JSON is re-normalized, and report.md is rebuilt here rather than copied.

Usage: publish.py --in OUTDIR [--issues] [--pages-url URL]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRITERIA, OVERALL, RATINGS, SEVERITIES, load_json, normalize_review, write_json  # noqa: E402
from report import neutralize, render_issue, render_report  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEWS = os.path.join(ROOT, "reviews")
EXT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]{0,99}$")
DIR_RE = re.compile(r"^[0-9a-f]{12}-(full|triage)$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,30}$")
LABELS = {"ai-review": "1f6feb", "needs-human": "d93f0b", "disputed": "8250df", "pr": "0e8a16", "catalog": "c5def5",
          "verdict: ok": "2da44e", "verdict: concerns": "fbca04", "verdict: blocking": "b60205"}


def s(v, n=2000):
    return str(v if v is not None else "")[:n]


def clean_meta(m, ext, d):
    reviewers = []
    for r in (m.get("reviewers") or [])[:8]:
        if not isinstance(r, dict) or not ID_RE.match(str(r.get("id", ""))):
            continue
        reviewers.append({"id": r["id"], "model": s(r.get("model"), 100), "label": s(r.get("label"), 60), "ok": bool(r.get("ok")),
                          "error": s(r.get("error"), 400) if r.get("error") else None,
                          "cost": float(r.get("cost") or 0), "turns": int(r.get("turns") or 0),
                          "tool_calls": int(r.get("tool_calls") or 0), "prompt_tokens": int(r.get("prompt_tokens") or 0),
                          "completion_tokens": int(r.get("completion_tokens") or 0),
                          "cross_exam_cost": float(r.get("cross_exam_cost") or 0)})
    commit = s(m.get("commit"), 40)
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not d.startswith(commit[:12]):
        raise ValueError("commit does not match the folder name")
    counts = {k: int(v) for k, v in (m.get("counts") or {}).items() if k in
              ("consensus", "disputed", "single", "unverified", "total", "open_disputes") and isinstance(v, int)}
    ids = {r["id"] for r in reviewers}
    return {"extension": ext, "scm_url": s(m.get("scm_url"), 300), "revision": s(m.get("revision"), 200) or None,
            "commit": commit, "panel": d.split("-", 1)[1], "pr": int(m["pr"]) if str(m.get("pr") or "").isdigit() else None,
            "source": "pr" if m.get("source") == "pr" else "catalog", "owner": s(m.get("owner"), 100),
            "started": s(m.get("started"), 25), "finished": s(m.get("finished"), 25), "reviewers": reviewers,
            "cost": round(sum(r["cost"] for r in reviewers), 4), "files": int(m.get("files") or 0),
            "large_files_skipped": [{"path": s(x.get("path"), 300), "bytes": int(x.get("bytes") or 0)}
                                    for x in (m.get("large_files_skipped") or [])[:50] if isinstance(x, dict)],
            "agents_md": s(m.get("agents_md"), 100), "rubric_version": int(m.get("rubric_version") or 1),
            "complete": bool(m.get("complete")), "budget_exhausted": bool(m.get("budget_exhausted")),
            "escalate": bool(m.get("escalate")), "counts": counts,
            "overall": {k: v for k, v in (m.get("overall") or {}).items() if k in ids and v in OVERALL}}


def clean_comparison(c, ids):
    """Rebuild the comparison from known fields only."""
    if not isinstance(c, dict):
        return None
    ratings = set(RATINGS)

    def finding(f):
        v = f.get("verification") if isinstance(f.get("verification"), dict) else {}
        return {"reviewer": s(f.get("reviewer"), 30) if f.get("reviewer") in ids else "?",
                "severity": f.get("severity") if f.get("severity") in SEVERITIES else "minor",
                "title": s(f.get("title"), 200), "file": s(f.get("file"), 300), "line_start": _int(f.get("line_start")),
                "line_end": _int(f.get("line_end")), "evidence": s(f.get("evidence"), 1200),
                "explanation": s(f.get("explanation"), 1500), "suggestion": s(f.get("suggestion"), 800),
                "confidence": f.get("confidence") if f.get("confidence") in ("high", "medium", "low") else "medium",
                "verification": {"status": s(v.get("status"), 40), "file": s(v.get("file"), 300) or None, "line": _int(v.get("line"))}}

    def item(it):
        out = {"title": s(it.get("title"), 200), "category": it.get("category") if it.get("category") in CRITERIA else "soundness",
               "severity": it.get("severity") if it.get("severity") in SEVERITIES else "minor", "kind": s(it.get("kind"), 30),
               "disputed": bool(it.get("disputed")), "unverified": bool(it.get("unverified")),
               "raised_by": [x for x in (it.get("raised_by") or []) if x in ids],
               "severities": [x for x in (it.get("severities") or []) if x in SEVERITIES],
               "file": s(it.get("file"), 300) or None, "line": _int(it.get("line")),
               "findings": [finding(f) for f in (it.get("findings") or [])[:8] if isinstance(f, dict)]}
        if it.get("id"):
            out["id"] = s(it["id"], 10)
        if isinstance(it.get("rating_dispute"), dict):
            out["rating_dispute"] = {k: v for k, v in it["rating_dispute"].items() if k in ids and v in ratings}
        if it.get("outcome"):
            out["outcome"] = s(it["outcome"], 40)
        if isinstance(it.get("positions"), dict):
            out["positions"] = {k: {"item": s(p.get("item"), 10), "real": p.get("real") if p.get("real") in ("yes", "no", "unsure") else "unsure",
                                    "severity": p.get("severity") if p.get("severity") in SEVERITIES else None,
                                    "rating": p.get("rating") if p.get("rating") in ratings else None, "reason": s(p.get("reason"), 1200)}
                                for k, p in it["positions"].items() if k in ids and isinstance(p, dict)}
        if it.get("settled_severity") in SEVERITIES:
            out["settled_severity"] = it["settled_severity"]
        return out

    items = [item(it) for it in (c.get("items") or [])[:200] if isinstance(it, dict)]
    disputes = [item(it) for it in (c.get("dispute_items") or [])[:60] if isinstance(it, dict)]
    return {"reviewers": [r for r in (c.get("reviewers") or []) if r in ids], "items": items, "dispute_items": disputes,
            "disputes": [d["id"] for d in disputes if d.get("id")],
            "matrix": {cr: {k: v for k, v in (row or {}).items() if k in ids and v in ratings}
                       for cr, row in (c.get("matrix") or {}).items() if cr in CRITERIA},
            "overall": {k: v for k, v in (c.get("overall") or {}).items() if k in ids and v in OVERALL},
            "counts": {k: int(v) for k, v in (c.get("counts") or {}).items() if isinstance(v, int)}}


def _int(v):
    try:
        return int(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def gh(*args, input=None):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, input=input)
    if r.returncode:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def file_issue(meta, comparison, index_runs, pages_url):
    """Open an issue for a full-panel review, or comment on the extension's open one. Returns the issue number."""
    dirname = f"{meta['commit'][:12]}-{meta['panel']}"
    report_url = f"{pages_url}/review.html?ext={meta['extension']}&dir={dirname}"
    body = render_issue(meta, comparison, report_url, pages_url + "/")
    open_issue = None
    for r in reversed(index_runs):
        if r.get("issue"):
            state = json.loads(gh("issue", "view", str(r["issue"]), "--json", "state"))["state"]
            if state == "OPEN":
                open_issue = r["issue"]
            break
    disputed = bool(comparison and comparison["dispute_items"])
    if open_issue:
        gh("issue", "comment", str(open_issue), "--body-file", "-",
           input=f"New review of commit `{meta['commit'][:12]}`.\n\n" + body)
        gh("issue", "edit", str(open_issue), "--add-label", "needs-human" + (",disputed" if disputed else ""))
        return open_issue
    labels = ["ai-review", "needs-human", "pr" if meta["source"] == "pr" else "catalog"] + (["disputed"] if disputed else [])
    url = gh("issue", "create", "--title", neutralize(f"AI review: {meta['extension']} ({meta['commit'][:7]})"),
             "--label", ",".join(labels), "--body-file", "-", input=body).strip()
    return int(url.rstrip("/").rsplit("/", 1)[1])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="indir", required=True)
    ap.add_argument("--issues", action="store_true", help="Open or update GitHub issues for full-panel reviews")
    ap.add_argument("--pages-url", default="")
    args = ap.parse_args()
    index_path = os.path.join(REVIEWS, "index.json")
    index = load_json(index_path, {}) or {}
    if args.issues:
        for name, color in LABELS.items():
            subprocess.run(["gh", "label", "create", name, "--color", color, "--force"], capture_output=True)
    added = []
    for ext in sorted(os.listdir(args.indir)) if os.path.isdir(args.indir) else []:
        if not EXT_RE.match(ext) or not os.path.isdir(os.path.join(args.indir, ext)):
            print(f"skipping unexpected entry {ext!r}", file=sys.stderr)
            continue
        for d in sorted(os.listdir(os.path.join(args.indir, ext))):
            src = os.path.join(args.indir, ext, d)
            if not DIR_RE.match(d) or not os.path.isdir(src):
                print(f"skipping unexpected folder {ext}/{d!r}", file=sys.stderr)
                continue
            try:
                meta = clean_meta(load_json(os.path.join(src, "meta.json"), {}), ext, d)
            except (ValueError, TypeError, KeyError) as e:
                print(f"skipping {ext}/{d}: bad meta.json ({e})", file=sys.stderr)
                continue
            ids = {r["id"] for r in meta["reviewers"]}
            reviews = {}
            for rid in ids:
                raw = load_json(os.path.join(src, f"{rid}.json"))
                if isinstance(raw, dict) and os.path.getsize(os.path.join(src, f"{rid}.json")) < 3_000_000:
                    reviews[rid] = normalize_review(raw)
            comparison = clean_comparison(load_json(os.path.join(src, "comparison.json")), set(reviews))
            dest = os.path.join(REVIEWS, ext, d)
            shutil.rmtree(dest, ignore_errors=True)
            os.makedirs(dest)
            write_json(os.path.join(dest, "meta.json"), meta)
            for rid, rev in reviews.items():
                write_json(os.path.join(dest, f"{rid}.json"), rev)
            if comparison:
                write_json(os.path.join(dest, "comparison.json"), comparison)
            with open(os.path.join(dest, "report.md"), "w") as f:
                f.write(render_report(meta, reviews, comparison))
            runs = [r for r in index.get(ext, []) if r.get("dir") != d]
            entry = {"dir": d, "commit": meta["commit"], "panel": meta["panel"], "pr": meta["pr"], "source": meta["source"],
                     "owner": meta["owner"], "finished": meta["finished"], "cost": meta["cost"], "counts": meta["counts"],
                     "overall": meta["overall"], "escalate": meta["escalate"], "complete": meta["complete"],
                     "models": [r["model"] for r in meta["reviewers"] if r["ok"]]}
            if args.issues and meta["panel"] == "full" and meta["complete"]:
                try:
                    entry["issue"] = file_issue(meta, comparison, runs, args.pages_url.rstrip("/"))
                except RuntimeError as e:
                    print(f"issue for {ext}: {e}", file=sys.stderr)
            index[ext] = runs + [entry]
            added.append(f"{ext} ({meta['panel']}, ${meta['cost']:.2f})")
    write_json(index_path, dict(sorted(index.items())))
    print("published: " + (", ".join(added) or "nothing"), file=sys.stderr)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"summary={'; '.join(added)[:900]}\n")


if __name__ == "__main__":
    main()
