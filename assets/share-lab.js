/* Shared permalink hook for lab calculators. Page files pass the fields. */
(function (w) {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function shown(box) { return box && !box.hidden && (box.textContent || "").trim().length > 0; }
  function apply(params, fields) {
    var any = false, i, f, n;
    for (i = 0; i < fields.length; i++) {
      f = fields[i];
      if (!params.has(f.key) || !$(f.id)) continue;
      if (f.sel) { if (GSShare.pick($(f.id), params.get(f.key))) any = true; continue; }
      n = GSShare.num(params.get(f.key), f.min, f.max);
      if (n == null) continue;
      $(f.id).value = String(n);
      any = true;
    }
    return any;
  }
  function collect(fields) {
    var o = {}, i, f, v;
    for (i = 0; i < fields.length; i++) {
      f = fields[i];
      v = $(f.id).value;
      if (f.omitBlank && v === "") continue;
      if (f.def != null && (String(v) === String(f.def) || (!f.sel && Number(v) === Number(f.def)))) continue;
      o[f.key] = v;
    }
    return o;
  }
  function line(fields) {
    return fields.map(function (f) {
      var el = $(f.id), v = el.value;
      if (f.sel && el.selectedIndex >= 0) v = el.options[el.selectedIndex].text;
      if (f.omitBlank && el.value === "") return "";
      return f.label + " " + v;
    }).filter(Boolean).join(" · ");
  }
  w.GSLabShare = function (btnId, boxId, fields, title, after) {
    var btn = $(btnId);
    if (!btn || btn.getAttribute("data-gs-hook")) return;
    btn.setAttribute("data-gs-hook", "1");
    var orig = btn.onclick;
    btn.onclick = function (ev) {
      if (orig) orig.call(btn, ev);
      var box = $(boxId);
      if (!shown(box)) return;
      GSShare.write(collect(fields));
      GSShare.buttons(box, title, line(fields));
    };
    var params = new URLSearchParams(location.search), hit = false, i;
    for (i = 0; i < fields.length; i++) if (params.has(fields[i].key)) hit = true;
    if (!hit || !apply(params, fields)) return;
    if (after) after();
    btn.click();
  };
})(window);
