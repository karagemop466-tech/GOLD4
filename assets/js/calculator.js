/* GOLD4 calculator — all math is client-side and shown with formulas.
   Spot price is embedded at build time from data/gold_spot.json (source + timestamp displayed). */
(function () {
  var TROY_OZ_G = 31.1034768;
  var KARATS = { "10": 10 / 24, "14": 14 / 24, "18": 18 / 24, "22": 22 / 24, "24": 1 };

  function $(id) { return document.getElementById(id); }
  function fmt(n, d) { return isFinite(n) ? n.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }) : "—"; }

  function calc() {
    var w = parseFloat($("w").value);
    var k = $("k").value;
    var spot = parseFloat($("spot").value);
    var paid = parseFloat($("paid").value);
    var out = $("out");
    if (!(w > 0) || !(spot > 0)) {
      out.innerHTML = '<div class="row">Enter weight (g) and a spot price to calculate.</div>';
      return;
    }
    var purity = KARATS[k];
    var pureG = w * purity;
    var pureOz = pureG / TROY_OZ_G;
    var melt = pureOz * spot;
    var html = "";
    html += '<div class="row"><span>Purity (' + k + 'K = ' + k + '/24)</span><b>' + fmt(purity * 100, 2) + '%</b></div>';
    html += '<div class="row"><span>Pure gold content</span><b>' + fmt(pureG, 3) + ' g (' + fmt(pureOz, 4) + ' troy oz)</b></div>';
    html += '<div class="row"><span>Intrinsic (melt) gold value</span><b>$' + fmt(melt, 2) + '</b></div>';
    html += '<div class="row"><span>Formula</span><b>' + fmt(w, 2) + ' g × ' + fmt(purity * 100, 1) + '% ÷ ' + TROY_OZ_G + ' g/oz × $' + fmt(spot, 2) + '/oz</b></div>';
    if (paid > 0) {
      var premium = paid - melt;
      var pct = melt > 0 ? (premium / melt) * 100 : NaN;
      html += '<div class="row"><span>Price paid</span><b>$' + fmt(paid, 2) + '</b></div>';
      html += '<div class="row"><span>Premium over melt</span><b>$' + fmt(premium, 2) + ' (' + fmt(pct, 0) + '%)</b></div>';
      if (paid < melt) {
        html += '<div class="row"><span>⚠️ Red flag</span><b>Price BELOW melt value — verify purity before buying (per checklist).</b></div>';
      } else {
        html += '<div class="row"><span>Note</span><b>Retail includes craftsmanship, stones & margin; premium over melt is normal.</b></div>';
      }
    }
    out.innerHTML = html;
  }

  document.addEventListener("DOMContentLoaded", function () {
    ["w", "k", "spot", "paid"].forEach(function (id) {
      var el = $(id);
      if (el) { el.addEventListener("input", calc); el.addEventListener("change", calc); }
    });
    calc();
  });
})();
