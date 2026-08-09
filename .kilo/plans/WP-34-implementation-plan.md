# WP-34 Implementation Plan: External Research Capability

**Work Package:** WP-34 — External Research Capability  
**Status:** Draft — Pending Approval  
**Date:** 2026-08-09  
**Authority:** `PLAN.md` + `.kilo/plans/WP-34-spec.md` + `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Path:** `.kilo/plans/WP-34-implementation-plan.md`

---

## 1. الغرض

تنفيذ قدرة البحث الخارجي ككيان مستقل بحدود معمارية واضحة، مع ضمان تتبع المصادر والأدلة وعدم اختلاطه بـ Knowledge Ingestion أو Reasoning أو Planning.

---

## 2. نطاق المهام التنفيذية

### Task 1: Research Request Model & API Contract
**الهدف:** تعريف النموذج والواجهة التي تستقبل طلبات البحث.
**المخرجات:**
- Research Request model
- Research Result model
- Evidence/Source metadata models
**معايير الإنجاز:**
- نماذج منظمة تغطي: الهدف، النطاق، السياق، القيود
- واجهة واضحة للاستهلاك من الطبقات العليا
- لا توجد dépendances على مزودي بحث خارجيين محددين

---

### Task 2: Research Lifecycle Orchestration
**الهدف:** تنفيذ الـ lifecycle من الطلب إلى النتيجة المنظمة.
**المخرجات:**
- Research orchestrator
- Lifecycle stages (Planning → Discovery → Retrieval → Processing → Evidence Capture → Structuring)
**معايير الإنجاز:**
- كل مرحلة منفصلة وقابلة للاختبار
- فشل مصدر واحد لا يوقف البحث بالكامل
- نتائج جزئية ممكنة

---

### Task 3: Source Registry & Discovery
**الهدف:** إدارة مصادر خارجية واكتشافها.
**المخرجات:**
- Source registry interface
- Source discovery mechanism
**معايير الإنجاز:**
- المصادر مسجلة بمعرّف فريد واسم ونوع
- Discovery قادر على اختيار المصادر المناسبة حسب النطاق
- لا يوجد مزود محدد مسبقًا

---

### Task 4: Retrieval & Content Processing
**الهدف:** جلب المحتوى من المصادر وتحويله.
**المخرجات:**
- Retrieval abstraction
- Content processor
**معايير الإنجاز:**
- معالجة الأخطاء وال timeouts لكل مصدر
- تحويل المحتوى الخام إلى هيكل منظم
- تسجيل حالة الاسترجاع لكل مصدر

---

### Task 5: Evidence & Provenance Capture
**الهدف:** الحفاظ على تتبع المصدر والأدلة.
**المخرجات:**
- Evidence model
- Provenance tracker
**معايير الإنجاز:**
- كل نتيجة مرتبطة بمصدرها (معرّف، URL/مرجع، وقت الاسترجاع)
- قابلية التتبع من النتيجة إلى المصدر
- LLM-processed content مُعلّم ومرتبط بالمصدر

---

### Task 6: Result Structuring & Output
**الهدف:** إخراج نتيجة بحث منظمة للطبقات العليا.
**المخرجات:**
- Research Result structure
- Reasoning layer interface contract
**معايير الإنجاز:**
- النتيجة منظمة ويمكن استهلاكها من Reasoning
- النتيجة لا تحتوي على قرارات تجارية
- النتيجة لا تقوم بـ ERP mutations

---

### Task 7: Verification, Quality & Failure Handling
**الهدف:** ضمان جودة النتائج والتعامل مع الأخطاء.
**المخرجات:**
- Quality indicators
- Failure handling strategy
- Open Architectural Decisions log
**معايير الإنجاز:**
- فشل المصدر لا يوقف البحث
- النتائج الجزئية ممكنة مع تحديد المصادر الفاشلة
- قرارات معمارية مفتوحة موثقة للتصميم اللاحق

---

### Task 8: Governance & Documentation
**الهدف:** توثيق الحدود والاعتماديات والقرارات.
**المخرجات:**
- تحديث PLAN.md Section 15.3
- تحديث CURRENT_STATUS.md
- Changelog entry
**معايير الإنجاز:**
- PLAN.md يُحدّث بإضافة WP-34
- لا توجد تعارضات مع Knowledge Ingestion Contract
- Exit Criteria موثقة

---

## 3. ترتيب التنفيذ

```
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8
```

كل مهمة تعتمد على إنجاز المهمة السابقة.

---

## 4. نقاط التحقق (Validation Gates)

| Gate | المهام المُتحقق منها | الشرط للمتابعة |
|------|---------------------|----------------|
| Gate 1 | Task 1 | نماذج Request/Result/Evidence معتمدة |
| Gate 2 | Task 2 | Lifecycle orchestrator يعمل مع mock sources |
| Gate 3 | Task 3 + Task 4 | Source registry و retrieval يعملان |
| Gate 4 | Task 5 | Provenance capture يثبت على كل نتيجة |
| Gate 5 | Task 6 | Research Result interface مقبولة من Reasoning |
| Gate 6 | Task 7 | Failure handling و quality indicators معتمدة |
| Gate 7 | Task 8 | Governance docs محدّثة وExit Criteria مُستوفاة |

---

## 5. Deliverables النهائية

| # | Deliverable | المهمة المسؤولة | الملف |
|---|-------------|-----------------|-------|
| 1 | Research Request/Result Models | Task 1 | `backend/app/research/models.py` |
| 2 | Research Lifecycle Orchestrator | Task 2 | `backend/app/research/orchestrator.py` |
| 3 | Source Registry & Discovery | Task 3 | `backend/app/research/sources/` |
| 4 | Retrieval Abstraction | Task 4 | `backend/app/research/retrieval/` |
| 5 | Evidence & Provenance Capture | Task 5 | `backend/app/research/evidence.py` |
| 6 | Result Structuring & Output | Task 6 | `backend/app/research/result.py` |
| 7 | Verification & Quality | Task 7 | `backend/app/research/quality.py` |
| 8 | Governance Updates | Task 8 | `PLAN.md`, `CURRENT_STATUS.md`, `CHANGELOG.md` |

---

## 6. Acceptance Criteria Coverage

| AC | المهمة المسؤولة |
|----|-----------------|
| AC-34.1: إمكانية إنشاء Research Request | Task 1 |
| AC-34.2: تنفيذ Research Lifecycle كاملة | Task 2 |
| AC-34.3: اكتشاف واستعلام مصادر خارجية | Task 3 + Task 4 |
| AC-34.4: ارتباط النتائج بمصادرها | Task 5 |
| AC-34.5: تسجيل الأدلة/المراجع | Task 5 |
| AC-34.6: التعامل مع فشل المصدر | Task 7 |
| AC-34.7: عدم تقديم LLM كمصدر حقيقة | Task 5 + Task 7 |
| AC-34.8: إخراج نتيجة منظمة لـ Reasoning | Task 6 |
| AC-34.9: الحفاظ على حدود المسؤوليات | Task 2 + Task 6 + Task 7 |

---

## 7. Exit Criteria

| # | Exit Criterion | Verification |
|---|---------------|--------------|
| EC-34.1 | جميع المهام من 1 إلى 7 مكتملة | Git diff + review |
| EC-34.2 | Research Request model يثبت باختبارات | Unit tests |
| EC-34.3 | Lifecycle يعمل end-to-end مع mock sources | Integration tests |
| EC-34.4 | Provenance capture يثبت على كل نتيجة | Unit + integration tests |
| EC-34.5 | Source failure لا يوقف البحث | Fault injection tests |
| EC-34.6 | Research Result interface مقبولة من Reasoning | Contract test |
| EC-34.7 | لا توجد تعديلات على Knowledge Ingestion Contract | Git diff verification |
| EC-34.8 | PLAN.md و CURRENT_STATUS.md محدّثة | Manual verification |

---

## 8. Open Architectural Decisions

| # | Decision | Impact | Decision Required By |
|---|----------|--------|---------------------|
| 1 | Source trust scoring algorithm | ترتيب النتائج والثقة | Task 7 design |
| 2 | Duplicate detection strategy | تجميع النتائج | Task 7 design |
| 3 | Content validation mechanism | جودة النتائج | Task 7 design |
| 4 | Source registry format | إدارة المصادر | Task 3 design |
| 5 | LLM provider selection for research assistance | التكلفة والجودة | Task 2 design |

---

## 9. الاعتماديات

|ependency | Type | Status |
|------------|------|--------|
| WP-30F: Company Knowledge Layer Interface | Internal | ✅ Complete |
| WP-30G: Memory Interface Definition | Internal | ✅ Complete |
| WP-LLM-001: LLM Provider Integration | Internal | ✅ Complete |
| WP-31: AI Memory | Internal | ✅ Complete |
| WP-32: Knowledge Graph | Internal | ✅ Complete |
| WP-33: Trade Intelligence | Internal | ✅ Complete |
| WP-42: Owner Acceptance | Internal | ✅ Complete |
| Knowledge Ingestion Contract boundaries | Documentation | ✅ Clarified |

---

## 10. المهمة الأولى للتنفيذ

**Task 1: Research Request Model & API Contract**

السبب: هي المهمة الأساسية التي تحدد الهيكل الوثائقي للبحث. بدونها لا يمكن تنفيذ الـ lifecycle أو أي مهمة لاحقة.

---

*Document Status: Draft — Pending Approval*
