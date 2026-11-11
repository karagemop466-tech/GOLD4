# Pass 21 companion — seller-policy & legal-source assurance, plus an independent derivation audit

**Session:** `arena/91e9aba0-gold4` · **Branch:** `arena/91e9aba0-gold4` · **Task ids:** 58–61 on the board
**Read window:** 2026-11-11, 08:05–08:40 UTC (sandbox clock checked; `date -u` = 2026-11-11)
**Read path:** this session's own browser-rendered page reader. The shell in this sandbox reaches only `github.com`
(verified: `https://www.gold.org/` fails at TLS from `bash`), so nothing below was read by a runner, and no runner
artifact was available to read either (`gh run download` on a completed sweep fails on the blocked
`*.blob.core.windows.net` host — the same limitation every earlier pass recorded).

**Why this slice and not the product rows.** A concurrent session (`arena/4fe4a9c3-gold4`) claimed Pass 21 at
2026-11-11T08:00Z and its verification run is live. Its scope is the gold benchmark and the 64 ring product URLs,
then integration and publish. This session therefore **did not touch** the product rows, `data/**`, the generators,
the site or the README. It re-checked the layer nobody has re-read since 22–23 October: **the ten sellers' own
return, resize, warranty and contact terms (`data/sellers.json`)**, **the two legal sources the whole methodology
rests on**, and **the arithmetic** — with an independent implementation.

---

## 1. The headline numbers

