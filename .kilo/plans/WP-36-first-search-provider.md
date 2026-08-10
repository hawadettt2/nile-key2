# WP-36: First Search Provider Implementation

**Work Package:** WP-36 — First Search Provider Implementation  
**Status:** Closed — Completed  
**Date:** 2026-08-10  
**Authority:** `PLAN.md` (Master Roadmap v2.1) — Single Source of Truth  
**Governing Documents:** `.kilo/plans/WP-35-spec.md`, `.kilo/plans/WP-35-add-provider-guide.md`, `.kilo/plans/WP-34-spec.md`, `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Path:** `.kilo/plans/WP-36-first-search-provider.md`

---

## 1. الهدف

تنفيذ **SearXNG** كأول Search Provider فعلي واحد فوق طبقة WP-35 Provider-Agnostic، وتحويلها من طبقة مجردة إلى مزود بحث قابل للتشغيل فعليًا في الإنتاج.

## 2. النطاق

### 2.1 داخل النطاق
- تنفيذ **SearXNG فقط** كـ `SearchProviderAdapter` فعلي.
- تسجيل `SearXNGAdapter` في `SearchProviderRouter` في مسار الإنتاج.
- تحويل استجابة SearXNG إلى `RetrievedContent` و `RetrievalResult` باستخدام `RetrievalStatus` الحالي.
- اختبارات الـAdapter وتكامل failover.
- توثيق الـAdapter الجديد.

### 2.2 خارج النطاق
- **لا** تنفيذ أكثر من مزود بحث واحد في هذه الـWP.
- **لا** تنفيذ Brave Search API في هذه الـWP.
- **لا** تعديل WP-35 أو إعادة فتحها.
- **لا** تعديل WP-34 أو Knowledge Ingestion Contract أو أي عقد معماري.
- **لا** خلط Search Provider مع AI/LLM Provider Router.
- **لا** اعتماد VPS أو خدمة خارجية أو Credits كاعتماد معماري إلزامي.
- **لا** تنفيذ web scraping أو crawling مباشر.
- **لا** تغيير Evidence/Provenance/Verification lifecycle.

## 3. الاعتماد على WP-35

| المكون | المسار | الحالة |
|--------|--------|--------|
| `ProviderCapability` | `backend/app/research/retrieval/providers/capability.py` | ✅ موجود |
| `SearchProviderAdapter` | `backend/app/research/retrieval/providers/adapter.py` | ✅ موجود |
| `SearchProviderRouter` | `backend/app/research/retrieval/providers/router.py` | ✅ موجود |
| `SEARCH_STUB_FALLBACK` | `backend/app/core/config.py` | ✅ موجود |
| WP-35 Boundaries | محفوظة | لا تعديل على WP-35 |

WP-36 هي **أول مستهلك تشغيلي** لطبقة WP-35، وتنفّذ **SearXNG** فقط كأول مزود بحث فعلي.

## 4. القرارات المثبتة

| # | القرار | القيمة |
|---|--------|--------|
| D-1 | **أول Search Provider فعلي سيتم تنفيذه في WP-36** | ✅ **SearXNG** |
| D-2 | **خيار مستقبلي/بديل لاحق** | ✅ **Brave Search API** — ليس ضمن نطاق WP-36 |

**تفصيل D-1:**  
SearXNG هو أول مزود بحث فعلي سيتم تنفيذه في WP-36.  
نقطة الاتصال/البحث ستكون عبر SearXNG instance مُستضافة ذاتيًا أو عامة، وفقًا لموافقة المالك على البنية التحتية.  
البيانات الاعتمادية ستُدار عبر متغيرات البيئة التالية:
- `SEARXNG_BASE_URL`: عنوان الـinstance
- `SEARXNG_API_KEY`: مفتاح API إذا كان الـinstance يتطلب مصادقة
- `SEARXNG_TIMEOUT_SECONDS`: مهلة الاتصال بالثواني

لا تُخزن أسرار ثابتة في الكود. جميع القيم تُقرأ من `.env` أو متغيرات البيئة.

**تفصيل D-2:**  
Brave Search API مرشح لاحق/بديل مستقبلي فقط.  
لا يُنفّذ في WP-36، ولا يُشترط التخطيط له الآن.

## 5. المهام التنفيذية

```
Task 1: Implement SearXNG Adapter
Task 2: Register SearXNG Adapter in Production Router
Task 3: Tests — SearXNG Adapter + Failover + Regression
Task 4: Documentation Update
```

### Task 1: Implement SearXNG Adapter
**الهدف:** إنشاء `SearXNGAdapter` فعلي يمتد من `SearchProviderAdapter`.
**الملف المتوقع:** `backend/app/research/retrieval/providers/searxng_adapter.py`
**المتطلبات:**
- `ProviderCapability` مع `provider_id="searxng"`, `priority`, `enabled` والقدرات الفعلية لـ SearXNG.
- `retrieve(source, query)` ينفّذ طلب بحث HTTP إلى SearXNG instance ويحول الاستجابة إلى `RetrievedContent` / `RetrievalResult`.
- `health_check()` يتحقق من توفر SearXNG instance.
- أخطاء SearXNG تُ mapped إلى `RetrievalStatus` الحالي فقط.
- لا new contracts.

**مثال لهيكل الـAdapter:**
```python
class SearXNGAdapter(SearchProviderAdapter):
    def __init__(self, capability: ProviderCapability, base_url: str, timeout: float = 10.0):
        self._capability = capability
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def capability(self) -> ProviderCapability:
        return self._capability

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        # httpx post to {base_url}/search
        # Map JSON results to RetrievedContent
        # Map HTTP/network errors to RetrievalStatus
        pass

    async def health_check(self) -> bool:
        # Return True if SearXNG instance is reachable
        pass
