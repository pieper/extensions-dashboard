// One AI review: ratings side by side, disagreements first, then agreed and single-reviewer findings.
(function () {
  "use strict";
  var U = window.TriageUtil, h = U.h, a = U.a;
  var NAME_RE = /^[A-Za-z0-9][A-Za-z0-9_.+-]{0,99}$/, DIR_RE = /^[0-9a-f]{12}-(full|triage)$/;
  var meta, labels = {};

  function verification(v) {
    var st = (v && v.status) || "n/a";
    var cls = /^verified/.test(st) ? "good" : st === "partly verified" ? "warn" : st === "no quote" || st === "n/a" ? "info" : "bad";
    return h("span", { class: "hint " + cls, text: "quote " + st });
  }

  function where(f) {
    var v = f.verification || {}, path = v.file || f.file, line = v.line || f.line_start;
    if (!path) return h("span", { class: "by", text: "no file cited" });
    return a(U.sourceUrl(meta.scm_url, meta.commit, path, line), path + (line ? ":" + line : ""), "code");
  }

  function finding(f) {
    return h("div", { class: "finding" },
      h("div", { class: "head" }, h("span", { class: "who", text: labels[f.reviewer] || f.reviewer }),
        h("span", { class: "pill " + sevClass(f.severity), text: f.severity }), h("span", { class: "by", text: f.confidence + " confidence" }),
        where(f), verification(f.verification)),
      f.title ? h("div", { class: "step", text: f.title }) : null,
      h("div", { class: "ctx", text: f.explanation }),
      f.evidence ? h("pre", { class: "entry", text: f.evidence }) : null,
      f.suggestion ? h("div", { class: "by", text: "Suggestion: " + f.suggestion }) : null);
  }

  function sevClass(s) { return s === "blocking" ? "bad" : s === "major" ? "warn" : s === "minor" ? "muted" : "muted"; }

  function item(it, open) {
    var det = h("details", { class: "pr", open: open || null });
    det.appendChild(h("summary", null,
      h("span", { class: "stripe " + sevClass(it.severity) }),
      h("span", { class: "prnum", text: it.id || "" }),
      h("span", { class: "s-name" }, it.title, h("span", { class: "by", text: it.category + " · raised by " + it.raised_by.map(function (r) { return labels[r] || r; }).join(", ") })),
      h("span", { class: "pill " + sevClass(it.severity), text: it.kind === "rating dispute" ? "ratings differ" : it.severities.join(" / ") || it.severity }),
      it.outcome ? h("span", { class: "pill " + (/confirmed/.test(it.outcome) ? "warn" : /rejected/.test(it.outcome) ? "ok" : "new"), text: it.outcome }) :
        it.unverified ? h("span", { class: "pill bad", text: "quote not found" }) : h("span"),
      h("span")));
    var body = h("div", { class: "body" });
    if (it.rating_dispute) {
      body.appendChild(h("p", { class: "ctx", text: "Ratings of " + it.category + ": " + Object.keys(it.rating_dispute).map(function (k) { return (labels[k] || k) + " " + it.rating_dispute[k]; }).join(", ") }));
    }
    (it.findings || []).forEach(function (f) { body.appendChild(finding(f)); });
    var pos = it.positions || {};
    if (Object.keys(pos).length) {
      body.appendChild(h("h4", { text: "On re-check, each model said" }));
      body.appendChild(h("ul", { class: "hintlist" }, Object.keys(pos).map(function (k) {
        var p = pos[k];
        return h("li", { class: p.position === "agree" ? "warn" : p.position === "disagree" ? "" : "info" },
          h("b", { text: (labels[k] || k) + ": " + p.position + (p.severity ? " (" + p.severity + ")" : "") }), " " + p.reason);
      })));
    }
    det.appendChild(body);
    return det;
  }

  function render(comparison, reviews, summary) {
    var rids = comparison ? comparison.reviewers : Object.keys(reviews);
    meta.reviewers.forEach(function (r) { labels[r.id] = r.label || r.id; });
    document.getElementById("title").textContent = "AI review: " + meta.extension;
    document.title = "AI review: " + meta.extension;
    U.fill(document.getElementById("sub"), 
      a(meta.scm_url.replace(/\.git$/, ""), meta.scm_url.replace(/^https?:\/\//, "").replace(/\.git$/, "")), " at ",
      a(meta.scm_url.replace(/\.git$/, "") + "/tree/" + meta.commit, meta.commit.slice(0, 12)),
      " · " + (meta.pr ? "PR " : "catalog entry"), meta.pr ? a("https://github.com/Slicer/ExtensionsIndex/pull/" + meta.pr, "#" + meta.pr) : null,
      " · " + (meta.panel === "full" ? "full panel" : "first-pass panel") + " · " + U.fmtDate(meta.finished) + " · $" + meta.cost.toFixed(2));
    var v = summary && summary.verdict;
    U.fill(document.getElementById("verdict"), v ? h("p", null, h("span", { class: "pill " + U.VERDICT[v][1], text: U.VERDICT[v][0] }), " ", summary.issue ? a(summary.issue.url, "discussion") : null) :
      h("p", { class: "by" }, "No maintainer verdict yet.", summary && summary.issue ? [" ", a(summary.issue.url, "Review issue")] : meta.panel === "triage" ? " First-pass reviews get a maintainer issue only if they are escalated to the full panel." : null));

    // Ratings matrix
    var crit = comparison ? Object.keys(comparison.matrix) : [];
    var disputedCrit = {};
    (comparison ? comparison.dispute_items : []).forEach(function (d) { if (d.rating_dispute) disputedCrit[d.category] = true; });
    var rows = crit.map(function (c) {
      return h("tr", { class: disputedCrit[c] ? "disputed" : "" }, h("th", { text: c + (disputedCrit[c] ? " ⚠" : "") }),
        rids.map(function (r) { var val = comparison.matrix[c][r] || "unknown"; return h("td", null, h("span", { class: "pill " + (U.RATING_CLASS[val] || "muted"), text: val })); }));
    });
    if (comparison) rows.push(h("tr", { class: "overall" }, h("th", { text: "overall" }), rids.map(function (r) {
      var val = comparison.overall[r]; return h("td", null, h("span", { class: "pill " + (U.OVERALL_CLASS[val] || "muted"), text: val }));
    })));
    var failed = meta.reviewers.filter(function (r) { return !r.ok; });
    U.fill(document.getElementById("matrix-section"), h("h2", { text: "Ratings" }),
      h("div", { class: "tablewrap" }, h("table", { class: "rtable matrix" },
        h("thead", null, h("tr", null, h("th"), rids.map(function (r) {
          var m = meta.reviewers.find(function (x) { return x.id === r; }) || {};
          return h("th", null, labels[r] || r, h("span", { class: "by block", text: m.model || "" }));
        }))), h("tbody", null, rows))),
      failed.length ? h("p", { class: "by", text: "Did not finish: " + failed.map(function (r) { return (r.label || r.id) + " (" + (r.error || "error") + ")"; }).join("; ") }) : null);

    var items = comparison ? comparison.items : [];
    var disputes = comparison ? comparison.dispute_items : [];
    U.fill(document.getElementById("disputes-section"), 
      h("h2", null, "Where the models disagree ", h("span", { class: "count", text: String(disputes.length) })),
      disputes.length ? h("div", { class: "list" }, disputes.map(function (d) { return item(d, true); })) : h("p", { class: "empty", text: "No disagreements on serious findings or ratings." }));
    var agreed = items.filter(function (it) { return it.kind === "consensus" && !it.id; });
    U.fill(document.getElementById("agreed-section"), 
      h("h2", null, "All models agree ", h("span", { class: "count", text: String(agreed.length) })),
      agreed.length ? h("div", { class: "list" }, agreed.map(function (it) { return item(it, it.severity === "blocking" || it.severity === "major"); })) : h("p", { class: "empty", text: "No finding was raised by every model." }));
    var other = items.filter(function (it) { return it.kind !== "consensus" && !it.id; });
    U.fill(document.getElementById("other-section"), 
      h("h2", null, "Raised by some models ", h("span", { class: "count", text: String(other.length) })),
      other.length ? h("div", { class: "list" }, other.map(function (it) { return item(it, false); })) : h("p", { class: "empty", text: "None." }));

    U.fill(document.getElementById("summaries-section"), h("h2", { text: "What each model wrote" }),
      h("div", { class: "cardgrid" }, rids.map(function (r) {
        var rv = reviews[r] || {};
        return h("li", null, h("div", { class: "head" }, h("span", { class: "name", text: labels[r] || r }),
          h("span", { class: "pill " + (U.OVERALL_CLASS[rv.overall] || "muted"), text: rv.overall || "" })),
          h("div", { class: "what", text: rv.purpose || "" }), h("div", { class: "ctx", text: rv.summary || "" }),
          (rv.not_checked || []).length ? h("div", { class: "by", text: "Not checked: " + rv.not_checked.join("; ") }) : null,
          (rv.questions_for_author || []).length ? h("div", { class: "by", text: "Questions for the author: " + rv.questions_for_author.join("; ") }) : null,
          h("div", { class: "links" }, U.local("reviews/" + encodeURIComponent(meta.extension) + "/" + meta.commit.slice(0, 12) + "-" + meta.panel + "/" + encodeURIComponent(r) + ".json", "raw JSON")));
      })));
    var tokens = meta.reviewers.map(function (r) { return (r.label || r.id) + ": " + r.turns + " turns, " + r.tool_calls + " file reads/searches, $" + (r.cost || 0).toFixed(3); }).join(" · ");
    U.fill(document.getElementById("foot"), h("p", { text: meta.files + " files in the repository. " + tokens }),
      h("p", { text: "Review policy: the Slicer Extensions Index AGENTS.md plus this dashboard's rubric. Made with Claude (Anthropic's AI assistant) under @pieper's direction." }));
  }

  function init() {
    var p = new URLSearchParams(location.search);
    var ext = p.get("ext") || "", dir = p.get("dir") || "";
    if (!NAME_RE.test(ext) || !DIR_RE.test(dir)) { document.getElementById("sub").textContent = "No review selected."; return; }
    var base = "reviews/" + encodeURIComponent(ext) + "/" + dir + "/";
    U.getJSON(base + "meta.json").then(function (m) {
      meta = m;
      var ids = m.reviewers.filter(function (r) { return r.ok; }).map(function (r) { return r.id; });
      return Promise.all([U.getJSON(base + "comparison.json").catch(function () { return null; }),
        Promise.all(ids.map(function (id) { return U.getJSON(base + encodeURIComponent(id) + ".json").catch(function () { return {}; }); })),
        U.getJSON("data.json").catch(function () { return {}; })]).then(function (res) {
        var reviews = {};
        ids.forEach(function (id, i) { reviews[id] = res[1][i]; });
        render(res[0], reviews, ((res[2] || {}).reviews || {})[ext]);
      });
    }).catch(function (e) { document.getElementById("sub").textContent = "Could not load this review (" + e.message + ")."; });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
