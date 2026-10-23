# R-b8c1f11d — Live production-site verification (2026-10-23)

> **NO-HALLUCINATION RULE** applies to this record too: each line is either a verbatim read of the deployed
> page (quoted, with fetch time UTC) or the Pages API's own answer. A final post-integration re-check is run
> after this session's own merge and appended to the close-out section of `COORDINATION.md`.

Production target: **https://karagemop466-tech.github.io/GOLD4/** (Pages API: `source: main /`, `https_enforced: true`).

## Baseline fetches (this session's own reads)

| UTC | Page (deployed) | What it served (verbatim reads) | Verdict |
|-----|-----------------|----------------------------------|---------|
| 09:57 | `/` (front page, build of merge `6256af9`) | "⚠ NO HALLUCINATIONS — read before using any number" block at the top with the FTC + § 295 links and "Re-run the check after every review" instruction; "64 rings tracked / across 10 retailers"; "62 prices read from source / captured 22 October 2026"; "17 gram weights published / the rest stay blank"; "**$129.39** gold per gram · **$4,024.45/oz** · 22 October, 2026"; "234 flags raised"; "Only 17 of 64 rows can be priced against their gold at all… 1.33× to 6.65×" | ✔ required no-hallucination summary **is** the front-page top; served counts match the repo data exactly (64/10/62/17) and the served spot matches the live WGC panel I fetched at the same minute |
| ~10:30 | `/pages/flagged.html` | Same no-hallucinations block; "Blank values — 48 of 64 rows" table with per-row official-page links; MN-01 served at its stored **$1,465** (snapshot of 22 Oct — my live Menē read at 10:15 showed $1,454; documented as `PRICE_MOVED_SINCE_CAPTURE` in the corroboration record, request logged for the data owner); CB-01 "from $3,900"; VR-02 price cell blank | ✔ flagged page serves sourced, dated content; the MN-01 staleness is the expected snapshot behaviour, flagged |
| ~10:31 | `/categories/calculator.html` (NIST stone-deduction suite) | "NO HALLUCINATIONS — STRICT VERIFICATION RULE" banner; four **dated** spot feeds labelled (BullionVault 2026-10-22 $4,026.25; JM Bullion ask $4,039.76 / bid $4,025.26; WGC 2026-10-21 $4,024.36); RS-01 preset computes 1.700 g 14K → 0.9917 g pure → $128.37 melt at its own labelled $129.45/g feed (self-consistent); karat table with millesimal stamps + § 295 floors incl. "10K … 41.67% … **lowest traditional US karat standard**" (the post-PR-#27 wording — matches the CFR text I read); NIST HB 44 PDF linked for 0.200 g/ct | ✔ calculator arithmetic spot-checked against its own labelled feeds; wording matches the regulation text I re-read |
| 10:12 | Pages API `pages/builds/latest` | `{"commit":"86cebea…","status":"built","created_at":"2026-10-23T10:12:37Z"}` — i.e., each of this morning's merges (#27→#35+) produced a successful build; `main` head at that moment = `86cebea` | ✔ deploy pipeline healthy |

## Cross-checks against the repo tree

1. Served front-page numbers == `data/derived.json` stats == my hand recompute (64 rows / 62 prices / 17
   weights / 19 solid-wording rows / 0 hallmarks; $4,024.45/oz = $129.389072/g). ✔
2. No-hallucination summary, FTC link and § 295 link are on the front page **and** the flagged page **and** the
   categories calculator — the three entry points a buyer would land on. ✔
3. Calculator behaviour (categories suite): stone deduction 0.200 g/ct, pennyweight conversion shown
   (1 dwt = 1.5552 g ✔ definition), troy ounce 31.1035 g ✔; § 295 floor modes −0.003/−0.007 ✔.
   The categories calculator prices rows against **its own dated feed panel**, not the canonical benchmark —
   each number it shows is labelled with the feed it used, so no unstated basis was found. ✔
4. Left for post-integration final check: full re-fetch of `/`, `/pages/flagged.html`, `/pages/calculator.html`
   + a spot check that the deployed build's commit == the merge commit of this session's own PR, and that
   `https://karagemop466-tech.github.io/GOLD4/reviews/` resolves (this session's browsable findings page).

## Live-site irregularities surfaced (all logged, none blocking)

- **MN-01 snapshot staleness visible in production** ($1,465 served vs $1,454 live): inherent to the
  frozen-snapshot design and already caveated on the site ("prices are a snapshot… re-check the source link");
  logged for the data owner — see corroboration record D-2.
- **Deployed content churns with every merge** (5+ builds in ~20 min this morning): fine for a research site,
  but it means the *printed* "captured 22 October 2026" freshness line refers to the data capture date, not
  the deploy time — a reader could confuse the two. Suggestion (logged): the front page already separates
  "captured" vs "benchmark dated"; keep that discipline on every page during `03c0c10f`'s consolidation.

*Reviewer: session `arena/b8c1f11d-gold4` · review id `R-b8c1f11d` · 2026-10-23.*
