# Contract Plan — AI Autonomy Policy Runtime Enforcement

**الفرع:** `main`
**الحالة:** Plan — READY FOR CODE
**الموقع:** `.kilo/plans/1788647877906-ai-autonomy-policy-runtime-enforcement.md`

---

## 1. Gap

- **`AutonomyPolicyInterpreter`** يبني `AutonomyPolicy` من Goal/Plan لكنه **لا يفرضها وقت التشغيل**.
- **`AutonomyEvaluator`** يقيّم العمليات ويُنتج `AutonomyEvaluationSignal` (blocked / approval_required / allowed) لكنه **لا يمنع التنفيذ**.
- **`ToolOrchestrator`** يملك `ApprovalGate` لكنه يعتمد على **string matching** بسيط (intent/parameters) ولا يرتبط بـ AutonomyPolicy.
- **`AgentOrchestrator`** ينفّذ الأدوات مباشرة بدون أي فحص autonomy.
- **النتيجة:** لا يوجد enforcement layer يربط السياسة بمسار التنفيذ. السياسة موجودة كعقد فقط.

---

## 2. Architecture

### 2.1 المكونات الحالية

```
AutonomyPolicyInterpreter → يبني AutonomyPolicy من Goal/Plan
AutonomyEvaluator → يقيّم العملية مقابل Policy/Context/History → Signal
ApprovalGate → يفحص العمليات الحساسة (string matching)
ToolOrchestrator → ينفّذ الأدوات مع approval gate check
AgentOrchestrator → ينفّذ الأدوات مباشرة بدون autonomy check
AuditRecorder → يسجل في agent_audit_logs
```

### 2.2 التعديل المعماري

```
AutonomyPolicyInterpreter → AutonomyPolicy (كما هو)
AutonomyEvaluator → AutonomyEvaluationSignal (كما هو)
AutonomyEnforcer (جديد) → AutonomyEnforcementDecision (قbinding)
                                 │
                                 ▼
ToolOrchestrator / AgentOrchestrator
    │
    ├── BLOCK → إيقاف فوري + Audit + خطأ
    ├── APPROVAL_REQUIRED → Approval Request/Record → PENDING_APPROVAL state → Explicit Approval → Resume → Tool Execution
    └── ALLOW → ApprovalGate check → تنفيذ
                                 │
                                 ▼
                          Tool Execution
```

### 2.3 المكون الجديد: `AutonomyEnforcer`

**الموقع:** `backend/app/agent/autonomy/enforcer.py`

**المسؤولية:**
- يربط `AutonomyPolicyInterpreter` + `AutonomyEvaluator` بمسار التنفيذ.
- ينتج قرار **ملزم**: `ALLOW` | `APPROVAL_REQUIRED` | `BLOCK`.
- يسجل كل قرار في `AuditRecorder`.
- يعالج failures بآمنة (لا يصير `ALLOW` تلقائيًا عند الفشل).
- **لا يمكن تعطيله للعمليات الحساسة.**

### 2.4 Sensitive Operations Contract

**Canonical Sensitivity Helper:**

```python
def is_sensitive_operation(approval_gate, tool_name, parameters, risk):
    """Canonical helper to determine if an operation is sensitive.

    Returns True if ANY of the following is true:
    - risk == "high"
    - approval_gate.check_approval() returns True
    """
    if risk == "high":
        return True
    if approval_gate is None:
        return False
    intent = parameters.get("intent", "") or tool_name
    requires_approval, _ = approval_gate.check_approval(
        chosen_path="",
        intent=intent,
        parameters=parameters,
    )
    return requires_approval
```

**Risk Sources (canonical, no invented heuristics):**

- `context["risk"]` when provided by execution context/policy/task metadata.
- `risk` parameter passed from orchestrator derived from existing metadata.
- If no explicit `risk` is available, use `risk=None` and rely on `ApprovalGate.check_approval()`.

**القاعدة:** 
- العمليات الحساسة **تخضع دائماً** لـ AutonomyEnforcement حتى لو لم يكن هناك Policy.
- غياب `autonomy_enforcer` للعمليات الحساسة = `APPROVAL_REQUIRED` (safe default)، ليس ALLOW.
- العمليات غير الحساسة (non-sensitive) بدون Policy = `ALLOW` (backward compatibility).
- **لا يجوز أن يصبح `risk == "high"` غير حساس فقط لأن `ApprovalGate.check_approval()` أعاد False.** Helper يتحقق من `risk` أولاً.

**تنفيذ:**
- `ToolOrchestrator` و `AgentOrchestrator` يستخدمان `is_sensitive_operation()` قبل استدعاء `AutonomyEnforcer.enforce()`.
- `AutonomyEnforcer` يرفض `ALLOW` للعمليات الحساسة بدون Policy صريحة.
- fallback بدون enforcer يستخدم نفس الـhelper.

**العقد:**

```python
class AutonomyEnforcementDecision:
    decision: str  # ALLOW | APPROVAL_REQUIRED | BLOCK
    operation: str
    policy_ref: Dict[str, Any]  # goal_id, plan_id, autonomy_level
    reason: str
    evidence: Dict[str, Any]
    timestamp: str
    trace: Dict[str, Any]  # decision trace for audit
```

```python
class AutonomyEnforcer:
    def __init__(
        self,
        policy_interpreter: AutonomyPolicyInterpreter,
        evaluator: AutonomyEvaluator,
        audit_recorder: AuditRecorder,
        goal_repository: GoalRepository,
        plan_repository: PlanRepository,
        approval_gate: Optional[ApprovalGate] = None,
    ):
        ...

    def enforce(
        self,
        operation: str,
        context: Dict[str, Any],
        risk: Optional[str] = None,
    ) -> AutonomyEnforcementDecision:
        """Evaluate and return binding autonomy decision.

        Flow:
        1. Resolve policy from context (goal_id, plan_id)
        2. If no policy → ALLOW (backward compatibility)
        3. If policy exists → evaluate via AutonomyEvaluator
        4. On evaluation failure → APPROVAL_REQUIRED (safe default)
        5. Record decision in audit
        6. Return binding decision
        """
```

---

## 3. Enforcement Point

### 3.1 النقطة الوحيدة

**في `ToolOrchestrator.execute()`** — بعد فحص التبعيات وقبل `ApprovalGate.check_approval()`.

**الموقع:** السطر ~177 في `backend/app/agent/execution_engine/orchestrator.py`

```python
# 1. Dependency checks (existing)
# 2. Autonomy Enforcement (NEW)
# 3. Approval Gate (existing)
# 4. Tool Execution (existing)
```

### 3.2 في `AgentOrchestrator.execute()`

**الموقع:** السطر ~97 في `backend/app/agent/core/orchestrator.py`

```python
# 1. Planning (existing)
# 2. For each step:
#    a. Autonomy Enforcement (NEW)
#    b. Tool Execution (existing)
```

### 3.3 لماذا هذه النقطة؟

- لا يمكن تنفيذ أي أداة بدون المرور بهذه النقطة.
- جميع مسارات التنفيذ تمر عبر `ToolOrchestrator` أو `AgentOrchestrator`.
- لا يوجد مسار بديل لتنفيذ الأدوات.

---

## 4. Decision Contract

### 4.1 القرارات النهائية

| Decision | المعنى | المسار |
|----------|--------|--------|
| `ALLOW` | العملية مسموحة ضمن السياسة | استمر في `ApprovalGate` ثم التنفيذ |
| `APPROVAL_REQUIRED` | العملية تحتاج موافقة بشرية | إنشاء approval_state → PENDING_APPROVAL → Explicit Approval → Resume → تنفيذ |
| `BLOCK` | العملية ممنوعة | إيقاف فوري + Audit + خطأ |

### 4.2 شروط القرار

**`ALLOW`:**
- `autonomy_level == "full"` AND
- العملية ليست destructive AND
- لا توجد مخالفة policy AND
- السياق active (goal/plan not terminal) AND
- **إما:** العملية غير حساسة (non-sensitive)
- **أو:** العملية حساسة و policy صريحة تسمح بها
- **أو:** العملية حساسة و يوجد `approval_proof` صالح (approved re-entry)

**`APPROVAL_REQUIRED`:**
- العملية حساسة ولا توجد policy صريحة لها AND لا يوجد `approval_proof` صالح
- **ملاحظة:** `approval_proof` الصحيح يحول `APPROVAL_REQUIRED` إلى `ALLOW` كـ approved re-entry، حتى بدون Policy.
- `autonomy_level == "manual"` OR
- العملية destructive OR
- مخاطرة عالية OR
- تاريخ تنفيذ غير كافٍ OR
- فشل evaluator (graceful degradation) OR
- `autonomy_enforcer` غير متاح (fallback آمن)

**`BLOCK`:**
- العملية محظورة صراحةً في `allowed_operations` OR
- terminal goal/plan state OR
- مخاطرة حرجة بدون مسار موافقة
- **ملاحظة:** `BLOCK` لا يمكن تجاوزه حتى مع `approval_proof`.

### 4.3 No-Policy Behavior

| نوع العملية | Policy موجودة؟ | القرار |
|-------------|----------------|--------|
| Non-sensitive | لا | `ALLOW` (backward compatibility) |
| Sensitive | لا | `APPROVAL_REQUIRED` (safe default) |
| أي | نعم | evaluation عبر AutonomyEvaluator |

### 4.4 Approval Lifecycle

`APPROVAL_REQUIRED` يمر بالحياة التالية:

```
APPROVAL_REQUIRED
    → Orchestrator ينشئ approval_state في SessionManager
    → PENDING_APPROVAL في agent_sessions.context
    → Existing Approval API (/approvals/{id}/approve | /reject)
    → Explicit Approval يُسجل في audit_logs + mission state
    → Resume Handler يتحقق من approval_state
    → نفس المهمة/الخطوة تنفذ
```

**المراحل:**

1. **Approval Request/Record:** Orchestrator يكتب approval_state في `SessionManager` داخل `agent_sessions.context`.
2. **PENDING_APPROVAL state:** `SessionManager` يُحدّث حالة الـmission إلى `pending_approval`.
3. **Explicit Approval:** المستخدم يرسل قرار عبر existing API `POST /approvals/{id}/approve`.
4. **Resume:** مكوّن Resume يتحقق من `approval_state` ثم يستأنف نفس المهمة/الخطوة.
5. **Tool Execution:** تنفيذ الأداة فقط بعد `APPROVED + explicit_approval`.

**الفرق بين المفاهيم:**

