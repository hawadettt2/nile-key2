# Owner Operational Validation Plan

**Phase:** Operational Readiness — Owner Perspective  
**Work Package:** OV-001  
**Authority:** PROJECT_EXECUTION_RULES.md Section 16 (Manual UAT), WP-42 Specification  
**Governing Document:** `docs/UAT_CHECKLIST.md`  
**Date:** 2026-07-27  
**Status:** Ready for Execution  
**Baseline:** `79c686a` (HEAD)

---

## 1. الهدف

إنشاء مرحلة رسمية موحدة لمعاينة تشغيلية المشروع من منظور المالك/المستخدم النهائي، بحيث:
- تغطي جميع المسارات والواجهات والقدرات المرئية للمستخدم.
- تُنفذ بالكامل في زمن مضبوط (ساعات، ليس أيام).
- يمكن إيقافها واستئنافها من آخر نقطة تحقق (Checkpoint) دون فقدان حالة.
- تفصل بين المهام القابلة للأتمتة والمهام اليدوية المرتبطة بالملاحظة البشرية.
- تُنتج سجلات رسمية قابلة للمراجعة: execution log، issues registry، وتقرير نهائي.

---

## 2. النطاق

### 2.1 داخل النطاق (In Scope)

| # | المجال | Route / API | الأتمتة المحتملة |
|---|--------|-------------|------------------|
| 1 | Authentication & Session | `/login`, `/api/v1/auth` | API + Browser |
| 2 | Navigation & Routing | `/`, `/suppliers`, `/customers`, `/shipments`, `/invoices`, `/customs`, `/documents`, `/resources`, `/profile`, `/notifications` | Browser |
| 3 | CRUD Operations | Suppliers, Customers, Shipments, Invoices, Customs, Documents, Resources, Profile | API |
| 4 | Workflows | CSV import, Duty calculator, Tracking, Labels, Invoice validate/cancel, Declaration submit, ETA | API + Browser |
| 5 | Validation & Error Handling | Error messages, invalid inputs, CSRF, token expiry | API + Browser |
| 6 | UI / UX Review | Responsive, loading, empty states, forms, messages | Browser |
| 7 | Browser & Console Review | Security headers, cookie flags, console errors, network errors | DevTools / Browser |
| 8 | Final Owner Review | Overall sign-off, defect acceptance, go/no-go decision | Manual |

### 2.2 خارج النطاق (Out of Scope)

- تعديل الكود أو إصلاح أخطاء أثناء المعاينة.
- اختبارات الأداء المتقدمة أو Load testing.
- اختبار الأمان المتقدم (Penetration testing).
- Backend-only routes غير المرئية للمالك (`/api/v1/agent`, `/api/v1/knowledge-graph`, `/api/v1/trade-intelligence`, `/api/v1/eta`, `/api/v1/export-workflows`, `/api/v1/digital-export-manager`).
- إنشاء بيانات إنتاج حقيقية أو ترحيل بيانات.

---

## 3. تعريف المراحل الثمانية

### Stage 1: Startup Validation

**الهدف:** التحقق من أن التطبيق يعمل ويمكن الوصول إليه والولوج بنجاح.

**المدخلات:**
- التطبيق قيد التشغيل (`uvicorn` + React dev server أو Preview).
- قاعدة بيانات مهيأة (`nile_key.db`).
- بيانات اختبار متاحة.

**المخرجات:**
- `/health` يعيد `{"status": "healthy"}`.
- `/login` يحمل بدون أخطاء.
- تسجيل دخول ناجح يحصل على `access_token` و `refresh_token`.

**أتمتة:**
- استدعاء `/health` وتحقق من الحالة.
- استدعاء `/api/v1/auth/login` ببيانات صحيحة وتحقق من 200 + وجود التوكن.

**يدوي:**
- ملاحظة أن واجهة `/login` تظهر بشكل صحيح.

**معيار النجاح:** 200 OK من `/health` و `/api/v1/auth/login` مع وجود cookies أو bearer token.

---

### Stage 2: Navigation Validation

**الهدف:** التحقق من أن جميع المسارات الرئيسية accessible وأن التوجيه والـ PrivateRoute يعملان.

**المدخلات:** توكن صالح من Stage 1.

