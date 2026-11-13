# خطة الحوكمة الرئيسية لنظام عمل Kilo في Nile Key

**الملف:** `.kilo/plans/nile-key-agent-governance-plan.md`
**الإصدار:** 3 (مراجعة بعد ملاحظات المالك — 10 نقاط)
**الهدف:** تنظيم نظام عمل Kilo عبر أربع مراحل متتابعة: Rules → Skills → Workflows → Agent Governance.
**القاعدة الحاكمة:** مرحلة واحدة في كل مرة، ويتوقف التنفيذ بعد كل مرحلة حتى موافقة المالك.
**حالة هذه الوثيقة:** خطة إعداد فقط — لم يُنفَّذ أي تعديل على أي ملف.

---

## 0. تصحيحات الإصدار 3 (مقابل الإصدار 2)

| # | التصحيح | الدليل |
|---|---|---|
| V1 | `.kilo/kilo.jsonc` **إعداد محلي مستثنى من Git** وليس مشتركًا؛ كل ما يُكتب فيه لا يصل لبقية الفريق | `.gitignore:32` → `.kilo/kilo.jsonc`؛ `git check-ignore` يؤكد |
| V2 | `CURRENT_STATUS.md` **ليس مصدر حالة نهائيًا** ما دام D9 مفتوحًا | تعارضه مع `PLAN.md` |
| V3 | نصوص الأوامر نفسها تُصحَّح: إزالة تعليمات commit التلقائي، و`npm run typecheck` → `npm run build` | `runtime-verification.md:4,9,10`؛ `frontend/package.json` لا يحتوي `typecheck` |
| V4 | فصل Completion عن `/commit-verification`؛ يصبح اختياريًا بعد اكتمال المهمة وبطلب صريح | `PATCH_WORKFLOW.md:46-54` |
| V5 | إعادة صياغة أسبقية الوكلاء: **دمج عميق (deep-merge)** وليس استبدالًا كليًا | توثيق 7.4.21 + `types.gen.d.ts:835-877` |
| V6 | مراجعة الصلاحيات النهائية لكل وكيل شاملة `task` و`external_directory` قبل اعتماد الكتلة | `kilo.jsonc:3-21` + وكلاء inline |
| V7 | معالجة تعارض شرط تعديل `AGENTS.md` (محمي كتابةً) مع معايير المرحلة الأولى | توثيق: AGENTS.md محمي |
| V8 | تنبيه دقيق لمسار قاعدة البيانات الفعلي في Docker مقابل المضيف | `docker-compose.yml:30,32` |
| V9 | إدراج التحقق من اعتماد `data-investigation` المفقود ضمن مراجعة المهارات | `kilo.jsonc:211-213` |
| V10 | تصحيح عدد عناوين `04_KILO_SETUP.md` إلى **7** | `Select-String "^#{1,6} "` = 7 |

---

## 1. الجرد الفعلي (مُثبت بالأدلة)

**إصدار Kilo:** `7.4.21` — `.kilo/node_modules/@kilocode/plugin/package.json` + `opencode.log:1`.

### 1.1 حالة `.kilo/kilo.jsonc` (حسم V1)

| السؤال | الجواب | الدليل |
|---|---|---|
| هل هو متتبَّع في Git؟ | **لا** | `git ls-files .kilo/kilo.jsonc` → فارغ |
| هل هو مستثنى؟ | **نعم** | `.gitignore:31-32` → `# Local Kilo config (machine-specific)` + `.kilo/kilo.jsonc` |
| ماذا يصل للفريق؟ | لا شيء من هذا الملف | — |
| البديل المشترك المشروع | ملف `kilo.json`/`kilo.jsonc` في **جذر المستودع** (متتبَّع) | `.gitignore` لا يستثنيه |

**النتيجة:** `.kilo/kilo.jsonc` **محلي فقط**. أي `instructions` أو `permission` يُكتب فيه يعمل على هذا الجهاز وحده.

### 1.2 القواعد (Rules)