| مفهوم | الوصف |
|--------|-------|
| `ApprovalGate.check_approval()` | تقييم/تحديد الحاجة للموافقة بناءً على السياق. لا يُعتبر موافقة بشرية. |
| Explicit Approval | قرار بشري فعلي مسجل وموثق عبر existing approval API. |
| Resume | استئناف تنفيذ نفس المهمة/الخطوة بعد التحقق من وجود APPROVED + explicit_approval. |

**Persistence:**

- **مصدر الحالة:** `SessionManager` يخزن `approval_state` في `agent_sessions.context` كجزء من mission.
- **المرجع:** `mission_id` + `task_id` + `step_id` (أو ما يعادله في الكود الحالي).
- **بدون explicit approval → لا يوجد execution.**

**الربط بـ ApprovalGate والـAPIs الموجودة:**

- `ApprovalGate.check_approval()` يُستدعى لتحديد الحاجة للموافقة فقط.
- **Important:** existing approval endpoints لا تُحدّث `approval_state` إلى `APPROVED` ولا تشغّل Resume حاليًا. لذلك الكود المطلوب يتضمن **تعديلاً بسيطاً** لـ:
  - `POST /approvals/{id}/approve` ← تحميل `approval_state` من `SessionManager` → تحديث `status` إلى `APPROVED` + تعبئة `explicit_approval` → حفظ عبر `SessionManager.update_mission_status()` → استدعاء `ResumeService.resume_if_approved()`
  - `POST /approvals/{id}/reject` ← تحديث `status` إلى `REJECTED` → حفظ → لا execution
- `GET /approvals` ← `SessionManager.get_pending_approvals()` كما هو.
- ApprovalGate وحدها لا يمكنها تحويل `APPROVAL_REQUIRED` إلى `ALLOW`.

**العقد:**

```python
# approval_state يُحفظ في agent_sessions.context كجزء من mission
mission_context = {
    "mission_id": str,
    "task_id": str,
    "step_id": str,
    "operation": str,
    "status": "PENDING_APPROVAL" | "APPROVED" | "REJECTED",
    "autonomy_decision": Dict[str, Any],
    "approval_gate_result": Dict[str, Any],
    "explicit_approval": Optional[Dict[str, Any]],
    "created_at": str,
    "updated_at": str,
}
```

**قواعد الاستئناف:**

- Resume يتحقق من `mission_context["status"] == "APPROVED"` ووجود `explicit_approval`.
- بدون explicit approval → يبقى في `PENDING_APPROVAL` ولا يتم التنفيذ.
- بعد explicit approval → يستأنف نفس المهمة/الخطوة ثم ينفذ.
- `REJECTED` → يبقي التنفيذ متوقفًا.
- **Idempotency:** بعد نجاح Resume، يتم تحديث الحالة إلى `RESUMED` لمنع تنفيذ المهمة مرتين.
- **No Re-approval Loop:** `ResumeService` يمرر `approval_proof` في السياق إلى `AutonomyEnforcer`، الذي يتحقق من صحة الموافقة ولا يعيد إصدار `APPROVAL_REQUIRED` لنفس `approval_id == mission_id` + `task_id` + `step_id`.

**Approval Transition Rules (إلزامي):**

```text
PENDING_APPROVAL → APPROVED  (عبر /approve)
PENDING_APPROVAL → REJECTED  (عبر /reject)

APPROVED → RESUMING  (atomic claim)
RESUMING → RESUMED   (بعد نجاح التنفيذ فقط)

APPROVED / RESUMING / RESUMED / REJECTED → لا يمكن إعادة approve
REJECTED → لا Resume
```

**مصدر الحقيقة (Source of Truth):**

- `approval_state.status` هو مصدر الحقيقة الوحيد لدورة الموافقة.
- `mission.status` هو projection فقط، ولا يمكنه بمفرده السماح بالتنفيذ.
- جميع قرارات التنفيذ تعتمد على `approval_state.status` فقط.
- كل transition يحدّث `approval_state.status` أولاً، ثم `mission.status` باتساق.

**State Casing الموحد:**

```text
approval_state.status:
PENDING_APPROVAL
APPROVED
REJECTED
RESUMING
RESUMED

mission.status:
pending_approval
approved
rejected
resuming
resumed
```

**قواعد التحديث:**

- `approval_state.status = "PENDING_APPROVAL"` → `mission.status = "pending_approval"`
- `approval_state.status = "APPROVED"` → `mission.status = "approved"`
- `approval_state.status = "REJECTED"` → `mission.status = "rejected"`
- `approval_state.status = "RESUMING"` → `mission.status = "resuming"`
- `approval_state.status = "RESUMED"` → `mission.status = "resumed"`

### 4.5 Approval Required Contract (Legacy)

`APPROVAL_REQUIRED` في التصميم الحالي يعني:
1. **إيقاف التنفيذ فورًا** — لا يتم تنفيذ الأداة.
2. **إيقاف المهمة بالكامل** — لا يمكن الانتقال لأدوات/خطوات لاحقة. العملية في حالة `PENDING_APPROVAL` حتى موافقة صريحة خارجية.
3. **تسجيل الحالة كـ `PENDING_APPROVAL`** — هذا ليس مجرد تغيير status، بل يمنع الاستمرار في المسار الحالي بأكمله.
4. **التمرير عبر `ApprovalGate`** — يتم فحص إضافي من خلال ApprovalGate الحالي لتحديد ما إذا كانت العملية تحتاج موافقة بشرية فعلية. لكن ApprovalGate **لا يمكنها تحويل APPROVAL_REQUIRED إلى ALLOW**.
5. **العملية تنتظر قرار خارجي** — لا تستمر في التنفيذ بدون موافقة صريحة.

**الربط بـ ApprovalGate:**
- `APPROVAL_REQUIRED` من AutonomyEnforcer → `ApprovalGate.check_approval()` → إذا كانت النتيجة `requires_approval=True` → يتم إيقاف المهمة مؤقتًا.
- إذا كانت النتيجة `requires_approval=False` → **يظل التنفيذ متوقفاً** لأن AutonomyEnforcer حددت أن موافقة مطلوبة. ApprovalGate هنا لتأكيد حالة الموافقة، وليس لتجاوز قرار Enforcer.
- لا يوجد تلقائي لتجاوز ApprovalGate أو قرار AutonomyEnforcer.

---

## 5. Security Model

### 5.1 منع Bypass

1. **نقطة واحدة:** كل تنفيذ أدوات يمر عبر `AutonomyEnforcer.enforce()`.
2. **لا يوجد skip flag:** لا معلمة أو سياق يسمح بتجاوز Enforcement.
3. **قرار ملزم:** Orchestrator يطبق القرار فورًا بدون مراجعة لاحقة.
4. **Audit مسبق:** القرار يُسجل قبل التنفيذ.
5. **إلزامية للعمليات الحساسة:** حتى لو كان `autonomy_enforcer=None`، العمليات الحساسة تنتقل تلقائيًا إلى `APPROVAL_REQUIRED` ولا تُنفذ.
6. **No fallback to ALLOW for sensitive ops:** أي فشل في enforcement للعمليات الحساسة = `APPROVAL_REQUIRED`.

### 5.2 Graceful Degradation

| الحالة | القرار | السبب |
|--------|--------|-------|
| Policy موجود + Evaluator فشل | `APPROVAL_REQUIRED` | لا نسمح بـ ALLOW عند عدم اليقين |
| Policy موجود + Memory/History غير متاح | `APPROVAL_REQUIRED` | safe default |
| Policy غير موجود + عملية non-sensitive | `ALLOW` | backward compatibility |
| Policy غير موجود + عملية sensitive | `APPROVAL_REQUIRED` | لا نسمح بـ ALLOW لعمليات حساسة بدون policy |
| Enforcement itself fails + عملية non-sensitive | `ALLOW` | backward compatibility |
| Enforcement itself fails + عملية sensitive | `APPROVAL_REQUIRED` | never silent ALLOW |
| `autonomy_enforcer=None` + عملية non-sensitive | `ALLOW` | backward compatibility |
| `autonomy_enforcer=None` + عملية sensitive | `APPROVAL_REQUIRED` | إلزامي حتى بدون enforcer |

### 5.3 Human-in-the-Loop

- `APPROVAL_REQUIRED` يمر عبر `ApprovalGate` الحالي.
- `ApprovalGate` يحدد ما إذا كانت العملية تحتاج موافقة بناءً على السياق.
- `BLOCK` لا يمكن تجاوزه بدون تعديل السياسة (عملية إدارية).
- جميع القرارات قابلة للتدقيق.

---

## 6. Audit Model

كل قرار enforcement يُسجل في `agent_audit_logs` عبر `AuditRecorder`:

```python
audit_recorder.record_agent_action(
    session_id=session_id,
    agent_id=agent_id,
    action="autonomy_enforcement",
    input_data={
        "operation": operation,
        "policy_ref": policy_ref,
        "context_summary": {
            "goal_id": context.get("goal_id"),
            "plan_id": context.get("plan_id"),
            "chosen_path": context.get("chosen_path"),
            "user_id": context.get("user_id"),
        },
        "risk": risk,
    },
    output_data={
        "decision": decision,  # ALLOW | APPROVAL_REQUIRED | BLOCK
        "reason": reason,
        "evidence": evidence,
        "proposed_autonomy_level": proposed_level,
    },
    duration_ms=duration_ms,
)
```

---

## 7. Integration Contract

### 7.1 بين `AutonomyPolicyInterpreter` و `AutonomyEnforcer`

- **Input:** Goal/Plan data (goal_id, plan_id, autonomy_level, allowed_operations, required_approvals)
- **Output:** `AutonomyPolicy`
- **Enforcer responsibility:** يستدعي Interpreter لبناء Policy من السياق.

### 7.2 بين `AutonomyEvaluator` و `AutonomyEnforcer`

- **Input:** operation, policy, context, execution_history, memory_provider
- **Output:** `AutonomyEvaluationSignal`
- **Enforcer responsibility:** يستدعي Evaluator ويحوّل الإشارة إلى قرار ملزم.
- **Contract Update Required:** `AutonomyEvaluationSignal` يجب أن يشير صراحةً ما إذا كانت العملية حساسة (sensitive) أم لا، أو أن Enforcer يحدد ذلك من `context["is_sensitive"]`.

### 7.3 بين `AutonomyEnforcer` و `ApprovalGate`

