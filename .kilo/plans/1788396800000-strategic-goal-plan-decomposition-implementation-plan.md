# Implementation Plan: Strategic Goal/Plan Decomposition

**تاريخ الإنشاء:** 2026-09-03
**الحالة:** Plan Ready — ينتقل إلى Code لاحقاً
**المسؤول:** Architecture Planning
**النطاق:** Strategic Goal/Plan Decomposition فقط

---

## 1. الهدف والنطاق المعماري

### الهدف
تحويل **Strategic Goal** واحد إلى **Plan** منظم يحتوي على **Missions مترابطة، مرتبة، وقابلة للتنفيذ**، مع الحفاظ على تتبع التقدم والتبعيات والقيود، ودعم إعادة التخطيط ضمن حدود واضحة.

### النطاق المعماري
هذه الـcapability مسؤولة فقط عن **التحويل الهيكلي** من `Goal` إلى `Plan` + `Missions`:
- **لا** تقرر HOW تنفيذ الهدف (هذا لـ Deep Strategic Reasoning)
- **لا** تمنع أو تسمح بالتنفيذ (هذا لـ Runtime Autonomy Enforcement)
- **لا** تنفذ Tools أو Missions (هذا لـ Tool Orchestrator و Execution Engine)

---

## 2. الـCurrent State والفجوة الفعلية

### ما الموجود حالياً (Foundation مكتمل):
- `Goal` schema كامل مع `parent_goal_id`, `constraints`, `autonomy_level`, `status`
- `Plan` schema كامل مع `missions`, `dependencies`, `constraints`, `approval_policy`, `fallback_strategy`
- `GoalManager` مع `create_goal()`, `create_plan_for_goal()`, `complete_goal()`, `abandon_goal()`
- `PlanManager` مع `create_plan()`, `activate_plan()`, `append_mission()`, `complete_plan()`, `abandon_plan()`
- `PlanPlanner.create_plan()` — ينشئ Plan مع `missions=[]`, `dependencies=[]`, ينسخ `goal.constraints` إلى `plan.constraints`
- `GoalRepository` و `PlanRepository` مع CRUD كامل
- `Mission` schema و `MissionPlanner` و `TaskPlanner` موجودون لكنهم يتلقون input من خارج Decomposition

### ما المفقود (الفجوة الفعلية):
1. **Goal analysis logic** — لا يوجد تحليل لـ Goal objective/scope/constraints لتحديد كيف سيتم تفكيكه
2. **Sub-goal decomposition** — `parent_goal_id` موجود في schema لكن لا يوجد منطق يستخدمه لإنشاء sub-goals
3. **Mission creation/sequencing** — `PlanPlanner.create_plan()` ينتج Plan مع `missions=[]` فارغ، لا يوجد منطق لإنشاء Missions
4. **Dependency mapping** — `Plan.dependencies=[]` فارغ دائماً، لا يوجد منطق لتعيين `depends_on` بين Missions
5. **Constraints propagation** — `Plan.constraints` ينسخ من `Goal.constraints` لكن لا يصل إلى `Mission.context`
6. **Fallback structure** — `Plan.fallback_strategy={}` فارغ دائماً
7. **Re-planning boundaries** — لا يوجد منطق لتحديد متى يحتاج Plan إلى إعادة تخطيط

---

## 3. الملفات / Components المتأثرة

### الملفات التي ستُعدَّل:
| File | Component | التغيير |
|------|-----------|---------|
| `backend/app/agent/plan/planner.py` | `PlanPlanner` | إضافة decomposition logic: goal analysis → sub-goals → mission ID generation → sequencing → dependency graph → constraints propagation |
| `backend/app/agent/plan/manager.py` | `PlanManager` | إضافة re-planning boundary logic و fallback structure management |
| `backend/app/agent/goal/manager.py` | `GoalManager` | تحديث `create_plan_for_goal()` لاستدعاء decomposition logic الجديد |
| `backend/app/agent/plan/schema.py` | `Plan` schema | مراجعة الحقول فقط، لا تعديل إلا إذا ثبت الحاجة |

