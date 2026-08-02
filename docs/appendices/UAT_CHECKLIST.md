# Nile Key - User Acceptance Testing

## Governing Document
- `PLAN.md` Section 23 is the governing execution constitution of the Nile Key project.
- UAT is not considered complete unless all execution rules defined in `PLAN.md` Section 23 are satisfied.
- Any failed UAT item immediately reopens the related Work Package or defect for re-work.

## Test Environment
| Field | Value |
|-------|-------|
| تاريخ الاختبار | |
| إصدار المشروع | 1.1.0-MVP |
| قاعدة البيانات المستخدمة | SQLite (`nile_key.db`) |
| المتصفح | |
| نظام التشغيل | |
| اسم المختبر | |

---

## Authentication

### Login
- [ ] تسجيل الدخول عبر `/login` ببيانات صحيحة ينجح
- [ ] تسجيل الدخول ببيانات خاطئة يعرض رسالة خطأ واضحة
- [ ] الحقول المطلوبة (username / password) تُValidate
- [ ] زر الإظهار/الإخفاء لكلمة المرور يعمل (إن وُجد)
- [ ] التوجيه التلقائي بعد نجاح تسجيل الدخول إلى `/`

### Logout
- [ ] تسجيل الخروج من القائمة الجانبية يعمل
- [ ] إزالة `refresh_token` من التخزين المحلي بعد تسجيل الخروج
- [ ] التوجيه بعد تسجيل الخروج إلى `/login`

### Invalid Credentials
- [ ] اسم مستخدم غير موجود يعرض رسالة خطأ
- [ ] كلمة مرور خاطئة تعرض رسالة خطأ
- [ ] الحساب غير المفعل لا يمكنه تسجيل الدخول
- [ ] تفعيل Rate Limiting على نقاط نهاية المصادقة (/login, /register, /refresh)

### Session Persistence
- [ ] تحديث الصفحة يحافظ على حالة تسجيل الدخول
- [ ] إعادة فتح المتصفح يحافظ على الجلسة (حسب إعدادات expires)
- [ ] توكن المصادقة يُرسل عبر HttpOnly Cookies (بدون تخزين في localStorage)
- [ ] خصائص الأمان للـ Cookies: HttpOnly, Secure, SameSite, Domain مطابقة للإعدادات
- [ ] حماية CSRF تعمل على الطلبات التي تغير الحالة (POST/PUT/PATCH/DELETE) مع Cookies
- [ ] Security Headers مُفعّلة في الاستجابات

### Token Expiration
- [ ] انتهاء صلاحية `access_token` يُعيد التوجيه إلى `/login`
- [ ] `refresh_token` يعيد إنشاء `access_token` تلقائياً
- [ ] انتهاء صلاحية `refresh_token` يُعيد التوجيه إلى `/login`

### Unauthorized Access Redirect
- [ ] الوصول المباشر إلى `/` بدون تسجيل دخول يوجه إلى `/login`
- [ ] الوصول المباشر إلى أي صفحة محمية بدون Token يوجه إلى `/login`

---

## Dashboard

- [ ] الصفحة تفتح بدون أخطاء
- [ ] تحميل بيانات الإحصائيات ( suppliers / customers / shipments / invoices )
- [ ] عدم وجود أخطاء Console
- [ ] عدم وجود أخطاء Network
- [ ] عرض البطاقات الإحصائية بشكل صحيح
- [ ] عرض كتابع "Platform v1.0" بشكل صحيح
- [ ] حالة التحميل (Loading spinner) تظهر أثناء جلب البيانات

---

## Suppliers

### List
- [ ] عرض قائمة الموردين
- [ ] عرض أعمدة: الاسم، جهة الاتصال، البريد، الهاتف، المدينة، الحالة، إجراءات
- [ ] حالة فارغة تظهر عند عدم وجود بيانات

### Search
- [ ] البحث بالاسم يعمل
- [ ] زر البحث يعيد تحميل القائمة
- [ ] الضغط على Enter يعيد تحميل القائمة