- **APPROVAL_REQUIRED:** قرار binding من AutonomyEnforcer. لا يمكن لـ ApprovalGate تحويله إلى ALLOW.
- **الغرض من ApprovalGate هنا:** فحص إضافي لتحديد ما إذا كانت العملية تحتاج موافقة بشرية فعلية، وليس لتجاوز قرار Enforcer.
- **ALLOW:** يظل فحص ApprovalGate الحالي كخطوة دفاع إضافية.
- **BLOCK:** لا يصل إلى ApprovalGate.
- **Binding Rule:** APPROVAL_REQUIRED + ApprovalGate.requires_approval=True → التنفيذ متوقف فعلياً.
- **No Override:** ApprovalGate لا يمكنها إلغاء APPROVAL_REQUIRED من AutonomyEnforcer.
- **ApprovalGate ليست approval record:** `ApprovalGate.check_approval()` هي فحص حساسية/سياسة، وليس سجل موافقة. الموافقة الصريحة محفوظة داخل `approval_state["explicit_approval"]` فقط.
- **Resume Re-entry contract:** إذا كان `approval_proof` صالحًا لنفس `approval_id + task_id + step_id`، فإن AutonomyEnforcer ينتج `ALLOW`. في هذه الحالة:
  - ApprovalGate تظل كدفاع إضافي
  - ApprovalGate لا يمكنها إعادة فتح نفس approval lifecycle
  - ApprovalGate لا يمكنها تحويل `ALLOW` إلى `APPROVAL_REQUIRED` إذا كان القرار ناتجًا عن valid `approval_proof`
  - هذا is a legitimate re-entry state لنفس approval، وليس bypass
- **ToolOrchestrator behavior:** بعد `AutonomyEnforcer` يعيد `ALLOW` مع `approval_proof` صالح، لا يجوز لـ `ToolOrchestrator` أن يعيد حالة المهمة إلى `PENDING_APPROVAL` بناءً على نتيجة `ApprovalGate.check_approval()`. ApprovalGate هنا للدفاع فقط.

### 7.4 بين `AutonomyEnforcer` و Orchestrators

- **ToolOrchestrator:** يطلب قرار قبل كل أداة.
- **AgentOrchestrator:** يطلب قرار قبل كل خطوة.
- **APPROVAL_REQUIRED Binding في كلاهما:** إذا أصدر AutonomyEnforcer قرار `APPROVAL_REQUIRED`، فإن Orchestrator **يستدعي ApprovalGate.check_approval() فورًا** ثم **يوقف المهمة بالكامل** (Mission Status → `PENDING_APPROVAL`). لا يمكن الانتقال لأدوات/خطوات لاحقة.
- **BLOCK:** Orchestrator يوقف التنفيذ فورًا مع خطأ.
- **ALLOW:** يمر عبر ApprovalGate كدفاع إضافي ثم التنفيذ.
- **Mandatory for sensitive operations:** لا يمكن تشغيل Orchestrator بدون AutonomyEnforcer للعمليات الحساسة.
- **Explicit Approval Gate:** `APPROVAL_REQUIRED` في `AgentOrchestrator` لا يكتفي بتسجيل `pending_approval`، بل يمر عبر `ApprovalGate.check_approval()` كجزء من مسار الموافقة الفعلية.
- **Resume Re-entry Prevention:** عند استدعاء Resume لـ Orchestrator، يضيف `approval_proof` إلى السياق. `AutonomyEnforcer` يتحقق من صحة `approval_proof` (نفس `approval_id == mission_id` + `task_id` + `step_id` + `status == APPROVED`) ويرجع `ALLOW` دون إعادة تقييم. `BLOCK` لا يمكن تجاوزه حتى مع `approval_proof`.
- **Resume Execution Path:** Resume لا يستدعي `AgentOrchestrator.execute()` مباشرة ولا يستدعي `tool.execute()` مباشرة. Resume يمر عبر `ToolOrchestrator.execute(execution_plan, session_context)` canonical path فقط.
- **approval_proof propagation:** `ResumeService` يمرر `approval_proof` عبر `session_context` إلى `ToolOrchestrator.execute()`. `ToolOrchestrator` ينسخ `approval_proof` إلى `context_for_enforcement` قبل استدعاء `AutonomyEnforcer.enforce()`. بهذه الطريقة يصل `approval_proof` من Resume إلى Enforcer.

### 7.5 Enforcement / Re-entry Contract

- `AutonomyEnforcer.enforce()` يتحقق من `context.get("approval_proof")`.
- إذا وجد `approval_proof` و جميع الشروط التالية صحيحة:
  - `approval_proof["status"] == "APPROVED"`
  - `approval_proof["approval_id"] == mission_id`
  - `approval_proof["task_id"] == task_id`
  - `approval_proof["step_id"] == step_id`
  - `approval_proof["explicit_approval"]` موجود
  → يرجع `ALLOW` مباشرة دون إعادة تقييم.
- **هذا ينطبق حتى بدون Policy.** `approval_proof` هو دليل موافقة بشرية صريحة ومحددة لنفس execution identity، وليس policy.
- `BLOCK` لا يمكن تجاوزه حتى مع `approval_proof`.
- `approval_proof` صالح فقط لنفس `approval_id == mission_id` + `task_id` + `step_id`.
- لا يوجد bypass عام لـ `AutonomyEnforcer`.
- Resume لا ينشئ execution path بديل. Resume يمر عبر `ToolOrchestrator.execute()` canonical path فقط.

---

## 8. Tests

### 8.1 Unit Tests

| # | Test | الهدف |
|---|------|--------|
| 1 | `test_enforce_allow_path` | عملية مسموحة → تنفذ |
| 2 | `test_enforce_approval_required_path` | عملية تحتاج موافقة → لا تنفذ مباشرة |
| 3 | `test_enforce_block_path` | عملية محظورة → إيقاف |
| 4 | `test_enforce_bypass_prevention` | لا يمكن تجاوز Enforcement |
| 5 | `test_enforce_policy_evaluation_failure` | فشل Evaluator → APPROVAL_REQUIRED |
| 6 | `test_enforce_missing_policy_non_sensitive` | عملية non-sensitive بدون Policy → ALLOW |
| 7 | `test_enforce_missing_policy_sensitive` | عملية sensitive بدون Policy → APPROVAL_REQUIRED |
| 8 | `test_enforce_audit_recorded` | كل قرار يُسجل في Audit |
| 9 | `test_enforce_rbac_preserved` | RBAC الحالي لا يتChanged |
| 10 | `test_enforce_backward_compatibility` | عمليات غير محكومة تعمل كما قبل |
| 11 | `test_sensitive_operation_without_enforcer_requires_approval` | عملية حساسة بدون enforcer → APPROVAL_REQUIRED |
| 12 | `test_non_sensitive_operation_without_enforcer_allows` | عملية غير حساسة بدون enforcer → ALLOW |

### 8.2 Integration Tests

| # | Test | الهدف |
|---|------|--------|
| 13 | `test_enforcement_in_tool_orchestrator` | Enforcement يعمل في ToolOrchestrator |
| 14 | `test_enforcement_in_agent_orchestrator` | Enforcement يعمل في AgentOrchestrator |
| 15 | `test_block_stops_execution` | BLOCK يوقف التنفيذ فورًا |
| 16 | `test_approval_required_saves_state_to_session_manager` | APPROVAL_REQUIRED يحفظ approval_state في SessionManager |
| 17 | `test_allow_proceeds_to_execution` | ALLOW يسمح بالتنفيذ |
| 18 | `test_graceful_degradation_no_security_bypass` | فشل لا ينتج ALLOW لعمليات حساسة |
| 19 | `test_sensitive_governed_no_policy_requires_approval` | عملية حساسة محكومة بدون Policy → APPROVAL_REQUIRED |
| 20 | `test_non_sensitive_ungoverned_no_policy_allows` | عملية غير محكومة بدون Policy → ALLOW |
| 21 | `test_enforcer_none_sensitive_operation_blocked` | `autonomy_enforcer=None` + عملية حساسة → APPROVAL_REQUIRED |
| 22 | `test_enforcer_none_non_sensitive_operation_allowed` | `autonomy_enforcer=None` + عملية غير حساسة → ALLOW |
| 23 | `test_approval_gate_blocks_execution_when_required` | ApprovalGate يمنع التنفيذ فعلياً عند APPROVAL_REQUIRED |
| 24 | `test_approval_gate_integration_after_autonomy_enforcer` | APPROVAL_REQUIRED من AutonomyEnforcer يمر عبر ApprovalGate قبل التنفيذ |
| 25 | `test_approval_required_halts_execution_no_override` | AutonomyEnforcer = APPROVAL_REQUIRED → لا تنفيذ قبل موافقة صريحة |
| 26 | `test_approval_gate_cannot_override_approval_required` | ApprovalGate لا تستطيع تحويل APPROVAL_REQUIRED إلى تنفيذ تلقائي |
| 27 | `test_approve_updates_approval_state_to_approved` | POST /approvals/{id}/approve يغيّر approval_state["status"] إلى APPROVED |
| 28 | `test_reject_keeps_pending_approval` | POST /approvals/{id}/reject لا يسمح بالتنفيذ |
| 29 | `test_resume_passes_approval_proof_to_orchestrator` | ResumeService يمرر approval_proof في session_context |
| 30 | `test_resume_executes_same_task_after_approval` | Resume يعيد تنفيذ نفس task/step بعد APPROVED |
| 31 | `test_no_new_mission_created_on_resume` | لا يتم إنشاء Mission جديدة عند Resume |
| 32 | `test_no_execution_before_explicit_approval` | لا تنفيذ قبل APPROVED + explicit_approval |
| 33 | `test_tool_orchestrator_does_not_bypass_approval` | ToolOrchestrator لا يتجاوز Approval lifecycle |
| 34 | `test_agent_orchestrator_does_not_bypass_approval` | AgentOrchestrator لا يتجاوز Approval lifecycle |
| 35 | `test_resume_does_not_reenter_approval_loop` | Resume مع approval_proof صالح لا يعيد APPROVAL_REQUIRED |
| 36 | `test_resume_cannot_bypass_block` | Resume مع approval_proof لا يتجاوز BLOCK |
| 37 | `test_resume_with_approval_proof_and_no_policy` | approval_proof صالح يسمح بـ ALLOW حتى بدون Policy |
| 38 | `test_approval_id_equals_mission_id` | `approval_id` في endpoint يطابق `mission_id` في SessionManager |
| 39 | `test_resume_uses_tool_orchestrator_canonical_path` | Resume يمر عبر ToolOrchestrator.execute() ولا يستدعي tool.execute() مباشرة |
| 40 | `test_single_resume_only` | نفس approval لا ينفذ أكثر من مرة |
| 41 | `test_atomic_resume_claim_prevents_concurrent_execution` | Atomic claim يمنع تنفيذ مزدوج عند طلبات متزامنة عبر conditional write |
| 42 | `test_duplicate_approve_does_not_execute_twice` | تكرار `/approve` لا يؤدي إلى تنفيذ مكرر |
| 43 | `test_pending_or_rejected_does_not_execute` | `PENDING` أو `REJECTED` لا يسمحان بالتنفيذ |
| 44 | `test_resume_executes_same_mission_task_step` | Resume ينفذ نفس `mission_id + task_id + step_id` |
| 45 | `test_approval_state_status_is_source_of_truth` | قرار التنفيذ يعتمد على `approval_state["status"]` فقط |
| 46 | `test_resume_audit_is_recorded` | قرار Resume ALLOW يُسجل في agent_audit_logs |
| 47 | `test_enforce_always_returns_decision_object` | `enforce()` يعيد `AutonomyEnforcementDecision` دائماً |
| 48 | `test_audit_before_every_return` | Audit يُسجل قبل كل return في `enforce()` |
| 49 | `test_resume_is_async_safe` | `resume_if_approved()` يستخدم `await` بشكل صحيح |
| 50 | `test_resume_executes_same_step_not_new_plan` | Resume ينفذ نفس step محفوظ، لا يخلق Plan جديد |
| 51 | `test_sensitive_operation_helper_canonical` | `is_sensitive_operation()` يعطي نتيجة صحيحة لـ destructive/high-risk |
| 52 | `test_resume_approval_proof_reaches_autonomy_enforcer` | `approval_proof` يصل من ResumeService إلى AutonomyEnforcer عبر ToolOrchestrator canonical path |
| 53 | `test_resume_valid_approval_proof_does_not_reopen_approval` | ApprovalGate لا تعيد فتح approval lifecycle بعد valid approval_proof |

