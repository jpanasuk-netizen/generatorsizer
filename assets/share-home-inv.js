/* Inverter and battery permalinks. Does not change their math. */
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function fmt(n) { return Math.round(Number(n)).toLocaleString("en-US"); }
  function show(tab) {
    var id = "tab-" + tab;
    if (!$(id) || typeof showTab !== "function") return;
    showTab(id, document.querySelector('button[onclick*="' + id + '"]'));
  }
  function shareInv() {
    var box = $("invResult"), c = GSShare.num($("invCont").value, 0, null), k = $("invKind").value, o;
    if (!box || box.hidden || !(c > 0)) return;
    o = { tab: "inv", c: c };
    if (k !== "mixed") o.k = k;
    GSShare.write(o);
    GSShare.buttons(box, "Inverter size estimate", "continuous " + fmt(c) + " W · " + k);
  }
  function shareBat() {
    var box = $("btResult"), ah = GSShare.num($("btAh").value, 0, null), bw = GSShare.num($("btLoad").value, 1, null);
    var v = $("btV").value, ch = $("btChem").value, o;
    if (!box || box.hidden || !(ah > 0) || !(bw > 0)) return;
    o = { tab: "bat", ah: ah, bw: bw };
    if (v !== "12") o.v = v;
    if (ch !== "lifepo4") o.ch = ch;
    GSShare.write(o);
    GSShare.buttons(box, "Battery runtime estimate", ah + " Ah · " + v + " V · " + fmt(bw) + " W · " + ch);
  }
  function apply(params) {
    var tab = params.get("tab") || "", c, ah, bw;
    if (!tab) {
      if (params.has("c") || params.has("k")) tab = "inv";
      else if (params.has("ah") || params.has("v") || params.has("bw") || params.has("ch")) tab = "bat";
    }
    if (tab === "inv") {
      c = params.has("c") ? GSShare.num(params.get("c"), 0, null) : null;
      if (params.has("k")) GSShare.pick($("invKind"), params.get("k"));
      if (!(c > 0)) return;
      $("invCont").value = c;
      show("inv");
      sizeInverter();
    } else if (tab === "bat") {
      ah = params.has("ah") ? GSShare.num(params.get("ah"), 0, null) : null;
      bw = params.has("bw") ? GSShare.num(params.get("bw"), 1, null) : null;
      if (params.has("v")) GSShare.pick($("btV"), params.get("v"));
      if (params.has("ch")) GSShare.pick($("btChem"), params.get("ch"));
      if (!(ah > 0) || !(bw > 0)) return;
      $("btAh").value = ah;
      $("btLoad").value = bw;
      show("bat");
      sizeBatteryRuntime();
    }
  }
  if (typeof sizeInverter !== "function") return;
  var inv = sizeInverter, bat = sizeBatteryRuntime;
  sizeInverter = function () { inv(); shareInv(); };
  sizeBatteryRuntime = function () { bat(); shareBat(); };
  document.addEventListener("DOMContentLoaded", function () {
    var params = new URLSearchParams(location.search);
    var keys = ["c", "k", "ah", "v", "bw", "ch"];
    var tab = params.get("tab");
    if (tab === "gen" || tab === "ts") return;
    if (tab !== "inv" && tab !== "bat" && !keys.some(function (k) { return params.has(k); })) return;
    apply(params);
  });
})();
