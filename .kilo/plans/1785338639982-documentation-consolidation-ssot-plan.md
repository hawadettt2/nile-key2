# Architecture Consolidation Plan — Documentation SSOT

**Plan:** Documentation Consolidation & Single Source of Truth (SSOT)  
**Date:** 2026-07-29  
**Authority:** EARP-001 Executive Architecture Decision (EAD)  
**Constraint:** No code changes. No architectural decision changes. No document deletion.  

---

## 1. Executive Summary

The project currently has 50+ Markdown documents across root, `docs/`, `docs/architecture/`, and `.kilo/plans/`. Multiple documents declare themselves authoritative, contain overlapping content, or are superseded. Despite `PLAN.md` declaring itself the "Master Roadmap v2.1 — Single Source of Truth" in over 100 cross-references, the actual document landscape violates SSOT principles through duplication, drift, and unclear authority chains.

This plan defines a phased consolidation to make the actual document structure match the declared SSOT intent. The target is a clean, maintainable, non-redundant documentation hierarchy where every document has a single clear purpose, and `PLAN.md` is the true Single Source of Truth.

**Key Decision:** Keep `PLAN.md` as the Master Document filename. Restructure its content in place to eliminate bloat and clarify sections. Preserve backward compatibility with 100+ existing references.

---

## 2. Current State Assessment

### 2.1 Document Inventory