---

## 9. Acceptance Criteria

| AC | الوصف |
|----|-------|
| AC-001 | لا يمكن تنفيذ action محكوم بـpolicy إذا كانت النتيجة `BLOCK` |
| AC-002 | `APPROVAL_REQUIRED` لا ينفذ مباشرة، بل يمر عبر `ApprovalGate` الحالي ويوقف التنفيذ فعلياً |
| AC-003 | `ALLOW` يسمح بالتنفيذ ضمن حدود السياسة |
| AC-004 | لا يوجد execution path يتجاوز enforcement |
| AC-005 | القرار يحمل trace واضح للـpolicy/context |
| AC-006 | كل قرار enforcement قابل للتدقيق |
| AC-007 | failure/graceful degradation لا يتحول إلى bypass أمني |
| AC-008 | لا يتChanged السلوك غير المحكوم بسياسة جديدة |
| AC-009 | لا يتم إدخال Full Autonomy العامة |
| AC-010 | العمليات الحساسة بدون Policy → `APPROVAL_REQUIRED` (safe default) |
| AC-011 | `autonomy_enforcer=None` + عملية حساسة → `APPROVAL_REQUIRED` (لا bypass) |
| AC-012 | `autonomy_enforcer=None` + عملية غير حساسة → `ALLOW` (backward compatibility) |
| AC-013 | `APPROVAL_REQUIRED` يمر فعلياً عبر `ApprovalGate.check_approval()` ويوقف التنفيذ |
| AC-014 | لا يمكن تنفيذ أداة بعد `APPROVAL_REQUIRED` بدون موافقة صريحة من ApprovalGate |
| AC-015 | `is_sensitive` يُحدد من `is_sensitive_operation()` canonical helper، ويعتمد على `risk` من السياق أو `ApprovalGate.check_approval()` |
| AC-016 | `APPROVAL_REQUIRED` يحفظ approval_state في `SessionManager` كجزء من `agent_sessions.context` |
| AC-017 | بدون explicit approval لا يوجد execution |
| AC-018 | مع explicit approval يتم استئناف نفس المهمة/الخطوة ثم التنفيذ |
| AC-019 | `ApprovalGate` وحدها لا يمكنها تحويل `APPROVAL_REQUIRED` إلى `ALLOW` |
| AC-020 | `AgentOrchestrator` لا يتجاوز Approval lifecycle |
| AC-021 | `ToolOrchestrator` لا يتجاوز Approval lifecycle |
| AC-022 | `POST /approvals/{id}/approve` يحدّث `approval_state["status"]` إلى `APPROVED` |
| AC-023 | `POST /approvals/{id}/reject` يبقي التنفيذ متوقفًا |
| AC-024 | Resume يستخدم نفس `mission_id + task_id + step_id` ولا يخلق Mission جديدة |
| AC-025 | `approval_id` في endpoint يطابق `mission_id` في `SessionManager` |
| AC-026 | `APPROVED + explicit_approval + approval_proof` يمنع إعادة `APPROVAL_REQUIRED` عند Resume |
| AC-027 | `BLOCK` لا يمكن تجاوزه حتى مع `approval_proof` |
| AC-028 | `PENDING_APPROVAL → APPROVED → RESUMING → RESUMED` يمنع التنفيذ المكرر |
| AC-029 | `/approvals/{id}/approve` لا يُحدّث الحالة إذا لم تكن `PENDING_APPROVAL` |
| AC-030 | Resume ينفذ نفس step عبر ToolOrchestrator canonical path |
| AC-031 | `approval_state.status` هو مصدر الحقيقة الوحيد لدورة الموافقة |
| AC-032 | `mission.status` و `approval_state.status` لا يحدث بينهما divergence يسمح بالتنفيذ |
| AC-033 | Atomic claim `APPROVED → RESUMING` يسمح لـ Resume واحد فقط بالتنفيذ عبر conditional write في الـpersistence |
| AC-034 | كل قرار Enforcement، بما فيه Resume ALLOW، يُسجل في `agent_audit_logs` |
| AC-035 | `enforce()` يعيد `AutonomyEnforcementDecision` دائماً، وليس string |
| AC-036 | Audit يُسجل قبل كل return في `enforce()` |
| AC-037 | `ResumeService.resume_if_approved()` هو async-safe |
| AC-038 | Resume ينفذ نفس task/step فعلياً عبر ToolOrchestrator canonical path، ولا يخلق Plan جديد |
| AC-039 | `is_sensitive_operation()` هو canonical helper لحساب الحساسية، ويعتمد على `risk` من السياق أو `ApprovalGate.check_approval()` فقط |
| AC-040 | `approval_proof` صالح حتى بدون Policy: `no_policy + sensitive + valid proof → ALLOW` كـ approved re-entry |
| AC-041 | `approval_proof` لا يتجاوز `BLOCK` في أي حالة |
| AC-042 | `AutonomyEnforcer`, `ToolOrchestrator`, `AgentOrchestrator`, و fallback يستخدمون نفس نتيجة `is_sensitive` |
| AC-043 | عند Resume مع `approval_proof` صالح، `ApprovalGate.check_approval()` تظل defense check فقط ولا تعيد فتح approval lifecycle |
| AC-044 | `ToolOrchestrator` لا يعيد حالة المهمة إلى `PENDING_APPROVAL` بناءً على نتيجة `ApprovalGate` بعد `AutonomyEnforcer` أعاد `ALLOW` مع `approval_proof` صالح |

---

## 10. First Code Slice

### 10.1 `AutonomyEnforcer` Class

```python
# backend/app/agent/autonomy/enforcer.py

class AutonomyEnforcementDecision:
    def __init__(self, decision, operation, policy_ref, reason, evidence, timestamp, trace):
        self.decision = decision  # ALLOW | APPROVAL_REQUIRED | BLOCK
        self.operation = operation
        self.policy_ref = policy_ref
        self.reason = reason
        self.evidence = evidence
        self.timestamp = timestamp
        self.trace = trace

    def to_dict(self):
        return {
            "decision": self.decision,
            "operation": self.operation,
            "policy_ref": self.policy_ref,
            "reason": self.reason,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
            "trace": self.trace,
        }


class AutonomyEnforcer:
    def __init__(self, policy_interpreter, evaluator, audit_recorder, goal_repository, plan_repository, approval_gate=None):
        self.policy_interpreter = policy_interpreter
        self.evaluator = evaluator
        self.audit_recorder = audit_recorder
        self.goal_repository = goal_repository
        self.plan_repository = plan_repository
        self.approval_gate = approval_gate

    def enforce(self, operation, context, risk=None, is_sensitive=None):
        """Evaluate and return binding autonomy decision.

        Flow:
        1. Resolve policy from context (goal_id, plan_id)
        2. Determine base decision:
           - No policy + sensitive → APPROVAL_REQUIRED
           - No policy + non-sensitive → ALLOW
           - Policy exists → evaluate via AutonomyEvaluator → map to decision
        3. If base decision is BLOCK → audit and return BLOCK (cannot be bypassed)
        4. If base decision is APPROVAL_REQUIRED and valid approval_proof exists → ALLOW
        5. Record decision in audit
        6. Return binding decision
        """
        goal_id = context.get("goal_id")
        plan_id = context.get("plan_id")

        # 1. Resolve policy
        policy = self._resolve_policy(goal_id, plan_id)
        
        # 2. Determine if operation is sensitive
        if is_sensitive is None:
            is_sensitive = context.get("is_sensitive", False)
        
        # 3. Determine base decision
        if not policy:
            if is_sensitive:
                base_decision = "APPROVAL_REQUIRED"
                base_signal = AutonomyEvaluationSignal(
                    operation=operation,
                    decision="approval_required",
                    reason="no_policy_sensitive_operation",
                    evidence={"fallback": "no_policy_for_sensitive_operation"},
                )
            else:
                base_decision = "ALLOW"
                base_signal = AutonomyEvaluationSignal(
                    operation=operation,
                    decision="allowed",
                    reason="no_policy",
                    evidence={"fallback": "no_policy"},
                    proposed_autonomy_level=context.get("autonomy_level", "manual"),
                )
        else:
            try:
                signal = self.evaluator.evaluate(
                    operation=operation,
                    policy=policy,
                    context=context,
                    execution_history=context.get("execution_history"),
                    memory_provider=context.get("memory_provider"),
                )
            except Exception as exc:
                signal = AutonomyEvaluationSignal(
                    operation=operation,
                    decision="approval_required",
                    reason=f"evaluation_failed: {exc}",
                    evidence={"error": str(exc)},
                )
            base_decision = self._map_signal_to_decision(signal, risk, is_sensitive)
            base_signal = signal

        # 4. BLOCK cannot be bypassed by approval_proof
        if base_decision == "BLOCK":
            block_decision = AutonomyEnforcementDecision(
                decision="BLOCK",
                operation=operation,
                policy_ref=context.get("policy_ref", {}),
                reason=base_signal.reason,
                evidence=base_signal.evidence,
                timestamp=datetime.now(timezone.utc).isoformat(),
                trace={"step": "policy_evaluation", "result": "blocked"},
            )
            self._record_audit(operation, context, block_decision, base_signal)
            return block_decision

        # 5. Check approval_proof for APPROVAL_REQUIRED
        if base_decision == "APPROVAL_REQUIRED":
            approval_proof = context.get("approval_proof")
            if approval_proof:
                mission_id = context.get("mission_id")
                task_id = context.get("task_id")
                step_id = context.get("step_id")
                if (
                    approval_proof.get("status") == "APPROVED"
                    and approval_proof.get("approval_id") == mission_id
                    and approval_proof.get("task_id") == task_id
                    and approval_proof.get("step_id") == step_id
                    and approval_proof.get("explicit_approval")
                ):
                    base_decision = "ALLOW"
                    base_signal = AutonomyEvaluationSignal(
                        operation=operation,
                        decision="allowed",
                        reason="resumed_after_explicit_approval",
                        evidence={"approval_proof": approval_proof},
                        proposed_autonomy_level=context.get("autonomy_level", "manual"),
                    )

        # 6. Build final decision object
        final_decision = AutonomyEnforcementDecision(
            decision=base_decision,
            operation=operation,
            policy_ref=context.get("policy_ref", {}),
            reason=base_signal.reason,
            evidence=base_signal.evidence,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trace={"step": "policy_evaluation", "result": base_decision.lower()},
        )

        # 7. Audit and return
        self._record_audit(operation, context, final_decision, base_signal)

        return final_decision

    def _map_signal_to_decision(self, signal, risk, is_sensitive):
        decision = signal.decision
        
        if decision == "blocked":
            return "BLOCK"
        elif decision == "approval_required":
            return "APPROVAL_REQUIRED"
        elif decision == "allowed":
            # If operation is sensitive and no explicit policy, require approval
            if is_sensitive and not signal.evidence.get("policy_explicitly_allows"):
                return "APPROVAL_REQUIRED"
            if risk == "high":
                return "APPROVAL_REQUIRED"
            return "ALLOW"
        
        # Default safe fallback
        return "APPROVAL_REQUIRED"

    def _resolve_policy(self, goal_id, plan_id):
        if not goal_id or not self.goal_repository:
            return None
        goal = self.goal_repository.get(goal_id)
        if not goal or not plan_id or not self.plan_repository:
            return None
        plan = self.plan_repository.get(plan_id)
        if not plan:
            return None
        return self.policy_interpreter.build_policy(goal, plan)

    def _record_audit(self, operation, context, decision, signal):
        self.audit_recorder.record_agent_action(
            session_id=context.get("session_id", ""),
            agent_id=context.get("agent_id", "system"),
            action="autonomy_enforcement",
            input_data={
                "operation": operation,
                "policy_ref": {
                    "goal_id": context.get("goal_id"),
                    "plan_id": context.get("plan_id"),
                },
                "context_summary": {
                    "chosen_path": context.get("chosen_path"),
                    "user_id": context.get("user_id"),
                    "is_sensitive": context.get("is_sensitive"),
                },
                "risk": context.get("risk"),
            },
            output_data={
                "decision": decision.decision,
                "reason": decision.reason,
                "evidence": decision.evidence,
                "proposed_autonomy_level": signal.proposed_autonomy_level if hasattr(signal, 'proposed_autonomy_level') else None,
            },
        )
```

