"""Human-readable Markdown for a review: report.md, its GitHub issue, and a draft comment for the maintainer."""

import re

DISCLAIMER = ("> **AI-generated review, not yet checked by a maintainer.** Several AI models (listed below) read this "
              "extension's source as text; nothing was run. Findings can be wrong. Quotes were checked automatically "
              "against the source; anything marked *unverified* may be invented. A Slicer maintainer's verdict, when "
              "there is one, is shown on the dashboard.")


def neutralize(text):
    """Keep model-written text from pinging people or cross-linking issues when shown on GitHub."""
    t = str(text or "")
    t = re.sub(r"@(?=[A-Za-z0-9])", "@​", t)
    t = re.sub(r"(?<![\w/])#(?=\d)", "#​", t)
    t = re.sub(r"(github\.com/[^\s)]+/(?:issues|pull))/(\d+)", r"\1/​\2", t)
    return t


def _src_link(meta, path, line=None):
    url = (meta.get("scm_url") or "").removesuffix(".git").rstrip("/")
    if "github.com/" not in url or not path:
        return f"`{path}`" + (f" line {line}" if line else "")
    return f"[`{path}{f':{line}' if line else ''}`]({url}/blob/{meta['commit']}/{path}{f'#L{line}' if line else ''})"


def render_report(meta, reviews, comparison):
    lab = {r["id"]: f"{r.get('label', r['id'])} (`{r['model']}`)" for r in meta["reviewers"]}
    out = [f"# AI review: {meta['extension']}", "", DISCLAIMER, "",
           f"- Source: {meta['scm_url']} at commit `{meta['commit']}`",
           f"- Context: {'pull request ' + str(meta['pr']) + ' to the Extensions Index' if meta.get('pr') else 'Extensions Index catalog entry'}",
           f"- Panel: {meta['panel']} ({', '.join(lab.values())})",
           f"- Reviewed {meta['finished']}; cost ${meta['cost']:.2f}"]
    failed = [r for r in meta["reviewers"] if not r.get("ok")]
    if failed:
        out.append("- Reviewers that did not finish: " + "; ".join(f"{r['id']}: {r.get('error', '')}" for r in failed))
    if not comparison:
        out += ["", "No reviewer finished, so there is nothing to compare."]
        return "\n".join(out) + "\n"
    out += ["", "## Overall", "", "| Criterion | " + " | ".join(comparison["reviewers"]) + " |",
            "|---|" + "---|" * len(comparison["reviewers"])]
    for c, row in comparison["matrix"].items():
        out.append(f"| {c} | " + " | ".join(row[r] for r in comparison["reviewers"]) + " |")
    out.append("| **overall** | " + " | ".join(comparison["overall"][r] for r in comparison["reviewers"]) + " |")

    out += ["", "## What each reviewer says the extension does", ""]
    for rid in comparison["reviewers"]:
        out.append(f"- **{rid}**: {neutralize(reviews[rid]['purpose'])}")

    if comparison["dispute_items"]:
        out += ["", "## Disagreements (start here)", ""]
        for d in comparison["dispute_items"]:
            out.append(f"### {d['id']}. {neutralize(d['title'])}")
            out.append(f"{d['kind']}; category {d['category']}; raised by {', '.join(d['raised_by'])}"
                       + (f"; outcome after cross-examination: **{d['outcome']}**" if d.get("outcome") else ""))
            if d.get("rating_dispute"):
                out.append("Ratings: " + ", ".join(f"{k} {v}" for k, v in d["rating_dispute"].items()))
            for f in d["findings"]:
                out += _finding_lines(meta, f)
            for rid, p in (d.get("positions") or {}).items():
                verdict = f"rating {p['rating']}" if p.get("rating") else f"real: {p.get('real', '?')}" + (f", {p['severity']}" if p.get("severity") else "")
                out.append(f"- {rid} on re-check: **{verdict}**: {neutralize(p['reason'])}")
            out.append("")

    for title, kinds in (("Findings all reviewers agree on", ("consensus",)),
                         ("Findings from some reviewers", ("partial", "single", "severity dispute"))):
        rows = [it for it in comparison["items"] if it["kind"] in kinds and not it.get("id")]
        if rows:
            out += ["", f"## {title}", ""]
            for it in rows:
                out.append(f"### {neutralize(it['title'])}")
                out.append(f"{it['severity']}; {it['category']}; raised by {', '.join(it['raised_by'])}"
                           + ("; **quote not found in source**" if it["unverified"] else ""))
                for f in it["findings"]:
                    out += _finding_lines(meta, f)
                out.append("")

    out += ["", "## Reviewer summaries", ""]
    for rid in comparison["reviewers"]:
        r = reviews[rid]
        out.append(f"### {lab.get(rid, rid)}: {r['overall']}")
        out.append(neutralize(r["summary"]))
        if r["not_checked"]:
            out.append("Not checked: " + "; ".join(neutralize(x) for x in r["not_checked"]))
        if r["questions_for_author"]:
            out.append("Questions for the author: " + "; ".join(neutralize(x) for x in r["questions_for_author"]))
        out.append("")
    return "\n".join(out) + "\n"


