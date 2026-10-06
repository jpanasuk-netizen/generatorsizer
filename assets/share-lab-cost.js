/* Permalink fields for the load sequencer and 5-year cost. House names stay off the URL. */
(function () {
  "use strict";
  function boot() {
    if (!window.GSLabShare) return;
    var stack = document.getElementById("stackPick");
    if (stack && document.getElementById("runBtn")) {
      GSLabShare("runBtn", "out", [
        { id: "stackPick", key: "sk", sel: 1, def: "wellRanch", label: "stack" },
        { id: "headroom", key: "h", min: 0, max: 40, def: 20, label: "headroom %" }
      ], "Load sequencer estimate", function () { if (stack.onchange) stack.onchange(); });
    } else if (document.getElementById("oilCost")) {
      GSLabShare("go", "out", [
        { id: "runW", key: "w", min: 100, max: null, def: 2210, label: "running" },
        { id: "hours", key: "hy", min: 0, max: null, def: 18, label: "outage h/yr" },
        { id: "gas", key: "gp", min: 1, max: null, def: 3.4, label: "$/gal" },
        { id: "port", key: "pp", min: 200, max: null, def: 1400, label: "portable $" },
        { id: "stand", key: "si", min: 3000, max: null, def: 12500, label: "standby $" },
        { id: "svc", key: "sv", min: 0, max: null, def: 280, label: "service $/yr" },
        { id: "oilUnit", key: "ou", sel: 1, def: "hondaEU2200i", label: "oil" },
        { id: "oilCost", key: "oc", min: 0, max: null, omitBlank: 1, label: "oil $" }
      ], "5-year cost estimate");
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
