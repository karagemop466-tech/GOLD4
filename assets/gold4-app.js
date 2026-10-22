/* GOLD4 Interactive Category & Calculator Controller (Session arena/81b71aa5-gold4)
 * Pure client-side enhancements over pre-rendered, source-linked HTML tables.
 * Never fabricates or fills in unconfirmed values; blank fields stay explicitly UNVERIFIED.
 */
(function () {
  "use strict";

  function initTableFilters() {
    var filterBar = document.querySelector("[data-gold4-filter-bar]");
    var table = document.querySelector("[data-gold4-catalog-table]");
    if (!filterBar || !table) return;

    var karatSel = filterBar.querySelector("[data-filter-karat]");
    var sellerSel = filterBar.querySelector("[data-filter-seller]");
    var weightChk = filterBar.querySelector("[data-filter-weight-only]");
    var searchInp = filterBar.querySelector("[data-filter-search]");
    var countEl = filterBar.querySelector("[data-filter-count]");
    var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr[data-row-id]"));

    function apply() {
      var kVal = karatSel ? karatSel.value : "all";
      var sVal = sellerSel ? sellerSel.value : "all";
      var wOnly = weightChk ? weightChk.checked : false;
      var q = searchInp ? searchInp.value.trim().toLowerCase() : "";
      var shown = 0;

      rows.forEach(function (tr) {
        var rKarat = tr.getAttribute("data-karat") || "";
        var rSeller = tr.getAttribute("data-seller") || "";
        var rHasWeight = tr.getAttribute("data-has-weight") === "1";
        var text = tr.textContent.toLowerCase();

        var ok = true;
        if (kVal !== "all" && rKarat !== kVal) ok = false;
        if (sVal !== "all" && rSeller !== sVal) ok = false;
        if (wOnly && !rHasWeight) ok = false;
        if (q && text.indexOf(q) === -1) ok = false;

        tr.style.display = ok ? "" : "none";
        if (ok) shown += 1;
      });

      if (countEl) {
        countEl.textContent = shown + " of " + rows.length + " verified rows shown";
      }
    }

    [karatSel, sellerSel, weightChk, searchInp].forEach(function (el) {
      if (!el) return;
      el.addEventListener("input", apply);
      el.addEventListener("change", apply);
    });
    apply();
  }

  function fmtUSD(n) {
    return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function initCalculator() {
    var form = document.getElementById("gold4-calc-form");
    if (!form) return;

    var TROY_OZ_G = 31.1034768;
    var CARAT_G = 0.2;
    var DWT_G = 1.55517384;

    var spotPreset = document.getElementById("calc-spot-preset");
    var spotOzInp = document.getElementById("calc-spot-oz");
    var weightInp = document.getElementById("calc-total-weight");
    var unitSel = document.getElementById("calc-weight-unit");
    var stoneCtInp = document.getElementById("calc-stone-ct");
    var karatSel = document.getElementById("calc-karat");
    var solderSel = document.getElementById("calc-solder-mode");
    var priceInp = document.getElementById("calc-retail-price");

    var outNetAlloy = document.getElementById("out-net-alloy-g");
    var outStoneMass = document.getElementById("out-stone-mass-g");
    var outPureGold = document.getElementById("out-pure-gold-g");
    var outLegalMinGold = document.getElementById("out-legal-min-gold-g");
    var outMeltUSD = document.getElementById("out-melt-usd");
    var outLegalMinUSD = document.getElementById("out-legal-min-usd");
    var outSpotGram = document.getElementById("out-spot-gram");
    var outMarkup = document.getElementById("out-markup");
    var outMultiple = document.getElementById("out-multiple");
    var outDiagnostic = document.getElementById("out-diagnostic");

    if (spotPreset && spotOzInp) {
      spotPreset.addEventListener("change", function () {
        if (spotPreset.value !== "custom") {
          spotOzInp.value = spotPreset.value;
          compute();
        }
      });
      spotOzInp.addEventListener("input", function () {
        spotPreset.value = "custom";
        compute();
      });
    }

    var presetBtns = document.querySelectorAll("[data-calc-load-ring]");
    Array.prototype.forEach.call(presetBtns, function (btn) {
      btn.addEventListener("click", function () {
        weightInp.value = btn.getAttribute("data-weight-g") || "";
        unitSel.value = "g";
        stoneCtInp.value = btn.getAttribute("data-stone-ct") || "0";
        karatSel.value = btn.getAttribute("data-karat") || "14";
        priceInp.value = btn.getAttribute("data-price-usd") || "";
        compute();
      });
    });

    function compute() {
      var spotOz = parseFloat(spotOzInp.value);
      var rawW = parseFloat(weightInp.value);
      var stoneCt = parseFloat(stoneCtInp.value || "0");
      var karat = parseFloat(karatSel.value);
      var solderPpt = parseFloat(solderSel.value || "0.003");
      var retail = parseFloat(priceInp.value);

      if (!(spotOz > 0)) {
        outDiagnostic.textContent = "Enter a positive gold spot quote (USD per troy ounce) from a dated source.";
        return;
      }
      var spotPerG = spotOz / TROY_OZ_G;
      outSpotGram.textContent = fmtUSD(spotPerG) + " / g (24K)";

      if (!(rawW > 0)) {
        outNetAlloy.textContent = "UNVERIFIED (enter scale weight)";
        outStoneMass.textContent = "0.000 g";
        outPureGold.textContent = "—";
        outLegalMinGold.textContent = "—";
        outMeltUSD.textContent = "—";
        outLegalMinUSD.textContent = "—";
        outMarkup.textContent = "—";
        outMultiple.textContent = "—";
        outDiagnostic.textContent =
          "No Hallucinations Rule: metal gram weight is required to compute raw gold content. Weigh the ring on a calibrated 0.01 g jeweler scale or request the spec in writing.";
        return;
      }

      var totalG = rawW;
      if (unitSel.value === "dwt") totalG = rawW * DWT_G;
      if (unitSel.value === "ozt") totalG = rawW * TROY_OZ_G;

      var stoneG = Math.max(0, isNaN(stoneCt) ? 0 : stoneCt) * CARAT_G;
      var netAlloyG = totalG - stoneG;

      if (netAlloyG <= 0) {
        outNetAlloy.textContent = "0.000 g (stone mass >= total mass)";
        outStoneMass.textContent = stoneG.toFixed(3) + " g";
        outPureGold.textContent = "—";
        outLegalMinGold.textContent = "—";
        outMeltUSD.textContent = "—";
        outLegalMinUSD.textContent = "—";
        outMarkup.textContent = "—";
        outMultiple.textContent = "—";
        outDiagnostic.textContent =
          "Check inputs: deducted stone mass (" + stoneG.toFixed(3) + " g) exceeds or equals total scale mass (" + totalG.toFixed(3) + " g).";
        return;
      }

      var nominalFineness = karat / 24.0;
      var legalMinFineness = karat === 24 ? 0.999 : Math.max(0, nominalFineness - solderPpt);
      var pureGoldG = netAlloyG * nominalFineness;
      var legalMinGoldG = netAlloyG * legalMinFineness;
      var meltUSD = pureGoldG * spotPerG;
      var legalMinUSD = legalMinGoldG * spotPerG;

      outStoneMass.textContent = stoneG.toFixed(3) + " g (" + (isNaN(stoneCt) ? 0 : stoneCt).toFixed(2) + " ct × 0.200 g/ct)";
      outNetAlloy.textContent = netAlloyG.toFixed(3) + " g (" + karat + "K alloy)";
      outPureGold.textContent = pureGoldG.toFixed(4) + " g (" + (nominalFineness * 100).toFixed(2) + "% nominal)";
      outLegalMinGold.textContent = legalMinGoldG.toFixed(4) + " g (" + (legalMinFineness * 100).toFixed(2) + "% 15 U.S.C. § 295 floor)";
      outMeltUSD.textContent = fmtUSD(meltUSD);
      outLegalMinUSD.textContent = fmtUSD(legalMinUSD);

      var notes = [];
      if (netAlloyG < 1.5) {
        notes.push("WARNING: Net gold alloy mass (" + netAlloyG.toFixed(2) + " g) is ultra-light (< 1.50 g)—verify band is not hollow or prone to bending.");
      } else if (netAlloyG >= 3.0) {
        notes.push("Substantial solid-shank mass (" + netAlloyG.toFixed(2) + " g net alloy) suitable for daily engagement wear.");
      } else {
        notes.push("Petite/standard band mass (" + netAlloyG.toFixed(2) + " g net alloy); inspect shank thickness >= 1.6–1.8 mm.");
      }

      if (retail > 0) {
        var diff = retail - meltUSD;
        var mult = retail / meltUSD;
        outMarkup.textContent = (diff >= 0 ? "+" : "") + fmtUSD(diff) + " over melt";
        outMultiple.textContent = mult.toFixed(2) + "× raw gold melt";
        if (retail < meltUSD * 0.95) {
          notes.push("CRITICAL RED FLAG: Asking price (" + fmtUSD(retail) + ") is BELOW raw gold melt value (" + fmtUSD(meltUSD) + ")! High risk of gold-plated, hollow, vermeil, or counterfeit alloy.");
        } else if (mult > 8 && stoneG === 0) {
          notes.push("High brand/craftsmanship multiple (" + mult.toFixed(2) + "× melt) for a stone-free gold band; compare gram-disclosed alternatives.");
        }
      } else {
        outMarkup.textContent = "Enter asking price to compare";
        outMultiple.textContent = "—";
      }

      outDiagnostic.textContent = notes.join(" ");
    }

    [weightInp, unitSel, stoneCtInp, karatSel, solderSel, priceInp].forEach(function (el) {
      if (!el) return;
      el.addEventListener("input", compute);
      el.addEventListener("change", compute);
    });
    compute();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTableFilters();
    initCalculator();
  });
})();
