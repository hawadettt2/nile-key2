# Master Remediation Plan — DEM Commercial Readiness Reset

**Plan ID:** 1789672443844-master-remediation-plan  
**Branch:** main  
**Mode:** Plan Only — No Implementation  
**Authority:** Forensic Audit findings (2026-09-17)  
**Governing Baseline:** Commit `d238f5489922ad472521cd61ca63002f73129f5d` + Baseline Document `.kilo/plans/baseline-2026-09-17.md` + Current `.env` and `backend/data/` state  
**Objective:** إعادة ضبط الأساس المعرفي والتشغيلي والتجاري لـDEM بناءً على الحقيقة التشغيلية الحالية، دون افتراض أي قدرة لا يثبتها مصدر ودليل.

---

## Architectural Integrity Gate

هذه الخطة تعمل داخل المعمارية القائمة، ولا تستبدلها.

### Canonical AI Lifecycle

```text
USER
 ↓
INTENT
 ↓
GOAL
 ↓
PLAN
 ↓
DECISION
 ↓
STRATEGIC REASONING
 ↓
REPLANNING
 ↓
MISSION
 ↓
TASK
 ↓
EXECUTION
 ↓
OUTCOME
 ↓
FEEDBACK
 ↓
MEMORY
 ↓
FUTURE DECISION
 ↓
RESPONSEBUILDER
 ↓
INTENTCONTENT
 ↓
AVATAR
```

**ملاحظة:** Research → Evidence → Business Intelligence ليست مراحل داخل الـcanonical lifecycle. هي Knowledge Plane منفصلة تغذي Decision / Strategic Reasoning / Response.

### Knowledge Plane

```text
External Knowledge Sources
        ↓
Research
        ↓
Evidence
        ↓
Business Intelligence
        ↓
Decision / Strategic Reasoning Context
```

**القاعدة:** Knowledge Plane تقدم معلومات للـAI Core، ولا تُضاف كمراحل داخل الـcanonical lifecycle.

### Response Plane

```text
Decision / Strategic Context
        +
Research / Evidence
        +
Business Intelligence
        ↓
ResponseBuilder
        ↓
IntentContent
        ↓
Avatar
```

### Architecture Rules

* `Research` ليس Decision Engine.
* `Business Intelligence` ليس Decision Engine.
* `ResponseBuilder` ليس Reasoning Engine.
* `Avatar` ليس Decision Engine.
* نقص المعرفة لا يجوز أن يتحول إلى Capability غير موجودة داخل Decision.
* نقص المعرفة لا يجوز أن يتحول إلى Strategic Recommendation غير مثبتة.
* نقص المعرفة لا يجوز أن يختفي داخل Business Intelligence.
* نقص المعرفة لا يجوز أن يظهر للمستخدم كأنها حقيقة مؤكدة.
* لا يوجد second planner.
* لا يوجد second reasoning engine.
* لا يوجد second decision engine.

### Architectural Freeze

هذه الطبقات تعتبر **Closed / Protected**:

```text
Goal
Plan
Decision
Strategic Reasoning
Adaptive Replanning
Mission
Task
Execution
Outcome
Feedback
Memory
Multi-Mission Orchestration
Goal Evolution
Autonomy Policies
Avatar architecture
Business Intelligence architecture
```

لا تعاد هندستها.

المسموح هو:

```text
Targeted correction
Contract-consistent validation
Capability truth propagation
Evidence propagation
Readiness enforcement
False-claim prevention
```

فقط.

---

## المبدأ الأساسي

هذه الخطة هي **المرجع الوحيد** لإصلاح DEM. لا تُنشأ خطط أخرى لنفس الغرض. لا تُعاد فتح Work Packages المغلقة دون سبب مثبت.

---

## القاعدة الذهبية

لا يُسمح بأي مما يلي في أي مرحلة:

| الفعل المحظور | السبب |
|---------------|-------|
| اعتبار `Registered = Available` | التسجيل لا يضمن التفعيل |
| اعتبار `HTTP 200 = Sufficient` | الاستجابة لا تعني Capability كافية |
| اعتبار `Capability Label = Proven Capability` | التسمية لا تعني الإثبات |
| اعتبار `test fixture = production source` | البيانات الوهمية لا تمثل الإنتاج |
| اعتبار `historical trade = market opportunity` | التجارة التاريخية لا تُنتج فرص السوق |
| اعتبار `country LPI = route freight cost` | مؤشر الدولة لا يعادل تكلفة الشحن |
| اعتبار `Complementary = Production` | المصدر التكميلي ليس إنتاجيًا |
| اعتبار `Planned = Available` | المخطط له ليس متاحًا |
| اعتبار `Jordan = general scope` | السيناريو الاختباري لا يعمم |
| اعتبار `Provider Count = Success` | العدد لا يدل على الجاهزية |

---

## Missing Knowledge Rule

```text
Missing Knowledge
must never become
Unsupported Finding
or Unsupported Decision
or Unsupported Strategic Conclusion
or Unsupported User-facing Claim
```

---

## Readiness Model

يجب الفصل بين مستويات جاهزية مختلفة:

### Provider Readiness

```text
1. Implemented — Code exists
2. Registered — In registry
3. Configured — Credentials/settings present
4. Activated — Registered at startup
5. Reachable — Health check passes
6. Returns Data — Returns non-empty results
7. Capability Proven — Data matches family requirement
```

وهنا ينتهي **Provider Readiness**.

### Capability Readiness

```text
8. Scope Ready — Covers declared scope
9. Country/Product Ready — Coverage matches target geography and products
```

### Business Question Readiness

```text
10. Business Question Ready — Can answer the specific commercial question
11. Decision-Safe — Evidence supports tactical decision
12. Response-Safe — Evidence supports user-facing claim
```

**القاعدة الأساسية:**

```text
Provider ≠ Capability Bundle ≠ Business Answer
```

---

# Phase 0 — Baseline Freeze + Security

## الهدف
تثبيت الحالة الحالية كمرجع Baseline، وتوثيق/احتواء المخاطر الأمنية، ومنع العودة للتحقيق من البداية.

**في هذه المرحلة:**
- يتم تجميع Baseline Document
- يتم توثيق暴露ات الأمان
- يتم تسجيل خطة Credential Rotation
- لا يتم تنفيذ تدوير credentials فعلي
- لا يتم إجراء تغييرات تطبيقية
- لا يتم تفعيل أي Provider

## Inputs
- آخر Forensic Audit عن Production Knowledge Coverage
- آخر Forensic Audit عن Production Knowledge Readiness
- Baseline Document `.kilo/plans/baseline-2026-09-17.md`
- Commit `d238f5489922ad472521cd61ca63002f73129f5d`
- ملف `.env` الحالي
- مجلد `backend/data/` الحالي

## Scope
تثبيت الحالة الحالية فقط. لا إصلاحات. لا تفعيل مصادر.

## Dependencies
لا يوجد. هذه أول Phase.

## Exact Deliverables

### 0.1 Baseline Document
وثيقة واحدة `.kilo/plans/baseline-2026-09-17.md` تحتوي على:
- كل Provider المُنَفَّذ حالياً
- حالة Runtime Activation لكل منها (Active / Inactive / Conditional)
- حالة Credentials (Configured / Missing / Placeholder)
- حالة Data Files (Present / Missing / Test-only)
- Known Gaps لكل Family
- Closed WPs التي تؤثر على هذه الخطة
- Accepted Complementary Coverage
- Known Implementation Defects

### 0.2 Security Track
- اعتبار أي credential ظهر في التقارير السابقة **compromised**
- توثيق أن `LLM_API_KEY` في `.env` يجب تدويره
- توثيق أن أي credential قديم في git history يجب استبداله
- منع أي secret من الظهور في هذه الخطة أو أي خطة لاحقة

## Acceptance Criteria
- [ ] Baseline document موحد ومعتمد
- [ ] Security Track موثّق بدون تعديل الكود
- [ ] Credential exposure risks documented with rotation plan
- [ ] required owner approvals recorded
- [ ] Runtime identity matches governing baseline commit

