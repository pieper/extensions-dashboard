// Helpers shared by the review pages. All text from GitHub or from AI reviewers is untrusted: it is inserted
// as text, never as HTML, and links are made only from http(s) URLs.
(function () {
  "use strict";

  function h(tag, props) {
    var el = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (k) {
        var v = props[k];
        if (v === undefined || v === null || v === false) return;
        if (k === "class") el.className = v;
        else if (k === "text") el.textContent = v;
        else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), v);
        else el.setAttribute(k, v === true ? "" : v);
      });
    }
    for (var i = 2; i < arguments.length; i++) add(el, arguments[i]);
    return el;
  }
  function add(el, kid) {
    if (kid === undefined || kid === null || kid === false) return;
    if (Array.isArray(kid)) { kid.forEach(function (k) { add(el, k); }); return; }
    el.appendChild(typeof kid === "string" || typeof kid === "number" ? document.createTextNode(String(kid)) : kid);
  }
  // replaceChildren() would print null as text; this skips empty pieces like h() does.
  function fill(el) {
    el.replaceChildren();
    for (var i = 1; i < arguments.length; i++) add(el, arguments[i]);
    return el;
  }
  function safeUrl(u) { return typeof u === "string" && /^https?:\/\//i.test(u) ? u : null; }
  function a(url, text, cls) {
    var u = safeUrl(url);
    if (!u) return h("span", { class: cls }, text);
    return h("a", { href: u, target: "_blank", rel: "noopener noreferrer", class: cls }, text);
  }
  function local(url, text, cls) { return h("a", { href: url, class: cls }, text); }
  function daysSince(t) { return t ? (Date.now() - Date.parse(t)) / 86400000 : 0; }
  function fmtDays(d) {
    if (d < 1) return "today";
    if (d < 60) return Math.round(d) + "d ago";
    if (d < 730) return Math.round(d / 30.4) + "mo ago";
    return (d / 365).toFixed(1) + "y ago";
  }
  function fmtDate(t) { return t ? new Date(t).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }) : ""; }
  function getJSON(url) {
    return fetch(url, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(url + ": HTTP " + r.status);
      return r.json();
    });
  }
  function getText(url) {
    return fetch(url, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(url + ": HTTP " + r.status);
      return r.text();
    });
  }
  function sourceUrl(scmUrl, commit, path, line) {
    var base = (scmUrl || "").replace(/\.git$/, "").replace(/\/$/, "");
    if (!/^https:\/\/github\.com\//.test(base) || !path) return null;
    return base + "/blob/" + commit + "/" + path.split("/").map(encodeURIComponent).join("/") + (line ? "#L" + line : "");
  }
  var OVERALL_CLASS = { "no concerns": "ok", "minor issues": "ok", "needs fixes": "warn", "do not accept": "bad", "incomplete": "muted" };
  var RATING_CLASS = { ok: "ok", minor: "ok", concern: "warn", blocking: "bad", unknown: "muted" };
  var VERDICT = { ok: ["Maintainer verdict: OK", "ok"], concerns: ["Maintainer verdict: concerns", "warn"], blocking: ["Maintainer verdict: blocking", "bad"] };

  // "2 say needs fixes, 1 says minor issues"
  function overallText(overall) {
    var counts = {};
    Object.keys(overall || {}).forEach(function (k) { counts[overall[k]] = (counts[overall[k]] || 0) + 1; });
    return Object.keys(counts).sort(function (x, y) { return counts[y] - counts[x]; })
      .map(function (k) { return counts[k] + (counts[k] === 1 ? " says " : " say ") + k; }).join(", ");
  }
  function worstOverall(overall) {
    var order = ["do not accept", "needs fixes", "incomplete", "minor issues", "no concerns"];
    var vals = Object.keys(overall || {}).map(function (k) { return overall[k]; });
    for (var i = 0; i < order.length; i++) if (vals.indexOf(order[i]) >= 0) return order[i];
    return "incomplete";
  }

  window.TriageUtil = { h: h, fill: fill, a: a, local: local, safeUrl: safeUrl, daysSince: daysSince, fmtDays: fmtDays, fmtDate: fmtDate,
    getJSON: getJSON, getText: getText, sourceUrl: sourceUrl, OVERALL_CLASS: OVERALL_CLASS, RATING_CLASS: RATING_CLASS, VERDICT: VERDICT,
    overallText: overallText, worstOverall: worstOverall };
})();