### الملفات التي **لن** تتغير:
- `backend/app/agent/decision_engine/engine.py` — `ReasoningEngine` بدون تغيير
- `backend/app/agent/approval/gate.py` — `ApprovalGate` بدون تغيير
- `backend/app/agent/schemas/decision.py` — بدون تغيير
- `backend/app/agent/schemas/mission.py` — بدون تغيير
- `backend/app/agent/mission_planner/planner.py` — بدون تغيير
- `backend/app/agent/execution_engine/orchestrator.py` — بدون تغيير

---

## 4. المسؤوليات المطلوبة (يجب تنفيذها)

### 4.1 Goal Analysis
- قراءة `Goal` fields: `objective`, `scope`, `constraints`, `stakeholders`, `autonomy_level`, `status`, `parent_goal_id`
- تحليل الهدف لتحديد:
  - هل يحتاج إلى sub-goals؟
  - ما هي المكونات الأساسية للهدف؟
  - ما هي القيود التي تؤثر على التنفيذ؟
  - ما هو مستوى الاستقلالية المطلوب؟
- **ملاحظة:** التحليل هنا هو **structural deterministic decomposition** فقط، وليس Deep Strategic Reasoning. إذا كان الهدف يحتاج إلى تحليل استراتيجي عميق غير ممكن بالـruntime الحالي، يُسجّل كـ boundary/deferred constraint.

### 4.2 Sub-goal Decomposition
- تقسيم `Goal` إلى `sub-goals` عبر `parent_goal_id` عند الحاجة
- كل sub-goal يُنشأ كـ `Goal` object منفصل مع `parent_goal_id` يشير إلى Goal الأصلي
- لا يغير `Goal` الأصلي، يضيف sub-goals جديدة
- sub-goals تُحفظ عبر `GoalRepository`

### 4.3 Plan Generation
- إنشاء `Plan` من `Goal` (أو من sub-goals)
- `Plan.objective` = `Goal.objective`
- `Plan.constraints` = `Goal.constraints` propagated
- `Plan.approval_policy` = derived من `Goal.autonomy_level` كـ structure فقط
- `Plan.status` = يتبع سلوك `GoalManager.create_plan_for_goal()` الحالي: ينشئ Plan ثم يُفعّل مباشرة عبر `PlanManager.activate_plan()`
- لا تغيير في lifecycle semantics

### 4.4 Mission Creation / Sequencing
- إنشاء `Missions` كـ objects كاملة عبر `MissionPlanner` أو ما يعادلها
- توليد `mission_id` لكل Mission
- ترتيب `Missions` حسب:
  - dependencies المنطقية
  - constraints
  - first-principles ordering
- كل Mission لها:
  - `mission_type` مناسب
  - `context` يحتوي على `goal_id`, `plan_id`, `constraints`
  - `execution_policy` مناسب
- **ملاحظة:** `Plan.missions` هو `List[str]` من `mission_id`، ليس `Mission objects`. لذا يجب حفظ Missions أولاً ثم ربط `mission_id` بالـPlan.

### 4.5 Dependency Mapping
- تعريف `depends_on` بين Missions
- **ملاحظة:** `Mission` schema الحالية لا تحتوي `depends_on`. لذا فإن dependency ordering يُحفظ عبر `Plan.dependencies` كـ list من tuples أو structure محددة، ولا يُضاف إلى `Mission` schema
- تحديد Missions التي يمكن تنفيذها بالتوازي
- تحديد Missions التي تحتاج إلى إكمال missions أخرى أولاً

### 4.6 Constraints Propagation
- نقل `Goal.constraints` إلى كل `Mission.context`
- نقل `Plan.approval_policy` إلى `Mission.approval_policy`
- ضمان أن constraints تصل إلى Mission قبل التنفيذ

### 4.7 Fallback Structure
- تعريف Missions بديلة في حالة فشل Mission أساسية
- `Plan.fallback_strategy` يحدد:
  - ما هي Missions البديلة
  - متى يتم تفعيلها
  - كيف يتم الانتقال إليها