## Exit Gate
```text
Baseline frozen
+
Known security exposure contained with rotation plan
+
Runtime artifact/commit identity matches governing baseline
```

## Stop Conditions
- إذا ظهر credential جديد غير موثق → توقف حتى توثيقه
- إذا ظهر source جديد غير مصنف → توقف حتى تصنيفه

## What Must Not Change
- لا تعديل الكود
- لا تعديل Architecture
- لا تعديل Business Intelligence
- لا تعديل Avatar
- لا تعديل Knowledge Graph أو Multi-Agent

## Architecture Impact
لا يوجد. Phase 0 لا تعدل Architecture.

## Evidence Required
- Baseline Document موقّع
- Security Track موقّع

---

# Phase 1 — Honest Commercial Promise

## الهدف
تحديد **ما الذي نعد المستخدم به فعليًا** قبل أي إصلاح للمصادر.

المشكلة في النسخة السابقة أنها تعاملت مع العائلات السبعة كأن كل سؤال يجب أن يحتاج نفس المستوى منها.

الصحيح:

```text
Business Question
      ↓
Required Evidence Dimensions
      ↓
Minimum Sufficiency
```

## Inputs
- Baseline من Phase 0
- تعريفات العائلات السبعة من Governance
- نتائج Forensic Audit

## Scope
تحديد الوعد التجاري فقط. لا إصلاح مصادر. لا تعديل كود.

## Dependencies
- Phase 0 مكتمل

## Exact Deliverables

### 1.1 Minimum Business Promise Definition
حدد بوضوح:

**Core (ما يجب أن يثبته DEM لكي يكون Commercial Export Intelligence):**
1. Trade Intelligence: تدفقات تجارية موثقة على مستوى HS بين مصر والدولة المستهدفة
2. Market Opportunity: تحليل الطلب والنمو والفرص غير المستغلة
3. Market Access: تكاليف الدخول وإجراءات الاستيراد للدولة/المنتج
4. Regulatory/SPS-TBT: متطلبات المطابقة للمنتج/الدولة
5. Rules of Origin: معايير المنشأ وأهلية الاتفاقيات
6. Agrifood: معلومات زراعية متخصصة (إذا كان المنتج زراعيًا)
7. Logistics: تكاليف العبور وأوقاته وموثوقية الطريق

**ملاحظة هامة:** العائلات السبعة هي Knowledge Portfolio وليست Mandatory Checklist لكل سؤال تجاري. المطلوب من كل سؤال يُحدد حسب:

```text
Business Question
      ↓
Required Evidence Dimensions
      ↓
Minimum Sufficiency
```

**Optional (مفيد لكن ليس أساسًا):**
- تحليل شركات
- مقارنات متقدمة
- توصيات مخصصة

**Complementary (مُعرَّف بوضوح للمستخدم):**
- مصادر يدوية/بوابات ويب
- بيانات عامة
- معلومات غير مؤكدة

**Future (خارجة عن النطاق الحالي):**
- رؤى تنبؤية متقدمة
- تكاملات خاصة
- بيانات حصرية

### 1.2 Minimum Sufficiency Criteria
لكل Family، حدد الحد الأدنى من Evidence Dimensions المطلوبة:

| Family | Required Evidence Dimensions | Access Tier | Notes |
|--------|------------------------------|-------------|-------|
| Trade Intelligence | Bilateral trade flows, HS-level, Egypt↔Y, documented values | Authoritative | UN Comtrade or equivalent official source |
| Market Opportunity | Demand signal, growth indicator, export potential, market attractiveness | Authoritative / Complementary |至少要一個 dimension مثبتة; Complementary acceptable if disclosed |
| Market Access | Tariff rates, duties, import procedures, permits for Y | Authoritative / Complementary | Official source preferred; Manual-accessible acceptable as Complementary |
| Regulatory/SPS-TBT | MRL, SPS/TBT requirements, conformity standards for product+Y | Authoritative | Must be country-product-specific |
| Rules of Origin | FTA eligibility, criteria, certificate requirements for Y | Authoritative / Complementary | Official source preferred |
| Agrifood | Agricultural prices, market conditions, alerts for commodity | Authoritative / Complementary | FAOSTAT or equivalent if activated |
| Logistics | Route cost, transit time, reliability Egypt→Y | Authoritative / Complementary | Route-level data required; country scores insufficient |

**Access Tier Definitions:**

| Tier | Description | Trust Level |
|------|-------------|-------------|
| Authoritative | Official API or database with provenance | Highest |
| Complementary | Manual/web-accessible sources with clear provenance | Medium |
| Manual-accessible | Human-verified web portals, no automated API | Lower |
| Unverified | No provenance, no verification | Not acceptable for Core promise |

**ملاحظة:** Business Question Profile هو الذي يحدد Required Evidence Set من العائلات السبعة، وليس كل سؤال يحتاج جميع العائلات.

## Acceptance Criteria
- [ ] Business Promise معتمد وموثق
- [ ] لكل Family حد أدنى واضح
- [ ] لا توجد قدرة غير مثبتة في الوعد
- [ ] Complementary coverage مُعرَّفة بوضوح

## Exit Gate
Business Promise + Minimum Sufficiency Criteria معتمدان.

## Stop Conditions
- إذا تعارضت Definitions مع Governance الموجودة → توقف وحسّن Governance أولاً

## What Must Not Change
- لا تعديل الكود
- لا تعديل Architecture
- لا تعديل Business Intelligence
- لا تعديل Avatar
- لا تعديل Knowledge Graph أو Multi-Agent

## Architecture Impact
لا يوجد. Phase 1 تحدد الوعد فقط.

## Evidence Required
- Business Promise Document معتمد
- Minimum Sufficiency Matrix معتمد

---

# Phase 2 — Capability Truth Model

## الهدف
إنشاء نموذج موحد للحقيقة يُفرق بين:
- Implemented
- Registered
- Configured
- Activated
- Reachable
- Returns Data
- Capability Proven
- Scope Ready
- Country/Product Ready
- Business Question Ready
- Decision-Safe
- Response-Safe

## Inputs
- Baseline من Phase 0
- Business Promise من Phase 1
- Governance definitions

## Scope
توثيق الحقيقة فقط. لا إصلاحات. لا تفعيل مصادر.

## Dependencies
- Phase 0 مكتمل
- Phase 1 مكتمل

## Exact Deliverables

### 2.1 Capability Truth Matrix
جدول واحد موثق لكل Provider:

| Provider | Implemented | Registered | Configured | Activated | Reachable | Returns Data | Capability Proven | Scope Ready | Country/Product Ready | Business Question Ready | Decision-Safe | Response-Safe | Evidence |
|----------|-------------|------------|------------|-----------|-----------|--------------|-------------------|-------------|-----------------------|------------------------|---------------|---------------|----------|
| UN Comtrade | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Trade flows HS-level) | Partial | Partial | Partial | Partial | Partial | Preview API returns real data |
| World Bank LPI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Country scores only) | ✅ | ✅ | Partial | Partial | Partial | Indicators API returns real data |
| Company Knowledge | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Internal curated knowledge) | ✅ | ✅ | Partial | Partial | Partial | Internal curated knowledge, no external API |
| FAOSTAT | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| Moaah | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| TradeData | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| ZATCA | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| GCC-Stat | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| Regulations | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | `regulations.json` missing |
| WTO ePing | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Config only, no implementation |

### 2.2 Capability Sufficiency Assessment
لكل Family، حدد:

| Family | Required Capability | Current Source | Capability Actually Proven | Gap Type |
|--------|---------------------|----------------|---------------------------|----------|
| Trade Intelligence | Bilateral trade flows, HS-level, Egypt↔Y | UN Comtrade | ✅ Proven | None |
| Market Opportunity | Demand, growth, export potential, market attractiveness | TBD after Phase 3 | ❌ | **Source Gap** |
| Market Access | Tariffs, duties, procedures, permits for Y | TBD after Phase 3 | ❌ | **Source Gap** |
| Regulatory/SPS-TBT | MRL, SPS/TBT, conformity for product+Y | TBD after Phase 3 | ❌ | **Source Gap** |
| Rules of Origin | FTA criteria, eligibility, certificate for Y | TBD after Phase 3 | ❌ | **Source Gap** |
| Agrifood | Agricultural prices, conditions, alerts | FAOSTAT (inactive) | ❌ | **Configuration Gap** |
| Logistics | Route cost, transit time, reliability Egypt→Y | World Bank LPI | ❌ | **Source Limitation** |