```

**Acceptance Criteria:**
- AC-36.1: `retrieve()` يرجع `RetrievalStatus.SUCCESS` مع `RetrievedContent` صالح عند استجابة ناجحة من SearXNG.
- AC-36.2: `retrieve()` يرجع `RetrievalStatus.TIMEOUT` عند انتهاء مهلة الاتصال بـ SearXNG.
- AC-36.3: `retrieve()` يرجع `RetrievalStatus.CONNECTION_FAILURE` عند عدم الاتصال بـ SearXNG.
- AC-36.4: `retrieve()` يرجع `RetrievalStatus.INVALID_RESPONSE` عند استجابة غير متوقعة من SearXNG.
- AC-36.5: `health_check()` يرجع `True` عند توفر SearXNG و `False` عند عدم توفره.
- AC-36.6: لا تعديلات على `contracts.py` أو `RetrievalStatus` enum.

### Task 2: Register SearXNG Adapter in Production Router
**الهدف:** تسجيل `SearXNGAdapter` في `SearchProviderRouter` في `research.py`.
**المتطلبات:**
- تسجيل صريح عند bootstrap.
- `SEARCH_STUB_FALLBACK` يبقى كاحتياط صريح فقط.
- لا makes الـAdapter الجديد silent fallback.

**Acceptance Criteria:**
- AC-36.7: `SearXNGAdapter` مسجل في `SearchProviderRouter` عند بدء التطبيق.
- AC-36.8: `SEARCH_STUB_FALLBACK=false` افتراضيًا.
- AC-36.9: عند فشل `SearXNGAdapter`، يحاول Router المحاولة مرة أخرى أو يرجع `FAILED` دون استخدام `StubRetriever` تلقائيًا.

### Task 3: Tests
**الهدف:** التحقق من سلوك `SearXNGAdapter` والـRouter معه.
**المخرجات:**
- `tests/test_research_searxng_adapter.py`
**المتطلبات:**
- اختبار نجاح `retrieve()` مع استجابة وهمية/mock من SearXNG.
- اختبار فشل `retrieve()` يُ mapped إلى `RetrievalStatus` الصحيح.
- اختبار `health_check()`.
- اختبار failover إذا كان هناك أكثر من adapter (حاليًا واحد فقط).
- اختبار أن `StubRetriever` لا يُستخدم تلقائيًا.
- WP-34 regression tests تظل سليمة.

**Acceptance Criteria:**
- AC-36.10: Unit test يغطي جميع حالات `retrieve()` المحددة في Task 1.
- AC-36.11: Unit test يغطي `health_check()`.
- AC-36.12: Integration test يثبت أن `SearXNGAdapter` يعمل مع `SearchProviderRouter`.
- AC-36.13: WP-34 regression tests تنجح (لا كسر في `test_research_retrieval.py`, `test_research.py`, `test_research_quality.py`, `test_research_evidence.py`).

### Task 4: Documentation Update
**الهدف:** تحديث الوثائق لتعكس SearXNG كأول مزود فعلي.
**المتطلبات:**
- تحديث `.kilo/plans/WP-35-add-provider-guide.md` إذا لزم الأمر.
- لا تعديل WP-35 spec أو plan الأساسية.
- docstrings في `SearXNGAdapter`.

## 6. هيكل الملفات المتوقع

```
backend/app/research/retrieval/providers/
├── __init__.py
├── capability.py       (FROZEN — WP-35)
├── adapter.py          (FROZEN — WP-35)
├── router.py           (FROZEN — WP-35)
└── searxng_adapter.py   (NEW — WP-36)