### 4.8 Re-planning Boundaries
- تحديد متى يحتاج `Plan` إلى إعادة تخطيط:
  - change of scope
  - failure of critical mission
  - new information / knowledge
  - user intervention
- إرجاع trigger signals بدون تنفيذ re-planning فعلي

---

## 5. الـRuntime Flow المستهدف

```
Goal (existing, persisted)
    ↓
Goal Analysis (new, deterministic structural analysis)
    ↓
Sub-goal Decomposition (new, via parent_goal_id, persisted via GoalRepository)
    ↓
Plan Generation (new, via PlanPlanner)
    ↓
Mission Creation (new, full Mission objects via MissionPlanner)
    ↓
Mission Sequencing + Dependency Mapping (new, ordering stored in Plan.dependencies)
    ↓
Constraints Propagation (new, into Mission.context)
    ↓
Plan persisted with:
  - missions = List[str] of mission_ids
  - dependencies = dependency structure
  - constraints = propagated from Goal
  - approval_policy = structure derived from Goal.autonomy_level
  - fallback_strategy = defined
  - status = "active" (following current lifecycle)
    ↓
Ready for existing downstream consumers (existing)
```

### Inputs:
- `Goal` object (existing, persisted)
- Optional: `parent_goal_id` hierarchy (existing field)
- Optional: Knowledge/Memory hints (non-blocking, optional)

### Outputs:
- `Plan` object persisted with:
  - `missions` = `List[str]` of `mission_id` values
  - `dependencies` = dependency structure (list of tuples or compatible format)
  - `constraints` = propagated from `Goal.constraints`
  - `approval_policy` = structure derived from `Goal.autonomy_level`
  - `fallback_strategy` = defined fallback Missions (by mission_id or reference)
  - `status` = `"active"` (following current `GoalManager.create_plan_for_goal()` lifecycle)
- Optional: `sub-goals` list (new `Goal` objects with `parent_goal_id`)

### مهم:
- `Plan.missions` هو `List[str]` من `mission_id`، وليس `Mission objects`. لذا فإن الـflow يتطلب حفظ Missions أولاً، ثم ربط `mission_id` بالـPlan عبر `PlanManager.append_mission()` أو ما يعادلها.
- `Plan.dependencies` هو الـsingle source of truth للتبعيات، لأن `Mission` schema الحالية لا تحتوي `depends_on`.
- `GoalManager.create_plan_for_goal()` الحالي ينشئ Plan ثم يُفعّله مباشرة. Decomposition يتبع هذا السلوك ولا يغيره.

---

## 6. Definition of Done واختبارات التحقق

### Definition of Done (Runtime):
1. `GoalManager.create_plan_for_goal()` ينتج `Plan` كامل من `Goal` واحد
2. `Plan.missions` يحتوي على `List[str]` من `mission_id` المحفوظة
3. `Plan.dependencies` يحتوي على dependency structure صحيحة
4. `Goal.constraints` تصل إلى كل `Mission.context`
5. `Plan.approval_policy` مُعرّف كـ structure فقط
6. `parent_goal_id` يُستخدم فعلياً في decomposition
7. `Plan.fallback_strategy` مُعرّف
8. Re-planning boundaries محددة وموثقة
9. **لا** يتطلب `ReasoningEngine` أو `AutonomyPolicy` enforcement ليعمل
10. **لا** ي改性 أي من `Decision`, `Mission`, `Task`, `ExecutionPlan` schemas
11. Plan lifecycle تتبع السلوك الحالي: `create_plan()` → `activate_plan()`

