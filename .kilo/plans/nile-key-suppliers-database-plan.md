# خطة بناء قاعدة بيانات الموردين داخل Nile Key

## الاسم
nile-key-suppliers-database-plan.md

## المسار
.kilo/plans/nile-key-suppliers-database-plan.md

---

## 1. الهدف الرئيسي

بناء قاعدة بيانات موثوقة لشركات ومحطات تعبئة ومزارع
الخضروات والفاكهة في مصر، وإدخال بياناتها مباشرة
إلى قسم الموردين داخل Nile Key.

الهدف النهائي هو فتح Nile Key والعثور على بيانات
الموردين قد أُضيفت بالفعل، مع إمكانية تتبع مصدر
كل معلومة والتحقق من حالة اعتماد المنشأة.

لا نريد إنشاء قاعدة بيانات موازية.
ولا نريد اعتماد Excel باعتباره وسيطًا إلزاميًا
لإدخال البيانات.

---

## 2. مصادر البيانات المعتمدة

### الطبقة الأولى: الجهات الحكومية المصرية

1. CAPQ – الحجر الزراعي المصري.
   المصدر الأول والأولوية الأولى.

2. NFSA – الهيئة القومية لسلامة الغذاء.
   المصدر الثاني.

### الطبقة الثانية: جهات الاعتماد والتحقق الدولية

3. جهات الاعتماد الرقابية في دول الخليج.
4. جهات الاعتماد الرقابية في الدول العربية الأخرى.
5. جهات الاعتماد الرقابية الأوروبية.

الصين مستبعدة من نطاق المشروع الحالي.

### الطبقة الثالثة

GLOBALG.A.P.

للتحقق من شهادات المزارع ومحطات التعامل
مع المنتجات بعد الحصاد، مع التمييز بين
أنواع الشهادات ونطاق كل شهادة.

### الطبقة الرابعة

مصادر اكتشاف الموردين الإضافيين:

- Expo Egypt.
- HEIA.
- الأدلة المتخصصة للموردين ومحطات التعبئة.

هذه المصادر لا تثبت الاعتماد الحكومي بذاتها،
ويجب التحقق من المنشآت التي يتم اكتشافها.

---

## 3. قواعد البيانات التي يجب مراعاتها

يجب التمييز بين:

- الشركة.
- محطة التعبئة.
- المزرعة.

يجب أن تسمح البنية بارتباط شركة واحدة
بعدة محطات تعبئة، مع الاحتفاظ بالكود المستقل
لكل محطة.

يجب الاحتفاظ ببيانات:

- اسم المنشأة.
- نوع المنشأة.
- الشركة المالكة أو المرتبطة بها.
- كود المحطة.
- المحافظة والعنوان.
- المحاصيل.
- الموسم.
- جهة الاعتماد.
- تاريخ الاعتماد والصلاحية.
- المستند الأصلي.
- رقم الصفحة أو موضع السجل.
- مصدر البيانات.
- حالة التحقق.

يجب أن تدعم البنية تسجيل عدة اعتمادات
للمنشأة نفسها دون دمجها أو فقدان تواريخها.

يجب التمييز بين الاعتماد الحالي والاعتماد السابق
والبيانات التي لم يتم التحقق منها.

---

## 4. مراحل المشروع وترتيبها

### المرحلة 1
تدقيق قسم الموردين وفهم بنيته الحالية.

**الحالة:** مكتملة.

**نتيجة التدقيق:**
قسم المورains فارغ.
النموذج الحالي لا يدعم جميع متطلبات CAPQ.
توجد أنماط سابقة لتوثيق مصادر البيانات
في قسم العملاء يمكن دراستها وإعادة استخدامها.

### المرحلة 2
تهيئة قسم المورains لاستقبال بيانات CAPQ،
بأقل تعديلات هندسية ضرورية.

**الحالة:** مكتملة.

**النتيجة:**
- جدول `suppliers` موسع (facility_type, station_code, province, parent_company_id, data_status, verification_status).
- جدول `supplier_accreditations` منشأ (15 حقلًا، مصادر متعددة، تواريخ، صلاحية، مستند، صفحة).
- جدول `supplier_accreditation_crops` منشأ (محاصيل منظمة، قابلة للبحث).
- قيد UNIQUE جزئي على `station_code`.
- SchemaRegistry محدّث.
- واجهة المورains محدثة (حقول، فلاتر، اعتمادات، إضافة/تعديل/حذف/تحقق).
- 25 اختبار Backend + Frontend build + live DB تحقق.
- حقل `season` موحد (مصدر وحيد: `supplier_accreditations.season`).

### المرحلة 3
جمع قوائم CAPQ واستخراج بياناتها والتحقق منها
وإدخالها مباشرة إلى قسم المورains.

