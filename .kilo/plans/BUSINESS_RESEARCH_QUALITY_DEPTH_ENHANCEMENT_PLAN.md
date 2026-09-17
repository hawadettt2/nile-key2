# Business Research Quality & Depth Enhancement

## الهدف
تحسين جودة وعمق Business Research بحيث تتحول الأدلة المسترجعة إلى معلومات تجارية فعلية ومفهومة وقابلة للاستفادة، مع الحفاظ على سلامة الدليل وعدم اختراع استنتاجات غير مدعومة.

---

## 1. Commercial Result Structuring

### الهدف
تحويل الأدلة إلى Findings تجارية فعلية بدل `meta-findings` العامة.

### النهج
- تحديث `DefaultResultStructurer` لاستخراج معلومات تجارية من `Evidence.content` بدلاً من عد الأدلة فقط.
- استخدام extraction deterministic فقط: أرقام، وحدات، بلدان، HS codes، فترات، اتجاهات ظاهرة في النص.
- الحفاظ على `evidence` و `provenance` كما هي دون تعديل.

### ممنوع
- لا LLM.
- لا summarization.
- لا translation.
- لا اختراع بيانات غير موجودة في الدليل.

### معايير القبول
- [ ] `FindingItem.content` لا يبدأ بـ `Retrieved N evidence item(s)`.
- [ ] `FindingItem.topic` يعبر عن موضوع تجاري قابل للتتبع.
- [ ] كل `FindingItem` مرتبط بـ `EvidenceItem` بنفس `source_id` و `query_id`.
- [ ] لا تُفقد أي `EvidenceReference` موجودة أثناء التحويل.

---

## 2. Business Fact Extraction & Normalization

### الهدف
تحويل Findings إلى Business Facts ذات معنى وقابلة للتتبع.

### النهج
- تحديث `BusinessFactNormalizer.normalize_findings()` لاستخراج `BusinessFact` من النص التجاري للـfinding.
- كل `BusinessFact` يحتوي على:
  - `dimension`
  - `statement`
  - `evidence`
  - `confidence`
  - `source_ids`
- لا تُخلق facts إلا إذا كان هناك نص تجاري واضح في الدليل.

### معايير القبول
- [ ] كل `BusinessFact.statement` نص تجاري ملموس وليس وصفًا للعدد.
- [ ] `BusinessFact.source_ids` مطابق للمصدر الفعلي.
- [ ] `BusinessFact.confidence` يُحفظ من الدليل أو يُعين `None` فقط عند عدم وجود دليل.
- [ ] لا توجد `BusinessFact` بدون `evidence` أو `source_ids`.

---

## 3. Explicit Derivation Signals

### الهدف
تحديد كيف تنتقل الإشارات المدعومة من Findings/Facts إلى Opportunity / Risk / Entity.

### النهج
- تحديث `OpportunityDeriver` و `RiskDeriver` و `EntityDeriver` ليعتمدوا على إشارات واضحة من `BusinessFact` بدلاً من `provenance` keys غير المملوءة.
- الإشارات المقبولة:
  - `Opportunity`: facts ذات دلالة نمو/طلب/سوق إيجابية.
  - `Risk`: facts ذات دلالة تحذير/قيود/مخاطر سلبية.
  - `Entity`: كيانات تجارية ظاهرة في النص (دول، منتجات، HS codes).
- لا يُنشأ Opportunity أو Risk إلا إذا كان هناك fact يدعمه.

### معايير القبول
- [ ] `OpportunityDeriver` ينتج `Opportunity` فقط عندما توجد facts مناسبة.
- [ ] `RiskDeriver` ينتج `Risk` فقط عندما توجد facts مناسبة.
- [ ] `EntityDeriver` ينتج `Entity` من facts تحتوي على كيانات تجارية.
- [ ] لا تعتمد أي مرحلة على `provenance.get("opportunity_basis")` أو `provenance.get("risk_signal")` بعد التعديل.

---

## 4. Research Coverage & Source Capability

### الهدف
مراجعة تغطية export/import الحالية وتحسين اكتشاف المصادر.

### النهج
- مراجعة `ResearchQueryPlanner` لضمان أن `market_access` و `regulatory_sps_tbt` و `rules_of_origin` تُولّد تلقائيًا عندما يكون هناك export/import intent، دون الاعتماد على keyword matching فقط.
- مراجعة `SourceDiscovery` و `SourceCapabilityResolver` لضمان أن المصادر المسجلة تُكتشف بشكل صحيح.
- تحديث `_knowledge_source_to_research_source()` لتعيين `source_type` صحيح للمصادر external/agrifood.
- لا إضافة مصادر جديدة إلا إذا ثبت أن المصدر المطلوب غير مسجل أو غير قادر.

### معايير القبول
- [ ] `ResearchQueryPlanner` يولد queries لـ `market_access` و `regulatory_sps_tbt` و `rules_of_origin` تلقائيًا لاستعلامات export/import.
- [ ] `SourceDiscovery` يكتشف المصادر المناسبة لهذه الأبعاد.
- [ ] `un-comtrade` يُكتشف لـ `trade_intelligence` و `market_opportunity`.
- [ ] لا تُزال capabilities أو أبعاد موجودة فعلاً.

---

## 5. End-to-End Acceptance

### الهدف
التحقق من أن الناتج أصبح Business-Ready للسيناريو المرجعي.

### السيناريو المرجعي
`اريد تصدير الخضروات والفاكهة المصرية الى الاردن`

### معايير القبول
- [ ] `keyFindings`: على الأقل 2 findings تجارية فعلية.
- [ ] `entities`: على الأقل 1 entity (دولة/منتج/HS code).
- [ ] `opportunities`: على الأقل 1 opportunity مدعوم بدليل.
- [ ] `risks`: على الأقل 1 risk مدعوم بدليل.
- [ ] `evidence`: على الأقل 3 evidence items.
- [ ] `confidence`: رقم تجاري أو `None` فقط عند عدم وجود دليل كافٍ.
- [ ] لا توجد limitations من نوع:
  - `No structured research findings are available`
  - `No source evidence is available`
  - `Coverage status: insufficient` عند وجود مصادر ناجحة.
- [ ] لا توجد meta-findings عامة في `keyFindings`.
- [ ] كل `Opportunity` و `Risk` مرتبط بـ `EvidenceReference` واضح.

---

## Out of Scope

- LLM / Summarization / Translation.
- Multi-Agent / Knowledge Graph.
- Frontend / Avatar redesign.
- Backend API redesign.
- BI Schema redesign.
- إعادة فتح BI Work Packages المغلقة.
- اختراع Opportunity أو Risk من أرقام أو إشارات ضعيفة غير مدعومة.
- تغيير Evidence Capture لتحليل تجاري؛ دورها يقتصر على حفظ الدليل القابل للتتبع فقط.

---

## Implementation Order

1. Commercial Result Structuring
2. Business Fact Extraction & Normalization
3. Explicit Derivation Signals
4. Research Coverage & Source Capability
5. End-to-End Acceptance
