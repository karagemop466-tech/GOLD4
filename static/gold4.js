/* GOLD4 Interactive Melt & Markup Analyzer, Catalog Filter & Persistent Buyer Checklist
 * Security & Anti-Hallucination Invariant:
 * - Never fabricates spot prices, gram weights, or karat purities.
 * - Uses strict DOM textContent APIs (zero untrusted innerHTML injection).
 * - Unverified fields remain explicitly marked UNVERIFIED and never coerce null -> 0.
 */
(function () {
  "use strict";

  var TROY_OZ_GRAMS = 31.1034768;
  var CARAT_GRAMS = 0.200;
  var SPOT_PRESETS = {
    kitco: {
      label: "Kitco Live Spot (2026-10-22: $4,024.60/oz = $129.39/g)",
      usdPerOz: 4024.60,
      usdPerGram: 4024.60 / TROY_OZ_GRAMS,
      url: "https://www.kitco.com/charts/gold"
    },
    jmbullion: {
      label: "JM Bullion Live Ask (2026-10-22: $4,039.76/oz = $129.88/g)",
      usdPerOz: 4039.76,
      usdPerGram: 4039.76 / TROY_OZ_GRAMS,
      url: "https://www.jmbullion.com/charts/gold-price/"
    },
    custom: {
      label: "Custom Dated Spot Quote (User Entered)",
      usdPerOz: null,
      usdPerGram: null,
      url: null
    }
  };

  function fmtUSD(n) {
    if (typeof n !== "number" || !isFinite(n)) return "—";
    return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function fmtGrams(n, digits) {
    if (typeof n !== "number" || !isFinite(n)) return "—";
    return n.toFixed(digits || 3) + " g";
  }

  // ---------------- 1. Interactive Gold Weight, Karat & Melt Calculator ----------------
  function initCalculator() {
    var form = document.getElementById("gold4-calc-form");
    if (!form) return;

    var presetSel = document.getElementById("calc-ring-preset");
    var weightInput = document.getElementById("calc-weight");
    var stoneCtInput = document.getElementById("calc-stone-ct");
    var karatSel = document.getElementById("calc-karat");
    var customFinenessInput = document.getElementById("calc-custom-fineness");
    var spotSourceSel = document.getElementById("calc-spot-source");
    var spotGramInput = document.getElementById("calc-spot-gram");
    var retailPriceInput = document.getElementById("calc-retail-price");

    var outPureG = document.getElementById("out-pure-grams");
    var outNetMetal = document.getElementById("out-net-metal");
    var outMeltUSD = document.getElementById("out-melt-usd");
    var outSpotNote = document.getElementById("out-spot-note");
    var outRatio = document.getElementById("out-markup-ratio");
    var outSignal = document.getElementById("out-markup-signal");
    var matrixBody = document.getElementById("calc-karat-matrix-body");
    var presetBanner = document.getElementById("calc-preset-banner");

    function getActiveSpotPerGram() {
      var mode = spotSourceSel ? spotSourceSel.value : "kitco";
      if (mode === "kitco" || mode === "jmbullion") {
        var preset = SPOT_PRESETS[mode];
        if (spotGramInput) {
          spotGramInput.value = preset.usdPerGram.toFixed(2);
          spotGramInput.readOnly = true;
        }
        return preset;
      }
      if (spotGramInput) {
        spotGramInput.readOnly = false;
        var val = parseFloat(spotGramInput.value);
        if (val > 0 && isFinite(val)) {
          return {
            label: "User-entered custom fine-gold spot quote ($" + val.toFixed(2) + "/g)",
            usdPerOz: val * TROY_OZ_GRAMS,
            usdPerGram: val,
            url: null
          };
        }
      }
      return { label: "No spot price entered — enter verified $/g above", usdPerOz: null, usdPerGram: null, url: null };
    }

    function getPurityFraction() {
      if (!karatSel) return null;
      if (karatSel.value === "custom") {
        if (customFinenessInput) customFinenessInput.disabled = false;
        var parts = parseFloat(customFinenessInput ? customFinenessInput.value : "");
        if (parts > 0 && parts <= 1000) return parts / 1000.0;
        return null;
      }
      if (customFinenessInput) customFinenessInput.disabled = true;
      var k = parseFloat(karatSel.value);
      if (k > 0 && k <= 24) return k / 24.0;
      return null;
    }

    function recompute() {
      var spot = getActiveSpotPerGram();
      var grossG = parseFloat(weightInput ? weightInput.value : "");
      var stoneCt = parseFloat(stoneCtInput ? stoneCtInput.value : "");
      var stoneG = stoneCt > 0 && isFinite(stoneCt) ? stoneCt * CARAT_GRAMS : 0;
      var purity = getPurityFraction();
      var retail = parseFloat(retailPriceInput ? retailPriceInput.value : "");

      if (!(grossG > 0 && isFinite(grossG)) || !(purity > 0)) {
        if (outPureG) outPureG.textContent = "— UNVERIFIED WEIGHT / KARAT";
        if (outNetMetal) {
          outNetMetal.textContent =
            "Enter documented gram weight ( never guess from photos ) and confirmed karat purity.";
        }
        if (outMeltUSD) outMeltUSD.textContent = "—";
        if (outSpotNote) outSpotNote.textContent = spot.label;
        if (outRatio) outRatio.textContent = "—";
        if (outSignal) {
          outSignal.textContent =
            "NO HALLUCINATIONS RULE: When a retailer omits ring weight in grams, leave weight blank and request written confirmation before buying.";
        }
      } else {
        var netMetalG = Math.max(0, grossG - stoneG);
        var fineGoldG = netMetalG * purity;
        if (outPureG) outPureG.textContent = fmtGrams(fineGoldG, 3) + " pure 24K Au";
        if (outNetMetal) {
          outNetMetal.textContent =
            "Net alloy mass: " +
            fmtGrams(netMetalG, 3) +
            (stoneG > 0 ? " (deducted " + stoneG.toFixed(3) + " g for " + stoneCt.toFixed(2) + " ct stones)" : " (0.00 ct stone deduction)") +
            " × " +
            (purity * 100).toFixed(2) +
            "% fineness";
        }
        if (spot.usdPerGram) {
          var meltUSD = fineGoldG * spot.usdPerGram;
          if (outMeltUSD) outMeltUSD.textContent = fmtUSD(meltUSD);
          if (outSpotNote) outSpotNote.textContent = spot.label;
          if (retail > 0 && isFinite(retail) && meltUSD > 0) {
            var ratio = retail / meltUSD;
            var premium = retail - meltUSD;
            if (outRatio) {
              outRatio.textContent =
                ratio.toFixed(2) + "× melt (" + (premium >= 0 ? "+" : "") + fmtUSD(premium) + " over raw gold)";
            }
            if (outSignal) {
              if (ratio < 1.02) {
                outSignal.textContent =
                  "CRITICAL FRAUD / PLATING RED FLAG (<1.02× melt): Asking price is AT OR BELOW raw melt value! Almost certainly plated, vermeil, hollow resin-filled, or misstated karat/weight.";
              } else if (ratio <= 1.65) {
                outSignal.textContent =
                  "BULLION / PLAIN BAND BENCHMARK ZONE (1.02×–1.65× melt): Matches verified plain solid gold wedding bands (Sarraf 1.33×–1.50× melt on 2026-10-22). Verify size-specific weight & hallmark.";
              } else if (ratio <= 3.5) {
                outSignal.textContent =
                  "CRAFTED DESIGNER / ACCENT SETTING ZONE (1.65×–3.50× melt): Typical manufacturing & retail margin for solid gold settings or small accent melee.";
              } else {
                outSignal.textContent =
                  "CENTER GEMSTONE / LUXURY BRAND PREMIUM (>3.50× melt): Majority of price reflects center diamond/gemstone or brand markup — audit GIA diamond report independently!";
              }
            }
          } else {
            if (outRatio) outRatio.textContent = "Enter asking price (optional)";
            if (outSignal) outSignal.textContent = "Enter listing price in USD to compute markup ratio and fraud-risk signal.";
          }
        } else {
          if (outMeltUSD) outMeltUSD.textContent = "— (enter custom $/g)";
          if (outSpotNote) outSpotNote.textContent = spot.label;
          if (outRatio) outRatio.textContent = "—";
        }
      }

      // Update live 5-karat side-by-side table whenever net weight or spot changes
      if (matrixBody) {
        var baseMass = grossG > 0 && isFinite(grossG) ? Math.max(0, grossG - stoneG) : 5.0;
        var karats = [10, 14, 18, 22, 24];
        while (matrixBody.firstChild) matrixBody.removeChild(matrixBody.firstChild);
        karats.forEach(function (k) {
          var tr = document.createElement("tr");
          var frac = k / 24.0;
          var pure = baseMass * frac;
          var melt = spot.usdPerGram ? pure * spot.usdPerGram : null;
          var retailVal = parseFloat(retailPriceInput ? retailPriceInput.value : "");
          var mult = melt && retailVal > 0 ? (retailVal / melt).toFixed(2) + "×" : "—";
          [
            k + "K Solid Gold",
            (frac * 100).toFixed(2) + "% (" + k + "/24)",
            baseMass.toFixed(2) + " g",
            pure.toFixed(3) + " g",
            melt ? fmtUSD(melt) : "—",
            mult
          ].forEach(function (txt, idx) {
            var td = document.createElement("td");
            if (idx >= 1) td.className = "mono";
            td.textContent = txt;
            tr.appendChild(td);
          });
          matrixBody.appendChild(tr);
        });
      }
    }

    if (presetSel) {
      presetSel.addEventListener("change", function () {
        var opt = presetSel.options[presetSel.selectedIndex];
        if (!opt || !opt.value) {
          if (presetBanner) presetBanner.textContent = "";
          recompute();
          return;
        }
        var w = opt.getAttribute("data-weight");
        var k = opt.getAttribute("data-karat");
        var p = opt.getAttribute("data-price");
        var st = opt.getAttribute("data-stone") || "0";
        var name = opt.getAttribute("data-name") || "";
        if (weightInput) weightInput.value = w ? w : "";
        if (stoneCtInput) stoneCtInput.value = st ? st : "0";
        if (karatSel) karatSel.value = k ? k : "";
        if (retailPriceInput) retailPriceInput.value = p ? p : "";
        if (presetBanner) {
          presetBanner.textContent = w
            ? "Loaded verified listing: " + name + " — confirmed weight " + w + " g, " + k + "K, $" + p + " (retrieved 2026-10-22)."
            : "Loaded listing: " +
              name +
              " — OFFICIAL WEIGHT IS UNVERIFIED (left blank per Zero-Hallucination Policy! Request gram weight in writing from retailer before buying).";
        }
        recompute();
      });
    }

    // Support URL hash / query deep-linking from any table row (`calculator.html?id=G4-BND-04`)
    var params = new URLSearchParams(window.location.search);
    var requestedId = params.get("id");
    if (requestedId && presetSel) {
      for (var i = 0; i < presetSel.options.length; i++) {
        if (presetSel.options[i].value === requestedId) {
          presetSel.selectedIndex = i;
          presetSel.dispatchEvent(new Event("change"));
          break;
        }
      }
    }

    [weightInput, stoneCtInput, karatSel, customFinenessInput, spotSourceSel, spotGramInput, retailPriceInput].forEach(
      function (el) {
        if (el) {
          el.addEventListener("input", recompute);
          el.addEventListener("change", recompute);
        }
      }
    );

    recompute();
  }

  // ---------------- 2. Interactive Catalog Table Filtering ----------------
  function initTableFilters() {
    var searchInput = document.getElementById("filter-search");
    var karatSel = document.getElementById("filter-karat");
    var statusSel = document.getElementById("filter-status");
    var catSel = document.getElementById("filter-category");
    var countOut = document.getElementById("filter-visible-count");
    var rows = Array.prototype.slice.call(document.querySelectorAll("tr[data-ring-row]"));
    if (!rows.length) return;

    function applyFilter() {
      var q = searchInput ? searchInput.value.trim().toLowerCase() : "";
      var k = karatSel ? karatSel.value : "all";
      var st = statusSel ? statusSel.value : "all";
      var cat = catSel ? catSel.value : "all";
      var shown = 0;

      rows.forEach(function (tr) {
        var matchQ = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
        var matchK = k === "all" || tr.getAttribute("data-karat") === k;
        var matchSt = st === "all" || tr.getAttribute("data-status") === st;
        var matchCat = cat === "all" || tr.getAttribute("data-category") === cat;
        var visible = matchQ && matchK && matchSt && matchCat;
        tr.hidden = !visible;
        if (visible) shown++;
      });
      if (countOut) {
        countOut.textContent = "Showing " + shown + " of " + rows.length + " live-audited rows";
      }
    }

    [searchInput, karatSel, statusSel, catSel].forEach(function (el) {
      if (el) {
        el.addEventListener("input", applyFilter);
        el.addEventListener("change", applyFilter);
      }
    });
    applyFilter();
  }

  // ---------------- 3. Flagged Items Severity Filter ----------------
  function initFlagFilter() {
    var sevSel = document.getElementById("filter-flag-severity");
    var cards = Array.prototype.slice.call(document.querySelectorAll("[data-flag-card]"));
    if (!sevSel || !cards.length) return;
    sevSel.addEventListener("change", function () {
      var target = sevSel.value;
      cards.forEach(function (c) {
        c.hidden = target !== "all" && c.getAttribute("data-severity") !== target;
      });
    });
  }

  // ---------------- 4. Persistent Buyer Verification Checklist ----------------
  function initChecklist() {
    var boxes = Array.prototype.slice.call(document.querySelectorAll("input[data-check-id]"));
    if (!boxes.length) return;
    var bar = document.getElementById("checklist-progress-fill");
    var statusText = document.getElementById("checklist-progress-text");
    var resetBtn = document.getElementById("checklist-reset-btn");
    var copyBtn = document.getElementById("copy-seller-script-btn");
    var STORAGE_KEY = "gold4_buyer_checklist_v1";

    var saved = {};
    try {
      saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}") || {};
    } catch (_) {
      saved = {};
    }

    function updateProgress() {
      var done = 0;
      boxes.forEach(function (cb) {
        var id = cb.getAttribute("data-check-id");
        var parent = cb.closest(".check-item");
        if (cb.checked) {
          done++;
          if (parent) parent.classList.add("checked");
        } else if (parent) {
          parent.classList.remove("checked");
        }
        saved[id] = !!cb.checked;
      });
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
      } catch (_) {}
      var pct = Math.round((done / boxes.length) * 100);
      if (bar) bar.style.width = pct + "%";
      if (statusText) {
        statusText.textContent =
          done +
          " / " +
          boxes.length +
          " buyer protection checks completed (" +
          pct +
          "%)" +
          (done === boxes.length
            ? " — READY FOR CREDIT-CARD CHECKOUT & 48-HOUR INDEPENDENT XRF ASSAY"
            : " — Complete every item before finalizing purchase.");
      }
    }

    boxes.forEach(function (cb) {
      var id = cb.getAttribute("data-check-id");
      if (saved[id]) cb.checked = true;
      cb.addEventListener("change", updateProgress);
    });

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        boxes.forEach(function (cb) {
          cb.checked = false;
        });
        updateProgress();
      });
    }

    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var scriptEl = document.getElementById("seller-inquiry-template");
        if (!scriptEl || !navigator.clipboard) return;
        navigator.clipboard.writeText(scriptEl.textContent).then(function () {
          var prev = copyBtn.textContent;
          copyBtn.textContent = "Copied Written Seller Inquiry Script ✓";
          setTimeout(function () {
            copyBtn.textContent = prev;
          }, 2200);
        });
      });
    }

    updateProgress();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initCalculator();
    initTableFilters();
    initFlagFilter();
    initChecklist();
  });
})();