| Question | Answer | Where it came from |
|---|---|---|
| Sellers re-read from their own pages today | **10 of 10** (+ Sarraf's separate Lifetime Guarantee page = 11 policy pages) | §2 below, each with its URL |
| Stored seller claims confirmed unchanged | **26** | §2 |
| Claims that now differ or are understated | **4** (Anjolee exclusions, Sarraf warranty wording, Menē refund structure, Catbird resize wording) | F-A21-04, -05, -07, -08 |
| Seller page defects found (not our data) | **1** (Sarraf's holiday-return paragraph runs 3 Nov 2026 → 15 Dec **2025**) | F-A21-06 |
| New consumer-relevant facts the dataset does not carry | **19** (5 of them extended holiday return windows) | §2, "new facts" |
| Legal sources re-read | **2 of 9 tier-A** (FTC gold-jewellery guidance, 15 U.S.C. § 295) | §3 |
| Independent arithmetic comparisons | **644 → 0 mismatches, 1 rounding note** | §4, `derive-audit.txt` |
| Stored values changed by this session | **0** | by design; requests are logged, not applied |

The gold benchmark used by every derived figure is **still the 23 October reading** (`USD 3,996.31/oz`). Read today,
the same official panel prints **`USD 4,059.49/oz`** with the page's own line *"Data as of 10 November, 2026"*
([World Gold Council Goldhub](https://www.gold.org/goldhub/data/gold-prices), read 2026-11-11T08:03Z). That is
**+1.58%**, and it is recorded here as an observation only — applying it is the Pass 21 owner's documented step, not
this session's, because every derived number on the site must be recomputed in the same commit that moves the
benchmark.

---

## 2. Seller-policy layer, line by line

Each row is one stored fact compared with the seller's own page, read today. "Confirmed" means the page prints it;
"differs" means the page prints something else and **both readings stay published**; nothing was overwritten.

| Seller | Stored fact | Result today | Exact wording read on 2026-11-11 |
|---|---|---|---|
| [Blue Nile](https://www.bluenile.com/policies/returns) | 30 days from shipment | **Confirmed** | "you may return eligible items in their original, unworn condition within 30 days from the shipment date" |
| Blue Nile | 7 exclusions incl. Final Sale + Personalized gemstones | **Confirmed** | "Personalized jewelry, custom orders, engraved items, items resized after initial purchase, Diamond Upgrade Program purchases, clearance items and 'Final Sale' items are not eligible"; "Personalized gemstones collection & clearance items are not eligible for return" |
| Blue Nile | 2 complimentary returns per customer per year; RMA required | **Confirmed** | "Two complimentary returns are allowed per customer, per year. A Return Merchandise Authorization (RMA) number is required" |
| Blue Nile | USD 150 missing grading report fee | **Confirmed** | "The cost to replace a missing diamond grading report is $150" |
| Blue Nile | One free resize ±2 sizes within 6 months; eternity/tension/alternative-metal exclusions | **Confirmed** | verbatim match |
| Blue Nile | Contact +1-800-242-2728 / service@bluenile.com | **Confirmed** | printed in the page header |
| Blue Nile | Lifetime warranty on gold/platinum ≥ USD 1,000 | **Not on this page** — neither confirmed nor contradicted | — |
| [Allurez](https://www.allurez.com/pages/return-policy) | Return must *arrive* within 30 days of original shipment | **Confirmed** | "Your return must arrive at our office within 30 days of the original shipment." |
| Allurez | 9 exclusions (engraved, custom, Design Your Own, contoured bands, clearance, appraisals, gift cards, layaway, resized/altered) | **Confirmed** | all nine printed |
| Allurez | Buyer pays return shipping; RMA required | **Confirmed** | "You are responsible for return shipping costs"; "Returns cannot be accepted without an RMA number" |
| Allurez | USD 300 missing-document fee | **Confirmed, narrower** | "A deduction of $300 per missing **certificate** applies to your refund" — it is the diamond certificate, not any document |
| [VRAI](https://www.vrai.com/returns-exchanges) | 30 days; < USD 15,000 refund-minus-recycling-fee or store credit; > USD 15,000 store credit only | **Confirmed** | verbatim match (page "Last revised on November 2, 2026") |
| VRAI | 6 exclusions | **Confirmed** | all six in the NON-ELIGIBLE list |
| VRAI | One free resize up to one US size; infinity/eternity not resizable | **Confirmed** | "one complimentary resize up to one full US size … must be returned and repurchased" |
| VRAI | Free US return shipping; 14 business days to refund | **Confirmed** | verbatim match |
| VRAI | Lifetime warranty / annual shine | **Not on this page** | returns page links a Lifetime Diamond *Upgrade* instead |
| [Mejuri](https://mejuri.com/company/returns-terms) | Free 30-day returns US/CA/UK/AU/DE from delivery or pickup | **Confirmed** | verbatim match |
| Mejuri | Engraved/monogrammed never returnable | **Confirmed** | "not eligible for return or refund at any time" |
| Mejuri | Final sale, gift cards, piercing earrings, lab-grown without SCS certificate | **Confirmed** | all four printed |
| Mejuri | EU USD 20 / RoW USD 30 fee; no online exchanges; 30-day in-store exchanges | **Confirmed** | fee table + both exchange sentences |
| [Brilliant Earth](https://www.brilliantearth.com/30-Day-Returns/) | 30-day window (previously carried from the 22 Oct capture because a later re-read showed only a badge) | **Confirmed on the page itself** | page headline "Free Extended Holiday Returns & 1-Year Resizes"; "we have extended our 30-day money back guarantee" |
| Brilliant Earth | Non-returnable list (custom, altered, resized, repaired, exchanged, Diamond Upgrade) | **Confirmed** | all seven under "What products aren't eligible for return?" |
| Brilliant Earth | Engraved rings returnable, USD 40 removal fee | **Confirmed** | "we charge $40 to remove the custom engraving" |
| Brilliant Earth | The recorded conflict: badge "Free 1-Year Resizing" vs an earlier "one complimentary resize within 60 days" | **Resolved — two rules, not a contradiction** | "one complimentary resizing within 60 days regardless of sizing range, **or** up to 1 year if within sizing range" |
| [Anjolee](https://www.anjolee.com/information/ReturnPolicy) | 30 days from receipt | **Confirmed** | "any item in its original condition within 30 days of receipt" |
| Anjolee | "All customized orders can be returned for full refund within 30 days of receipt" | **Confirmed** | identical sentence on the dedicated policy page |
| Anjolee | `return_exclusions: []` | **Differs — understated** | "If an item has been worn or is not in its original condition, a **15% restocking fee** will apply"; "A Package without a Return Authorization number will not be accepted" |
| Anjolee | `resize: "Not captured on the page"` | **Now captured** | "Ring Size Adjustments … We will make the necessary adjustments and send the ring back to you - free of charge." |
| [Sarraf](https://www.sarraf.com/30-day-returns-and-exchange-policy/) | 30 days from receipt; insured return to Los Angeles address | **Confirmed** | window, full address and insured-signature requirement printed |
| Sarraf | Worn/altered/third-party-resized/special-order items not returnable | **Confirmed** | "cannot be accepted for return" |
| Sarraf | USD 25 engraving fee non-refundable | **Confirmed** | "the $25.00 engraving fee or $50.00 finish charges are non-refundable" |
| [Sarraf Lifetime Guarantee](https://www.sarraf.com/lifetime-guarantee/) | Fee = greater of USD 100 or 10% of the **purchase** price | **Differs in wording** | "a Shipping and handling fee of $100.00 or 10% of the **current price**, whichever amount is greater" |
| Sarraf Lifetime Guarantee | Invoice required; third-party alteration voids; stones/wear excluded; wholesale excluded | **Confirmed** | conditions 2–7 |
| [Catbird](https://www.catbirdnyc.com/returns) | 20 days from delivery; USD 9 deducted | **Confirmed** | verbatim match |
| Catbird | Engraved/special/custom/international final sale | **Confirmed, plus more** | "Special orders, engraved items, Forever jewelry, earrings from piercing events, home & beauty items, and comestibles are final sale"; "All international sales are final." |
| Catbird | Domestic-shipment window | **Confirmed** | section heading "(Domestic Shipments only)" |
| Catbird | `resize: "Must inspect unengraved before return window closes (20 days)"` | **Imprecise in the dataset** | page describes a repairs/resizing service for Catbird-bought items, cost quoted after receipt, and exchanges done by return + new order |
| [Menē](https://mene.com/customer-care/en-US/articles/returns-319505) | 7-day return window from receipt | **Confirmed** | "you may return it for merchandise credit (Menē Credit) within seven (7) days of receipt" |
| Menē | Certificate of Authenticity must accompany the return | **Confirmed** | "return your jewelry and Certificate(s) of Authenticity" |
| Menē | `contact: null` | **Blank in dataset, published by seller** | "+1 833 636 3245" (Mon–Fri 9am–6pm ET) and "service@mene.com" |

**New facts the dataset does not carry (19).** Extended holiday return windows, all read today:

| Seller | Holiday window as printed |
|---|---|
| Blue Nile | Orders **1 Nov – 5 Dec 2026** returnable through **5 Jan 2027** (standard 30 days after 5 Dec) |
| Brilliant Earth | Items ordered **1 Nov – 15 Dec** returnable through **15 Jan** |
| VRAI | Purchases **1 Nov – 16 Dec 2026** returnable through **15 Jan 2027** |
| Sarraf | Items purchased **3 Nov 2026 – 15 Dec 2025** (sic) returnable through **15 Jan 2027** — see F-A21-06 |
| Ross-Simons | Items purchased **16 Oct – 25 Dec 2026** returnable through **31 Jan 2027** |

Other new facts, by seller: Blue Nile refund timing 5–15 business days · Allurez unreturned free gift deducted at retail value, refund in 7 business days · VRAI recycling fees USD 300 / 50 / 50, waived for store credit, plus an EU/EEA 14-day statutory withdrawal right · Mejuri sets must be returned complete, excessive-return refusal clause · Brilliant Earth the USD 1,000 portal limit and comparative-purchasing ban · Anjolee free size adjustment and Return Ticket ID · Sarraf "do not ship via FedEx" for international returns and duty clawback · Catbird in-store 20-day/store-credit-only and 7–10 business-day processing · Menē prepaid FedEx label on approval.

---

## 3. Legal layer

| Source | Read today | What the page says (quoted) | Effect on the project |
|---|---|---|---|
| [FTC — Buying Platinum, Gold, and Silver Jewelry](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry) | **Yes** | "Near the karat quality mark, look for the name or the U.S. registered trademark … If … you don't see a trademark along with the karat mark, don't buy it." · "The phrase 'solid gold' means the gold item isn't hollow." · gold filled / overlay / RGP / electroplate / vermeil / flashed defined | Confirms the site's hallmark rule and its `solid_gold_status` treatment. No change needed |
| [15 U.S.C. § 295](https://www.law.cornell.edu/uscode/text/15/295) | **Yes** | 3/1000 tolerance on the solder-free sample; **in addition** 7/1000 on the whole article (3/1000 for watchcase/flatware), "concurrent and not alternative" | The `minimum_fineness_if_stamped` table checks out arithmetically: 0.5833 − 0.007 = 0.5763 (14K), 1.0 − 0.007 = 0.993 (24K) |
| 16 CFR Part 23, 15 U.S.C. §§ 297 / 1666 / ch. 8, CFPB Reg Z, NIST HB 44, NIST SP 811, LBMA, Kitco/BullionVault/JM Bullion spot pages | **No — not re-fetched this pass** | — | They keep their 2026-10-22/23 dates. The CFR citation gate validates 110 references against a stored section table; that is an internal check, **not** a live re-read, and this report does not claim otherwise |

---

## 4. Independent derivation audit

`scripts/session_91e9aba0/derive_audit.py` re-derives every weighted row, every karat/retailer/category aggregate and
every karat-pair gap from the stored inputs, using `decimal.Decimal` with `ROUND_HALF_UP` — a different
implementation from both `scripts/compute.py` (producer) and `scripts/audit.py` (project checker).

```
independent Decimal re-derivation | 64 rows, 17 weighted, 7 karat pairs | 644 field comparisons
benchmark in force: USD 3996.31/oz = USD 128.48435/g (22 October, 2026)
NOTE: 3 aggregate value(s) differ by one hundredth (half-way rounding path, not a data error):
    retailer:vrai multiple_min: exact-decimal 3.76 vs stored 3.75
    retailer:vrai multiple_max: exact-decimal 3.76 vs stored 3.75
    retailer:vrai multiple_avg: exact-decimal 3.76 vs stored 3.75
PASS: every derived value, aggregate and pair gap re-derives to the stored figure
```

The note is a genuine (if tiny) presentation defect: VR-01 is `USD 1,035` over `USD 275.604…` of gold =
**3.755457**; at two decimals `ROUND_HALF_UP` gives **3.76**, while the float path in `compute.py` prints **3.75**.
Both the dashboard row and the retailer aggregate show 3.75. It is not fabricated, it is rounded on the wrong side
of a half-way digit — recorded as F-A21-02.

---

## 5. Findings, and what this session asks the Pass 21 owner to do

This session edits no shared file. Each finding below is a **request** logged on the board.

| ID | Severity | Finding | Requested action |
|---|---|---|---|
| **F-A21-01** | High (for the research, not a bug) | The official gold panel moved to **USD 4,059.49/oz, "Data as of 10 November, 2026"** (+1.58% on the stored USD 3,996.31). Every derived gold value on the site is still computed at the 23 October rate, so all of them now understate the metal value by about 1.6% | Replace the benchmark with a first-hand reading of the same panel, keep the old value in `prior_captures`, re-run `compute.py`, state the new USD/g rate and the reading date on the site |
| **F-A21-02** | Low | VR-01's displayed multiple is **3.75**; exact arithmetic gives **3.755457 → 3.76**. Same value appears in the VRAI aggregate | Round presentation output with `Decimal`/`ROUND_HALF_UP` rather than binary-float `round()`, or display 3 decimals consistently |
| **F-A21-03** | Medium | Ross-Simons' stored exclusion **"Final sale items"** is **not printed** on today's returns page, which instead says "return eligible merchandise" and adds an extended holiday window (16 Oct – 25 Dec 2026 → 31 Jan 2027). With RS-05 already flagged `CLEARANCE_RETURN_TERMS_UNCLEAR`, the *basis* for that exclusion is now unconfirmed | Keep the flag, mark the exclusion `basis_not_reconfirmed_2026-11-11`, and record the holiday window; ask Ross-Simons in writing before relying on final-sale status |
| **F-A21-04** | Medium | **Anjolee `return_exclusions` is empty**, but its official policy page states a **15% restocking fee** for worn/non-original items and requires a Return Ticket ID. Its `resize` field ("not captured") is now verifiable as **free size adjustment**, and `service@anjolee.com` is published but not stored | Add the restocking fee and Return Ticket ID conditions, fill the resize field from the page, add the email |
| **F-A21-05** | Medium | Sarraf's guarantee fee is **10% of the *current* price**, not the *purchase* price as stored | Correct the wording; the arithmetic consequence is that the fee can exceed 10% of what was paid if the gold price rose |
| **F-A21-06** | Medium (seller defect) | Sarraf's extended-holiday paragraph is self-contradictory: "items purchased between **November 03, 2026**, and **December 15, 2025**, are returnable through January 15, 2027" | Publish it verbatim as a seller-page defect. Do **not** silently pick one date |
| **F-A21-07** | Medium | **Menē refunds are Menē Credit by default** within the 7-day window; the dataset records the window but not the store-credit structure, and stores no contact although the page prints +1 833 636 3245 and service@mene.com | Record the credit-first structure and the contact; the 7-day window plus store credit is a material limit for a card-protection strategy |
| **F-A21-08** | Medium | **Catbird's stored resize line is imprecise** ("must inspect unengraved before return window closes"); the page describes a paid repairs/resizing service for Catbird-bought pieces and exchanges by return + new order | Rewrite from the page wording |
| **F-A21-09** | Low | **Brilliant Earth** has been refused with HTTP 403 to the runner for 19 days; today's browser read shows the page is alive and printing the 30-day and resize terms, so the 403s are bot filtering, not link rot. Also resolved: the "1-year vs 60-day resizing" conflict is **one rule with two branches** | State the resolution on the Freshness/Flagged pages and stop treating the two readings as a conflict |
| **F-A21-10** | Low (housekeeping) | `data/sources.json` registers the **same Brilliant Earth URL twice** (`brilliant-earth-returns`, `brilliantearth-returns-30d`) | Merge into one entry, keeping both retrieval notes |
| **F-A21-11** | Low | Anjolee's registered "returns" source is a **product page**; the seller has a dedicated official policy page at `/information/ReturnPolicy` (found in Anjolee's own navigation, not guessed) | Register the policy page as the returns source and keep the product page for the product facts |
| **F-A21-12** | Info | Five sellers now advertise **extended holiday return windows** (table in §2) that the dataset does not carry | Publish them dated, as seller promises that expire |
| **F-A21-13** | Info | The legal layer holds: FTC guidance and 15 U.S.C. § 295 both still say what the project quotes, and the fineness-tolerance arithmetic matches the statute | No change |
| **F-A21-14** | Info | 644 independent arithmetic comparisons: **0 mismatches**; 1 rounding note (F-A21-02) | No change |

---

## 6. What this pass does **not** establish

* It does **not** re-read any of the 64 ring product pages, any ring price, weight, karat or availability — that is the
  concurrent Pass 21 owner's scope, and duplicating it would have produced two half-sweeps instead of one full one.
* It does **not** prove any ring is solid gold, hallmarked, or worth its price.
* It does **not** re-fetch 16 CFR Part 23, the NIST, CFPB or remaining USC pages; they keep their October dates.
* The seller policies above are **promises read on 2026-11-11**, not contract terms this project can enforce. A policy
  can change the day after it is read — which is exactly why every row above carries its URL and its read date.

**Standing instruction, unchanged:** after every review, look for hallucinations again — source link, read date, read
path, and whether anything was inferred rather than read.
