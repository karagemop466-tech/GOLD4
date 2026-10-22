# AUDIT — hallucination/security check
Date: 2026-10-22

HARD FAILURES: 0

FLAGGED (blank/unverified, by design): 15
- BN-01.weight_g: blank/UNVERIFIED (correct per policy)
- BN-02.weight_g: blank/UNVERIFIED (correct per policy)
- BN-03.weight_g: blank/UNVERIFIED (correct per policy)
- BN-04.weight_g: blank/UNVERIFIED (correct per policy)
- BN-05.weight_g: blank/UNVERIFIED (correct per policy)
- BN-06.weight_g: blank/UNVERIFIED (correct per policy)
- BN-07.weight_g: blank/UNVERIFIED (correct per policy)
- BN-08.weight_g: blank/UNVERIFIED (correct per policy)
- VR-02.price: blank/UNVERIFIED (correct per policy)
- MJ-01.weight_g: blank/UNVERIFIED (correct per policy)
- MJ-02.weight_g: blank/UNVERIFIED (correct per policy)
- MJ-03.weight_g: blank/UNVERIFIED (correct per policy)
- MJ-04.weight_g: blank/UNVERIFIED (correct per policy)
- MJ-05.weight_g: blank/UNVERIFIED (correct per policy)
- AN-01.weight_g: blank/UNVERIFIED (correct per policy)

Records audited: 20
Rule: a value with no official source link + retrieval date must stay blank. Re-run after every review.
Deeper checks (domain allow-list, recomputation of every derived number, speculation scan) run in scripts/audit.py.