backend/app/core/config.py       (MODIFIED — add SEARXNG_* env vars)
backend/app/routers/research.py   (MODIFIED — register SearXNGAdapter)
backend/tests/
└── test_research_searxng_adapter.py   (NEW — WP-36)
```

## 7. هيكل SearXNGAdapter المتوقع

```python
from app.research.retrieval.providers.adapter import SearchProviderAdapter
from app.research.retrieval.providers.capability import ProviderCapability
from app.research.retrieval.contracts import RetrievedContent, RetrievalResult, RetrievalStatus
from app.schemas.research import Source

class SearXNGAdapter(SearchProviderAdapter):
    def __init__(self, capability: ProviderCapability, base_url: str, timeout: float = 10.0):
        self._capability = capability
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def capability(self) -> ProviderCapability:
        return self._capability

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        # httpx post to {base_url}/search
        # Map JSON results to RetrievedContent
        # Map HTTP/network errors to RetrievalStatus
        pass

    async def health_check(self) -> bool:
        # Return True if SearXNG instance is reachable
        pass
```

## 8. الاختبارات والتحقق

| النوع | الوصف |
|--------|-------|
| Unit tests | `SearXNGAdapter` فقط: success, failure, health_check |
| Integration tests | Router + `SearXNGAdapter` + WP-34 lifecycle |
| Regression | `tests/test_research_retrieval.py`, `tests/test_research.py`, `tests/test_research_quality.py`, `tests/test_research_evidence.py` |
| Boundary | لا تعديل على `contracts.py`, `orchestrator.py`, `quality.py`, `KNOWLEDGE_INGESTION_CONTRACT.md` |

## 9. حدود صارمة

| الحد | التحقق |
|-------|--------|
| لا تعديل WP-34 contracts | `git diff` على `contracts.py`, `orchestrator.py`, `retrieval/orchestrator.py`, `quality.py` |
| لا تعديل Knowledge Ingestion Contract | `git diff` على `KNOWLEDGE_INGESTION_CONTRACT.md` |
| لا خلط Search Provider مع AI/LLM | لا imports من `app.agent.llm` أو ما يعادله في adapter |
| لا تعديل WP-35 | لا تعديل على `capability.py`, `adapter.py`, `router.py` إلا إذا كان bug في WP-35 |
| StubRetriever احتياط صريح فقط | `SEARCH_STUB_FALLBACK` يبقى `false` افتراضيًا |
| Brave Search API غير مدرج الآن | لا ملفات أو تكوينات خاصة بـ Brave في WP-36 |

## 10. Exit Criteria

| # | الشرط | التحقق |
|---|-------|--------|
| EC-36.1 | D-1 مثبت: SearXNG هو أول Provider | Decision record في الخطة |
| EC-36.2 | `SearXNGAdapter` منفَّذ ومسجل | Code review + unit test |
| EC-36.3 | `retrieve()` يرجع `RetrievalResult` صالح | Unit test |
| EC-36.4 | `health_check()` يعمل | Unit test |
| EC-36.5 | failover يعمل عند فشل `SearXNGAdapter` | Integration test |
| EC-36.6 | WP-34 regression tests تنجح | pytest suite |
| EC-36.7 | لا تعديلات على WP-34 contracts | Git diff |
| EC-36.8 | لا تعديلات على Knowledge Ingestion Contract | Git diff |
| EC-36.9 | `StubRetriever` لا يُused كـ silent fallback | Test + config review |

## 11. المخاطر والقرارات المفتوحة

| # | المخاطر | الاحتمال | التأثير | التخفيف |
|---|---------|---------|--------|---------|
| R-1 | واجهة برمجة SearXNG تتغير | Low | Medium | إصدارات ثابتة من الاستعلام/الاستجابة؛ وثّق الاختلافات |
| R-2 | Instance SearXNG غير موثوق أو بطيء | Medium | High | تأكد من موافقة المالك على البنية التحتية قبل التنفيذ |
| R-3 | نتائج SearXNG غير مناسبة لاحتياجات DEM | Medium | Medium | خريطة الحقول قابلة للتعديل بدون تعديل WP-35 |
| R-4 | StubRetriever يُused كـ fallback صامت | Low | Medium | اختبار صريح + `SEARCH_STUB_FALLBACK=false` افتراضيًا |

| # | القرار المفتوح | المالك؟ |
|---|---------------|---------|
| D-1 | مثبت: **SearXNG** كأول Provider | ✅ مثبت |
| D-2 | Brave Search API كبديل لاحق | ✅ مؤجل — ليس ضمن WP-36 |
| D-3 | ما إذا كان `SEARCH_STUB_FALLBACK` يُفعَّل في الإنتاج | تشغيلي |
| D-4 | مسؤولية تشغيل وصيانة instance SearXNG | تشغيلي |

## 12. Closure Record

**Closure Date:** 2026-08-10
**Closure Status:** Completed
**Baseline:** WP-36 First Search Provider Implementation — SearXNG

### 12.1 Completed Tasks

| Task | Status | Evidence |
|------|--------|----------|
| Task 1: Select/Approve Provider | ✅ Completed | D-1 = SearXNG + SEARXNG_* env vars |
| Task 2: Implement SearXNG Adapter | ✅ Completed | `backend/app/research/retrieval/providers/searxng_adapter.py` |
| Task 3: Register in Production Router | ✅ Completed | `backend/app/routers/research.py` |
| Task 4: Tests | ✅ Completed | `tests/test_research_searxng_adapter.py` + regression |
| Task 5: Documentation Update | ✅ Completed | `WP-35-add-provider-guide.md` + docstrings |

### 12.2 Exit Criteria Verification

| # | Condition | Status | Evidence |
|---|-----------|--------|----------|
| EC-36.1 | D-1 fixed: SearXNG is first provider | ✅ PASS | Section 4 decision record |
| EC-36.2 | SearXNGAdapter implemented and registered | ✅ PASS | Code review + tests |
| EC-36.3 | `retrieve()` returns valid `RetrievalResult` | ✅ PASS | Unit tests |
| EC-36.4 | `health_check()` works | ✅ PASS | Unit tests |
| EC-36.5 | failover works when adapter fails | ✅ PASS | Integration test |
| EC-36.6 | WP-34 regression tests pass | ✅ PASS | pytest suite |
| EC-36.7 | No WP-34 contracts modified | ✅ PASS | Git diff clean |
| EC-36.8 | No Knowledge Ingestion Contract modified | ✅ PASS | Git diff clean |
| EC-36.9 | `StubRetriever` not used as silent fallback | ✅ PASS | Test + config review |

### 12.3 Boundary Verification

- ✅ WP-35 = **Closed — Completed**, not reopened
- ✅ WP-34 contracts unchanged
- ✅ Knowledge Ingestion Contract unchanged
- ✅ No mixing of Search Provider with AI/LLM Provider
- ✅ No architectural primary provider declared
- ✅ No hardcoded secrets or API keys
- ✅ Brave Search API deferred, not implemented

### 12.4 Final Forensic Audit

**Result:** PASS
**Findings:** None
**Remaining technical gaps:** None

---

*Document Status: Closed — Completed*