### Create
- [ ] فتح نموذج إضافة مورد
- [ ] إضافة مورد جديد يعمل
- [ ] التحقق من الحقول المطلوبة (الاسم مطلوب)
- [ ] إغلاق النموذج بعد الحفظ
- [ ] تحديث القائمة تلقائياً بعد الحفظ

### Edit
- [ ] زر التعديل يفتح النموذج بالبيانات الحالية
- [ ] تعديل مورد يعمل
- [ ] تحديث القائمة تلقائياً بعد الحفظ

### Delete
- [ ] تأكيد الحذف يظهر
- [ ] حذف مورد يعمل
- [ ] تحديث القائمة تلقائياً بعد الحذف

### Validation
- [ ] الاسم مطلوب
- [ ] البريد الإلكتروني يخضع للتحقق من الصيغة (إن وُجد)

### Empty State
- [ ] عرض "No Data" عند عدم وجود موردين

### Loading State
- [ ] عرض Spinner أثناء تحميل البيانات

---

## Customers

### List
- [ ] عرض قائمة العملاء
- [ ] عرض أعمدة: الاسم، جهة الاتصال، البريد، الدولة، الفئة، الحالة، إجراءات
- [ ] حالة فارغة تظهر عند عدم وجود بيانات

### Search
- [ ] البحث بالاسم يعمل
- [ ] زر البحث يعيد تحميل القائمة

### Create
- [ ] فتح نموذج إضافة عميل
- [ ] إضافة عميل جديد يعمل
- [ ] التحقق من الحقول المطلوبة (الاسم، الدولة)
- [ ] إغلاق النموذج بعد الحفظ
- [ ] تحديث القائمة تلقائياً بعد الحفظ

### Edit
- [ ] زر التعديل يفتح النموذج بالبيانات الحالية
- [ ] تعديل عميل يعمل
- [ ] تحديث القائمة تلقائياً بعد الحفظ

### Delete
- [ ] تأكيد الحذف يظهر
- [ ] حذف عميل يعمل
- [ ] تحديث القائمة تلقائياً بعد الحذف

### CSV Import
- [ ] زر رفع CSV يظهر
- [ ] اختيار ملف CSV يعمل
- [ ] استيراد العملاء يعمل
- [ ] عرض رسالة نجاح/فشل الاستيراد

### Validation
- [ ] الاسم مطلوب
- [ ] الدولة مطلوبة
- [ ] البريد الإلكتروني يخضع للتحقق من الصيغة (إن وُجد)

---

## Shipments

### List
- [ ] عرض قائمة الشحنات
- [ ] عرض أعمدة: رقم التتبع، المنشأ، الوجهة، الناقل، الحالة، إجراءات
- [ ] حالة فارغة تظهر عند عدم وجود بيانات

### Create
- [ ] فتح نموذج إضافة شحنة
- [ ] إنشاء شحنة جديدة يعمل
- [ ] الحقول المطلوبة: المنشأ، الوجهة
- [ ] إغلاق النموذج بعد الحفظ
- [ ] تحديث القائمة تلقائياً بعد الحفظ

### Edit
- [ ] زر التعديل يفتح النموذج بالبيانات الحالية
- [ ] تعديل شحنة يعمل

### Shipping Rates
- [ ] زر "Get Rates" يظهر
- [ ] نموذج حساب Rates يظهر
- [ ] إدخال المنشأ والوجهة والوزن يعمل
- [ ] حساب Rates يعرض النتائج
- [ ] عرض الناقل، الخدمة، التكلفة، الأيام المتوقعة

### Tracking
- [ ] الرابط `/api/v1/shipping/track/{tracking_id}` يعمل
- [ ] عرض حالة الشحنة (إن متاح من الـ API)

### Label
- [ ] الرابط `/api/v1/shipping/shipments/{id}/label` يعمل
- [ ] تحميل الملصق كملف PDF (إن متاح من الـ API)

---

## Invoices

### List
- [ ] عرض قائمة الفواتير
- [ ] عرض أعمدة: رقم الفاتورة، المجموع الفرعي، الضريبة، الإجمالي، تاريخ الإصدار، الحالة، إجراءات
- [ ] حالة فارغة تظهر عند عدم وجود بيانات