| # | Document | Location | Current Role | Issues |
|---|----------|----------|--------------|--------|
| 1 | PLAN.md | Root | De facto Master | 1246 lines, bloated, mixes strategy with execution details |
| 2 | README.md | Root | Project overview | Derived from PLAN.md; risk of drift |
| 3 | CURRENT_STATUS.md | Root | Live status tracking | Subordinate to PLAN.md; dynamic content |
| 4 | TECH_DEBT.md | Root | Debt register | Subordinate to PLAN.md |
| 5 | CHANGELOG.md | Root | Version history | Standalone; references PLAN.md |
| 6 | ARCHITECTURE_CHARTER.md | Root | Governance | Explicitly says content merged into PLAN.md; still exists |
| 7 | PROJECT_BASELINE_AFTER_WP21.md | Root | Baseline snapshot | Overlaps with CURRENT_STATUS.md and PLAN.md |
| 8 | WORKFLOW.md | Root | Workflow definitions | May overlap with PLAN.md Section 9 |
| 9 | INSTRUCTIONS.md | Root | Operational instructions | May overlap with PLAN.md execution rules |
| 10 | PROJECT_RULES.md | Root | Execution rules | Likely overlaps with PLAN.md Section 9 |
| 11 | DEPLOYMENT.md | Root | Deployment guide | Derived from PLAN.md |
| 12 | WP-15_FINAL_VERIFICATION.md | Root | Historical verification | Timestamped; historical |
| 13 | WP21_M5_StageA_Baseline_Verification_Report.md | Root | Historical report | Timestamped; historical |
| 14 | WP21_M5_StageB_Gap_Analysis_Remediation_Plan.md | Root | Historical plan | Timestamped; historical |
| 15 | WP21_M5_StageC_Implementation_Plan.md | Root | Historical plan | Timestamped; historical |
| 16 | UAT_CHECKLIST.md | docs/ | UAT checklist | Execution detail; may be appendix |
| 17 | PROJECT_EXECUTION_RULES.md | docs/ | Execution rules | May overlap with PLAN.md Section 9 |
| 18 | OV-001-stage-6-ux-manual.md | docs/ | UX manual | Execution detail; may be appendix |
| 19 | OV-001-stage-8-final-review.md | docs/ | Historical review | Timestamped; historical |
| 20 | ENGINEERING_MEMORY.md | docs/architecture/ | Decision Log | Standalone reference; authority = PLAN.md |
| 21 | WORK_PACKAGE_PLAN.md | docs/architecture/ | WP lifecycle order | 1129 lines; based on PLAN.md; duplicate risk |
| 22 | PROJECT_BASELINE.md | docs/architecture/ | Baseline reference | Overlaps with CURRENT_STATUS.md |
| 23 | FINAL_BASELINE.md | docs/architecture/ | Final baseline | Overlaps with PROJECT_BASELINE_AFTER_WP21.md |
| 24 | BASELINE_SUMMARY.md | docs/architecture/ | Baseline summary | Overlaps with other baselines |
| 25 | REPOSITORY_INTELLIGENCE.md | docs/architecture/ | Historical snapshot | Explicitly says authority moved to PLAN.md |
| 26 | WP-02_COMPLETION_REPORT.md | docs/architecture/ | Completion report | Execution detail; may be appendix |
| 27 | ADR-0001-shipments-legacy-columns.md | docs/architecture/ | Architecture Decision | Standalone reference |
| 28 | executive-architecture-vision.md | .kilo/plans/earp-001/ | EARP-001 governance | Standalone package |
| 29 | EAD.md | .kilo/plans/earp-001/ | EARP-001 governance | Standalone package |
| 30 | architecture-refactoring-change-log.md | .kilo/plans/earp-001/ | EARP-001 change log | Standalone package |
| 31 | earp-001 README.md | .kilo/plans/earp-001/ | EARP-001 nav | Standalone package |
| 32 | ED-WP30-001.md | .kilo/plans/ | Engineering Decision | Standalone reference |
| 33 | ED-WP30-002.md | .kilo/plans/ | Engineering Decision | Standalone reference |
| 34 | ED-WP32-001.md | .kilo/plans/ | Engineering Decision | Standalone reference |
| 35 | MEMORY_CONTRACT.md | .kilo/plans/ | Contract | Standalone reference |
| 36 | KNOWLEDGE_INGESTION_CONTRACT.md | .kilo/plans/ | Contract | Standalone reference |
| 37 | AVATAR_CONTRACT.md | .kilo/plans/ | Contract | Standalone reference |
| 38 | BA-ARCH-001.md | .kilo/plans/ | Business Architecture | Standalone reference |
| 39 | BA-IMPL-001.md | .kilo/plans/ | Implementation plan | Standalone reference |
| 40 | BA-WP-001.md | .kilo/plans/ | Work Package plan | Standalone reference |
| 41 | BA-ARCH-001-ADR-001.md | .kilo/plans/ | ADR | Standalone reference |
| 42 | BA-ARCH-001-ADR-002.md | .kilo/plans/ | ADR | Standalone reference |
| 43 | BA-ARCH-001-ADR-003.md | .kilo/plans/ | ADR | Standalone reference |
| 44 | WP-30I-spec.md | .kilo/plans/ | Specification | Standalone reference |
| 45 | WP-32-spec.md | .kilo/plans/ | Specification | Standalone reference |
| 46 | WP-33-spec.md | .kilo/plans/ | Specification | Standalone reference |
| 47 | WP-41-spec.md | .kilo/plans/ | Specification | Standalone reference |
| 48 | WP-42-spec.md | .kilo/plans/ | Specification | Standalone reference |
| 49 | wp30-implementation-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 50 | wp31-implementation-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 51 | wp32-implementation-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 52 | wp33-implementation-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 53 | wp21-platform-integration-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 54 | wp30d-reasoning-engine-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 55 | wp30-digital-export-manager-architecture.md | .kilo/plans/ | Architecture doc | Superseded by EAD |
| 56 | wp31-forensic-audit-and-correction-plan.md | .kilo/plans/ | Audit plan | Timestamped; historical |
| 57 | wp32-knowledge-graph-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 58 | wp40-planning-and-governance-report.md | .kilo/plans/ | Governance report | Timestamped; historical |
| 59 | wp42-implementation-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 60 | wp42-uat-deferral-plan.md | .kilo/plans/ | UAT plan | Timestamped; historical |
| 61 | wp42-owner-acceptance-certificate.md | .kilo/plans/ | UAT evidence | Timestamped; historical |
| 62 | wp42-uat-runbook.md | .kilo/plans/ | UAT runbook | Execution detail; appendix |
| 63 | wp42-uat-session-schedule.md | .kilo/plans/ | UAT schedule | Execution detail; appendix |
| 64 | wp33e-final-roadmap-verification.md | .kilo/plans/ | Verification report | Timestamped; historical |
| 65 | wp40f-final-closure-and-baseline-verification.md | .kilo/plans/ | Verification report | Timestamped; historical |
| 66 | wp41-documentation-verification-report.md | .kilo/plans/ | Verification report | Timestamped; historical |
| 67 | browser-automation-docs-restructuring.md | .kilo/plans/ | Historical plan | Timestamped; historical |
| 68 | browser-automation-final-audit.md | .kilo/plans/ | Historical audit | Timestamped; historical |
| 69 | manual-uat-execution-package.md | .kilo/plans/ | UAT package | Timestamped; historical |
| 70 | phase5-frontend-pages-audit.md | .kilo/plans/ | Audit report | Timestamped; historical |
| 71 | uat-closure-execution-package.md | .kilo/plans/ | UAT closure | Timestamped; historical |
| 72 | project-closure-recovery-plan-v1.2.md | .kilo/plans/ | Recovery plan | Timestamped; historical |
| 73 | project-stabilization-plan.md | .kilo/plans/ | Stabilization plan | Timestamped; historical |
| 74 | shipping-engine-plan.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 75 | minimal-refactor-stage2.md | .kilo/plans/ | Refactor plan | Timestamped; historical |
| 76 | wp17-test-coverage-expansion.md | .kilo/plans/ | Test plan | Timestamped; historical |
| 77 | wp17a-api-test-coverage.md | .kilo/plans/ | Test plan | Timestamped; historical |
| 78 | wp17b-service-layer-unit-tests.md | .kilo/plans/ | Test plan | Timestamped; historical |
| 79 | wp18-production-readiness.md | .kilo/plans/ | Implementation plan | Timestamped; historical |
| 80 | 1782941896877-wp08-execution-plan.md | .kilo/plans/ | Execution plan | Timestamped; historical |
| 81 | 1783128677721-wp08-execution-plan.md | .kilo/plans/ | Execution plan | Timestamped; historical |
| 82 | 1783138634123-wp09-execution-plan.md | .kilo/plans/ | Execution plan | Timestamped; historical |
| 83 | 1783259473425-wp17-test-coverage-expansion.md | .kilo/plans/ | Duplicate of #76 | Redundant |
| 84 | 1783259473425-wp17a-api-test-coverage.md | .kilo/plans/ | Duplicate of #77 | Redundant |
| 85 | 1783259473425-wp17b-service-layer-unit-tests.md | .kilo/plans/ | Duplicate of #78 | Redundant |
| 86 | 1783388583926-wp18-production-readiness.md | .kilo/plans/ | Duplicate of #79 | Redundant |
| 87 | 1783388583927-project-closure-recovery-plan-v1.2.md | .kilo/plans/ | Duplicate of #72 | Redundant |
| 88 | 1783474903226-project-stabilization-plan.md | .kilo/plans/ | Duplicate of #73 | Redundant |
| 89 | 1783879837991-shipping-engine-plan.md | .kilo/plans/ | Duplicate of #75 | Redundant |
| 90 | 1783879837991-wp21-platform-integration-roadmap.md | .kilo/plans/ | Duplicate of #53 | Redundant |
| 91 | 1784024628892-wp21-m4-export-operations.md | .kilo/plans/ | Historical plan | Timestamped; historical |
| 92 | 1784079736812-wp30-architecture-compliance-review.md | .kilo/plans/ | Compliance review | Superseded by EAD |
| 93 | 1784079736812-wp30d-reasoning-engine-plan.md | .kilo/plans/ | Duplicate of #54 | Redundant |
| 94 | 1784089363000-wp30-digital-export-manager-architecture.md | .kilo/plans/ | Superseded by EAD | Redundant |
| 95 | 1784207193717-wp31-forensic-audit-and-correction-plan.md | .kilo/plans/ | Duplicate of #56 | Redundant |
| 96 | 1784505859302-wp32-knowledge-graph-plan.md | .kilo/plans/ | Duplicate of #57 | Redundant |
| 97 | 1784644008165-wp40-planning-and-governance-report.md | .kilo/plans/ | Duplicate of #58 | Redundant |
| 98 | 1784690072071-browser-automation-docs-restructuring.md | .kilo/plans/ | Duplicate of #67 | Redundant |
| 99 | 1784690190387-browser-automation-final-audit.md | .kilo/plans/ | Duplicate of #68 | Redundant |
| 100 | 1784780019692-wp42-uat-deferral-plan.md | .kilo/plans/ | Duplicate of #60 | Redundant |
| 101 | 1785014994692-uat-closure-execution-package.md | .kilo/plans/ | Duplicate of #71 | Redundant |
| 102 | wp42-uat-evidence/ | .kilo/plans/ | UAT evidence directory | Historical artifacts |
| 103 | AGENTS.md | Root | Kilo config | Tool config; not planning doc |
| 104 | AGENTS.md | .kilo/ | Kilo config | Tool config; not planning doc |