**المخرجات:**
- جميع المسارات الرئيسية تُرجع 200 عند طلبها بالـ Browser.
- المسارات المحمية تُوجه إلى `/login` بدون توكن.
- القائمة الجانبية تحتوي على جميع الروابط المتوقعة.

**أتمتة:**
- طلب كل route رئيسي بخادم اختبار وتحقق من 200 أو التوجيه المتوقع.
- فحص HTML لكل صفحة للتأكد من عدم وجود خطأ تحميل.

**يدوي:**
- التنقل عبر القائمة الجانبية بالترتيب ومشاهدة التحميل.

**معيار النجاح:** جميع المسارات principal respond 200 redirect correctly without server errors.

---

### Stage 3: CRUD Validation

**الهدف:** التحقق من عمليات إنشاء/قراءة/تعديل/حذف لكل كيان رئيسي.

**الكيانات:**
1. Supplier
2. Customer
3. Shipment
4. Invoice
5. Customs Declaration
6. Document (Upload)
7. Resource
8. Profile

**المدخلات:** توكن صالح + بيانات اختبار.

**المخرجات:**
- لكل كيان: Satu record created, readable, updated, deletable.
- القوائم تعرض السجلات بعد الإنشاء.
- حالات فارغة تظهر عند عدم وجود بيانات.

**أتمتة:**
- استدعاءات API لكل عملية CRUD لكل كيان.
- تحقق من حالة الاستجابة (201/200/204) ووجود البيانات في الاستجابة.

**يدوي:**
- ملاحظة ظهور السجلات في الواجهة بعد كل عملية.

**معيار النجاح:** جميع عمليات CRUD تعيد الحالات المتوقعة (2xx) وتبقى البيانات ثابتة.

---

### Stage 4: Workflow Validation

**الهدف:** التحقق من سير العمل business المتكامل والعمليات المتسلسلة.

**الكيانات والعمليات:**

| # | Workflow | Automation Approach |
|---|----------|---------------------|
| 4.1 | Customer CSV Import | POST upload الملف + تحقق من السجلات المستوردة |
| 4.2 | Duty Calculator | POST `/api/v1/customs/calculate-duties` + تحقق من القيم |
| 4.3 | Shipment Tracking | GET `/api/v1/shipping/track/{id}` + تحقق من الاستجابة |
| 4.4 | Shipping Label | GET `/api/v1/shipping/shipments/{id}/label` + تحقق من PDF/response |
| 4.5 | Invoice Validate | PATCH/POST validate + تحقق من تغيير الحالة |
| 4.6 | Invoice Cancel | POST cancel + تحقق من تغيير الحالة |
| 4.7 | Declaration Submit | POST submit + تحقق من تغيير الحالة |
| 4.8 | Profile Update | PUT `/api/v1/auth/me` + تحقق من التحديث |

**المدخلات:** توكن صالح + بيانات اختبار محددة (كود HS، بيانات شحنة، إلخ).

**المخرجات:**
- كل workflow ينتهي بالنتيجة المتوقعة.
- الحالات تتغير بشكل صحيح.

**أتمتة:**
- استدعاءات API متسلسلة لكل workflow.
- تحقق من الحالة بعد كل خطوة.

**يدوي:**
- ملاحظة التفاعل في الواجهة لكل workflow.

**معيار النجاح:** جميع workflows تنفذ بدون أخطاء وتنتج النتائج المتوقعة.

---

### Stage 5: Validation & Error Handling

**الهدف:** التحقق من معالجة الأخطاء والتحقق من المدخلات.

**الحالات المطلوبة:**

| # | الحالة | الطريقة |
|---|--------|---------|
| 5.1 | تسجيل دخول ببيانات خاطئة | Manual/API |
| 5.2 | حقل مطلوب فارغ | Manual/API |
| 5.3 | صيغة بريد إلكتروني خاطئة | Manual/API |
| 5.4 | توكن منتهي الصلاحية | Manual/API |
| 5.5 | وصول بدون صلاحية (403) | Manual/API |
| 5.6 | وصول لمسار غير موجود (404) | Manual/API |
| 5.7 | CSRF token missing على POST | Manual |
| 5.8 | Rate limitingtrigger | Manual |

**المدخلات:** بيانات خاطئة/ناقصة، توكن منتهي، مستخدم بدون صلاحية.

**المخرجات:**
- رسائل خطأ واضحة لكل حالة.
- أرقام حالة HTTP صحيحة (400/401/403/404).
- CSRF reject عند عدم وجود origin/header صالح.

