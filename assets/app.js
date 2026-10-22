/* GOLD4 — dashboard behaviour. No network calls: every number is computed locally
   from the values the page already carries. */
(function () {
  "use strict";

  /* ---------------- table filter ---------------- */
  var filterInput = document.getElementById("filter");
  var rows = Array.prototype.slice.call(document.querySelectorAll("tr[data-row-id]"));
  var countEl = document.getElementById("filterCount");

  function applyFilter() {
    if (!filterInput) return;
    var q = filterInput.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (tr) {
      var hit = !q || (tr.getAttribute("data-search") || "").indexOf(q) !== -1;
      tr.hidden = !hit;
      if (hit) shown++;
    });
    if (countEl) countEl.textContent = shown + " of " + rows.length + " rows shown";
  }
  if (filterInput) {
    filterInput.addEventListener("input", applyFilter);
    applyFilter();
  }

  /* ---------------- gold calculator ---------------- */
  var FINENESS = { 10: 10 / 24, 14: 14 / 24, 18: 18 / 24, 22: 22 / 24, 24: 1 };
  /* 15 U.S.C. 295: whole-article fineness may be up to 0.007 below the stamp. */
  var LEGAL_MIN = { 10: 10 / 24 - 0.007, 14: 14 / 24 - 0.007, 18: 18 / 24 - 0.007, 22: 22 / 24 - 0.007, 24: 24 / 24 - 0.007 };

  var weightEl = document.getElementById("c-weight");
  var karatEl = document.getElementById("c-karat");
  var spotEl = document.getElementById("c-spot");
  var priceEl = document.getElementById("c-price");
  var outPure = document.getElementById("c-pure");
  var outValue = document.getElementById("c-value");
  var outMin = document.getElementById("c-min");
  var outPerGram = document.getElementById("c-pergram");
  var outMult = document.getElementById("c-mult");
  var outMultNote = document.getElementById("c-multnote");

  function money(n) {
    return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function calc() {
    if (!weightEl || !karatEl || !spotEl) return;
    var oz = 31.1034768;
    var w = parseFloat(weightEl.value);
    var k = parseInt(karatEl.value, 10);
    var spot = parseFloat(spotEl.value);
    var price = parseFloat(priceEl.value);

    var valid = isFinite(w) && w > 0 && isFinite(spot) && spot > 0 && FINENESS[k];
    if (!valid) {
      [outPure, outValue, outMin, outPerGram, outMult].forEach(function (el) { if (el) el.textContent = "—"; });
      if (outMultNote) outMultNote.textContent = "Enter a weight and a spot price.";
      return;
    }
    var usdPerGram = spot / oz;
    var pure = w * FINENESS[k];
    var value = pure * usdPerGram;
    var minValue = w * LEGAL_MIN[k] * usdPerGram;

    if (outPure) outPure.textContent = pure.toFixed(3) + " g";
    if (outValue) outValue.textContent = money(value);
    if (outMin) outMin.textContent = money(minValue > 0 ? minValue : 0);
    if (outPerGram) outPerGram.textContent = money(usdPerGram);

    if (outMult) {
      if (isFinite(price) && price > 0) {
        outMult.textContent = (price / value).toFixed(2) + "×";
        if (outMultNote) {
          outMultNote.textContent = "Price ÷ gold value. A multiple below ~1 would mean the ring is priced at or under its bare gold content, which is a red flag for a genuine solid-gold engagement ring.";
        }
      } else {
        outMult.textContent = "—";
        if (outMultNote) outMultNote.textContent = "Add the asking price to see the multiple.";
      }
    }
  }

  [weightEl, karatEl, spotEl, priceEl].forEach(function (el) {
    if (el) el.addEventListener("input", calc);
    if (el) el.addEventListener("change", calc);
  });
  if (weightEl) calc();
})();
