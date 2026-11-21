# مصفوفة الصلاحيات المستهدفة — Nile Key (المرحلة الثانية)

**الإصدار:** 1.0
**التاريخ:** 2026-11-20
**الحالة:** مسودة أولية — **غير معتمدة**؛ تنتظر مراجعة المالك واعتمادها.
**المراجع:**
- الخطة المعتمدة: `MASTER_PLAN.md` — الإصدار 1.1، القسم 2.3 (سياسة الصلاحيات، 359–377).
- تقرير المرحلة الأولى: `PHASE_1_AUDIT_REPORT.md` — نتائج E1–E28 (8.4.13، 8.4.17–8.4.19).
- سجل القرارات: `DECISION_LOG.md` — قرارات المالك (2026-11-20).
- البطاقات المعتمدة: `TARGET_ROLE_CARDS.md` — البطاقات الاثنتا عشرة (معتمدة).

> **تنبيه:** هذه مصفوفة **مستهدفة** (ما اعتمده المالك)، **لا** مصفوفة فعلية (الحالة الحالية المثبتة). عمود «الحالي» = **م¤** من E1–E28؛ عمود «المستهدف» = **معتمد من المالك**. **لا تُقرأ أي قيمة مستهدفة كقيمة حالية.** لا تُفترض أي صلاحية لا يسندها قرار صريح.

---

## 1. المصفوفة الموحدة (12 وكيلًا — باستثناء General)

### 1.1 Bash / Edit / Write / Task

| الوكيل | Bash (حالي → مستهدف) | Edit (حالي → مستهدف) | Write (حالي → مستهدف) | Task (حالي → مستهدف) |
|---|---|---|---|---|
| **Code** | `allow` (JSONC:34) → **ask** (قرار المالك) | `allow` (global:8) → **allow ضمن النطاق** | `allow` (edit) → **allow ضمن النطاق** | `allow` موروثة (@110,775,608) → **deny** (قرار 5) |
| **Ask** | `deny` (JSONC:7) → **deny** | `allow` (global:8) → **deny** (قرار المالك) | `allow` (edit) → **deny** (قرار المالك) | `allow` (افتراضي) → **deny** (قرار 5) |
| **Forensic Audit** | `deny` (JSONC:16) → **deny** | `deny` (MD:5) → **deny** | `deny` (edit) → **deny** | `deny` (MD:6) → **deny** (قرار 5) |
| **Code Reviewer** | `deny` (MD) → **deny** | `deny` (MD) → **deny** | `deny` (edit) → **deny** | `deny` (MD) → **deny** (قرار 5) |
| **Explore** | `deny` (JSONC:48–49) → **deny** | `deny` (JSONC:48) → **deny** (م¤) | `deny` (edit) → **deny** (م¤) | `allow` (افتراضي) → **deny** (قرار 5) |
| **Architect** | `deny` (MD:8) → **deny** | `* deny` + plan patterns (MD:14) → **allow لـ`.kilo/plans/nile-key-agent-stabilization/*.md` فقط** (قرار 4) | `* deny` + plan → **allow لـ`.kilo/plans/nile-key-agent-stabilization/*.md` فقط** (قرار 4) | `allow` (افتراضي) → **deny** (قرار 5) |
| **Orchestrator** | `deny` (JSONC:77) → **deny** | `deny` (JSONC:77) → **deny** | `deny` (edit) → **deny** | `allow` (JSONC:78) → **allow** (وحده — قرار 5) |
| **Debug** | `ask` (JSONC:22) → **ask** (قرار 3 + قرار المالك) | `allow` (global:8) → **deny** (قرار 3 + قرار المالك) | `allow` (edit) → **deny** (قرار 3 + قرار المالك) | `allow` (افتراضي) → **deny** (قرار 5) |
| **Incident Remediation** | `ask` (JSONC:28) → **ask** (قرار 6 + قرار المالك) | `ask` (MD:5) → **ask** (قرار 6 + قرار المالك) | `ask` (edit) → **ask** (قرار 6 + قرار المالك) | `deny` (MD:6) → **deny** (قرار 5) |
| **Frontend Specialist** | `allow` (JSONC:70) → **ask** (قرار 7 + قرار المالك) | test patterns (MD) → **allow (ملفات الواجهة)** | test patterns (edit) → **allow (ملفات الواجهة)** | `allow` (افتراضي) → **deny** (قرار 5) |
| **Data** | `allow` (JSONC:58) → **ask** (قرار 7 + قرار المالك) | `allow` (global:8) → **allow (Notebook ومخرجات محددة)** | `allow` (edit) → **allow (Notebook ومخرجات محددة)** | `allow` (افتراضي) → **deny** (قرار 5) |
| **Test Engineer** | `allow` (JSONC:64) → **ask** (قرار 7 + قرار المالك) | `* deny` + 8 test patterns (MD:7–22) → **allow (ملفات الاختبار فقط)** | `* deny` + 8 test → **allow (ملفات الاختبار فقط)** | `allow` (افتراضي) → **deny** (قرار 5) |

### 1.2 أدوات القراءة/البحث والأدوات الأخرى

