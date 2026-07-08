# Manual UAT Execution Package - WP-18

**Version:** 2.0
**Generated:** 2026-07-06
**Baseline:** baseline-wp18
**Governing Document:** PROJECT_EXECUTION_RULES.md §§16-18

---

## Test Environment Fields

| Field | Value (to be filled by executor) |
|-------|--------------------------------|
| تاريخ الاختبار | |
| إصدار المشروع | 1.1.0-MVP |
| قاعدة البيانات المستخدمة | SQLite (`nile_key.db`) |
| المتصفح | |
| نظام التشغيل | |
| اسم المختبر | |

---

## Evidence Requirements

For **every** scenario, collect:

1. **Browser Screenshot** - Full page showing the result
2. **Browser Network Tab** - Screenshot of API request/response
3. **Browser Console** - Screenshot showing no errors
4. **Backend Logs** - When applicable (terminal output during request)

Evidence files naming convention: `uat-{scenario-id}-{evidence-type}.{ext}` (e.g., `uat-auth-01-screenshot.png`)

---

## Execution Order

### Phase 1: Authentication (Critical Path)
- AUTH-01 through AUTH-20

### Phase 2: Dashboard
- DASH-21 through DASH-27

### Phase 3: Suppliers
- SUPP-28 through SUPP-46

### Phase 4: Customers
- CUST-47 through CUST-71

### Phase 5: Shipments
- SHIP-72 through SHIP-87

### Phase 6: Invoices
- INV-88 through INV-109

### Phase 7: Customs
- CUSTMS-110 through CUSTMS-130

### Phase 8: Documents
- DOC-131 through DOC-150

### Phase 9: Resources
- RES-151 through RES-172

### Phase 10: Profile
- PROF-173 through PROF-181

### Phase 11: API Endpoints
- API-182 through API-187

### Phase 12: Security (Regression)
- SEC-188 through SEC-204

### Phase 13: Performance
- PERF-205 through PERF-218

### Phase 14: UI / UX
- UX-219 through UX-241

---

## Full Scenario Matrix