| الملف | الحالة |
|---|---|
| `.kilocode/NILE_KEY_RULES.md` | متتبَّع، 165 سطرًا |
| `.kilocode/PATCH_WORKFLOW.md` | متتبَّع، 64 سطرًا |
| `.kilocode/SESSION_STATE.md` | متتبَّع، **متوقف** (WP-10) |
| `.kilocode/00_README.md` | متتبَّع، 25 سطرًا |
| `.kilocode/04_KILO_SETUP.md` | متتبَّع، **7 عناوين** |
| `AGENTS.md` | متتبَّع، **0 بايت**، **محمي من الكتابة** |
| `.kilocode/rules/` | **غير موجود** |
| `.kilo/kilo.jsonc` | محلي، `$schema` فقط |
| `kilo.json` (الجذر) | **غير موجود** |

### 1.3 عناوين `04_KILO_SETUP.md` (تصحيح V10)

`Select-String "^#{1,6} "` يعيد **7** عناوين:
1. `# Kilo Environment` (سطر 1)
2. `# Required Rule Files` (13)
3. `# VS Code` (23)
4. `# Backend` (31)
5. `# Frontend` (40)
6. `# Recovery Procedure` (47)
7. `# Engineering Notes` (61)

### 1.4 المهارات (Skills)

| المسار | الحالة |
|---|---|
| `.kilo/skills/`, `.kilo/skill/` | **غير موجودين** |
| `~/.kilo/skills/cheerio-parsing` | عامة |
| `~/.claude/skills/{browser-automation, game-development}` | عامة |
| `~/.agents/skills/find-skills` | عامة |

**اعتماد مفقود (V9):** `kilo.jsonc:211-213` يعرّف `"requirements": {"skills": ["data-investigation"]}` للوكيل `data`، ولا يوجد أي مجلد `data-investigation` في أي مسار مهارات. الاعتماد **غير محقَّق**.

### 1.5 الأوامر (Workflows)

| الملف | frontmatter | مشكلة |
|---|---|---|
| `runtime-verification.md` | لا يوجد | السطر 4 "before any commit"؛ السطر 9 `npm run typecheck` (غير موجود)؛ السطر 10 `npm test` (أمر عام) |
| `forensic-audit.md` | لا يوجد | السطر 8 مرجع `INSTRUCTIONS.md` مفقود |
| `incident-remediation.md` | لا يوجد | السطر 7 "skill" لكائن وكيل؛ السطر 13 "Commit with single-purpose message" |
| `commit-verification.md` | لا يوجد | السطر 6 "Commit only if all checks pass" |

**إثبات `typecheck`:** `frontend/package.json` — لا يوجد `typecheck`. الموجود: `build` (`tsc -b && vite build`)، `lint` (`eslint .`)، `test` (`vitest run`).

### 1.6 الوكلاء (Agents)

| الموضع | المحتوى | ملاحظة |
|---|---|---|
| `.kilo/agent/forensic-audit.md` | `description` + `mode: primary` | لا `permission` |
| `.kilo/agent/incident-remediation.md` | `description` + `mode: primary` | لا `permission` |
| `.kilo/agents/` | **غير موجود** | — |
| `~/.config/kilo/agents/*.md` | 4 وكلاء | — |
| inline في `~/.config/kilo/kilo.jsonc` | 7 وكلاء | `data` بلا `permission` |

**تعارض:** `forensic-audit` و`incident-remediation` معرّفان في `.kilo/agent/*.md` **و** inline عالميًا.

---

## 2. المرجعيات الرسمية (Kilo 7.4.21)

### 2.1 أسبقية التعليمات

| الأولوية | المصدر |
|---|---|
| 1 | `agent.<name>.prompt` |
| 2 | `instructions` في إعداد المشروع |
| 3 | `AGENTS.md` |
| 4 | `instructions` في الإعداد العام |
| 5 | Skills (عند الطلب) |

**ملاحظة V7:** `AGENTS.md` **محمي من الكتابة** — لا يمكن تعديله بطلب من الوكيل، ويحتاج موافقة المستخدم. لذلك لا يُعتمد عليه كخطوة أولى.

**ملاحظة على `.kilocode/rules/`:** التوثيق يذكر إدراجها للتوافق الخلفي، لكن مهارة `kilo-config` لا تذكرها ضمن مصادر `instructions`. **تبقى غير مؤكدة** — لا تُستخدم كأساس تصميم.

### 2.2 أسبقية الإعدادات

