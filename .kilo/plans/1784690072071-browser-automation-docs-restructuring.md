# Browser Automation Documentation Restructuring — Implementation Plan

**Plan ID:** 1784690072071-browser-automation-docs-restructuring
**Authority:** BA-DEC-001 (Executive Decision)
**Governing Documents:** PLAN.md, PROJECT_EXECUTION_RULES.md
**Date:** 2026-07-22
**Status:** Ready for Execution
**Baseline:** ebc2181 (HEAD)

---

## 1. Purpose

Restructure the Browser Automation Platform documentation from one monolithic draft (`BA-ARCH-001`) into:
- `BA-ARCH-001` — Architecture-only specification (~300–400 lines)
- `BA-IMPL-001` — Implementation + Operations plan (new, following project `wp*-implementation-plan.md` pattern)
- Three standalone ADR files extracted from the original draft

This plan is governed by BA-DEC-001. No other document structure is authorized.

---

## 2. Scope

### In Scope
- Refining `BA-ARCH-001` (currently a draft in working memory; will be created as a new file)
- Creating `BA-IMPL-001`
- Extracting 3 ADRs to standalone `.kilo/plans/` files
- Recording the restructuring decision in `PLAN.md`
- Obtaining Project Owner approval before execution

### Out of Scope
- Creating `BA-OPS-001` — explicitly prohibited by BA-DEC-001
- Any architecture or implementation changes to the application
- Any code changes
- Any test execution

---

## 3. Pre-Execution Gates (Must Pass Before Starting)

| Gate | Requirement | Evidence | Status |
|------|-------------|----------|--------|
| G-1 | Project Owner approval of BA-DEC-001 | Formal approval record | **REQUIRED** — block until obtained |
| G-2 | Decision recorded in `PLAN.md` | Entry in `PLAN.md` Section 10.1 or 12.3 | **REQUIRED** |
| G-3 | No governance amendment needed | Confirmed by Governance Audit | PASS — no amendment required |
| G-4 | ADR file paths confirmed | Standard `.kilo/plans/` naming pattern | PASS — follow existing ADR convention |

---

## 4. Affected Files

| File | Action | Type |
|------|--------|------|
| `BA-ARCH-001` (new file) | **Create** — architecture-only content | New artifact |
| `BA-IMPL-001` (new file) | **Create** — implementation + operations content | New artifact |
| `.kilo/plans/BA-ARCH-001-ADR-001.md` | **Create** — ADR: Scope and Isolation | New artifact |
| `.kilo/plans/BA-ARCH-001-ADR-002.md` | **Create** — ADR: Browser Selection | New artifact |
| `.kilo/plans/BA-ARCH-001-ADR-003.md` | **Create** — ADR: MCP Integration | New artifact |
| `PLAN.md` | **Modify** — record restructuring decision | Existing artifact |

---

## 5. Content Mapping

### 5.1 BA-ARCH-001 — What Remains

Based on BA-DEC-001 Section 3.1:

| Sections Retained | Source Content | Notes |
|-------------------|---------------|-------|
| 1 — Executive Summary | High-level overview only | No implementation details |
| 2 — Background | Evidence-based history | Stable |
| 3 — Problem Statement | Architectural concern | Stable |
| 4 — Goals | Measurable architectural outcomes | Stable |
| 5 — Non-Goals | Scope boundaries | Stable |
| 6 — Current State Assessment | Evidence audit | Stable |
| 7 — Target Architecture | Principles + high-level design | Stable; remove specific tool versions |
| 8 — Logical Architecture | Component boundaries and responsibilities | Stable |
| 10 — Component Diagram | ASCII diagram | Stable |
| 11 — Runtime Flow | Behavioral architecture | Stable |
| 12 — Browser Automation Lifecycle | Conceptual lifecycle | Stable |
| 13 — Supported Execution Modes | Abstracted mode definitions | Stable |
| 14 — Integration Points | Architectural boundaries | Retain contracts; abstract ports/paths |
| 18 — Governance Rules | Test-to-UAT traceability, evidence retention, change control, backward compatibility | Stable |
| 22 — Future Extensibility | Extension points, planned extensions | Stable |
| 26 — Open Questions | Architectural decision tracking | Stable |
| 27 — Traceability | Governance compliance matrix | Stable |
| Section 25 — ADR Index Table | Table referencing standalone ADR files | Replaces full ADR text |
| Acceptance Criteria | Architectural ACs only (isolation, no runtime coupling, version control, no secrets in committed config) | Project spec precedent (WP-33, WP-42) |

### 5.2 BA-IMPL-001 — What Moves Here

Based on BA-DEC-001 Section 3.2:

| Content | Source Section | Notes |
|---------|---------------|-------|
| Configuration Strategy (detailed) | BA-ARCH-001 Section 15 | Full parameter table with defaults |
| Environment Strategy | BA-ARCH-001 Section 16 | Setup steps, bootstrap procedures |
| Dependency Matrix (specific packages) | BA-ARCH-001 Section 19.1 | `playwright`, `pytest-playwright`, `@playwright/mcp`, `typescript`, `ts-node` |
| Migration Strategy (detailed phases) | BA-ARCH-001 Section 21 | 7-phase table with owners and deliverables |
| Acceptance Criteria (verification) | BA-ARCH-001 Section 23 | Verification ACs with file paths, commands, methods |
| Success Metrics | BA-ARCH-001 Section 24 | Time-based metrics, developer feedback |
| Detailed Repository Layout | BA-ARCH-001 Section 9.1 | Complete directory tree with file names |
| Security operational procedures | BA-ARCH-001 Section 17 | `.env` exclusion, credential seeding, CI secrets handling |

### 5.3 ADR Extraction

| ADR File | Title | Source |
|----------|-------|--------|
| `.kilo/plans/BA-ARCH-001-ADR-001.md` | Scope and Isolation | BA-ARCH-001 Section 25 — ADR-BA-001 |
| `.kilo/plans/BA-ARCH-001-ADR-002.md` | Browser Selection — Chromium Only | BA-ARCH-001 Section 25 — ADR-BA-002 |
| `.kilo/plans/BA-ARCH-001-ADR-003.md` | MCP Integration as Enhancement | BA-ARCH-001 Section 25 — ADR-BA-003 |

Each ADR file follows the existing project ADR format:
- `docs/architecture/ADR-0001-shipments-legacy-columns.md` pattern
- Sections: Context, Options Considered, Decision, Rationale, Consequences, Related

---

## 6. Execution Sequence

### Step 1: Project Owner Approval and PLAN.md Recording
**Dependencies:** None
**Owner:** Project Manager + Architect
**Actions:**
1. Obtain formal Project Owner approval of BA-DEC-001
2. Record decision in `PLAN.md` per Section 10.1 ("كل تغيير MUST يُسجل في Master Roadmap v2.1 أولاً")
   - Add entry under Section 12.3 (Continuity Table) or Section 10.1
   - Record: BA-ARCH-001 → BA-ARCH-001 + BA-IMPL-001 split; 3 ADRs extracted
3. Verify approval recorded before proceeding

**Risk:** Project Owner defers decision
**Mitigation:** Escalate to Project Owner immediately; do not proceed without approval

---

### Step 2: ADR Extraction
**Dependencies:** Step 1 complete
**Owner:** Architect
**Actions:**
1. Create `.kilo/plans/BA-ARCH-001-ADR-001.md` — Scope and Isolation
2. Create `.kilo/plans/BA-ARCH-001-ADR-002.md` — Browser Selection
3. Create `.kilo/plans/BA-ARCH-001-ADR-003.md` — MCP Integration
4. Verify each ADR follows project ADR format (ADR-0001 pattern)
5. Verify no ADR content remains in BA-ARCH-001 after this step

**Risk:** ADR numbering conflicts with existing ADRs
**Mitigation:** Use distinct naming `BA-ARCH-001-ADR-*` to avoid collision with `ADR-*` sequence

---

### Step 3: BA-ARCH-001 Refinement
**Dependencies:** Step 2 complete
**Owner:** Architect
**Actions:**
1. Create/refine `BA-ARCH-001` with architecture-only content per Section 3.1 of this plan
2. Remove: Section 15 (detailed config), Section 16 (environment setup), Section 19.1 (package list), Section 21 (migration phases), Section 23 (verification ACs), Section 24 (metrics), Section 9.1 (detailed tree)
3. Retain: Architectural ACs in Section 23 (isolation, no app coupling, version control)
4. Replace Section 25 full ADR text with ADR index table referencing standalone files
5. Target size: ~300–400 lines
6. Abstract specific ports/paths in Section 14 (use "Backend provides `/health` endpoint" rather than `http://backend:8000/health`)

**Risk:** Over-refinement removes necessary architectural constraints
**Mitigation:** Review against BA-DEC-001 Section 3.1 checklist before finalizing

---

### Step 4: BA-IMPL-001 Creation
**Dependencies:** Step 3 complete
**Owner:** Architect + DevOps
**Actions:**
1. Create `BA-IMPL-001` following project `wp*-implementation-plan.md` pattern
2. Include content per Section 3.2 of this plan
3. Include environment setup steps, configuration parameters, dependency lists, migration phases, verification ACs, success metrics, repository layout
4. Include operational security procedures (`.env` exclusion, credential seeding)
5. Format: Task tables, commit sequences, file creation/modification lists, acceptance criteria with verification methods

