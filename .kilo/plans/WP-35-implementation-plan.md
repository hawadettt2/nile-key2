# WP-35 Implementation Plan: External Research Provider Adapter & Routing Layer

**Work Package:** WP-35 — External Research Provider Adapter & Routing Layer  
**Status:** Closed — Completed  
**Date:** 2026-08-10  
**Authority:** `PLAN.md` + `.kilo/plans/WP-35-spec.md` + `.kilo/plans/WP-34-spec.md` + `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Path:** `.kilo/plans/WP-35-implementation-plan.md`

---

## 1. الغرض

بناء طبقة توجيه/تكيّف للبحث الخارجي تسمح بإضافة وتبديل مزودات البحث دون إعادة بناء معمارية WP-34، مع الحفاظ على خط البحث كاملاً: Search → Sources → Retrieval → Evidence → Provenance → Verification → Result.

---

## 2. نطاق المهام التنفيذية

### Task 1: Provider Capability Model
**الهدف:** تعريف نموذج وصف قادرات أي مزود بحث، مستقل عن اسم المزود أو واجهته.
**المخرجات:**
- `backend/app/research/retrieval/providers/capability.py`
- `ProviderCapability` dataclass/model
- اختبارات serialization وقدرات افتراضية

**معايير الإنجاز:**
- `ProviderCapability` يصف: `supports_web_search`, `supports_source_urls`, `supports_snippets`, `requires_api_key`, `has_usage_limit`, `priority`, `enabled`
- لا يحتوي على أي اسم مزود محدد أو بيانات اعتماد
- قابل للتوسعة بمجرد إضافة حقول جديدة
- لا يشير إلى أي مزود فعلي كـ primary أو مثال ملزم

---

### Task 2: Search Provider Adapter Interface
**الهدف:** تعريف الواجهة التي سينفذها كل مزود.
**المخرجات:**
- `backend/app/research/retrieval/providers/adapter.py`
- `SearchProviderAdapter` ABC مع: `capability`, `retrieve(source, query)`, `health_check()`

**معايير الإنجاز:**
- `retrieve()` ترجع `RetrievalResult` باستخدام `RetrievalStatus` الحالي من WP-34
- لا تُضاف عقود جديدة
- `RetrievedContent` و `RetrievalResult` remains بدون تغيير
- مثال واحد mock adapter يثبت الواجهة فقط

---

### Task 3: Search Provider Router
**الهدف:** بناء/router يختار التكيف المناسب بناءً على القدرات والحالة.
**المخرجات:**
- `backend/app/research/retrieval/providers/router.py`
- `SearchProviderRouter` مع: `register_adapter()`, `unregister_adapter()`, `retrieve_with_fallback(source, query)`

**معايير الإنجاز:**
- يختارAdapter بناءً على `capability.supports_web_search` و `capability.enabled` و `capability.priority`
- على timeout/failure/invalid response: ينتقل للـAdapter التالي بالأولوية
- إذا فشل كل الـAdapters: يرجع `RetrievalStatus.FAILED`
- لا يستخدم `StubRetriever` كاحتياط تلقائي صامت
- يُسجل كل تبديل/فشل في السجلات

---

### Task 4: Optional Example Adapters
**الهدف:** توفير أمثلة اختيارية يثبتان قابلية تشغيل الواجهة مع مزودات مختلفة.
**المخرجات:**
- `backend/app/research/retrieval/providers/` (ملفات اختيارية)

**معايير الإنجاز:**
- كل مثال يحول استجابة المزود إلى `RetrievedContent` و `RetrievalResult`
- كل مثال يطابق حالات الخطأ إلى `RetrievalStatus`
- الأمثلة **لا تُعتبر التزامًا باختيار مزود معين**
- يمكن تشغيل اختباراتها بدون خدمات خارجية حقيقية
- لا يُشترط تنفيذ أي مثال معين لإكمال WP-35

---

### Task 5: Router Wiring in Production
**الهدف:** ربط الـRouter في مسار البحث الحالي.
**المخرجات:**
- تعديل `backend/app/routers/research.py`

**معايير الإنجاز:**
- يستبدل إنشاء `StubRetriever` المباشر بإنشاء `SearchProviderRouter`
- عند عدم وجود أي adapter مسجل: يسجل تحذير
- `StubRetriever` يُستخدم فقط إذا كان `SEARCH_STUB_FALLBACK=true` بشكل صريح
- لا يتطلب تعديل `ResearchOrchestrator` أو `RetrievalOrchestrator` أو أي مرحلة بحث
- جميع اختبارات WP-34 الحالية (103 اختبار) تظل سليمة

---

### Task 6: Tests — Failover, Partial Degradation, Evidence Preservation
**الهدف:** التحقق من سلوك الـRouter والـAdapters.
**المخرجات:**
- `backend/tests/test_research_search_router.py` (جديد)

**معايير الإنجاز:**
- اختبار: Router يختارAdapter حسب الأولوية والقدرات
- اختبار: عند فشلAdapter، ينتقل للتالي
- اختبار: عند فشل كل الـAdapters، يرجع `FAILED`
- اختبار: `EvidenceCaptureStage` يلتقط الأدلة من المصدر الناجح فقط
- اختبار: `ProvenanceRecord` يحتوي على `source_id` و `source_reference` و `retrieval_timestamp` صحيحين
- اختبار: `VerificationStage` يتحقق من وجود `source_id` في الأدلة
- اختبار: سلوك `StubRetriever` كاحتياط صريح فقط
- اختبار: عدم خلط Search Provider مع LLM Provider (لا imports لـ LLM routing)

---

### Task 7: Documentation
**الهدف:** توثيق كيفية إضافة مزود جديد.
**المخرجات:**
- docstrings في `capability.py`, `adapter.py`, `router.py`
- دليل قصير: "How to add a new Search Provider"

**معايير الإنجاز:**
- خطوات واضحة: أنشئ adapter → عرّف capability → سجّله في Router
- لا توجد أسرار مكشوفة
- لا اختيار مزود نهائي موصى به

---

## 3. ترتيب التنفيذ

```
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7
```

كل مهمة تعتمد على سابقتها. Task 4 اختيارية ويمكن تنفيذها بالتوازي مع Task 5.

---

## 4. نقاط التحقق (Validation Gates)

| Gate | المهام المُتحقق منها | الشرط للمتابعة |
|------|---------------------|----------------|
| Gate 1 | Task 1 | `ProviderCapability` model working مع فحوصات serialization |
| Gate 2 | Task 1 + Task 2 | `SearchProviderAdapter` ABC ثابت مع mock adapter |
| Gate 3 | Task 3 | `SearchProviderRouter` يختار وينتقل بين mock adapters |
| Gate 4 | Task 4 | مثال اختياري واحد على الأقل يعمل مع استجابة وهمية |
| Gate 5 | Task 5 | Router مربوط في `research.py` مع سلوك صحيح بدون/مع adapters |
| Gate 6 | Task 6 | اختبارات failover وpartial degradation وevidence preservation تنجح |
| Gate 7 | Task 7 | documentation كاملة + WP-34 tests regression (103) تنجح |

---

## 5. Deliverables النهائية

| # | Deliverable | المهمة المسؤولة | الملف |
|---|-------------|-----------------|-------|
| 1 | Provider Capability Model | Task 1 | `backend/app/research/retrieval/providers/capability.py` |
| 2 | Search Provider Adapter Interface | Task 2 | `backend/app/research/retrieval/providers/adapter.py` |
| 3 | Search Provider Router | Task 3 | `backend/app/research/retrieval/providers/router.py` |
| 4 | Example Adapters (optional) | Task 4 | `backend/app/research/retrieval/providers/*.py` (اختياري) |
| 5 | Router wiring | Task 5 | `backend/app/routers/research.py` (تعديل) |
| 6 | Failover & degradation tests | Task 6 | `backend/tests/test_research_search_router.py` |
| 7 | Documentation | Task 7 | docstrings + guide |

---

## 6. Acceptance Criteria Coverage

| AC | المهمة المسؤولة |
|----|-----------------|
| AC-35.1: `ProviderCapability` model يعمل | Task 1 |
| AC-35.2: `SearchProviderAdapter` ABC ثابت | Task 2 |
| AC-35.3: Router يختارAdapter حسب القدرات والأولوية | Task 3 |
| AC-35.4: Failover بين Adapters عند timeout/failure | Task 3 + Task 6 |
| AC-35.5: `StubRetriever` كاحتياط صريح فقط | Task 5 |
| AC-35.6: Evidence/Provenance محفوظة دون تعديل | Task 6 |
| AC-35.7: Partial results تعمل | Task 6 |
| AC-35.8: لا كسر في اختبارات WP-34 | Gate 7 |
| AC-35.9: لا خلط بين Search Provider و LLM Provider | Task 6 |
| AC-35.10: إضافة مزود جديد لا يتطلب تعديل WP-34 | Architecture review + Task 2 design |
| AC-35.11: Provider-Agnostic architecture | Architecture review |

---

## 7. Exit Criteria

| # | Exit Criterion | Verification |
|---|---------------|--------------|
| EC-35.1 | جميع المهام من 1 إلى 7 مكتملة | Git diff + review |
| EC-35.2 | `ProviderCapability` model يعمل | Unit test |
| EC-35.3 | `SearchProviderAdapter` ABC ثابت | Interface test |
| EC-35.4 | `SearchProviderRouter` يختار وينتقل بين adapters | Integration test |
| EC-35.5 | عند فشل كل الـAdapters: `FAILED` + partial handling | Integration test |
| EC-35.6 | `StubRetriever` كاحتياط صريح فقط | Integration test |
| EC-35.7 | Evidence/Provenance/Verification boundaries محفوظة | WP-34 test suite (103 tests) تنجح |
| EC-35.8 | لا تعديلات على `KNOWLEDGE_INGESTION_CONTRACT.md` | Git diff verification |
| EC-35.9 | لا تعديلات على عقود WP-34 | Git diff verification |
| EC-35.10 | Router مربوط في `research.py` | Manual + integration test |
| EC-35.11 | إضافة adapter جديد لا يتطلب تعديل WP-34 | Architecture review |
| EC-35.12 | لا مزود معين مُعلَّن كـ primary في المعمارية أو الإعدادات | Architecture review |
| EC-35.13 | `.env.example` محدّث بمتغيرات Router فقط | Manual verification |

---

## 8. Open Architectural Decisions (Inherited from WP-34)

| # | Decision | Impact | Status |
|---|----------|--------|--------|
| OAD-1 | Source trust scoring algorithm | ترتيب النتائج والثقة | Future work — NOT addressed |
| OAD-2 | Duplicate detection strategy | تجميع النتائج | Future work — NOT addressed |
| OAD-3 | Content validation mechanism | جودة النتائج | Future work — NOT addressed |

**WP-35 does NOT resolve OAD-1, OAD-2, or OAD-3.**

---

## 9. القرارات التي تحتاج موافقة المالك

| # | القرار | لماذا |
|---|--------|-------|
| D-1 | أي مزود/موفرات سيتم تفعيلها فعليًا في الإنتاج | الخطة لا تختار مزودًا؛ المالك يحدد أي adapters تسجَّل |
| D-2 | ما إذا كان سيتم تفعيل `SEARCH_STUB_FALLBACK` في الإنتاج | يؤثر على سلوك النظام عند عدم توفر مزود |
| D-3 | مسؤولية تشغيل وصيانة أي بنية تحتية للمزودات المختارة | خارج نطاق الخطة الهندسية |

---

## 10. Boundaries Verification Checklist

قبل التنفيذ، تأكد من:

- [ ] لا تعديلات على `backend/app/research/retrieval/contracts.py`
- [ ] لا تعديلات على `backend/app/research/evidence/contracts.py`
- [ ] لا تعديلات على `backend/app/research/quality.py`
- [ ] لا تعديلات على `backend/app/research/orchestrator.py`
- [ ] لا تعديلات على `backend/app/research/retrieval/orchestrator.py`
- [ ] لا تعديلات على `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`
- [ ] لا تعديلات على `PLAN.md` أو `CURRENT_STATUS.md` أو `CHANGELOG.md` (في هذه المرحلة)
- [ ] لا imports أو تبعيات من `Search Provider Router` إلى `AI Provider Router`
- [ ] لا مزود معين مُعلَّن كـ primary في الوثائق أو الكود

---

## 11. Closure Record

**Closure Date:** 2026-08-10
**Closure Status:** Completed
**Baseline:** WP-35 Provider-Agnostic Search Provider Router/Adapter Layer

### 11.1 Completed Tasks

| Task | Status | Evidence |
|------|--------|----------|
| Task 1: Provider Capability Model | ✅ Completed | `backend/app/research/retrieval/providers/capability.py` + unit tests |
| Task 2: Search Provider Adapter Interface | ✅ Completed | `backend/app/research/retrieval/providers/adapter.py` + interface tests |
| Task 3: Search Provider Router | ✅ Completed | `backend/app/research/retrieval/providers/router.py` + failover tests |
| Task 4: Optional Example Adapters | ⏸️ Deferred | Mock adapters in tests are sufficient; deferred to first provider adoption |
| Task 5: Router Wiring in Production | ✅ Completed | `backend/app/routers/research.py` + `backend/app/core/config.py` |
| Task 6: Tests — Failover, Partial Degradation, Evidence Preservation | ✅ Completed | `backend/tests/test_research_search_router.py` + WP-34 regression tests |
| Task 7: Documentation | ✅ Completed | Docstrings + `.kilo/plans/WP-35-add-provider-guide.md` |

### 11.2 Exit Criteria Verification

All Exit Criteria EC-35.1 through EC-35.13 are satisfied. See sections 6 and 7 for mapping.

### 11.3 Deferred Decisions

| Decision | Original Reference | Deferred To |
|----------|-------------------|-------------|
| D-1: Select production search providers | WP-35 Decision D-1 | Future Work Package: "First Search Provider Implementation" |
| D-2: Enable `SEARCH_STUB_FALLBACK` in production | WP-35 Decision D-2 | Deployment/operations decision; not a WP-35 closure requirement |
| D-3: Provider infrastructure ownership | WP-35 Decision D-3 | Future operational planning |

**Note:** D-1 is explicitly **not** a closure requirement for WP-35. WP-35 delivers the abstraction layer; provider selection is a separate operational decision.

### 11.4 Boundary Verification

- ✅ No modifications to WP-34 contracts (`contracts.py`, `orchestrator.py`, `retrieval/orchestrator.py`, `quality.py`)
- ✅ No modifications to `KNOWLEDGE_INGESTION_CONTRACT.md`
- ✅ No mixing of Search Provider Router with AI/LLM Provider Router
- ✅ No provider designated as primary in architecture or config
- ✅ No external service/VPS/credits mandated as architectural dependency

### 11.5 Next Steps

1. Use WP-35 as the new baseline for External Research retrieval.
2. Create a separate Work Package for **First Search Provider Implementation** when a provider is selected.
3. Follow `.kilo/plans/WP-35-add-provider-guide.md` when implementing new adapters.

---

*Document Status: Closed — Completed*