remote well-known → global (`~/.config/kilo/kilo.json`) → `KILO_CONFIG` → project `./kilo.json` → `.kilo/kilo.json` → `KILO_CONFIG_CONTENT` → managed. **دمج عميق، والأحدث يسود لكل مفتاح.**

**النتيجة العملية:** `./kilo.json` (جذر، متتبَّع) و`.kilo/kilo.jsonc` (محلي) يُدمجان. الأول مشترك، الثاني محلي.

### 2.3 أسبقية الوكلاء — تصحيح V5

**ليست استبدالًا كليًا بل دمجًا عميقًا (deep-merge) بمستويات:**

1. الافتراضات المدمجة
2. الإعداد العام `~/.config/kilo/kilo.jsonc`
3. إعداد المشروع `./kilo.json`
4. `.kilo/kilo.json` (محلي)
5. ملفات الوكلاء: `.kilo/agent/*.md` و`.kilocode/agent/*.md`
6. `KILO_CONFIG_CONTENT` وmanaged

**القاعدة:** عند تعارض نفس اسم الوكيل، **الحقل المُحدَّد فقط** يُستبدل؛ بقية الحقول تُورَّث. مثال: إذا عرّف `.kilo/agent/forensic-audit.md` الحقول `description` و`mode` فقط، فإن `permission` يبقى موروثًا من الإعداد العام.

**تحفّظ موثّق:** الترتيب بين (4) و(5) غير مثبت تجريبيًا على هذا التثبيت. يُعامل كـ **افتراض قابل للانقلاب** ويُتحقق في Phase 4 قبل الاعتماد.

### 2.4 صلاحيات الوكلاء — تصحيح V6

**الأدوات الموثّقة:** `read, edit, glob, grep, list, bash, task, webfetch, websearch, semantic_search, kilo_memory_save, kilo_memory_recall, lsp, skill, external_directory, todowrite, todoread, question, doom_loop`.

**خارج التوثيق:** `mcp` و`plan_exit` و`question` (مذكورة في إعدادات محلية) ليست ضمن القائمة الموثّقة — الأولان على الأرجح **مهملان**.

**تعسف في الترتيب:** التوثيق يقول "first match wins"، بينما صفحة الأوامر تقول "last matching rule wins". **النتيجة العملية: استخدم أنماطًا غير متداخلة** ولا تعتمد على الترتيب.

**الصلاحيات النهائية الفعلية (دمج عام ← وكيل):**

| الوكيل | bash | edit | read | external_directory | task |
|---|---|---|---|---|---|
| code (مدمج) | allow | allow | allow | allow | موروث |
| architect | **deny** | `*` deny / `*.md` allow | allow | allow | موروث |
| data | allow | allow | allow | allow | موروث |
| frontend-specialist | allow | `*` deny / `*.{ts,tsx,js,jsx,css,scss,less}` allow | allow | allow | موروث |
| test-engineer | allow | `*` deny / `*.test.*` allow | allow | allow | موروث |
| forensic-audit | allow | allow | allow | allow | موروث |
| incident-remediation | allow | allow | allow | allow | موروث |

**ملاحظة:** `external_directory` في الإعداد العام مضبوط على `"*": allow` — أي أن كل الوكلاء يقرأون خارج المشروع. `task` غير مضبوط صراحةً في أي وكيل (موروث).

---

## 3. المبادئ غير القابلة للتفاوض

1. **لا commit في أي مرحلة** إلا بطلب صريح من المالك.
2. **الأرشيف للقراءة فقط** — لا تعديل داخل `.kilo/plans/archive/`.
3. **لا ملفات بديلة** — `.kilo/agents/` (جمع) ممنوع.
4. **حفظ محتوى `04_KILO_SETUP.md`** — لا حذف أقسام.
5. **`.kilo/kilo.jsonc` محلي** — لا يُستخدم كحامل إعداد مشترك.
6. **الدليل أولًا** — كل تعديل يُسند إلى سطر/ملف.
7. **بوابة موافقة إلزامية** بعد كل مرحلة.

---

## 4. المرحلة 1 — Rules

### الهدف
تفعيل القواعد عبر ملف **متتبَّع** (مشترك)، وحسم مصدر الحالة، دون تعديل الأرشيف ودون المساس بمحتوى `04_KILO_SETUP.md`، ودون الاعتماد على `AGENTS.md` المحمي.