**ملاحظة:** الحكم النهائي للمصادر الخارجية يأتي بعد Phase 3 (Current Source Reality Revalidation).

## Acceptance Criteria
- [ ] Capability Truth Matrix مكتملة لجميع Providers
- [ ] Capability Sufficiency Assessment مكتملة لجميع Families
- [ ] لا توجد حالة غامضة (مثل "Partial" بدون دليل)
- [ ] كل Gap مصنف بشكل واضح

## Exit Gate
Capability Truth Model معتمد.

## Stop Conditions
- إذا اكتشفت أن Governance definitions تتعارض مع Evidence → توقف وحسّن Governance أولاً

## What Must Not Change
- لا تعديل الكود
- لا تعديل Architecture
- لا تعديل Business Intelligence
- لا تعديل Avatar
- لا تعديل Knowledge Graph أو Multi-Agent

## Architecture Impact
لا يوجد. Phase 2 توثّق الحقيقة فقط.

## Evidence Required
- Capability Truth Matrix معتمد
- Capability Sufficiency Assessment معتمد

---

# Phase 3 — Current Source Reality Revalidation

## الهدف
التحقق الخارجي المحدود للمصادر التي قد تؤثر على قرارات الخطة.

هذه المرحلة تسبق Activation Decisions و Semantic Integrity fixes.

## Inputs
- Capability Truth Model من Phase 2
- Business Promise من Phase 1

## Scope
فحص الواقع الحالي للمصادر فقط. لا إصلاحات. لا تفعيل.

## Dependencies
- Phase 0 مكتمل
- Phase 1 مكتمل
- Phase 2 مكتمل

## Exact Deliverables

### 3.1 Source Reality Check
لكل مصدر محتمل:

| Source | Current Status | API Available | Filtering | Country Coverage | Product/HS Coverage | Freshness | Licensing | Assertion To Verify |
|--------|---------------|---------------|-----------|------------------|---------------------|-----------|-----------|---------------------|
| UN Comtrade | ✅ Active | Preview API | Limited | Global | HS-level | 2025 max | Free | Verify licensing / activation path |
| World Bank LPI | ✅ Active | Indicators API | Limited | Global | Indicator-level | 2012-2023 | Free | Verify licensing / activation path |
| FAOSTAT | Inactive | REST API | Yes | Global | Item/Element | Recent | CC BY-NC-SA 3.0 IGO | Verify licensing / activation path |
| Moaah | Inactive | REST API | Yes | Egypt-focused | HS | Recent | Commercial | Verify licensing / activation path |
| TradeData | Inactive | REST API | Yes | 200+ countries | HS/buyer/supplier | Recent | Commercial | Verify licensing / activation path |
| ZATCA | Inactive | REST API | Limited | Saudi Arabia | HS | Recent | Open Data | Verify licensing / activation path |
| GCC-Stat | Inactive | SDMX/REST | Yes | GCC | Product | Recent | Open | Verify licensing / activation path |
| WTO ePing | Complementary | Web + XLSX | No | Global | Product | Recent | WTO | Verify complementary-only status |
| ITC Market Access Map | Complementary | Web + bulk | No | Global | HS | Recent | ITC | Verify complementary-only status |
| ITC Export Potential Map | Complementary | Web only | No | Global | Product | Recent | ITC | Verify complementary-only status |
| UNCTAD LSCI/PLSCI | Complementary | CSV only | No | Global | Route | Recent | UNCTAD | Verify complementary-only status |

### 3.2 Stale Governance Assumptions
سجّل أي افتراض governance قديم:

| Document | Assumption | Current Reality | Status |
|----------|-----------|-----------------|--------|
| `external-knowledge-portfolio-re-evaluation.md` | WTO ePing may become accessible | No verifiable public REST API with filtering | **STALE** — Update trigger condition |
| `external-knowledge-portfolio-re-evaluation.md` | World Bank LPI covers Logistics | LPI gives country scores only, not route data | **STALE** — Coverage claim needs revision |
| `SourceCapabilityResolver` | `trade → market_opportunity` | Governance explicitly forbids this mapping | **STALE** — Remove mapping |

## Acceptance Criteria
- [ ] Source Reality Check مكتمل للمصادر ذات الصلة
- [ ] Stale Governance Assumptions موثقة
- [ ] لا تم تعديل الوثائق في هذه المرحلة

## Exit Gate
واضح أي مصدر قديم وأي مصدر ما زال صالحًا.

## Stop Conditions
- إذا اكتشفت أن مصدرًا مُصدَّق له API مختلف → أوقف وحسّن Candidate Evaluation أولاً

## What Must Not Change
- لا تعديل الكود
- لا تعديل Architecture
- لا تعديل Business Intelligence
- لا تعديل Avatar
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Governance docs في هذه المرحلة

## Architecture Impact
لا يوجد. Phase 3 توثّق الواقع فقط.

## Evidence Required
- Source Reality Check موقّع
- Stale Governance Assumptions موقّعة

---

# Phase 4 — Semantic Integrity + Readiness Governance

## الهدف
منع أن يتحول اسم الـsource إلى Capability غير حقيقية، وإنشاء Production Readiness Gate موحد.

## Inputs
- Capability Truth Model من Phase 2
- Source Reality Check من Phase 3
- Governance docs الموجودة

## Scope
إصلاح Semantic Mappings فقط. لا تفعيل مصادر. لا إصلاحات كود إلا ما يخص Semantic Mapping.

## Dependencies
- Phase 2 مكتمل
- Phase 3 مكتمل

## Exact Deliverables

### 4.1 Semantic Integrity Audit
افحص وقارن:

| Current Mapping | Governance Definition | Verdict | Action |
|-----------------|----------------------|---------|--------|
| `trade → market_opportunity` | "Historical trade data alone does not satisfy Market Opportunity" | **CONTRADICTION** | Remove `market_opportunity` from trade type in `SourceCapabilityResolver` |
| `agrifood → market_opportunity` | Agrifood data ≠ Market Opportunity | **OVERCLAIM** | Remove `market_opportunity` from agrifood type |
| `food → market_opportunity` | Same as above | **OVERCLAIM** | Remove `market_opportunity` from food type |
| `logistics → logistics_market_execution` | Logistics requires route-level data, not country scores | **OVERCLAIM** | Restrict LPI to partial coverage or create separate capability |
| `market_data → market_opportunity` | Market data label ≠ Proven opportunity | **OVERCLAIM** | Remove mapping |
| `regulation → market_access + regulatory_sps_tbt + rules_of_origin` | Local JSON file cannot cover all three with current data | **OVERCLAIM** | Split capability declarations per actual source capability |
| `external_trade_intelligence → market_opportunity` | Same as trade | **CONTRADICTION** | Remove from resolver |

### 4.2 Production Readiness Gate Definition
صمم Gate موحد:

```text
Provider Readiness Levels:
1. Implemented — Code exists
2. Registered — In registry
3. Configured — Credentials/settings present
4. Activated — Registered at startup
5. Reachable — Health check passes
6. Returns Data — Returns non-empty results
7. Capability Proven — Data matches family requirement
8. Scope Ready — Covers declared scope
9. Country/Product Ready — Coverage matches target
10. Business Question Ready — Can answer the commercial question
11. Decision-Safe — Evidence supports tactical decision
12. Response-Safe — Evidence supports user-facing claim
```

**WP Closure Gate:**
لا يُغلق Provider WP إلا إذا وصل إلى مستوى **Capability Proven** على الأقل.

**No shortcuts:**
- `Implemented` ≠ `Business Ready`
- `Registered` ≠ `Activated`
- `HTTP 200` ≠ `Capability Proven`
- `Capability Proven` ≠ `Scope Ready`
- `Scope Ready` ≠ `Country/Product Ready`
- `Country/Product Ready` ≠ `Business Question Ready`
- `Business Question Ready` ≠ `Decision-Safe`
- `Decision-Safe` ≠ `Response-Safe`

