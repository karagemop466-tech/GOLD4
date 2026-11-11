#!/usr/bin/env python3
"""Provenance and publication tests; malicious strings are synthetic fixtures."""
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
import sys

import build_review as review
import stage_pages


class Rows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.numeric = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'tr' and 'data-row-id' in attrs:
            self.row = {'id': attrs['data-row-id'], 'links': [], 'numbers': '', 'cells': 0}
        if self.row is not None and tag == 'td':
            self.numeric = attrs.get('class') in ('current-price', 'current-weight')
            self.row['cells'] += self.numeric
        if self.row is not None and tag == 'a':
            self.row['links'].append(attrs.get('href'))

    def handle_data(self, data):
        if self.row is not None and self.numeric:
            self.row['numbers'] += data

    def handle_endtag(self, tag):
        if tag == 'td':
            self.numeric = False
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None


class ReviewTests(unittest.TestCase):
    def mutate(self, filename, callback):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in review.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((review.ROOT / name).read_bytes())
            path = root / filename
            data = json.loads(path.read_text())
            callback(data)
            path.write_text(json.dumps(data))
            return review.outputs(root)

    def test_all_rows_have_sources_and_blank_numeric_cells(self):
        out = review.outputs()
        register = json.loads(out[review.OUTPUTS[0]])
        parser = Rows()
        parser.feed(out[review.OUTPUTS[1]])
        self.assertEqual(len(parser.rows), len(register['rows']))
        self.assertEqual({r['id'] for r in parser.rows}, {r['id'] for r in register['rows']})
        for htmlrow, row in zip(parser.rows, register['rows']):
            self.assertEqual(htmlrow['numbers'], '')
            self.assertEqual(htmlrow['cells'], 2)
            self.assertIn(row['source_url'], htmlrow['links'])
            self.assertIsNone(row['current_exact_price_usd'])
            self.assertIsNone(row['current_exact_metal_weight_g'])
            self.assertFalse(row['purchase_approved'])

    def test_reject_source_mismatch(self):
        with self.assertRaises(ValueError):
            self.mutate(review.INPUTS[-1], lambda d: d['product_observations'][0].update(source_url='https://evil.test'))

    def test_reject_price_promotion(self):
        with self.assertRaises(ValueError):
            self.mutate(review.INPUTS[-1], lambda d: d['product_observations'][0].update(current_configured_price_usd=1))

    def test_reject_unknown_observation(self):
        with self.assertRaises(ValueError):
            self.mutate(review.INPUTS[-1], lambda d: d['product_observations'][0].update(id='UNKNOWN'))

    def test_unsafe_source_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate('data/rings.json', lambda d: d['rows'][0].update(url='javascript:alert(1)'))

    def test_xss_escaped(self):
        out = self.mutate('data/rings.json', lambda d: d['rows'][0].update(product_name='<script>alert(1)</script>'))
        self.assertNotIn('<script>alert(1)</script>', out[review.OUTPUTS[1]])
        self.assertIn('&lt;script&gt;', out[review.OUTPUTS[1]])

    def test_input_hash_changes(self):
        before = json.loads(review.outputs()[review.OUTPUTS[0]])
        changed = self.mutate('data/rings.json', lambda d: d['rows'][0].update(product_name='Hypothetical fixture'))
        after = json.loads(changed[review.OUTPUTS[0]])
        self.assertNotEqual(before['input_sha256']['data/rings.json'], after['input_sha256']['data/rings.json'])

    def test_stage_excludes_private_files_and_tooling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            dest = Path(tmp) / 'site'
            for file in ['index.html', '.nojekyll', '.git/config', '.github/workflows/pages.yml',
                         'scripts/private.py', '.env', 'assets/style.css', 'data/rings.json',
                         'pages/current-review.html', 'reviews/report.md']:
                target = root / file
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('synthetic fixture')
            (root / 'assets/leak.txt').symlink_to(root / '.git/config')
            stage_pages.stage(dest, root)
            for wanted in ['index.html', '.nojekyll', 'assets/style.css', 'data/rings.json', 'pages/current-review.html']:
                self.assertTrue((dest / wanted).exists())
            for banned in ['.git/config', '.github/workflows/pages.yml', '.env', 'assets/leak.txt', 'scripts/private.py']:
                self.assertFalse((dest / banned).exists())
            with self.assertRaises(ValueError):
                stage_pages.stage(root / 'recursive', root)

    def test_future_observation_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(review.INPUTS[-1], lambda d: d['product_observations'][0].update(read_date_utc='2099-01-01'))

    def test_invalid_date_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(review.INPUTS[-1], lambda d: d['product_observations'][0].update(read_date_utc='not a date'))

    def test_invalid_chunk_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(review.INPUTS[-1], lambda d: d['product_observations'][0].update(chunks_read=[True]))

    def test_legacy_layout_caller_still_builds(self):
        sys.path.insert(0, str(review.ROOT / 'scripts'))
        import build_pass20
        import build_site
        build_pass20.prime_layout()
        html = build_site.render('Hypothetical fixture', '<p>Fixture</p>', 'pass20', root='../')
        self.assertIn('2026-11-11', html)
        self.assertIn('10 product URLs', html)
        self.assertIn('54 not re-opened', html)

    def test_deterministic(self):
        self.assertEqual(review.outputs(), review.outputs())


if __name__ == '__main__':
    unittest.main()
