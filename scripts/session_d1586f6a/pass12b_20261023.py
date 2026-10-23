#!/usr/bin/env python3
"""Pass 12b — corrections found by reading the Standards page line by line after Pass 12.

Live sources opened for this round (2026-10-23):
  https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.7
  https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.8
  https://www.law.cornell.edu/uscode/text/15/297
  https://www.law.cornell.edu/uscode/text/15/1666
  https://www.consumerfinance.gov/ask-cfpb/how-do-i-dispute-a-charge-on-my-credit-card-bill-en-61/
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
TODAY = "2026-10-23"


def load(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def save(name, obj):
    with open(DATA / name, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


catalog = load("catalog_a0be79d4.json")
ecfr = next(s for s in catalog["standards_sources"] if "23.1" in s["citation"])
cfpb = next(s for s in catalog["standards_sources"] if "1666" in s["citation"])

# 1. same 10K myth, second location: the summary bullets under the eCFR card.
old = "16 CFR § 23.3: Unqualified 'Gold' means 24K through and through; <10K cannot be called karat gold; hollow centers must not be deceptively described."
new = ("16 CFR § 23.3: unqualified 'Gold' means fine (24K) gold through and through; a gold alloy must carry its karat designation "
       "immediately before the word 'Gold' and with equal conspicuousness; hollow-centred articles should not be marked 'solid'. "
       "There is NO 10-karat floor for calling a gold alloy 'karat gold' — § 23.3(c)(1) itself gives '9 Karat Gold' as acceptable — "
       "10 karat survives only as the minimum fineness for plating, gold-filled and vermeil (§ 23.3(c)(2)-(3), § 23.4(b)).")
i = ecfr["key_takeaways"].index(old)
ecfr["key_takeaways"][i] = new

# 2. § 23.7 / § 23.8 wording: separate what each section actually requires.
old2 = "16 CFR § 23.7 & § 23.8: White gold rhodium plating and multi-metal components (e.g., 18K shank + platinum/14K prongs) require non-deceptive disclosure in weight order."
new2 = ("16 CFR § 23.7: it is unfair or deceptive to fail to disclose a surface-layer application of rhodium on a product marked or "
        "described as precious metal — the relevant rule for rhodium-plated white gold. 16 CFR § 23.8: where a product contains more "
        "than one precious metal, the relative quantity of each must not be misrepresented, and metals should be listed from greatest "
        "to least by weight (e.g., an 18K shank with platinum prongs).")
j = ecfr["key_takeaways"].index(old2)
ecfr["key_takeaways"][j] = new2

# 3. Trademark rule: assert only what 15 U.S.C. § 297(b) actually says.
old3 = "16 CFR § 23.9 & 15 U.S.C. § 297 (National Stamping Act): Every quality stamp must be accompanied by the registered manufacturer/seller trademark."
new3 = ("15 U.S.C. § 297(b) (National Stamping Act): a quality mark indicating gold or silver must be accompanied by the maker's "
        "registered trademark (or the maker's name), applied by the same means, in lettering at least as large, and as close as "
        "possible to the quality mark. § 297(b)(B) adds that where a multi-part article has parts of different quality, each other "
        "part must carry a matching quality mark. The FTC's consumer page states the practical version: don't buy a gold piece if "
        "the trademark is missing beside the karat mark.")
k = ecfr["key_takeaways"].index(old3)
ecfr["key_takeaways"][k] = new3

# 4. CFPB figure: the linked CFPB page does not state the two-billing-cycle/90-day deadline.
old4 = "Written dispute notice must reach card issuer within 60 days after the first statement showing the charge; creditor must acknowledge within 30 days and resolve within 2 billing cycles (max 90 days)."
new4 = ("Written dispute notice must reach the card issuer within 60 calendar days after the charge appeared on the statement, and the "
        "issuer has 30 days to acknowledge it — both read directly from the CFPB page linked here. The resolution deadline (within two "
        "complete billing cycles, and in no event later than 90 days, after receiving the notice) is set by the statute, 15 U.S.C. "
        "§ 1666(a)(B), which the CFPB page does not restate; the statute is linked separately above.")
m = cfpb["key_takeaways"].index(old4)
cfpb["key_takeaways"][m] = new4

# 5. give the statutory deadline its own linked source card
catalog["standards_sources"].append({
    "authority": "U.S. Code (Legal Information Institute, Cornell Law School)",
    "citation": "15 U.S.C. § 1666 — Correction of billing errors",
    "title": "15 U.S.C. § 1666 — Correction of billing errors (Fair Credit Billing Act)",
    "source_url": "https://www.law.cornell.edu/uscode/text/15/1666",
    "key_takeaways": [
        "§ 1666(a): on receiving a written billing-error notice within 60 days of the statement, the creditor must send a written acknowledgement within 30 days (unless it resolves the dispute in that time).",
        "§ 1666(a)(B): the creditor must correct the account or send a written explanation within two complete billing cycles, and in no event later than 90 days, after receiving the notice.",
        "§ 1666(b)(3): a 'billing error' includes goods or services not accepted by, or not delivered in accordance with the agreement to, the cardholder.",
    ],
    "retrieved_date": TODAY,
})

catalog["flagged_items"].append({
    "flag_id": "FLG-PASS12-05",
    "severity": "HIGH",
    "category": "Anti-Hallucination Correction (same error, second location)",
    "item_ref": "standards.html — eCFR summary bullets (16 CFR § 23.3 line)",
    "title": "Same 10K Myth Found In A Second Place After The Table Was Fixed — Plus Two Wording Fixes To § 23.7/§ 23.8 And The Chargeback Deadline",
    "detail": (
        "Reading the Standards page line by line after the karat table was corrected showed the '10K is the legal minimum' myth repeated "
        "verbatim in the eCFR summary bullet. It is now replaced with what § 23.3 actually requires. Two further statements were tightened: "
        "(a) the § 23.7/§ 23.8 bullet conflated two different rules — § 23.7 requires disclosure of a rhodium surface layer, while § 23.8 "
        "requires metals to be listed from greatest to least by weight; (b) the chargeback bullet attributed the 'two billing cycles / max "
        "90 days' resolution deadline to the CFPB page, which does not state it — that deadline is in 15 U.S.C. § 1666(a)(B), which is now "
        "cited and linked. The 60-day notice period and the 30-day acknowledgement are confirmed on the CFPB page itself."
    ),
    "action": "Both legal bullets rewritten to match the regulation text; 15 U.S.C. § 1666 added as its own linked source card so the deadline is traceable.",
    "source_url": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3",
    "date": TODAY,
})
save("catalog_a0be79d4.json", catalog)

# 6. log the second round
log = load("verification_log.json")
log["passes"].append({
    "pass": "Pass 12b — Standards-page line-by-line legal re-read (session arena/d1586f6a-gold4)",
    "when_utc": "2026-10-23T10:25Z",
    "scope": "Reading the published Standards page line by line against the regulation text, after Pass 12 corrected the karat table.",
    "checked": [
        "16 CFR § 23.7 (read live): titled 'Disclosure of surface-layer application of rhodium' — failure to disclose rhodium on a product described as precious metal is unfair or deceptive. The site's combined § 23.7/§ 23.8 bullet was rewritten to separate it from § 23.8.",
        "16 CFR § 23.8 (read live): 'Misrepresentation as to products containing more than one precious metal' — mark relative quantity correctly; list metals in order of relative weight, greatest to least, unless context makes clear the first-listed metal is not predominant. Site wording updated to match.",
        "15 U.S.C. § 297 (read live): 'Stamping plated articles' — § 297(b)(A) requires the maker's registered trademark or name, applied by the same means as the quality mark, in lettering at least as large, as close as possible to it; § 297(b)(B) requires matching quality marks on non-identical parts. The site's trademark bullet now quotes this instead of paraphrasing § 23.9.",
        "CFPB billing-error page (read live): confirms the 60-calendar-day written notice and the creditor's 30-day acknowledgement. It does NOT state a two-billing-cycle/90-day resolution deadline, so that figure was re-attributed to the statute.",
        "15 U.S.C. § 1666 (read live): § 1666(a)(A) 30-day acknowledgement; § 1666(a)(B) resolution within two complete billing cycles and in no event later than 90 days; § 1666(b)(3) goods not delivered per the agreement counts as a billing error.",
        "IRREGULARITY FOUND AND CORRECTED: the 10K-is-the-legal-minimum myth appeared a SECOND time, in the eCFR summary bullet, after Pass 12 fixed the karat table. Replaced. Published as FLG-PASS12-05 — evidence that fixing one instance is not verification of the page.",
    ],
    "not_verified_this_pass": [
        "The two GIA Gems & Gemology citations (EDXRF depth limits; electroformed-gold lab note) were not re-opened in this round; their retrieved date remains 2026-10-22.",
        "16 CFR § 23.9 was not re-read this round; the site no longer attributes any specific requirement to it.",
    ],
    "result": "PASS — 5 further official pages read live; 3 statements corrected (10K myth repeat, § 23.7/§ 23.8 conflation, chargeback deadline attribution); 1 new linked source card (15 U.S.C. § 1666).",
    "outcome": "Standards page now states only what the cited text says; every correction is on the Flagged page.",
})
save("verification_log.json", log)
print("Pass 12b applied: 3 statements corrected, 1 source card added, 1 flag published.")