### 4.3 Capability Declaration Contract
كل Capability يجب أن تكون:

```text
Declared
+
Observed
+
Proven
+
Scoped
```

## Acceptance Criteria
- [ ] Semantic Integrity Audit مكتمل
- [ ] كل contradiction مصنف
- [ ] Production Readiness Gate معتمد
- [ ] Capability Declaration Contract معتمد
- [ ] لا يوجد false capability declaration

## Exit Gate
Semantic Integrity مثبتة + Production Readiness Gate معتمد + Capability Declaration Contract معتمد.

## Stop Conditions
- إذا تطلب الإصلاح تعديل Contract > خطة منفصلة → أوقف ووثّق

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Business Intelligence architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs

## Architecture Impact
يُسمح بتعديل `SourceCapabilityResolver` فقط. لا تعديل طبقات أعلى.

## Evidence Required
- Semantic Integrity Audit موقّع
- Production Readiness Gate موقّع
- Capability Declaration Contract موقّع

---

# Phase 5 — Existing Provider Activation & Repair

## الهدف
استنفاد قيمة المصادر الموجودة قبل التفكير في مصادر جديدة.

## لكل Provider
القرار يكون واحدًا من:

```text
Keep Active
Activate
Repair
Restrict Scope
Replace
Retire
```

## Inputs
- Capability Truth Model من Phase 2
- Source Reality Check من Phase 3
- Semantic Integrity Audit من Phase 4

## Scope
تفعيل/إصلاح المصادر المُنفَّذة فقط. لا مصادر جديدة.

## Dependencies
- Phase 2 مكتمل
- Phase 3 مكتمل
- Phase 4 مكتمل

## Exact Deliverables

### 5.1 Provider Activation Plan
لكل Provider:

| Provider | Action Required | Type | Owner |
|----------|-----------------|------|-------|
| UN Comtrade | ✅ Already active | None | — |
| World Bank LPI | ✅ Already active | None | — |
| Company Knowledge | ✅ Already active | None | — |
| FAOSTAT | Configure credentials + verify JWT | Configuration | DevOps |
| Moaah | Configure credentials + verify endpoint | Configuration | DevOps |
| TradeData | Configure credentials + verify plan | Configuration + Licensing | Legal/DevOps |
| ZATCA | Configure credentials + verify endpoint | Configuration | DevOps |
| GCC-Stat | Configure credentials + verify endpoint | Configuration | DevOps |
| Regulations | Capability/Data Decision | Capability/Data Decision | Architecture |

### 5.2 Regulations Decision
قبل إنشاء الملف، طبق المعايير التالية بالترتيب:

**Decision Criteria:**

1. **Minimum Sufficiency Check (Phase 1):**
   - هل يتطلب السؤال التجاري المعتمد Regulatory/SPS-TBT evidence؟
   - إذا كان السؤال لا يتطلبها → لا حاجة لـregulations.json
   - إذا كان السؤال يتطلبها → استمر للخطوة 2

2. **Existing Provider Check:**
   - هل Regulations Knowledge Provider جزء صحيح من Production Architecture؟
   - هل البيانات موثوقة وحديثة وcountry/product-specific؟
   - هل provenance واضح؟

3. **Alternative Source Check:**
   - هل يمكن تحقيق الهدف بمصدر موجود/نشط بدل إنشاء data file؟
   - Check existing providers: Moaah, WTO ePing, ZATCA, GCC-Stat
   - Check complementary sources: ITC Market Access Map, WTO ePing
   - **ملاحظة:** Complementary sources فقط لا تُحقق Authoritative evidence المطلوب في Core Business Promise

4. **Local File Justification:**
   - إذا كان الملف المحلي هو الحل الوحيد المبرر:
     - حدد حجم البيانات المطلوب
     - حدد مصدر البيانات
     - حدد آلية التحديث
     - حدد Validation rules

**Decision Paths:**

| Path | Condition | Action |
|------|-----------|--------|
| Retain | Existing source covers requirements | Keep current provider/source |
| Activate | Provider exists but inactive | Activate with credentials |
| Enhance | Provider needs additional data/file | Add data/file to existing provider |
| Replace | Better source available | Replace with alternative provider |
| Retire | No viable source or not needed | Remove production dependency |
| Complementary | Only manual/web sources available | Document as Complementary in Business Promise |

**Result:** One of the above paths. `regulations.json` is created only if the Enhance/Replace path requires it AND the decision is approved AFTER Minimum Sufficiency check.

**لا تنشئ الملف تلقائيًا في هذه المرحلة.**

### 5.3 Activation Verification Checklist
التفعيل يجب أن يتحقق من:

```text
Credentials
Licensing
Startup registration
Reachability
Real response
Real data
Capability sufficiency
Operational reliability
```

ليس مجرد:

```text
Credential exists
```

## Acceptance Criteria
- [ ] كل Provider له خطة تفعيل أو توثيق سبب عدم التفعيل
- [ ] Regulations decision مُسجَّل
- [ ] لا يوجد "مجهول" في حالة Provider

## Exit Gate
كل Provider له حالة نهائية موثقة.

## Stop Conditions
- إذا تطلب Regulations إنشاء ملف بيانات ضخم → أوقف وحدد النطاق أولاً
- إذا تطلب Activation تعديل Closed WP → أوقف ووثّق Contract Conflict أولاً
- إذا كان Replace يتطلب New Provider غير موجود/غير معتمد مسبقًا → أوقف ووجّه إلى Phase 7 bounded Source-Admission

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Business Intelligence architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs إلا عند Contract Conflict مثبت

## Architecture Impact
يُسمح بـ:
- Configuration و Credential Store
- Targeted provider repair داخل الـowning provider/layer عند الحاجة
- Replace بـExisting Provider معتمد مسبقًا (لا يتطلب Phase 7)

ممنوع:
- Architecture redesign
- Upper-layer redesign
- Reopening Closed WPs
- Replace بـNew Provider غير موجود/غير معتمد مسبقًا (يتطلب Phase 7 bounded Source-Admission)

إلا وفق قواعد Contract Conflict / Real Defect / Security Issue / Production-Critical Defect / Proven Governance Contradiction.

## Evidence Required
- Provider Activation Plan موقّع
- Regulations Decision موقّع
- Activation Verification Checklist مكتمل لكل Provider

---

# Phase 6 — Knowledge Gap Closure

## الهدف
تحويل كل Gap إلى قرار صريح.

## Inputs
- Capability Truth Model من Phase 2
- Capability Sufficiency Assessment من Phase 2
- Source Reality Check من Phase 3
- Business Promise من Phase 1
- Provider Activation Plan من Phase 5

## Scope
تحديد قرار Gap Closure لكل Family. لا تنفيذ.

## Dependencies
- Phase 1 مكتمل
- Phase 2 مكتمل
- Phase 3 مكتمل
- Phase 5 مكتمل

## Exact Deliverables

### 6.1 Preliminary Gap Classification

هذه مصنّفات أولية فقط. القرار النهائي يعتمد على نتائج Phase 3–5.

| Family | Preliminary Classification | Rationale |
|--------|---------------------------|-----------|
| **Trade Intelligence** | Preliminary: Accept Partial / Enhance | Comtrade gives verified trade flows. Limit: 500 records, no advanced filtering. Final decision after Phase 3 source reality check. |
| **Market Opportunity** | Preliminary: Full Gap | No source provides demand/growth/export-potential yet. Final decision after Phase 3–5 confirms no existing provider can cover. |
| **Market Access** | Preliminary: Full Gap | Moaah inactive + ZATCA KSA-only. Final decision after Phase 5 activation verification. |
| **Regulatory/SPS-TBT** | Preliminary: Full Gap | No automated provider. Local file missing. Final decision after Phase 4 semantic review + Phase 5 activation check. |
| **Rules of Origin** | Preliminary: Full Gap | GCC-Stat inactive + GCC scope only. Final decision after Phase 5 activation verification. |
| **Agrifood** | Preliminary: Configuration Gap | FAOSTAT implemented but inactive. Final decision after Phase 5 credential verification. |
| **Logistics** | Preliminary: Partial / Enhancement Needed | LPI gives country scores. Final decision after Phase 3 confirms no route-level source available. |