**الحالة:** جاهزة للتنفيذ (Stage 2 مكتمل).

#### 3.1 تحديد المصادر الرسمية

- **CAPQ (الحجر الزراعي المصري)** — المصدر الأول والأولوية الأولى.
  - source_type = `'CAPQ'`
  - مستندات رسمية: قوائم محطات التعبئة المعتمدة (PDF/HTML).
  - **مهم:** لا تفترض توفر روابط или مسارات محددة؛ تحقق من توفرها فعليًا قبل الاعتماد.
  - **مهم:** تفضيل الأدوات المجانية (wget, curl, Python requests) دون اشتراكات مدفوعة.
- **NFSA** — المصدر الثاني (المرحلة 4، مستقلة).
- **Gulf regulatory bodies** — المرحلة 5.
- **Other Arab regulatory bodies** — المرحلة 6.
- **European regulatory bodies** — المرحلة 7.
- **GLOBALG.A.P.** — المرحلة 8 (للتحقق من شهادات المزارع/المحطات).
- **Expo Egypt / HEIA / specialized directories** — المرحلة 9 (اكتشاف، لا تثبت اعتمادًا).

**China خارج النطاق.**

#### 3.2 حفظ دفعات الاستيراد

- إنشاء جدول `supplier_source_batches` (إعادة استخدام نمط `customer_source_batches`):
  - `id`, `source_type`, `source_format`, `source_name`, `source_reference`, `source_url`, `file_name`, `row_count`, `success_count`, `skip_count`, `error_count`, `status` (preview/reviewed/confirmed/cancelled/expired), `mapping_metadata`, `imported_at`, `imported_by`, `expires_at`, `created_at`.
- كل دفعة CAPQ تحفظ: اسم المستند، تاريخ الحصول، رابط/مرجع، عدد السجلات، حالة المعالجة.
- إمكانية الرجوع إلى المستند الأصلي لاحقًا (source_url / file_name).

#### 3.3 تخزين السجلات الخام

- إنشاء جدول `supplier_raw_records` (إعادة استخدام نمط `customer_raw_records`):
  - `id`, `batch_id` (FK), `sheet_name`, `row_number`, `raw_data` (JSON), `normalized_supplier_id`, `validation_errors`, `conflict_resolution`, `conflict_details`, `created_at`.
- **القاعدة:** حفظ النص الأصلي لكل سجل، ورقم الصفحة أو الصف أو موضعه في المصدر. لا استبدال للبيانات الخام بالبيانات المنظمة.

#### 3.4 استخراج البيانات والتحقق منها

البيانات المطلوبة من CAPQ:

| الحقل | الوجهة في DB | ملاحظة |
|---|---|---|
| اسم المحطة | `suppliers.name` | |
| كود المحطة | `suppliers.station_code` | UNIQUE (partial) |
| الشركة المالكة | `suppliers.parent_company_id` → company row | إنشاء company row إذا لم يكن موجودًا |
| المحافظة | `suppliers.province` | |
| العنوان/الموقع | `suppliers.address`, `suppliers.city` | |
| المحاصيل المعتمدة | `supplier_accreditations.scope` + `supplier_accreditation_crops.crop_name` | |
| الموسم | `supplier_accreditations.season` | |
| جهة الاعتماد | `supplier_accreditations.source_type` = 'CAPQ', `accrediting_body` = 'CAPQ' | |
| تاريخ الاعتماد | `supplier_accreditations.accreditation_date` | ISO date |
| صلاحية الاعتماد | `supplier_accreditations.validity_date` | ISO date |
| المستند الأصلي | `supplier_accreditations.source_document` | اسم المستند/URL |
| رقم الصفحة | `supplier_accreditations.source_page` | |
| مرجع إضافي | `supplier_accreditations.source_reference` | |
| حالة التحقق | `suppliers.data_status` = 'raw', `verification_status` = 'unverified' | |
| حالة الاعتماد | `supplier_accreditations.status` = 'unverified' (default) | لا يصبح 'current' دون verify |

**قواعد:**
- المعلومات غير الموجودة أو غير الواضحة تظل فارغة أو معلّمة للمراجعة. لا تخمين.
- `facility_type`: 'packing_station' (CAPQ lists stations). 'company' if a separate company entity. 'farm' if farm.
- التمييز بين تسجيل المنشأة واعتمادها: `suppliers` (entity) + `supplier_accreditations` (accreditation).

#### 3.5 مطابقة السجلات ومنع التكرار

**مطابقة (Deduplication):**
- أولاً: `station_code` (إذا توفر).
- ثانياً: `name` + `province` (normalized).
- ثالثاً: `name` + `parent_company_id` (if company known).