### اختبارات التحقق المطلوبة:
1. **Goal Analysis Test** — تحليل Goal صحيح يحدد المكونات الأساسية
2. **Sub-goal Decomposition Test** — Goal معقد يُقسم إلى sub-goals صحيحة محفوظة في `GoalRepository`
3. **Plan Generation Test** — `PlanPlanner.create_plan()` ينتج Plan كامل مع `missions=[]` ثم يتم ملؤها
4. **Mission Persistence Test** — Missions تُحفظ وتُربط بالـPlan عبر `PlanManager.append_mission()`
5. **Mission Sequencing Test** — `Plan.missions` مرتبة بالترتيب الصحيح حسب `Plan.dependencies`
6. **Dependency Mapping Test** — `Plan.dependencies` يحتوي على structure صحيحة
7. **Constraints Propagation Test** — `Goal.constraints` تصل إلى `Mission.context`
8. **Fallback Structure Test** — `Plan.fallback_strategy` مُعرّف بشكل صحيح
9. **Re-planning Boundaries Test** — triggers محددة بشكل صحيح
10. **Lifecycle Test** — `GoalManager.create_plan_for_goal()` يتبع سلوك `create_plan()` → `activate_plan()` الحالي
11. **End-to-End Test** — `Goal → Decomposition → Plan → persisted Mission IDs + dependency structure` يعمل بدون أي dependency خارجية
12. **Regression Test** — لا تأثير على `ReasoningEngine`, `ApprovalGate`, `Decision Engine`

---

## 7. Dependencies و Integration Boundaries

### Dependencies:
| Dependency | Status | كيفية الاستخدام |
|------------|--------|-----------------|
| Goal/Plan Foundation | CLOSED | Input: `Goal` object, schemas, repositories |
| `GoalManager` | موجود | Entry point: `create_plan_for_goal()` |
| `PlanManager` | موجود | Plan lifecycle management: `create_plan()` → `activate_plan()` |
| `PlanPlanner` | موجود | Plan generation (سيتم تعديله) |
| `PlanRepository` | موجود | Persistence للـPlan |
| `GoalRepository` | موجود | Reading Goal data + saving sub-goals |
| `MissionPlanner` | موجود | Mission creation (يستخدم لإنشاء Mission objects) |
| Knowledge/Memory | Optional | Non-blocking hints for decomposition |
| `ReasoningEngine` | **لا يعتمد** | لا يستخدم في التشغيل الأساسي |
| `AutonomyPolicy` | **لا يعتمد** | لا يستخدم في التشغيل الأساسي |
| `Decision` | **لا يعتمد** | Decomposition ينتج Plan/Missions، وليس Decisions |
| `TaskPlanner` | **لا يعتمد** | لا يستقبل Plan كـ input في الـruntime الحالي |

### Integration Boundaries:
- **مع Goal/Plan Foundation:** Decomposition يبني فوق Foundation، لا يعدل الـschemas الأساسية
- **مع Deep Strategic Reasoning:** Decomposition output هو input للـStrategic Reasoning (لا overlap)
- **مع Runtime Autonomy Enforcement:** Decomposition output هو input للـAutonomy Enforcement (لا overlap)
- **مع Mission/Task Execution:** Decomposition ينتج Plan/Missions فقط، لا ينفذها
- **مع Business Response:** لا علاقة مباشرة
- **مع TaskPlanner:** TaskPlanner يأخذ `Decision` كـ input، وليس Plan. Decomposition لا يصمم للاندماج المباشر مع TaskPlanner.

### Lifecycle Boundary:
- `GoalManager.create_plan_for_goal()` الحالي: ينشئ Plan → يُفعّله مباشرة
- Decomposition يتبع هذا السلوك: ينتج Plan معmissions، ثم `PlanManager.activate_plan()` يُستدعى كما هو
- لا تغيير في lifecycle semantics

---

## 8. Explicit Non-Goals