### 6.2 Gap Closure Decision Tree

لكل Gap، افحص بالترتيب قبل اللجوء إلى New Provider:

```text
1. Configuration — Activate existing provider with correct credentials
2. Implementation Fix — Fix code bug in existing provider
3. Scope Restriction — Reduce declared scope to match actual capability
4. Existing Provider Enhancement — Add data/file to existing provider
5. Source Composition — Combine multiple existing providers
6. New Provider — Must go through Phase 7
7. Complementary Acceptance — Document permanently in Business Promise
8. Not Required — Document why and move to Optional/Future
```

### 6.3 Gap Closure Decision Options

| Option | Action |
|--------|--------|
| Configuration | Activate existing provider with correct credentials |
| Implementation Fix | Fix code bug in existing provider |
| Scope Restriction | Reduce declared scope to match actual capability |
| Existing Provider Enhancement | Add data/file to existing provider |
| Source Composition | Combine multiple existing providers |
| New Provider | Must go through Phase 7 |
| Complementary Accepted | Document permanently in Business Promise |
| Not Required for Minimum Promise | Document why and move to Optional/Future |

**قاعدة هامة:**

```text
Complementary
≠
Authoritative
≠
Core Minimum Sufficiency
```

إذا كان الـBusiness Question المعتمد يتطلب `Authoritative Evidence`، فإن `Complementary Accepted` لا يغلق Gap Core Minimum. Complementary تبقى طبقة مكشوفة للمستخدم فقط.

## Acceptance Criteria
- [ ] كل Family لها قرار Gap Closure واحد واضح
- [ ] لا توجد حالة "غير محدد"
- [ ] Complementary coverage مُعرَّفة بوضوح في Business Promise
- [ ] Gap Closure Decision Tree مُتبع لكل Gap

## Exit Gate
كل Gap له قرار واضح.

## Stop Conditions
- إذا احتاج Gap قرار New Provider → يتم تسجيل القرار والتقدم عبر Phase 7 bounded source-admission flow دون إعادة فتح مراحل سابقة
- بعد approval/implementation/activation/provider-proven → استمر في المراحل التالية
- إذا تطلب التنفيذ تعديل Closed WP → أوقف ووثّق Contract Conflict أولاً

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Business Intelligence architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs إلا عند Contract Conflict مثبت

## Architecture Impact
لا يوجد. Phase 6 يحدد القرارات فقط.

## Evidence Required
- Gap Closure Matrix موقّع
- Gap Closure Decisions موقّعة
- Rationales موثقة لكل قرار

---

# Phase 7 — Source Candidate Evaluation

## الهدف
تقييم المرشحين للمصادر الناقصة فقط.

## Inputs
- Gap Closure Matrix من Phase 6
- Source Reality Check من Phase 3
- Provider Ceiling = 7

## Scope
Phase 7 = Candidate Evaluation + bounded Source-Admission.

**لـNew Provider المعتمد فقط:**
```text
Candidate Evaluation
    ↓
Governance Approval
    ↓
Admission Decision
    ↓
bounded implementation/activation handoff
    ↓
Capability Proven
    ↓
Return to Phase 8
```

هذا ليس تنفيذًا عامًا؛ بل مسار مقيد فقط للـapproved New Provider.

## Dependencies
- Phase 3 مكتمل
- Phase 6 مكتمل

## Exact Deliverables

### 7.1 Candidate Evaluation
لكل Gap الذي تقرر Phase 6 أنه يحتاج New Provider:

| Gap | Candidate | Knowledge Value | Unique Value | API | Filtering | Countries | Products | Freshness | Licensing | Feasibility | Provider Ceiling Impact | Admission Decision |
|------|-----------|-----------------|--------------|-----|-----------|-----------|----------|-----------|-----------|-------------|------------------------|----------|
| Market Opportunity | ITC Export Potential Map | Very High | High | Web only | No | Global | Product | Recent | ITC terms | Low (no API) | N/A | Complementary Only |
| Market Opportunity | UN Comtrade (re-analysis) | Low | Low | REST | Limited | Global | HS | 2025 max | Free | High | Already have | Insufficient |
| Market Access | WTO Timeseries API | High | High | REST (key required) | Yes | Global | HS | Recent | WTO | Medium | +1 | Candidate |
| Regulatory/SPS-TBT | WTO ePing | Critical | High | Web + XLSX | No | Global | Product | Recent | WTO | Low (no API) | N/A | Complementary Only |
| Rules of Origin | ITC Rules of Origin Facilitator | Medium | Medium | Web only | No | Global | Product | Recent | ITC terms | Low | N/A | Complementary Only |
| Logistics | Shipping APIs (various) | High | High | REST | Yes | Route-specific | Route | Real-time | Commercial | Medium | +1 | Candidate |

**ملاحظة:** TradeData هو Existing Provider (Inactive) وليس New Provider Candidate. تتم معالجته من خلال Phase 5 Activation/Repair.

### 7.2 Provider Ceiling Analysis

**التفريق الأساسي:**

```text
Implemented Providers
≠
Operational Production Provider Ceiling
```

**الوضع الحالي (من Baseline):**

| العنصر | العدد | الملاحظات |
|--------|-------|-----------|
| إجمالي الـProviders المُنفَّذة ككود | 9 | UN Comtrade, World Bank LPI, FAOSTAT, Moaah, TradeData, ZATCA, GCC-Stat, Regulations, Company Knowledge |
| منها Active / Operational | 2 | UN Comtrade, World Bank LPI |
| Company Knowledge | 1 | داخلي، لا يحسب ضمن الـCeiling |
| Config-only / Inactive | 6 | FAOSTAT, Moaah, TradeData, ZATCA, GCC-Stat, Regulations |
| **Operational Production Provider Ceiling** | **7** | الحد الأقصى المسموح به للمصادر الإنتاجية |

**قواعد Provider Ceiling:**

1. `Provider Ceiling = 7` يخص **Production Operational Portfolio** فقط.
2. Company Knowledge لا يُحسب ضمن الـ7 لأنه مصدر داخلي.
3. Provider له كود فقط أو config فقط أو inactive لا يُحسب ضمن الـ7.
4. Provider إضافي لا يدخل Production إلا بعد Governance Approval.
5. لإضافة Provider جديد: must deactivate/merge existing OR request ceiling expansion.

**الوضع الحالي:**
- Active Production Providers: 2 (UN Comtrade, World Bank LPI)
- Available slots within ceiling: 5
- To activate inactive provider: requires credentials + verification
- To add new provider: requires Governance Approval + ceiling management

### 7.3 Bounded Source-Admission Flow
لـNew Provider المعتمد فقط:

```text
Candidate Evaluation
    ↓
Governance Approval
    ↓
Admission Decision
    ↓
bounded implementation/activation handoff
    ↓
Capability Proven
    ↓
Return to Phase 8
```

## Acceptance Criteria
- [ ] كل New Provider المعتمد له تقييم مكتمل + admission decision
- [ ] لا يوجد New Provider بدون governance approval
- [ ] Provider Ceiling impact موثق لكل admission
- [ ] Existing Providers لا تُعالج كـNew Providers في Phase 7

## Exit Gate
كل New Provider المعتمد وصل إلى:
- Capability Proven

**ملاحظة:** `Admission Decision + bounded handoff plan` هو حالة وسيطة فقط، وليس Exit Gate. لا يسمح بالانتقال إلى Phase 8 إلا بعد Capability Proven.

## Stop Conditions
- إذا تطلب New Provider admission تعديل Closed WP → أوقف ووثّق Contract Conflict أولاً
- إذا تطلب Candidate تعديل Architecture → أوقف ووثّق Contract Conflict أولاً

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Business Intelligence architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs إلا عند Contract Conflict مثبت

## Architecture Impact
Phase 7 يسمح بـ:
- Candidate Evaluation
- bounded implementation/activation handoff للـNew Provider المعتمد فقط