**Total:** 104 entries. Many are timestamped duplicates or historical execution plans.

### 2.2 Key Problems Identified

1. **Duplicate Timestamped Files:** Files like `1783388583926-wp18-production-readiness.md` and `wp18-production-readiness.md` are duplicates.
2. **Superseded Documents Still Present:** `ARCHITECTURE_CHARTER.md` claims merged into PLAN.md but still exists at root.
3. **Baseline Document Proliferation:** 4 baseline documents (`PROJECT_BASELINE.md`, `FINAL_BASELINE.md`, `BASELINE_SUMMARY.md`, `PROJECT_BASELINE_AFTER_WP21.md`) overlap with each other and with `CURRENT_STATUS.md`.
4. **Execution Plan Proliferation:** 30+ timestamped execution plans in `.kilo/plans/` clutter the planning directory.
5. **WORK_PACKAGE_PLAN.md Bloat:** 1129 lines of detailed WP breakdowns derived from PLAN.md but maintained separately, creating drift risk.
6. **Unclear Authority Chains:** Multiple documents claim authority or reference PLAN.md inconsistently.

---

## 3. Classification Scheme

Apply exactly one classification to each document:

| Classification | Definition | Count |
|----------------|------------|-------|
| **Master Document** | The Single Source of Truth. One document only. | 1 |
| **Merge into Master** | Current authoritative content that should be incorporated into the Master Document, then archived. | 12 |
| **Appendix** | Long execution details, checklists, or evidence that is still referenced but too verbose for the master. | 8 |
| **Standalone Reference** | Decisions, contracts, specs, or governance packages that must remain independent. | 18 |
| **Historical Archive** | Superseded execution plans, audit reports, and snapshots. Move to archive, do not delete. | 48 |
| **Out of Scope** | Tool configs or non-planning documents. | 2 |

---

## 4. Classification Details

### 4.1 Master Document

| Document | Rationale |
|----------|-----------|
| **`PLAN.md`** | Already declared "Master Roadmap v2.1 — Single Source of Truth" in 100+ references. Contains architecture, execution rules, work package registry, and governance. Restructure in place. |

### 4.2 Merge into Master (Content Absorption)

These documents contain authoritative information that should be incorporated into `PLAN.md` to eliminate duplication, then archived.

| # | Document | Content to Merge | Merge Target Section in PLAN.md |
|---|----------|------------------|--------------------------------|
| 1 | `ARCHITECTURE_CHARTER.md` | Architecture principles | Section 9 (Architecture Principles) |
| 2 | `docs/architecture/WORK_PACKAGE_PLAN.md` | Detailed WP lifecycle breakdowns (1129 lines) | Section 15 (Work Package Registry) — as expanded detail |
| 3 | `docs/architecture/PROJECT_BASELINE.md` | Baseline state, accepted deviations | Section 16 (Baseline & State) |
| 4 | `docs/architecture/FINAL_BASELINE.md` | Final baseline snapshot | Section 16 (Baseline & State) |
| 5 | `docs/architecture/BASELINE_SUMMARY.md` | Baseline summary | Section 16 (Baseline & State) |
| 6 | `PROJECT_BASELINE_AFTER_WP21.md` | Post-WP-21 baseline | Section 16 (Baseline & State) |
| 7 | `docs/architecture/REPOSITORY_INTELLIGENCE.md` | Historical repository state | Section 17 (Repository Intelligence) |
| 8 | `docs/PROJECT_EXECUTION_RULES.md` | Execution rules | Section 9 (Architecture Principles / Execution Rules) |
| 9 | `WORKFLOW.md` | Workflow definitions | Section 9 or dedicated Section 18 |
| 10 | `INSTRUCTIONS.md` | Operational instructions | Section 9 (Execution Rules) |
| 11 | `DEPLOYMENT.md` | Deployment guide | Section 19 (Deployment & Operations) |
| 12 | `PROJECT_RULES.md` | Project rules | Section 9 (Execution Rules) |

