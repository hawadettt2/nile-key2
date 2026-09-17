# Master Remediation Plan — DEM Commercial Readiness Reset

**Plan ID:** 1789672443844-master-remediation-plan  
**Branch:** main  
**Mode:** Plan Only — No Implementation  
**Authority:** Forensic Audit findings (2026-09-17)  
**Governing Baseline:** Commit `0a643af6d6ad9959dd529aae28681dd509d71765` + Commit `28539a3bb053554de9af0b9d1a1dae043f62e8e7` + Current `.env` and `backend/data/` state  
**Objective:** إعادة ضبط الأساس المعرفي والتشغيلي والتجاري لـDEM بناءً على الحقيقة التشغيلية الحالية، دون افتراض أي قدرة لا يثبتها مصدر ودليل.

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

## Phase 0 — Baseline Freeze + Security

### الهدف
تثبيت الحالة الحالية كمرجع، وعلاج المخاطر الأمنية، ومنع العودة للتحقيق من البداية.

### Inputs
- آخر Forensic Audit عن Production Knowledge Coverage
- آخر Forensic Audit عن Production Knowledge Readiness
- Commit `0a643af6d6ad9959dd529aae28681dd509d71765`
- Commit `28539a3bb053554de9af0b9d1a1dae043f62e8e7`
- ملف `.env` الحالي
- مجلد `backend/data/` الحالي

### Deliverables

#### 0.1 Baseline Document
وثيقة واحدة تحتوي على:
- كل Provider المُنَفَّذ حالياً
- حالة Runtime Activation لكل منها (Active / Inactive / Conditional)
- حالة Credentials (Configured / Missing / Placeholder)
- حالة Data Files (Present / Missing / Test-only)
- Known Gaps لكل Family
- Closed WPs التي تؤثر على هذه الخطة
- Accepted Complementary Coverage
- Known Implementation Defects

#### 0.2 Security Track
- اعتبار أي credential ظهر في التقارير السابقة **compromised**
- توثيق أن `LLM_API_KEY` في `.env` يجب تدويره
- توثيق أن أي credential قديم في git history يجب استبداله
- منع أي secret من الظهور في هذه الخطة أو أي خطة لاحقة

### Acceptance Criteria
- [ ] Baseline document موحد ومعتمد
- [ ] Security issues موثقة بدون تعديل الكود
- [ ] لا توجد ثغرات أمنية غير موثقة
- [ ] كل stakeholder وافق على Baseline

### Exit Gate
Baseline معتمد + Security Track موثق.

### Stop Conditions
- إذا ظهر credential جديد غير موثق → توقف حتى توثيقه
- إذا ظهر source جديد غير مصنف → توقف حتى تصنيفه

---

## Phase 1 — Define the Honest Commercial Promise

### الهدف
تحديد **ما الذي نعد المستخدم به فعليًا** قبل أي إصلاح للمصادر.

### Inputs
- Baseline من Phase 0
- تعريفات العائلات السبعة من Governance
- نتائج Forensic Audit

### Deliverables

#### 1.1 Minimum Business Promise Definition
حدد بوضوح:

**Core (ما يجب أن يثبته DEM لكي يكون Commercial Export Intelligence):**
1. Trade Intelligence: تدفقات تجارية موثقة على مستوى HS بين مصر والدولة المستهدفة
2. Market Opportunity: تحليل الطلب والنمو والفرص غير المستغلة
3. Market Access: تكاليف الدخول وإجراءات الاستيراد للدولة/المنتج
4. Regulatory/SPS-TBT: متطلبات المطابقة للمنتج/الدولة
5. Rules of Origin: معايير المنشأ وأهلية الاتفاقيات
6. Agrifood: معلومات زراعية متخصصة (إذا كان المنتج زراعيًا)
7. Logistics: تكاليف العبور وأوقاته وموثوقية الطريق

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

#### 1.2 Minimum Sufficiency Criteria
لكل Family، حدد الحد الأدنى من Evidence المطلوب:

| Family | Minimum Evidence |
|--------|------------------|
| Trade Intelligence | بيانات رسمية/تجارية موثقة لتدفقات مصر ↔ الدولة Y للمنتج X |
| Market Opportunity | مصدر واحد على الأقل يثبت demand/growth/export-potential للسوق |
| Market Access | tariff + procedures + permits للدولة/المنتج |
| Regulatory/SPS-TBT | MRL/SPS/TBT requirements للدولة/المنتج |
| Rules of Origin | FTA eligibility + criteria للاتفاقية/المنتج |
| Agrifood | أسعار/ظروف سوق/تنبيهات للسلعة الزراعية |
| Logistics | تكلفة/وقت/موثوقية الطريق مصر → الدولة Y |