### 10.2 Integration in `ToolOrchestrator`

```python
# في __init__:
def __init__(self, ..., autonomy_enforcer=None, session_manager=None, approval_gate=None):
    self.autonomy_enforcer = autonomy_enforcer
    self.session_manager = session_manager
    # maintain current behavior: approval_gate or ApprovalGate()
    self.approval_gate = approval_gate or ApprovalGate()

# في execute() قبل approval_gate.check_approval():
# استخدم canonical helper
from app.agent.autonomy.helpers import is_sensitive_operation

# Risk comes from existing execution context/policy/task metadata.
# If no explicit risk is available in context, pass None.
risk = context.get("risk")

is_sensitive = is_sensitive_operation(
    approval_gate=self.approval_gate,
    tool_name=tool_name,
    parameters=parameters,
    risk=risk,
)

if self.autonomy_enforcer:
    operation = tool_name
    context_for_enforcement = {
        "session_id": context.get("session_id"),
        "agent_id": getattr(self, 'agent_id', 'tool-orchestrator'),
        "goal_id": context.get("goal_id"),
        "plan_id": context.get("plan_id"),
        "chosen_path": context.get("chosen_path", ""),
        "intent": context.get("intent", ""),
        "user_id": context.get("user_id"),
        "execution_history": context.get("execution_history"),
        "memory_provider": context.get("memory_provider"),
        "risk": risk,
        "is_sensitive": is_sensitive,
        "mission_id": mission_id,
        "task_id": task_id,
        "step_id": task_id,
        "approval_proof": context.get("approval_proof"),
    }

    enforcement_decision = self.autonomy_enforcer.enforce(
        operation=operation,
        context=context_for_enforcement,
        risk=risk,
    )

    if enforcement_decision.decision == "BLOCK":
        # إيقاف فوري للـmission/execution path + Audit + خطأ
        task_dict["status"] = TaskStatus.FAILED.value
        task_dict["result"] = {"error": f"Blocked by autonomy policy: {enforcement_decision.reason}"}
        execution_trace.append(
            ExecutionStep(
                task_id=task_id,
                tool_name=tool_name,
                start_time=datetime.now(timezone.utc),
                finish_time=datetime.now(timezone.utc),
                execution_status="blocked",
                result=ToolResult(status="blocked", error=f"Blocked by autonomy policy: {enforcement_decision.reason}"),
            ).to_dict()
        )
        failed_task_id = task_id
        mission_status = MissionStatus.FAILED.value
        if self.monitoring_service:
            self.monitoring_service.record_task_execution(
                mission_id=mission_id or "",
                task_id=task_id,
                tool_name=tool_name,
                execution_status="blocked",
                execution_time_ms=0.0,
                retry_count=0,
                error=f"Blocked by autonomy policy: {enforcement_decision.reason}",
            )
        break

    elif enforcement_decision.decision == "APPROVAL_REQUIRED":
        # إنشاء approval_state في SessionManager
        approval_state = {
            "mission_id": mission_id or "",
            "task_id": task_id,
            "step_id": task_id,
            "operation": tool_name,
            "status": "PENDING_APPROVAL",
            "autonomy_decision": enforcement_decision.to_dict(),
            "approval_gate_result": {},
            "explicit_approval": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # استدعاء ApprovalGate لتقييم الحاجة فقط
        if self.approval_gate:
            requires_human_approval, approval_status = self.approval_gate.check_approval(
                chosen_path=context.get("chosen_path", ""),
                intent=context.get("intent", ""),
                parameters=parameters,
            )
            approval_state["approval_gate_result"] = {
                "requires_approval": requires_human_approval,
                "status": approval_status,
            }

        # حفظ approval_state في SessionManager
        if self.session_manager and mission_id:
            self.session_manager.update_mission_status(
                session_id=context.get("session_id"),
                mission_id=mission_id,
                status="pending_approval",
                result={"approval_state": approval_state},
            )

        # إيقاف المهمة بالكامل
        task_dict["status"] = TaskStatus.PENDING.value
        task_dict["result"] = {
            "approval_required": True,
            "approval_state": approval_state,
        }
        execution_trace.append(
            ExecutionStep(
                task_id=task_id,
                tool_name=tool_name,
                start_time=datetime.now(timezone.utc),
                finish_time=datetime.now(timezone.utc),
                execution_status="pending_approval",
                result=ToolResult(status="pending_approval", error="Approval required by autonomy policy"),
            ).to_dict()
        )
        failed_task_id = task_id
        mission_status = MissionStatus.PENDING_APPROVAL.value
        if self.monitoring_service:
            self.monitoring_service.record_task_execution(
                mission_id=mission_id or "",
                task_id=task_id,
                tool_name=tool_name,
                execution_status="pending_approval",
                execution_time_ms=0.0,
                retry_count=0,
                error="Approval required by autonomy policy",
            )
        break

    # ALLOW → استمر إلى approval_gate.check_approval() الحالي
else:
    # fallback عندما لا يوجد autonomy_enforcer
    if is_sensitive:
        # إنشاء approval_state في SessionManager
        approval_state = {
            "mission_id": mission_id or "",
            "task_id": task_id,
            "step_id": task_id,
            "operation": tool_name,
            "status": "PENDING_APPROVAL",
            "autonomy_decision": {"decision": "APPROVAL_REQUIRED", "reason": "sensitive_operation_without_enforcer"},
            "approval_gate_result": {},
            "explicit_approval": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if self.approval_gate:
            requires_human_approval, approval_status = self.approval_gate.check_approval(
                chosen_path=context.get("chosen_path", ""),
                intent=context.get("intent", ""),
                parameters=parameters,
            )
            approval_state["approval_gate_result"] = {
                "requires_approval": requires_human_approval,
                "status": approval_status,
            }

        if self.session_manager and mission_id:
            self.session_manager.update_mission_status(
                session_id=context.get("session_id"),
                mission_id=mission_id,
                status="pending_approval",
                result={"approval_state": approval_state},
            )

        task_dict["status"] = TaskStatus.PENDING.value
        task_dict["result"] = {
            "approval_required": True,
            "reason": "sensitive_operation_without_enforcer",
            "approval_state": approval_state,
        }
        execution_trace.append(
            ExecutionStep(
                task_id=task_id,
                tool_name=tool_name,
                start_time=datetime.now(timezone.utc),
                finish_time=datetime.now(timezone.utc),
                execution_status="pending_approval",
                result=ToolResult(status="pending_approval", error="Sensitive operation requires approval (enforcer unavailable)"),
            ).to_dict()
        )
        failed_task_id = task_id
        mission_status = MissionStatus.PENDING_APPROVAL.value
        if self.monitoring_service:
            self.monitoring_service.record_task_execution(
                mission_id=mission_id or "",
                task_id=task_id,
                tool_name=tool_name,
                execution_status="pending_approval",
                execution_time_ms=0.0,
                retry_count=0,
                error="Sensitive operation requires approval (enforcer unavailable)",
            )
        break
    # non-sensitive بدون enforcer = ALLOW (backward compatibility)
```

### 10.3 Integration in `AgentOrchestrator`

