/* GeneratorSizer monetization — Amazon Associates.
 * Single swap point. Tag live. No income claims.
 */
(function () {
  "use strict";
  var AMAZON_TAG = "generatorsi0d-20";
  var STAGED = AMAZON_TAG.indexOf("YOUR-") === 0;

  function amzUrl(q) {
    var url = "https://www.amazon.com/s?k=" + encodeURIComponent(q);
    if (!STAGED) url += "&tag=" + encodeURIComponent(AMAZON_TAG);
    return url;
  }

  function tagLinks() {
    document.querySelectorAll("a[data-amz]").forEach(function (a) {
      var q = a.getAttribute("data-amz");
      a.href = amzUrl(q);
      a.setAttribute("rel", "sponsored nofollow noopener");
      a.target = "_blank";
    });
    document.querySelectorAll("[data-amz-staged-note]").forEach(function (el) {
      if (STAGED) el.hidden = false;
    });
  }

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

  function bandFor(kind, rec) {
    rec = Math.max(1, Math.round(rec || 0));
    if (kind === "inverter") {
      return {
        label: "Pure-sine inverter class matched to your continuous load",
        q: rec + " watt pure sine wave inverter",
        alt: "2000 watt pure sine wave inverter",
        primary: "Shop this inverter size on Amazon",
        secondary: "Popular 2,000 W inverters on Amazon"
      };
    }
    if (kind === "transfer") {
      var amps = rec;
      return {
        label: "Manual transfer switch / inlet gear for your backup circuits",
        q: amps + " amp manual transfer switch generator",
        alt: "generator power inlet box 50 amp",
        primary: "Shop " + amps + " A transfer switches on Amazon",
        secondary: "Inlet boxes on Amazon"
      };
    }
    // generator (default)
    if (rec <= 2500) {
      return {
        label: "Inverter class — quiet, clean power for essentials",
        q: rec + " watt inverter generator",
        alt: "2000 watt inverter generator",
        primary: "Shop this size on Amazon",
        secondary: "Popular 2,000 W inverters on Amazon"
      };
    }
    if (rec <= 5000) {
      return {
        label: "Dual-fuel class — flexible fuel, mid-size backup",
        q: rec + " watt dual fuel portable generator",
        alt: "4500 watt dual fuel portable generator",
        primary: "Shop this size on Amazon",
        secondary: "Popular 4,500 W dual-fuel on Amazon"
      };
    }
    return {
      label: "Whole-home class — runs central AC + everything",
      q: rec + " watt portable generator electric start",
      alt: "7500 watt dual fuel portable generator",
      primary: "Shop this size on Amazon",
      secondary: "Popular 7,500 W+ class on Amazon"
    };
  }

  function fillSticky(url, label) {
    var bar = document.getElementById("amzSticky");
    if (!bar) return;
    var link = document.getElementById("amzStickyLink");
    if (link) {
      link.href = url;
      link.textContent = label || "Shop this size on Amazon";
      link.setAttribute("rel", "sponsored nofollow noopener");
      link.target = "_blank";
    }
    bar.hidden = false;
    bar.setAttribute("aria-hidden", "false");
  }

  window.dismissAmzSticky = function () {
    var bar = document.getElementById("amzSticky");
    if (bar) {
      bar.hidden = true;
      bar.setAttribute("aria-hidden", "true");
    }
    try { sessionStorage.setItem("amzStickyDismissed", "1"); } catch (e) {}
  };

  /* kind: "generator" | "inverter" | "transfer". rec = watts or amps for transfer */
  window.updateMatchedCTA = function (rec, kind) {
    kind = kind || "generator";
    var box = document.getElementById("matchedCta");
    var band = bandFor(kind, rec);
    var url = amzUrl(band.q);
    var altUrl = amzUrl(band.alt);
    window.__lastSizeKW = band.q;

    var headline = (kind === "transfer")
      ? ("Matched to your " + Math.round(rec) + " A class:")
      : ("Matched to your " + Math.round(rec).toLocaleString() + " W result:");

    if (box) {
      box.innerHTML =
        '<p class="small"><b>' + headline + '</b> ' + band.label + '</p>' +
        '<div class="affil-links">' +
        '<a class="btn-amz btn-amz-primary" rel="sponsored nofollow noopener" target="_blank" href="' +
          url + '">' + band.primary + '</a>' +
        '<a class="btn-amz" rel="sponsored nofollow noopener" target="_blank" href="' +
          altUrl + '">' + band.secondary + '</a>' +
        '</div>';
      box.hidden = false;
    }

    try {
      if (sessionStorage.getItem("amzStickyDismissed") !== "1") {
        fillSticky(url, band.primary);
      }
    } catch (e) {
      fillSticky(url, band.primary);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { tagLinks(); wireInertForms(); });
  } else { tagLinks(); wireInertForms(); }
})();