### Create
- [ ] فتح نموذج إضافة فاتورة
- [ ] إنشاء فاتورة جديدة يعمل
- [ ] إضافة عناصر الفاتورة (Items) يعمل
- [ ] حساب الإجمالي تلقائياً
- [ ] إغلاق النموذج بعد الحفظ
- [ ] تحديث القائمة تلقائياً بعد الحفظ

### Edit
- [ ] زر التعديل يفتح النموذج بالبيانات الحالية
- [ ] تعديل فاتورة يعمل (حالة Draft فقط)
- [ ] تحديث القائمة تلقائياً بعد الحفظ

### Validate
- [ ] زر اعتماد الفاتورة يظهر (حالة Draft فقط)
- [ ] اعتماد الفاتورة يعمل
- [ ] تغيير الحالة إلى `validated` بعد الاعتماد

### Cancel
- [ ] زر إلغاء الفاتورة يظهر (ليس للفواتير الملغاة)
- [ ] تأكيد الإلغاء يظهر
- [ ] إلغاء الفاتورة يعمل
- [ ] تغيير الحالة إلى `cancelled` بعد الإلغاء

### Details Modal
- [ ] النقر على الفاتورة يفتح modal التفاصيل
- [ ] عرض تفاصيل الفاتورة بشكل صحيح
- [ ] إغلاق الـ Modal يعمل

---

## Customs

### HS Codes
- [ ] عرض قاعدة بيانات أكواد HS
- [ ] عرض الأعمدة: الكود، الوصف، معدل الرسوم، معدل الضريبة
- [ ] البحث في أكواد HS يعمل
- [ ] حالة فارغة تظهر عند عدم وجود بيانات

### Duty Calculator
- [ ] زر "Calculate Duties" يظهر
- [ ] نموذج حساب الرسوم يظهر
- [ ] إدخال كود HS والقيمة والعملة والوجهة يعمل
- [ ] حساب الرسوم يعرض: Duty Rate, Duty Amount, Tax Amount, Total
- [ ] عرض النتائج بشكل صحيح

### Declaration List
- [ ] عرض قائمة التصاريح الجمركية
- [ ] عرض الأعمدة: الرقم، الوجهة، القيمة، الحالة، إجراءات
- [ ] حالة فارغة تظهر عند عدم وجود بيانات

### Create Declaration
- [ ] زر "Add Declaration" يظهر
- [ ] نموذج إنشاء تصريح يظهر
- [ ] إنشاء تصريح جديد يعمل
- [ ] الحقول: الدولة الوجهة، القيمة الإجمالية، العملة
- [ ] إغلاق النموذج بعد الحفظ

### Submit Declaration
- [ ] زر إرسال التصريح يظهر (حالة غير submitted)
- [ ] تقديم التصريح يعمل
- [ ] تغيير الحالة بعد الإرسال

### Declaration Details
- [ ] النقر على التصريح يفتح modal التفاصيل
- [ ] عرض تفاصيل التصريح بشكل صحيح

---

## Documents

### List
- [ ] عرض قائمة الوثائق
- [ ] عرض الأعمدة: العنوان، النوع، الملف، التاريخ، إجراءات
- [ ] حالة فارغة تظهر عند عدم وجود بيانات

### Upload
- [ ] زر رفع ملف يظهر
- [ ] اختيار ملف (PDF, JPG, PNG) يعمل
- [ ] رفع الملف يعمل
- [ ] تحديث القائمة تلقائياً بعد الرفع

### Download (إن متاح)
- [ ] تحميل الملف يعمل (إن وُجد رابط تحميل)

### Edit
- [ ] زر التعديل يفتح النموذج بالبيانات الحالية
- [ ] تعديل وثيقة يعمل
- [ ] تحديث القائمة تلقائياً بعد التعديل

### Delete
- [ ] تأكيد الحذف يظهر
- [ ] حذف وثيقة يعمل
- [ ] تحديث القائمة تلقائياً بعد الحذف

