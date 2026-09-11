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

  /* Lead + optin forms: INERT until a real inbox is configured
   * (action contains YOUR-INBOX). Intercept, confirm locally, leak nothing. */
  function wireInertForms() {
    ["proLeadForm", "optinForm"].forEach(function (id) {
      var f = document.getElementById(id);
      if (!f) return;
      f.addEventListener("submit", function (e) {
        if (/YOUR-INBOX/.test(f.getAttribute("action") || "")) {
          e.preventDefault();
          var done = document.getElementById("leadDone") || document.getElementById("optinMsg");
          if (done) {
            done.hidden = false;
            done.textContent = "Thanks — quote requests open shortly. " +
              "Nothing was sent from this preview form; check back soon or use the Amazon links above.";
          }
          f.reset();
        } else {
          try {
            var ctx = document.getElementById("leadContext");
            if (ctx && window.__lastSizeKW) ctx.value = String(window.__lastSizeKW);
          } catch (err) { /* never blocks submit */ }
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { tagLinks(); wireInertForms(); });
  } else { tagLinks(); wireInertForms(); }
})();

/* Wattage-matched CTA (2026-09-11): key the calculator's Amazon buttons to the
 * recommended wattage. ≤2,500W -> inverter class; 2,501-5,000W -> dual-fuel
 * mid class; >5,000W -> 7,500W+ whole-home class. */
window.updateMatchedCTA = function (rec) {
  var box = document.getElementById("matchedCta");
  if (!box) return;
  rec = Math.max(500, Math.round(rec || 0));
  var band;
  if (rec <= 2500) {
    band = { label: "Inverter class — quiet, clean power for essentials",
             q: rec + " watt inverter generator",
             alt: "2000 watt inverter generator" };
  } else if (rec <= 5000) {
    band = { label: "Dual-fuel class — flexible fuel, mid-size backup",
             q: rec + " watt dual fuel portable generator",
             alt: "4500 watt dual fuel portable generator" };
  } else {
    band = { label: "Whole-home class — runs central AC + everything",
             q: rec + " watt portable generator electric start",
             alt: "7500 watt dual fuel portable generator" };
  }
  var url = "https://www.amazon.com/s?k=" + encodeURIComponent(band.q) +
            "&tag=" + encodeURIComponent(AMAZON_TAG);
  var altUrl = "https://www.amazon.com/s?k=" + encodeURIComponent(band.alt) +
               "&tag=" + encodeURIComponent(AMAZON_TAG);
  box.innerHTML =
    '<p class="small"><b>Matched to your ' + rec.toLocaleString() +
    ' W result:</b> ' + band.label + '</p>' +
    '<div class="affil-links">' +
    '<a class="btn-amz" rel="sponsored nofollow noopener" target="_blank" href="' +
      url + '">' + rec.toLocaleString() + ' W class on Amazon</a>' +
    '<a class="btn-amz" rel="sponsored nofollow noopener" target="_blank" href="' +
      altUrl + '">Popular alternative on Amazon</a>' +
    '</div>';
  box.hidden = false;
};