### Acceptance Criteria
- [ ] Business Promise معتمد وموثق
- [ ] لكل Family حد أدنى واضح
- [ ] لا توجد قدرة غير مثبتة في الوعد
- [ ] Complementary coverage مُعرَّفة بوضوح

### Exit Gate
Business Promise + Minimum Sufficiency Criteria معتمدان.

### Stop Conditions
- إذا تعارضت Definitions مع Governance الموجودة → توقف وحسّن Governance أولاً

---

## Phase 2 — Capability Truth Model

### الهدف
إنشاء نموذج موحد للحقيقة يُفرق بين:
- Implemented
- Registered
- Activated
- Reachable
- Returns Data
- Capability Proven
- Country/Product Ready
- Business Ready

### Inputs
- Baseline من Phase 0
- Business Promise من Phase 1
- Governance definitions

### Deliverables

#### 2.1 Capability Truth Matrix
جدول واحد موثق لكل Provider:

| Provider | Implemented | Registered | Activated | Reachable | Returns Data | Capability Proven | Country/Product Ready | Business Ready | Evidence |
|----------|-------------|------------|-----------|-----------|--------------|-------------------|-----------------------|----------------|----------|
| UN Comtrade | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Trade flows) | Partial (HS-level only) | Partial | UN Comtrade Preview API returns real data |
| World Bank LPI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Country scores) | ✅ | Partial | World Bank Indicators API returns real data |
| FAOSTAT | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| Moaah | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| TradeData | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| ZATCA | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| GCC-Stat | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | No credentials in `.env` |
| Regulations | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | `regulations.json` missing from `backend/data/` |

#### 2.2 Capability Sufficiency Assessment
لكل Family، حدد:

| Family | Required Capability | Current Source | Capability Actually Proven | Gap Type |
|--------|---------------------|----------------|---------------------------|----------|
| Trade Intelligence | Bilateral trade flows, HS-level, Egypt↔Y | UN Comtrade | ✅ Proven | None |
| Market Opportunity | Demand, growth, export potential, market attractiveness | None | ❌ Not Proven | **Source Gap** |
| Market Access | Tariffs, duties, procedures, permits for Y | Moaah (inactive) | ❌ Not Proven | **Configuration + Source Limitation** |
| Regulatory/SPS-TBT | MRL, SPS/TBT, conformity for product+Y | Regulations (inactive) | ❌ Not Proven | **Data File Missing + Source Limitation** |
| Rules of Origin | FTA criteria, eligibility, certificate for Y | GCC-Stat (inactive) | ❌ Not Proven | **Configuration + Scope Limitation** |
| Agrifood | Agricultural prices, conditions, alerts | FAOSTAT (inactive) | ❌ Not Proven | **Configuration Gap** |
| Logistics | Route cost, transit time, reliability Egypt→Y | World Bank LPI | ❌ Not Proven | **Source Limitation** (country scores ≠ route data) |

### Acceptance Criteria
- [ ] Capability Truth Matrix مكتملة لجميع Providers
- [ ] Capability Sufficiency Assessment مكتملة لجميع Families
- [ ] لا توجد حالة غامضة (مثل "Partial" بدون دليل)
- [ ] كل Gap مصنف بشكل واضح

### Exit Gate
Capability Truth Model معتمد.

### Stop Conditions
- إذا اكتشفت أن Governance definitions تتعارض مع Evidence → توقف وحسّن Governance أولاً

---

## Phase 3 — Semantic Integrity + Production Readiness Governance

### الهدف
إصلاح الـ Semantic Mapping Gap وإنشاء Production Readiness Gate موحد.

### Inputs
- Capability Truth Model من Phase 2
- Governance docs الموجودة

### Deliverables

#### 3.1 Semantic Integrity Audit
افحص وقارن:

| Current Mapping | Governance Definition | Verdict | Action |
|-----------------|----------------------|---------|--------|
| `trade → market_opportunity` | "Historical trade data alone does not satisfy Market Opportunity" | **CONTRADICTION** | Remove `market_opportunity` from trade type in `SourceCapabilityResolver` |
| `regulation → market_access + regulatory_sps_tbt + rules_of_origin` | Local JSON file cannot cover all three with current, country-product-specific data | **OVERCLAIM** | Split capability declarations per actual source capability |
| `external_logistics_intelligence → logistics_market_execution` | Logistics requires route-level data, not country scores | **OVERCLAIM** | Restrict LPI to partial coverage or create separate capability |
| `external_trade_intelligence → market_opportunity` | Same as first row | **CONTRADICTION** | Remove from resolver |

#### 3.2 Production Readiness Gate Definition
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
8. Country/Product Ready — Coverage matches target
9. Business Ready — Can answer the commercial question
```

**WP Closure Gate:**
لا يُغلق Provider WP إلا إذا وصل إلى مستوى **Capability Proven** على الأقل للـ Country/Product المطلوب.

**No shortcuts:**
- `Implemented` ≠ `Business Ready`
- `Registered` ≠ `Activated`
- `HTTP 200` ≠ `Capability Proven`

### Acceptance Criteria
- [ ] Semantic Integrity Audit مكتمل
- [ ] كل contradiction مصنف
- [ ] Production Readiness Gate معتمد
- [ ] لا يوجد false capability declaration

### Exit Gate
Semantic Integrity مثبتة + Production Readiness Gate معتمد.

### Stop Conditions
- إذا تطلب الإصلاح تعديل Contract > خطة منفصلة → أوقف ووثّق

---

## Phase 4 — Existing Provider Activation & Repair

### الهدف
تفعيل كل Provider الممكن تفعيله، وتوثيق سبب عدم تفعيل الباقي.

### Inputs
- Capability Truth Model من Phase 2
- Semantic Integrity Audit من Phase 3

### Deliverables

#### 4.1 Provider Activation Plan
لكل Provider:

| Provider | Action Required | Type | Owner |
|----------|-----------------|------|-------|
| UN Comtrade | ✅ Already active | None | — |
| World Bank LPI | ✅ Already active | None | — |
| FAOSTAT | Configure credentials + verify JWT | Configuration | DevOps |
| Moaah | Configure credentials + verify endpoint | Configuration | DevOps |
| TradeData | Configure credentials + verify plan | Configuration + Licensing | Legal/DevOps |
| ZATCA | Configure credentials + verify endpoint | Configuration | DevOps |
| GCC-Stat | Configure credentials + verify endpoint | Configuration | DevOps |
| Regulations | Create `backend/data/regulations.json` OR remove production dependency | Data/Architecture Decision | Architecture |

#### 4.2 Regulations Decision
قبل إنشاء الملف، حدد:
1. هل Regulations Knowledge Provider جزء صحيح من Production Architecture؟
2. هل البيانات ستكون موثوقة وحديثة وcountry/product-specific؟
3. هل يوجد مصدر أفضل (مثل Moaah/WTO ePing) يمكن أن يحل محل الملف المحلي؟
4. إذا كان الملف هو الحل الوحيد، حدد:
   - حجم البيانات المطلوب
   - مصدر البيانات
   - آلية التحديث
   - Validation rules

**لا تنشئ الملف في هذه المرحلة.**

### Acceptance Criteria
- [ ] كل Provider له خطة تفعيل أو توثيق سبب عدم التفعيل
- [ ] Regulations decision مُسجَّل
- [ ] لا يوجد "مجهول" في حالة Provider

### Exit Gate
كل Provider له حالة نهائية موثقة.

### Stop Conditions
- إذا تطلب Regulations إنشاء ملف بيانات ضخم → أوقف وحدد النطاق أولاً

---

## Phase 5 — Current Source Reality Revalidation

### الهدف
التحقق الخارجي المحدود للمصادر التي قد تؤثر على قرارات الخطة.

### Inputs
- Capability Truth Model
- Provider Activation Plan

### Deliverables

#### 5.1 Source Reality Check
لكل مصدر محتمل:

| Source | Current Status | API Available | Filtering | Country Coverage | Product/HS Coverage | Freshness | Licensing | Verdict |
|--------|---------------|---------------|-----------|------------------|---------------------|-----------|-----------|---------|
| UN Comtrade | ✅ Active | Preview API | Limited | Global | HS-level | 2025 max | Free | Keep |
| World Bank LPI | ✅ Active | Indicators API | Limited | Global | Indicator-level | 2012-2023 | Free | Keep (with limitation noted) |
| FAOSTAT | Inactive | REST API | Yes | Global | Item/Element | Recent | CC BY-NC-SA 3.0 IGO | Activate if licensing cleared |
| Moaah | Inactive | REST API | Yes | Egypt-focused | HS | Recent | Commercial | Activate if needed |
| TradeData | Inactive | REST API | Yes | 200+ countries | HS/buyer/supplier | Recent | Commercial | Activate if needed |
| ZATCA | Inactive | REST API | Limited | Saudi Arabia | HS | Recent | Open Data | Activate for KSA only |
| GCC-Stat | Inactive | SDMX/REST | Yes | GCC | Product | Recent | Open | Activate for GCC only |
| WTO ePing | Complementary | Web + XLSX | No | Global | Product | Recent | WTO | Complementary only |
| ITC Market Access Map | Complementary | Web + bulk | No | Global | HS | Recent | ITC | Complementary only |
| ITC Export Potential Map | Complementary | Web only | No | Global | Product | Recent | ITC | Complementary only |

#### 5.2 Stale Governance Assumptions
سجّل أي افتراض governance قديم:

| Document | Assumption | Current Reality | Status |
|----------|-----------|-----------------|--------|
| `external-knowledge-portfolio-re-evaluation.md` | WTO ePing may become accessible | No verifiable public REST API with filtering | **STALE** — Update trigger condition |
| `external-knowledge-portfolio-re-evaluation.md` | World Bank LPI covers Logistics | LPI gives country scores only, not route data | **STALE** — Coverage claim needs revision |
| `SourceCapabilityResolver` | `trade → market_opportunity` | Governance explicitly forbids this mapping | **STALE** — Remove mapping |

### Acceptance Criteria
- [ ] Source Reality Check مكتمل للمصادر ذات الصلة
- [ ] Stale Governance Assumptions موثقة
- [ ] لا تم تعديل الوثائق في هذه المرحلة

### Exit Gate
واضح أي مصدر قديم وأي مصدر ما زال صالحًا.

### Stop Conditions
- إذا اكتشفت أن مصدرًا مُصدَّق له API مختلف → أوقف وحسّن Candidate Evaluation أولاً

---

## Phase 6 — Knowledge Gap Closure

### الهدف
تقييم العائلات السبعة وتحديد قرار Gap Closure لكل منها.

### Inputs
- Capability Truth Model
- Capability Sufficiency Assessment
- Source Reality Check
- Business Promise

### Deliverables

#### 6.1 Gap Closure Matrix
لكل Family:

| Family | Gap | Decision | Rationale |
|--------|-----|----------|-----------|
| **Trade Intelligence** | Partial (Comtrade limits) | **Accept Partial** | Comtrade gives verified trade flows. Limit: 500 records, no advanced filtering. Sufficient for basic question. | 
| **Market Opportunity** | **Full Gap** | **New Source Required** | No source provides demand/growth/export-potential. TradeData/Comtrade give historical flows only. Cannot be filled by Configuration. | 
| **Market Access** | **Full Gap** | **Source Required** | Moaah inactive + ZATCA KSA-only. Need global tariff database or accept Complementary (ITC Market Access Map). | 
| **Regulatory/SPS-TBT** | **Full Gap** | **Source Required or Complementary Accepted** | No automated provider. Local file missing. WTO ePing is Complementary only. Must decide: new source OR permanent Complementary. | 
| **Rules of Origin** | **Full Gap** | **Source Required** | GCC-Stat inactive + GCC scope only. Need FTA database or accept Complementary (ITC Rules of Origin Facilitator). | 
| **Agrifood** | **Full Gap** | **Configuration + Source Verification** | FAOSTAT implemented but inactive. Need credentials + verify JWT flow. If activated, covers Agrifood. | 
| **Logistics** | **Partial** | **Source Enhancement Required** | LPI gives country scores. Need route-level data (UNCTAD LSCI/PLSCI or shipping APIs). Cannot be filled by Configuration. | 

#### 6.2 Gap Closure Decisions
لكل Gap، حدد بالضبط:

| Gap Type | Action |
|----------|--------|
| Configuration | Activate existing provider with correct credentials |
| Implementation Fix | Fix code bug in existing provider |
| Existing Source Enhancement | Add data/file to existing provider |
| New Source Required | Must go through Phase 7 |
| Complementary Accepted | Document permanently in Business Promise |
| Not Required for Minimum Promise | Document why and move to Optional/Future |

### Acceptance Criteria
- [ ] كل Family لها قرار Gap Closure واحد واضح
- [ ] لا توجد حالة "غير محدد"
- [ ] Complementary coverage مُعرَّفة بوضوح في Business Promise

### Exit Gate
كل Gap له قرار واضح.

### Stop Conditions
- إذا تطلب Market Opportunity أو Logistics مصدرًا جديدًا → توقف عند Phase 7

---

## Phase 7 — Source Candidate Evaluation

### الهدف
تقييم المرشحين للمصادر الناقصة فقط.

### Inputs
- Gap Closure Matrix من Phase 6
- Source Reality Check من Phase 5
- Provider Ceiling = 7

### Deliverables

#### 7.1 Candidate Evaluation
لكل Gap الذي يتطلب مصدرًا جديدًا:

| Gap | Candidate | Knowledge Value | Unique Value | API | Filtering | Countries | Products | Freshness | Licensing | Feasibility | Provider Ceiling Impact | Decision |
|------|-----------|-----------------|--------------|-----|-----------|-----------|----------|-----------|-----------|-------------|------------------------|----------|
| Market Opportunity | ITC Export Potential Map | Very High | High | Web only | No | Global | Product | Recent | ITC terms | Low (no API) | N/A | **Complementary Only** |
| Market Opportunity | TradeData | Medium | Medium | REST | Yes | 200+ | HS/buyer | Recent | Commercial | Medium (requires API key) | +1 if activated | **Candidate** |
| Market Opportunity | UN Comtrade (re-analysis) | Low | Low | REST | Limited | Global | HS | 2025 max | Free | High | Already have | **Insufficient** |
| Market Access | ITC Market Access Map | High | High | Web + bulk | Partial | Global | HS | Recent | ITC terms | Low | N/A | **Complementary Only** |
| Market Access | WTO Timeseries API | High | High | REST (key required) | Yes | Global | HS | Recent | WTO | Medium | +1 | **Candidate** |
| Regulatory/SPS-TBT | WTO ePing | Critical | High | Web + XLSX | No | Global | Product | Recent | WTO | Low (no API) | N/A | **Complementary Only** |
| Rules of Origin | ITC Rules of Origin Facilitator | Medium | Medium | Web only | No | Global | Product | Recent | ITC terms | Low | N/A | **Complementary Only** |
| Logistics | UNCTAD LSCI/PLSCI | Medium-High | Medium | CSV only | No | Global | Route | Recent | UNCTAD | Low | N/A | **Complementary Only** |
| Logistics | Shipping APIs (various) | High | High | REST | Yes | Route-specific | Route | Real-time | Commercial | Medium | +1 | **Candidate** |

#### 7.2 Provider Ceiling Analysis
- Current: 7 implemented providers
- Ceiling: 7 (operational)
- Available slots: 0
- To add new provider: must deactivate/merge existing OR request ceiling expansion

### Acceptance Criteria
- [ ] كل Gap المُتطلب لمصدر جديد له تقييم مرشح واحد على الأقل
- [ ] لا يوجد مرشح بدون تقييم Feasibility
- [ ] Provider Ceiling impact موثق
- [ ] لا يوجد قرار "إضافة Provider" بدون governance approval

### Exit Gate
لا يوجد Candidate غير مُقيَّم.

### Stop Conditions
- لا تنفذ Implementation من هذه المرحلة

---

## Phase 8 — Research / BI Alignment

### الهدف
التأكد من أن طبقات البحث والذكاء التجاري لا تعلن قدرات لا يثبتها المصدر.

### Inputs
- Capability Truth Model
- Semantic Integrity Audit
- Provider Activation Plan

### Deliverables

#### 8.1 Research Query Planner Alignment
افحص:
- هل `ResearchQueryPlanner` يولد queries للعائلات التي ليس لها مصادر نشطة؟
- هل Discovery يكتشف المصادر الصحيحة للـ queries المُولَّدة؟
- هل intent_profile يعكس الواقع وليس الافتراضات؟

#### 8.2 BI Alignment
افحص:
- هل `BusinessIntelligenceSynthesizer` ينتج limitations صحيحة عندما لا يوجد source؟
- هل `unsupported_dimensions` يُبلغ عنها بوضوح؟
- هل `CoverageBuilder` يحسب التغطية بناءً على المصادر الفعلية وليس المُسجَّلة؟

#### 8.3 Findings
| Component | Issue | Fix Required | Priority |
|-----------|-------|--------------|----------|
| `SourceCapabilityResolver` | `trade → market_opportunity` mapping | Remove mapping | P0 |
| `ResearchQueryPlanner` | Auto-generates 7 dimensions for any export | Adjust to actual available sources | P1 |
| `CoverageBuilder` | Counts entries not unique sources | ✅ Fixed in 0a643af | ✅ Done |
| `BusinessIntelligenceSynthesizer` | Meta-findings in output | ✅ Fixed in 0a643af | ✅ Done |

### Acceptance Criteria
- [ ] لا يوجد false capability declaration في الكود
- [ ] Research/BI ينتج limitations صحيحة للمصادر غير المتاحة
- [ ] Provenance كامل للبيانات

### Exit Gate
Research/BI aligned مع Capability Truth Model.

---

## Phase 9 — Country / Product / Route Readiness

### الهدف
إثبات أن DEM يستطيع بناء صورة تجارية موثقة لـ market/product combination.

### Inputs
- Capability Truth Model
- Provider Activation Plan
- Gap Closure Decisions

### Deliverables

#### 9.1 Readiness Scenarios
استخدم هذه الأمثلة لإثبات المبدأ:

| Scenario | Market | Product | Trade Intelligence | Market Opportunity | Market Access | Regulatory | Rules of Origin | Agrifood | Logistics | Overall |
|----------|--------|---------|-------------------|-------------------|---------------|------------|-----------------|----------|-----------|---------|
| 1 | Jordan (Levant) | Vegetables (HS 07) | ✅ UN Comtrade | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None | **Not Ready** |
| 2 | Saudi Arabia (GCC) | Dates (HS 08) | ✅ UN Comtrade | ❌ None | ⚠️ ZATCA (inactive) | ❌ None | ⚠️ GCC-Stat (inactive) | ❌ None | ❌ None | **Not Ready** |
| 3 | Germany (EU) | Citrus (HS 08) | ✅ UN Comtrade | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None | **Not Ready** |
| 4 | Kenya (East Africa) | Coffee (HS 09) | ✅ UN Comtrade | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None | **Not Ready** |
| 5 | China (East Asia) | Textiles (HS 61) | ✅ UN Comtrade | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None | **Not Ready** |

**الخلاصة:** DEM اليوم **غير جاهز** لأي سوق خارج نطاق Trade Intelligence الأساسي.

### Acceptance Criteria
- [ ] كل Scenario له تقييم واضح
- [ ] لا يوجد سوق يعتبر "Ready" بدون دليل
- [ ] Limitations موثقة لكل سوق

### Exit Gate
واضح ما هو Ready وما هو Not Ready ولماذا.

---

## Phase 10 — End-to-End Commercial Acceptance

### الهدف
اختبار المسار الكامل من Employee Request إلى Business Response.

### Inputs
- Capability Truth Model
- Provider Activation Plan
- Gap Closure Decisions
- Readiness Scenarios

### Deliverables

#### 10.1 Acceptance Test Design
صمم اختبارات تثبت:

1. **Capability Truth:** يعلن النظام فقط ما يستطيع إثباته
2. **Evidence Backing:** كل claim له دليل
3. **Provenance:** كل dato له مصدر قابل للتتبع
4. **Limitations:** تُظهر بوضوح ما هو غير متاح
5. **No Overclaim:** لا توجد capability خارجة عن Capability Truth Model

#### 10.2 Test Scenarios
لكل سيناريو، تحقق:

| Scenario | Expected Behavior | Actual Behavior (Current) | Gap |
|----------|-------------------|---------------------------|-----|
| Egypt → Jordan vegetables | Shows trade flows + limitations for other families | Shows trade flows + fake opportunities/risks from stub data | **Overclaim** |
| Egypt → Saudi Arabia dates | Shows trade flows + ZATCA if activated | Shows trade flows + no market access | **Gap** |
| Egypt → EU citrus | Shows trade flows + regulatory limitations | Shows trade flows + no regulatory data | **Gap** |

### Acceptance Criteria
- [ ] لا يوجد Overclaim في أي سيناريو
- [ ] Limitations ظاهرة بوضوح
- [ ] Provenance كامل
- [ ] لا توجد meta-findings في output

### Exit Gate
End-to-End Commercial Acceptance مُحقَّق.

---

## Phase 11 — Governance / Documentation Reconciliation

### الهدف
تحديث الوثائق لتطابق الحقيقة التشغيلية الجديدة.

### Inputs
- جميع المراحل السابقة

### Deliverables

#### 11.1 Documents to Update
| Document | Required Update |
|----------|-----------------|
| `PLAN.md` | Business Promise, Capability Model, Source Status |
| `CURRENT_STATUS.md` | Project status, source availability, gaps |
| `external-knowledge-portfolio-re-evaluation.md` | Stale assumptions, capability mappings |
| `SourceCapabilityResolver` | Remove false mappings |
| `ResearchQueryPlanner` | Align with actual capabilities |
| Provider metadata | Reflect actual activation status |
| Acceptance tests | Remove stub-based "validation" |

#### 11.2 Documents NOT to Modify
- Closed WP contracts (لا تعيد فتحها)
- Architecture contracts الثابتة
- Provider admission criteria (لا تعديل إلا إذا ظهر conflict مثبت)

### Acceptance Criteria
- [ ] لا توجد وثيقة تتعارض مع الحقيقة التشغيلية
- [ ] لا توجد capability claim بدون مصدر
- [ ] لا يوجد status "Complete" بدون دليل

### Exit Gate
Governance Reconciliation مكتمل.

---

## Phase 12 — Final Closure

### الهدف
إثبات أن DEM وصل إلى حالة Commercial Readiness حقيقية.

### Inputs
- جميع المراحل السابقة

### Exit Criteria

| Criterion | Evidence |
|-----------|----------|
| Architecture | ✅ سليم، لا تعديل مطلوب |
| Business Promise | ✅ معتمد وواقعي |
| Capability Model | ✅ موثق وموثق |
| Semantic Integrity | ✅ لا false mappings |
| Production Readiness | ✅ Gate معتمد |
| Source Activation | ✅ كل source له حالة واضحة |
| Knowledge Coverage | ✅ Gap Closure Decisions مُسجَّلة |
| Evidence / Provenance | ✅ كامل وموثق |
| Research / BI Alignment | ✅ aligned مع Capability Truth |
| Country/Product/Route Readiness | ✅ scenarios موثقة |
| Governance Consistency | ✅ لا تناقضات |
| Security | ✅ credentials risks موثقة |
| No Known False Capability Claims | ✅ verified |

### Final State
عند تحقيق جميع Exit Criteria:

```text
DEM COMMERCIAL READINESS REMEDIATION = COMPLETE
```

### إذا لم يتم تحقيق جميع Exit Criteria
توثيق:
- أي Criteria لم تحقق
- السبب
- الإجراء المطلوب لتحقيقه
- عدم الإعلان عن DEM كمنتج تجاري كامل

---

## Closed Work Packages — قاعدة الحماية

لا تعاد فتح Work Package مغلقة إلا إذا ظهر **واحد فقط** من:

1. **Contract Conflict** — تعديل الكود يتطلب تعديل Contract مثبت
2. **Defect حقيقي** — خطأ برمجي يمنع الوظيفة الأساسية
3. **Security issue** — ثغرة أمنية مثبتة
4. **Production-critical defect** — عطل في الإنتاج موثق
5. **Governance contradiction مثبت** — وثيقة تتعارض مع الحقيقة التشغيلية

**إذا كان الإصلاح ممكناً كـ Targeted Remediation بدون reopening WP → هذا هو المسار المفضل.**

---

## Prevention of Recursion

لا يُسمح بـ:

| الفعل | الشرط |
|--------|-------|
| Forensic Audit كاملة بين المراحل | ممنوع — استخدم Baseline |
| إعادة فحص ما تم إثباته | ممنوع — استخدم Deliverables |
| Source Research متكرر | ممنوع بعد اعتماد Requirement |
| Provider جديد قبل Capability Gap | ممنوع — اتبع التسلسل |
| تعديل طبقة أعلى لمعالجة نقص طبقة أدنى | ممنوع — عالج الجذر |
| اعتبار test fixture دليل Production | ممنوع — استخدم Capability Truth |
| اعتبار HTTP 200 دليل Capability | ممنوع — استخدم Capability Proven |
| اعتبار registered provider دليل readiness | ممنوع — استخدم Business Ready |
| اعتبار historical trade دليل opportunity | ممنوع — استخدم Market Opportunity source |
| اعتبار country LPI دليل route freight cost | ممنوع — استخدم Logistics route data |
| اعتبار Complementary = Production | ممنوع — استخدم Business Promise definitions |
| اعتبار Planned = Available | ممنوع — استخدم Runtime Activation |
| تغيير Architecture | ممنوع إلا عند إثبات conflict |
| فتح Multi-Agent | ممنوع |
| فتح Knowledge Graph | ممنوع |
| إعادة تصميم Avatar | ممنوع |
| إعادة تصميم BI | ممنوع |
| إعادة فتح Closed WP بلا evidence | ممنوع |

---

## Phase Exit Discipline

كل Phase تحتوي على:

| البند | الوصف |
|--------|-------|
| **Objective** | ما الذي تحققه هذه المرحلة |
| **Inputs** | ماذا تحتاج لتبدأ |
| **Scope** | ما هو داخل النطاق |
| **Dependencies** | ما الذي يجب أن يكتمل أولاً |
| **Exact Deliverables** | ماذا تنتج |
| **Acceptance Criteria** | كيف تعرف أنك انتهيت |
| **Exit Gate** | الشرط الوحيد للانتقال |
| **Stop Conditions** | متى تتوقف |
| **What Must Not Change** | ما الذي لا يُسمح بتعديله |

**لا تبدأ Phase التالية إلا بعد Exit Gate.**

---

## Execution Order

```text
Phase 0: Baseline Freeze + Security
    ↓ Gate
