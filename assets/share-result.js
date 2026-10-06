/* Copy buttons and URL updates. No sizing math. */
(function (w) {
  "use strict";
  function num(v, min, max) {
    if (v == null || v === "") return null;
    var n = Number(v);
    if (!isFinite(n)) return null;
    if (min != null && n < min) return null;
    if (max != null && n > max) return null;
    return n;
  }
  function write(obj) {
    var p = new URLSearchParams();
    Object.keys(obj).forEach(function (k) {
      if (obj[k] != null && obj[k] !== "") p.set(k, String(obj[k]));
    });
    var q = p.toString().replace(/%2C/gi, ",");
    var next = location.pathname + (q ? "?" + q : "") + location.hash;
    if (next !== location.pathname + location.search + location.hash) history.replaceState(null, "", next);
  }
  function pick(sel, v) {
    if (!sel || v == null || v === "") return false;
    for (var i = 0; i < sel.options.length; i++) {
      if (sel.options[i].value === String(v)) { sel.value = String(v); return true; }
    }
    return false;
  }
  function plain(box) {
    var c = box.cloneNode(true), s = c.querySelector("[data-share]");
    if (s) s.remove();
    return (c.innerText || "").replace(/\n{3,}/g, "\n\n").trim();
  }
  function copy(text, btn) {
    var old = btn.textContent;
    function done() { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = old; }, 1500); }
    function fb() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.left = "-9999px";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); } catch (e) {}
      ta.remove();
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { fb(); done(); });
    else { fb(); done(); }
  }
  function buttons(box, title, inputs) {
    if (!box || box.hidden || box.querySelector("[data-share]")) return;
    var bar = document.createElement("p");
    bar.className = "small";
    bar.setAttribute("data-share", "");
    ["Copy link to this result", "Copy as text"].forEach(function (label, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = label;
      b.style.cssText = "margin:.45rem .45rem 0 0;border:1px solid var(--bd);background:var(--card);color:var(--fg);border-radius:8px;padding:.35rem .7rem;cursor:pointer";
      b.addEventListener("click", function () {
        var body = title + " (GeneratorSizer)\nInputs: " + inputs + "\nResult: " + plain(box) + "\nPlanning estimate — check the nameplate. " + location.href;
        copy(i ? body : location.href, b);
      });
      bar.appendChild(b);
    });
    box.appendChild(bar);
  }
  w.GSShare = { num: num, write: write, pick: pick, buttons: buttons };
})(window);
