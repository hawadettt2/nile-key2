# Architecture Knowledge Inventory — EARP-001 Phase 1 Baseline

**Plan:** EARP-001
**Document:** Architecture Knowledge Inventory (Baseline)
**Status:** Approved — Phase 1 Baseline
**Authority:** EARP-001 Executive Architecture Decision (EAD)
**Date:** 2026-07-30
**Baseline For:** Phase 2 Conformance Audit, Phase 5 Controlled Refactoring

---

## 1. Overview

This inventory classifies all architecture documents in the Nile Key Platform repository into tiers per EARP-001 governance rules. It is the authoritative baseline for all subsequent EARP-001 phases.

**Rules:**
- No new architecture references may be added without a Change Request to EARP-001.
- Any document not listed here requires review and addition through change control before it may be considered part of the architecture baseline.
- Paths reflect the post-Documentation Consolidation state of the repository.

---

## 2. Tier 1 — Authoritative Architecture Documents

| # | Document | Path | Role |
|---|----------|------|------|
| 1 | PLAN.md | `PLAN.md` | Single Source of Truth |
| 2 | ED-WP30-001.md | `.kilo/plans/ED-WP30-001.md` | Executive decision correcting WP-30 architecture and dependency chain |
| 3 | wp30-architecture-compliance-review.md | `.kilo/plans/archive/1784079736812-wp30-architecture-compliance-review.md` | Level-0 architecture compliance review |
| 4 | WORK_PACKAGE_PLAN.md | `.kilo/plans/archive/WORK_PACKAGE_PLAN.md` | Master Work Package governance |

---

## 3. Tier 2 — Bounded Context Specifications

| # | Document | Path | Role |
|---|----------|------|------|
| 1 | wp30-implementation-plan.md | `.kilo/plans/archive/wp30-implementation-plan.md` | DEM implementation plan |
| 2 | wp31-implementation-plan.md | `.kilo/plans/archive/wp31-implementation-plan.md` | Long-Term Memory implementation plan |
| 3 | wp32-implementation-plan.md | `.kilo/plans/archive/wp32-implementation-plan.md` | Knowledge Graph implementation plan |
| 4 | WP-32-spec.md | `.kilo/plans/WP-32-spec.md` | Knowledge Graph specification |
| 5 | WP-33-spec.md | `.kilo/plans/WP-33-spec.md` | Trade Intelligence specification |

---

## 4. Tier 3 — Interface Contracts

| # | Document | Path | Role |
|---|----------|------|------|
| 1 | MEMORY_CONTRACT.md | `.kilo/plans/MEMORY_CONTRACT.md` | DEM + Memory interface contract |
| 2 | KNOWLEDGE_INGESTION_CONTRACT.md | `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md` | Company Knowledge ingestion contract |
| 3 | AVATAR_CONTRACT.md | `.kilo/plans/AVATAR_CONTRACT.md` | DEM + Avatar presentation contract |

---

## 5. Tier 4 — Current State References

| # | Document | Path | Role |
|---|----------|------|------|
| 1 | CURRENT_STATUS.md | `CURRENT_STATUS.md` | Live project status |
| 2 | ENGINEERING_MEMORY.md | `docs/architecture/ENGINEERING_MEMORY.md` | Completed work and decisions |

---

## 6. Tier 5 — Supporting Plans

| # | Document | Path | Role |
|---|----------|------|------|
| 1 | wp30d-reasoning-engine-plan.md | `.kilo/plans/archive/1784079736812-wp30d-reasoning-engine-plan.md` | Reasoning Engine plan |
| 2 | wp31-forensic-audit-and-correction-plan.md | `.kilo/plans/archive/1784207193717-wp31-forensic-audit-and-correction-plan.md` | WP-31 audit findings |
| 3 | 1784505859302-wp32-knowledge-graph-plan.md | `.kilo/plans/archive/1784505859302-wp32-knowledge-graph-plan.md` | Knowledge Graph planning package |
| 4 | wp33-implementation-plan.md | `.kilo/plans/archive/wp33-implementation-plan.md` | Trade Intelligence implementation plan |
| 5 | CHANGELOG.md | `CHANGELOG.md` | Version history |
| 6 | README.md | `README.md` | Project entry point |

---

## 7. Change Control

Any addition, removal, or modification of architecture references requires:
1. A Change Request recorded in `.kilo/plans/earp-001/`
2. Review against this inventory
3. Update to this inventory and the baseline snapshot (`earp-001-baseline-snapshot.json`)