### النطاق

| الملف | نوع | الإجراء |
|---|---|---|
| `kilo.json` (الجذر) | **جديد، متتبَّع** | إضافة `instructions` |
| `AGENTS.md` | متتبَّع، **محمي** | اختياري — بموافقة صريحة فقط |
| `.kilocode/00_README.md` | متتبَّع | تحديث خريطة الملفات |
| `.kilocode/04_KILO_SETUP.md` | متتبَّع | سطر حالة تاريخية واحد |
| `.kilo/command/forensic-audit.md` | متتبَّع | تصحيح مرجع مكسور |
| `.kilo/kilo.jsonc` | **محلي** | لا يُعتمد عليه |

### المهام

1. **إنشاء `kilo.json` في الجذر** (متتبَّع) بالحقول:
   ```json
   {
     "$schema": "https://app.kilo.ai/config.json",
     "instructions": [
       ".kilocode/NILE_KEY_RULES.md",
       ".kilocode/PATCH_WORKFLOW.md"
     ]
   }
   ```
   **لا** يُكتب في `.kilo/kilo.jsonc` لأنه مستثنى من Git (V1).

2. **`AGENTS.md` (اختياري، مؤجل):** لا يُدرج ضمن نطاق المرحلة إلا بطلب صريح. إن طُلب، يُملأ بـ loader موجز فقط. **معيار القبول لا يشترط امتلاءه** (V7).

3. **مصدر الحالة (تصحيح V2):**
   - `CURRENT_STATUS.md` = **فهرس حالة غير نهائي**، ويتعارض مع `PLAN.md` (D9 مفتوح).
   - المرجع المُعلن: `.kilo/plans/1789672443844-master-remediation-plan.md` + `.kilo/plans/1789733769109-commercial-readiness-completion.md`.
   - `.kilocode/SESSION_STATE.md` = **متوقف**، لا يُعتمد.
   - تُوثَّق هذه القاعدة في `00_README.md`، **لا** في `AGENTS.md`.

4. **`04_KILO_SETUP.md`:** إضافة سطر واحد أعلى الملف:
   `> **Status:** Historical environment snapshot. Verify against \`~/.config/kilo/kilo.jsonc\` before use.`
   مع الحفاظ على **كل العناوين السبعة** ومحتواها.

5. **مرجع مكسور:** `.kilo/command/forensic-audit.md:8` → `Read .kilocode/NILE_KEY_RULES.md and project rules`.

6. **`00_README.md`:** تحديث خريطة الملفات (الأسطر 6–25) لتشمل: `kilo.json` (جذر)، `AGENTS.md` (محمي)، وقاعدة أن `.kilo/kilo.jsonc` محلي.

### المخرجات
- `kilo.json` (جذر) مع `instructions`.
- `04_KILO_SETUP.md` + سطر حالة واحد.
- مرجع واحد مصحح.
- `00_README.md` محدَّث.

### معايير التحقق
- [ ] `Test-Path .\kilo.json` = True، وهو **غير مستثنى** (`git check-ignore` لا يعيد شيئًا).
- [ ] `kilo.json` صالح JSON ويحتوي `instructions`، وكل مسار في `instructions` **موجود** (`Test-Path`).
- [ ] `.kilo/kilo.jsonc` **لم يُعدَّل** (لا يحتوي `instructions`).
- [ ] `.kilocode/04_KILO_SETUP.md` لا يزال يحتوي **7 عناوين**、`poolside/malibu-2:free`، و`Mode Overrides`.
- [ ] `.kilo/plans/archive/` — `git status --short` نظيف.
- [ ] `forensic-audit.md` لا يحتوي `INSTRUCTIONS.md` ويحتوي `.kilocode/NILE_KEY_RULES.md`.
- [ ] `AGENTS.md` إما لم يُمس (الحالة الافتراضية) أو مُعدَّل بموافقة موثقة.
- [ ] `git status --short` يُظهر فقط: `kilo.json` (جديد)، `00_README.md`، `04_KILO_SETUP.md`، `forensic-audit.md` (+`AGENTS.md` إن طُلب).
- [ ] **لا commit** — `git log -1` لم يتغير.