لا يسمح بـ:
- تنفيذ عام
- تعديل Architecture
- تعديل Upper-layer

## Evidence Required
- Candidate Evaluation موقّع
- Provider Ceiling Analysis موقّع
- Source Admission Decision موقّع
- Provider Admission Evidence موقّع

---

# Phase 8 — Research + Evidence + BI Alignment

## الهدف
ربط طبقة Knowledge الجديدة مباشرة بالطبقة التي بنيناها بالفعل، وضمان أن Research + Evidence + BI تعكس الحقيقة التشغيلية الفعلية.

## Inputs
- Capability Truth Model من Phase 2
- Semantic Integrity Audit من Phase 4
- Provider Activation Plan من Phase 5
- Gap Closure Decisions من Phase 6
- Source Admission Decision / Provider Admission Evidence من Phase 7

## Scope
تحديثات مستهدفة في Research/Evidence/BI فقط. لا إعادة تصميم.

## Dependencies
- Phase 2 مكتمل
- Phase 4 مكتمل
- Phase 5 مكتمل
- Phase 6 مكتمل
- Phase 7 مكتمل

## Exact Deliverables

### 8.1 Research Query Planner Alignment
- هل `ResearchQueryPlanner` يولد queries للعائلات التي ليس لها مصادر نشطة؟
- هل Discovery يكتشف المصادر الصحيحة للـ queries المُولَّدة؟
- هل intent_profile يعكس الواقع وليس الافتراضات؟
- هل intent_profile مرتبط بالـ Capability Truth Model؟

### 8.2 Evidence Integrity
- هل كل Evidence يحتفظ بـ:
  - Source
  - Source Type
  - Retrieved At
  - Data Date
  - Country Scope
  - Product / HS Scope
  - Geographic Scope
  - Granularity
  - Units
  - Currency
  - Freshness
  - Confidence
  - Transformation Path
- هل Evidence traceable chain كامل من Source → Finding → Business Fact → Opportunity/Risk/Entity؟

### 8.3 Business Intelligence Alignment
- هل `BusinessIntelligenceSynthesizer` ينتج limitations صحيحة عندما لا يوجد source؟
- هل `unsupported_dimensions` يُبلغ عنها بوضوح؟
- هل `CoverageBuilder` يحسب التغطية بناءً على المصادر الفعلية وليس المُسجَّلة؟
- هل BI يمنع:
  ```text
  No Source
  → Empty Dimension
  → Inferred Fact
  ```
  ويستبدلها بـ:
  ```text
  No Source
  → Unsupported Dimension
  → Limitation
  ```

### 8.4 Findings & Verification Targets
| Component | Issue | Verification Target | Priority |
|-----------|-------|---------------------|----------|
| `SourceCapabilityResolver` | Phase 4 semantic corrections | Verify Phase 4 semantic corrections are reflected in Research/Evidence/BI behavior. | P0 |
| `ResearchQueryPlanner` | Auto-generates dimensions beyond available sources | Verify planner starts from Business Question → Required Evidence Dimensions, not from all 7 families by default. | P1 |
| `CoverageBuilder` | Counts entries not unique sources | ✅ Fixed in 0a643af | ✅ Done |
| `BusinessIntelligenceSynthesizer` | Meta-findings in output | ✅ Fixed in 0a643af | ✅ Done |
| `EvidenceChain` | Missing provenance fields | Verify all Evidence items include required provenance fields. | P1 |

## Acceptance Criteria
- [ ] لا يوجد false capability declaration في الكود
- [ ] Research/BI ينتج limitations صحيحة للمصادر غير المتاحة
- [ ] Provenance كامل للبيانات
- [ ] Evidence traceability chain مكتمل
- [ ] Missing Knowledge Rule مطبق في Research/Evidence/BI

## Exit Gate
Research + Evidence + BI تعكس الحقيقة التشغيلية الفعلية.

## Stop Conditions
- إذا تطلب الإصلاح تعديل Architecture → أوقف ووثّق Contract Conflict أولاً

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs

## Architecture Impact
يُسمح بتعديل Research/Evidence/BI فقط. لا تعديل Decision أو Strategic Reasoning أو Replanning.

## Evidence Required
- Research Alignment Report موقّع
- Evidence Integrity Report موقّع
- BI Alignment Report موقّع

---

# Phase 9 — Decision + Strategic Reasoning Integrity

## الهدف
إثبات أن نقص المعرفة **لا يتسرب إلى الـAI Core كقرار كاذب**.

هذه مرحلة جديدة ومهمة جدًا. الغرض هو إثبات أن:

```text
Missing Knowledge
must never become
Unsupported Decision
or Unsupported Strategic Conclusion
or Unsupported User-facing Claim
```

## Inputs
- Capability Truth Model من Phase 2
- Semantic Integrity Audit من Phase 4
- Provider Activation Plan من Phase 5
- Gap Closure Decisions من Phase 6
- Research + Evidence + BI Alignment من Phase 8

## Scope
التحقق من Decision/Strategic Reasoning/Replanning فقط. لا تعديل Research/Evidence/BI.

## Dependencies
- Phase 2 مكتمل
- Phase 4 مكتمل
- Phase 5 مكتمل
- Phase 6 مكتمل
- Phase 8 مكتمل

## Exact Deliverables

### 9.1 Decision Integrity Check
افحص:

```text
Research
   ↓
Evidence
   ↓
BI
   ↓
Decision Context
   ↓
Decision
```

- هل Decision يعلن فقط ما يثبته Evidence؟
- هل Decision يعالج Unsupported Dimensions كـ Limitation وليس كـ Fact؟
- هل Decision لا يختار Recommendation بدون Evidence؟

### 9.2 Strategic Reasoning Integrity Check
افحص:

```text
Evidence
   ↓
BI
   ↓
Strategic Context
   ↓
Strategic Reasoning
   ↓
Strategic Conclusion
```

- هل Strategic Reasoning يظل مسؤولًا عن:
  - Strategic interpretation
  - Trade-offs
  - Constraints
  - Longer-horizon reasoning
- ولا يتحول إلى مصدر بيانات؟
- هل Strategic Reasoning لا يختار Conclusion بدون Evidence؟

### 9.3 Replanning Integrity Check
افحص:

```text
Outcome
   ↓
Feedback
   ↓
Constraint
   ↓
Failure
   ↓
New Evidence
   ↓
Replanning
```

- هل Replanning تستجيب فقط إلى:
  - New Evidence
  - Outcome
  - Feedback
  - Constraint
  - Failure
- ولا تستخدم غياب المصدر كذريعة لاختراع معلومة؟

### 9.4 Verification Targets
| Component | Issue | Verification Target | Priority |
|-----------|-------|---------------------|----------|
| Decision Engine | Uses unsupported dimension as fact | Verify no unsupported dimension used as fact | P0 |
| Strategic Reasoning | Infers market opportunity from trade alone | Verify no market opportunity inferred without explicit source | P0 |
| Replanning | Fabricates fallback when source missing | Verify explicit degradation when source missing | P0 |

## Acceptance Criteria
- [ ] لا توجد recommendation مبنية على unsupported data
- [ ] لا توجد strategic conclusion تتجاوز Evidence
- [ ] Replanning لا تختبر معلومات بدون Evidence
- [ ] Missing Knowledge Rule مطبق في Decision/Strategic Reasoning/Replanning

## Exit Gate
إثبات:

```text
Knowledge limitation
≠
Decision fabrication
```

## Stop Conditions
- إذا تطلب الإصلاح تعديل Architecture → أوقف ووثّق Contract Conflict أولاً

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs

## Architecture Impact
Phase 9 هي مرحلة تحقق فقط. لا تنفذ أي تعديل. أي فشل يوجّه إلى Targeted Remediation في الـowning layer → Retest → Resume. لا تعديل Decision/Strategic Reasoning/Replanning هنا.

## Evidence Required
- Decision Integrity Report موقّع
- Strategic Reasoning Integrity Report موقّع
- Replanning Integrity Report موقّع

---

# Phase 10 — Country / Product / Route Readiness

## الهدف
الانتقال من:

```text
Provider Ready
```

إلى:

```text
Business Question Ready
```

