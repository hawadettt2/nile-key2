# قرار مصدر الحقيقة — Nile Key (المرحلة الثانية)

**الإصدار:** 1.2
**التاريخ:** 2026-11-20 + 2026-11-21
**الحالة:** ✅ **معتمد من المالك — الإصدار 1.2**.
**المراجع:**
- الخطة المعتمدة: `MASTER_PLAN.md` — الإصدار 1.1، القسم 3.3 (توحيد مصدر التعريف، 445–452).
- تقرير المرحلة الأولى: `PHASE_1_AUDIT_REPORT.md` — نتائج E1–E28 (8.4.13–8.4.21).
- سجل القرارات: `DECISION_LOG.md` — قرارات المالك (2026-11-20).
- البطاقات المعتمدة: `TARGET_ROLE_CARDS.md` — البطاقات الاثنتا عشرة (معتمدة).
- مصفوفة الصلاحيات: `TARGET_PERMISSION_MATRIX.md` — المصفوفة المستهدفة.

> **تنبيه:** هذا المستند يوثّق **قرار المالك** بشأن مصدر الحقيقة لتعريفات الأدوار، **لا** يعدّل أي تعريف فعلي. التنفيذ (إن وافق المالك) يتم في `IMPLEMENTATION_SCOPE.md` (مرحلة لاحقة).

---

## 1. قرار المالك المعتمد

**النص:** تعريفات وكلاء المشروع هي **المصدر الرسمي للحقيقة** لتعريفات الأدوار؛ وإعدادات Kilo العامة مسؤولة عن **إعدادات التشغيل والنماذج والمزود**، **وليست مصدرًا موازيًا** لتعريفات الأدوار.

**التاريخ:** 2026-11-20 (أصلي) + 2026-11-21 (تحديث).
**الحالة:** ✅ معتمد من المالك.

**الأثر:**
- **تعريفات الأدوار** (الاسم، الوصف، الـprompt، الـmode، الصلاحيات) → **من تعريفات المشروع**.
- **إعدادات Kilo العامة** (`~/.config/kilo/kilo.jsonc`) → **إعدادات التشغيل، النماذج، المزود** — لا مصدر موازٍ للأدوار.

### قرار إضافي (2026-11-21): تعريفات متكاملة لـforensic-audit وincident-remediation

**النص:** اعتماد تعريفات **Forensic Audit** و**Incident Remediation** كمصدر رسمي **متكامل** يتكون من JSONC وMarkdown معًا:
- **forensic-audit:** `.kilo/kilo.jsonc` + `.kilo/agent/forensic-audit.md`.
- **incident-remediation:** `.kilo/kilo.jsonc` + `.kilo/agent/incident-remediation.md`.

**التاريخ:** 2026-11-21.
**الحالة:** ✅ معتمد من المالك.

**الأثر:**
- الملفان **متكاملان** (JSONC: mode/bash؛ MD: edit/task/description/prompt) — **لا دمج، لا حذف، لا ترحيل**.
- **تداخل `mode`:** كلا الملفين يعرّف `mode: all` — **نقطة تحقق تشغيلية لاحقة** (لا تُفترض أسبقية غير مثبتة).
- **النتيجة:** المصدر الرسمي = **JSONC + MD معًا** (ليس ملفًا واحدًا).

## 2. جدول الوكلاء الاثني عشر (مصدر رسمي واحد لكل وكيل)

> **ملاحظة:** 10 وكلاء لهم ملف مصدر واحد؛ **forensic-audit** و**incident-remediation** لهما **مصدر رسمي متكامل** (JSONC + MD) بقرار المالك 2026-11-21 — **لا دمج، لا حذف، لا ترحيل**. تداخل `mode` بين الملفين = **نقطة تحقق تشغيلية لاحقة** (لا أسبقية غير مثبتة).

