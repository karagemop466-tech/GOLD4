# Pass 20 — session `arena/bfbdf30c-gold4`

**Date:** 2026-10-23, evidence window 23:43–23:45Z · **Branch:** `arena/bfbdf30c-gold4`
**Evidence:** [`observations.json`](observations.json) (machine-readable) · [`gates.txt`](gates.txt) / [`gates.json`](gates.json) (gate output)

> **No hallucinations.** Every value on this pass's page is either read from the official page linked beside
> it, or computed by `scripts/compute.py` from published inputs, or left blank. Where a page printed a
> different number from the stored one, both numbers are published and nothing was overwritten.

---

## 1. What this pass did before touching a file

1. Read the whole board (`COORDINATION.md`, 18 prior pass records) and every remote branch head.
2. Re-ran **all eight gates (nine invocations)** on `main@a832eed` before claiming: all green.
3. Found one **stale** claim — PR [#47](https://github.com/karagemop466-tech/GOLD4/pull/47)
   (`arena/bc872fef-gold4`, draft), last commit `9c001e1` at **20:43:29Z**, i.e. more than 60 minutes
   before this session started, with no commits since. Under the board's crash/handover rule this session
   **took over the task** and recorded the handover on the board and in the PR thread.
4. Wrote the claim to `COORDINATION.md` and pushed it **before** editing any file in scope (`2769cca`).

**Branch note.** Arena pins this session to `arena/bfbdf30c-gold4`; the board's `session-<id>/<task>`
convention cannot be followed here. No other branch was created, modified or force-pushed.

## 2. Read paths available in this sandbox — stated, not assumed

| Path | Available? | What it was used for |
|---|---|---|
| Shell + internet to retailer sites | **No** — only GitHub, npm and PyPI hosts are reachable; `curl` to the live site fails at TLS | nothing |
| GitHub Actions (`workflow_dispatch`) | **No** — HTTP 403 "Resource not accessible by integration" | nothing |
| GitHub Actions run logs / artifacts | **No** — `results-receiver.actions.githubusercontent.com` is unreachable | nothing |
| This session's browser-rendered page reader | **Yes** | all 14 reads below |

Consequence, said plainly: **no runner evidence was collected by this pass.** No runner result is quoted,
re-used or implied. Passes 15–18's runner evidence remains the most recent all-URL sweep
(`2026-10-23T20:23:21Z`) and is left exactly as it was.

## 3. Readings (14 pages, all official)

| Ref | Row | Verdict | Stored | Page printed |
|---|---|---|---|---|
| R01 | gold benchmark (WGC) | differs, immaterial (−0.021%) | $3,996.31/oz @ 20:23Z | **$3,995.47/oz**, same "Data as of 22 October, 2026" |
| R02 | AL-01 | **match** | $585 · 3.58 g · NG4426 | `$585`, `Approximate Metal Weight 3.58 grams`, `Setting only`, `NG4426`, 14k yellow |
| R03 | SR-03 | **match** | $871 · 6.70 g · 18K | `Now: US$871.00`, `18K Solid Gold`, `6.70 grams` (size-10 approximation stated by the seller) |
| R04 | SR-05 | **match** | $2,858 · 8.00 g · 14K | `Now: US$2,858.00`, `14K Solid Gold`, `8.00 grams`, diamond 0.50 ct H/SI1 natural |
| R05 | RS-02 | **match** | $249 · 0.7 g · 18kt | `$249`, `18kt Yellow Gold`, `Gold Weight 0.7 grams`, sizes 5–10 in stock |
| R06 | RS-05 | **match + new finding** | $2,819 · weight blank | `Sale price $2,819`, `CLEARANCE 29% Off`, 14kt white, 0.80 ct I/VS1, GIA 2225975086, no weight |
| R07 | MJ-01 | variant-conditional | $548 · yellow gold | `$548` on the **white-gold** variant the URL renders; no gram weight |
| R08 | MN-01 | **differs** (−1.57%) | $1,465 | **$1,442** (third independent read) |
| R09 | VR-01 | partial | $1,035 "from" · 2.86 g | `Metal weight: 2.86g (Ring size 6)` with size 5 selected; pavé spec on a plain band |
| R10 | BE-07 | partial | $1,350 | page live, title still `14K Yellow Gold`; price not in returned content |
| R11 | AN-01 | partial | $870.76 · 2.9 g | navigation only (JavaScript shell), no product figures |
| R12 | BN-09 | **dead link confirmed** | $1,125 | "We're sorry, the page you're looking for cannot be found." |
| S01 | Sarraf returns source | source fix adopted | product-page URL | dedicated policy page read in full |
| S02 | Sarraf warranty source | new source | — | Lifetime Guarantee page read in full |

**Coverage:** 11 of 64 product rows touched, of which **5 fully corroborated** (price and, where published,
weight). **53 rows were not re-read this pass** and keep their 2026-10-22 capture dates. The site says this
on the Pass 20 page; it is not implied anywhere that a full sweep happened.

## 4. Findings (published, not "fixed" by overwriting)

| ID | Severity | Finding | Action |
|---|---|---|---|
| F20-01 | info | Gold panel prints $3,995.47 vs stored $3,996.31 on the same source date (−0.021%) | benchmark retained; reading recorded in `data/gold_spot.json` |
| F20-02 | medium | Menē MN-01 prints $1,442 vs stored $1,465 (−1.57%), third independent read | both published; no overwrite; `PRICE_STRUCTURED_DIFFERS` stands |
| F20-03 | medium | Blue Nile BN-09 serves its own 404 copy to a normal browser | `SOURCE_URL_DEAD` stands; no URL guessed |
| F20-04 | medium | RS-05 is priced as **clearance** ($3,995 → $2,819) while Ross-Simons excludes "Final sale items" from returns and the page never says *final sale* | new flag `CLEARANCE_RETURN_TERMS_UNCLEAR`; price/date untouched |
| F20-05 | low | Mejuri MJ-01's stored URL renders a different metal variant (white gold) from the stored metal (yellow gold) | `PRICE_VARIANT_DEPENDENT` confirmed accurate; yellow-gold price unconfirmed |
| F20-06 | low | Compare-at price anchors are flagged inconsistently: Allurez shows `$1,194 Everyone Else` (2.04×) and "up to 55% below retail" without `SALE_MSRP_ANCHOR` | published; not patched, because adding flags to rows not re-read would assert unverified facts |
| F20-07 | low | README drift: "Seven CI gates" (pipeline runs eight / nine invocations); a Pass 15 section introduced as "latest" | corrected in this pass |
| F20-08 | info | Stale PR #47's one still-valuable fix (cite Sarraf's dedicated policy pages) re-verified and adopted | `sarraf-returns` URL corrected with `url_history`; `sarraf-warranty` registered → 32 sources |

## 5. Security / anti-hallucination checks (all nine invocations, after the edits)

| Gate | Result |
|---|---|
| 1 `audit.py` — dataset integrity, allow-list, recompute of every derived number | PASS 132 checks, 1 warning (BE-05 V2-only), 0 failures |
| 2 `check_site.py` — links, per-row source link, no-hallucination banner | PASS, 29 pages |
| 3 `verify.py` — schema + blank-value accounting | PASS, 64 records, 0 hard failures |
| 4 `verify_a0be79d4.py` — XSS / 404 blocklist / Assay Lab scan | PASS, 0 dead, 0 unsafe URIs |
| 5 `audit_hallucinations.py` — phantom math, unsourced values | PASS, 0 failures |
| 6a citation self-test | PASS — a known-wrong CFR citation is rejected |
| 6b citation integrity | PASS — 110 CFR references, 0 rule violations |
| 7 `audit_freshness.py` — evidence present, recent, applied to every row | PASS — 295 checks, 2 warnings (BE-06/BE-07, unchanged), 0 failures |
| 8 `test_assurance.py` — conservative currency parsing, blank current-price register | PASS, 8/8 |

Gate 1's single warning and Gate 7's two warnings are pre-existing and published on the Flagged page.

## 6. What this pass changed

- `COORDINATION.md` — claim, handover of the stale PR #47 task, results, PR/merge record.
- `README.md` — Pass 20 record; gate count corrected to eight (nine invocations) with Gate 8 listed;
  source count 32; "Latest pass — Pass 15" re-labelled as the historical record it is; benchmark
  limitation now records the fourth same-day read and the retention policy.
- `data/rings.json` — **additive only**: RS-05 gains `CLEARANCE_RETURN_TERMS_UNCLEAR` and a
  `pass20_observation` note. No price, weight, karat, SKU, URL or date changed.
- `data/gold_spot.json` — **additive only**: `pass20_live_crosscheck_2026_10_23`.
- `data/sources.json` — `sarraf-returns` now cites the policy page (old URL kept in `url_history`),
  new `sarraf-warranty` source → 32 registered sources.
- `scripts/build_pass20.py`, `scripts/run_gates_pass20.py` (new); `scripts/build_site.py` (nav entry and
  a flag label for the new flag).
- Generated: `index.html`, `pages/**` (incl. new `pages/pass20.html`), `reviews/index20.html`,
  `reviews/pass20/{observations.json,gates.json,gates.txt}`.

## 7. What a human should still do

1. **Treat every price as a dated reading.** 53 rows were not re-read in this pass.
2. **Before paying for RS-05**, get the return terms for a clearance item in writing (F20-04).
3. **For MJ-01**, select the yellow-gold variant and confirm the price in the cart (F20-05).
4. **After delivery**, take the ring to an independent jeweller for XRF purity testing *and* a gram-weight
   check, before resizing. A stamp is a claim; XRF is the check.
5. **Next review pass: look for hallucinations again** — source link, read date, read path, and whether
   anything was inferred.