| ID | Section | Scenario | Pass/Fail | Notes | Evidence Files |
|----|---------|----------|-----------|-------|--------------|
| AUTH-01 | Authentication-Login | تسجيل الدخول عبر `/login` ببيانات صحيحة ينجح | ☐ | | |
| AUTH-02 | Authentication-Login | تسجيل الدخول ببيانات خاطئة يعرض رسالة خطأ واضحة | ☐ | | |
| AUTH-03 | Authentication-Login | الحقول المطلوبة (username / password) تُValidate | ☐ | | |
| AUTH-04 | Authentication-Login | زر الإظهار/الإخفاء لكلمة المرور يعمل (إن وُجد) | ☐ | | |
| AUTH-05 | Authentication-Login | التوجيه التلقائي بعد نجاح تسجيل الدخول إلى `/` | ☐ | | |
| AUTH-06 | Authentication-Logout | تسجيل الخروج من القائمة الجانبية يعمل | ☐ | | |
| AUTH-07 | Authentication-Logout | إزالة التوكن من التخزين المحلي بعد تسجيل الخروج | ☐ | | |
| AUTH-08 | Authentication-Logout | التوجيه بعد تسجيل الخروج إلى `/login` | ☐ | | |
| AUTH-09 | Authentication-Credentials | اسم مستخدم غير موجود يعرض رسالة خطأ | ☐ | | |
| AUTH-10 | Authentication-Credentials | كلمة مرور خاطئة تعرض رسالة خطأ | ☐ | | |
| AUTH-11 | Authentication-Credentials | الحساب غير المفعل لا يمكنه تسجيل الدخول | ☐ | | |
| AUTH-12 | Authentication-Credentials | _rate limiting أو تأخير في الاستجابة (إن مطبق) | ☐ | | |
| AUTH-13 | Authentication-Session | تحديث الصفحة يحافظ على حالة تسجيل الدخول | ☐ | | |
| AUTH-14 | Authentication-Session | إعادة فتح المتصفح يحافظ على الجلسة (حسب إعدادات expires) | ☐ | | |
| AUTH-15 | Authentication-Session | التوكن يُخزن في `localStorage` بشكل صحيح | ☐ | | |
| AUTH-16 | Authentication-Token | انتهاء صلاحية `access_token` يُعيد التوجيه إلى `/login` | ☐ | | |
| AUTH-17 | Authentication-Token | `refresh_token` يعيد إنشاء `access_token` تلقائياً | ☐ | | |
| AUTH-18 | Authentication-Token | انتهاء صلاحية `refresh_token` يُعيد التوجيه إلى `/login` | ☐ | | |
| AUTH-19 | Authentication-Security | الوصول المباشر إلى `/` بدون تسجيل دخول يوجه إلى `/login` | ☐ | | |
| AUTH-20 | Authentication-Security | الوصول المباشر إلى أي صفحة محمية بدون Token يوجه إلى `/login` | ☐ | | |
| DASH-21 | Dashboard | الصفحة تفتح بدون أخطاء | ☐ | | |
| DASH-22 | Dashboard | تحميل بيانات الإحصائيات ( suppliers / customers / shipments / invoices ) | ☐ | | |
| DASH-23 | Dashboard | عدم وجود أخطاء Console | ☐ | | |
| DASH-24 | Dashboard | عدم وجود أخطاء Network | ☐ | | |
| DASH-25 | Dashboard | عرض البطاقات الإحصائية بشكل صحيح | ☐ | | |
| DASH-26 | Dashboard | عرض كتابع "Platform v1.0" بشكل صحيح | ☐ | | |
| DASH-27 | Dashboard | حالة التحميل (Loading spinner) تظهر أثناء جلب البيانات | ☐ | | |
| SUPP-28 | Suppliers-List | عرض قائمة الموردين | ☐ | | |
| SUPP-29 | Suppliers-List | عرض أعمدة: الاسم، جهة الاتصال، البريد، الهاتف، المدينة، الحالة، إجراءات | ☐ | | |
| SUPP-30 | Suppliers-List | حالة فارغة تظهر عند عدم وجود بيانات | ☐ | | |
| SUPP-31 | Suppliers-Search | البحث بالاسم يعمل | ☐ | | |
| SUPP-32 | Suppliers-Search | زر البحث يعيد تحميل القائمة | ☐ | | |
| SUPP-33 | Suppliers-Search | الضغط على Enter يعيد تحميل القائمة | ☐ | | |
| SUPP-34 | Suppliers-Create | فتح نموذج إضافة مورد | ☐ | | |
| SUPP-35 | Suppliers-Create | إضافة مورد جديد يعمل | ☐ | | |
| SUPP-36 | Suppliers-Create | التحقق من الحقول المطلوبة (الاسم مطلوب) | ☐ | | |
| SUPP-37 | Suppliers-Create | إغلاق النموذج بعد الحفظ | ☐ | | |
| SUPP-38 | Suppliers-Create | تحديث القائمة تلقائياً بعد الحفظ | ☐ | | |
| SUPP-39 | Suppliers-Edit | زر التعديل يفتح النموذج بالبيانات الحالية | ☐ | | |
| SUPP-40 | Suppliers-Edit | تعديل مورد يعمل | ☐ | | |
| SUPP-41 | Suppliers-Edit | تحديث القائمة تلقائياً بعد الحفظ | ☐ | | |
| SUPP-42 | Suppliers-Delete | تأكيد الحذف يظهر | ☐ | | |
| SUPP-43 | Suppliers-Delete | حذف مورد يعمل | ☐ | | |
| SUPP-44 | Suppliers-Delete | تحديث القائمة تلقائياً بعد الحذف | ☐ | | |
| SUPP-45 | Suppliers-Validation | الاسم مطلوب | ☐ | | |
| SUPP-46 | Suppliers-Validation | البريد الإلكتروني يخضع للتحقق من الصيغة (إن وُجد) | ☐ | | |
| SUPP-47 | Suppliers-Empty | عرض "No Data" عند عدم وجود موردين | ☐ | | |
| SUPP-48 | Suppliers-Loading | عرض Spinner أثناء تحميل البيانات | ☐ | | |
| CUST-49 | Customers-List | عرض قائمة العملاء | ☐ | | |
| CUST-50 | Customers-List | عرض أعمدة: الاسم، جهة الاتصال، البريد، الدولة، الفئة، الحالة، إجراءات | ☐ | | |
| CUST-51 | Customers-List | حالة فارغة تظهر عند عدم وجود بيانات | ☐ | | |
| CUST-52 | Customers-Search | البحث بالاسم يعمل | ☐ | | |
| CUST-53 | Customers-Search | زر البحث يعيد تحميل القائمة | ☐ | | |
| CUST-54 | Customers-Create | فتح نموذج إضافة عميل | ☐ | | |
| CUST-55 | Customers-Create | إضافة عميل جديد يعمل | ☐ | | |
| CUST-56 | Customers-Create | التحقق من الحقول المطلوبة (الاسم، الدولة) | ☐ | | |
| CUST-57 | Customers-Create | إغلاق النموذج بعد الحفظ | ☐ | | |
| CUST-58 | Customers-Create | تحديث القائمة تلقائياً بعد الحفظ | ☐ | | |
| CUST-59 | Customers-Edit | زر التعديل يفتح النموذج بالبيانات الحالية | ☐ | | |
| CUST-60 | Customers-Edit | تعديل عميل يعمل | ☐ | | |
| CUST-61 | Customers-Edit | تحديث القائمة تلقائياً بعد الحفظ | ☐ | | |
| CUST-62 | Customers-Delete | تأكيد الحذف يظهر | ☐ | | |
| CUST-63 | Customers-Delete | حذف عميل يعمل | ☐ | | |
| CUST-64 | Customers-Delete | تحديث القائمة تلقائياً بعد الحذف | ☐ | | |
| CUST-65 | Customers-CSV | زر رفع CSV يظهر | ☐ | | |
| CUST-66 | Customers-CSV | اختيار ملف CSV يعمل | ☐ | | |
| CUST-67 | Customers-CSV | استيراد العملاء يعمل | ☐ | | |
| CUST-68 | Customers-CSV | عرض رسالة نجاح/فشل الاستيراد | ☐ | | |
| CUST-69 | Customers-Validation | الاسم مطلوب | ☐ | | |
| CUST-70 | Customers-Validation | الدولة مطلوبة | ☐ | | |
| CUST-71 | Customers-Validation | البريد الإلكتروني يخضع للتحقق من الصيغة (إن وُجد) | ☐ | | |
| SHIP-72 | Shipments-List | عرض قائمة الشحنات | ☐ | | |
| SHIP-73 | Shipments-List | عرض أعمدة: رقم التتبع، المنشأ، الوجهة، الناقل، الحالة، إجراءات | ☐ | | |
| SHIP-74 | Shipments-List | حالة فارغة تظهر عند عدم وجود بيانات | ☐ | | |
| SHIP-75 | Shipments-Create | فتح نموذج إضافة شحنة | ☐ | | |
| SHIP-76 | Shipments-Create | إنشاء شحنة جديدة يعمل | ☐ | | |
| SHIP-77 | Shipments-Create | الحقول المطلوبة: المنشأ، الوجهة | ☐ | | |
| SHIP-78 | Shipments-Create | إغلاق النموذج بعد الحفظ | ☐ | | |
| SHIP-79 | Shipments-Create | تحديث القائمة تلقائياً بعد الحفظ | ☐ | | |
| SHIP-80 | Shipments-Edit | زر التعديل يفتح النموذج بالبيانات الحالية | ☐ | | |
| SHIP-81 | Shipments-Edit | تعديل شحنة يعمل | ☐ | | |
| SHIP-82 | Shipments-Rates | زر "Get Rates" يظهر | ☐ | | |
| SHIP-83 | Shipments-Rates | نموذج حساب Rates يظهر | ☐ | | |
| SHIP-84 | Shipments-Rates | إدخال المنشأ والوجهة والوزن يعمل | ☐ | | |
| SHIP-85 | Shipments-Rates | حساب Rates يعرض النتائج | ☐ | | |
| SHIP-86 | Shipments-Rates | عرض الناقل، الخدمة، التكلفة، الأيام المتوقعة | ☐ | | |
| SHIP-87 | Shipments-Tracking | الرابط `/api/v1/shipping/track/{tracking_id}` يعمل | ☐ | | |
| SHIP-88 | Shipments-Tracking | عرض حالة الشحنة (إن متاح من الـ API) | ☐ | | |
| SHIP-89 | Shipments-Label | الرابط `/api/v1/shipping/shipments/{id}/label` يعمل | ☐ | | |
| SHIP-90 | Shipments-Label | تحميل الملصق كملف PDF (إن متاح من الـ API) | ☐ | | |
| INV-91 | Invoices-List | عرض قائمة الفواتير | ☐ | | |
| INV-92 | Invoices-List | عرض أعمدة: رقم الفاتورة، المجموع الفرعي، الضريبة، الإجمالي، تاريخ الإصدار، الحالة، إجراءات | ☐ | | |
| INV-93 | Invoices-List | حالة فارغة تظهر عند عدم وجود بيانات | ☐ | | |
| INV-94 | Invoices-Create | فتح نموذج إضافة فاتورة | ☐ | | |
| INV-95 | Invoices-Create | إنشاء فاتورة جديدة يعمل | ☐ | | |
| INV-96 | Invoices-Create | إضافة عناصر الفاتورة (Items) يعمل | ☐ | | |
| INV-97 | Invoices-Create | حساب الإجمالي تلقائياً | ☐ | | |
| INV-98 | Invoices-Create | إغلاق النموذج بعد الحفظ | ☐ | | |
| INV-99 | Invoices-Create | تحديث القائمة تلقائياً بعد الحفظ | ☐ | | |
| INV-100 | Invoices-Edit | زر التعديل يفتح النموذج بالبيانات الحالية | ☐ | | |
| INV-101 | Invoices-Edit | تعديل فاتورة يعمل (حالة Draft فقط) | ☐ | | |
| INV-102 | Invoices-Edit | تحديث القائمة تلقائياً بعد الحفص | ☐ | | |
| INV-103 | Invoices-Validate | زر اعتماد الفاتورة يظهر (حالة Draft فقط) | ☐ | | |
| INV-104 | Invoices-Validate | اعتماد الفاتورة يعمل | ☐ | | |
| INV-105 | Invoices-Validate | تغيير الحالة إلى `validated` بعد الاعتماد | ☐ | | |
| INV-106 | Invoices-Cancel | زر إلغاء الفاتورة يظهر (ليس للفواتير الملغاة) | ☐ | | |
| INV-107 | Invoices-Cancel | تأكيد الإلغاء يظهر | ☐ | | |
| INV-108 | Invoices-Cancel | إلغاء الفاتورة يعمل | ☐ | | |
| INV-109 | Invoices-Cancel | تغيير الحالة إلى `cancelled` بعد الإلغاء | ☐ | | |
| INV-110 | Invoices-Details | النقر على الفاتورة يفتح modal التفاصيل | ☐ | | |
| INV-111 | Invoices-Details | عرض تفاصيل الفاتورة بشكل صحيح | ☐ | | |
| INV-112 | Invoices-Details | إغلاق الـ Modal يعمل | ☐ | | |
| CUSTMS-113 | Customs-HS | عرض قاعدة بيانات أكواد HS | ☐ | | |
| CUSTMS-114 | Customs-HS | عرض الأعمدة: الكود، الوصف، معدل الرسوم، معدل الضريبة | ☐ | | |
| CUSTMS-115 | Customs-HS | البحث في أكواد HS يعمل | ☐ | | |
| CUSTMS-116 | Customs-HS | حالة فارغة تظهر عند عدم وجود بيانات | ☐ | | |
| CUSTMS-117 | Customs-Duty | زر "Calculate Duties" يظهر | ☐ | | |
| CUSTMS-118 | Customs-Duty | نموذج حساب الرسوم يظهر | ☐ | | |
| CUSTMS-119 | Customs-Duty | إدخال كود HS والقيمة والعملة والوجهة يعمل | ☐ | | |
| CUSTMS-120 | Customs-Duty | حساب الرسوم يعرض: Duty Rate, Duty Amount, Tax Amount, Total | ☐ | | |
| CUSTMS-121 | Customs-Duty | عرض النتائج بشكل صحيح | ☐ | | |
| CUSTMS-122 | Customs-Declarations | عرض قائمة التصاريح الجمركية | ☐ | | |
| CUSTMS-123 | Customs-Declarations | عرض الأعمدة: الرقم، الوجهة، القيمة، الحالة، إجراءات | ☐ | | |
| CUSTMS-124 | Customs-Declarations | حالة فارغة تظهر عند عدم وجود بيانات | ☐ | | |
| CUSTMS-125 | Customs-Create | زر "Add Declaration" يظهر | ☐ | | |
| CUSTMS-126 | Customs-Create | نموذج إنشاء تصريح يظهر | ☐ | | |
| CUSTMS-127 | Customs-Create | إنشاء تصريح جديد يعمل | ☐ | | |
| CUSTMS-128 | Customs-Create | الحقول: الدولة الوجهة، القيمة الإجمالية، العملة | ☐ | | |
| CUSTMS-129 | Customs-Create | إغلاق النموذج بعد الحفظ | ☐ | | |
| CUSTMS-130 | Customs-Submit | زر إرسال التصريح يظهر (حالة غير submitted) | ☐ | | |
| CUSTMS-131 | Customs-Submit | تقديم التصريح يعمل | ☐ | | |
| CUSTMS-132 | Customs-Submit | تغيير الحالة بعد الإرسال | ☐ | | |
| CUSTMS-133 | Customs-Details | النقر على التصريح يفتح modal التفاصيل | ☐ | | |
| CUSTMS-134 | Customs-Details | عرض تفاصيل التصريح بشكل صحيح | ☐ | | |
| DOC-135 | Documents-List | عرض قائمة الوثائق | ☐ | | |
| DOC-136 | Documents-List | عرض الأعمدة: العنوان، النوع، الملف، التاريخ، إجراءات | ☐ | | |
| DOC-137 | Documents-List | حالة فارغة تظهر عند عدم وجود بيانات | ☐ | | |
| DOC-138 | Documents-Upload | زر رفع ملف يظهر | ☐ | | |
| DOC-139 | Documents-Upload | اختيار ملف (PDF, JPG, PNG) يعمل | ☐ | | |
| DOC-140 | Documents-Upload | رفع الملف يعمل | ☐ | | |
| DOC-141 | Documents-Upload | تحديث القائمة تلقائياً بعد الرفع | ☐ | | |
| DOC-142 | Documents-Download | تحميل الملف يعمل (إن وُجد رابط تحميل) | ☐ | | |
| DOC-143 | Documents-Edit | زر التعديل يفتح النموذج بالبيانات الحالية | ☐ | | |
| DOC-144 | Documents-Edit | تعديل وثيقة يعمل | ☐ | | |
| DOC-145 | Documents-Edit | تحديث القائمة تلقائياً بعد التعديل | ☐ | | |
| DOC-146 | Documents-Delete | تأكيد الحذف يظهر | ☐ | | |
| DOC-147 | Documents-Delete | حذف وثيقة يعمل | ☐ | | |
| DOC-148 | Documents-Delete | تحديث القائمة تلقائياً بعد الحذف | ☐ | | |
| DOC-149 | Documents-Details | النقر على الوثيقة يفتح modal التفاصيل | ☐ | | |
| DOC-150 | Documents-Details | عرض تفاصيل الوثيقة بشكل صحيح | ☐ | | |
| RES-151 | Resources-List | عرض قائمة الموارد | ☐ | | |
| RES-152 | Resources-List | عرض البطاقات بشكل صحيح | ☐ | | |
| RES-153 | Resources-List | عرض العنوان، النوع، الفئة، الدولة، الرابط | ☐ | | |
| RES-154 | Resources-List | حالة فارغة تظهر عند عدم وجود بيانات | ☐ | | |
| RES-155 | Resources-Search | حقل البحث يعمل | ☐ | | |
| RES-156 | Resources-Search | زر البحث يسري البحث | ☐ | | |
| RES-157 | Resources-Search | الضغط على Enter يعيد تحميل القائمة | ☐ | | |
| RES-158 | Resources-Create | زر "Add Resource" يظهر | ☐ | | |
| RES-159 | Resources-Create | نموذج إضافة مورد يظهر | ☐ | | |
| RES-160 | Resources-Create | إنشاء مورد جديد يعمل | ☐ | | |
| RES-161 | Resources-Create | الحقول: العنوان، النوع، الفئة، الرابط، الدولة | ☐ | | |
| RES-162 | Resources-Create | إغلاق النموذج بعد الحفص | ☐ | | |
| RES-163 | Resources-Create | تحديث القائمة تلقائياً بعد الحفص | ☐ | | |
| RES-164 | Resources-Edit | زر التعديل يفتح النموذج بالبيانات الحالية | ☐ | | |
| RES-165 | Resources-Edit | تعديل مورد يعمل | ☐ | | |
| RES-166 | Resources-Edit | تحديث القائمة تلقائياً بعد التعديل | ☐ | | |
| RES-167 | Resources-Delete | تأكيد الحذف يظهر | ☐ | | |
| RES-168 | Resources-Delete | حذف مورد يعمل | ☐ | | |
| RES-169 | Resources-Delete | تحديث القائمة تلقائياً بعد الحذف | ☐ | | |
| RES-170 | Resources-Details | النقر على المورد يفتح modal التفاصيل | ☐ | | |
| RES-171 | Resources-Details | عرض تفاصيل المورد بشكل صحيح | ☐ | | |
| RES-172 | Resources-Details | الرابط الخارجي يعمل بشكل صحيح | ☐ | | |
| PROF-173 | Profile-View | صفحة البروفايل تفتح بدون أخطاء | ☐ | | |
| PROF-174 | Profile-View | عرض البيانات الحالية للمستخدم | ☐ | | |
| PROF-175 | Profile-View | الحقول: Full Name, Email, Phone, Company | ☐ | | |
| PROF-176 | Profile-Update | تعديل الاسم الكامل يعمل | ☐ | | |
| PROF-177 | Profile-Update | تعديل البريد الإلكتروني يعمل | ☐ | | |
| PROF-178 | Profile-Update | تعديل رقم الهاتف يعمل | ☐ | | |
| PROF-179 | Profile-Update | تعديل الشركة يعمل | ☐ | | |
| PROF-180 | Profile-Update | رسالة نجاح تظهر بعد التحديث | ☐ | | |
| PROF-181 | Profile-Update | تحديث البيانات في الواجهة بعد الحفظ | ☐ | | |
| API-182 | API-Endpoints | الرابط `/health` يعيد `{"status": "healthy", ...}` | ☐ | | |
| API-183 | API-Endpoints | الرمز `200 OK` (/health) | ☐ | | |
| API-184 | API-Endpoints | الرابط `/docs` يفتح Swagger UI | ☐ | | |
| API-185 | API-Endpoints | عرض جميع الـ Endpoints بشكل صحيح | ☐ | | |
| API-186 | API-Endpoints | الرابط `/redoc` يفتح ReDoc | ☐ | | |
| API-187 | API-Endpoints | عرض التوثيق بشكل صحيح | ☐ | | |
| API-188 | API-Endpoints | الرابط `/openapi.json` يعيد schema صالح | ☐ | | |
| API-189 | API-Endpoints | الرمز `200 OK` (/openapi.json) | ☐ | | |
| SEC-190 | Security | الوصول إلى `/` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-191 | Security | الوصول إلى `/suppliers` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-192 | Security | الوصول إلى `/customers` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-193 | Security | الوصول إلى `/shipments` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-194 | Security | الوصول إلى `/invoices` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-195 | Security | الوصول إلى `/customs` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-196 | Security | الوصول إلى `/documents` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-197 | Security | الوصول إلى `/resources` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-198 | Security | الوصول إلى `/profile` بدون Token يوجه إلى `/login` | ☐ | | |
| SEC-199 | Security-Role | دور `owner` يستطيع الوصول لجميع الصفحات | ☐ | | |
| SEC-200 | Security-Role | دور `manager` يستطيع الوصول لصفحات الإدارة | ☐ | | |
| SEC-201 | Security-Role | دور `sales` يمكنه إنشاء/تعديل العملاء والشحنات | ☐ | | |
| SEC-202 | Security-Role | دور `accountant` يمكنه الوصول للفواتير | ☐ | | |
| SEC-203 | Security-Role | دور `logistics` يمكنه الوصول للشحنات والجمارك | ☐ | | |
| SEC-204 | Security-Role | Roles غير المخوّلة تستقبل `403 Forbidden` عند محاولة عمليات محمية | ☐ | | |
| SEC-205 | Security-Token | إرسال Token غير صالح ينتج `401 Unauthorized` | ☐ | | |
| SEC-206 | Security-Token | إرسال Token منتهي الصلاحية ينتج `401 Unauthorized` | ☐ | | |
| SEC-207 | Security-Token | بعد انتهاء صلاحية `access_token` يتم تجديده تلقائياً عبر `refresh_token` | ☐ | | |
| SEC-208 | Security-Token | بعد انتهاء صلاحية `refresh_token` يتم التوجيه إلى `/login` | ☐ | | |
| SEC-209 | Security-Navigation | كتابة `/dashboard` مباشرة في المتصفح تفتح الصفحة (إذا كان مسجلاً) | ☐ | | |
| SEC-210 | Security-Navigation | كتابة `/suppliers` مباشرة في المتصفح تفتح الصفحة (إذا كان مسجلاً) | ☐ | | |
| SEC-211 | Security-Navigation | كتابة `/login` أثناء التسجيل يوجه إلى الصفحة بدون أخطاء | ☐ | | |
| PERF-212 | Performance | تحميل الصفحة الأولى بعد تسجيل الدخول أقل من 3 ثوان٢ | ☐ | | |
| PERF-213 | Performance | عدم وجود تأخير ملحوظ في عرض المحتوى | ☐ | | |
| PERF-214 | Performance | التنقل بين الصفحات سريع | ☐ | | |
| PERF-215 | Performance | عدم إعادة تحميل كامل الصفحة عند التنقل (React Router) | ☐ | | |
| PERF-216 | Performance | عرض قائمة من 50+ سجل بدون تأخير | ☐ | | |
| PERF-217 | Performance | تمرير الجدول سلس | ☐ | | |
| PERF-218 | Performance | رفع ملف PDF بحجم 10MB يعمل في أقل من 5 ثوان٢ | ☐ | | |
| PERF-219 | Performance | عرض تقدم الرفع (إن متاح) | ☐ | | |
| UX-220 | UI | الصفحة تعمل على شاشة سطح المكتب (1920x1080) | ☐ | | |
| UX-221 | UI | الصفحة تعمل على شاشة لابتوب (1366x768) | ☐ | | |
| UX-222 | UI | الصفحة تعمل على شاشة آيباد (768x1024) | ☐ | | |
| UX-223 | UI | الصفحة تعمل على شاشة موبايل (375x667) | ☐ | | |
| UX-224 | UI | القائمة الجانبية تظهر/تخفي بشكل صحيح على الموبايل | ☐ | | |
| UX-225 | UI | الجداول قابلة للتمرير أفقيّاً على الشاشات الصغيرة | ☐ | | |
| UX-226 | UI-Buttons | جميع الأزرار قابلة للنقر | ☐ | | |
| UX-227 | UI-Buttons | الأزرار تعرض حالة `hover` و `active` | ☐ | | |
| UX-228 | UI-Buttons | الأزرار المعطلة (`disabled`) لا يمكن النقر عليها | ☐ | | |
| UX-229 | UI-Forms | الحقول المطلوبة معلمة بـ * | ☐ | | |
| UX-230 | UI-Forms | التحقق من صحة البيانات قبل الإرسال | ☐ | | |
| UX-231 | UI-Forms | رسائل خطأ واضحة عند فشل التحقق | ☐ | | |
| UX-232 | UI-Forms | النموذج يُغلق بعد الحفظ بنجاح | ☐ | | |
| UX-233 | UI-Messages | رسائل النجاح تظهر بالأخضر | ☐ | | |
| UX-234 | UI-Messages | رسائل الخطأ تظهر بالأحمر | ☐ | | |
| UX-235 | UI-Messages | رسائل التحذير تظهر بالبرتقالي/الأصفر | ☐ | | |
| UX-236 | UI-Loading | Spinner يظهر أثناء تحميل البيانات | ☐ | | |
| UX-237 | UI-Loading | Spinner يظهر أثناء تقديم النماذج | ☐ | | |
| UX-238 | UI-Loading | مؤشر التحميل في الصفحة الرئيسية يعمل | ☐ | | |
| UX-239 | UI-Empty | حالة فارغة معروضة عند عدم وجود بيانات في جميع القوائم | ☐ | | |
| UX-240 | UI-Empty | رسالة "No data available" تظهر بشكل صحيح | ☐ | | |
| UX-241 | UI-Empty | زر إضافة جديد يظهر في الحالة الفارغة (إن متاح) | ☐ | | |