### خارج النطاق تماماً:
1. **لا Deep Strategic Reasoning** — لا تقرر HOW تنفيذ الهدف
2. **لا Runtime Autonomy Enforcement** — لا تمنع أو تسمح بالتنفيذ
3. **لا Tool execution** — لا تنفذ أي tools
4. **لا Mission execution** — لا تدير تنفيذ Missions
5. **لا Business Response generation** — لا تنتج `IntentContent` أو responses
6. **لا Avatar rendering** — لا تتعامل مع presentation
7. **لا Multi-agent coordination** — خارج النطاق
8. **لا LLM-based strategic decisions** — decomposition يمكن أن يكون deterministic أو assisted، لكن decision logic stays out. إذا كان الهدف يحتاج إلى LLM لفهمه بشكل موثوق، يُسجّل كـ boundary/deferred constraint
9. **لا تعديل ReasoningEngine** — بدون تغيير
10. **لا تعديل ApprovalGate** — بدون تغيير
11. **لا تعديل Decision Engine** — بدون تغيير
12. **لا تعديل Mission/Task/ExecutionPlan schemas** — بدون تغيير
13. **لا تعديل WP-43/WP-44/WP-45** — خارج النطاق
14. **لا database migration** — بدون تغيير schema
15. **لا Multi-agent coordination** — خارج النطاق
16. **لا إعادة تصميم TaskPlanner** — TaskPlanner يأخذ `Decision` كـ input في الـruntime الحالي، ولا علاقة مباشرة بـ Decomposition
17. **لا تغيير Plan.missions semantics** — يبقى `List[str]` من `mission_id`
18. **لا إضافة depends_on إلى Mission schema** — dependency ordering يُحفظ في `Plan.dependencies`

---

## 9. الملفات المطلوبة للتنفيذ

### ملفات جديدة محتملة:
| File | الغرض |
|------|--------|
| `backend/app/agent/plan/decomposer.py` | `PlanDecomposer` — المنطق الرئيسي لتحويل Goal إلى Plan/Missions (اختياري: يمكن وضعه في `PlanPlanner`) |
| `backend/tests/agent/test_plan_decomposition.py` | اختبارات الـcapability |

### ملفات معدلة:
| File | التغيير |
|------|---------|
| `backend/app/agent/plan/planner.py` | إضافة decomposition logic: goal analysis → sub-goals → mission creation → sequencing → dependency mapping → constraints propagation |
| `backend/app/agent/plan/manager.py` | إضافة re-planning boundary logic و fallback structure management |
| `backend/app/agent/goal/manager.py` | تحديث `create_plan_for_goal()` لاستدعاء decomposition logic الجديد مع الحفاظ على سلوك `create_plan()` → `activate_plan()` |

### ملاحظة:
- `PlanDecomposer` كملف منفصل هو **اختياري** وليس مطلوباً. يمكن وضع decomposition logic داخل `PlanPlanner` لتقليل عدد الملفات الجديدة.
- لا حاجة لملفات جديدة إلا إذا أثبتت الضرورة.

---

## 10. Risk and Edge Cases

| Risk | Mitigation |
|------|------------|
| Goal يحتاج إلى LLM لفهمه بشكل صحيح | Decomposition يمكن أن تكون deterministic أولاً، ثم يمكن إضافة LLM assistance كـ enhancement لاحقاً |
| Sub-goals كثيرة جداً | حد أقصى لعدد sub-goals قابل للتكوين |
| Circular dependencies بين Missions | Validation في decomposition logic يمنعها |
| Plan constraints لا تصل إلى Missions | Test مخصص يتحقق من propagation |
| Re-planning triggers خاطئة | Documentation و tests واضحة للـboundaries |

---

## 11. Architecture Decision Records (ADRs)

### ADR-001: Decomposition Logic Location
**القرار:** وضع decomposition logic في `PlanPlanner` (تعديل الملف الموجود) بدلاً من إنشاء `PlanDecomposer` منفصل.
**السبب:** الحفاظ على بساطة الـarchitecture وعدم إنشاء layers جديدة غير ضرورية. `PlanPlanner` هو already responsible لـ Plan generation،所以 إضافة decomposition logic إليه طبيعي.

### ADR-002: Sub-goal Storage
**القرار:** sub-goals تُخزن كـ `Goal` objects منفصلة مع `parent_goal_id` يشير إلى Goal الأصلي.
**السبب:** يعيد استخدام `Goal` schema و repositories الموجودة، ولا يتطلب schema changes.

### ADR-003: Re-planning Triggers
**القرار:** Re-planning triggers تُحدد كـ signals فقط، بدون تنفيذ فعلي.
**السبب:** تنفيذ re-planning فعلي يتطلب Runtime Autonomy Enforcement و Decision Engine integration، وهو خارج النطاق الحالي.