```python
# في __init__:
def __init__(self, ..., autonomy_enforcer=None, session_manager=None, approval_gate=None):
    self.autonomy_enforcer = autonomy_enforcer
    self.session_manager = session_manager
    # maintain current behavior: approval_gate or ApprovalGate()
    self.approval_gate = approval_gate or ApprovalGate()

# في execute() قبل tool_instance.execute():
# استخدم canonical helper
from app.agent.autonomy.helpers import is_sensitive_operation

step_context = {
    "session_id": session_id,
    "agent_id": self.agent_id,
    "goal_id": context.get("goal_id"),
    "plan_id": context.get("plan_id"),
    "chosen_path": "",
    "intent": intent,
    "user_id": context.get("user_id"),
    "execution_history": context.get("execution_history"),
    "memory_provider": context.get("memory_provider"),
    "mission_id": context.get("mission_id"),
    "task_id": step.step_id,
    "step_id": step.step_id,
}

# Risk comes from existing step/context metadata.
# If no explicit risk is available, pass None.
risk = context.get("risk")

# تحديد ما إذا كانت الخطوة حساسة
is_sensitive = is_sensitive_operation(
    approval_gate=self.approval_gate,
    tool_name=step.tool_name,
    parameters={**parameters, **step.parameters},
    risk=risk,
)

if self.autonomy_enforcer:
    step_context["risk"] = risk
    step_context["is_sensitive"] = is_sensitive
    enforcement_decision = self.autonomy_enforcer.enforce(
        operation=step.tool_name,
        context=step_context,
        risk=risk,
    )

    if enforcement_decision.decision == "BLOCK":
        # تسجيل كخطأ وإيقاف المهمة بالكامل
        self.audit_recorder.record_agent_action(
            session_id=session_id,
            agent_id=self.agent_id,
            action=f"tool_blocked:{step.tool_name}",
            input_data={"intent": intent, "step": step.step_id},
            output_data={"error": f"Blocked by autonomy policy: {enforcement_decision.reason}"},
            duration_ms=0,
        )
        results.append({
            "step_id": step.step_id,
            "tool": step.tool_name,
            "result": {"status": "blocked", "error": f"Blocked by autonomy policy: {enforcement_decision.reason}"},
            "duration_ms": 0,
        })
        break

    elif enforcement_decision.decision == "APPROVAL_REQUIRED":
        # إنشاء approval_state في SessionManager
        approval_state = {
            "mission_id": context.get("mission_id", ""),
            "task_id": step.step_id,
            "step_id": step.step_id,
            "operation": step.tool_name,
            "status": "PENDING_APPROVAL",
            "autonomy_decision": enforcement_decision.to_dict(),
            "approval_gate_result": {},
            "explicit_approval": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # استدعاء ApprovalGate لتقييم الحاجة فقط
        if getattr(self, 'approval_gate', None):
            requires_human_approval, approval_status = self.approval_gate.check_approval(
                chosen_path=step_context.get("chosen_path", ""),
                intent=step_context.get("intent", ""),
                parameters={**parameters, **step.parameters},
            )
            approval_state["approval_gate_result"] = {
                "requires_approval": requires_human_approval,
                "status": approval_status,
            }

        # حفظ approval_state في SessionManager
        if self.session_manager and context.get("mission_id"):
            self.session_manager.update_mission_status(
                session_id=session_id,
                mission_id=context.get("mission_id"),
                status="pending_approval",
                result={"approval_state": approval_state},
            )

        # إيقاف المهمة بالكامل
        self.audit_recorder.record_agent_action(
            session_id=session_id,
            agent_id=self.agent_id,
            action=f"tool_approval_required:{step.tool_name}",
            input_data={"intent": intent, "step": step.step_id},
            output_data={
                "approval_required": True,
                "approval_state": approval_state,
            },
            duration_ms=0,
        )
        results.append({
            "step_id": step.step_id,
            "tool": step.tool_name,
            "result": {
                "status": "pending_approval",
                "approval_required": True,
                "approval_state": approval_state,
            },
            "duration_ms": 0,
        })
        break

else:
    # fallback بدون enforcer
    if is_sensitive:
        # إنشاء approval_state في SessionManager
        approval_state = {
            "mission_id": context.get("mission_id", ""),
            "task_id": step.step_id,
            "step_id": step.step_id,
            "operation": step.tool_name,
            "status": "PENDING_APPROVAL",
            "autonomy_decision": {"decision": "APPROVAL_REQUIRED", "reason": "sensitive_operation_without_enforcer"},
            "approval_gate_result": {},
            "explicit_approval": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if getattr(self, 'approval_gate', None):
            requires_human_approval, approval_status = self.approval_gate.check_approval(
                chosen_path=step_context.get("chosen_path", ""),
                intent=step_context.get("intent", ""),
                parameters={**parameters, **step.parameters},
            )
            approval_state["approval_gate_result"] = {
                "requires_approval": requires_human_approval,
                "status": approval_status,
            }

        if self.session_manager and context.get("mission_id"):
            self.session_manager.update_mission_status(
                session_id=session_id,
                mission_id=context.get("mission_id"),
                status="pending_approval",
                result={"approval_state": approval_state},
            )

        self.audit_recorder.record_agent_action(
            session_id=session_id,
            agent_id=self.agent_id,
            action=f"tool_approval_required:{step.tool_name}",
            input_data={"intent": intent, "step": step.step_id},
            output_data={
                "reason": "sensitive_operation_without_enforcer",
                "approval_required": True,
                "approval_state": approval_state,
            },
            duration_ms=0,
        )
        results.append({
            "step_id": step.step_id,
            "tool": step.tool_name,
            "result": {
                "status": "pending_approval",
                "approval_required": True,
                "reason": "sensitive_operation_without_enforcer",
                "approval_state": approval_state,
            },
            "duration_ms": 0,
        })
        break
    # non-sensitive بدون enforcer = ALLOW (backward compatibility)
```

### 10.4 Approval Lifecycle Integration

**الهدف:** ربط `APPROVAL_REQUIRED` بالآلية الموجودة فعليًا لتحقيق موافقة خارجية فعلية ثم Resume لنفس المهمة/الخطوة.

**المكونات الموجودة التي سيتم استخدامها:**

1. **`SessionManager`** (`backend/app/agent/session/manager.py`):
   - `update_mission_status(session_id, mission_id, status, result)` ← لحفظ `approval_state` داخل `agent_sessions.context`
   - `get_pending_approvals(user_id)` ← لتحديد Missions المنتظرة موافقة
   - `get_mission_by_id(session_id, mission_id)` ← لاسترجاع حالة المهمة

2. **Approval APIs** (`backend/app/routers/digital_export_manager.py`):
   - `GET /approvals` ← يستدعي `SessionManager.get_pending_approvals()`
   - `POST /approvals/{id}/approve` ← **يجب تعديله إلزامياً** لتحقيق Approval Lifecycle
   - `POST /approvals/{id}/reject` ← **يجب تعديله إلزامياً** لتحقيق Approval Lifecycle

3. **`MonitoringService` / `WorkflowOrchestrator`** ← تتبع للحالات، ليس نظام Approval جديد.

**تنبيه هام: الكود الحالي للـendpoints غير مكتمل.**

- `POST /approvals/{id}/approve` الحالي في `backend/app/routers/digital_export_manager.py` يسجل Audit فقط ولا يغيّر `approval_state` ولا يحدّث `mission.status` ولا يشغّل ResumeService.
- `POST /approvals/{id}/reject` الحالي في نفس الملف يسجل Audit فقط ولا يغيّر `approval_state` ولا يحدّث `mission.status`.

لذلك، **تعديل هذين الـendpointين إلزامي** ضمن Implementation Work لتحقيق Approval Lifecycle كاملاً.

**الحد الأدنى للتعديلات المطلوبة:**

- **لا redesign لـ `SessionManager` أو Approval APIs.**
- **أضف `ResumeService` واحد جديد فقط** إذا لم يكن ممكنًا استئناف المهمة مباشرة من المكونات الحالية.
- **عدّل إلزامياً:**
  - `POST /approvals/{id}/approve` ← validation → update `approval_state["status"]` → persist → call `ResumeService`
  - `POST /approvals/{id}/reject` ← validation → update `approval_state["status"]` → persist → NO execution
- `ResumeService` مسؤول عن:
  1. تحميل `approval_state` من `SessionManager`.
  2. التحقق من `approval_state["status"] == "APPROVED"` ووجود `explicit_approval`.
  3. atomic claim `APPROVED → RESUMING`
  4. استدعاء `ToolOrchestrator.execute()` لنفس `mission_id + task_id + step_id` مع `approval_proof`.

**Resume Execution Contract:**

```text
ResumeService.resume_if_approved()
    ↓
build execution_plan with same task/step identity
    ↓
await ToolOrchestrator.execute(execution_plan, session_context={"session_id": ..., "approval_proof": ...})
    ↓
ToolOrchestrator canonical path:
    AutonomyEnforcer.enforce()  [approval_proof may downgrade APPROVAL_REQUIRED → ALLOW]
    ApprovalGate.check_approval()  [defense only, cannot reopen approval lifecycle]
    tool.execute()
```

**ApprovalGate Behavior After Resume:**

- `ApprovalGate.check_approval()` ليست approval record. هي فحص حساسية/سياسة فقط.
- الموافقة الصريحة محفوظة داخل `approval_state["explicit_approval"]` فقط.
- إذا كان `approval_proof` صالحًا لنفس `approval_id + task_id + step_id`، فإن AutonomyEnforcer ينتج `ALLOW`.
- في هذه الحالة، ApprovalGate تظل كدفاع إضافي ولا يمكنها:
  - إعادة فتح نفس approval lifecycle
  - تحويل `ALLOW` إلى `APPROVAL_REQUIRED` إذا كان القرار ناتجًا عن valid `approval_proof`
- هذا is a legitimate re-entry state لنفس approval، وليس bypass.

**ممنوع:**

- `tool.execute()` مباشرة من Resume.
- `ResumeService → AgentOrchestrator.execute()` مباشرة.
- أي bypass لـ `AutonomyEnforcer` أو `ApprovalGate`.
- أي execution path بديل.

**العقد:**

```
AutonomyEnforcer → APPROVAL_REQUIRED
    ↓
Orchestrator ينشئ approval_state في SessionManager
    ↓
approval_state.status = PENDING_APPROVAL
mission.status = pending_approval (projection)
    ↓
Existing Approval API (/approvals/{id}/approve)
    ↓
Explicit Approval يُسجل + approval_state.status → APPROVED
    ↓
ResumeService يتحقق من approval_state
    ↓
نفس المهمة/الخطوة تنفذ عبر ToolOrchestrator canonical path
```

**Approval API Mandatory Changes:**