## Inputs
- Capability Truth Model من Phase 2
- Provider Activation Plan من Phase 5
- Gap Closure Decisions من Phase 6
- Business Promise من Phase 1
- Minimum Sufficiency Criteria من Phase 1

## Scope
تقييم الجاهزية على مستوى السوق/المنتج/الطريق. لا تنفيذ.

## Dependencies
- Phase 1 مكتمل
- Phase 2 مكتمل
- Phase 5 مكتمل
- Phase 6 مكتمل
- Phase 8 مكتمل
- Phase 9 مكتمل

## Exact Deliverables

### 10.1 Readiness Scenarios
استخدم هذه الأمثلة لإثبات المبدأ:

| Scenario | Market | Product | Trade | Opportunity | Market Access | Regulatory | Origin | Agrifood | Logistics | Overall |
|----------|--------|---------|-------|-------------|---------------|------------|--------|----------|-----------|---------|
| 1 | Jordan (Levant) | Vegetables (HS 07) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **Computed at execution** |
| 2 | Saudi Arabia (GCC) | Dates (HS 08) | ✅ | ❌ | ⚠️ | ❌ | ⚠️ | ❌ | ❌ | **Computed at execution** |
| 3 | Germany (EU) | Citrus (HS 08) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **Computed at execution** |
| 4 | Kenya (East Africa) | Coffee (HS 09) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **Computed at execution** |
| 5 | China (East Asia) | Textiles (HS 61) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **Computed at execution** |

**ملاحظة:** هذه السيناريوهات هي baseline test profiles وليست أحكامًا نهائية ثابتة. قيم `Overall` لا تُحسب مسبقًا.

**حساب الجاهزية:** يُحسب `Overall Readiness` وقت التنفيذ من الأدلة الفعلية وفقًا للمنطق التالي:

```text
Overall Readiness = Required Evidence Set ∩ Proven Available Evidence
                  + Minimum Sufficiency Check
                  + Decision-Safe / Response-Safe conditions
```

النتيجة النهائية: `Ready / Conditionally Ready / Not Ready`

## Acceptance Criteria
- [ ] كل Scenario له تقييم واضح
- [ ] لا يوجد سوق يعتبر "Ready" بدون دليل
- [ ] Limitations موثقة لكل سوق
- [ ] Minimum Sufficiency Criteria مطبقة على كل Scenario

## Exit Gate
واضح ما هو Ready وما هو Not Ready ولماذا.

## Stop Conditions
- إذا تطلب السيناريو مصدرًا جديدًا → يتم توجيه القرار إلى Phase 7 bounded source-admission flow
- بعد إتمام Phase 7 admission flow → استمر في Phase 8 فصاعدًا

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Business Intelligence architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs

## Architecture Impact
لا يوجد. Phase 10 يقيّم الجاهزية فقط.

## Evidence Required
- Readiness Scenarios موقّعة
- Readiness Assessment Framework موقّع

---

# Phase 11 — End-to-End Decision-Safe + Response-Safe Acceptance

## الهدف
اختبار الـcanonical lifecycle كاملًا، وليس Research → Response فقط.

## Test Path

### Canonical AI Lifecycle

```text
Employee Request
 ↓
Intent
 ↓
Goal
 ↓
Plan
 ↓
Decision
 ↓
Strategic Reasoning
 ↓
Replanning
 ↓
Mission
 ↓
Task
 ↓
Execution
 ↓
Outcome
 ↓
Feedback
 ↓
Memory
 ↓
Future Decision
 ↓
ResponseBuilder
 ↓
IntentContent
 ↓
Avatar
```

### Knowledge Plane (Separate)

```text
External Knowledge Sources
        ↓
Research
        ↓
Evidence
        ↓
Business Intelligence
        ↓
Decision / Strategic Reasoning Context
```

**القاعدة:** Knowledge Plane تغذي Decision/Strategic Reasoning/Response، وهي ليست مراحل داخل الـcanonical lifecycle.

## Inputs
- Capability Truth Model
- Provider Activation Plan
- Gap Closure Decisions
- Readiness Scenarios
- Decision Integrity Report من Phase 9

## Scope
اختبار End-to-End كامل. لا إصلاحات.

## Dependencies
- Phase 9 مكتمل
- Phase 10 مكتمل

## Exact Deliverables

### 11.1 Evidence Safety
كل claim له دليل.

### 11.2 Decision Safety
لا توجد recommendation مبنية على unsupported data.

### 11.3 Strategic Safety
لا توجد strategic conclusion تتجاوز Evidence.

### 11.4 Memory Safety
Memory لا تحول نتيجة غير مؤكدة إلى حقيقة مستقبلية.

### 11.5 Response Safety
ResponseBuilder لا يضيف claims جديدة.

### 11.6 Avatar Safety
Avatar يعرض:

```text
Supported findings
+
Confidence
+
Limitations
+
Provenance
```

ولا ينشئ استنتاجًا جديدًا.

### 11.7 Failure / Partial Coverage
إذا تعذر مصدر:

```text
System degrades explicitly
```

ولا:

```text
fallback → fabricated answer
```

### 11.8 Test Scenarios
لكل سيناريو، تحقق:

| Scenario | Expected Behavior | Baseline Anti-Pattern | Gap |
|----------|-------------------|-----------------------|-----|
| Egypt → Jordan vegetables | Shows trade flows + limitations for other families | Verify system does not show fake opportunities/risks from stub data | **Overclaim** |
| Egypt → Saudi Arabia dates | Shows trade flows + ZATCA if activated | Verify system does not show absent market access as available | **Gap** |
| Egypt → EU citrus | Shows trade flows + regulatory limitations | Verify system does not claim regulatory data when source is absent | **Gap** |

## Acceptance Criteria
- [ ] لا يوجد Overclaim في أي سيناريو
- [ ] Limitations ظاهرة بوضوح
- [ ] Provenance كامل
- [ ] لا توجد meta-findings في output
- [ ] Missing Knowledge Rule مطبق في End-to-End flow
- [ ] ResponseBuilder → IntentContent → Avatar لا يضيف claims جديدة

## Exit Gate
End-to-End Decision-Safe / Response-Safe commercial behavior passed without overclaim.

## Stop Conditions
- إذا تطلب الاختبار تعديل Architecture → أوقف ووثّق Contract Conflict أولاً

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs

## Architecture Impact
لا يوجد. Phase 11 يختبر فقط.

## Evidence Required
- Acceptance Test Report موقّع
- End-to-End Evidence Log مكتمل
- No Overclaim Certificate

---

# Phase 12 — Governance / Documentation Reconciliation

## الهدف
بعد انتهاء التنفيذ فقط، تصبح الوثائق مطابقة للحقيقة الجديدة.

## Update

```text
Current Status
Capability Matrix
Provider Status
Knowledge Portfolio
Source mappings
Research status
BI limitations
Acceptance results
Security status
Commercial readiness
```

## Inputs
- جميع المراحل السابقة

## Scope
تحديث الوثائق فقط. لا تعديل Architecture.

## Dependencies
- جميع المراحل السابقة مكتملة

## Exact Deliverables

### 12.1 Documents to Update
| Document | Required Update |
|----------|-----------------|
| `PLAN.md` | Business Promise, Capability Model, Source Status |
| `CURRENT_STATUS.md` | Project status, source availability, gaps |
| `external-knowledge-portfolio-re-evaluation.md` | Stale assumptions, capability mappings |
| Provider metadata | Reflect actual activation status |

### 12.2 Documents NOT to Modify
- Closed WP contracts (لا تعيد فتحها)
- Architecture contracts الثابتة
- Provider admission criteria (لا تعديل إلا إذا ظهر conflict مثبت)

## Acceptance Criteria
- [ ] لا توجد وثيقة تتعارض مع الحقيقة التشغيلية
- [ ] لا توجد capability claim بدون مصدر
- [ ] لا يوجد status "Complete" بدون دليل

## Exit Gate
Governance Reconciliation مكتمل.

## Stop Conditions
- إذا تطلب التحديث تعديل Closed WP → أوقف ووثّق Contract Conflict أولاً

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs

## Architecture Impact
لا يوجد. Phase 12 تحدث الوثائق فقط.

## Evidence Required
- Governance Reconciliation Report موقّع
- Document Update Log مكتمل

---

# Phase 13 — Final Closure

## الهدف
الإغلاق النهائي، وليس مجرد نجاح الاختبارات.

## Inputs
- جميع المراحل السابقة

## Scope
إثبات أن DEM وصل إلى حالة Commercial Readiness حقيقية.

## Dependencies
- جميع المراحل السابقة مكتملة

## Exact Deliverables

### 13.1 Final Gates
| Gate | Evidence |
|------|----------|
| Architecture | Canonical lifecycle intact |
| Knowledge | Capabilities proven, Coverage scoped, Gaps explicit |
| Research | Queries match real capabilities |
| Evidence | Provenance كامل |
| BI | Only evidence-supported intelligence |
| Decision | No unsupported tactical decision |
| Strategic Reasoning | No unsupported strategic conclusion |
| Replanning | Responds only to valid feedback/evidence |
| Memory | Does not elevate uncertain data into fact |
| ResponseBuilder | Transforms truth, does not create truth |
| Avatar | Presents truth, does not create decisions |
| Commercial Readiness | Business Question → Required Evidence → Proven Capability → Safe Decision → Safe Explanation |

### 13.2 Final State
عند تحقيق جميع Exit Criteria:

```text
MASTER REMEDIATION PLAN = EXECUTION COMPLETE
DEM COMMERCIAL READINESS REMEDIATION = PROVEN FOR APPROVED BUSINESS PROMISE
```

**ملاحظة:** لا يُعلن عن DEM كمنتج تجاري كامل إلا بعد تحقق جميع Gates للوعد الأساسي المعتمد. Complementary/Optional/Future capabilities لا تُعتبر blockers.

### 13.3 إذا لم يتم تحقيق جميع Exit Criteria
توثيق:
- أي Criteria لم تحقق
- السبب
- الإجراء المطلوب لتحقيقه
- عدم الإعلان عن DEM كمنتج تجاري كامل

## Acceptance Criteria
- [ ] Commercial Readiness proven for the approved Business Promise and its defined Business Questions
- [ ] Complementary capabilities documented and disclosed to users
- [ ] Optional capabilities documented as non-blocking
- [ ] Future capabilities documented as out-of-scope
- [ ] جميع Final Gates المُحقَّقة للوعد الأساسي
- [ ] لا توجد capability claim خارجة عن الوعد بدون disclosure واضح

## Exit Gate
Final Commercial Readiness Closure مكتمل للوعد الأساسي المعتمد.

**ملاحظة:** Complementary capabilities, Optional capabilities, و Future capabilities لا تُعتبر blockers طالما هي معلنة ولا تدخل ضمن الوعد الأساسي.

## Stop Conditions
- إذا لم تحقق جميع Gates للوعد الأساسي → وثّق Missing Criteria ولا تعلن COMPLETE
- عدم اكتمال Complementary/Optional/Future capabilities لا يمنع الإغلاق

## What Must Not Change
- لا تعديل Architecture
- لا تعديل Avatar architecture
- لا تعديل Knowledge Graph أو Multi-Agent
- لا تعديل Closed WPs

## Architecture Impact
لا يوجد. Phase 13 تغلق الخطة فقط.

## Evidence Required
- Final Closure Report موقّع
- جميع Gates مُثبتة بأدلة

---

## Closed Work Package Protection

لا تعاد أي Work Package مغلقة إلا إذا ثبت:

```text
1. Contract Conflict
2. Real Defect
3. Security Issue
4. Production-Critical Defect
5. Proven Governance Contradiction
```

والمسار المفضل دائمًا:

```text
Targeted Remediation
```

وليس:

```text
Reopen + Redesign
```

---

## Recursion Prevention

ممنوع:

```text
Full forensic audit after every phase
Repeatedly proving the same fact
Adding provider before proving the gap
Fixing upper layers for lower-layer source absence
Using fixtures as production evidence
Using HTTP 200 as capability proof
Using provider count as readiness
Using historical trade as opportunity
Using LPI as route freight
Using complementary sources as production
Using planned sources as available
Creating second decision engines
Creating second planning engines
Changing Architecture without evidence
Opening Multi-Agent
Opening Knowledge Graph
Redesigning Avatar
Redesigning BI
```

---

## Execution Order

```text
Phase 0: Baseline Freeze + Security
    ↓ Gate
Phase 1: Honest Commercial Promise
    ↓ Gate
Phase 2: Capability + Evidence Truth
    ↓ Gate
Phase 3: Current Source Reality Revalidation
    ↓ Gate
Phase 4: Semantic Integrity + Readiness Governance
    ↓ Gate
Phase 5: Existing Provider Activation & Repair
    ↓ Gate
Phase 6: Knowledge Gap Closure
    ↓ Gate
Phase 7: Candidate / Source Composition
    ↓ Gate
Phase 8: Research + Evidence + BI Alignment
    ↓ Gate
Phase 9: Decision + Strategic Reasoning Integrity
    ↓ Gate
Phase 10: Country / Product / Route Readiness
    ↓ Gate
Phase 11: End-to-End Decision-Safe / Response-Safe Acceptance
    ↓ Gate
Phase 12: Governance Reconciliation
    ↓ Gate
Phase 13: Final Closure
```

---

## Critical Path Notes

1. **Phase 0 يُهمل غالبًا** — لا تتخطاه. Baseline الموحد هو ما يمنع العودة للتحقيق من البداية.
2. **Phase 1 يُهمل غالبًا** — لا تحاول إصلاح المصادر قبل أن تعرف ما الذي تعد المستخدم به.
3. **Phase 3 هو الذي يمنع العودة للfalse assumptions** — لا تتخطى Current Source Reality.
4. **Phase 4 هو الذي يمنع العودة للfalse claims** — لا تتخطى Semantic Integrity.
5. **Phase 6 هو نقطة القرار** — هنا تحدد ما الذي يمكن إصلاحه وما الذي يحتاج مصدرًا جديدًا.
6. **Phase 9 هو الذي يثبت سلامة الـAI Core** — لا تعتبر Pipeline Passed = Decision Safe.
7. **Phase 11 هو الذي يثبت الجاهزية** — لا تعتبر Research Passed = Business Ready.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Stakeholder يرفض Business Promise الواقعي | Medium | High | عرض الأدلة من Forensic Audit |
| Provider Activation يفشل بسبب credentials | Medium | Medium | وثّق Alternatives وComplementary coverage |
| Gap Closure يتطلب مصادر جديدة | High | High | اتبع Phase 7 بصرامة |
| Semantic Mapping fixes تؤثر على existing code | Low | Medium | راجع Phase 8 كجزء من Exit Gate |
| Governance docs تتعارض مع الحقيقة | Medium | Medium | وثّق في Phase 3، لا تعدل في هذه المرحلة |
| Decision/Strategic Reasoning تتسرب فيها knowledge gaps | Medium | High | راجع Phase 9 كجزء من Exit Gate |

---

## Out of Scope

### Plan Mode (Current)
هذه الخطة **لا تشمل** الآن:

- Code implementation
- Provider implementation
- Credential configuration
- Data file creation
- BI redesign
- Avatar modification
- Market ranking studies
- Provider count expansion beyond ceiling

### Execution Mode (Later)
عند الانتقال إلى Execution، تبقى خارج النطاق دائماً:

- Multi-Agent reopening
- Knowledge Graph reopening
- Architecture redesign
- Avatar redesign
- BI redesign

إلا عند وجود Contract Conflict / Real Defect / Security Issue / Production-Critical Defect مثبت.

**ملاحظة:** Out of Scope ينطبق على Plan Mode الحالي فقط. مراحل التنفيذ اللاحقة ستتضمن أعمالاً مثل:
- Provider activation
- Targeted provider repair
- Credential configuration
- Data updates
- Research/Evidence/BI corrections
- Decision/Reasoning corrections
عندما تكون هذه الأعمال معتمدة داخل الخطة.

---

```text
Plan reviewed for cross-phase consistency. Ready for explicit transition to Execution after owner approval.
```