### 4.3 Appendices (Long Content, Still Referenced)

These documents contain long-form execution details that are still actively referenced but would bloat the master if inlined.

| # | Document | Rationale |
|---|----------|-----------|
| 1 | `docs/UAT_CHECKLIST.md` | Long checklist; referenced by WP-42 |
| 2 | `docs/OV-001-stage-6-ux-manual.md` | UX manual; execution detail |
| 3 | `.kilo/plans/wp42-uat-runbook.md` | UAT runbook; execution detail |
| 4 | `.kilo/plans/wp42-uat-session-schedule.md` | UAT schedule; execution detail |
| 5 | `.kilo/plans/wp42-owner-acceptance-certificate.md` | UAT evidence; append after closure |
| 6 | `.kilo/plans/wp33e-final-roadmap-verification.md` | Verification report; appendix |
| 7 | `.kilo/plans/wp40f-final-closure-and-baseline-verification.md` | Verification report; appendix |
| 8 | `.kilo/plans/wp41-documentation-verification-report.md` | Verification report; appendix |

**Target:** Move to `docs/appendices/` and reference from `PLAN.md` Section 20 (References).

### 4.4 Standalone References (Never Merge)

These documents represent immutable decisions, contracts, or governance packages. They must remain independent and be referenced by ID from the Master.

| # | Document | Rationale |
|---|----------|-----------|
| 1 | `CURRENT_STATUS.md` | Live project state; dynamic; subordinate but not mergeable |
| 2 | `TECH_DEBT.md` | Live debt register; dynamic |
| 3 | `CHANGELOG.md` | Project version history |
| 4 | `docs/architecture/ENGINEERING_MEMORY.md` | Engineering Decisions Log; standalone reference |
| 5 | `docs/architecture/ADR-0001-shipments-legacy-columns.md` | Architecture Decision Record |
| 6 | `.kilo/plans/ED-WP30-001.md` | Engineering Decision |
| 7 | `.kilo/plans/ED-WP30-002.md` | Engineering Decision |
| 8 | `.kilo/plans/ED-WP32-001.md` | Engineering Decision |
| 9 | `.kilo/plans/MEMORY_CONTRACT.md` | Contract |
| 10 | `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md` | Contract |
| 11 | `.kilo/plans/AVATAR_CONTRACT.md` | Contract |
| 12 | `.kilo/plans/BA-ARCH-001.md` | Business Architecture |
| 13 | `.kilo/plans/BA-IMPL-001.md` | Business Architecture Implementation |
| 14 | `.kilo/plans/BA-WP-001.md` | Business Architecture Work Package |
| 15 | `.kilo/plans/BA-ARCH-001-ADR-001.md` | Business Architecture ADR |
| 16 | `.kilo/plans/BA-ARCH-001-ADR-002.md` | Business Architecture ADR |
| 17 | `.kilo/plans/BA-ARCH-001-ADR-003.md` | Business Architecture ADR |
| 18 | `.kilo/plans/WP-30I-spec.md` | Specification |
| 19 | `.kilo/plans/WP-32-spec.md` | Specification |
| 20 | `.kilo/plans/WP-33-spec.md` | Specification |
| 21 | `.kilo/plans/WP-41-spec.md` | Specification |
| 22 | `.kilo/plans/WP-42-spec.md` | Specification |
| 23 | `.kilo/plans/earp-001/` (entire package) | EARP-001 governance package (EAD, Vision, Change Log, README) |

### 4.5 Historical Archive (Move, Do Not Delete)

All timestamped execution plans, completed verification reports, and superseded snapshots. Move to `.kilo/plans/archive/`.