**أتمتة:**
- API tests for 4xx responses with correct status codes and messages.
- Rate limit test with rapid requests.

**يدوي:**
- ملاحظة رسائل الخطأ في الواجهة.

**معيار النجاح:** جميع حالات الخطأ تعيد الحالة المتوقعة ورسالة واضحة.

---

### Stage 6: UI / UX Review

**الهدف:** التحقق من تجربة المستخدم والواجهة.

**نقاط الفحص:**

| # | البند | الطريقة |
|---|--------|---------|
| 6.1 | تخطيط متجاوب (Desktop 1920x1080, Laptop 1366x768, Tablet 768x1024, Mobile 375x667) | Manual |
| 6.2 | الأزرار قابلة للنقر وحالات hover/active واضحة | Manual |
| 6.3 | الحقول المطلوبة معلمة بـ * | Manual |
| 6.4 | رسائل نجاح/خطأ/تحذير بالألوان الصحيحة | Manual |
| 6.5 | Loading spinner يظهر أثناء تحميل البيانات | Manual |
| 6.6 | حالة فارغة تظهر عند عدم وجود بيانات | Manual |
| 6.7 | banner "Platform v1.0" يظهر في Dashboard | Manual |

**المدخلات:** متصفح بأحجام شاشة مختلفة.

**المخرجات:**
- لقطات شاشة لكل نقطة فحص.
- قائمة بالعيوب المكتشفة إن وجدت.

**أتمتة:**
- يمكن استخدام Playwright لأخذ screenshots تلقائية عند أحجام مختلفة، لكن التقييم البشري مطلوب.

**يدوي:**
- معظم النقاط تتطلب تقيماً بصرياً.

**معيار النجاح:** جميع النقاط المدرجة تعمل كما هو موثق.

---

### Stage 7: Browser & Console Review

**الهدف:** التحقق من عدم وجود أخطاء في Console وNetwork وتحققibles الأمان.

**نقاط الفحص:**

| # | البند | الأداة |
|---|--------|--------|
| 7.1 | Console devoid من أخطاء during normal use | DevTools Console |
| 7.2 | Network devoid من أخطاء 4xx/5xx during navigation | DevTools Network |
| 7.3 | Security Headers مفعّلة (CSP, X-Frame-Options, إلخ) | curl/DevTools |
| 7.4 | Cookies by HttpOnly + Secure + SameSite | DevTools Application |
| 7.5 | CORS headers صحيحة | curl API calls |

**المدخلات:** متصفح مفتوح، DevTools مفعّل.

**المخرجات:**
- لقطات شاشة من Console وNetwork tab لكل صفحة رئيسية.
- تقرير Security headers.

**أتمتة:**
- `curl -I` لفحص headers.
- لا يوجد بديل لأتمتة Console/Network errors بدون browser automation.

**يدوي:**
- فحص Console وNetwork tab لكل صفحة.

**معيار النجاح:** لا توجد أخطاء Console، ولا استجابات Network فاشلة، والـ Headers صحيحة.

---

### Stage 8: Final Owner Review

**الهدف:** الحصول على قرار المالك النهائي.

**المدخلات:**
- تقرير تنفيذ كامل.
- Issues registry.
- تقرير نهائي.

**المخرجات:**
- قرار ACCEPT / NOT ACCEPT مع الشروط إن وجدت.
- توقيع المالك إلكترونياً أو كتابياً.

**يدوي:**
- مراجعة المالك لكل التقارير.

**معيار النجاح:** قرار مكتوب وموقع من المالك.

---

## 4. ترتيب التنفيذ

```
Stage 1: Startup Validation
    ↓
Stage 2: Navigation Validation
    ↓
Stage 3: CRUD Validation
    ↓
Stage 4: Workflow Validation
    ↓
Stage 5: Validation & Error Handling
    ↓
Stage 6: UI / UX Review
    ↓
Stage 7: Browser & Console Review
    ↓
Stage 8: Final Owner Review
    ↓
Final Report Generation
```

**لا يمكن تجاوز أي مرحلة.** كل مرحلة تمر بـ Checkpoint قبل الانتقال إلى التالية.

---

## 5. قواعد التنفيذ

