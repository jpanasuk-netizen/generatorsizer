/* Permalink fields for altitude, noise, storm runbook, and kWh. */
(function () {
  "use strict";
  function boot() {
    if (!window.GSLabShare) return;
    if (document.getElementById("nameplate")) {
      GSLabShare("go", "out", [
        { id: "nameplate", key: "np", min: 500, max: null, def: 7500, label: "nameplate" },
        { id: "elev", key: "ev", min: 0, max: null, def: 1050, label: "ft" },
        { id: "temp", key: "tp", min: -20, max: 130, def: 90, label: "F" },
        { id: "need", key: "nd", min: 0, max: null, def: 4200, label: "need" }
      ], "Altitude derate estimate");
    } else if (document.getElementById("klass")) {
      GSLabShare("go", "out", [
        { id: "klass", key: "k", sel: 1, def: "inverter22", label: "class" },
        { id: "dist", key: "d", min: 3, max: null, def: 25, label: "ft" },
        { id: "bar", key: "b", sel: 1, def: "0", label: "barrier" }
      ], "Lot-line noise estimate");
    } else if (document.getElementById("house")) {
      GSLabShare("go", "out", [
        { id: "runW", key: "w", min: 100, max: null, def: 2210, label: "running" },
        { id: "hrs", key: "hr", min: 1, max: 24, def: 16, label: "h/day" },
        { id: "tank", key: "tk", min: 0.5, max: null, def: 4, label: "tank gal" },
        { id: "unit", key: "u", sel: 1, def: "hondaEU2200i", label: "oil" },
        { id: "meter", key: "m", min: 0, max: null, def: 0, label: "meter" }
      ], "Storm runbook estimate");
    } else if (document.getElementById("kwWatts")) {
      GSLabShare("kwGo", "kwOut", [
        { id: "kwWatts", key: "w", min: 0, max: null, def: 3500, label: "watts" },
        { id: "kwHours", key: "h", min: 0, max: null, def: 8, label: "hours" }
      ], "kW to kWh estimate");
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
