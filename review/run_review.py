#!/usr/bin/env python3
"""Review one extension at one commit with a panel of models, and write the results.

Usage: run_review.py --item item.json --panel full|triage --out OUTDIR

The extension's source is downloaded as an archive and only read. Nothing from it is executed.
"""

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent  # noqa: E402
from common import (HERE, UPSTREAM_AGENTS_MD, BudgetExhausted, ModelError, Workspace, http_json, http_text,  # noqa: E402
                    load_json, write_json)
from compare import apply_positions, compare, needs_escalation  # noqa: E402
from report import render_report  # noqa: E402

MAX_ARCHIVE_BYTES = 400_000_000
MAX_MEMBER_BYTES = 2_000_000


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def github_parts(scm_url):
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", (scm_url or "").strip())
    return (m.group(1), m.group(2)) if m else None


def resolve_commit(scm_url, revision):
    if revision and re.fullmatch(r"[0-9a-f]{40}", revision):
        return revision
    gh = github_parts(scm_url)
    if gh:
        headers = {"Accept": "application/vnd.github+json"}
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
        ref = revision or "HEAD"
        return http_json(f"https://api.github.com/repos/{gh[0]}/{gh[1]}/commits/{urllib.parse.quote(ref, safe='')}",
                         headers=headers, timeout=60)["sha"]
    out = subprocess.run(["git", "ls-remote", scm_url, revision or "HEAD"], capture_output=True, text=True, timeout=120,
                         env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    line = out.stdout.split("\n")[0].split()
    if not line:
        raise RuntimeError(f"cannot resolve {revision!r} in {scm_url}")
    return line[0]


def fetch_source(scm_url, commit, dest):
    """Put the repository's files at `commit` into dest. Returns the list of large files left out."""
    skipped = []
    gh = github_parts(scm_url)
    if gh:
        url = f"https://codeload.github.com/{gh[0]}/{gh[1]}/tar.gz/{commit}"
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            req = urllib.request.Request(url, headers={"User-Agent": "slicer-extensions-dashboard"})
            with urllib.request.urlopen(req, timeout=300) as r:
                total = 0
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_ARCHIVE_BYTES:
                        raise RuntimeError("source archive is larger than 400 MB")
                    tmp.write(chunk)
        try:
            with tarfile.open(tmp.name, "r:gz") as tf:
                members = []
                for m in tf.getmembers():
                    parts = m.name.split("/", 1)
                    if len(parts) < 2 or not parts[1]:
                        continue
                    if m.isfile() and m.size > MAX_MEMBER_BYTES:
                        skipped.append({"path": parts[1], "bytes": m.size})
                        continue
                    if not (m.isfile() or m.isdir()):
                        continue  # no links or devices
                    m.name = parts[1]
                    members.append(m)
                tf.extractall(dest, members=members, filter="data")
        finally:
            os.unlink(tmp.name)
        return skipped
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
    git = ["git", "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never", "-c", "core.symlinks=false"]
    subprocess.run(git + ["init", "-q", dest], check=True, env=env, timeout=60)
    subprocess.run(git + ["-C", dest, "fetch", "-q", "--depth", "1", scm_url, commit], check=True, env=env, timeout=600)
    subprocess.run(git + ["-C", dest, "checkout", "-q", "FETCH_HEAD"], check=True, env=env, timeout=300)
    shutil.rmtree(os.path.join(dest, ".git"), ignore_errors=True)
    for dirpath, _, files in os.walk(dest):
        for fn in files:
            full = os.path.join(dirpath, fn)
            if os.path.getsize(full) > MAX_MEMBER_BYTES:
                skipped.append({"path": os.path.relpath(full, dest), "bytes": os.path.getsize(full)})
                os.unlink(full)
    return skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--item", required=True, help="JSON file describing the extension (see plan.py)")
    ap.add_argument("--panel", required=True, choices=["full", "triage"])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    item = load_json(args.item)
    panels = load_json(os.path.join(HERE, "panels.json"))
    panel = panels["panels"][args.panel]
    settings = dict(panels.get("settings", {}), **panel.get("settings", {}))

    started = now()
    commit = item.get("commit") or resolve_commit(item["scm_url"], item.get("revision"))
    ctx = dict(item, commit=commit)
    outdir = os.path.join(args.out, item["extension"], f"{commit[:12]}-{args.panel}")
    os.makedirs(outdir, exist_ok=True)
    log(f"== {item['extension']} @ {commit[:12]} ({args.panel} panel)")

    agents_md = http_text(UPSTREAM_AGENTS_MD)
    with tempfile.TemporaryDirectory() as src:
        skipped = fetch_source(item["scm_url"], commit, src)
        ws = Workspace(src)
        if skipped:
            ctx["hints"] = (ctx.get("hints") or []) + [{"level": "info", "text": "Large files not available to read: " +
                                                       ", ".join(f"{s['path']} ({s['bytes'] // 1_000_000} MB)" for s in skipped[:10])}]
        log(f"   {len(ws.files)} files")

        reviews, meta_reviewers, budget_hit = {}, [], None

        def one(reviewer):
            log(f"   reviewer {reviewer['id']} ({reviewer['model']})")
            return reviewer, agent.review(reviewer, ctx, ws, agents_md, settings, log=log)

        with concurrent.futures.ThreadPoolExecutor(len(panel["reviewers"])) as ex:
            futures = [ex.submit(one, r) for r in panel["reviewers"]]
            for fut, reviewer in zip(futures, panel["reviewers"]):
                entry = {"id": reviewer["id"], "model": reviewer["model"], "label": reviewer.get("label", reviewer["id"])}
                try:
                    _, (rev, usage) = fut.result()
                    reviews[reviewer["id"]] = rev
                    entry.update(ok=True, **usage)
                    write_json(os.path.join(outdir, f"{reviewer['id']}.json"), dict(rev, reviewer=entry))
                except BudgetExhausted as e:
                    budget_hit = str(e)
                    entry.update(ok=False, error="OpenRouter credit or limit reached")
                except (ModelError, Exception) as e:  # noqa: BLE001 - one reviewer failing must not lose the others
                    entry.update(ok=False, error=str(e)[:400])
                meta_reviewers.append(entry)

        comparison = compare(reviews, ws) if reviews else None
        if comparison and len(reviews) >= 2 and settings.get("cross_exam") and comparison["dispute_items"] and not budget_hit:
            positions = {}

            def examine(reviewer):
                return reviewer, agent.cross_examine(reviewer, ctx, ws, agents_md, comparison["dispute_items"], settings, log=log)

            ok = [r for r in panel["reviewers"] if r["id"] in reviews]
            with concurrent.futures.ThreadPoolExecutor(len(ok)) as ex:
                for fut in [ex.submit(examine, r) for r in ok]:
                    try:
                        reviewer, (plist, usage) = fut.result()
                        positions[reviewer["id"]] = plist
                        m = next(x for x in meta_reviewers if x["id"] == reviewer["id"])
                        m["cross_exam_cost"] = usage["cost"]
                        m["cost"] = m.get("cost", 0) + usage["cost"]
                    except BudgetExhausted as e:
                        budget_hit = str(e)
                    except Exception as e:  # noqa: BLE001
                        log(f"   cross-examination failed: {e}")
            apply_positions(comparison, positions)

    meta = {"extension": item["extension"], "scm_url": item["scm_url"], "revision": item.get("revision"), "commit": commit,
            "panel": args.panel, "pr": item.get("pr"), "source": item.get("source", "catalog"), "owner": item.get("owner"),
            "started": started, "finished": now(), "reviewers": meta_reviewers,
            "cost": round(sum(r.get("cost", 0) for r in meta_reviewers), 4),
            "files": len(ws.files), "large_files_skipped": skipped[:50],
            "agents_md": "Slicer/ExtensionsIndex main AGENTS.md", "rubric_version": panels.get("rubric_version", 1),
            "complete": len(reviews) >= 2, "budget_exhausted": bool(budget_hit)}
    if comparison:
        meta["escalate"] = args.panel == "triage" and needs_escalation(reviews, comparison)
        meta["counts"] = comparison["counts"]
        meta["overall"] = comparison["overall"]
        write_json(os.path.join(outdir, "comparison.json"), comparison)
    write_json(os.path.join(outdir, "meta.json"), meta)
    with open(os.path.join(outdir, "report.md"), "w") as f:
        f.write(render_report(meta, reviews, comparison))
    log(f"   done: cost ${meta['cost']:.3f}, {meta.get('counts')}")
    if budget_hit:
        log("   OpenRouter credit or limit reached; stopping")
        sys.exit(3)


if __name__ == "__main__":
    main()