```python
# POST /approvals/{approval_id}/approve (إلزامي):
# 1. استرجاع session_id المرتبط بـ approval_id (= mission_id)
# 2. تحميل approval_state من SessionManager
# 3. التحقق أن approval_state["status"] الحالية = PENDING_APPROVAL فقط
#    (لا يقبل APPROVED أو RESUMING أو RESUMED أو REJECTED)
# 4. تحديث approval_state["status"] = "APPROVED"
# 5. تعبئة approval_state["explicit_approval"] = {"approved_by": ..., "decided_at": ..., "approval_id": ...}
# 6. حفظ عبر SessionManager.update_mission_status(session_id, mission_id, status="approved", result={"approval_state": approval_state})
#    - ملاحظة: update_mission_status يجب أن يدعم keyword args صحيحة.
# 7. استدعاء ResumeService.resume_if_approved(session_id, mission_id, task_id, step_id)
```

```python
# POST /approvals/{approval_id}/reject (إلزامي):
# 1. استرجاع session_id المرتبط بـ approval_id (= mission_id)
# 2. تحميل approval_state من SessionManager
# 3. التحقق أن approval_state["status"] الحالية = PENDING_APPROVAL فقط.
# 4. تحديث approval_state["status"] = "REJECTED"
# 5. تعبئة approval_state["explicit_approval"] = {"rejected_by": ..., "decided_at": ..., "approval_id": ..., "decision": "rejected"}
# 6. حفظ عبر SessionManager.update_mission_status(session_id, mission_id, status="rejected", result={"approval_state": approval_state})
# 7. لا استدعاء لـ ResumeService
```

**Resume Re-entry / Enforcement Loop Prevention:**

- عند استدعاء `ResumeService.resume_if_approved()`، يبني `approval_proof` ويُمرره للتنفيذ:
  ```python
  approval_proof = {
      "approval_id": mission_id,
      "task_id": task_id,
      "step_id": step_id,
      "status": "APPROVED",
      "explicit_approval": approval_state["explicit_approval"],
  }
  ```
- `ResumeService` يختار مسار التنفيذ:
  - `await self.tool_orchestrator.execute(execution_plan, session_context={"session_id": session_id, "approval_proof": approval_proof})`
- `AutonomyEnforcer.enforce()` يتحقق من `context.get("approval_proof")` فقط بعد تقييم السياسة وتحديد القرار:
  - أولاً: تقييم السياسة → قد ينتج `BLOCK` أو `APPROVAL_REQUIRED` أو `ALLOW`.
  - إذا كان القرار `BLOCK` → يرجع `BLOCK` فوراً ولا يتحقق من `approval_proof`.
  - إذا كان القرار `APPROVAL_REQUIRED` → يتحقق من `approval_proof`، وإذا كان صالحاً لنفس `approval_id == mission_id` + `task_id` + `step_id` → يسجل Audit ثم يرجع `ALLOW`.
  - إذا كان القرار `ALLOW` → يسجل Audit ثم يرجع `ALLOW`.
- هذا التجاوز صالح فقط لنفس `approval_id == mission_id` + `task_id` + `step_id`.
- `BLOCK` لا يمكن تجاوزه حتى مع `approval_proof`.
- **كل قرار enforcement، بما فيه Resume ALLOW، يُسجل في `agent_audit_logs`.`

```python
# POST /approvals/{approval_id}/approve (معدّل minimally):
# 1. تحميل approval_state من SessionManager عبر get_pending_approvals() + get_mission_by_id()
# 2. التحقق أن الحالة الحالية = PENDING_APPROVAL
# 3. تحديث approval_state["status"] = "APPROVED"
# 4. تعبئة approval_state["explicit_approval"] = {"approved_by": ..., "decided_at": ..., "approval_id": ...}
# 5. حفظ عبر SessionManager.update_mission_status(session_id, mission_id, status="approved", result={"approval_state": approval_state})
# 6. استدعاء ResumeService.resume_if_approved(session_id, mission_id, task_id, step_id)
```

```python
# POST /approvals/{approval_id}/reject (معدّل minimally):
# 1. تحميل approval_state من SessionManager
# 2. التحقق أن الحالة الحالية = PENDING_APPROVAL
# 3. تحديث approval_state["status"] = "REJECTED"
# 4. تعبئة approval_state["explicit_approval"] = {"rejected_by": ..., "decided_at": ..., "approval_id": ..., "decision": "rejected"}
# 5. حفظ عبر SessionManager.update_mission_status(session_id, mission_id, status="rejected", result={"approval_state": approval_state})
# 6. لا استدعاء لـ ResumeService
```

```python
# Resume Service (جديد - أقل مكوّن جديد):
# الملف المقترح: backend/app/agent/approval/resume.py

class ResumeService:
    def __init__(self, session_manager, tool_orchestrator):
        self.session_manager = session_manager
        self.tool_orchestrator = tool_orchestrator

    async def resume_if_approved(self, session_id, mission_id, task_id, step_id):
        """Resume execution for a specific task/step within a mission after explicit approval.

        Args:
            session_id: Session identifier
            mission_id: Mission identifier
            task_id: Task identifier within the mission
            step_id: Step identifier within the task

        Returns:
            Dict with execution result, or None if resume is not allowed
        """
        # 1. تحميل approval_state من SessionManager
        mission = self.session_manager.get_mission_by_id(session_id, mission_id)
        if not mission:
            return None

        approval_state = mission.get("result", {}).get("approval_state", {})
        if not approval_state:
            return None

        # 2. شروط الاستئناف - approval_state.status هو مصدر الحقيقة الوحيد
        if approval_state.get("status") != "APPROVED":
            return None

        if not approval_state.get("explicit_approval"):
            return None

        # 3. Atomic claim: تحويل APPROVED → RESUMING لمنع تنفيذ مزدوج
        claim_succeeded = self._atomic_claim_resume(session_id, mission_id, approval_state)
        if not claim_succeeded:
            return None

        # 4. بناء approval_proof لمنع إعادة APPROVAL_REQUIRED
        approval_proof = {
            "approval_id": mission_id,
            "task_id": task_id,
            "step_id": step_id,
            "status": "APPROVED",
            "explicit_approval": approval_state["explicit_approval"],
        }

        # 5. استدعاء تنفيذ نفس المهمة/الخطوة مع approval_proof
        # يتم تنفيذ نفس task/step مباشرة عبر ToolOrchestrator canonical path
        # لا يتم إنشاء Mission جديدة
        execution_plan = {
            "mission_id": mission_id,
            "task_id": task_id,
            "step_id": step_id,
            "tasks": [
                {
                    "task_id": task_id,
                    "tool_name": approval_state["operation"],
                    "parameters": approval_state.get("parameters", {}),
                }
            ],
        }

        try:
            session_context = {
                "session_id": session_id,
                "approval_proof": approval_proof,
                "goal_id": mission.get("goal_id"),
                "plan_id": mission.get("plan_id"),
                "risk": mission.get("risk"),
                "chosen_path": mission.get("chosen_path"),
                "intent": mission.get("intent"),
                "mission_id": mission_id,
                "task_id": task_id,
                "step_id": step_id,
            }
            result = await self.tool_orchestrator.execute(execution_plan, session_context=session_context)

            # RESUMED فقط عند نجاح التنفيذ
            if result and result.get("mission_status") == "completed":
                self.session_manager.update_mission_status(
                    session_id=session_id,
                    mission_id=mission_id,
                    status="resumed",
                    result={"approval_state": {**approval_state, "status": "RESUMED"}},
                )
            return result
        except Exception:
            # عند الفشل: تبقى الحالة RESUMING أو تنتقل إلى حالة failure
            # لا يُعتبر التنفيذ ناجحًا ولا يحدث duplicate execution
            raise

    def _atomic_claim_resume(self, session_id, mission_id, approval_state):
        """Atomically claim resume by transitioning approval_state from APPROVED to RESUMING.

        Uses approval_state.status as source of truth.
        SessionManager must support conditional atomic update:
        update_mission_status_if(
            session_id, mission_id,
            expected_status="APPROVED",
            new_status="RESUMING",
            result={"approval_state": approval_state}
        )

        Returns True if claim succeeded, False if already claimed/executed/rejected.
        """
        # Atomic transition: approval_state.status APPROVED → RESUMING
        # This is conditional on approval_state["status"] == "APPROVED"
        # SessionManager.update_mission_status_if should check approval_state["status"] inside result
        return self.session_manager.update_mission_status_if(
            session_id=session_id,
            mission_id=mission_id,
            expected_status="APPROVED",
            new_status="RESUMING",
            result={"approval_state": approval_state},
        )
```

### 10.5 Approval API Integration

**Contract محدث:**

- `approval_id == mission_id` في الكود الحالي.
- `approval_state.status` هو مصدر الحقيقة الوحيد لدورة الموافقة.
- `mission.status` يُحدّث فقط كتعبير عن حالة المهمة، ولا يُستخدم لاتخاذ قرارات التنفيذ.
- `/approvals/{id}/approve` و `/reject` يجب أن يحتفظا بـ `session_id` المرتبط بـ `approval_id` ويحدّثا `approval_state` فقط.

```python
# POST /approvals/{approval_id}/approve (معدّل minimally):
# 1. تحميل approval_state من SessionManager عبر get_pending_approvals() + get_mission_by_id()
#    مع استرجاع session_id المرتبط.
# 2. التحقق أن approval_state["status"] الحالية = PENDING_APPROVAL فقط
#    (لا يقبل APPROVED أو RESUMING أو RESUMED أو REJECTED).
# 3. تحديث approval_state["status"] = "APPROVED"
# 4. تعبئة approval_state["explicit_approval"] = {"approved_by": ..., "decided_at": ..., "approval_id": ...}
# 5. حفظ عبر SessionManager.update_mission_status(session_id, mission_id, status="approved", result={"approval_state": approval_state})
#    - ملاحظة: update_mission_status يجب أن يدعم keyword args صحيحة.
# 6. استدعاء ResumeService.resume_if_approved(session_id, mission_id, task_id, step_id)
```

```python
# POST /approvals/{approval_id}/reject (معدّل minimally):
# 1. تحميل approval_state من SessionManager مع session_id.
# 2. التحقق أن approval_state["status"] الحالية = PENDING_APPROVAL فقط.
# 3. تحديث approval_state["status"] = "REJECTED"
# 4. تعبئة approval_state["explicit_approval"] = {"rejected_by": ..., "decided_at": ..., "approval_id": ..., "decision": "rejected"}
# 5. حفظ عبر SessionManager.update_mission_status(session_id, mission_id, status="rejected", result={"approval_state": approval_state})
# 6. لا استدعاء لـ ResumeService
```

### 10.6 SessionManager Atomic Update Contract

**المشكلة:** `update_mission_status()` الحالي يقرأ ثم يتحقق ثم يحدث، وهو non-atomic. طلبان متزامنان لـ Resume يمكن أن يرى كلاهما `approval_state["status"] == "APPROVED"` ويستمر كلاهما إلى التنفيذ.

**الحل المطلوب (أقل تعديل):** أضف `update_mission_status_if()` إلى `SessionManager` الذي ينفذ conditional atomic update على `approval_state["status"]` داخل `agent_sessions.context`.

```python
def update_mission_status_if(
    self,
    session_id: str,
    mission_id: str,
    expected_status: str,
    new_status: str,
    result: Optional[Dict[str, Any]] = None,
) -> bool:
    """Atomically update mission/approval state only if current status matches expected_status.
    
    Returns True if update succeeded, False otherwise.
    """