def _finding_lines(meta, f):
    v = f.get("verification") or {}
    where = _src_link(meta, v.get("file") or f.get("file"), v.get("line") or f.get("line_start")) if (v.get("file") or f.get("file")) else "no file cited"
    lines = [f"- **{f['reviewer']}** ({f['severity']}, {f['confidence']} confidence, quote {v.get('status', 'n/a')}) {where}: "
             f"{neutralize(f['explanation'])}"]
    if f.get("evidence"):
        q = f["evidence"].replace("```", "'''")
        lines.append("  ```\n  " + "\n  ".join(q.splitlines()[:6]) + "\n  ```")
    if f.get("suggestion"):
        lines.append(f"  Suggestion: {neutralize(f['suggestion'])}")
    return lines


def render_issue(meta, comparison, report_url, dashboard_url):
    """Issue body: what a maintainer needs to decide, with links to the full report."""
    c = comparison or {"counts": {}, "dispute_items": [], "matrix": {}, "overall": {}, "reviewers": []}
    out = [DISCLAIMER, "",
           f"**{meta['extension']}** at commit `{meta['commit'][:12]}` ({'extension pull request' if meta.get('pr') else 'catalog entry'}), "
           f"reviewed by {len(c['reviewers'])} models.",
           f"[Full review]({report_url}) · [Dashboard]({dashboard_url})", "",
           "Overall, by reviewer: " + ", ".join(f"{r}: **{c['overall'].get(r)}**" for r in c["reviewers"]), ""]
    if c["dispute_items"]:
        out += ["### Disagreements to settle", ""]
        for d in c["dispute_items"]:
            out.append(f"- [ ] **{d['id']}. {neutralize(d['title'])}** ({d['category']}; raised by {', '.join(d['raised_by'])}"
                       + (f"; after re-check: {d['outcome']}" if d.get("outcome") else "") + ")")
    blocking = [it for it in c.get("items", []) if it["kind"] == "consensus" and it["severity"] in ("blocking", "major")]
    if blocking:
        out += ["", "### Agreed serious findings", ""]
        out += [f"- [ ] {neutralize(it['title'])} ({it['severity']}, {it['category']})" for it in blocking]
    draft = render_pr_comment(meta, comparison, report_url).replace("~~~~", "~~~")
    out += ["", f"### Draft comment (suggested action: {suggested_action(comparison)})",
            "Edit as needed and paste it on the pull request; nothing is posted automatically.", "",
            "~~~~markdown", draft.rstrip(), "~~~~"]
    out += ["", "### To finish this review",
            "Check the items above against the source, comment with what you found, then add one label: "
            "`verdict: ok`, `verdict: concerns` or `verdict: blocking`, and close the issue. "
            "The dashboard shows that label as the maintainer verdict for this extension."]
    return "\n".join(out) + "\n"


