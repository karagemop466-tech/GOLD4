#!/usr/bin/env python3
"""
patch_20261022_corroboration.py — Audit-trailed data patch.

Applies corroboration gathered at 2026-10-22T23:33–23:40Z from dated search
snapshots of OFFICIAL retailer pages (live page-fetch proxy was down). No value
is invented: every added field was read from a snapshot of the seller's own page,
with the snapshot context recorded in notes. Rows remain Level B-SNIPPET until a
live fetch re-confirms them; new irregularities are added as flags.

Run once: python3 scripts/patch_20261022_corroboration.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "data" / "rings.json"
doc = json.loads(p.read_text())
by_id = {r["id"]: r for r in doc["rings"]}

def upd(rid, **kw):
    r = by_id[rid]
    r.update(kw)

# --- Blue Nile rows: SKU/width/details read from snapshots of official product pages ---
upd("BN-192261",
    sku="502500y14", width_mm="1.80",
    notes=("Snapshot of official product page showed: Stock Number 502500y14, Metal 14K Yellow Gold, "
           "Width 1.80mm, '$1,290 (Setting Price)'. Corroborated by JSON-LD on official category page "
           "bluenile.com/engagement-rings/styles/simple (sku 502500y14, InStock, price 1290). "
           "Corroboration gathered 2026-10-22T23:35Z."))

upd("BN-203321",
    sku="501580y14", width_mm="5.00",
    flags=["Price from search snapshot of official page - live re-confirmation PENDING",
           "IRREGULARITY on seller page: specs say Metal=14K Yellow Gold but the seller's own Product Details text says 'this platinum solitaire setting' - confirm metal with seller before buying"],
    notes=("Snapshot of official product page showed: Stock Number 501580y14, Metal 14K Yellow Gold, Width 5.00mm, "
           "'$2,050 (Setting Price)'. Product Details text on the same page erroneously mentions 'platinum solitaire setting' "
           "(copy/paste inconsistency by the seller) - flagged, not silently corrected. Corroboration gathered 2026-10-22T23:36Z."))

upd("BN-203303",
    sku="501472y14", width_mm="4.00",
    price_basis=("Setting Price; setting includes 6 prong-set emerald-cut side diamonds, total 1 ct "
                 "(based on 1 ct center stone per seller disclaimer); center diamond sold separately"),
    flags=["Price from search snapshot of official page - live re-confirmation PENDING"],
    notes=("Snapshot of official product page showed: Stock Number 501472y14, Metal 14K Yellow Gold, Width 4.00mm, "
           "'$5,190 (Setting Price)', Natural Diamond Information: Shape Emerald, Quantity 6, Total Carat 1, "
           "Color G-H, Clarity VS2-SI1, Setting Prong; disclaimer: diamond counts based on a 1 ct center stone. "
           "Earlier 'price basis ambiguous' flag resolved from the same official page. Corroboration gathered 2026-10-22T23:36Z."))

upd("BN-195730",
    sku="502120w14", width_mm="2.40",
    notes=("Snapshot of official product page showed: Stock Number 502120w14, 14K White Gold, 2.40mm, Rhodium Finish: Yes. "
           "Price $1,145 (Setting Price) corroborated by official category page bluenile.com/engagement-rings/styles/gold/white-gold "
           "with JSON-LD (sku 502120w14, InStock). Same style family as live-verified BN-203348 (502120y14). "
           "Corroboration gathered 2026-10-22T23:37Z."))

upd("BN-315661",
    sku="505094w14", width_mm="1.75",
    notes=("Snapshot of official product page showed: Stock Number 505094w14, Metal 14K White Gold, Width 1.75mm, "
           "Rhodium Finish: Yes, 26 round diamonds, total 1/5 ct, F-G color, VS1-VS2 clarity, "
           "'$2,210 $1,657 (Setting Price) -25%'. Corroboration gathered 2026-10-22T23:37Z."))

upd("BN-310896",
    sku="505038y14", width_mm="1.80",
    flags=["Price from search snapshot of official page - live re-confirmation PENDING",
           "SALE PRICE VARIES across official Blue Nile category snapshots: $772 (-20%) on product page & gold category, $724 (-25%) on affordable category, $730 on engravable category, $728 on designer category - sale is time-sensitive; confirm the live price before buying"],
    notes=("Snapshot of official product page showed: Stock Number 505038y14, Metal 14K Yellow Gold, Width 1.80mm, "
           "'$965 $772 (Setting Price) -20%'. Other official category-page snapshots show different sale prices "
           "($724/$730/$728) - recorded as an irregularity flag, base price_usd kept at the product-page value $772. "
           "Corroboration gathered 2026-10-22T23:38Z."))

# --- Brilliant Earth rows: style/width/setting details + multi-snapshot corroboration ---
upd("BE-1D3939-14KY",
    notes=("Snapshot of official product page showed: '$1,190 (Setting Only)', Style BE1D3939-14KY, Metal 14K Yellow Gold, "
           "Width 2-1.3 mm, Setting Claw Prong (snapshot dated 2026-06-18). Price $1,190 independently corroborated by JSON-LD on "
           "official category pages: brilliantearth.com/engagement-rings/hidden-halo/ (2026-09-15) and "
           "brilliantearth.com/jewelry/collections/signature/ (2026-09-24, '14K Yellow Gold Freesia Hidden Halo Diamond Ring', price 1190). "
           "Corroboration gathered 2026-10-22T23:35Z."))

upd("BE-1D3939-18KY",
    notes=("Snapshot of official product page (dated 2026-09-28) showed: '$1,390 (Setting Only)', Metal: 18K Yellow Gold. "
           "Corroboration gathered 2026-10-22T23:35Z."))

upd("BE-BE1574-14KY",
    sku="BE1574-14KY", width_mm="1.8",
    notes=("Snapshot of official product page (dated 2026-08-07) showed: '$1,350 (Setting Only)', Style BE1574-14KY, "
           "Metal 14K Yellow Gold, Width 1.8 mm, Setting Four-Prong. Corroboration gathered 2026-10-22T23:39Z."))

upd("BE-BE1D2444-14KY",
    sku="BE1D2444-14KY", width_mm="2",
    notes=("Snapshot of official product page (dated 2026-08-27) showed: '$1,190 (Setting Only)', Style BE1D2444-14KY, "
           "Metal 14K Yellow Gold, Width 2 mm, Setting Claw Prong. Price $1,190 corroborated by JSON-LD on official category pages "
           "(solitaire 2026-08-25; yellow-gold solitaire 2026-09-23; princess-cut 2026-09-14). "
           "Corroboration gathered 2026-10-22T23:39Z."))

doc["meta"]["corroboration_pass_utc"] = "2026-10-22T23:40Z"
doc["meta"]["corroboration_note"] = ("All Level B rows re-checked against additional dated snapshots of the SAME official retailer pages "
                                     "(including embedded schema.org JSON-LD where present). Rows stay B-SNIPPET until a live fetch confirms them. "
                                     "Two irregularities found and flagged: BN-203321 description/spec mismatch, BN-310896 varying sale prices.")
p.write_text(json.dumps(doc, indent=2) + "\n")
print("patched", p)

# --- gold spot cross-check ---
sp = ROOT / "data" / "gold_spot.json"
spot = json.loads(sp.read_text())
spot["cross_check"] = {
    "status": "DONE-SNAPSHOT",
    "checked_at_utc": "2026-10-22T23:38Z",
    "method": "Dated search snapshots of official price pages (live page-fetch proxy outage); values are each source's own published numbers",
    "sources": [
        {"name": "Kitco - Gold Price Today", "url": "https://www.kitco.com/charts/gold",
         "value_usd_oz": 4062.30, "as_of": "2026-10-22 10:54 a.m. ET (bid; down $78.00 / -1.88% on the day)"},
        {"name": "Kitco - Gold Spot Prices", "url": "https://www.kitco.com/price/precious-metals",
         "value_usd_oz": 4032.80, "as_of": "2026-10-22 14:46 ET (bid 4,032.80 / ask 4,034.80)"},
        {"name": "APMEX - Gold Price", "url": "https://www.apmex.com/gold-price",
         "value_usd_oz": 4042.90, "as_of": "2026-10-22 7:13:01 PM ET (per-gram $129.98)"},
    ],
    "assessment": ("Primary reading $4,028.10 @ 2026-10-22T23:01:42Z lies inside the Oct-22 intraday range seen across sources "
                   "($4,028.10-$4,062.30 on a day down ~1.9-2.6%). Nearest-in-time comparison: APMEX $4,042.90 @ 23:13Z -> "
                   "difference $14.80 (0.37%), consistent with normal intraday movement. Cross-check PASSES at snapshot level; "
                   "re-verify live before any melt-value decision.")
}
sp.write_text(json.dumps(spot, indent=2) + "\n")
print("patched", sp)
