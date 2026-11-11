#!/usr/bin/env python3
"""Offline adversarial tests. All domains/data here are synthetic fixtures."""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, MagicMock
from urllib.request import Request
from urllib.error import URLError
from email.message import Message

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import live_source_check as live


class SourceSecurity(unittest.TestCase):
    allowed = {'example.com'}

    def test_valid_https(self):
        for url in ['https://example.com/a', 'https://www.example.com/a',
                    'https://example.com:443/']:
            with self.subTest(url=url):
                self.assertTrue(live.host_ok(url, self.allowed))

    def test_unsafe_urls(self):
        for url in ['http://example.com/', 'file:///etc/passwd', 'https://example.com.evil.test/',
                    'https://evil-example.com/', 'https://example.com@evil.test/',
                    'https://evil.test@example.com/', 'https://example.com:8080/',
                    'https://example.com:bad/', 'https://shop.example.com/a', 'https://[invalid/', 'https://127.0.0.1/',
                    'https://example.com/\nfoo', 'https://example.com\\@evil.test/']:
            with self.subTest(url=url):
                self.assertFalse(live.host_ok(url, self.allowed))

    def test_redirect_blocked_before_request(self):
        handler = live.SourceRedirectHandler(self.allowed)
        req = Request('https://example.com/a')
        for target in ['https://evil.test/', 'http://example.com/', 'https://127.0.0.1/']:
            with self.subTest(target=target), self.assertRaises(live.UnsafeSourceURL):
                handler.redirect_request(req, None, 302, 'Found', {}, target)

    def test_same_host_redirect(self):
        req = live.SourceRedirectHandler(self.allowed).redirect_request(
            Request('https://example.com/a'), None, 302, 'Found', {}, 'https://example.com/b')
        self.assertEqual(req.full_url, 'https://example.com/b')

    def test_invalid_initial_never_opens_network(self):
        with patch.object(live.urllib.request, 'build_opener') as opener:
            rec = live.fetch('https://evil.test/', 1, self.allowed)
            opener.assert_not_called()
            self.assertEqual(live.classify(rec), 'SECURITY_BLOCKED')

    def test_blocked_redirect_is_not_dead_link(self):
        with patch.object(live.urllib.request, 'build_opener') as opener:
            opener.return_value.open.side_effect = live.UnsafeSourceURL('blocked')
            self.assertEqual(live.classify(live.fetch('https://example.com/', 1, self.allowed)),
                             'SECURITY_BLOCKED')

    def test_connection_failure_cause_not_inferred(self):
        with patch.object(live.urllib.request, 'build_opener') as opener:
            opener.return_value.open.side_effect = URLError('synthetic DNS failure')
            rec = live.fetch('https://example.com/', 1, self.allowed)
            self.assertEqual(live.classify(rec), 'NO_RESPONSE')
            self.assertNotIn('_env_blocked', rec)

    def test_bounded_response_cannot_be_ok(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.geturl.return_value = 'https://example.com/'
        response.status = 200
        response.headers = Message()
        response.read.return_value = b'x' * (live.MAX_RESPONSE_BYTES + 1)
        with patch.object(live.urllib.request, 'build_opener') as opener:
            opener.return_value.open.return_value = response
            rec = live.fetch('https://example.com/', 1, self.allowed)
            response.read.assert_called_once_with(live.MAX_RESPONSE_BYTES + 1)
            self.assertTrue(rec['body_truncated'])
            self.assertEqual(rec['bytes'], live.MAX_RESPONSE_BYTES)
            self.assertEqual(live.classify(rec), 'INCOMPLETE_RESPONSE')

    def test_only_selects_one_ring(self):
        print("SYNTHETIC CLI fixture: NO_RESPONSE below is mocked, not a retailer request.")
        captured = []
        def fake_fetch(url, timeout, allowed):
            captured.append(url)
            return {'url': url, 'http_status': None}
        import tempfile
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp, patch.object(live, 'REPORTS', Path(tmp)), \
             patch.object(live, 'fetch', side_effect=fake_fetch), \
             patch.object(live.time, 'sleep'), patch.object(sys, 'argv', ['check', '--only', 'AL-01']):
            self.assertEqual(live.main(), 0)
            self.assertEqual(len(captured), 1)
            artifact = json.loads((Path(tmp) / 'live_source_check_latest.json').read_text())
            self.assertTrue(artifact['all_requests_failed'])
            self.assertFalse(artifact['network_environment_blocked'])
            self.assertEqual(artifact['summary'], {'NO_RESPONSE': 1})

    def test_unknown_only_fails(self):
        print('SYNTHETIC negative CLI fixture: FAIL below is the expected rejection of an unknown ID.')
        with patch.object(sys, 'argv', ['check', '--only', 'NOT-A-ROW']), \
             patch.object(live, 'fetch') as fetch:
            self.assertEqual(live.main(), 4)
            fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
