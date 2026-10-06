/* Generator-tab result link. Does not change sizeGenerator math. */
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function fmt(n) { return Math.round(Number(n)).toLocaleString("en-US"); }
  function inputs() {
    var bits = [];
    if (loads.length === 1) bits.push("running " + fmt(loads[0].run) + " W · largest starting " + fmt(loads[0].surge) + " W");
    else bits.push("loads " + loads.map(function (l) { return l.run + "/" + l.surge + "×" + l.qty; }).join(", "));
    if (Number($("headroom").value) !== 20) bits.push("headroom " + $("headroom").value + "%");
    if (Number($("hrsDay").value) !== 8) bits.push($("hrsDay").value + " h/day");
    if (Number($("tankGal").value) !== 4) bits.push($("tankGal").value + " gal tank");
    return bits.join(" · ");
  }
  function share() {
    var box = $("genResult"), o = {};
    if (!box || box.hidden || !loads.length) return;
    if (loads.length === 1 && Number(loads[0].qty) === 1) { o.w = loads[0].run; o.s = loads[0].surge; }
    else o.ld = loads.map(function (l) { return l.run + "-" + l.surge + "-" + l.qty; }).join(",");
    if (Number($("headroom").value) !== 20) o.h = $("headroom").value;
    if (Number($("hrsDay").value) !== 8) o.hr = $("hrsDay").value;
    if (Number($("tankGal").value) !== 4) o.tk = $("tankGal").value;
    GSShare.write(o);
    GSShare.buttons(box, "Generator size estimate", inputs());
  }
  if (typeof sizeGenerator !== "function" || !$("genResult")) return;
  var orig = sizeGenerator;
  sizeGenerator = function () { orig(); share(); };
})();