### Document Details
- [ ] النقر على الوثيقة يفتح modal التفاصيل
- [ ] عرض تفاصيل الوثيقة بشكل صحيح

---

## Resources

### List
- [ ] عرض قائمة الموارد
- [ ] عرض البطاقات بشكل صحيح
- [ ] عرض العنوان، النوع، الفئة، الدولة، الرابط
- [ ] حالة فارغة تظهر عند عدم وجود بيانات

### Search
- [ ] حقل البحث يعمل
- [ ] زر البحث يسري البحث
- [ ] الضغط على Enter يعيد تحميل القائمة

### Create
- [ ] زر "Add Resource" يظهر
- [ ] نموذج إضافة مورد يظهر
- [ ] إنشاء مورد جديد يعمل
- [ ] الحقول: العنوان، النوع، الفئة، الرابط، الدولة
- [ ] إغلاق النموذج بعد الحفظ
- [ ] تحديث القائمة تلقائياً بعد الحفظ

### Edit
- [ ] زر التعديل يفتح النموذج بالبيانات الحالية
- [ ] تعديل مورد يعمل
- [ ] تحديث القائمة تلقائياً بعد التعديل

### Delete
- [ ] تأكيد الحذف يظهر
- [ ] حذف مورد يعمل
- [ ] تحديث القائمة تلقائياً بعد الحذف

### Resource Details
- [ ] النقر على المورد يفتح modal التفاصيل
- [ ] عرض تفاصيل المورد بشكل صحيح
- [ ] الرابط الخارجي يعمل بشكل صحيح

---

## Profile

### View Profile
- [ ] صفحة البروفايل تفتح بدون أخطاء
- [ ] عرض البيانات الحالية للمستخدم
- [ ] الحقول: Full Name, Email, Phone, Company

### Update Profile
- [ ] تعديل الاسم الكامل يعمل
- [ ] تعديل البريد الإلكتروني يعمل
- [ ] تعديل رقم الهاتف يعمل
- [ ] تعديل الشركة يعمل
- [ ] رسالة نجاح تظهر بعد التحديث
- [ ] تحديث البيانات في الواجهة بعد الحفظ

---

## API Endpoints

### /health
- [ ] الرابط `/health` يعيد `{"status": "healthy", ...}`
- [ ] الرمز `200 OK`

### /docs
- [ ] الرابط `/docs` يفتح Swagger UI
- [ ] عرض جميع الـ Endpoints بشكل صحيح

### /redoc
- [ ] الرابط `/redoc` يفتح ReDoc
- [ ] عرض التوثيق بشكل صحيح

### /openapi.json
- [ ] الرابط `/openapi.json` يعيد schema صالح
- [ ] الرمز `200 OK`

---

## Security

### Protected Routes
- [ ] الوصول إلى `/` بدون Token يوجه إلى `/login`
- [ ] الوصول إلى `/suppliers` بدون Token يوجه إلى `/login`
- [ ] الوصول إلى `/customers` بدون Token يوجه إلى `/login`
- [ ] الوصول إلى `/shipments` بدون Token يوجه إلى `/login`
- [ ] الوصول إلى `/invoices` بدون Token يوجه إلى `/login`
- [ ] الوصول إلى `/customs` بدون Token يوجه إلى `/login`
- [ ] الوصول إلى `/documents` بدون Token يوجه إلى `/login`
- [ ] الوصول إلى `/resources` بدون Token يوجه إلى `/login`
- [ ] الوصول إلى `/profile` بدون Token يوجه إلى `/login`

### Role Permissions
- [ ] دور `owner` يستطيع الوصول لجميع الصفحات
- [ ] دور `manager` يستطيع الوصول لصفحات الإدارة
- [ ] دور `sales` يمكنه إنشاء/تعديل العملاء والشحنات
- [ ] دور `accountant` يمكنه الوصول للفواتير
- [ ] دور `logistics` يمكنه الوصول للشحنات والجمارك
- [ ] Roles غير المخوّلة تستقبل `403 Forbidden` عند محاولة عمليات محمية