---

## 12. Validation Plan

### Unit Tests:
- Goal analysis logic
- Sub-goal decomposition (creation + persistence via `GoalRepository`)
- Plan generation
- Mission creation and persistence
- Mission sequencing based on `Plan.dependencies`
- Dependency mapping in `Plan.dependencies` (not `Mission.depends_on`)
- Constraints propagation from `Goal.constraints` to `Mission.context`
- Fallback structure definition in `Plan.fallback_strategy`
- Re-planning boundaries detection

### Integration Tests:
- `Goal → Decomposition → Plan → persisted Mission IDs + dependency structure` end-to-end
- Integration مع `PlanManager` و `GoalManager` و `MissionPlanner`
- Lifecycle test: `GoalManager.create_plan_for_goal()` follows `create_plan()` → `activate_plan()` sequence
- Regression tests لـ `ReasoningEngine`, `ApprovalGate`, `Decision Engine`

### Manual Verification:
- تشغيل سيناريو Goal بسيط → Plan → Missions
- تشغيل سيناريو Goal معقد مع sub-goals
- تشغيل سيناريو Goal مع constraints
- التحقق من عدم تأثير التغييرات على现有的 functionality
- التحقق من أن `Plan.missions` يحتوي على `mission_id` strings فقط
- التحقق من أن `Plan.dependencies` هو الـsingle source of truth للتبعيات

---

## 13. Lifecycle Boundary

### Current Lifecycle (الحالي):
```python
# GoalManager.create_plan_for_goal() الحالي
plan = plan_planner.create_plan(goal_id=goal_id, ...)
plan_manager.create_plan(plan)
plan_manager.activate_plan(plan.plan_id, user_id)
```

### Decomposition Lifecycle (المخطط):
- يتبع نفس السلوك الحالي
- `PlanPlanner.create_plan()` ينتج Plan مع `missions=[]` أولاً
- Decomposition logic يضيف `missions` كـ `mission_id` strings
- `PlanManager.create_plan()` يحفظ Plan
- `PlanManager.activate_plan()` يُفعل Plan
- **لا تغيير في lifecycle semantics**

### Plan.missions Semantics:
- `Plan.missions` هو `List[str]` من `mission_id`
- Mission objects يُحفظون بشكل منفصل
- `PlanManager.append_mission()` هو الأداة الحالية لربط `mission_id` بالـPlan

### Plan.dependencies Semantics:
- `Plan.dependencies` هو الـsingle source of truth للتبعيات
- `Mission` schema لا تحتوي `depends_on`
- Dependency structure يمكن أن تكون list of tuples أو format متوافق مع الـschema الحالي

---

## 14. Timeline / Implementation Order

1. **المرحلة 1:** Goal Analysis + Sub-goal Decomposition logic
2. **المرحلة 2:** Plan Generation + Mission Creation
3. **المرحلة 3:** Mission Sequencing + Dependency Mapping (in `Plan.dependencies`)
4. **المرحلة 4:** Constraints Propagation + Fallback Structure
5. **المرحلة 5:** Re-planning Boundaries + Integration Tests

---

## 15. الخلاصة

هذه الخطة تحدد **Strategic Goal/Plan Decomposition** كـ capability مستقلة مع:
- Entry Point واضح: `GoalManager.create_plan_for_goal()`
- Inputs/Outputs واضحة ومتوافقة مع الـruntime الحالي
- مسؤوليات محددة بدون overlap مع capabilities أخرى
- Definition of Done قابل للتحقق فعلياً من الـrepository
- Non-Goals واضحة
- Dependencies محددة
- Lifecycle boundary محدد: يتبع سلوك `create_plan()` → `activate_plan()` الحالي
- Mission persistence واضح: `Plan.missions` = `List[str]` من `mission_id`
- Dependency ordering واضح: يُحفظ في `Plan.dependencies` فقط

الخطة جاهزة للانتقال إلى Code عند الحاجة.

---

```
STRATEGIC GOAL/PLAN DECOMPOSITION PLAN READY
```
