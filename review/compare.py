"""Compare reviewers: verify quoted evidence, group matching findings, and find the disagreements."""

import re

from common import CRITERIA, RATINGS, SEVERITIES

SEV_RANK = {s: i for i, s in enumerate(SEVERITIES)}
RATING_RANK = {r: i for i, r in enumerate(RATINGS) if r != "unknown"}
STOP = set("a an the of to in for is are be and or not with without on at by from this that it its as".split())


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def verify(finding, ws):
    """Check that the quoted evidence really is in the repository, preferring the cited file."""
    f = finding
    if not (f.get("evidence") or "").strip():
        return {"status": "no quote"}
    path = f.get("file") or ""
    cited = [path] if path in ws.files else [p for p in ws.files if path and p.endswith("/" + path)]
    others = [p for p in ws.files if p not in cited and ws.is_text(p)]
    needle = _norm(f["evidence"])
    first = next((_norm(x) for x in f["evidence"].splitlines() if _norm(x)), "")
    parts = [_norm(x) for x in f["evidence"].splitlines() if len(_norm(x)) >= 12]
    for group, is_cited in ((cited, True), (others, False)):
        for p in group:
            t = ws.text(p)
            if t is None:
                continue
            lines = t.splitlines()
            flat = _norm(t)
            if needle in flat:
                line = next((i for i, x in enumerate(lines, 1) if first and first in _norm(x)), None)
                near = line is None or f.get("line_start") is None or abs(line - f["line_start"]) <= 10
                status = ("verified" if near else "verified, other lines") if is_cited else "verified, other file"
                return {"status": status, "file": p, "line": line}
            hits = [x for x in parts if x in flat]
            if parts and len(hits) * 2 >= len(parts):
                line = next((i for i, x in enumerate(lines, 1) if hits[0] in _norm(x)), None)
                return {"status": "partly verified", "file": p, "line": line}
    return {"status": "file not found" if path and not cited else "quote not found"}


def _tokens(s):
    return {w for w in re.findall(r"[a-z0-9_]+", (s or "").lower()) if w not in STOP and len(w) > 2}


def _similar(a, b):
    if a["reviewer"] == b["reviewer"]:
        return False
    fa, fb = a.get("vfile") or a.get("file"), b.get("vfile") or b.get("file")
    la, lb = a.get("vline") or a.get("line_start"), b.get("vline") or b.get("line_start")
    if fa and fb and fa == fb and la and lb and abs(la - lb) <= 8:
        return True
    ta, tb = _tokens(a["title"] + " " + a.get("evidence", "")[:200]), _tokens(b["title"] + " " + b.get("evidence", "")[:200])
    if not ta or not tb:
        return False
    jac = len(ta & tb) / len(ta | tb)
    same_file = fa and fb and fa == fb
    return (a["category"] == b["category"] and jac >= 0.35) or (same_file and jac >= 0.25)


