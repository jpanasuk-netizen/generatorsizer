/* GeneratorSizer monetization staging — STAGED, NOT LIVE.
 * Single swap point for Amazon Associates links. Until Jeremy supplies a
 * real Associate ID, AMAZON_TAG stays a placeholder and every [data-amz]
 * link below renders as a plain Amazon search URL with NO tracking tag.
 * No income claims anywhere. See MONETIZATION_STAGING.md for activation.
 */
(function () {
  "use strict";
  var AMAZON_TAG = "generatorsi0d-20"; // live 2026-09-10
  var STAGED = AMAZON_TAG.indexOf("YOUR-") === 0;

  function tagLinks() {
    document.querySelectorAll("a[data-amz]").forEach(function (a) {
      var q = a.getAttribute("data-amz");
      var url = "https://www.amazon.com/s?k=" + encodeURIComponent(q);
      if (!STAGED) url += "&tag=" + encodeURIComponent(AMAZON_TAG);
      a.href = url;
      a.setAttribute("rel", "sponsored nofollow noopener");
      a.target = "_blank";
    });
    document.querySelectorAll("[data-amz-staged-note]").forEach(function (el) {
      if (STAGED) el.hidden = false;
    });
  }

  /* Lead form draft: front-end only. Prevents submit, shows local
   * confirmation, stores nothing, posts nowhere. */
  function wireLeadForm() {
    var f = document.getElementById("proLeadForm");
    if (!f) return;
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var zip = (document.getElementById("leadZip") || {}).value || "";
      var done = document.getElementById("leadDone");
      if (done) {
        done.hidden = false;
        done.textContent = "Noted — this demo form doesn't send anywhere yet. " +
          "When a vetted installer program launches, " +
          (zip ? "requests from " + zip + " " : "") +
          "will route to the approved operator. No data left your browser.";
      }
      try {
        var ctx = document.getElementById("leadContext");
        if (ctx && window.__lastSizeKW) ctx.value = String(window.__lastSizeKW);
      } catch (err) { /* local-only nicety, never blocks */ }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { tagLinks(); wireLeadForm(); });
  } else { tagLinks(); wireLeadForm(); }
})();
