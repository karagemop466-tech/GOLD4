#!/usr/bin/env python3
"""Currency-evidence gate, not price/variant/authenticity certification."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {'AN-01','VR-01','BE-01','BE-02','BE-03','BE-05','BE-06','BE-07'}


def explicit_usd(rec, hand=None):
    codes = {p.get('currency') for p in rec.get('structured_prices', [])
             if p.get('price') is not None}
    # Mixed currencies are not resolved by selecting the preferred one.
    if codes == {'USD'}:
        return True
    text = ' '.join((hand or {}).get('verbatim', []))
    # An option menu containing USD is not an identified dollar-price currency.
    return bool(re.search(r'US\$\s*\d|\$\s*\d[\d,.]*\s+USD\b', text))


def check():
    load = lambda p: json.loads((ROOT / p).read_text())
    rings = load('data/rings.json')['rows']
    raw = {r['key']:r for r in load('reports/live_source_check_20261111T080309Z.json')['results']}
    hand = {r['id']:r for r in load('reviews/reread-4fe4a9c3/hand_reads.json')['rows']}
    corrections = load('reviews/currency-a2f26a30.json')['quarantined_rows']
    failures = []
    if {r['id'] for r in corrections} != EXPECTED:
        failures.append('quarantine record IDs differ from inspected correction scope')
    for row in rings:
        rid = row['id']
        if rid in EXPECTED:
            if row.get('price_usd') is not None or 'PRICE_UNVERIFIED' not in row['flags'] or 'CURRENCY_NOT_CONFIRMED_2026_11_11' not in row['flags']:
                failures.append(rid + ': unsupported price not blank/flagged')
        if row.get('price_usd') is not None and row.get('price_captured_utc') == '2026-11-11':
            if not explicit_usd(raw.get(rid, {}), hand.get(rid)):
                failures.append(rid + ': populated November 11 USD amount lacks explicit currency evidence')
    if failures:
        print('FAIL currency evidence:\n'+'\n'.join(failures))
        return 1
    print('PASS currency evidence: 8 unsupported assertions blank/flagged; remaining populated November 11 amounts have explicit USD evidence. Not exact-variant or price/authenticity certification.')
    return 0


class CurrencyTests(unittest.TestCase):
    def test_bare_dollar_is_not_usd(self):
        self.assertFalse(explicit_usd({}, {'verbatim':['$990 (Setting Only)']}))
    def test_menu_is_not_selection(self):
        self.assertFalse(explicit_usd({}, {'verbatim':['AUD CAD GBP USD $990']}))
    def test_explicit_price_code(self):
        self.assertTrue(explicit_usd({}, {'verbatim':['$990 USD']}))
        self.assertTrue(explicit_usd({}, {'verbatim':['US$871.00']}))
    def test_structured_currency(self):
        self.assertTrue(explicit_usd({'structured_prices':[{'price':'1','currency':'USD'}]}))
    def test_missing_or_mixed_currency(self):
        self.assertFalse(explicit_usd({'structured_prices':[{'price':'1','currency':''}]}))
        self.assertFalse(explicit_usd({'structured_prices':[{'price':'1','currency':'USD'},{'price':'2','currency':'CAD'}]}))


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        sys.exit(check())
