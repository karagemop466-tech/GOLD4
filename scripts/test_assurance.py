#!/usr/bin/env python3
"""Regression checks for conservative price parsing and current-review publication."""
import json
import re
import unittest
from pathlib import Path
from build_source_health import money, reconcile

ROOT = Path(__file__).resolve().parents[1]


class AssuranceTests(unittest.TestCase):
    def test_reject_ambiguous_numbers(self):
        for value in (True, False, '-585', -585, '$585', 'EUR 585', '585 USD',
                      '1.234,56', 'NaN', float('nan'), float('inf'), '1e3', {}, []):
            with self.subTest(value=value):
                self.assertIsNone(money(value))

    def test_accept_plain_numbers(self):
        for value, expected in [('585.00', 585), ('1,234.56', 1234.56), (0, 0), (585.5, 585.5)]:
            self.assertEqual(money(value), expected)

    def record(self, currency):
        return {'classification': 'OK', 'http_status': 200,
                'structured_prices': [{'price': '585', 'currency': currency,
                                       'source': 'json-ld', 'type': 'Offer'}]}

    def row(self):
        return {'id': 'TEST', 'retailer': 'Test', 'product_name': 'Test',
                'url': 'https://example.com/ring', 'price_usd': 585}

    def test_missing_or_foreign_currency_never_confirms_usd(self):
        for currency in ('', 'EUR', 'CAD'):
            self.assertEqual(reconcile(self.row(), self.record(currency))['price_state'], 'NOT_MACHINE_READABLE')

    def test_explicit_usd_can_match(self):
        self.assertEqual(reconcile(self.row(), self.record('USD'))['price_state'], 'CONFIRMED')

    def test_unreachable_never_confirms(self):
        for state in ('HTTP_404', 'REFUSED_403', 'ENVIRONMENT_BLOCKED', 'SOFT_404'):
            record = self.record('USD')
            record['classification'] = state
            self.assertEqual(reconcile(self.row(), record)['price_state'], 'SOURCE_NOT_REACHED')

    def test_review_has_exactly_all_rows_and_blank_current_prices(self):
        page = (ROOT / 'pages/session-review.html').read_text()
        rows = json.loads((ROOT / 'data/rings.json').read_text())['rows']
        ids = re.findall(r'data-review-id="([^"]+)"', page)
        self.assertCountEqual(ids, [r['id'] for r in rows])
        self.assertEqual(page.count('class="current-price" aria-label="Unverified current price"></td>'), len(rows))
        for row in rows:
            self.assertIn('href="' + row['url'].replace('&', '&amp;') + '"', page)
        self.assertNotRegex(page, r'<script|javascript:|\son\w+=')

    def test_pr_checks_do_not_cancel_other_sessions_or_production(self):
        workflow = (ROOT / '.github/workflows/pages.yml').read_text()
        self.assertIn("github.event.pull_request.number || 'production'", workflow)
        self.assertNotIn('group: pages\n', workflow)

    def test_read_only_workflow(self):
        workflow = (ROOT / '.github/workflows/live-source-check.yml').read_text()
        self.assertIn('contents: read', workflow)
        self.assertNotIn('git push', workflow)
        # Expressions in YAML configuration are fine; none may enter run scripts.
        self.assertNotIn('HEAD:${{ github.head_ref }}', workflow)


if __name__ == '__main__':
    unittest.main(verbosity=2)