def compare(reviews, ws):
    """reviews: {reviewer_id: review}. Returns the comparison structure stored as comparison.json."""
    reviewers = sorted(reviews)
    findings = []
    for rid in reviewers:
        for i, f in enumerate(reviews[rid]["findings"]):
            v = verify(f, ws)
            f["verification"] = v
            findings.append(dict(f, reviewer=rid, key=f"{rid}:{i}", vfile=v.get("file"), vline=v.get("line")))

    # Group findings that describe the same problem (greedy, at most one finding per reviewer per group).
    groups = []
    for f in sorted(findings, key=lambda x: -SEV_RANK[x["severity"]]):
        for g in groups:
            if f["reviewer"] not in {m["reviewer"] for m in g} and any(_similar(f, m) for m in g):
                g.append(f)
                break
        else:
            groups.append([f])

    n = len(reviewers)
    items = []
    for g in groups:
        sev = [SEV_RANK[m["severity"]] for m in g]
        lead = max(g, key=lambda m: (SEV_RANK[m["severity"]], m["verification"]["status"].startswith("verified")))
        verified = [m for m in g if m["verification"]["status"].startswith(("verified", "partly"))]
        raised = sorted({m["reviewer"] for m in g})
        if len(raised) == n:
            kind = "consensus" if max(sev) - min(sev) <= 1 else "severity dispute"
        elif len(raised) > 1:
            kind = "partial" if max(sev) - min(sev) <= 1 else "severity dispute"
        else:
            kind = "single"
        important = max(sev) >= SEV_RANK["major"]
        disputed = kind == "severity dispute" or (kind in ("single", "partial") and important)
        unverified = not verified and any(m.get("evidence") for m in g)
        items.append({
            "title": lead["title"], "category": lead["category"], "severity": lead["severity"],
            "kind": kind, "disputed": disputed and not unverified, "unverified": unverified,
            "raised_by": raised, "severities": [m["severity"] for m in g],
            "file": lead.get("vfile") or lead.get("file"), "line": lead.get("vline") or lead.get("line_start"),
            "findings": [{k: m.get(k) for k in ("reviewer", "severity", "title", "file", "line_start", "line_end",
                                                  "evidence", "explanation", "suggestion", "confidence", "verification")}
                         for m in sorted(g, key=lambda m: m["reviewer"])]})
    items.sort(key=lambda it: (not it["disputed"], it["kind"] != "consensus", -SEV_RANK[it["severity"]], it["title"]))

    matrix, rating_disputes = {}, {}
    for c in CRITERIA:
        row = {rid: reviews[rid]["ratings"][c]["rating"] for rid in reviewers}
        matrix[c] = row
        ranks = [RATING_RANK[v] for v in row.values() if v in RATING_RANK]
        if len(ranks) >= 2 and max(ranks) - min(ranks) >= 2:
            rating_disputes[c] = row
    overall = {rid: reviews[rid]["overall"] for rid in reviewers}

    disputes, k = [], 0
    for it in items:
        if it["disputed"]:
            k += 1
            it["id"] = f"D{k}"
            disputes.append(it)
    for c, row in rating_disputes.items():
        k += 1
        disputes.append({"id": f"D{k}", "title": f"Rating of {c}", "category": c, "severity": "major", "kind": "rating dispute",
                         "raised_by": sorted(row), "severities": [], "findings": [], "rating_dispute": row})
    return {"reviewers": reviewers, "items": items, "matrix": matrix, "overall": overall,
            "disputes": [d["id"] for d in disputes], "dispute_items": disputes,
            "counts": {"consensus": sum(it["kind"] == "consensus" for it in items),
                       "disputed": len(disputes), "single": sum(it["kind"] == "single" for it in items),
                       "unverified": sum(it["unverified"] for it in items), "total": len(items)}}


def _median(values, order):
    ranked = sorted(order.index(v) for v in values)
    return order[ranked[(len(ranked) - 1) // 2]] if ranked else None  # lower median on ties


def apply_positions(comparison, positions):
    """positions: {reviewer_id: [{item, real, severity, rating, reason}]}. Summarizes each dispute after re-checking."""
    by_id = {d["id"]: d for d in comparison["dispute_items"]}
    for rid, plist in positions.items():
        for p in plist:
            d = by_id.get(p["item"])
            if d is not None:
                d.setdefault("positions", {})[rid] = p
    rating_order = [r for r in RATINGS if r != "unknown"]
    for d in comparison["dispute_items"]:
        ps = list((d.get("positions") or {}).values())
        if not ps:
            d["outcome"] = "not re-checked"
            continue
        if d.get("rating_dispute"):
            given = [p["rating"] for p in ps if p.get("rating") in rating_order]
            if given:
                ranks = [rating_order.index(g) for g in given]
                settled = max(ranks) - min(ranks) <= 1
                d["outcome"] = (f"settled: {_median(given, rating_order)}" if settled else "still disputed") + f" ({', '.join(given)})"
            else:
                d["outcome"] = "still disputed"
            continue
        yes = [p for p in ps if p["real"] == "yes"]
        no = [p for p in ps if p["real"] == "no"]
        if len(yes) * 2 > len(ps):
            sev = _median([p["severity"] or d["severity"] for p in yes], SEVERITIES)
            d["outcome"] = f"real, {sev} ({len(yes)} of {len(ps)})"
            d["settled_severity"] = sev
        elif len(no) * 2 > len(ps):
            d["outcome"] = f"not a problem ({len(no)} of {len(ps)})"
        else:
            d["outcome"] = "still disputed"
    comparison["counts"]["open_disputes"] = sum(d.get("outcome", "").startswith(("still", "not re-checked"))
                                                for d in comparison["dispute_items"])
    return comparison


def needs_escalation(reviews, comparison):
    """For a first-pass (triage) review: does this extension deserve the full panel?"""
    if comparison["counts"]["disputed"] or comparison["counts"]["unverified"]:
        return True
    for r in reviews.values():
        if r["overall"] in ("needs fixes", "do not accept", "incomplete"):
            return True
        if any(v["rating"] in ("concern", "blocking") for v in r["ratings"].values()):
            return True
        if any(f["severity"] in ("major", "blocking") for f in r["findings"]):
            return True
    return False