| الوكيل | القراءة/البحث | أدوات أخرى (mcp/webfetch/websearch/skill…) | قيود المسارات |
|---|---|---|---|
| **Code** | read/glob/grep/list | mcp: allow (عام) | لا قيود أمان (إرشاد) |
| **Ask** | read/glob/grep/list | mcp: allow (عام) | لا (لا يعدّل) |
| **Forensic Audit** | read/glob/grep/list | mcp: deny | لا (قراءة فقط) |
| **Code Reviewer** | read/glob/grep/list | mcp: deny، webfetch: deny | لا (قراءة فقط) |
| **Explore** | read/glob/grep/list | mcp: deny | لا (قراءة فقط) |
| **Architect** | read/glob/grep/list | mcp: deny | `.kilo/plans/nile-key-agent-stabilization/*.md` فقط (قرار 4) |
| **Orchestrator** | read/glob/grep/list | mcp: deny | لا (لا يعدّل) |
| **Debug** | read/glob/grep/list | mcp: deny | لا (لا يعدّل) |
| **Incident Remediation** | read/glob/grep/list | mcp: deny | نطاق الحادثة المعتمد (بعد موافقة المالك) |
| **Frontend Specialist** | read/glob/grep/list | mcp: deny | ملفات الواجهة فقط (حسب المهمة) |
| **Data** | read/glob/grep/list | mcp: deny | Notebook ومخرجات محددة |
| **Test Engineer** | read/glob/grep/list | mcp: deny | ملفات الاختبار فقط |

## 2. السبب والمصدر واختبار القبول

| الوكيل | السبب/المصدر | اختبار القبول |
|---|---|---|
| **Code** | قرار المالك (Bash=ask)؛ قرار 5 (Task=deny)؛ الخطة 366 | تنفيذ تغيير معتمد + Diff + عدم تجاوز النطاق |
| **Ask** | الخطة 346 («لا يعدّل ملفات»)؛ قرار 5؛ قرار المالك (Edit/Write=deny) | إجابة صحيحة دون تنفيذ/تعديل |
| **Forensic Audit** | الخطة 348 («قراءة فقط، لا إصلاح ولا Bash ولا Task») | تقرير أدلة صحيح دون إصلاح |
| **Code Reviewer** | الخطة 352 («لا يصلح ولا يعدل ولا يشغّل اختبارات») | ملاحظات مراجعة صحيحة دون إصلاح |
| **Explore** | الخطة 356 («لا ينفذ كتابة/نقلًا/حذفًا»)؛ قرار 5 | نتائج بحث صحيحة دون كتابة |
| **Architect** | قرار 4 (ملفات الخطط)؛ قرار المالك (حصر المسار)؛ قرار 5 | تصميم صحيح دون تغيير كود التطبيق |
| **Orchestrator** | الخطة 357 («تُمنع أدوات تعديل الملفات والتنفيذ المباشر»)؛ قرار 5 | توزيع صحيح دون تعديل/تنفيذ |
| **Debug** | قرار 3 (تشخيص فقط)؛ قرار 5؛ قرار المالك (Bash=ask، Edit/Write=deny) | تشخيص دون تنفيذ الإصلاح |
| **Incident Remediation** | قرار 6 (موافقة المالك)؛ قرار 5 | إصلاح ضيق معتمد دون توسيع |
| **Frontend Specialist** | قرار 7 (تقييد Bash)؛ قرار المالك (Bash=ask)؛ قرار 5 | تغييرات واجهة دون تجاوز |
| **Data** | قرار 7؛ قرار المالك (Bash=ask)؛ قرار 5 | تحليل صحيح دون تغيير التطبيق |
| **Test Engineer** | قرار 7؛ قرار المالك (Bash=ask)؛ قرار 5 | اختبارات صحيحة دون تغيير الإنتاج |

## 3. حدود الإنفاذ التقني (م¤ — لا ضمانات غير مثبتة)

- **Bash = ask**: موافقة على **سلسلة الأمر** (assert bash @109,207,519)؛ **لا فحص مسار** (E27).
- **Bash = allow**: سلطة على سلسلة الأمر؛ **لا حماية مسار** (ShellTool.collect استشاري، E22/E23).
- **Edit/Write**: قاعدة `edit` (edit/write/apply_patch)؛ الأنماط (إن وجدت) تُقيّد الأداة، **لا Bash**.
- **OS sandbox**: غير متاح على Windows (E27)؛ macOS/Linux فقط.
- **external_directory**: طلب مستقل (E18)؛ مخفّف بـ`{"*":"allow"}` (global).
- **hardRuleset**: للعالم المحروس (code/build/architect/ask/debug/orchestrator) — agent.permission كـhardRuleset → deny صارم (E26).

## 4. Q6 — الأدوات غير المحسومة (مؤجلة)

- **الأدوات الخمس:** `plan_exit`, `suggest`, `kilo_local_recall`, `chart`, `agent_manager_models`.
- **الحالة:** التسجيل/الإتاحة للوكلاء التسعة **غير محسوم** (يحتاج `debug agent`)؛ القيمة الافتراضية `ask` **لا تثبت** الوجود/الإتاحة.
- **الأثر:** قد تتغير مصفوفة الصلاحيات إذا ثبت presence الأدوات الخمس؛ **مؤجل (E27/Q6)**.
- **E9 مستقل** (Tool-use/Role-performance).

## 5. التحقق من الاتساق

- **12 وكيلًا** (باستثناء General) — مطابق للبطاقات الاثنتي عشرة المعتمدة. ✅
- **لا تعارض** بين المصفوفة والبطاقات (نفس القيم المستهدفة). ✅
- **لا تعارض** مع DECISION_LOG.md (القرارات 3/4/5/6/7 + قرار المالك). ✅
- **فصل الحالي/المستهدف** — عمودان منفصلان. ✅
- **Q6 مؤجلة** — دون افتراض presence. ✅

## 6. الحالة

- **مسودة أولية — غير معتمدة**؛ تنتظر مراجعة المالك واعتمادها.
- **المعيار 317 (الرابع):** جزئي (بسبب قيود Bash التشغيلية)؛ **316 (الثالث):** جزئي (Q6).
- **لا اعتماد للمرحلة الأولى** من تلقاء النفس.
