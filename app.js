(() => {
  const weight = document.getElementById('weight');
  const karat = document.getElementById('karat');
  const price = document.getElementById('price');
  const pureResult = document.getElementById('pure-result');
  const valueResult = document.getElementById('value-result');
  const formula = document.getElementById('formula');
  const priceDate = document.getElementById('price-date');
  const update = () => {
    const w = Number(weight.value);
    const k = Number(karat.value);
    const usable = weight.value !== '' && karat.value !== '' && Number.isFinite(w) && Number.isFinite(k) && w >= 0 && k > 0 && k <= 24;
    const pure = usable ? w * k / 24 : null;
    pureResult.innerHTML = pure === null ? '— <small>g</small>' : `${pure.toFixed(4)} <small>g</small>`;
    formula.textContent = usable ? `${w} g × ${k} ÷ 24. Estimate only; actual alloy composition must be professionally verified.` : 'Enter documented weight and karat. Formula: weight × karat ÷ 24.';
    const p = Number(price.value);
    const priceUsable = usable && price.value !== '' && Number.isFinite(p) && p >= 0;
    valueResult.innerHTML = priceUsable ? `$${(pure * p).toFixed(2)} <small>USD</small>` : '— <small>USD</small>';
    priceDate.textContent = priceUsable ? 'Arithmetic only. Add and retain the official price source and retrieval timestamp separately; price not independently verified by this tool.' : 'Price source and timestamp: not provided. No price is assumed.';
  };
  [weight, karat, price].forEach(el => el.addEventListener('input', update));
})();
