/* Transfer-switch permalinks. Circuit names are not written to the URL. */
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function numsFrom(text) {
    var nums = [];
    String(text || "").split("\n").forEach(function (line) {
      var m = line.trim().match(/\s[-–:]\s*([\d,]+)/);
      if (m) nums.push(String(Number(m[1].replace(/,/g, ""))));
    });
    return nums;
  }
  function share() {
    var box = $("tsResult"), text = $("tsCircuits").value.trim(), nums;
    if (!box || box.hidden || !text) return;
    nums = numsFrom(text);
    if (nums.length) GSShare.write({ tab: "ts", tw: nums.join(",") });
    GSShare.buttons(box, "Transfer switch estimate", nums.length ? nums.join(", ") + " W" : "circuits listed");
  }
  function apply(params) {
    var parts, nums = [], i, n;
    if (!params.has("tw")) return;
    parts = params.get("tw").split(",");
    for (i = 0; i < parts.length; i++) {
      n = GSShare.num(parts[i].trim(), 0, null);
      if (n == null) return;
      nums.push(n);
    }
    if (!nums.length) return;
    $("tsCircuits").value = nums.map(function (x) { return "Circuit - " + x; }).join("\n");
    if ($("tab-ts") && typeof showTab === "function") showTab("tab-ts", document.querySelector('button[onclick*="tab-ts"]'));
    planSwitch();
  }
  if (typeof planSwitch !== "function" || !$("tsResult")) return;
  var orig = planSwitch;
  planSwitch = function () { orig(); share(); };
  document.addEventListener("DOMContentLoaded", function () {
    var params = new URLSearchParams(location.search);
    if (params.get("tab") && params.get("tab") !== "ts") return;
    if (!params.has("tw") && params.get("tab") !== "ts") return;
    apply(params);
  });
})();
