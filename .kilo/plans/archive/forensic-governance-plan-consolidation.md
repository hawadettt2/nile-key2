# Nile Key — Forensic Governance & Plan Consolidation Plan

## الهدف

توحيد وتنظيف ملفات:

- Governance
- Plans
- Closure Records
- Audit/Decision Records
- Historical project documentation

بحيث يصبح للمشروع:

> أقل عدد عملي من الملفات
> + مصدر حقيقة واضح
> + لا تعارضات
> + لا فقدان للقرارات أو الأدلة
> + لا تأثير على Application Code أو Runtime

---

# القاعدة الحاكمة

> **Governance Clarity > File Count Reduction**

ولا يحذف أي ملف لمجرد أنه:
- قديم
- قصير
- مكتمل
- مكرر ظاهريًا
- يمكن إعادة كتابة محتواه

قبل أي حذف:

> **Inventory → Authority Check → Dependency Check → Consolidation Decision → Approval → Migration → Verification → Deletion**

---

# PHASE 0 — FREEZE & BASELINE

**MODE: Forensic Audit**

على:

`main` — Canonical

تحقق من:

- Git status
- Current HEAD
- Remote parity
- جميع ملفات `.kilo/plans/`
- جميع ملفات `.kilo/audits/`
- `PLAN.md`
- `CURRENT_STATUS.md`
- `TECH_DEBT.md`
- `CHANGELOG.md`
- `README.md`
- أي Governance indexes أو SSOT documents

### Exit Criteria

> Inventory baseline مكتمل.
> لا تعديل.
> لا حذف.

---

# PHASE 1 — GOVERNANCE INVENTORY

أنشئ جردًا فعليًا لكل ملف Governance/Plan.

لكل ملف:

| File | Type | Status | Authority | References | Superseded? | Duplicate? |
|------|------|--------|-----------|------------|-------------|------------|

التصنيفات المسموحة:

- ACTIVE PLAN
- AUTHORITATIVE
- GOVERNANCE RECORD
- PERMANENT CONTRACT
- HISTORICAL EVIDENCE
- COMPLETED / SUPERSEDED
- DUPLICATE / REDUNDANT
- UNKNOWN

---

# PHASE 2 — AUTHORITY & SSOT MAP

أنشئ خريطة واضحة:

## Layer 1 — Permanent Authority

مثل:

`PLAN.md`

## Layer 2 — Current State

مثل:

`CURRENT_STATUS.md`

## Layer 3 — Technical Debt

مثل:

`TECH_DEBT.md`

## Layer 4 — Active Plans

الخطط التي ما زالت فعالة.

## Layer 5 — Historical Evidence

Audit / closure / completed records.

### الهدف

لكل موضوع يجب أن يكون هناك:

> **مرجع حالي واحد فقط**

---

# PHASE 3 — CROSS-DOCUMENT CONFLICT AUDIT

قارن محتوى الملفات ضد بعضها.

ابحث عن:

- قرارات متعارضة.
- Status مختلف لنفس Finding.
- Roadmap قديم مقابل Roadmap أحدث.
- خطة تقول ACTIVE وأخرى تقول CLOSED.
- Authorization قديم لا يزال يبدو ساريًا.
- نفس القرار مكتوب في عدة ملفات بصيغ مختلفة.
- معلومات أصبحت obsolete.

كل تعارض يصنف:

- RESOLVED BY NEWER AUTHORITY
- HISTORICAL / PRESERVE
- GOVERNANCE GAP
- UNKNOWN

### ممنوع

لا تحل أي تعارض بالحذف.

أولًا حدد:

> أي ملف هو Authority؟

---

# PHASE 4 — CONSOLIDATION MATRIX

لكل مجموعة ملفات مرتبطة، أنشئ قرارًا:

| Files | Current Authority | Action | Destination |
|-------|-------------------|--------|-------------|

القرارات المسموحة:

### KEEP
ملف يحتاجه المشروع حاليًا.

### MERGE
المعلومات المهمة تُدمج في ملف authoritative آخر.

### ARCHIVE
المعلومات تاريخية ويجب الحفاظ عليها، لكن لا تحتاج أن تبقى ضمن Current Working Set.

### DELETE
لا قيمة مستقبلية + لا Evidence مطلوب + لا References + المعلومات محفوظة عند الحاجة.

### UNKNOWN
لا يمكن إثبات سلامة الإزالة.

---

# PHASE 5 — DEFINE TARGET GOVERNANCE SET

قبل أي تعديل، حدد **Target Governance Set**.

الهدف هو الوصول إلى مجموعة صغيرة وواضحة، مثل:

### 1. Master Authority
`PLAN.md`

### 2. Current State
`CURRENT_STATUS.md`

### 3. Technical Debt
`TECH_DEBT.md`

### 4. Changelog
`CHANGELOG.md`

### 5. Active Plans
فقط الخطط التي ما زالت فعالة.

### 6. Permanent Contracts / Policies
فقط ما يجب أن يبقى دائمًا.

### 7. Historical/Audit Evidence
في مساحة منفصلة وواضحة، دون خلطها مع Active Plans.

**مهم:**
هذه أسماء طبقات مستهدفة، وليست إذنًا بحذف الملفات الحالية.

---

# PHASE 6 — CONSOLIDATION PLAN

لكل ملف سيتم دمجه:

1. حدد المعلومات التي يجب حفظها.
2. حدد الملف المستهدف.
3. ادمج المعلومات.
4. تحقق من عدم فقدان أي Decision/Evidence.
5. تحقق من عدم تغيير معنى القرار.
6. سجل Source → Destination.

أنشئ:

> **CONSOLIDATION TRACEABILITY MATRIX**

