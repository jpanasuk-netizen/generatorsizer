/* Click a header to sort. Does nothing until a click, so the first paint is the HTML table. */
(function(){
  var table = document.getElementById("spec-table");
  if (!table) return;
  var buttons = table.querySelectorAll("thead button[data-col]");
  buttons.forEach(function(btn){
    btn.addEventListener("click", function(){
      var idx = +btn.getAttribute("data-col");
      var numeric = btn.getAttribute("data-type") === "num";
      var dir = btn.getAttribute("data-dir") === "asc" ? "desc" : "asc";
      buttons.forEach(function(b){ b.removeAttribute("data-dir"); });
      btn.setAttribute("data-dir", dir);
      var tbody = table.tBodies[0];
      var rows = Array.prototype.slice.call(tbody.rows);
      rows.sort(function(a, b){
        var av = a.cells[idx].getAttribute("data-sort");
        var bv = b.cells[idx].getAttribute("data-sort");
        if (av == null) av = a.cells[idx].textContent.trim();
        if (bv == null) bv = b.cells[idx].textContent.trim();
        var c;
        if (numeric) {
          var an = parseFloat(av);
          var bn = parseFloat(bv);
          if (isNaN(an)) an = Infinity;
          if (isNaN(bn)) bn = Infinity;
          c = an - bn;
        } else {
          c = String(av).localeCompare(String(bv), "en", {numeric: true, sensitivity: "base"});
        }
        return dir === "asc" ? c : -c;
      });
      rows.forEach(function(row){ tbody.appendChild(row); });
    });
  });
})();
