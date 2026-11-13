// All AI reviews: one row per extension, newest review first, with filters for what needs a human.
(function () {
  "use strict";
  var U = window.TriageUtil, h = U.h, a = U.a;
  var state = { rows: [], filter: "all", term: "" };

  var FILTERS = [["all", "All"], ["needs", "Needs a maintainer"], ["disputed", "Models disagree"], ["escalated", "Flagged by first pass"],
    ["verdict", "Has a verdict"], ["pr", "Open PRs"]];

  function matches(r, f) {
    switch (f) {
      case "needs": return r.full && !r.verdict;
      case "disputed": return (r.latest.counts || {}).disputed > 0;
      case "escalated": return r.latest.escalate || (r.full && r.firstEscalated);
      case "verdict": return !!r.verdict;
      case "pr": return r.latest.source === "pr";
      default: return true;
    }
  }

  function render() {
    var term = state.term.toLowerCase().trim();
    var rows = state.rows.filter(function (r) { return matches(r, state.filter) && (!term || (r.ext + " " + (r.latest.owner || "")).toLowerCase().indexOf(term) >= 0); });
    var head = h("tr", null, ["Extension", "Context", "Reviewed", "Panel", "What the models say", "Disputes", "Unverified quotes", "Maintainer", ""]
      .map(function (t) { return h("th", { text: t }); }));
    var body = rows.map(function (r) {
      var l = r.latest, c = l.counts || {}, worst = U.worstOverall(l.overall);
      var verdict = r.verdict ? h("span", { class: "pill " + U.VERDICT[r.verdict][1], text: r.verdict }) :
        r.issue ? a(r.issue.url, r.issue.state === "open" ? "open issue" : "issue closed") : h("span", { class: "by", text: r.full ? "not yet" : "n/a" });
      return h("tr", null,
        h("td", null, h("span", { class: "name", text: r.ext }), h("span", { class: "by block", text: l.owner || "" })),
        h("td", { text: l.source === "pr" ? "PR " + l.pr : "catalog" }),
        h("td", { class: "num", text: U.fmtDays(U.daysSince(l.finished)) }),
        h("td", { text: l.panel === "full" ? "full" : "first pass" + (l.escalate ? " → flagged" : "") }),
        h("td", null, h("span", { class: "pill " + (U.OVERALL_CLASS[worst] || "muted"), text: worst }), " ", h("span", { class: "by", text: U.overallText(l.overall) })),
        h("td", { class: "num" + (c.disputed ? " hot" : ""), text: String(c.disputed || 0) }),
        h("td", { class: "num" + (c.unverified ? " hot" : ""), text: String(c.unverified || 0) }),
        h("td", null, verdict),
        h("td", null, U.local("review.html?ext=" + encodeURIComponent(r.ext) + "&dir=" + encodeURIComponent(l.dir), "Open review")));
    });
    var table = document.getElementById("table");
    table.replaceChildren(h("thead", null, head), h("tbody", null, body.length ? body : h("tr", null, h("td", { colspan: "9", class: "empty", text: "No reviews match." }))));
    var fb = document.getElementById("filters");
    fb.replaceChildren.apply(fb, FILTERS.map(function (f) {
      return h("button", { class: "fbtn" + (state.filter === f[0] ? " on" : ""), type: "button", text: f[1],
        onclick: function () { state.filter = state.filter === f[0] ? "all" : f[0]; render(); } });
    }));
  }

  function tiles(rows, spent) {
    var t = [["Extensions reviewed", rows.length], ["Full-panel reviews", rows.filter(function (r) { return r.full; }).length],
      ["Need a maintainer", rows.filter(function (r) { return r.full && !r.verdict; }).length],
      ["With disagreements", rows.filter(function (r) { return (r.latest.counts || {}).disputed > 0; }).length],
      ["Spent this month", "$" + spent.toFixed(2)]];
    document.getElementById("tiles").replaceChildren.apply(document.getElementById("tiles"), t.map(function (x) {
      return h("div", { class: "tile static" }, h("span", { class: "tv", text: String(x[1]) }), h("span", { class: "tl", text: x[0] }));
    }));
  }

  function init() {
    Promise.all([U.getJSON("reviews/index.json"), U.getJSON("data.json").catch(function () { return {}; })]).then(function (res) {
      var index = res[0] || {}, data = res[1] || {}, summaries = data.reviews || {};
      var month = new Date().toISOString().slice(0, 7), spent = 0;
      state.rows = Object.keys(index).filter(function (ext) { return index[ext].length; }).map(function (ext) {
        var runs = index[ext];
        runs.forEach(function (r) { if ((r.finished || "").slice(0, 7) === month) spent += r.cost || 0; });
        var s = summaries[ext] || {};
        return { ext: ext, latest: runs[runs.length - 1], full: runs.some(function (r) { return r.panel === "full"; }),
          firstEscalated: runs.some(function (r) { return r.escalate; }), verdict: s.verdict, issue: s.issue };
      }).sort(function (x, y) { return (y.latest.finished || "").localeCompare(x.latest.finished || ""); });
      U.fill(document.getElementById("sub"), "Reviews of extensions in the ",
        a("https://github.com/Slicer/ExtensionsIndex", "Slicer Extensions Index"), " and its open pull requests.");
      document.getElementById("foot").textContent = "Made with Claude (Anthropic's AI assistant) under @pieper's direction. Review files are kept in this site's repository under reviews/.";
      tiles(state.rows, spent);
      render();
    }).catch(function (e) { document.getElementById("sub").textContent = "Could not load the reviews (" + e.message + ")."; });
    document.getElementById("q").addEventListener("input", function (e) { state.term = e.target.value; render(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