Phase 1: Define Honest Commercial Promise
    ↓ Gate
Phase 2: Capability Truth Model
    ↓ Gate
Phase 3: Semantic Integrity + Production Readiness Governance
    ↓ Gate
Phase 4: Existing Provider Activation & Repair
    ↓ Gate
Phase 5: Current Source Reality Revalidation
    ↓ Gate
Phase 6: Knowledge Gap Closure
    ↓ Gate
Phase 7: Source Candidate Evaluation
    ↓ Gate
Phase 8: Research / BI Alignment
    ↓ Gate
Phase 9: Country / Product / Route Readiness
    ↓ Gate
Phase 10: End-to-End Commercial Acceptance
    ↓ Gate
Phase 11: Governance / Documentation Reconciliation
    ↓ Gate
Phase 12: Final Closure
```

---

## Critical Path Notes

1. **Phase 0 يُهمل غالبًا** — لا تتخطاه. Baseline الموحد هو ما يمنع العودة للتحقيق من البداية.
2. **Phase 1 يُهمل غالبًا** — لا تحاول إصلاح المصادر قبل أن تعرف ما الذي تعد المستخدم به.
3. **Phase 3 هو الذي يمنع العودة للfalse claims** — لا تتخطى Semantic Integrity.
4. **Phase 6 هو نقطة القرار** — هنا تحدد ما الذي يمكن إصلاحه وما الذي يحتاج مصدرًا جديدًا.
5. **Phase 10 هو الذي يثبت الجاهزية** — لا تعتبر Pipeline Passed = Business Ready.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Stakeholder يرفض Business Promise الواقعي | Medium | High | عرض الأدلة من Forensic Audit |
| Provider Activation يفشل بسبب credentials | Medium | Medium | وثّق Alternatives وComplementary coverage |
| Gap Closure يتطلب مصادر جديدة | High | High | اتبع Phase 7 بصرامة |
| Semantic Mapping fixes تؤثر على existing code | Low | Medium | راجع Phase 8 كجزء من Exit Gate |
| Governance docs تتعارض مع الحقيقة | Medium | Medium | وثّق في Phase 5، لا تعدل في هذه المرحلة |

---

## Out of Scope

هذه الخطة **لا تشمل**:

- Code implementation
- Provider implementation
- Credential configuration
- Data file creation
- BI redesign
- Avatar modification
- Multi-Agent reopening
- Knowledge Graph reopening
- Architecture redesign
- Market ranking studies
- Provider count expansion beyond ceiling

---

```text
MASTER REMEDIATION PLAN = READY

No implementation started.
No new provider authorized.
No closed architecture reopened.
Execution starts only after explicit transition to Code.
```