**قواعد التعارض:**
- سجل جديد: إنشاء supplier + accreditation.
- سجل موجود (تطابق station_code): إضافة accreditation جديدة (لا استبدال). Mark conflict in raw_records.
- تكرار داخل المستند: mark as duplicate in raw_records, skip creation.
- اختلاف البيانات بين مصدرين: الاحتفاظ بالسجلين (لا دمج تلقائي). Mark conflict.
- سجلات متشابهة غير محسومة: تحويل للمراجعة البشرية (conflict_resolution = 'manual_review').

**ممنوع:** الدمج أو الحذف التلقائي عند وجود تعارض أو غموض.

#### 3.6 المراجعة قبل الإدخال النهائي

- واجهة مراجعة (reuse customer import_review pattern) تسمح بـ:
  - فحص السجلات الخام (raw_data).
  - مقارنتها بالمصادر الأصلية (source_document, source_page).
  - قبول/رفض/تصحيح.
  - الاحتفاظ بأثر المراجعة (conflict_resolution, validation_errors).
- States: preview → reviewed → confirmed / cancelled / expired.

#### 3.7 الإدخال إلى قاعدة المورains

- تحويل السجلات المقبولة إلى:
  - companies (facility_type='company') — إذا وُجد كيان شركة.
  - packing stations (facility_type='packing_station', parent_company_id) — من CAPQ.
  - farms (facility_type='farm') — إذا ثُبت.
  - accreditations (supplier_accreditations) — مع source, scope (crops), season, dates, status='unverified'.
- `data_status='raw'`, `verification_status='unverified'` initially.
- `accreditation.status='unverified'` (لا يصبح 'current' دون verify).

---

### المرحلة 4
جمع قوائم NFSA ومطابقتها مع سجلات CAPQ،
مع الحفاظ على مصدر كل معلومة واعتماد مستقل.

### المرحلة 5
التحقق من الجهات الرقابية في دول الخليج.

### المرحلة 6
التحقق من الجهات الرقابية في الدول العربية الأخرى.

### المرحلة 7
التحقق من الجهات الرقابية الأوروبية.

### المرحلة 8
التحقق من شهادات GLOBALG.A.P.

### المرحلة 9
اكتشاف مورains إضافيين من المصادر التجارية
والجمعيات المتخصصة، ثم التحقق من اعتمادهم.

### المرحلة 10
مراجعة شمول قاعدة البيانات ودقتها
واستكمال إدخال السجلات المؤهلة.

---

filePath">
F:\nilekey\nile-key-project\nile-key22\.kilo\plans\stages_4_10.md

## 5. قواعد التنفيذ الملزمة

1. الالتزام بالترتيب المعتمد للمراحل.

2. عدم الانتقال إلى مرحلة قبل استكمال متطلبات المرحلة السابقة والتحقق من نتائجها.

3. عدم إدخال منشأة باعتبارها معتمدة دون دليل يثبت جهة اعتمادها ونطاق الاعتماد وتاريخه.

4. عدم تخمين البيانات غير الواضحة.

5. عدم دمج الشركات ومحطات التعبئة والمزارع في كيان واحد يفقد العلاقات بينها.

6. عدم حذف السجلات المكررة من المصادر تلقائيًا؛ بل مراجعتها وتحديد ما إذا كانت تمثل المنشأة نفسها أم مواقع مستقلة.

7. الاحتفاظ بمصدر كل سجل وإمكانية الرجوع إليه.

8. تفضيل الأدوات المجانية والحلول المحلية دون اشتراكات أو أرصدة مدفوعة.

9. عدم إجراء تغييرات لا تخدم مباشرة بناء قاعدة بيانات المورains.

10. عدم توسيع نطاق المشروع خارج الهدف المحدد.

---

## 6. قواعد هذه المهمة (الخطة)

المطلوب إنشاء وثيقة الخطة فقط.

- لا تنفيذ أي مرحلة من مراحل المشروع.
- لا تعديل كود التطبيق.
- لا تعديل قاعدة البيانات.
- لا تنفيذ Migrations.
- لا إضافة بيانات مورains.
- لا تغيير واجهة المستخدم.
- لا إنشاء ملفات خارج `.kilo/plans`.

---

## 7. النتيجة المطلوبة

الخطة الرئيسية محفوظة في:

`.kilo/plans/nile-key-suppliers-database-plan.md`

يجب أن تكون الخطة واضحة ومرتبة وقابلة للرجوع
إليها طوال مراحل المشروع.
filePath">
F:\nilekey\nile-key-project\nile-key22\.kilo\plans\nile-key-suppliers-database-plan.md