# Governance Plan: Accept Complementary-Only Coverage for SPS/TBT

**Plan ID:** 1787046369923-sps-tbt-complementary-only-decision  
**Date:** 2026-08-18  
**Status:** Ready for Execution  
**Authority:** `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md`  
**Scope:** Document final portfolio decision for SPS/TBT gap only  
**Constraints:** No implementation, no G1, no code changes, no PLAN.md rewrites, no reopening ePing/I-TIP

---

## 1. Objective

Document the decision to **accept Complementary-Only Coverage for the Regulatory / SPS / TBT knowledge family**, reflecting that:
- No current candidate meets Provider Admission Criteria for SPS/TBT automation.
- WTO ePing and WTO I-TIP are closed as candidates and cannot be reopened under this decision.
- The SPS/TBT Automated Provider Coverage score remains **0/10**.
- Complementary sources (ePing web portal, Codex, IPPC) exist but do not count toward automated coverage.

---

## 2. Affected Files and Sections

| File | Section | Change Type |
|------|---------|-------------|
| `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` | Section 27.7 — Phase 5 Regulatory / SPS / TBT | **Update** |
| `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` | Section 30.1 — Current Open Items | **Update** |
| `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` | Section 30.2 — Governance Blockers | **Update** |
| `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` | Section 31.2 — Next Actions | **Update** |
| `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` | Section 27.5 — 7-Family Baseline Snapshot (Regulatory / SPS / TBT row) | **No change to score**; update trigger wording only |

**No other files are modified.**

---

## 3. Required Changes

### 3.1 Section 27.7 — Phase 5 Regulatory / SPS / TBT

**Current state:** Blocked — Complementary Only — "no automated provider addition until public REST API is verified"  
**New state:** Complementary-Only Accepted — No automated provider — Gap remains open

**Changes:**
- Update `Phase Status` to: **Complementary-Only Accepted — Gap Unfilled**
- Update `Current Coverage` to: **0/10 (Automated Provider Coverage)**
- Add explicit statement: **"WTO ePing and WTO I-TIP are CLOSED as candidates for this gap. They cannot be reopened under this decision."**
- Update `Primary Source` to: **None (automated)**
- Update `Secondary/Fallback` to: **Manual/Complementary: WTO ePing web portal + XLSX downloads; Codex (FAO/WHO); IPPC (FAO)**
- Update `Provider vs Complementary` to: **All sources = Complementary; no automated provider; no candidate currently qualifies for G1**
- Update `Entry Gate` to: **N/A — No provider entry without documented public REST API providing current SPS/TBT data and server-side filtering**
- Update `Exit/Acceptance Gate` to: **N/A — Complementary status is the accepted end state for this phase**
- Update `Trigger for Re-Evaluation` to: **A new machine-readable source emerges that: (1) provides current SPS/TBT data, (2) offers server-side filtering by SPS/TBT type, country, date, and product/HS, (3) meets all Provider Admission Criteria, AND (4) Project Owner approves ceiling expansion or replacement of an existing provider**
- Update `Dependencies` to: **No automated source currently exists; gap remains dependent on future API availability or Project Owner decision to accept complementary-only coverage permanently**

**Phase 5 Constraints (update):**
- WTO ePing is CLOSED as a candidate for this gap. No re-evaluation unless new evidence of server-side filtering emerges.
- WTO I-TIP is CLOSED as a candidate for this gap. Its SPS/TBT data is delegated to ePing and is historical only (1995-2021).
- Codex and IPPC remain Complementary (web-only). No provider feasibility.
- No WP creation for any SPS/TBT automation until a verifiable public REST API with filtering is confirmed.
- **This is a P0 Critical Gap that remains unfilled and is accepted as Complementary-Only.**

### 3.2 Section 30.1 — Current Open Items

**Current SPS/TBT row:**
| 1 | SPS/TBT Gap (0/10) | P0 — Unfilled | WTO ePing/TFA remain blocked; no alternative source identified |

**New SPS/TBT row:**
| 1 | SPS/TBT Automated Coverage Gap (0/10) | P0 — Unfilled — Accepted as Complementary-Only | No machine-readable source currently meets Provider Admission Criteria; complementary access via ePing/Codex/IPPC maintained |

**Add new row:**
| 7 | SPS/TBT Re-evaluation Trigger | P0 — Monitor | Re-open candidate evaluation only when a new source provides current SPS/TBT data with server-side filtering and meets Provider Admission Criteria |

### 3.3 Section 30.2 — Governance Blockers

**Current SPS/TBT blocker:**
| SPS/TBT Automated Access | WTO ePing | Public REST API required |

**New SPS/TBT blocker:**
| SPS/TBT Automated Access | None currently available | Accept Complementary-Only; re-evaluate only when a new source meets Provider Admission Criteria with current data and filtering |

### 3.4 Section 31.2 — Next Actions