| # | الوكيل | التعريفات الحالية (الح) | مصدر كل تعريف | المصدر الرسمي المستهدف | حالة base/default |
|---|---|---|---|---|---|---|---|---|
| 1 | **ask** | mode=all، bash=deny، prompt | project JSONC (`.kilo/kilo.jsonc:4–10`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |
| 2 | **architect** | mode=all، prompt | project JSONC (`:11–14`) + **global MD** (`~/.config/kilo/agents/architect.md`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |
| 3 | **forensic-audit** | mode=all، bash=deny | project JSONC (`:15–20`) + **global JSONC** (`:156–160`) + project MD (`.kilo/agent/forensic-audit.md`) | **`.kilo/kilo.jsonc` + `.kilo/agent/forensic-audit.md`** (متكامل — قرار 2026-11-21) | **متجاوز** (م¤) |
| 4 | **debug** | mode=all، bash=ask | project JSONC (`:21–26`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |
| 5 | **incident-remediation** | mode=all، bash=ask | project JSONC (`:27–32`) + **global JSONC** (`:150–155`) + project MD (`.kilo/agent/incident-remediation.md`) | **`.kilo/kilo.jsonc` + `.kilo/agent/incident-remediation.md`** (متكامل — قرار 2026-11-21) | **متجاوز** (م¤) |
| 6 | **code** | mode=all، bash=allow، prompt | project JSONC (`:33–39`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |
| 7 | **code-reviewer** | read=allow، bash/edit/task/webfetch=deny، question=allow | project MD (`.kilo/agents/code-reviewer.md`) | `.kilo/agents/code-reviewer.md` | **متجاوز** (م¤) |
| 8 | **frontend-specialist** | mode=all، bash=allow | project JSONC (`:69–74`) + **global MD** (`~/.config/kilo/agents/frontend-specialist.md`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |
| 9 | **data** | mode=all، bash=allow | project JSONC (`:57–62`) + **global MD** (`~/.config/kilo/agents/data.md`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |
| 10 | **test-engineer** | mode=all، bash=allow | project JSONC (`:63–68`) + **global MD** (`~/.config/kilo/agents/test-engineer.md`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |
| 11 | **explore** | mode=all، prompt، edit=deny، bash=deny، read/glob/grep=allow | project JSONC (`:46–56`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |
| 12 | **orchestrator** | mode=primary، edit=deny، bash=deny، task=allow | project JSONC (`:75–82`) | `.kilo/kilo.jsonc` | **متجاوز** (م¤) |

**ملاحظة:** **General** (مستثنى من الـ12) — project JSONC (`:40–45`) + **global JSONC** (`:161–163`, `disable:false`) → المصدر الرسمي: `.kilo/kilo.jsonc`؛ حالة base/default: **متجاوز** (م¤).

**التحفظ على base/default:** جميع الـ12 لديهم تعريف مشروع → الـbuilt-in **متجاوز** لكل منهم (تم التحقق per-agent، لا افتراض). أما الوكلاء التقنيون المدمجون (plan، compaction، summary، title، build) **غير معرّفين في المشروع** → **غير متجاوزين** (خارج الـ12).

## 3. حصر التعريفات المكررة (global + project)

| الوكيل | التكرار | المعالجة (دون حذف قبل إثبات بديل) |
|---|---|---|
| **architect** | global MD (`~/.config/kilo/agents/architect.md`) + project JSONC (`:11–14`) | الـglobal MD = **legacy**؛ يُرحَّل/يُحذف بعد إثبات بديل المشروع |
| **forensic-audit** | global JSONC (`:156–160`) + project JSONC (`:15–20`) + project MD | **project JSONC + project MD = مصدر رسمي متكامل** (قرار 2026-11-21)؛ الـglobal JSONC = **legacy**؛ لا دمج/حذف/ترحيل للـproject |
| **incident-remediation** | global JSONC (`:150–155`) + project JSONC (`:27–32`) + project MD | **project JSONC + project MD = مصدر رسمي متكامل** (قرار 2026-11-21)؛ الـglobal JSONC = **legacy**؛ لا دمج/حذف/ترحيل للـproject |
| **data** | global MD (`~/.config/kilo/agents/data.md`) + project JSONC (`:57–62`) | الـglobal MD = **legacy**؛ يُرحَّل/يُحذف بعد إثبات بديل المشروع |
| **test-engineer** | global MD (`~/.config/kilo/agents/test-engineer.md`) + project JSONC (`:63–68`) | الـglobal MD = **legacy**؛ يُرحَّل/يُحذف بعد إثبات بديل المشروع |
| **frontend-specialist** | global MD (`~/.config/kilo/agents/frontend-specialist.md`) + project JSONC (`:69–74`) | الـglobal MD = **legacy**؛ يُرحَّل/يُحذف بعد إثبات بديل المشروع |
| **general** (خارج الـ12) | global JSONC (`:161–163`) + project JSONC (`:40–45`) | الـglobal JSONC = **legacy**؛ يُرحَّل/يُحذف بعد إثبات بديل المشروع |

**لا حذف قبل إثبات بديل:** أي تعريف global يُعامل كـ**legacy**؛ لا يُحذف إلا بعد إثبات أن البديل (project) يغطيه.

## 4. AGENTS.md

- **المحتوى:** `AGENTS.md` = **1,190 بايت (ليس فارغًا)** — يحتوي تعليمات المشروع (العربية الإلزامية، قواعد المشروع، حدود العمل).
- **الوراثة:** **غير مثبت** (التقرير سطر 2362: «هل تُورّث AGENTS.md... **غير مثبت**») — الوراثة للوكلاء الفرعيين **لم تُثبت ساكنًا**.
- **التمييز:** **وجود التعليمات** (م¤ — 1,190 بايت) ≠ **ثبوت وراثتها** (غير مثبت).

## 5. `.kilocode`

- **المحتوى:** `.kilocode/` يضم `NILE_KEY_RULES.md` (7,086)، `PATCH_WORKFLOW.md` (2,559)، `00_README.md` (2,680)، `04_KILO_SETUP.md` (1,421)، `SESSION_STATE.md` (1,483)، `.gitignore`، `package.json`، `package-lock.json`.
- **التحميل:** **وجود الملفات لا يثبت تحميلها كـinstructions** — التقرير (سطر 1507–1517) يوضح `.kilocode` كمجلد إعداد (up)، تحميل محتواه كـinstructions **غير مثبت ساكنًا**.
- **التمييز:** ملفات `.kilocode` **موجودة** (م¤) ≠ **محمّلة كـinstructions** (غير مثبت).

## 6. حالة base/default لكل وكيل

| الفئة | الوكلاء | base/default |
|---|---|---|
| **متجاوز** (project يعرّفهم) | الـ12 (ask, architect, forensic-audit, debug, incident-remediation, code, code-reviewer, frontend-specialist, data, test-engineer, explore, orchestrator) + general | **متجاوز** (م¤ — لكل واحد تعريف مشروع) |
| **غير متجاوز** (خارج الـ12) | plan، compaction، summary، title، build (تقنيون مدمجون) | **غير متجاوز** (لا تعريف مشروع) |
| **غير محسوم** | — | — |

**التفصيل:** لا تعميم «متجاوز» على الجميع — الـ12 فقط (وكلاء المشروع)؛ التقنيون (plan/compaction/summary/title/build) **غير متجاوزين**.

## 7. منع التكرار والتعارض

1. **مصدر واحد لكل وكيل:** تعريف المشروع (`.kilo/kilo.jsonc` أو `.kilo/agent/forensic-audit.md` / `.kilo/agent/incident-remediation.md` / `.kilo/agents/code-reviewer.md`) هو المرجع.
2. **لا تعريف موازٍ** في الإعدادات العامة (بعد الترحيل/الحذف).
3. **التعارض:** عند تعارض عام/مشروع → **المشروع يفوز** (override).
4. **التكرار:** عند تكرار تعريف (عام + مشروع) → **يُحذف العام** (بعد إثبات الترحيل).
5. **التوثيق:** أي تعريف محلي/عام مستثنى من Git → **يُوثّق**.

## 8. دور قواعد المشروع

| الملف | الدور | التمييز |
|---|---|---|
| `.kilocode/NILE_KEY_RULES.md` | **الدستور المعماري** | **قواعد المشروع** — لا تعريف أدوار |
| `.kilocode/PATCH_WORKFLOW.md` | **دورة حياة الرقعة** | **قواعد المشروع** — لا تعريف أدوار |
| `AGENTS.md` | **تعليمات المشروع** (1,190 بايت) | **تعليمات** — لا تعريف أدوار |

**التمييز:** قواعد المشروع (دستور/سير عمل/تعليمات) **≠** تعريفات الأدوار (اسم/وصف/prompt/mode/permission).

## 9. خريطة المصدر الحالي مقابل المستهدف

| الطبقة | الحالي (E1–E28) | المستهدف (قرار المالك) |
|---|---|---|
| **تعريفات المشروع** | `.kilo/kilo.jsonc` + `.kilo/agent/forensic-audit.md` + `.kilo/agent/incident-remediation.md` + `.kilo/agents/code-reviewer.md` | **المصدر الرسمي** |
| **التعريفات العامة** | `~/.config/kilo/agents/*.md` + `~/.config/kilo/kilo.jsonc` (agent section) | **تُرحَّل/تُحذف** |
| **التعريفات المدمجة** | built-in (base) | base (متجاوز للـ12؛ غير متجاوز للتقنيين) |
| **إعدادات Kilo** | `~/.config/kilo/kilo.jsonc` | **إعدادات تشغيل/نماذج/مزود** — لا أدوار |
| **قواعد المشروع** | `.kilocode/*` + `AGENTS.md` | قواعد (لا أدوار) |

## 10. الاستثناءات وغير المحسوم

| # | الاستثناء/غير المحسوم | السبب | الدليل المطلوب |
|---|---|---|---|
| 1 | تعريفات global (architect, data, frontend-specialist, test-engineer, forensic-audit, incident-remediation, general) | تحتاج ترحيل/حذف | قرار المالك + IMPLEMENTATION_SCOPE |
| 2 | `plan_exit` كأداة مستقلة | تعريفه غير مثبت | `debug agent` (E27) |
| 3 | Q6 (الأدوات الخمس) | presence غير محسوم | `debug agent` (E27) |
| 4 | قواعد عامة/محلية مستثناة من Git | تحتاج توثيق | قرار المالك |
| 5 | تعارض `options`/`title` | مسألة توثيقية مستقلة | IMPLEMENTATION_SCOPE |
| 6 | تحميل `.kilocode`/AGENTS.md كـinstructions | غير مثبت ساكنًا | تتبّعدخلي (المرحلة الثالثة) |
| 7 | **تداخل `mode` بين JSONC وMD** (forensic-audit/incident-remediation) | **محسوم جزئيًا** (قرار 2026-11-21: متكامل، لا دمج) — **نقطة تحقق تشغيلية لاحقة** (لا أسبقية) | تتبّعدخلي (المرحلة الثالثة) |

## 11. معايير التحقق من التطبيق

**بعد التنفيذ (IMPLEMENTATION_SCOPE.md):**
1. **لا تعريف موازٍ:** بحث `~/.config/kilo/agents/*.md` → لا تعريف دور (بعد الترحيل/الحذف).
2. **مصدر واحد:** كل وكيل له تعريف مشروع واحد (`.kilo/kilo.jsonc` أو `.kilo/agent/forensic-audit.md` / `.kilo/agent/incident-remediation.md` / `.kilo/agents/code-reviewer.md`).
3. **لا تعارض:** عند تعارض → المشروع يفوز (override).
4. **إعدادات Kilo:** لا تحتوي تعريفات أدوار (فقط إعدادات تشغيل/نماذج/مزود).
5. **قواعد المشروع:** `.kilocode/*` + `AGENTS.md` لا تحتوي تعريفات أدوار.
6. **التوثيق:** أي تعريف مستثنى → موثّق.
7. **تحميل `.kilocode`/AGENTS.md:** تحققدخلي (المرحلة الثالثة) — لا يُفترض.

**التحقق التشغيلي (بعد التنفيذ):** `kilo debug agent <name>` لكل وكيل — للتأكد من المصدر الفعلي (خارج هذه المهمة).

## 12. الحالة

- **✅ معتمد من المالك — الإصدار 1.2**.
- **المرحلة الأولى:** معتمدة (نتائج E1–E28).
- **المرحلة الثانية:** البطاقات الاثنتا عشرة + المصفوفة + هذا المستند — **معتمدة من المالك (الإصدار 1.2)**.
- **لا اعتماد للمرحلة الأولى** من تلقاء النفس؛ **IMPLEMENTATION_SCOPE.md** مؤجل (أمر منفصل).