1. **Automatable First:** كل فحص يمكن أتمتته يتم أتمتته أولاً عبر API أو script.
2. **Manual Supplement:** الملاحظة البشرية تُضاف فقط حيث لا يمكن الأتمتة (UI/UX، Console، Final Review).
3. **No Code Changes:** لا يُسمح بتعديل الكود أثناء المعاينة. كل مشكلة تُسجل فقط.
4. **Evidence-Based:** كل نتيجة يجب أن تكون مدعومة بأدلة (HTTP status، screenshot، console log).
5. **Stop & Resume:** يمكن إيقاف التنفيذ بعد أي Checkpoint واستئنافه لاحقاً من نفس النقطة.
6. **Single Source of Truth:** جميع السجلات تُحفظ في `.kilo/plans/owner-operational-validation/`.
7. **No Assumptions:** كل فحص له معيار نجاح واضح قبل التنفيذ.
8. **Issue Passthrough:** كل مشكلة تُسجل فوراً في `owner-operational-validation-issues.md` مع تفاصيل كاملة.

---

## 6. معايير النجاح

| المعيار | الشرط |
|---------|-------|
| Startup | `/health` + `/login` يعملان بنجاح |
| Navigation | جميع المسارات accessible بدون أخطاء خادم |
| CRUD | جميع الـ 8 كيانات تدعم CRUD مع حالات 2xx |
| Workflows | جميع الـ 8 workflows تنفذ بنجاح |
| Validation | جميع حالات الخطأ تعيد الحالة المتوقعة |
| UI/UX | جميع النقاط المحددة في Checklist تعمل |
| Browser/Console | لا أخطاء Console/Network، والـ Headers صحيحة |
| Final Review | قرار المالك مكتوب وموقّع |

**النجاح الكلي:** جميع المراحل الثمانية تعمل بنجاح ولا توجد مشكلات ذات أولوية Critical أو High مفتوحة.

---

## 7. معايير الإيقاف والاستئناف

### إيقاف (Stop)

يمكن الإيقاف بعد أي Checkpoint إذا:
- تم اكتشاف مشكلة **Critical** أو **High** تتطلب إيقاف التنفيذ.
- ظروف بيئية (الخادم متوقف، قاعدة البيانات معطلة).
- قرار من منسق المعاينة أو المالك.
- تم استنفاد الوقت المخصص للجلسة.

### استئناف (Resume)

يتم الاستئناف من آخر Checkpoint مسجل في `owner-operational-validation-execution.md`:
1. قراءة آخر نقطة مسجلة (stage، test، timestamp).
2. التحقق من أن البيئة في الحالة نفسها (أو إعادة تشغيل الخدمات).
3. استئناف من نفس المرحلة والفحص الذي توقف عنده.
4. تحديث `last_checkpoint` في execution log.

---

## 8. المسؤوليات

| الدور | المسؤول |
|-------|---------|
| **Project Owner / End-User** | تنفيذ المراحل اليدوية (UI/UX، Browser Review، Final Review)، اتخاذ القرار النهائي |
| **Implementation Engineer** | إعداد البيئة، تنفيذ الأتمتة، تسجيل المشكلات، إدارة الـ Checkpoints |
| **QA Observer** | مراقبة التنفيذ، التحقق من الأدلة، تحديث الـ Issues Registry |
| **Project Manager** | تنسيق الجلسة، إدارة الوقت، رفع التقرير النهائي |

---

## 9.酮宿 الأحكام

**أتمتة:**
- تشغيل عبر `python scripts/run_ov_stage_automated.py --stage N` لكل مرحلة قابلة للأتمتة.
- كل script يُنتج JSON output يمكن التحقق منه.

**يدوي:**
- checklist تعريفية يُملأ يدوياً لكل مرحلة.
- screenshots تُأخذ يدوياً أو عبر browser automation مع تقييم بشري.

**مدة التنفيذ المستهدفة:**
- الأتمتة: 30–60 دقيقة لجميع المراحل الآلية.
- اليدوي: 2–4 ساعات (UI/UX + Browser + Final Review).
- الإجمالي المستهدف: **4 ساعات** في جلسة واحدة، مع إمكانية التوقف والاستئناف.

---

**Plan Status:** Ready for Execution  
**Approval Required:** Project Owner before Stage 1  
**Execution Sequence:** Stage 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8  
**Blocking Dependencies:** Environment ready, data seeded, Project Owner availability