**Risk:** BA-IMPL-001 duplicates content from other implementation plans
**Mitigation:** Cross-reference existing plans (`wp33-implementation-plan.md`, `wp42-implementation-plan.md`) for format consistency

---

### Step 5: PLAN.md Update
**Dependencies:** Steps 2–4 complete
**Owner:** Project Manager
**Actions:**
1. Add entry in `PLAN.md` recording documentation restructuring
2. Update `CURRENT_STATUS.md` if applicable
3. Verify no contradictions with existing `PLAN.md` content

**Risk:** PLAN.md update introduces inconsistencies
**Mitigation:** Review against BA-DEC-001 requirements before committing

---

### Step 6: Final Review and Approval
**Dependencies:** Steps 2–5 complete
**Owner:** Project Owner
**Actions:**
1. Project Owner reviews refined `BA-ARCH-001` and new `BA-IMPL-001`
2. Project Owner reviews extracted ADRs
3. Project Owner approves or requests revisions
4. If revisions requested: return to relevant step

---

## 7. Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|-----------|
| R-1 | Project Owner does not approve BA-DEC-001 | Low | High | Escalate immediately; do not start restructuring |
| R-2 | ADR extraction misses content from original draft | Medium | Low | Cross-check BA-DEC-001 Section 3.3 checklist |
| R-3 | BA-ARCH-001 retains volatile content | Medium | Medium | Review against BA-DEC-001 Section 3.1 checklist |
| R-4 | BA-IMPL-001 format diverges from project implementation plan pattern | Medium | Low | Compare with `wp33-implementation-plan.md` and `wp42-implementation-plan.md` |
| R-5 | PLAN.md update conflicts with existing content | Low | Medium | Review existing Section 10.1 and 12.3 before editing |
| R-6 | Restructuring creates confusion about which document to reference | Low | Low | Clear document headers and cross-references |

---

## 8. Validation Checklist

Before declaring execution complete, verify:

- [ ] `BA-ARCH-001` exists and contains only architectural content per BA-DEC-001 Section 3.1
- [ ] `BA-IMPL-001` exists and contains only implementation + operations content per BA-DEC-001 Section 3.2
- [ ] Three ADR files extracted to `.kilo/plans/` following project ADR format
- [ ] `BA-ARCH-001` Section 25 replaced with ADR index table (not full ADR text)
- [ ] No operational security procedures (`.env` handling, CI secrets) remain in `BA-ARCH-001`
- [ ] No specific package names, config parameter values, or detailed directory trees remain in `BA-ARCH-001`
- [ ] `PLAN.md` records the restructuring decision
- [ ] Project Owner approval obtained
- [ ] No `BA-OPS-001` file created
- [ ] No governance amendments required or made

---

## 9. Blockers and Escalation

| Condition | Action |
|-----------|--------|
| Project Owner approval not obtained | Stop; escalate to Project Owner; do not proceed |
| Governance amendment required | Stop; escalate to Architect; amendment process per `PROJECT_EXECUTION_RULES.md` Section 21 |
| Content boundary dispute (what stays vs moves) | Stop; escalate to Architect; reference BA-DEC-001 Section 3.1 and 3.2 |
| ADR format disagreement | Resolve by matching existing `ADR-0001-shipments-legacy-columns.md` format |

---

## 10. Compliance Matrix

| Governance Requirement | How This Plan Satisfies It |
|------------------------|---------------------------|
| `PLAN.md` 10.1: Record changes first | Step 1: PLAN.md updated before any document restructuring |
| `PLAN.md` 10.11: ADL for architectural changes | Step 2: ADRs extracted to standalone files |
| `PLAN.md` 11.1 Rule 10: Document major decisions | BA-DEC-001 is the documented decision; this plan executes it |
| `PROJECT_EXECUTION_RULES.md` 21: Project Owner approval | Step 1: Explicit approval gate |
| `PLAN.md` 9.14: Documentation describes reality | Two-document structure matches existing project WP pattern |
| `PLAN.md` 9.4: Reuse > Duplicate, Consistency > Cleverness | BA-IMPL-001 reuses existing implementation plan format; no new artifact class |

---

## 11. Post-Execution Next Step

After this plan is executed and documents are approved:
1. Browser Automation Platform moves to implementation phase
2. A new Work Package (WP-BA-001 or equivalent) is created per standard project process
3. BA-IMPL-001 serves as the implementation plan for that Work Package

---

**Plan Status:** Ready for Execution
**Approval Required:** Project Owner (per BA-DEC-001)
**Execution Sequence:** Steps 1 → 2 → 3 → 4 → 5 → 6
**Blocking Dependencies:** Step 1 (Project Owner approval + PLAN.md recording)