مثال:

`old-plan.md`
→ `CURRENT_STATUS.md`
→ Sections X/Y
→ verified.

---

# PHASE 7 — REFERENCE REVALIDATION

بعد تحديد Target Set، افحص references قبل أي حذف:

- Git
- scripts
- `.kilo`
- `.kilocode`
- documentation
- plans
- audits
- CI
- tooling
- developer instructions
- dynamic file discovery

إذا كان الملف referenced:

> لا يحذف تلقائيًا.

يجب تحديد هل المرجع:
- Current
- Historical
- Obsolete

---

# PHASE 8 — GOVERNANCE SAFETY REVIEW

تحقق أن عملية الدمج لن تفقد:

- Authorization decisions
- Acceptance decisions
- Closure decisions
- Findings
- Exceptions
- Conditions
- Evidence references
- Historical accountability

والأهم:

> **Current State must never depend on historical files to determine current authority.**

---

# PHASE 9 — TARGET STATE REVIEW

اعرض فقط:

### KEEP
الملفات التي ستبقى.

### MERGE
الملفات التي ستُدمج.

### ARCHIVE
الملفات التاريخية التي ستخرج من Working Governance Set.

### DELETE
الملفات التي ثبت عدم الحاجة إليها.

### UNKNOWN
أي ملف لم يحسم.

ثم:

> **Lead Architect Review**

ولا تنفيذ قبل الموافقة.

---

# PHASE 10 — CONTROLLED CONSOLIDATION EXECUTION

بعد الموافقة:

### Batch 1
Merge content only.

### Batch 2
Reference updates only.

### Batch 3
Archive/delete approved obsolete files only.

لا تخلط الأنواع في Batch واحدة.

لا تحذف ملفًا قبل أن:

> Destination verified + content preserved + references updated.

---

# PHASE 11 — POST-CONSOLIDATION VERIFICATION

تحقق من:

## Governance
- كل قرار قديم محفوظ.
- Current State له مصدر واحد.
- لا conflicting statuses.

## References
- لا Broken references.
- لا plans تشير إلى ملفات محذوفة دون معالجة.

## Git
- لا تغييرات خارج Governance scope.

## Application
- Application Code = UNTOUCHED.
- Tests = UNTOUCHED.
- Runtime = UNTOUCHED.

## Tooling
- Kilo يمكنه الوصول إلى الملفات المرجعية الجديدة.

---

# PHASE 12 — FINAL SSOT VERIFICATION

يجب أن نستطيع الإجابة بوضوح عن:

### ما هو المرجع الحالي للمشروع؟
`PLAN.md`

### أين الحالة الحالية؟
`CURRENT_STATUS.md`

### أين الديون التقنية؟
`TECH_DEBT.md`

### أين العمل النشط؟
`ACTIVE PLANS فقط`

### أين التاريخ والأدلة؟
`HISTORICAL / AUDIT RECORDS`

### هل يوجد أكثر من مصدر لنفس القرار؟
> لا.

إذا كان هناك أكثر من مصدر:

> STOP → Resolve Authority.

---

# PHASE 13 — FINAL GOVERNANCE CLEAN BASELINE

الهدف النهائي:

- أقل مجموعة عملية من ملفات Governance.
- لا Duplicate Active Plans.
- لا Conflicting Decisions.
- لا Obsolete Plan presented as active.
- لا فقدان Historical Evidence.
- لا Broken References.
- لا Application Changes.

ثم:

> `git status = CLEAN`

---

# STOP CONDITIONS

توقف فورًا إذا ظهر:

- تعارض غير محسوم.
- ملف مجهول السلطة.
- قرار تاريخي قد يفقد Evidence.
- Reference غير معروف.
- معلومات لا يمكن إثبات نقلها بالكامل.
- احتمال كسر Tooling/Kilo.
- حاجة لتعديل Application Code.
- حاجة لتعديل Architecture.

عندها:

> STOP → REPORT → REVIEW

---

# AUTHORIZATION BOUNDARY

هذه الخطة في البداية:

> **READ-ONLY / ASSESSMENT**

ولا تمنح:

- Delete Authorization
- Merge Authorization
- Archive Authorization
- Code Authorization

بعد اكتمال Phase 1–9 فقط:

> **Lead Architect Approval of Target Governance Set**

ثم يبدأ التنفيذ في Batches منفصلة.

---

# FINAL SUCCESS CRITERIA

تعتبر الخطة مكتملة فقط عندما:

1. تم جرد كل Governance/Plan files.
2. تم تحديد Authority لكل موضوع.
3. تم كشف التعارضات.
4. تم تحديد Target Governance Set.
5. تم تحديد KEEP/MERGE/ARCHIVE/DELETE/UNKNOWN.
6. تم إنشاء Traceability Matrix.
7. لم تفقد أي قرارات أو أدلة.
8. لا يوجد أكثر من SSOT لنفس القرار.
9. تم تنفيذ الدمج/الأرشفة/الحذف المعتمد فقط.
10. تم التحقق من عدم وجود Broken References.
11. Application / Tests / Runtime لم تتأثر.
12. `main` بقي Canonical.
13. Git baseline نظيف.

---

# النتيجة المستهدفة

> **Nile Key Governance = SMALL, CLEAR, AUTHORITATIVE, NON-CONFLICTING**

بدل:

> عدد كبير من الخطط والسجلات التي تتنافس على تفسير الحالة.

الهدف ليس حذف التاريخ.

الهدف:

> **فصل Current Authority عن Historical Evidence، ثم الاحتفاظ بأقل مجموعة عملية من الملفات التي يحتاجها المشروع فعلًا.**
