#!/usr/bin/env python3
"""Regression checks for conservative price parsing and current-review publication."""
import json
import re
import unittest
import urllib.error
from pathlib import Path
from build_source_health import money, reconcile
from live_source_check import AllowlistedRedirectHandler

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

    def test_multiple_variant_offers_are_not_exact_confirmation(self):
        record = self.record('USD')
        record['structured_prices'].append({'price': '398', 'currency': 'USD',
                                            'source': 'json-ld', 'type': 'Offer'})
        self.assertEqual(reconcile(self.row(), record)['price_state'],
                         'MULTIPLE_OFFERS_INCLUDE_STORED')
        # Repeated copies of one distinct amount are not multiple variants.
        record['structured_prices'][1]['price'] = '585'
        self.assertEqual(reconcile(self.row(), record)['price_state'], 'CONFIRMED')

    def test_redirects_stay_https_and_on_allowlisted_hosts(self):
        handler = AllowlistedRedirectHandler({'example.com'})
        for target in ('http://example.com/next', 'https://evil.example/next'):
            with self.subTest(target=target), self.assertRaises(urllib.error.URLError):
                handler.redirect_request(object(), None, 302, 'Found', {}, target)

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

    def test_evidence_return_is_isolated_and_ref_validated(self):
        workflow = (ROOT / '.github/workflows/live-source-check.yml').read_text()
        self.assertIn('permissions:\n  contents: read', workflow)
        self.assertIn('live-check:\n', workflow)
        self.assertIn('publish-evidence:\n', workflow)
        self.assertIn('github.event.pull_request.head.repo.full_name == github.repository', workflow)
        self.assertIn('git check-ref-format --branch "$PR_BRANCH"', workflow)
        self.assertIn('git push origin "HEAD:refs/heads/$PR_BRANCH"', workflow)
        self.assertIn('git add -- "${artifacts[@]}"', workflow)
        self.assertNotIn('HEAD:${{ github.head_ref }}', workflow)
        # GitHub expressions belong in action inputs/env, never in shell text.
        in_run = False
        run_indent = 0
        for line in workflow.splitlines():
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if stripped.startswith('run:'):
                self.assertNotIn('${{', line)
                in_run = True
                run_indent = indent
                continue
            if in_run and stripped and indent <= run_indent:
                in_run = False
            if in_run:
                self.assertNotIn('${{', line)


if __name__ == '__main__':
    unittest.main(verbosity=2)