```

**Atomic Contract — storage-level mechanism:**

```text
BEGIN transaction / serialized persistence operation
    ↓
SELECT current session context FOR UPDATE
    ↓
locate exact mission inside the loaded context
    ↓
verify current state:
    approval_state["status"] == expected_status
    mission["status"] == projection_of(expected_status)
    ↓
IF verify fails:
    ROLLBACK
    RETURN False
    ↓
update both atomically inside same transaction:
    approval_state["status"] = new_status
    mission["status"] = projection_of(new_status)
    mission["result"] = result  # includes updated approval_state
    ↓
COMMIT
    ↓
RETURN True
```

**الشرط الأساسي:**

- condition检查和state transition必须发生在同一个transaction/serialized persistence operation内。
- 不允许将读取、验证、修改、保存分为独立步骤。
- Implementation MUST确保在并发请求时只有一个请求能成功claim。
- 不使用 `read → check → modify → save` 作为独立步骤。

**لماذا هذا يمنع concurrent execution:**

- 两个并发请求：第一个成功获得True并执行，第二个获得False且不执行。
- 第二个请求永远不会执行。

**الاستخدام في ResumeService:**

```python
claim_succeeded = self.session_manager.update_mission_status_if(
    session_id=session_id,
    mission_id=mission_id,
    expected_status="APPROVED",
    new_status="RESUMING",
    result={"approval_state": approval_state},
)
if not claim_succeeded:
    return None
```

### 10.7 State Consistency Contract

**Source of Truth:** `approval_state["status"]` inside `agent_sessions.context`.

**Projection:** `mission["status"]` mirrors `approval_state["status"]` for convenience only. No execution decision may rely on `mission["status"]` alone.

**Allowed State Transitions:**

```text
PENDING_APPROVAL → APPROVED        (explicit approve)
PENDING_APPROVAL → REJECTED        (explicit reject)
APPROVED → RESUMING                (atomic claim by ResumeService)
RESUMING → RESUMED                 (successful execution completion)
RESUMING → FAILED                  (execution failure)
```

**Forbidden Transitions (must be rejected by implementation):**

```text
PENDING_APPROVAL → RESUMING
REJECTED → APPROVED
RESUMED → RESUMING
APPROVED → APPROVED (duplicate approve)
```

**Atomic Claim Contract:**

```text
update_mission_status_if(
    session_id=...,
    mission_id=...,
    expected_status="APPROVED",
    new_status="RESUMING",
    result={"approval_state": approval_state}
)
```

Implementation MUST perform a single conditional write at the persistence layer:
- Read current mission context from storage.
- If `approval_state["status"] == expected_status`, atomically update both `approval_state["status"]` and `mission["status"]`.
- If check fails, return `False` without any write.

This single call must atomically update both:
- `approval_state["status"]` from `"APPROVED"` to `"RESUMING"`
- `mission["status"]` from `"approved"` to `"resuming"`

**Resume Success/Failure Contract:**

```text
APPROVED
→ RESUMING (atomic claim)
→ execution
→ RESUMED (only if execution completes successfully)
```

On execution failure:
- `approval_state["status"]` remains `"RESUMING"` or transitions to `"FAILED"`
- No `RESUMED` is recorded
- No automatic re-execution
- No duplicate approval
- The operation is NOT considered successful

**Execution Gating Rule:**

No execution path may proceed based on `mission.status` alone. All execution gating must check `approval_state["status"]`:
- `"APPROVED"` + `explicit_approval` present → allow resume
- `"PENDING_APPROVAL"` → halt
- `"REJECTED"` → halt
- `"RESUMING"` → already claimed, reject duplicate
- `"RESUMED"` → already completed, reject duplicate

---

## 11. Rollback

- `AutonomyEnforcer` هو مكون جديد (لا يعدل مكونات موجودة).
- يمكن تعطيله بتمرير `None` كـ `autonomy_enforcer` في orchestrators، **لكن فقط للعمليات غير الحساسة**.
- للعمليات الحساسة، حتى مع `autonomy_enforcer=None`، يُطبق `APPROVAL_REQUIRED` ولا يمكن تعطيله.
- في حالة الفشل: يُستخدم `APPROVAL_REQUIRED` كـ safe default.
- لا يتChanged سلوك المكونات عند غياب Enforcer للعمليات غير الحساسة.

---

## 12. Definition of Done

- [ ] `AutonomyEnforcer` class implemented in `backend/app/agent/autonomy/enforcer.py`
- [ ] `AutonomyEnforcer` resolves policy from Goal/Plan via `AutonomyPolicyInterpreter`
- [ ] `AutonomyEnforcer` evaluates via `AutonomyEvaluator`
- [ ] `AutonomyEnforcer` returns `AutonomyEnforcementDecision` for ALL paths (no string returns)
- [ ] `ToolOrchestrator` integrates `AutonomyEnforcer` before tool execution
- [ ] `AgentOrchestrator` integrates `AutonomyEnforcer` before tool execution
- [ ] `BLOCK` halts execution immediately with audit
- [ ] `APPROVAL_REQUIRED` routes through existing `ApprovalGate` and halts execution until approval
- [ ] `APPROVAL_REQUIRED` saves approval state in `SessionManager` as part of `agent_sessions.context`
- [ ] No execution without explicit approval
- [ ] Resume after explicit approval executes same task/step using same `mission_id + task_id + step_id`
- [ ] **Mandatory: `POST /approvals/{id}/approve` updated to transition `approval_state["status"]` from `PENDING_APPROVAL` to `APPROVED`, persist `explicit_approval`, and call `ResumeService.resume_if_approved()`**
- [ ] **Mandatory: `POST /approvals/{id}/reject` updated to transition `approval_state["status"]` from `PENDING_APPROVAL` to `REJECTED`, persist `explicit_approval`, and NOT call ResumeService**
- [ ] `approval_state["status"]` is the single source of truth for approval lifecycle
- [ ] `mission.status` and `approval_state["status"]` do not diverge in a way that allows invalid execution
- [ ] `SessionManager.update_mission_status_if` performs single conditional write at persistence layer for `APPROVED → RESUMING`
- [ ] ResumeService passes `approval_proof` into `session_context` for `ToolOrchestrator`
- [ ] Resume ALLOW is recorded in `agent_audit_logs`
- [ ] `BLOCK` cannot be bypassed even with `approval_proof`
- [ ] Duplicate `/approvals/{id}/approve` does not execute twice
- [ ] `PENDING` or `REJECTED` states do not allow execution
- [ ] Resume executes same `mission_id + task_id + step_id`
- [ ] `ALLOW` proceeds to existing approval gate then execution
- [ ] Atomic resume claim allows exactly one execution even under concurrent requests
- [ ] All decisions logged via `AuditRecorder.record_agent_action()`
- [ ] Audit is recorded before every return in `AutonomyEnforcer.enforce()`
- [ ] Failure never results in silent ALLOW for governed operations
- [ ] Missing policy for sensitive operations → `APPROVAL_REQUIRED` (not ALLOW)
- [ ] Missing policy for non-sensitive operations → `ALLOW` (backward compatibility)
- [ ] `autonomy_enforcer=None` + sensitive operation → `APPROVAL_REQUIRED` (no bypass)
- [ ] `autonomy_enforcer=None` + non-sensitive operation → `ALLOW` (backward compatibility)
- [ ] `ResumeService.resume_if_approved()` is async-safe
- [ ] Resume executes same step via ToolOrchestrator canonical path, does not create new Plan
- [ ] `approval_proof` downgrades `APPROVAL_REQUIRED` to `ALLOW` even when no policy exists
- [ ] `BLOCK` cannot be bypassed by `approval_proof` regardless of policy presence
- [ ] `is_sensitive_operation()` helper is canonical and consistent across `ToolOrchestrator`, `AgentOrchestrator`, fallback, and `AutonomyEnforcer`
- [ ] `ToolOrchestrator` and `AgentOrchestrator` maintain `approval_gate or ApprovalGate()` behavior
- [ ] BLOCK in `ToolOrchestrator` halts execution path immediately (break, not continue)
- [ ] BLOCK in `AgentOrchestrator` halts execution path immediately (break, not continue)
- [ ] ResumeService preserves original execution context: goal_id, plan_id, risk, chosen_path, intent, mission_id, task_id, step_id, approval_proof
- [ ] `ApprovalGate.check_approval()` after valid `approval_proof` does not reopen approval lifecycle
- [ ] All 53 tests pass
- [ ] No regressions in existing agent tests
- [ ] Backward compatibility verified

---

## 13. Out of Scope

- Proactive Self-Directed Operations
- Autonomous Goal Generation
- Multi-Agent Coordination
- Decision Engine redesign
- ApprovalGate redesign
- Knowledge Graph / Providers expansion
- Memory redesign
- Full Autonomous Export Operations
- UI changes
- PostgreSQL / ORM work

---

## 14. ما الذي سيتم تمكينه الآن؟

**Policy Enforcement at Runtime**

- تحويل `AutonomyPolicyInterpreter` من advisory-only إلى layer مطبق فعليًا.
- إنشاء `AutonomyEnforcer` كبوابةbinding بين السياسة والتنفيذ.
- دمج enforcement في `ToolOrchestrator` و `AgentOrchestrator`.
- Audit logging لكل قرار.

## 15. ما الذي سيظل مؤجلًا؟

- **Proactive Autonomy** — يتطلب enforcement layer كأساس، لكنه توسع مستقبلي.
- **Autonomous Goals** — يتطلب enforcement + proactive layer.
- **Multi-Agent Coordination** — خارج النطاق الحالي.
- **Full Autonomy** — غير مبرر في هذه المرحلة.