### بوابة التوقف
⏸️ توقف إلزامي.

---

## 5. المرحلة 2 — Skills

### الهدف
مهارة مشروع واحدة صالحة + حسم اعتماد `data-investigation` المفقود.

### النطاق
- `.kilo/skills/<name>/SKILL.md` (جديد)
- `.kilo/command/incident-remediation.md` (تصحيح مرجع)

### المهام

1. **حسم اعتماد `data-investigation` (V9):**
   - الحالة: `~/.config/kilo/kilo.jsonc:211-213` يطلب المهارة، ولا وجود لها.
   - **قرار مطلوب من المالك:** (أ) إنشاء المهارة في `.kilo/skills/data-investigation/`، أو (ب) إزالة الاعتماد من الإعداد العام.
   - **التوصية:** (أ) إنشاء المهارة لأن `data` وكيل قائم، لكن **إزالتها من نطاق هذه المرحلة** إن لم تُعتمد.

2. **مهارة مشروع واحدة:** `.kilo/skills/supplier-data-audit/SKILL.md` — مُشتقة من `audit1.py`, `audit3.py`, `compare.py`, `build_excel_map.py`، `check_*.py` الموجودة في الجذر.
   - `frontmatter` إلزامي: `name` + `description`.
   - **حد أقصى مهارة واحدة** في هذه المرحلة.

3. **تصحيح مرجع:** `.kilo/command/incident-remediation.md:7` — `\`incident-remediation\` skill` ← `\`incident-remediation\` agent`.

### المخرجات
- `.kilo/skills/supplier-data-audit/SKILL.md`.
- قرار موثّق بشأن `data-investigation`.
- مرجع مصحح.

### معايير التحقق
- [ ] `Test-Path .kilo\skills\supplier-data-audit\SKILL.md` = True.
- [ ] `frontmatter` يحتوي `name` و`description` غير فارغين.
- [ ] عدد مجلدات `.kilo/skills/` = 1 (أو 2 إن اعتُمد `data-investigation`).
- [ ] لا `SKILL.md` داخل المستودع (عدا `node_modules`).
- [ ] `data-investigation`: إما موجود في مسار مهارات، أو أن الاعتماد في `kilo.jsonc` أُزيل — **لا حالة وسطى**.
- [ ] `incident-remediation.md` لا يصف الوكيل كـ skill.
- [ ] `git status` يُظهر فقط مسارات المهارة + `incident-remediation.md`.
- [ ] **لا commit.**

### بوابة التوقف
⏸️ توقف إلزامي.

---

## 6. المرحلة 3 — Workflows

### الهدف
سلسلة canonical + frontmatter صالح + نصوص خالية من commit التلقائي + فصل Completion عن commit.

### النطاق
- `.kilocode/PATCH_WORKFLOW.md`
- `.kilo/command/runtime-verification.md`
- `.kilo/command/forensic-audit.md`
- `.kilo/command/incident-remediation.md`
- `.kilo/command/commit-verification.md`

### المهام

1. **`runtime-verification.md` — تصحيح V3:**
   - السطر 4: `before any commit` ← `before declaring completion`.
   - السطر 9: `npm run typecheck` ← `npm run build` (لأن `build` = `tsc -b && vite build`).
   - السطر 10: `npm test` ← `npm test` (واجهة) / `pytest` (خلفية) — فصل المسارين.

2. **`incident-remediation.md` — إزالة commit:**
   - السطر 7: `Commit with single-purpose message` ← `Report completion with verification evidence`.
   - السطر 13: `Commit with single-purpose message` ← `Report completion with verification evidence`.
   - السطر 20: `Commit hash` ← `Verification evidence`.

3. **`commit-verification.md` — إعادة توصيف (V4):**
   - العنوان `# Commit Verification Workflow` يبقى، لكن يُعاد نصه:
     - الغرض: `Optional post-completion check. Runs only on explicit user request.`
     - السطر 6: `Commit only if all checks pass` ← `Report readiness; do not commit without explicit user request`.
   - **لا يُستدعى من السلسلة الأساسية.**