---

## UAT Evidence Summary

| Metric | Count |
|--------|-------|
| Total scenarios | 241 |
| Passed | 0 |
| Failed | 0 |
| Blocked | 0 |
| Not executed | 241 |

---

## Coverage Report

| Metric | Value |
|--------|-------|
| Source scenarios | 241 |
| Execution Package scenarios | 241 |
| Missing | 0 |
| Duplicate | 0 |
| Coverage | 241/241 (100%) |

---

## Defect Reporting Template

If any scenario FAILS:

```
**Defect Report - Gate 4 UAT Failure**

- **Scenario ID:** [e.g., AUTH-01]
- **Failure Type:** Functional / Visual / Performance
- **Observed Behavior:** [Description]
- **Expected Behavior:** [Description]
- **Evidence:** [Screenshots, Network, Console logs]
- **Work Package Impact:** WP-18 reopened for defect resolution
- **Gate Status:** Cannot proceed to Gate 5
```

---

## Next Steps After UAT Completion

1. All scenarios must show **Pass** with evidence
2. Project Owner signs UAT checklist
3. Gate 4 marked complete
4. Proceed to Gate 5 (Project Owner Acceptance)

**Gate 5 Prerequisites:**
- All 241 scenarios passed
- UAT Evidence Summary complete
- No critical/high defects
- Project Owner signature on this document