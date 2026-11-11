# Pass 21 — session `arena/91415e29-gold4`

**Date:** 2026-11-11, evidence window ~07:59Z · **Branch:** `arena/91415e29-gold4`
**Evidence:** [`observations.json`](observations.json) (machine-readable) · [`gates.txt`](gates.txt) / [`gates.json`](gates.json) (gate output)

> **No hallucinations.** Every value on this pass's page is either read from the official page linked beside
> it, or computed by `scripts/compute.py` from published inputs, or left blank. Where a page printed a
> different number from the stored one, both numbers are published and nothing was overwritten.

---

## 1. What this pass did before touching a file

1. Read the whole board (`COORDINATION.md`, all prior pass records), every remote branch head and the open-PR
   list: **no other branch and no open PR exists**, so no live claim overlaps this scope. This is a fresh
   pass, not a takeover; no stale claim was found.
2. Re-ran **all nine gates (twelve invocations)** on `main@b34ae17` before claiming: all green.
3. Wrote the claim to `COORDINATION.md` and pushed it **before** editing any file in scope (`dd1dad8`).

**Branch note.** Arena pins this session to `arena/91415e29-gold4`; the board's `session-<id>/<task>`
convention cannot be followed here. No other branch was created, modified or force-pushed.

## 2. Read paths available in this sandbox — stated, not assumed

| Path | Available? | What it was used for |
|---|---|---|
| Shell + internet to retailer sites | **No** — only GitHub, npm and PyPI hosts are reachable | nothing |
| GitHub Actions (`workflow_dispatch`) | not used this pass | nothing |
| This session's browser-rendered page reader | **Yes** | all 5 reads below |

Consequence, said plainly: **no runner sweep was run this pass.** Passes 15–18's runner evidence remains the
most recent all-URL sweep (`2026-10-23T20:23:21Z`, 18 days old) and is left exactly as it was. This pass is
a **freshness spot-check** (5 reads), not a full sweep.

## 3. Readings (5 pages, all official)

| Ref | Target | Verdict | Stored | Page printed |
|---|---|---|---|---|
| R01 | gold benchmark (WGC) | **differs, material (+1.58%)** | $3,996.31/oz, "Data as of 22 October, 2026" | **$4,059.49/oz**, "Data as of 10 November, 2026" |
| R02 | AL-01 (Allurez) | **match** | $585 · 3.58 g · NG4426 | `$585`, `Approximate Metal Weight 3.58 grams`, `Setting only`, `NG4426`, 14k yellow |
| R03 | FTC guidance | **match** | karat + trademark; solid vs plated/filled/vermeil | confirmed verbatim on the live page |
| R04 | 15 U.S.C. § 295 | **match** | 0.003 + 0.007 concurrent tests | confirmed verbatim on the live page |
| R05 | live site | **match** | 64 / 62 / 17 / 251 / $128.48/g | live dashboard serves exactly these |

**Coverage:** 1 of 64 product rows touched and fully corroborated (price + weight). **59 rows were not
re-read this pass** and keep their 2026-10-22/23 capture dates. The site says this; it is not implied
anywhere that a full sweep happened.

## 4. Findings (published, not "fixed" by overwriting)

| ID | Severity | Finding | Action |
|---|---|---|---|
| F21-01 | info | Gold panel prints $4,059.49 vs stored $3,996.31 (+1.58% over 18 days; source data date advanced to 10 Nov) | benchmark **retained**; reading recorded additively in `data/gold_spot.json` (`pass21_live_crosscheck_2026_11_11`); no derived value changed |
| F21-02 | info | AL-01 corroborated exactly for the **fourth** time (Passes 2, 12, 14/15, 20, now 21) | no value changed; corroboration recorded here |
| F21-03 | info | Freshness evidence is 18 days old (Gate 7 warning) | stated on this page and in the board; no new runner sweep was run, so no new per-URL/current-quote claim is made |
| F21-04 | info | No documentation drift found: 64 / 62 / 17 / 251 / $3,996.31 / $128.48435 / 32 sources / nine gates all match `data/*.json` | nothing to fix |

## 5. Security / anti-hallucination checks (all nine gates, after the edits)

| Gate | Result |
|---|---|
| 1 `audit.py` — dataset integrity, allow-list, recompute of every derived number | PASS 132 checks, 0 warnings, 0 failures |
| 2 `check_site.py` — links, per-row source link, no-hallucination banner | PASS, 30 pages |
| 3 `verify.py` — schema + blank-value accounting | PASS, 64 records, 0 hard failures |
| 4 `verify_a0be79d4.py` — XSS/404/Assay Lab scanner | PASS, 40 pages, 2,656 links, 0 dead |
| 5 `audit_hallucinations.py` — hallucination auditor | PASS, 1,183 checks, 0 failures |
| 6a/6b `verify_citations.py` — CFR citation integrity | PASS, 110 refs, 0 violations (+self-test) |
| 7 `audit_freshness.py` — source-health evidence | PASS, 295 checks, 4 known warnings (18-day age + 3× BE 403), 0 failures |
| 8 `test_assurance.py` — currency/blank-price register | PASS, 8/8 |
| 9 readiness + calculator runtime + readiness-check | PASS, 22 + 10 + check |

**The standing recommendation stands: after every review, look for hallucinations again — source link,
date, read path, and whether anything was inferred.**