### Invalid Token
- [ ] إرسال Token غير صالح ينتج `401 Unauthorized`
- [ ] إرسال Token منتهي الصلاحية ينتج `401 Unauthorized`

### Expired Token
- [ ] بعد انتهاء صلاحية `access_token` يتم تجديده تلقائياً عبر `refresh_token`
- [ ] بعد انتهاء صلاحية `refresh_token` يتم التوجيه إلى `/login`

### Direct URL Access
- [ ] كتابة `/dashboard` مباشرة في المتصفح تفتح الصفحة (إذا كان مسجلاً)
- [ ] كتابة `/suppliers` مباشرة في المتصفح تفتح الصفحة (إذا كان مسجلاً)
- [ ] كتابة `/login` أثناء التسجيل يوجه إلى الصفحة بدون أخطاء

### CSRF Protection
- [ ] الطلبات التي تغير الحالة مع Cookies تتفحص من خلال Origin/Referer
- [ ] الطلبات بدون Origin/Referer صالحين تُرفض (403)
- [ ] الطلبات برسوم التحقق CSRF صالحة تمر بنجاح
- [ ] الطلبات برسوم Authorization Header تتخطى فحص CSRF

### Cookie Security
- [ ] Access Token Cookie يحتوي على علم HttpOnly
- [ ] Refresh Token Cookie يحتوي على علم HttpOnly
- [ ] SameSite مُعَد حسب الإعدادات (lax أو strict)
- [ ] Secure flag مُفعل في بيئة الإنتاج
- [ ] Domain مُعَد عند الحاجة

### Rate Limiting
- [ ] Rate Limiting مفعّل على نقاط نهاية المصادقة
- [ ] الطلبات المتكررة تُرجع 429 Too Many Requests

---

## Performance

### Initial Load
- [ ] تحميل الصفحة الأولى بعد تسجيل الدخول أقل من 3 ثوانٍ
- [ ] عدم وجود تأخير ملحوظ في عرض المحتوى

### Navigation Speed
- [ ] التنقل بين الصفحات سريع
- [ ] عدم إعادة تحميل كامل الصفحة عند التنقل (React Router)

### Large Tables
- [ ] عرض قائمة من 50+ سجل بدون تأخير
- [ ] تمرير الجدول سلس

### Upload Performance
- [ ] رفع ملف PDF بحجم 10MB يعمل في أقل من 5 ثوانٍ
- [ ] عرض تقدم الرفع (إن متاح)

---

## UI / UX

### Responsive Layout
- [ ] الصفحة تعمل على شاشة سطح المكتب (1920x1080)
- [ ] الصفحة تعمل على شاشة لابتوب (1366x768)
- [ ] الصفحة تعمل على شاشة آيباد (768x1024)
- [ ] الصفحة تعمل على شاشة موبايل (375x667)
- [ ] القائمة الجانبية تظهر/تخفي بشكل صحيح على الموبايل
- [ ] الجداول قابلة للتمرير أفقيّاً على الشاشات الصغيرة

### Buttons
- [ ] جميع الأزرار قابلة للنقر
- [ ] الأزرار تعرض حالة `hover` و `active`
- [ ] الأزرار المعطلة (`disabled`) لا يمكن النقر عليها

### Forms
- [ ] الحقول المطلوبة معلمة بـ *
- [ ] التحقق من صحة البيانات قبل الإرسال
- [ ] رسائل خطأ واضحة عند فشل التحقق
- [ ] النموذج يُغلق بعد الحفظ بنجاح

### Messages
- [ ] رسائل النجاح تظهر بالأخضر
- [ ] رسائل الخطأ تظهر بالأحمر
- [ ] رسائل التحذير تظهر بالبرتقالي/الأصفر

### Loading Indicators
- [ ] Spinner يظهر أثناء تحميل البيانات
- [ ] Spinner يظهر أثناء تقديم النماذج
- [ ] مؤشر التحميل في الصفحة الرئيسية يعمل

### Empty States
- [ ] حالة فارغة معروضة عند عدم وجود بيانات في جميع القوائم
- [ ] رسالة "No data available" تظهر بشكل صحيح
- [ ] زر إضافة جديد يظهر في الحالة الفارغة (إن متاح)