4. **`PATCH_WORKFLOW.md` — سلسلة + فصل Completion (V4):**

   | المرحلة | المسؤول |
   |---|---|
   | Planning | يدوي |
   | Investigation | `/forensic-audit` |
   | Repair Decision | موافقة مالك |
   | Repair | `/incident-remediation` |
   | Verification | `/runtime-verification` |
   | **Completion** | تقرير إغلاق + موافقة مالك (**بلا commit**) |

   **إجراء اختياري بعد Completion:** `/commit-verification` — **فقط بطلب صريح**، وبعد اكتمال المهمة.

5. **frontmatter لكل أمر:**
   ```yaml
   ---
   description: <وصف>
   agent: <وكيل موجود>
   ---
   ```
   - `runtime-verification` → `code`
   - `forensic-audit` → `forensic-audit`
   - `incident-remediation` → `incident-remediation`
   - `commit-verification` → `code`

6. **الأرشيف:** لا يُنشأ `WORKFLOW.md` ولا يُعدَّل `archive/WORKFLOW.md`.

### المخرجات
- 4 أوامر بـ frontmatter + نصوص مصححة.
- سلسلة canonical في `PATCH_WORKFLOW.md`.
- `/commit-verification` اختياري بعد Completion.

### معايير التحقق
- [ ] كل أمر يبدأ بـ `---` ويحتوي `description`.
- [ ] كل `agent:` يطابق وكيلًا موجودًا.
- [ ] `runtime-verification.md` لا يحتوي `typecheck` ويحتوي `npm run build`.
- [ ] لا ملف في `.kilo/command/` يحتوي جملة commit تلقائي (`Commit with`, `Commit only`).
- [ ] `PATCH_WORKFLOW.md` يذكر Completion **بلا commit**، و`/commit-verification` كإجراء اختياري.
- [ ] عدد أوامر `.kilo/command/` = 4 (كما هو).
- [ ] `git status` على `.kilo/plans/archive/` نظيف.
- [ ] **لا commit.**

### بوابة التوقف
⏸️ توقف إلزامي.

---

## 7. المرحلة 4 — Agent Governance

### الهدف
حسم تعارض الوكلاء، توثيق أسبقية الدمج العميق، واعتماد كتلة صلاحيات **مشتركة** بعد مراجعة نهائية شاملة `task` و`external_directory`.

### النطاق
- `.kilo/agent/forensic-audit.md`, `.kilo/agent/incident-remediation.md` (متتبَّعة)
- `kilo.json` (الجذر — **مشترك**) للصلاحيات
- `.kilo/kilo.jsonc` (محلي) — **لا يُعتمد**
- `.kilo/plans/nile-key-agent-precedence.md` (جديد)
- `~/.config/kilo/kilo.jsonc` — قراءة فقط

### المهام

1. **توثيق الأسبقية (تصحيح V5):** وثيقة `nile-key-agent-precedence.md` تشرح:
   - الدمج العميق لا الاستبدال.
   - الحقل المحدَّد فقط يُستبدل.
   - الترتيب بين `.kilo/kilo.json` و`.kilo/agent/*.md` **غير مثبت** — يُشار إليه كافتراض قابل للانقلاب.

2. **حسم التعارض:** `.kilo/agent/*.md` يبقى canonical لمشروع Nile Key. الإصدارات العالمية (inline + `agents/`) تبقى للاستخدام العام ولا تُحذف. **منع `.kilo/agents/`.**

3. **مراجعة الصلاحيات النهائية (V6) — إلزامية قبل الاعتماد:**

   | البند | القيمة الحالية | الإجراء |
   |---|---|---|
   | `external_directory` | `"*": allow` (عام) | **تقييد** إلى مسارات المشروع + مسار محدد |
   | `task` | غير مضبوط (موروث) | **تحديد** صريح لكل وكيل |
   | `question` | مضبوط في 3 وكلاء فقط | **توحيد** لكل الوكلاء |
   | `mcp`, `plan_exit` | مضبوطان في وكلاء | **إزالة** أو توثيق كمهملين |

   **كتلة مقترحة (مشتركة، في `kilo.json` الجذر):**
   ```json
   "permission": {
     "read": "allow",
     "glob": "allow",
     "grep": "allow",
     "list": "allow",
     "skill": "allow",
     "lsp": "allow",
     "todowrite": "allow",
     "todoread": "allow",
     "websearch": "allow",
     "edit": { "*": "ask" },
     "bash": { "*": "ask" },
     "task": { "*": "ask" },
     "question": "allow",
     "external_directory": { "*": "ask" }
   }
   ```
   **أنماط غير متداخلة** لتجنّب تعارض "first/last match wins".