| # | Document | Rationale |
|---|----------|-----------|
| 1 | `WP-15_FINAL_VERIFICATION.md` | Completed WP verification |
| 2 | `WP21_M5_StageA_Baseline_Verification_Report.md` | Completed stage report |
| 3 | `WP21_M5_StageB_Gap_Analysis_Remediation_Plan.md` | Completed stage plan |
| 4 | `WP21_M5_StageC_Implementation_Plan.md` | Completed stage plan |
| 5 | `docs/OV-001-stage-8-final-review.md` | Completed review |
| 6 | `docs/OV-001-stage-6-ux-manual.md` | Completed UX manual |
| 7 | All `1784...` prefixed files in `.kilo/plans/` | Timestamped execution plans |
| 8 | `.kilo/plans/wp42-uat-evidence/` | UAT evidence directory |
| 9 | `.kilo/plans/wp30-implementation-plan.md` | Superseded by EAD |
| 10 | `.kilo/plans/wp31-implementation-plan.md` | Superseded |
| 11 | `.kilo/plans/wp32-implementation-plan.md` | Superseded |
| 12 | `.kilo/plans/wp33-implementation-plan.md` | Superseded |
| 13 | `.kilo/plans/wp21-platform-integration-plan.md` | Superseded |
| 14 | `.kilo/plans/wp30d-reasoning-engine-plan.md` | Superseded |
| 15 | `.kilo/plans/wp30-digital-export-manager-architecture.md` | Superseded by EAD |
| 16 | `.kilo/plans/wp31-forensic-audit-and-correction-plan.md` | Superseded |
| 17 | `.kilo/plans/wp32-knowledge-graph-plan.md` | Superseded |
| 18 | `.kilo/plans/wp40-planning-and-governance-report.md` | Superseded |
| 19 | `.kilo/plans/wp42-implementation-plan.md` | Superseded |
| 20 | `.kilo/plans/wp42-uat-deferral-plan.md` | Superseded |
| 21 | `.kilo/plans/wp42-owner-acceptance-certificate.md` | Superseded |
| 22 | `.kilo/plans/wp33e-final-roadmap-verification.md` | Superseded |
| 23 | `.kilo/plans/wp40f-final-closure-and-baseline-verification.md` | Superseded |
| 24 | `.kilo/plans/wp41-documentation-verification-report.md` | Superseded |
| 25 | `.kilo/plans/browser-automation-docs-restructuring.md` | Superseded |
| 26 | `.kilo/plans/browser-automation-final-audit.md` | Superseded |
| 27 | `.kilo/plans/manual-uat-execution-package.md` | Superseded |
| 28 | `.kilo/plans/phase5-frontend-pages-audit.md` | Superseded |
| 29 | `.kilo/plans/uat-closure-execution-package.md` | Superseded |
| 30 | `.kilo/plans/project-closure-recovery-plan-v1.2.md` | Superseded |
| 31 | `.kilo/plans/project-stabilization-plan.md` | Superseded |
| 32 | `.kilo/plans/shipping-engine-plan.md` | Superseded |
| 33 | `.kilo/plans/minimal-refactor-stage2.md` | Superseded |
| 34 | `.kilo/plans/wp17-test-coverage-expansion.md` | Superseded |
| 35 | `.kilo/plans/wp17a-api-test-coverage.md` | Superseded |
| 36 | `.kilo/plans/wp17b-service-layer-unit-tests.md` | Superseded |
| 37 | `.kilo/plans/wp18-production-readiness.md` | Superseded |
| 38 | `.kilo/plans/1782941896877-wp08-execution-plan.md` | Duplicate/timestamped |
| 39 | `.kilo/plans/1783008392560-minimal-refactor-stage2.md` | Duplicate/timestamped |
| 40 | `.kilo/plans/1783128677721-wp08-execution-plan.md` | Duplicate/timestamped |
| 41 | `.kilo/plans/1783138634123-wp09-execution-plan.md` | Duplicate/timestamped |
| 42 | `.kilo/plans/1783259473425-wp17-test-coverage-expansion.md` | Duplicate/timestamped |
| 43 | `.kilo/plans/1783259473425-wp17a-api-test-coverage.md` | Duplicate/timestamped |
| 44 | `.kilo/plans/1783259473425-wp17b-service-layer-unit-tests.md` | Duplicate/timestamped |
| 45 | `.kilo/plans/1783355240374-manual-uat-execution-package.md` | Duplicate/timestamped |
| 46 | `.kilo/plans/1783388583926-wp18-production-readiness.md` | Duplicate/timestamped |
| 47 | `.kilo/plans/1783388583927-project-closure-recovery-plan-v1.2.md` | Duplicate/timestamped |
| 48 | `.kilo/plans/1783474903226-project-stabilization-plan.md` | Duplicate/timestamped |
| 49 | `.kilo/plans/1783879837991-shipping-engine-plan.md` | Duplicate/timestamped |
| 50 | `.kilo/plans/1783879837991-wp21-platform-integration-roadmap.md` | Duplicate/timestamped |
| 51 | `.kilo/plans/1784024628892-wp21-m4-export-operations.md` | Timestamped |
| 52 | `.kilo/plans/1784079736812-wp30-architecture-compliance-review.md` | Superseded by EAD |
| 53 | `.kilo/plans/1784079736812-wp30d-reasoning-engine-plan.md` | Duplicate/timestamped |
| 54 | `.kilo/plans/1784089363000-wp30-digital-export-manager-architecture.md` | Superseded by EAD |
| 55 | `.kilo/plans/1784207193717-wp31-forensic-audit-and-correction-plan.md` | Duplicate/timestamped |
| 56 | `.kilo/plans/1784505859302-wp32-knowledge-graph-plan.md` | Duplicate/timestamped |
| 57 | `.kilo/plans/1784644008165-wp40-planning-and-governance-report.md` | Duplicate/timestamped |
| 58 | `.kilo/plans/1784690072071-browser-automation-docs-restructuring.md` | Duplicate/timestamped |
| 59 | `.kilo/plans/1784690190387-browser-automation-final-audit.md` | Duplicate/timestamped |
| 60 | `.kilo/plans/1784780019692-wp42-uat-deferral-plan.md` | Duplicate/timestamped |
| 61 | `.kilo/plans/1785014994692-uat-closure-execution-package.md` | Duplicate/timestamped |

**Note:** The `1784...` prefixed files and their non-prefixed counterparts are duplicates. Both versions are archived; the non-prefixed versions are kept as canonical historical names within the archive.

### 4.6 Out of Scope

| Document | Rationale |
|----------|-----------|
| `AGENTS.md` (root) | Kilo agent configuration, not project planning |
| `.kilo/AGENTS.md` | Kilo agent configuration, not project planning |
| `backend/` code files | Not documentation |
| `frontend/` code files | Not documentation |

---

## 5. Target SSOT Structure

### 5.1 Master Document: `PLAN.md`

Restructure `PLAN.md` in place. Proposed section order:

```
PLAN.md
├── Section 1: Executive Summary
├── Section 2: Executive Architecture Vision
│   (absorbed from .kilo/plans/earp-001/executive-architecture-vision.md)
├── Section 3: Product Identity & Platform Definition
├── Section 4: System Architecture
│   ├── 4.1 Layers
│   ├── 4.2 Bounded Contexts
│   ├── 4.3 Boundaries & Invariants
│   └── 4.4 ERP Isolation
├── Section 5: Naming Policy & Terminology
│   (absorbed from EAD Decision 9.1/9.2/9.3)
├── Section 6: Work Package Registry
│   ├── 6.1 WP Summary Table
│   ├── 6.2 WP-01 through WP-42 Detail
│   └── 6.3 Dependencies & Sequencing
│   (expanded from docs/architecture/WORK_PACKAGE_PLAN.md)
├── Section 7: Current Status Dashboard
│   (absorbed from CURRENT_STATUS.md summary tables)
├── Section 8: Execution Rules & Governance
│   (absorbed from PROJECT_RULES.md, PROJECT_EXECUTION_RULES.md, WORKFLOW.md, INSTRUCTIONS.md)
├── Section 9: Architecture Principles
│   (absorbed from ARCHITECTURE_CHARTER.md)
├── Section 10: Baseline & State
│   (absorbed from PROJECT_BASELINE.md, FINAL_BASELINE.md, BASELINE_SUMMARY.md, PROJECT_BASELINE_AFTER_WP21.md)
├── Section 11: Repository Intelligence
│   (absorbed from docs/architecture/REPOSITORY_INTELLIGENCE.md)
├── Section 12: Deployment & Operations
│   (absorbed from DEPLOYMENT.md)
├── Section 13: Technical Debt
│   (absorbed from TECH_DEBT.md)
├── Section 14: Changelog Summary
│   (index only; full detail remains in CHANGELOG.md)
├── Section 15: Decision Index
│   (links to EDs, ADRs, EADs, EARP-001 package)
├── Section 16: Contract Index
│   (links to contracts)
├── Section 17: Appendix References
│   (links to appendices in docs/appendices/)
└── Section 18: Document Authority Map
    (replaces current Section 20)
```

### 5.2 Target Directory Structure

```
F:\nilekey\nile-key-project\nile-key2\
├── README.md                          # Project overview, quickstart, SSOT link
├── PLAN.md                            # MASTER — Single Source of Truth
├── CURRENT_STATUS.md                  # Standalone — live status
├── TECH_DEBT.md                       # Standalone — debt register
├── CHANGELOG.md                       # Standalone — version history
├── ARCHITECTURE_CHARTER.md            # ARCHIVED → .kilo/plans/archive/
├── PROJECT_BASELINE_AFTER_WP21.md     # MERGED into PLAN.md, then archived
├── WORKFLOW.md                        # MERGED into PLAN.md, then archived
├── INSTRUCTIONS.md                    # MERGED into PLAN.md, then archived
├── PROJECT_RULES.md                   # MERGED into PLAN.md, then archived
├── DEPLOYMENT.md                      # MERGED into PLAN.md, then archived
├── WP-15_FINAL_VERIFICATION.md        # ARCHIVED
├── WP21_M5_Stage*.md                  # ARCHIVED
├── docs/
│   ├── architecture/
│   │   ├── ENGINEERING_MEMORY.md      # Standalone — Decision Log
│   │   ├── WORK_PACKAGE_PLAN.md       # MERGED into PLAN.md, then archived
│   │   ├── PROJECT_BASELINE.md        # MERGED into PLAN.md, then archived
│   │   ├── FINAL_BASELINE.md          # MERGED into PLAN.md, then archived
│   │   ├── BASELINE_SUMMARY.md        # MERGED into PLAN.md, then archived
│   │   ├── REPOSITORY_INTELLIGENCE.md # MERGED into PLAN.md, then archived
│   │   ├── WP-02_COMPLETION_REPORT.md # APPENDIX
│   │   └── ADR-0001-shipments-legacy-columns.md # Standalone
│   ├── appendices/
│   │   ├── UAT_CHECKLIST.md           # Appendix
│   │   ├── OV-001-stage-6-ux-manual.md # Appendix
│   │   ├── wp42-uat-runbook.md        # Appendix
│   │   ├── wp42-uat-session-schedule.md # Appendix
│   │   ├── wp42-owner-acceptance-certificate.md # Appendix
│   │   ├── wp33e-final-roadmap-verification.md # Appendix
│   │   ├── wp40f-final-closure-and-baseline-verification.md # Appendix
│   │   └── wp41-documentation-verification-report.md # Appendix
│   ├── UAT_CHECKLIST.md               # MOVED to appendices/
│   ├── PROJECT_EXECUTION_RULES.md     # MERGED into PLAN.md, then archived
│   ├── OV-001-stage-8-final-review.md # ARCHIVED
│   └── OV-001-stage-6-ux-manual.md    # MOVED to appendices/
└── .kilo/
    └── plans/
        ├── earp-001/                   # Standalone governance package
        ├── archive/                    # HISTORICAL ARCHIVE
        │   ├── 1784*-prefixed-files/
        │   ├── wp*-execution-plans/
        │   ├── wp*-verification-reports/
        │   ├── wp*-audit-reports/
        │   └── wp42-uat-evidence/
        ├── ED-*.md                     # Standalone references
        ├── *-spec.md                   # Standalone references
        ├── *-contract.md               # Standalone references
        └── BA-*.md, ADR-*.md           # Standalone references
```

---

## 6. Migration Map

### 6.1 Master Document Restructure (`PLAN.md`)

