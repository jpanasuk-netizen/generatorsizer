/* Read generator-tab params and run the existing calculator. */
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function show() {
    if (!$("tab-gen") || typeof showTab !== "function") return;
    showTab("tab-gen", document.querySelector('button[onclick*="tab-gen"]'));
  }
  function parseLd(s) {
    var parts = String(s).split(","), out = [], i, g, a, b, q;
    for (i = 0; i < parts.length; i++) {
      g = parts[i].split("-");
      if (g.length !== 3) return null;
      a = GSShare.num(g[0], 0, null);
      b = GSShare.num(g[1], 0, null);
      q = GSShare.num(g[2], 1, null);
      if (a == null || b == null || q == null) return null;
      out.push({ name: "Load " + (i + 1), run: a, surge: b, qty: q });
    }
    return out.length ? out : null;
  }
  function setLoads(arr) {
    loads.length = 0;
    arr.forEach(function (l) {
      addLoad(l.name, l.run, l.surge);
      loads[loads.length - 1].qty = l.qty;
    });
    renderLoads();
  }
  function apply(params) {
    var changed = false, groups, h, hr, tk;
    if (params.has("ld")) {
      groups = parseLd(params.get("ld"));
      if (groups) { setLoads(groups); changed = true; }
    } else if (params.has("w") || params.has("s")) {
      h = GSShare.num(params.get("w"), 0, null);
      hr = GSShare.num(params.get("s"), 0, null);
      if (h != null && hr != null) { setLoads([{ name: "Custom load", run: h, surge: hr, qty: 1 }]); changed = true; }
    }
    h = params.has("h") ? GSShare.num(params.get("h"), 0, 100) : null;
    hr = params.has("hr") ? GSShare.num(params.get("hr"), 1, 24) : null;
    tk = params.has("tk") ? GSShare.num(params.get("tk"), 0.5, null) : null;
    if (h != null) { $("headroom").value = h; changed = true; }
    if (hr != null) { $("hrsDay").value = hr; changed = true; }
    if (tk != null) { $("tankGal").value = tk; changed = true; }
    if (!changed) return;
    show();
    sizeGenerator();
  }
  document.addEventListener("DOMContentLoaded", function () {
    if (!$("genResult")) return;
    var params = new URLSearchParams(location.search), tab = params.get("tab");
    var keys = ["ld", "w", "s", "h", "hr", "tk"];
    if (tab && tab !== "gen") return;
    if (!keys.some(function (k) { return params.has(k); })) return;
    apply(params);
  });
})();