4. **سجل وكلاء:** جدول في وثيقة الحوكمة يطابق 1:1: الاسم، الوضع، الملف/المصدر، الصلاحيات، تاريخ الاعتماد.

5. **بوابة اعتماد:** لا وكيل جديد إلا بـ `description` + `mode` + `permission` + موافقة.

### المخرجات
- `.kilo/plans/nile-key-agent-precedence.md`.
- `permission` في `kilo.json` (الجذر).
- سجل وكلاء.

### معايير التحقق
- [ ] `Test-Path .kilo\agents` = False.
- [ ] كل وكيل في `.kilo/agent/` يملك `description` + `mode`.
- [ ] `kilo.json` (الجذر) صالح JSON ويحتوي `permission` + `instructions`.
- [ ] `.kilo/kilo.jsonc` **غير معدَّل** (لا صلاحيات فيه).
- [ ] لا `agent` inline في `kilo.json` (لأن `.kilo/agent/*.md` يسود).
- [ ] كل وكيل في السجل يقابله ملف/إعداد فعلي.
- [ ] `external_directory` ليس `"*": "allow"`.
- [ ] `task` مضبوط لكل وكيل.
- [ ] `~/.config/kilo/kilo.jsonc` **غير معدَّل** (`Get-FileHash` قبل/بعد).
- [ ] **لا commit.**

### بوابة التوقف
⏸️ نهاية الخطة. تقرير إغلاق + موافقة نهائية.

---

## 8. تنبيه قاعدة البيانات (V8)

**الحقائق:**

| السياق | القيمة | الدليل |
|---|---|---|
| مضيف (تطوير محلي) | `sqlite:///./nile_key.db` → `backend/nile_key.db` | `backend/app/core/config.py:19`؛ `backend/.env.example:5` |
| Docker | `DATABASE_URL=sqlite:////app/data/nile_key.db` | `docker-compose.yml:30` |
| مجلد Docker | `db-data:/app/data` (volume دائم) | `docker-compose.yml:32` |
| خدمة Postgres | معرَّفة لكن **غير مستخدمة** | `docker-compose.yml:2-19` (لا `DATABASE_URL` تشير إليها) |
| `.env` | موجود، مستثنى من Git | `.gitignore:11`؛ `env_file: .env` في السطر 28 |

**تحذيرات إلزامية:**
1. **قاعدتا بيانات مختلفتان:** `backend/nile_key.db` (مضيف) ≠ `/app/data/nile_key.db` (داخل الحاوية). أي تحقق يجب أن يحدد أيّهما.
2. **البيانات في الحاوية لا تُرى من المضيف** — الفحص من الداخل يتطلب `docker compose exec backend ...`.
3. **`environment:` يتجاوز `env_file:`** — السطر 30 يفرض sqlite داخل الحاوية حتى لو غيّر `.env`.
4. **`docker compose down -v` يحذف `db-data`** — فقدان بيانات دائم.
5. **خدمة Postgres غير مستخدمة** حاليًا — لا تُستخدم كمرجع للتحقق.

---

## 9. المخاطر

| الخطر | الأثر | التخفيف |
|---|---|---|
| `.kilo/kilo.jsonc` مستثنى من Git | إعداد غير مشترك | استخدام `kilo.json` الجذر (V1) |
| `AGENTS.md` محمي | رفض تعديل | تأجيله خارج نطاق إلزامي (V7) |
| تعارض D9 مفتوح | قرارات حالة خاطئة | `CURRENT_STATUS` فهرس غير نهائي (V2) |
| `task`/`external_directory` غير مضبوطين | صلاحيات أوسع من اللازم | مراجعة صريحة قبل الكتلة (V6) |
| تعارض ترتيب قواعد الصلاحيات | سلوك غير متوقع | أنماط غير متداخلة |
| تعديل الأرشيف | فقدان سجل | حظر + تحقق `git status` |
| commit تلقائي | خرق §10 | حظر + تحقق `git log -1` |