SEV_ORDER = ["info", "minor", "major", "blocking"]


def _median_sev(sevs):
    ranks = sorted(SEV_ORDER.index(x) for x in sevs if x in SEV_ORDER)
    return SEV_ORDER[ranks[(len(ranks) - 1) // 2]] if ranks else "minor"


def actionable_findings(comparison, limit=8):
    """Findings a maintainer would pass on: those most models judged real, plus verified single-model notes.

    Unsettled disputes are left out; the maintainer decides those on the review page.
    """
    if not comparison:
        return []
    n = len(comparison["reviewers"])
    picked = []
    for d in comparison["dispute_items"]:
        if d.get("settled_severity") and str(d.get("outcome", "")).startswith("real"):
            picked.append((d["settled_severity"], 0, d))
    for it in comparison["items"]:
        if it.get("id") or it["unverified"]:
            continue
        verified = any(str((f.get("verification") or {}).get("status", "")).startswith(("verified", "partly")) for f in it["findings"])
        if not verified:
            continue
        if len(it["raised_by"]) * 2 > n or it["kind"] == "consensus":
            picked.append((_median_sev(it["severities"]), 1, it))
        elif it["severity"] in ("minor", "major") and it["kind"] == "single":
            picked.append((it["severity"], 2, it))
    picked = [p for p in picked if p[0] != "info"]
    picked.sort(key=lambda p: (-SEV_ORDER.index(p[0]), p[1]))
    return [(sev, it) for sev, _, it in picked[:limit]]


def suggested_action(comparison):
    found = actionable_findings(comparison)
    if any(sev == "blocking" for sev, _ in found):
        return "changes needed"
    if comparison and comparison["counts"].get("open_disputes"):
        return "decide disputes first"
    return "merge with suggestions" if found else "merge"


def _finding_line(meta, sev, it):
    f = next((x for x in it["findings"] if str((x.get("verification") or {}).get("status", "")).startswith("verified")),
             it["findings"][0] if it["findings"] else {})
    v = f.get("verification") or {}
    path, line = v.get("file") or f.get("file"), v.get("line") or f.get("line_start")
    end = f.get("line_end") if f.get("line_end") and line and f.get("line_end") > line and f.get("line_end") - line < 15 else None
    url = (meta.get("scm_url") or "").removesuffix(".git").rstrip("/")
    if path and "github.com/" in url:
        anchor = f"#L{line}" + (f"-L{end}" if end else "") if line else ""
        where = f"[`{path}{f':{line}' if line else ''}{f'-{end}' if end else ''}`]({url}/blob/{meta['commit']}/{path}{anchor})"
    else:
        where = f"`{path}`" if path else ""
    text = neutralize(f.get("explanation") or it["title"]).strip()
    if f.get("suggestion"):
        text += " " + neutralize(f["suggestion"]).strip()
    return f"- {where}{': ' if where else ''}{text}"


def render_pr_comment(meta, comparison, review_url):
    """A comment the maintainer can paste on the pull request (or into an issue on the extension's repository)."""
    models = ", ".join(r.get("label") or r["model"] for r in meta["reviewers"] if r.get("ok"))
    found = actionable_findings(comparison)
    blocking = [x for x in found if x[0] == "blocking"]
    other = [x for x in found if x[0] != "blocking"]
    out = [f"> *This review was done by AI models ({models}) through the Slicer extensions dashboard, and checked by the "
           f"maintainer posting it. The extension source was read, not executed. Full review: {review_url}*", "",
           f"Thanks for {meta['extension']}!"]
    if blocking:
        out += ["", "Please fix these before the extension can be merged:", ""]
        out += [_finding_line(meta, sev, it) for sev, it in blocking]
    if other:
        out += ["", "Suggestions for a later update:" if not blocking else "Smaller suggestions:", ""]
        out += [_finding_line(meta, sev, it) for sev, it in other]
    if not found:
        out += ["", "The review found nothing that needs changing."]
    return "\n".join(out) + "\n"