| Phase | Action | Content Source | Validation |
|-------|--------|----------------|------------|
| 1 | Reorganize existing sections | Internal restructure | Section count, heading hierarchy |
| 2 | Merge `ARCHITECTURE_CHARTER.md` | Absorb Section 9 content | Cross-reference check |
| 3 | Merge `WORK_PACKAGE_PLAN.md` | Expand Section 15 | WP count, validation steps |
| 4 | Merge baselines | Absorb into Section 10 | Baseline state consistency |
| 5 | Merge execution rules | Absorb into Section 8 | Rule count, no duplicates |
| 6 | Merge `REPOSITORY_INTELLIGENCE.md` | Absorb into Section 11 | Historical accuracy |
| 7 | Add Decision & Contract Index | New Sections 15-16 | All ED/ADR/EAD/Contract IDs present |
| 8 | Add Appendix References | New Section 17 | All appendix links valid |

### 6.2 Document Moves

| Source | Destination | Action |
|--------|-------------|--------|
| `ARCHITECTURE_CHARTER.md` | `.kilo/plans/archive/` | Move after merge |
| `docs/architecture/WORK_PACKAGE_PLAN.md` | `.kilo/plans/archive/` | Move after merge |
| `docs/architecture/PROJECT_BASELINE.md` | `.kilo/plans/archive/` | Move after merge |
| `docs/architecture/FINAL_BASELINE.md` | `.kilo/plans/archive/` | Move after merge |
| `docs/architecture/BASELINE_SUMMARY.md` | `.kilo/plans/archive/` | Move after merge |
| `PROJECT_BASELINE_AFTER_WP21.md` | `.kilo/plans/archive/` | Move after merge |
| `docs/architecture/REPOSITORY_INTELLIGENCE.md` | `.kilo/plans/archive/` | Move after merge |
| `docs/PROJECT_EXECUTION_RULES.md` | `.kilo/plans/archive/` | Move after merge |
| `WORKFLOW.md` | `.kilo/plans/archive/` | Move after merge |
| `INSTRUCTIONS.md` | `.kilo/plans/archive/` | Move after merge |
| `DEPLOYMENT.md` | `.kilo/plans/archive/` | Move after merge |
| `PROJECT_RULES.md` | `.kilo/plans/archive/` | Move after merge |
| `docs/UAT_CHECKLIST.md` | `docs/appendices/UAT_CHECKLIST.md` | Move |
| `docs/OV-001-stage-6-ux-manual.md` | `docs/appendices/OV-001-stage-6-ux-manual.md` | Move |
| `.kilo/plans/wp42-uat-runbook.md` | `docs/appendices/wp42-uat-runbook.md` | Move |
| `.kilo/plans/wp42-uat-session-schedule.md` | `docs/appendices/wp42-uat-session-schedule.md` | Move |
| `.kilo/plans/wp42-owner-acceptance-certificate.md` | `docs/appendices/wp42-owner-acceptance-certificate.md` | Move |
| `.kilo/plans/wp33e-final-roadmap-verification.md` | `docs/appendices/wp33e-final-roadmap-verification.md` | Move |
| `.kilo/plans/wp40f-final-closure-and-baseline-verification.md` | `docs/appendices/wp40f-final-closure-and-baseline-verification.md` | Move |
| `.kilo/plans/wp41-documentation-verification-report.md` | `docs/appendices/wp41-documentation-verification-report.md` | Move |
| `docs/architecture/WP-02_COMPLETION_REPORT.md` | `docs/appendices/WP-02_COMPLETION_REPORT.md` | Move |
| All `1784*` and timestamped files | `.kilo/plans/archive/` | Move |
| `WP-15_FINAL_VERIFICATION.md` | `.kilo/plans/archive/` | Move |
| `WP21_M5_Stage*.md` | `.kilo/plans/archive/` | Move |
| `docs/OV-001-stage-8-final-review.md` | `.kilo/plans/archive/` | Move |
| All `wp*-implementation-plan.md` | `.kilo/plans/archive/` | Move |
| All `wp*-verification-report.md` | `.kilo/plans/archive/` | Move |
| All `browser-automation-*.md` | `.kilo/plans/archive/` | Move |
| `manual-uat-execution-package.md` | `.kilo/plans/archive/` | Move |
| `phase5-frontend-pages-audit.md` | `.kilo/plans/archive/` | Move |
| `uat-closure-execution-package.md` | `.kilo/plans/archive/` | Move |
| `project-closure-recovery-plan-v1.2.md` | `.kilo/plans/archive/` | Move |
| `project-stabilization-plan.md` | `.kilo/plans/archive/` | Move |
| `shipping-engine-plan.md` | `.kilo/plans/archive/` | Move |
| `minimal-refactor-stage2.md` | `.kilo/plans/archive/` | Move |
| `wp17-*.md` | `.kilo/plans/archive/` | Move |
| `wp18-production-readiness.md` | `.kilo/plans/archive/` | Move |
| `.kilo/plans/wp42-uat-evidence/` | `.kilo/plans/archive/wp42-uat-evidence/` | Move directory |

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Broken cross-references** | High | High | Before merging, scan all `.md` files for references to moved/archived documents. Update references to point to new locations or to `PLAN.md`. |
| **Information loss during merge** | Medium | High | Use content-preserving merge strategy: copy unique sections verbatim into `PLAN.md` before archiving originals. Maintain line-by-line audit trail. |
| **`PLAN.md` bloat beyond usability** | Medium | Medium | Keep master under 2000 lines. If content exceeds this, split into `PLAN.md` + `docs/appendices/`. Do not inline verbose completion reports. |
| **Resistance to renaming/moving files** | Low | Medium | Maintain backward-compatible redirects or index files in archive. Announce migration map before execution. |
| **Historical context lost** | Low | Medium | Archive all files in `.kilo/plans/archive/` with original filenames. Do not delete. Git history preserves all versions. |
| **Dynamic docs (CURRENT_STATUS.md, TECH_DEBT.md) accidentally merged** | Low | High | Explicitly exclude from merge list. Keep as standalone. |
| **Contracts/Decisions accidentally merged** | Low | High | Explicitly keep ED, EAD, ADR, Contract files as standalone references. |