---

## 10. النطاق المستبعد

- أي تعديل على `backend/` أو `frontend/`.
- أي تعديل على `~/.config/kilo/**`.
- أي تعديل على `.kilo/plans/archive/**`.
- أي معالجة للقيود الجغرافية للنموذج.
- أي تنفيذ فعلي — هذه الخطة إعداد فقط.

---

## 11. أوامر التحقق (قراءة فقط)

```powershell
# 1. حالة kilo.jsonc (محلي)
git check-ignore -v .kilo/kilo.jsonc
git ls-files .kilo/kilo.jsonc

# 2. المسارات
Test-Path .\kilo.json
Select-String -Path .\kilo.json -Pattern "instructions"

# 3. عناوين 04_KILO_SETUP
(Select-String -Path .kilocode\04_KILO_SETUP.md -Pattern "^#{1,6} " | Measure-Object).Count

# 4. الأرشيف
git status --short -- .kilo/plans/archive

# 5. الوكلاء
Test-Path .kilo\agents
Get-ChildItem .kilo\agent -File

# 6. frontmatter
Get-Content .kilo\command\runtime-verification.md -TotalCount 6

# 7. لا commit
git log -1 --oneline
```

---

## 12. سجل القرارات

| # | القرار | الحالة |
|---|---|---|
| D1 | `.kilocode/` canonical، والتفعيل عبر `instructions` في **`kilo.json` الجذر** (متتبَّع) | **معتمد** — V1 |
| D2 | `.kilo/kilo.jsonc` محلي فقط — لا يُستخدم كحامل إعداد مشترك | **معتمد** — V1 |
| D3 | `04_KILO_SETUP.md` يُحفظ محتواه + سطر حالة واحد | **معتمد** — V10 |
| D4 | `.kilocode/SESSION_STATE.md` متوقف | **معتمد** |
| D5 | `CURRENT_STATUS.md` **فهرس غير نهائي** | **معتمد** — V2 |
| D6 | `.kilo/plans/archive/**` للقراءة فقط | **معتمد** |
| D7 | `.kilo/agent/` (مفرد) canonical؛ `.kilo/agents/` (جمع) ممنوع | **معتمد** |
| D8 | مهارة مشروع واحدة كحد أقصى في Phase 2 | **معتمد** |
| D9 | تعارض `PLAN.md` ↔ `CURRENT_STATUS.md` | **مفتوح** |
| D10 | `AGENTS.md` خارج النطاق الإلزامي (محمي) | **معتمد** — V7 |
| D11 | لا commit في أي مرحلة | **معتمد** |
| D12 | `/commit-verification` اختياري بعد Completion | **معتمد** — V4 |
| D13 | `task` و`external_directory` يُراجعان قبل كتلة الصلاحيات | **معتمد** — V6 |
| D14 | `data-investigation`: إنشاء أو إزالة الاعتماد | **مفتوح** — V9 |
| D15 | ترتيب `.kilo/kilo.json` مقابل `.kilo/agent/*.md` | **غير مثبت** — يُتحقق في Phase 4 |

---

## 13. ملخص تنفيذي

| المرحلة | الهدف | الملفات | البوابة |
|---|---|---|---|
| 1. Rules | تفعيل عبر `kilo.json` الجذر + حسم مصدر الحالة | `kilo.json`, `00_README.md`, `04_KILO_SETUP.md`, `forensic-audit.md` | موافقة |
| 2. Skills | مهارة واحدة + حسم `data-investigation` | `.kilo/skills/…/SKILL.md`, `incident-remediation.md` | موافقة |
| 3. Workflows | سلسلة + frontmatter + نصوص بلا commit | `.kilocode/PATCH_WORKFLOW.md`, `.kilo/command/*.md` | موافقة |
| 4. Agent Governance | دمج عميق موثّق + كتلة صلاحيات مُعتمدة | `kilo.json`, `.kilo/agent/*.md`, `nile-key-agent-precedence.md` | إغلاق |

**القاعدة النهائية:** لا يُنفَّذ أي تعديل الآن. التنفيذ يبدأ بمرحلة واحدة بعد موافقة المالك، ولا commit في أي مرحلة.