---

## Final Acceptance

| Field | Value |
|-------|-------|
| Overall Status | PASS / FAIL |
| Critical Issues | |
| Major Issues | |
| Minor Issues | |
| Notes | |

---

## UAT Execution Notes — 2026-07-27

### Test Scope
This UAT round was executed via **Backend API only** (Python `urllib` / `TestClient`).
No browser automation or GUI interaction was performed because the execution environment does not support a graphical browser.

### Actors
- **Tester:** Kilo AI agent
- **Date:** 2026-07-27

### Environment
| Field | Value |
|-------|-------|
| API Base URL | http://localhost:8000 |
| Auth | JWT via `/api/v1/auth/login` |
| Test User | `uat_user8` / `UatPass123!` (or owner-equivalent roles created in-test) |

### Results Summary
| # | Scenario | Method | Final Result | Notes |
|---|----------|--------|--------------|-------|
| 1 | Login | POST `/api/v1/auth/login` | PASS | Works on first attempt |
| 2 | Dashboard | GET `/api/v1/dashboard` | PASS | Returns data |
| 3 | Create Customer | POST `/api/v1/customers` | PASS | Required fields accepted |
| 4 | Create Supplier | POST `/api/v1/suppliers` | PASS | Works |
| 5 | Create Shipment | POST `/api/v1/shipments` | PASS | Works |
| 6 | Create Customs Declaration | POST `/api/v1/customs/declarations` | PASS | Requires `destination_country` |
| 7 | List Documents | GET `/api/v1/documents` | PASS | Upload not tested here |
| 8 | Create Invoice | POST `/api/v1/invoices/` | PASS | Requires `subtotal`, `total`, `issue_date`, `items`, `items[0].total` |
| 9 | Search | GET `/api/v1/search` | PASS | Works |
| 10 | Audit Logs / Notifications List | GET endpoints | PASS | Send not tested here |
| 11 | Logout | POST `/api/v1/auth/logout` | PASS (after fix) | Previously NOT_IMPLEMENTED |

### Known API Quirks
- **Trailing slash:** `/api/v1/invoices` returns HTTP 307 redirect to `/api/v1/invoices/`. Use the trailing-slash form.
- **Mandatory fields discovered during execution:**
  - Customs declarations: `destination_country` is required.
  - Invoices: `subtotal`, `total`, `issue_date`, `items`, `items[0].total` are required.

### Excluded from This UAT
- Frontend GUI rendering, navigation, React/UX behavior.
- Actual SMTP delivery (notification send endpoint is present and permissioned; delivery depends on SMTP config).
- Browser-side cookie CSRF token injection (verified via Authorization header in API tests).

---

## AI / Digital Export Manager (DEM)

### Connect / Disconnect
- [ ] Connect creates a DEM session and updates the landing state
- [ ] Disconnect closes the active session
- [ ] Session history lists created sessions with mission counts

### Mission Composer
- [ ] New Mission page opens only when a session is active
- [ ] All supported mission types are selectable
- [ ] Submitting a mission returns `reasoning`, `requires_approval`, and `approval_status`

### Mission Dashboard
- [ ] Missions list loads missions from the active session
- [ ] Mission detail shows Results and Decision Trace tabs
- [ ] Execution Progress polls while mission is pending/running

### Approval Flow
- [ ] `pending_approval` missions remain in `pending_approval` state after manager approval
- [ ] Approval Inbox requires owner/manager role
- [ ] Approve/Reject records an `approval_decision` audit log entry
- [ ] Rejecting an approval does not auto-fail or resume the mission

### Knowledge Explorer
- [ ] Search returns entities by query and optional entity type
- [ ] Selecting an entity shows its relationships

### Trade Intelligence
- [ ] Supplier analysis accepts a supplier ID and returns analysis results
- [ ] Trend detection accepts an entity type and returns trend data

---

*يرجى التأشير (- [x]) على كل اختبار بعد اجتيازه، وترك ملاحظات في حال الفشل.*