**Current ePing/TFA monitoring actions:**
| 3 | Monitor WTO ePing for verifiable public REST API | Governance | No action until REST API confirmed |
| 4 | Monitor WTO TFA Database for verifiable public REST API | Governance | No action until REST API confirmed |

**New actions (replace):**
| 3 | Maintain Complementary SPS/TBT access via ePing/Codex/IPPC | Governance | No automated provider; manual/complementary access only |
| 4 | Monitor for new machine-readable SPS/TBT source with filtering | Governance | Re-evaluate only when source provides current data + filtering + meets Provider Admission Criteria |

### 3.5 Section 27.5 — 7-Family Baseline Snapshot

**Regulatory / SPS / TBT row (line 1442):**
- `Current Score`: **0/10** — **NO CHANGE**
- `Target Score`: **9/10** — **NO CHANGE**
- `Provider / Complementary`: Update to: **Complementary: WTO ePing, Codex, IPPC, WTO TFA Database. No automated provider. No candidate currently qualifies for G1.**
- `API / Machine Access`: Update to: **None (all web-only/XLSX). WTO ePing API exists but lacks filtering; classified as Complementary.**
- `Implementation Priority`: Update to: **P0 — Complementary-Only Accepted**
- `Entry Gate`: Update to: **N/A — No provider entry without verifiable public REST API with current SPS/TBT data and server-side filtering**
- `Trigger for Re-Evaluation`: Update to: **New machine-readable source with current SPS/TBT data + filtering + Provider Admission Criteria met + Project Owner approval**

---

## 4. Values That Must NOT Change

| Value | Current | Must Remain |
|-------|---------|-------------|
| Regulatory / SPS / TBT Current Coverage Score | 0/10 | **0/10** |
| Regulatory / SPS / TBT Target Coverage Score | 9/10 | **9/10** |
| Provider Ceiling | 7 | **7** |
| World Bank LPI Status | Implemented / G5 Closed | **No change** |
| ePing Classification | Complementary | **Complementary — CLOSED** |
| I-TIP Classification | Complementary | **Complementary — CLOSED** |
| Codex/IPPC Classification | Complementary | **Complementary** |
| WTO TFA Classification | Complementary | **Complementary** |
| Provider Admission Criteria | As defined in Section 12 | **No change** |
| Stopping Conditions | As defined in Section 28.3 | **No change** |

---

## 5. Checklist for Execution

### Pre-Execution Verification
- [ ] Confirm no modifications to any file other than `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md`
- [ ] Confirm no code changes, no provider implementation, no G1 initiation
- [ ] Confirm WTO ePing remains classified as Complementary and CLOSED
- [ ] Confirm WTO I-TIP remains classified as Complementary and CLOSED for SPS/TBT
- [ ] Confirm SPS/TBT Automated Provider Coverage score remains 0/10
- [ ] Confirm no new candidate is inserted into the plan without evidence

### Post-Execution Verification
- [ ] Section 27.7 updated with Complementary-Only decision
- [ ] Section 30.1 updated with new SPS/TBT gap status
- [ ] Section 30.2 updated with blocker resolution
- [ ] Section 31.2 updated with new next actions
- [ ] Section 27.5 baseline snapshot updated (trigger wording only, score unchanged)
- [ ] All cross-references to SPS/TBT remain consistent
- [ ] No contradictory statements introduced

---

## 6. Prohibited Actions

| Action | Status |
|--------|--------|
| Reopen WTO ePing as candidate | ❌ Prohibited |
| Reopen WTO I-TIP as SPS/TBT candidate | ❌ Prohibited |
| Add new provider without evidence | ❌ Prohibited |
| Change SPS/TBT coverage score from 0/10 | ❌ Prohibited |
| Initiate G1 for any candidate | ❌ Prohibited |
| Modify PLAN.md or other governance documents | ❌ Prohibited |
| Execute implementation or WP creation | ❌ Prohibited |
| Expand provider ceiling | ❌ Prohibited without separate PO approval |

---

## 7. Re-Evaluation Trigger (Final)

SPS/TBT candidate evaluation may be reopened **ONLY** when **ALL** of the following are true:

1. A new source provides **current SPS/TBT data** (not historical/delegated)
2. The source offers **server-side filtering** by SPS/TBT type, country, date, and product/HS code
3. The source has a **documented, accessible REST/SDMX/JSON API** (Tier A)
4. The source meets **all Provider Admission Criteria** (Section 12)
5. **Project Owner approval** is obtained for ceiling expansion or provider replacement
6. **Live evidence** confirms API behavior (not just portal listing)

**Until then: Complementary-Only coverage is the accepted and final state for SPS/TBT.**

---

## 8. Execution Sequence

1. Update Section 27.7
2. Update Section 30.1
3. Update Section 30.2
4. Update Section 31.2
5. Update Section 27.5 trigger wording (score unchanged)
6. Run checklist verification
7. Stop — no further action
