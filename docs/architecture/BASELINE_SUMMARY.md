# Operational Baseline Summary

**Commit ID:** fc598035ce6eb44797639f918e999e85f5125b1c  
**Tag:** baseline-2026-07-26  
**Created:** 2026-07-26  
**Status:** OFFICIAL OPERATIONAL BASELINE

---

## Reference Documents

- `PLAN.md` — Master Roadmap v2.1 (updated 2026-07-26)
- `CURRENT_STATUS.md` — Current operational status (updated 2026-07-26)
- `PROJECT_BASELINE_AFTER_WP21.md` — Post-WP-21 baseline snapshot (updated 2026-07-26)
- `docs/architecture/FINAL_BASELINE.md` — Final verification baseline document
- `docs/architecture/WORK_PACKAGE_PLAN.md` — Work Package reference
- `CHANGELOG.md` — Change history
- `ENGINEERING_MEMORY.md` — Engineering memory and decisions

---

## Verified Runtime State

- **Backend:** Running, healthy, 84 API endpoints registered in OpenAPI
- **Frontend:** Running, serving on port 3000, Arabic title renders correctly with `charset=utf-8`
- **Dashboard:** `/api/v1/dashboard` registered and responding
- **Search:** `/api/v1/search` registered and responding
- **Notifications:** `/api/v1/notifications/` list endpoint registered and responding
- **Customs:** `/api/v1/customs/` list endpoint registered and responding
- **Shipping:** `/api/v1/shipping/shipments` registered and responding
- **Authentication:** Register/login endpoints operational
- **Database:** SQLite (`/app/data/nile_key.db`) with owner user present

---

## Baseline Contents

This baseline captures the verified operational state after:
1. Verification Forensic Audit (2026-07-26) — 10/10 checks passed
2. Documentation synchronization — CURRENT_STATUS.md, PLAN.md, PROJECT_BASELINE_AFTER_WP21.md updated
3. Runtime fixes applied — dashboard/search routers registered, notifications/customs list endpoints added, frontend charset corrected

---

## Important Notice

**This version is the official operational reference before any further development.**

Any subsequent work must:
1. Be based on this baseline commit (`baseline-2026-07-26`)
2. Follow the governance process defined in `PLAN.md`
3. Update documentation before marking any Work Package as closed
4. Maintain backward compatibility with the verified API surface

---

## Restoration

To restore this baseline:
```bash
git checkout baseline-2026-07-26
git checkout -b baseline-restored
```

Or to reset to this baseline:
```bash
git reset --hard baseline-2026-07-26
```

---

**Authority:** Project Owner / Governance  
**Next Review:** Before WP-42 Owner Acceptance
