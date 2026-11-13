"""Human-readable Markdown for a review (report.md) and for its GitHub issue."""

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
    out += ["", "### To finish this review",
            "Check the items above against the source, comment with what you found, then add one label: "
            "`verdict: ok`, `verdict: concerns` or `verdict: blocking`, and close the issue. "
            "The dashboard shows that label as the maintainer verdict for this extension."]
    return "\n".join(out) + "\n"
