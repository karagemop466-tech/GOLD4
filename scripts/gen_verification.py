#!/usr/bin/env python3
"""Generate VERIFICATION.md — the line-by-line verification record.

The file is generated from the same JSON the site uses, so the document and the
published tables can never drift apart.
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(name: str) -> dict:
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def money(v) -> str:
    if v is None:
        return "**blank**"
    return f"${float(v):,.2f}" if abs(float(v) - round(float(v))) > 0.004 else f"${float(v):,.0f}"


def num(v, dec=2) -> str:
    return "**blank**" if v is None else f"{float(v):,.{dec}f}"


def main() -> None:
    d = load("derived.json")
    sellers_doc = load("sellers.json")
    sources_doc = load("sources.json")
    spot = load("gold_spot.json")
    audit = (ROOT / "reports" / "audit_latest.txt").read_text(encoding="utf-8") if (ROOT / "reports" / "audit_latest.txt").exists() else "not run"

    rows = d["rows"]
    st = d["stats"]
    usd_oz = d["spot"]["value_usd_per_oz"]
    usd_g = d["spot"]["usd_per_gram"]

    out: list[str] = []
    out.append("# VERIFICATION.md — line-by-line verification record\n")
    out.append(f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} from `data/*.json` by `scripts/gen_verification.py`.\n")
    out.append("## Rule applied to every single value\n")
    out.append("> **No hallucination.** A populated value requires direct evidence from the official page linked in the same row (verification level **V1**). If a current value cannot be confirmed, its structured cell is **blank** and flagged `PRICE_UNVERIFIED` / `NO_WEIGHT_PUBLISHED` / "
               "`WEIGHT_UNVERIFIED` on the Flagged for Review page. Historical snapshot-only observations may remain in review notes, never in a current value cell. Nothing is estimated, inferred from photos, or copied from a blog, marketplace, resale listing or "
               "price-comparison site. Derived values (gold grams, gold value, price ÷ gold) are arithmetic on published inputs and are re-computed independently by `scripts/audit.py` "
               "on every pass.\n")
    out.append(f"**Benchmark:** gold spot **${usd_oz:,.2f}/oz** as shown on the World Gold Council page for **{d['spot']['price_date']}** (retrieved {d['spot']['captured_utc']}) "
               f"= **${usd_g:,.4f}/g**. Benchmark source: {d['spot']['source_url']}\n")
    out.append("\n## Coverage summary\n")
    out.append(f"- Rows: **{st['total_rows']}**")
    out.append(f"- Populated prices with V1 direct official-page evidence: **{st['rows_with_verified_price']}**")
    out.append(f"- Prices deliberately blank / unverified: **{st['total_rows'] - st['rows_with_stored_price']}**")
    out.append(f"- Gram weights published by the seller: **{st['rows_with_published_weight']}** (therefore only these rows have a computable gold value)")
    out.append(f"- Rows with explicit *solid gold* wording: **{st['rows_with_solid_gold_statement']}**")
    out.append(f"- Rows publishing a hallmark or maker's mark: **{st['rows_with_hallmark_published']}** (the legal requirement is quoted in `data/methodology.json`)")
    out.append(f"- Rows carrying at least one flag: **{st['rows_with_any_flag']}**\n")

    out.append("## Line-by-line verification — every row\n")
    out.append("| ID | Retailer | Ring | Karat | Price | Price source (fetched) | Weight | Weight source (fetched) | Gold value (derived) | Solid wording | Hallmark | Flags |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        sold = f"stated: “{r['solid_gold_statement']}”" if r.get("solid_gold_statement") else "not stated"
        out.append(
            "| {id} | {ret} | [{name}]({url}) | {k}K | {price} | {psrc} | {w} | {wsrc} | {gv} | {solid} | not published | {flags} |".format(
                id=r["id"], ret=r["retailer"], name=r["product_name"].replace("|", "/"), url=r["url"], k=r["karat"],
                price=money(r["price_usd"]),
                psrc=("V1 · " + r["price_captured_utc"]) if r["price_verification"] == "V1_direct_page_fetch" else "**UNVERIFIED — current value must be blank**",
                w=(num(r["weight_g"]) + " g") if r["weight_g"] else "**blank**",
                wsrc=("V1" if r["weight_verification"] == "V1_direct_page_fetch" else "**not verified**") if r["weight_g"] else "—",
                gv=money(r["gold_value_usd"]) if r["gold_value_usd"] else "—",
                solid=sold, flags=", ".join(r["flags"]) or "—",
            )
        )

    out.append("\n## Derived arithmetic (re-computed and cross-checked by the audit)\n")
    out.append("| ID | Weight (g) | Fineness | Pure gold (g) | Spot $/g | Gold value | Legal-min value (stamp − 0.007) | Price | Price ÷ gold |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r["weight_g"] is None:
            continue
        out.append(f"| {r['id']} | {r['weight_g']:.2f} | {r['fineness']:.4f} | {r['pure_gold_g']:.3f} | ${usd_g:,.4f} | {money(r['gold_value_usd'])} | "
                   f"{money(r['legal_min_gold_value_usd'])} | {money(r['price_usd'])} | {num(r['price_to_gold_multiple'])}× |")

    out.append("\n## Karat pairs (same design, both karats sold by the same retailer)\n")
    out.append("| Pair | Retailer | Design | 14K → 18K price | Price gap | Gold-content gap | Multiple 14K → 18K |")
    out.append("|---|---|---|---|---|---|---|")
    for p in sorted(d["pairs"], key=lambda x: x["pair_id"]):
        low = next((r for r in rows if r["id"] == p["low_id"]), None)
        high = next((r for r in rows if r["id"] == p["high_id"]), None)
        gold_gap = f"+{p['gold_gap_pct']:.1f}%" if p["gold_gap_pct"] is not None else "**not computable** (no published weights)"
        out.append(f"| {p['pair_id']} | {p['retailer']} | [{p['design']}]({low['url']}) ([{p['low_id']}]({low['url']}), [{p['high_id']}]({high['url']})) | "
                   f"{money(p['low_price'])} → {money(p['high_price'])} | {'+' if p['price_gap_pct'] and p['price_gap_pct']>0 else ''}{num(p['price_gap_pct'],1)}% | {gold_gap} | "
                   f"{num(p['low_multiple'])}× → {num(p['high_multiple'])}× |")

    out.append("\n## Seller-level claims and the page that proves each one\n")
    out.append("| Seller | Return window | Contact captured | Resized rings returnable | Custom / engraved | Resize service | Warranty | Solid wording | Policy source |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    src_by_id = {s["id"]: s for s in sources_doc["sources"]}
    for s in sellers_doc["sellers"]:
        src = src_by_id.get(s["returns_source_id"], {})
        resized = "no" if any(("resized" in x.lower() or "altered" in x.lower()) for x in s["return_exclusions"]) else "not excluded"
        custom = "excluded" if any(("custom" in x.lower() or "engrav" in x.lower()) for x in s["return_exclusions"]) else "no exclusion captured"
        contact = s["contact"].get("phone") or s["contact"].get("email") or "**not captured**"
        out.append(f"| {s['name']} | {s['return_window_days']} days | {contact} | {resized} | {custom} | {s.get('resize_policy') or '**not captured**'} | "
                   f"{(s.get('warranty') or '**not captured**')[:90]} | {'stated' if s.get('solid_gold_stated') else 'not stated'} | [{src.get('title','policy')}]({src.get('url','#')}) |")

    out.append("\n## Source registry\n")
    out.append("| ID | Tier | Publisher | Document | Retrieved |")
    out.append("|---|---|---|---|---|")
    for s in sources_doc["sources"]:
        out.append(f"| {s['id']} | {s['tier']} | {s['publisher']} | [{s['title']}]({s['url']}) | {s['retrieved_utc']} |")

    blank_price_ids = [r["id"] for r in rows if r.get("price_usd") is None]
    contact_gaps = []
    for seller in sellers_doc["sellers"]:
        missing = [field for field in ("phone", "email") if not seller.get("contact", {}).get(field)]
        if missing:
            contact_gaps.append(f"{seller['name']} ({'/'.join(missing)})")
    vr01 = next(r for r in rows if r["id"] == "VR-01")

    out.append("\n## Irregularities flagged for human review\n")
    out.append("1. **Blue Nile copy contradicts its own specification (BN-04).** The 14K Comfort Fit 2.5 mm description says the ring is “crafted in 18k yellow gold” while the specification block says 14K Yellow Gold. "
               f"Page: {next(r['url'] for r in rows if r['id']=='BN-04')}")
    out.append("2. **Blue Nile copy names the wrong metal colour (BN-08).** The Riviera Pavé 14K *yellow* gold page says the diamonds are “set in 14k white gold”. "
               f"Page: {next(r['url'] for r in rows if r['id']=='BN-08')}")
    out.append("3. **Mixed-metal ambiguity (BN-07).** The Classic Four Prong Solitaire is titled 14K Yellow Gold but the description mentions “platinum prongs”; if true, the ring is not all gold and any gold-weight calculation would overstate the gold content. "
               f"Page: {next(r['url'] for r in rows if r['id']=='BN-07')}")
    out.append(f"4. **No hallmark anywhere.** {st['rows_with_hallmark_published']} of {st['total_rows']} rows publish the physical stamp or the maker's mark, so the hallmark requirement can only be checked in hand.")
    out.append("5. **Some weights are approximate or size-specific.** Allurez labels its numbers “Approximate Metal Weight”; VRAI publishes a size-6 metal weight. Neither is a measurement of the exact ring a buyer will receive.")
    out.append(f"6. **Unconfirmed current prices stay blank:** {', '.join(blank_price_ids)}. Historical snapshot or alternate-currency observations may be discussed in their review notes, but they do not populate `price_usd` and are never converted into USD.")
    out.append("7. **Reputation was not verified for any seller.** No independent review or complaints dataset was collected, so no reputation claim is made anywhere on the site.")
    out.append(f"8. **Seller contact gaps.** Fields left blank rather than guessed: {'; '.join(contact_gaps) if contact_gaps else 'none'}.")
    out.append(f"9. **Listing-card and configuration evidence are kept distinct (VR-01).** VRAI's “From {money(vr01['price_usd'])}” listing-level price and its {num(vr01['weight_g'])} g configuration-page weight come from different official URLs; the row is flagged `PRICE_AND_WEIGHT_DIFFERENT_URLS` and the configured structured-price difference remains a review item.")

    out.append("\n## Unverified values published as blank\n")
    for r in rows:
        gaps = []
        if r["price_usd"] is None:
            gaps.append("price")
        if r["weight_g"] is None:
            gaps.append("weight")
        if r["solid_gold_status"] != "stated":
            gaps.append("solid-gold wording")
        if gaps:
            out.append(f"- **{r['id']}** ({r['retailer']} · {r['product_name']}): {', '.join(gaps)} not published on the captured page → {r['url']}")

    out.append("\n## Integrity audit output (hallucination / security check)\n")
    out.append("```\n" + audit.strip() + "\n```\n")
    out.append("Re-run after every review pass:\n")
    out.append("```bash\npython3 scripts/compute.py && python3 scripts/generate_site.py && python3 scripts/build_site.py\npython3 scripts/audit.py && python3 scripts/check_site.py && python3 scripts/verify.py\npython3 scripts/verify_a0be79d4.py && python3 scripts/audit_hallucinations.py\npython3 scripts/session_46691f83/verify_citations.py --self-test\npython3 scripts/session_46691f83/verify_citations.py && python3 scripts/audit_freshness.py\n```\nAlways repeat the hallucination review after every source, data or generator change.\n")

    (ROOT / "VERIFICATION.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote VERIFICATION.md")


if __name__ == "__main__":
    main()
