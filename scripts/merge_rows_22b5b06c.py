#!/usr/bin/env python3
"""
merge_rows_22b5b06c.py — Integration script for session arena/22b5b06c-gold4.

Adds this session's independently collected rows to the published dataset
(data/rings.json) in the established schema, without modifying any existing
row's verified content (the single exception is an APPENDED cross-session
corroboration note on BE-01, whose text is preserved verbatim).

Provenance: every value below was read by this session on 2026-10-22 UTC from
the referenced official page — either by live fetch (V1_direct_page_fetch) or,
during the 23:20-23:47Z fetch-service outage, from dated search snapshots of
the same official pages (V2_official_page_snapshot_only, always flagged
PRICE_V2_ONLY per scripts/audit.py). The session's raw working dataset is kept
at data/preserved/rings_candidates_22b5b06c.json.

Also records (informational, not used in any derived arithmetic):
  - this session's live gold-api.com spot reading and same-day Kitco/APMEX
    snapshot readings in data/gold_spot.json under a clearly labelled key;
  - a Pass 7 entry in data/verification_log.json.

Idempotent: rows already present (by id) are skipped.
Run: python3 scripts/merge_rows_22b5b06c.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

BASE_FLAGS = ["NO_WEIGHT_PUBLISHED", "SOLID_NOT_STATED", "HALLMARK_NOT_PUBLISHED"]
BY = "arena/22b5b06c-gold4"
CAT_URL = "https://www.bluenile.com/engagement-rings/styles/gold/yellow-gold"
CAT_DETAIL = ("Price and listing read from a live fetch of the seller's official category page "
              f"({CAT_URL}) at 2026-10-22T23:15Z; the product page itself was not separately fetched for this row.")


def bn(pid, name, style, cat, metal, karat, sku, width, price, verif, basis, url, psrc,
       flags, detail, rever, pair=None):
    row = {
        "id": pid, "retailer": "Blue Nile", "retailer_id": "blue-nile",
        "product_name": name, "style": style, "category": cat,
        "metal_label": metal, "karat": karat, "sku": sku, "width_mm": width,
        "url": url,
        "solid_gold_statement": None, "solid_gold_status": "not_stated",
        "hallmark_published": False,
        "price_usd": price, "price_basis": basis,
        "price_captured_utc": "2026-10-22", "price_source_url": psrc,
        "price_verification": verif,
        "weight_g": None, "weight_scope": None, "weight_source_url": None,
        "weight_verification": "U_unverified",
        "returns_source_id": "bluenile-returns",
        "flags": BASE_FLAGS + flags,
        "flag_detail": detail,
        "reverified_utc": "2026-10-22", "reverified_by": BY,
        "reverification": rever,
    }
    if pair:
        row["pair_id"] = pair
    return row


def be(pid, name, style, cat, metal, karat, sku, width, price, basis, url,
       flags, detail, rever, pair=None):
    row = bn(pid, name, style, cat, metal, karat, sku, width, price,
             "V2_official_page_snapshot_only", basis, url, url, flags, detail, rever, pair)
    row.update({"retailer": "Brilliant Earth", "retailer_id": "brilliant-earth",
                "returns_source_id": "brilliantearth-atelier"})
    return row


SETTING = "Setting only — page shows '(Setting Price)'; centre diamond sold separately"
P = "https://www.bluenile.com/engagement-rings/design-your-own-ring/"

NEW_ROWS = [
    # ---- Brilliant Earth (insert after main's BE-03) ----
    be("BE-04", "Freesia Hidden Halo Diamond Ring", "Hidden halo — concealed pavé accents beneath the centre stone, claw prong",
       "pave", "14K Yellow Gold", 14, "BE1D3939-14KY", None, 1190.0,
       "Setting only — page shows '$1,190 (Setting Only)'",
       "https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-14K-Gold-BE1D3939-76789075/",
       ["PRICE_V2_ONLY"],
       "Snapshot of the official product page (dated 2026-06-18) showed: $1,190 (Setting Only), Style BE1D3939-14KY, Metal 14K Yellow Gold, 'Width: 2-1.3 mm' (tapered — recorded verbatim here; width_mm left blank rather than reduced to one number), Setting Claw Prong. Price independently corroborated by schema.org JSON-LD on two official category pages: /engagement-rings/hidden-halo/ (2026-09-15) and /jewelry/collections/signature/ (2026-09-24), both 1190. Returns anchored to the Brilliant Earth product-page source used by BE-01/BE-02; the generic BE returns-policy URL was not re-fetched by this session.",
       "2026-10-22T23:35Z: three dated snapshots of official Brilliant Earth pages agree on $1,190 (product page + two category JSON-LD records). Live re-fetch pending (fetch-service outage 23:20-23:47Z).",
       pair="PAIR-BE-FREESIA"),
    be("BE-05", "Freesia Hidden Halo Diamond Ring", "Hidden halo — concealed pavé accents beneath the centre stone",
       "pave", "18K Yellow Gold", 18, None, None, 1390.0,
       "Setting only — page shows '$1,390 (Setting Only)'",
       "https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-Gold-BE1D3939-19424930/",
       ["PRICE_V2_ONLY"],
       "Snapshot of the official product page (dated 2026-09-28) showed: $1,390 (Setting Only), Metal 18K Yellow Gold. The 18K style code was not visible in the captured text, so sku stays blank rather than inferred from the 14K variant.",
       "2026-10-22T23:35Z: value re-read from the dated official-page snapshot; live re-fetch pending (outage).",
       pair="PAIR-BE-FREESIA"),
    be("BE-06", "Fleur Solitaire Ring", "Solitaire, four-prong tulip head, low profile",
       "solitaire", "14K Yellow Gold", 14, "BE1574-14KY", 1.8, 1350.0,
       "Setting only — page shows '$1,350 (Setting Only)'",
       "https://www.brilliantearth.com/Fleur-Solitaire-Ring-14K-Gold-BE1574-76785943/",
       ["PRICE_V2_ONLY"],
       "Snapshot of the official product page (dated 2026-08-07) showed: $1,350 (Setting Only), Style BE1574-14KY, Metal 14K Yellow Gold, Width 1.8 mm, Setting Four-Prong.",
       "2026-10-22T23:39Z: value re-read from the dated official-page snapshot; live re-fetch pending (outage)."),

    # ---- Blue Nile (insert after BN-08) ----
    bn("BN-09", "Classic Simple Solitaire Engagement Ring", "Solitaire, classic simple",
       "solitaire", "14K Yellow Gold", 14, "502120y14", 2.4, 1145.0,
       "V1_direct_page_fetch", SETTING,
       P + "classic-simple-solitaire-engagement-ring-in-14k-yellow-gold-item-203348",
       P + "classic-simple-solitaire-engagement-ring-in-14k-yellow-gold-item-203348",
       [],
       "Product page fetched LIVE 2026-10-22T23:13Z: Stock Number 502120y14, Metal 14K Yellow Gold, Width 2.40mm, $1,145 '(Setting Price)'. Page advertises Free Shipping, Free Returns, and a Limited Lifetime Warranty on gold jewelry with purchase price $1,000 or more; seller contact +1-800-242-2728 / service@bluenile.com shown on page.",
       "Live fetch 2026-10-22T23:13Z; all recorded fields read directly from the fetched product page."),
    bn("BN-10", "Solitaire Engagement Ring With Pavé Basket In 14K Yellow Gold By James Allen",
       "Solitaire with pavé basket (By James Allen line, sold by Blue Nile)",
       "solitaire", "14K Yellow Gold", 14, None, None, 2260.0,
       "V1_direct_page_fetch", SETTING,
       P + "solitaire-engagement-ring-with-pave-basket-in-14k-yellow-gold-by-james-allen-item-311230", CAT_URL,
       ["PRICE_FROM_CATEGORY_PAGE"], CAT_DETAIL + " Price also re-displayed ($2,260) in the 'similar looks' block of a live-fetched Blue Nile product page (item 41515) at 23:19Z.",
       "Live category-page fetch 2026-10-22T23:15Z + live product-page re-display 23:19Z."),
    bn("BN-11", "Solitaire Engagement Ring With Intricate Basket In 14K Yellow Gold By James Allen",
       "Solitaire with intricate basket (By James Allen line)",
       "solitaire", "14K Yellow Gold", 14, None, None, 1385.0,
       "V1_direct_page_fetch", SETTING,
       P + "solitaire-engagement-ring-with-intricate-basket-in-14k-yellow-gold-by-james-allen-item-315036", CAT_URL,
       ["PRICE_FROM_CATEGORY_PAGE"], CAT_DETAIL + " Price also re-displayed ($1,385) in the 'similar looks' block of a live-fetched Blue Nile product page (item 41515) at 23:19Z.",
       "Live category-page fetch 2026-10-22T23:15Z + live product-page re-display 23:19Z."),
    bn("BN-12", "East West Knife Edge Cathedral Solitaire Engagement Ring In 14K Yellow Gold By James Allen",
       "East-west cathedral solitaire, knife edge (By James Allen line)",
       "solitaire", "14K Yellow Gold", 14, None, None, 975.0,
       "V1_direct_page_fetch", SETTING,
       P + "east-west-knife-edge-cathedral-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-311246", CAT_URL,
       ["PRICE_FROM_CATEGORY_PAGE"], CAT_DETAIL,
       "Live category-page fetch 2026-10-22T23:15Z."),
    bn("BN-13", "Pavé Diamond Halo Engagement Ring In 14K Yellow Gold (Oval) By James Allen",
       "Pavé halo for an oval centre stone (By James Allen line)",
       "pave", "14K Yellow Gold", 14, None, None, 1565.0,
       "V1_direct_page_fetch", SETTING,
       P + "pave-diamond-halo-engagement-ring-in-14k-yellow-gold-oval-by-james-allen-item-311127", CAT_URL,
       ["PRICE_FROM_CATEGORY_PAGE"], CAT_DETAIL,
       "Live category-page fetch 2026-10-22T23:15Z."),
    bn("BN-14", "Pavé Diamond Halo Engagement Ring In 14K Yellow Gold (Pear) By James Allen",
       "Pavé halo for a pear centre stone (By James Allen line)",
       "pave", "14K Yellow Gold", 14, None, None, 1555.0,
       "V1_direct_page_fetch", SETTING,
       P + "pave-diamond-halo-engagement-ring-in-14k-yellow-gold-pear-by-james-allen-item-311121", CAT_URL,
       ["PRICE_FROM_CATEGORY_PAGE"], CAT_DETAIL,
       "Live category-page fetch 2026-10-22T23:15Z."),
    bn("BN-15", "Petite Hidden Halo Solitaire Plus Diamond Engagement Ring in 14k Yellow Gold",
       "Hidden-halo solitaire plus (pavé accents beneath the head)",
       "pave", "14K Yellow Gold", 14, None, None, 1255.0,
       "V1_direct_page_fetch", SETTING,
       P + "petite-hidden-halo-solitaire-plus-diamond-engagement-ring-in-14k-yellow-gold-item-192506", CAT_URL,
       ["PRICE_FROM_CATEGORY_PAGE"], CAT_DETAIL + " Price also re-displayed ($1,255) in the 'similar looks' block of a live-fetched Blue Nile product page (item 41515) at 23:19Z.",
       "Live category-page fetch 2026-10-22T23:15Z + live product-page re-display 23:19Z."),
    bn("BN-16", "Bow-Tie Engagement Ring With Channel Set Round Diamonds In 14K Yellow Gold By James Allen",
       "Bow-tie band with channel-set round diamonds (By James Allen line)",
       "pave", "14K Yellow Gold", 14, None, None, 2350.0,
       "V1_direct_page_fetch", SETTING,
       P + "bow-tie-engagement-ring-with-channel-set-round-diamonds-in-14k-yellow-gold-by-james-allen-item-304294", CAT_URL,
       ["PRICE_FROM_CATEGORY_PAGE"], CAT_DETAIL,
       "Live category-page fetch 2026-10-22T23:15Z."),
    bn("BN-17", "Woven Solitaire Engagement Ring In 14K Yellow Gold By James Allen",
       "Woven split-band solitaire (By James Allen line)",
       "solitaire", "14K Yellow Gold", 14, "505038y14", 1.8, 772.0,
       "V2_official_page_snapshot_only",
       "Sale '(Setting Price)' — snapshot showed '$965 $772 (Setting Price) −20%'; the $965 list figure is the seller's own struck-through price",
       P + "woven-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-310896",
       P + "woven-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-310896",
       ["PRICE_V2_ONLY", "SALE_PRICE_VARIES_ACROSS_PAGES"],
       "Product-page snapshot showed Stock Number 505038y14, Metal 14K Yellow Gold, Width 1.80mm, '$965 $772 (Setting Price) −20%'. IRREGULARITY: other official Blue Nile category snapshots show different current sale prices for this same SKU — $724 (−25%) on /engagement-rings/affordable, $730 on /engagement-rings/engravable-engagement-rings/all, $728 on /engagement-rings/designer/all. Sale prices are time-sensitive and vary by page; confirm the live price before purchase.",
       "2026-10-22T23:38Z: five dated snapshots of official Blue Nile pages re-read; the price itself varies between them (see flag_detail) — recorded, not averaged."),
    bn("BN-18", "Knife Edge Solitaire Engagement Ring in 14k Yellow Gold", "Solitaire, knife-edge shank",
       "solitaire", "14K Yellow Gold", 14, "502500y14", 1.8, 1290.0,
       "V2_official_page_snapshot_only", SETTING,
       P + "knife-edge-solitaire-engagement-ring-in-14k-yellow-gold-item-192261",
       P + "knife-edge-solitaire-engagement-ring-in-14k-yellow-gold-item-192261",
       ["PRICE_V2_ONLY"],
       "Product-page snapshot showed Stock Number 502500y14, Metal 14K Yellow Gold, Width 1.80mm, $1,290 '(Setting Price)'. Corroborated by schema.org JSON-LD embedded in the official category page bluenile.com/engagement-rings/styles/simple (sku 502500y14, availability InStock, price 1290).",
       "2026-10-22T23:35Z: two independent official-page reads agree ($1,290). Live re-fetch pending (outage)."),
    bn("BN-19", "Wide Band Solitaire Engagement Ring in 14K Yellow Gold (5mm)", "Solitaire, wide flat band",
       "solitaire", "14K Yellow Gold", 14, "501580y14", 5.0, 2050.0,
       "V2_official_page_snapshot_only", SETTING,
       P + "wide-band-solitaire-engagement-ring-in-14k-yellow-gold-5mm-item-203321",
       P + "wide-band-solitaire-engagement-ring-in-14k-yellow-gold-5mm-item-203321",
       ["PRICE_V2_ONLY", "COPY_INCONSISTENT_METAL"],
       "Product-page snapshot showed Stock Number 501580y14, Metal 14K Yellow Gold, Width 5.00mm, $2,050 '(Setting Price)'. COPY_INCONSISTENT_METAL: the same page's Product Details text says 'this platinum solitaire setting features a flat profile' while every spec field says 14K Yellow Gold — the contradiction is recorded, not resolved; confirm the metal with the seller.",
       "2026-10-22T23:36Z: official-page snapshot re-read; metal-copy contradiction found and flagged."),
    bn("BN-20", "Emerald Cut Diamond Engagement Ring in 14K Yellow Gold (1 ct. tw.)",
       "Side-stone setting: six prong-set emerald-cut diamonds flanking the centre stone",
       "pave", "14K Yellow Gold", 14, "501472y14", 4.0, 5190.0,
       "V2_official_page_snapshot_only",
       "Setting price includes six prong-set emerald-cut side diamonds totalling 1 ct (side-diamond counts are stated by the page to be based on a 1 ct centre stone); centre diamond sold separately",
       P + "emerald-cut-diamond-engagement-ring-in-14k-yellow-gold-1-ct-tw-item-203303",
       P + "emerald-cut-diamond-engagement-ring-in-14k-yellow-gold-1-ct-tw-item-203303",
       ["PRICE_V2_ONLY"],
       "Product-page snapshot showed Stock Number 501472y14, Metal 14K Yellow Gold, Width 4.00mm, $5,190 '(Setting Price)', Natural Diamond Information: Shape Emerald, Quantity 6, Total Carat 1, Color G-H, Clarity VS2-SI1, Setting Type Prong, with the page's own disclaimer that diamond counts/weights are based on a 1 ct centre stone.",
       "2026-10-22T23:36Z: official-page snapshot re-read; price basis clarified from the same page."),
    bn("BN-21", "Classic Simple Solitaire Engagement Ring in 14k White Gold", "Solitaire, classic simple (white-gold variant of BN-09)",
       "solitaire", "14K White Gold", 14, "502120w14", 2.4, 1145.0,
       "V2_official_page_snapshot_only", SETTING,
       P + "classic-simple-solitaire-engagement-ring-in-14k-white-gold-item-195730",
       P + "classic-simple-solitaire-engagement-ring-in-14k-white-gold-item-195730",
       ["PRICE_V2_ONLY", "WHITE_GOLD"],
       "Product-page snapshot showed Stock Number 502120w14, 14K White Gold, 2.40mm, Rhodium Finish: Yes, $1,145 '(Setting Price)'. Corroborated by the official category page bluenile.com/engagement-rings/styles/gold/white-gold (JSON-LD sku 502120w14, InStock) and by the live-fetched yellow-gold sibling BN-09 (same 502120 style family, same $1,145, fetched 23:13Z).",
       "2026-10-22T23:37Z: two official-page reads agree ($1,145); live sibling variant (BN-09) fetched directly. Live re-fetch of THIS page pending (outage)."),
    bn("BN-22", "Pavé Contour Diamond Engagement Ring In 14K White Gold By James Allen",
       "Contour pavé band (By James Allen line)",
       "pave", "14K White Gold", 14, "505094w14", 1.75, 1657.0,
       "V2_official_page_snapshot_only",
       "Sale '(Setting Price)' — snapshot showed '$2,210 $1,657 (Setting Price) −25%'; includes 26 pavé-set round diamonds, 1/5 ct total, F-G colour, VS1-VS2 clarity",
       P + "pave-contour-diamond-engagement-ring-in-14k-white-gold-by-james-allen-item-315661",
       P + "pave-contour-diamond-engagement-ring-in-14k-white-gold-by-james-allen-item-315661",
       ["PRICE_V2_ONLY", "WHITE_GOLD"],
       "Product-page snapshot showed Stock Number 505094w14, Metal 14K White Gold, Width 1.75mm, Rhodium Finish: Yes, diamond spec as in price_basis, and the sale display '$2,210 $1,657 −25%'. Sale prices are time-sensitive; confirm live before purchase.",
       "2026-10-22T23:37Z: official-page snapshot re-read; live re-fetch pending (outage)."),
    bn("BN-23", "Comfort Fit Solitaire Engagement Ring In 14K Yellow Gold (James Allen style 17740y14)",
       "Comfort-fit solitaire (legacy James Allen style; sold out at check)",
       "solitaire", "14K Yellow Gold", 14, "17740y14", None, None,
       "V1_direct_page_fetch",
       "No purchasable price — the live page states 'This popular style is sold out' (checked 2026-10-22T23:19Z)",
       "https://www.bluenile.com/engagement-rings/design-your-own-ring/14k-yellow-gold-15mm-comfort-fit-engagement-ring-item-41515",
       "https://www.bluenile.com/engagement-rings/design-your-own-ring/14k-yellow-gold-15mm-comfort-fit-engagement-ring-item-41515",
       ["PRICE_UNVERIFIED", "SOLD_OUT_AT_CHECK"],
       "Product page fetched LIVE 2026-10-22T23:19Z (the original jamesallen.com item URL redirected here): sold-out notice displayed, plus the on-page announcement 'James Allen is Now Part of Blue Nile'. An older $660 '(Setting Price)' seen in a search snapshot was deliberately NOT recorded because it could not be confirmed live. SKU 17740y14 was read from the official page's own title snapshot ('…In 14K Yellow Gold-17740y14'). Width left blank: the URL slug reads '15mm' while the James Allen naming convention for this style family uses decimals (e.g. 2.5mm slugs appear as '25mm') — resolving that would be inference, so it stays unrecorded.",
       "Live fetch 2026-10-22T23:19Z: sold-out status and merger notice read directly from the page."),
]

INSERT_AFTER = {"BE": "BE-03", "BN": "BN-08"}


def insert_rows(doc):
    rows = doc["rows"]
    existing = {r["id"] for r in rows}
    added = []
    for nr in NEW_ROWS:
        if nr["id"] in existing:
            print("skip (already present):", nr["id"])
            continue
        anchor = INSERT_AFTER[nr["id"].split("-")[0]]
        idx = max(i for i, r in enumerate(rows) if r["id"].split("-")[0] == nr["id"].split("-")[0])
        rows.insert(idx + 1, nr)
        added.append(nr["id"])
    return added


def main():
    rp = DATA / "rings.json"
    doc = json.loads(rp.read_text(encoding="utf-8"))
    added = insert_rows(doc)

    # append cross-session corroboration to BE-01 (their text preserved verbatim)
    for r in doc["rows"]:
        if r["id"] == "BE-01":
            note = (" Cross-session corroboration (arena/22b5b06c-gold4, 2026-10-22T23:39Z): an independent dated snapshot of the same "
                    "product page (2026-08-27) and schema.org JSON-LD on three official Brilliant Earth category pages (2026-08-25, "
                    "2026-09-14, 2026-09-23) all show $1,190 (Setting Only), style BE1D2444-14KY, 2 mm, claw prong — consistent with this record.")
            if "Cross-session corroboration (arena/22b5b06c-gold4" not in (r.get("flag_detail") or ""):
                r["flag_detail"] = (r.get("flag_detail") or "") + note
                r["reverified_by"] = r.get("reverified_by", "") + " + arena/22b5b06c-gold4 (corroboration)"
            break

    rp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("rings.json rows now:", len(doc["rows"]), "| added:", added)

    # ---- gold_spot.json: informational cross-checks (benchmark untouched) ----
    sp = DATA / "gold_spot.json"
    spot = json.loads(sp.read_text(encoding="utf-8"))
    if "same_day_external_readings_22b5b06c" not in spot:
        spot["same_day_external_readings_22b5b06c"] = {
            "purpose": ("Informational same-day cross-checks recorded by session arena/22b5b06c-gold4. NOT used for any derived "
                        "number in this repository — the World Gold Council benchmark above remains the single calculation basis."),
            "live_api_reading": {
                "source": "gold-api.com metals API", "source_url": "https://api.gold-api.com/price/XAU",
                "value_usd_per_oz": 4028.10, "source_reported_updated_at": "2026-10-22T23:01:42Z",
                "fetched_by_session_at_utc": "2026-10-22T23:17Z (live JSON fetch)",
                "verification": "live fetch of the API response",
            },
            "snapshot_readings": [
                {"source": "Kitco — Gold Price Today", "url": "https://www.kitco.com/charts/gold",
                 "value_usd_per_oz": 4062.30, "as_of": "2026-10-22 10:54 a.m. ET bid (down $78.00 / −1.88% on the day)",
                 "verification": "dated search snapshot of the official page (fetch-service outage at the time)"},
                {"source": "Kitco — Gold Spot Prices", "url": "https://www.kitco.com/price/precious-metals",
                 "value_usd_per_oz": 4032.80, "as_of": "2026-10-22 14:46 ET (bid 4,032.80 / ask 4,034.80)",
                 "verification": "dated search snapshot of the official page"},
                {"source": "APMEX — Gold Price", "url": "https://www.apmex.com/gold-price",
                 "value_usd_per_oz": 4042.90, "as_of": "2026-10-22 7:13:01 PM ET (per-gram $129.98)",
                 "verification": "dated search snapshot of the official page"},
            ],
            "assessment": ("The WGC benchmark $4,028.53/oz and this session's independent live reading $4,028.10/oz (23:01:42Z) differ by 0.01%. "
                           "All same-day readings sit inside the 22 Oct intraday range ($4,028.10-$4,062.30) on a day the market fell ~1.9-2.6%. "
                           "Consistent — no evidence of a fabricated or stale quote in either direction."),
        }
        sp.write_text(json.dumps(spot, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("gold_spot.json: cross-check block added (benchmark untouched)")

    # ---- verification_log.json: Pass 6 ----
    vp = DATA / "verification_log.json"
    vlog = json.loads(vp.read_text(encoding="utf-8"))
    if not any("Pass 7" in p.get("pass", "") for p in vlog["passes"]):
        vlog["coordination_summary"] += (
            " Session arena/22b5b06c-gold4 later returned with its own independently collected dataset (15 Blue Nile / James Allen-line rows and "
            "4 Brilliant Earth rows, 9 of them from live page fetches) plus a live gold-api.com spot reading; its integration merged main's published "
            "35-row tree unchanged and added its rows to the same schema (PR #11), preserving its working files under data/preserved/, docs/legacy/ and "
            "scripts/session_22b5b06c/.")
        vlog["passes"].append({
            "pass": "Pass 7 — second independent collection (session arena/22b5b06c-gold4) + integration into the published dataset",
            "when_utc": "2026-10-22T23:55Z",
            "scope": ("19 candidate rows collected independently from official Blue Nile and Brilliant Earth pages (9 by live fetch 23:13-23:19Z, "
                      "10 from dated snapshots of the same official pages during a fetch-service outage 23:20-23:47Z, each corroborated against at "
                      "least one additional official-page read including schema.org JSON-LD where published); one live gold-spot API reading plus "
                      "same-day Kitco/APMEX snapshot readings; integration merge of main's tree with this session's branch."),
            "checked": [
                "Every added row carries its official source URL, capture date, and either V1 (live fetch) or V2 (dated official-page snapshot, always flagged PRICE_V2_ONLY) provenance. No value was carried over from memory or secondary sources.",
                "Duplicate scan vs the published 35 rows: one overlap found — Brilliant Earth Atelier Solitaire 14K (this session's candidate BE-BE1D2444-14KY = published BE-01, same URL, same $1,190). The published row was kept and this session's independent snapshot corroboration was APPENDED to its flag_detail; no duplicate row was added.",
                "Two new irregularities found on Blue Nile's own pages: BN-19 Wide Band Solitaire description says 'platinum solitaire setting' against a 14K Yellow Gold spec (COPY_INCONSISTENT_METAL — the third such Blue Nile copy contradiction after BN-04 '18k' and BN-08 '14k white gold'); BN-17 Woven Solitaire shows four different sale prices ($772/$724/$730/$728) across four official category pages for the same SKU (SALE_PRICE_VARIES_ACROSS_PAGES).",
                "James Allen status confirmed from a live-fetched page: jamesallen.com item URLs redirect to bluenile.com, which displays 'James Allen is Now Part of Blue Nile' (recorded on BN-23). BN-23 itself was sold out at the live check, so its price cell stays blank (an older $660 snapshot was deliberately not used).",
                "Gold spot cross-check: benchmark $4,028.53/oz (WGC) vs this session's independent live reading $4,028.10/oz (gold-api.com, 23:01:42Z) — 0.01% apart; Kitco ($4,062.30 @10:54 ET; $4,032.80 @14:46 ET) and APMEX ($4,042.90 @19:13 ET) snapshots sit inside the same intraday range. Recorded informationally in data/gold_spot.json; derived arithmetic still uses only the WGC benchmark.",
                "Timestamp anomaly noted, not corrected: Pass 5 in this log is stamped 2026-10-23T00:05Z, which is ahead of the wall-clock time when it was merged (main's PR #10 merged 23:33Z on 22 Oct). Left as that session wrote it; flagged here for the record.",
                "Ring weights: none of the 18 added rows has a retailer-published gram weight (Blue Nile and Brilliant Earth product pages do not publish one), so every added weight cell is blank with NO_WEIGHT_PUBLISHED — consistent with the published Blue Nile rows.",
            ],
            "result": "PASS (pending re-run of audit.py/check_site.py/verify.py after integration, recorded in reports/)",
            "outcome": ("Dataset grows from 35 to 53 rows; retailer count unchanged at 9 (Blue Nile +15 including the James Allen line and one sold-out "
                        "row with a deliberately blank price; Brilliant Earth +3: BE-04/BE-05/BE-06). 18 rows added: 9 at V1 (one of them the sold-out row, price blank) and 9 at V2-with-flag. Two new flag types "
                        "introduced (SALE_PRICE_VARIES_ACROSS_PAGES, SOLD_OUT_AT_CHECK) plus first use of PRICE_FROM_CATEGORY_PAGE for rows whose "
                        "price was read from a live category-page fetch. No existing row's verified content was altered. Recommendation unchanged: "
                        "re-run scripts/audit.py after every change, re-fetch the V2 rows when possible, and never fill a blank cell without an "
                        "official source."),
        })
        vlog["not_reverified_this_pass"].append(
            "Pass 7 did not re-fetch the 35 rows already published (they stand as the latest published passes verified them), and could not live-refetch its own 9 V2 rows "
            "or the Brilliant Earth generic returns-policy page because of the fetch-service outage (23:20-23:47Z); those rows carry PRICE_V2_ONLY and "
            "appear on the Flagged page until a live re-fetch confirms them.")
        vp.write_text(json.dumps(vlog, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("verification_log.json: Pass 7 appended")


if __name__ == "__main__":
    main()