---

## 8. Implementation Phases

### Phase 1: Preparation (No file changes)
- [ ] Publish this plan and obtain stakeholder approval.
- [ ] Create `docs/appendices/` directory.
- [ ] Create `.kilo/plans/archive/` directory.
- [ ] Run full cross-reference audit: identify all `[[doc]]`, `(doc)`, and relative-path references to target documents.

### Phase 2: Master Document Restructure
- [ ] Restructure `PLAN.md` into proposed section order.
- [ ] Merge `ARCHITECTURE_CHARTER.md` content into Section 9.
- [ ] Merge `WORK_PACKAGE_PLAN.md` key details into Section 15.
- [ ] Merge baseline documents into Section 10.
- [ ] Merge execution rules into Section 8.
- [ ] Merge `REPOSITORY_INTELLIGENCE.md` into Section 11.
- [ ] Add Decision Index (Section 15) and Contract Index (Section 16).
- [ ] Add Appendix References (Section 17).
- [ ] Validate: `PLAN.md` is still < 2000 lines. All unique content preserved.

### Phase 3: Appendix Migration
- [ ] Move appendix candidates from root and `.kilo/plans/` to `docs/appendices/`.
- [ ] Update `PLAN.md` Section 17 links to point to new appendix locations.

### Phase 4: Archive Migration
- [ ] Move all Historical Archive candidates to `.kilo/plans/archive/`.
- [ ] Preserve directory structure for `wp42-uat-evidence/`.
- [ ] Create `.kilo/plans/archive/README.md` explaining archive purpose and retention policy.

### Phase 5: Cross-Reference Update
- [ ] Update all remaining documents that reference archived/moved files.
- [ ] Update `README.md` authority map.
- [ ] Update `CURRENT_STATUS.md`, `TECH_DEBT.md`, `CHANGELOG.md` references if needed.
- [ ] Update `.kilo/plans/earp-001/README.md` if it references moved files.

### Phase 6: Validation
- [ ] Run link checker on all `.md` files.
- [ ] Verify no broken relative paths.
- [ ] Verify `PLAN.md` Section 20 (Document Authority Map) is accurate.
- [ ] Verify all decisions, contracts, and specs are still accessible.
- [ ] Verify git history is intact (all moves are git moves, not deletions).

---

## 9. Success Criteria

| Criterion | Metric | Target |
|-----------|--------|--------|
| **SSOT Declaration Matches Reality** | `PLAN.md` is the only document claiming master authority | 100% |
| **Duplicate Elimination** | No two active documents contain the same authoritative content | 0 duplicates |
| **Reference Integrity** | All internal `.md` links resolve | 100% |
| **Archive Completeness** | All superseded/timestamped files moved to archive | 100% |
| **Master Document Size** | `PLAN.md` remains readable | < 2000 lines |
| **Standalone Reference Integrity** | All EDs, EADs, ADRs, Contracts, Specs remain accessible | 100% |
| **Cross-Reference Accuracy** | All documents correctly reference `PLAN.md` or their actual authoritative source | 100% |
| **No Information Loss** | All architectural decisions, work package details, and governance rules preserved | 100% |
| **No Architectural Drift** | No architectural decisions modified during consolidation | 0 changes |
| **No Code Changes** | Zero source files modified | 0 files |

---

## 10. Open Questions / Decisions Required

| # | Question | Recommended Answer | Impact |
|---|----------|-------------------|--------|
| 1 | Should `PLAN.md` remain the master filename, or should it be renamed to `MASTER_PLAN.md`? | **Keep `PLAN.md`.** 100+ existing references. Renaming breaks backward compatibility and adds migration cost without SSOT benefit. | High |
| 2 | Should `WORK_PACKAGE_PLAN.md` detailed WP breakdowns be fully inlined into `PLAN.md`, or kept as an appendix? | **Inline summary tables into `PLAN.md`; move detailed validation steps to `docs/appendices/WORK_PACKAGE_PLAN.md`.** This keeps master readable while preserving detail. | Medium |
| 3 | Should `CURRENT_STATUS.md` and `TECH_DEBT.md` be kept as standalone, or converted to appendices? | **Keep standalone.** They are dynamic, frequently updated documents. Making them appendices would encourage editing the master for transient state. | Medium |
| 4 | Should the `1784*` timestamped files be preserved with their original names in the archive, or consolidated by content? | **Preserve original names.** Git history already captures timestamps. Renaming would obscure provenance. | Low |
| 5 | Should `docs/architecture/` be kept as a directory, or should architecture docs move to root or `docs/appendices/`? | **Keep `docs/architecture/` for standalone architecture references (ENGINEERING_MEMORY.md, ADRs).** Move merged/archived docs out. | Low |

---

## 11. Validation Gate

Before declaring consolidation complete:

1. **Inventory Check:** Run `find . -name "*.md" -not -path "./node_modules/*"` and verify every file is classified.
2. **Link Check:** Run a Markdown link checker against all `.md` files.
3. **Content Check:** Spot-check 5 randomly selected archived files to confirm they exist in `.kilo/plans/archive/` with original content.
4. **Authority Check:** Verify `PLAN.md` Section 20 (Document Authority Map) lists every remaining document with correct relationship.
5. **Drift Check:** Verify no architectural content was modified. Compare `PLAN.md` architecture sections against EAD and Executive Architecture Vision.

---

**Next Action:** Obtain approval for this plan, then proceed to Phase 1 (Preparation).
