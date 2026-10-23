#!/usr/bin/env python3
"""Adversarial tests for the isolated, fail-closed readiness register."""
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest

import readiness as r


class ProductRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current = None
        self.in_price = False
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr" and "data-row-id" in attrs:
            self.current = {"id": attrs["data-row-id"], "urls": [], "price": "", "price_cells": 0}
        if tag == "a" and self.current:
            self.current["urls"].append(attrs.get("href", ""))
        if tag == "td" and self.current and attrs.get("class") == "current-price":
            self.in_price = True
            self.current["price_cells"] += 1
        if tag == "script":
            self.scripts.append(attrs.get("src"))

    def handle_data(self, data):
        if self.current and self.in_price:
            self.current["price"] += data

    def handle_endtag(self, tag):
        if tag == "td":
            self.in_price = False
        if tag == "tr" and self.current:
            self.rows.append(self.current)
            self.current = None


class ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rings = r.read_json(r.ROOT / "data/rings.json")
        cls.raw = deepcopy(cls.rings["rows"][0])
        cls.sellers = {s["id"]: s for s in r.read_json(r.ROOT / "data/sellers.json")["sellers"]}
        cls.sources = {s["id"]: s for s in r.read_json(r.ROOT / "data/sources.json")["sources"]}

    def evaluate(self, **changes):
        raw = deepcopy(self.raw)
        raw.update(changes)
        return r.evaluate_row(raw, self.sellers[raw["retailer_id"]], self.sources, self.rings["captured_utc"])

    def test_only_finite_positive_numeric_inputs(self):
        for value in [True, False, None, "3.58", "$585", "-12", "12 grams", "1,200", 0, -1,
                      float("nan"), float("inf"), Decimal("Infinity"), Decimal("NaN"), Decimal("1e10000")]:
            with self.subTest(value=value):
                self.assertIsNone(r.positive_number(value))
        for value in [1, 3.58, Decimal("0.7")]:
            self.assertIsNotNone(r.positive_number(value))

    def test_official_https_hosts_not_lookalikes(self):
        for url in ["http://www.allurez.com/a", "https://www.allurez.com.evil.test/a",
                    "https://www.allurez.com@evil.test/a", "https://evil@www.allurez.com/a",
                    "https://www.allurez.com:8443/a", "javascript:alert(1)", "data:text/html,x",
                    "//www.allurez.com/a", "https://www.allurez.com/\nredirect", "https://www.allurez.com/%0d%0aX",
                    'https://www.allurez.com/\"><script>', "https://www.allurez.com\\@evil.test/a"]:
            with self.subTest(url=url):
                self.assertIsNone(r.safe_url(url, "allurez"))
        self.assertEqual(r.safe_url(self.raw["url"], "allurez"), self.raw["url"])
        self.assertIsNone(r.safe_url("https://www.allurez.com/a", "mene"))

    def test_solid_wording_cannot_be_inferred_from_karat_purity_or_name(self):
        for quote in [None, "14K Yellow Gold", "Pure 24k Gold sold by weight with Certificate of Authenticity",
                      "not solid gold", "hollowed 14k solid gold", "gold plated solid gold", "gold-filled", True]:
            with self.subTest(quote=quote):
                result = self.evaluate(solid_gold_status="stated", solid_gold_statement=quote)
                self.assertIsNone(result["recorded_explicit_solid_wording"])
                self.assertIn("EXPLICIT_SOLID_WORDING_UNVERIFIED", result["flags"])
        for quote in ["Solid Yellow Gold (14k)", "Material: 10K Solid Gold", "recycled solid 14k gold", "Solid 14k Yellow Gold"]:
            self.assertEqual(self.evaluate(solid_gold_status="stated", solid_gold_statement=quote)["recorded_explicit_solid_wording"], quote)

    def test_status_without_wording_and_wording_without_status_do_not_pass(self):
        self.assertIsNone(self.evaluate(solid_gold_status="stated", solid_gold_statement=None)["recorded_explicit_solid_wording"])
        self.assertIsNone(self.evaluate(solid_gold_status="not_stated", solid_gold_statement="solid gold")["recorded_explicit_solid_wording"])

    def test_weight_needs_provenance_source_and_scope(self):
        for changes in [{"weight_verification": "V2_official_page_snapshot_only"},
                        {"weight_source_url": None}, {"weight_source_url": "https://www.mene.com/a"},
                        {"weight_scope": ""}, {"weight_g": True}, {"weight_g": -1}]:
            with self.subTest(changes=changes):
                self.assertIsNone(self.evaluate(**changes)["recorded_weight_g"])
        result = self.evaluate()
        self.assertEqual(result["recorded_weight_g"], self.raw["weight_g"])
        self.assertIsNone(result["weight_field_capture_date_utc"])
        self.assertIn("WEIGHT_FIELD_CAPTURE_DATE_NOT_RECORDED", result["flags"])

    def test_weight_is_never_back_solved_from_price(self):
        result = self.evaluate(weight_g=None, price_usd=1000000)
        self.assertIsNone(result["recorded_weight_g"])
        self.assertIsNone(result["current_exact_price_usd"])

    def test_hallmark_boolean_does_not_prove_maker_mark_or_assay(self):
        result = self.evaluate(hallmark_published=True, assay_passed=True)
        self.assertIsNone(result["hallmark_and_maker_evidence"])
        self.assertIsNone(result["physical_test_result"])
        self.assertFalse(result["online_evidence_complete"])

    def test_reputation_boolean_has_no_approval_override(self):
        seller = deepcopy(self.sellers[self.raw["retailer_id"]])
        seller["reputation_independently_verified"] = True
        result = r.evaluate_row(self.raw, seller, self.sources, self.rings["captured_utc"])
        self.assertIsNone(result["independent_reputation_evidence"])
        self.assertFalse(result["online_evidence_complete"])

    def test_window_and_source_match_do_not_establish_configuration_rights(self):
        seller = deepcopy(self.sellers[self.raw["retailer_id"]])
        seller["return_window_days"] = 365
        seller["return_exclusions"] = []
        result = r.evaluate_row(self.raw, seller, self.sources, self.rings["captured_utc"])
        self.assertIsNone(result["configured_return_and_testing_eligibility"])
        self.assertTrue(result["official_return_policy_url"])

    def test_structured_confirmation_never_becomes_current_exact_quote(self):
        for state in ["CONFIRMED", "MULTIPLE_OFFERS_INCLUDE_STORED", "DIFFERS", "SOURCE_NOT_REACHED"]:
            result = self.evaluate(price_usd=585, price_captured_utc="2026-10-23", current_exact_price_usd=585,
                                   source_check={"state": "OK", "price_state": state})
            self.assertIsNone(result["current_exact_price_usd"])
            self.assertFalse(result["online_evidence_complete"])

    def test_missing_or_unsafe_source_suppresses_claim(self):
        result = self.evaluate(url="javascript:alert(1)", solid_gold_status="stated", solid_gold_statement="solid gold")
        self.assertIsNone(result["official_product_url"])
        self.assertIsNone(result["recorded_karat_claim"])
        self.assertIsNone(result["recorded_explicit_solid_wording"])

    def test_karat_bool_fraction_or_unsupported_number_is_blank(self):
        for value in [True, 14.5, 99, None, "14K"]:
            self.assertIsNone(self.evaluate(karat=value)["recorded_karat_claim"])

    def test_json_rejects_duplicate_keys_and_nonfinite_constants(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.json"
            for text in ['{"price": 1, "price": 2}', '{"price": NaN}', '{"price": Infinity}']:
                path.write_text(text)
                with self.assertRaises(ValueError):
                    r.read_json(path)

    def test_report_is_deterministic_hash_bound_and_read_only(self):
        before = {name: sha256((r.ROOT / name).read_bytes()).hexdigest() for name in r.INPUTS}
        first, second = r.outputs(r.ROOT), r.outputs(r.ROOT)
        self.assertEqual(first, second)
        report = json.loads(first[r.OUTPUT_JSON])
        self.assertEqual(report["input_sha256"], before)
        self.assertEqual(before, {name: sha256((r.ROOT / name).read_bytes()).hexdigest() for name in r.INPUTS})
        self.assertEqual(len(report["rows"]), len(self.rings["rows"]))
        self.assertEqual(report["stats"]["complete_online_evidence"], 0)
        self.assertEqual(report["stats"]["current_exact_quotes"], 0)

    def test_every_rendered_row_has_official_source_and_one_blank_current_price(self):
        report = r.build_report(r.ROOT)
        parser = ProductRows()
        parser.feed(r.render_html(report))
        self.assertEqual(len(parser.rows), len(report["rows"]))
        self.assertEqual(parser.scripts, ["../assets/app.js"])
        by_id = {row["id"]: row for row in report["rows"]}
        for row in parser.rows:
            self.assertIn(by_id[row["id"]]["official_product_url"], row["urls"])
            self.assertEqual(row["price_cells"], 1)
            self.assertEqual(row["price"], "")

    def test_html_escapes_recorded_text_and_attributes(self):
        report = r.build_report(r.ROOT)
        row = report["rows"][0]
        row["product_name"] = '\"><img src=x onerror=alert(1)>'
        row["recorded_weight_scope"] = "<script>alert(1)</script>"
        html = r.render_html(report)
        self.assertNotIn("<img", html)
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;img", html)
        self.assertIn("&lt;script&gt;", html)

    def test_field_capture_date_is_not_fabricated_or_overridden(self):
        self.assertIsNone(self.evaluate(weight_captured_utc="yesterday")["weight_field_capture_date_utc"])
        self.assertEqual(self.evaluate(weight_captured_utc="2026-10-22")["weight_field_capture_date_utc"], "2026-10-22")
        self.assertIsNone(r.date_only("2026-02-30"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
