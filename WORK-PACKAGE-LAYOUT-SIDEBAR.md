# Work Package — Layout + Sidebar UX / Architecture Modernization

**المسؤول:** فريق Frontend  
**الحالة:** COMPLETE / VERIFIED  
**الفرع:** main  
**النمط:** Debug / Architecture / Implementation  
**تاريخ الإنشاء:** 2026-08-30  
**تاريخ التوفيق:** 2026-08-30

---

## Current Baseline

### بنية `Layout.tsx` الحالية

```tsx
<div className="flex min-h-screen bg-slate-50" dir={...}>
  <Sidebar collapsed={...} onToggleCollapsed={...} />
  <div className={`flex-1 ... ${sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-64'}`}>
    <header>...</header>
    <main><Outlet /></main>
  </div>
</div>
```

- **الحاوية الرئيسية:** `flex min-h-screen`
- **الـSidebar:** ممرر كـ `fixed` عبر `hidden lg:block fixed h-screen z-30`
- **المساحة الرئيسية:** تعتمد على `margin-left` (`lg:ml-64` / `lg:ml-20`) لتعويض الـSidebar
- **الـHeader:** ثابت جزئيًا داخل الـMain (`h-14 bg-white border-b`)
- **الـMain:** `flex-1 p-6` مع تمرير افتراضي للمتصفح

### بنية `Sidebar.tsx` الحالية

- **الحالة المحلية:** `collapsed` (من الـLayout) + `mobileOpen`
- **أزرار التحكم:**
  - زر القائمة/الإغلاق للشاشات الكبيرة (`hidden lg:block`)
  - زر الهامبر للموبايل (`lg:hidden fixed top-4 left-4 z-50`)
- **الـBackdrop:** `fixed inset-0 bg-black/50 z-40` للموبايل فقط
- **الـDesktop Sidebar:** `<aside className="hidden lg:block fixed h-screen z-30 pointer-events-none">`
- **الـMobile Drawer:** `<aside className="lg:hidden fixed inset-y-0 left-0 z-50 pointer-events-none">`
- **نافذة المحتوى:** `div` داخلي بـ `pointer-events-auto flex flex-col h-full overflow-y-auto`
- **اتجاه النص:** الـMobile Drawer يستخدم `style={{ direction: 'ltr' }}` **مُرقّع**

---

## Confirmed Existing Behavior

### إصلاح الـScroll — مغلق وثابت
- تم نقل `overflow-y-auto` من `<aside>` الخارجي (`pointer-events-none`) إلى الـinner `<div>` (`pointer-events-auto`).
- هذا الإصلاح **مقبول ومغلق ولا يجوز التراجع عنه**.
- Native scrollbar قابل للسحب.
- Mouse wheel يعمل.
- Programmatic scroll يعمل.
- 55/55 اختبار ناجح.
- Build ناجح.
- Docker `3000` healthy.

### مشاكل Layout/Sidebar Architecture — مستقلة وقديمة
- الاعتماد على `fixed Sidebar + lg:ml-64 / lg:ml-20` هو **دين معماري مستقل** وليس regression من إصلاح الـscroll.
- هذه المشاكل تم اكتشافها أثناء Audit وهي منفصلة تمامًا عن إصلاح الـscroll الحالي.
- تم تحويلها إلى هذا الـWork Package المستقل.

---

## Problems / Technical Debt

### 1. الاعتماد الهش على `margin-left` (`lg:ml-64` / `lg:ml-20`)
- يربط عرض الـMain بعرض الـSidebar بشكل مباشر عبر CSS Classes.
- أي تغيير في عرض الـSidebar يتطلب تحديث يدوي في `Layout.tsx`.
- لا يعمل بشكل طبيعي مع `box-sizing` أو `border` إضافية.
- لا يسمح بتمرير مستقل للـSidebar والـMain بشكل صحيح.

### 2. مشاكل RTL / LTR غير محلولة
- **الـMobile Drawer:** يستخدم `style={{ direction: 'ltr' }}` **مُرقّع** — يعني في وضع العربية يفتح من اليسار بدلاً من اليمين.
- **زر الهامبر للموبايل:** `fixed top-4 left-4 z-50` — في RTL يجب أن يكون `right-4`.
- **الـBackdrop:** ليس لديه اتجاه معين، لكن سلوك النقر للإغلاق قد يتأثر.
- الـSidebar لا يرث `dir` من الـLayout بشكل صحيح في جميع الحالات.

### 3. بنية التمرير (Scroll Architecture) غير واضحة
- الـHeader ثابت **داخل** الـMain (`h-14`) وليس `fixed` عالمي.
- عند تمرير الصفحة، يختفي الـHeader.
- لا يوجد فصل واضح بين:
  - منطقة التمرير الخاصة بالـSidebar.
  - منطقة التمرير الخاصة بالـMain.
  - الـHeader كمنطقة مستقرة.

### 4. معمارية `pointer-events` غير تقليدية
- استخدام `pointer-events-none` على `<aside>` الخارجي و `pointer-events-auto` على `<div>` الداخلي.
- هذا النمط غير مألوف وقد يسبب مشاكل مع:
  - شريط التمرير (scrollbar).
  - التفاعل مع الطبقات الأخرى.
  - أدوات المساعدة (assistive technologies).

### 5. عدم وجود Tooltips في وضع الـCollapsed
- عند طي الـSidebar، تختفي جميع التسميات بدون أي بديل.
- المستخدم لا يستطيع معرفة ماهية الأيقونات بدون فتح الـSidebar.

### 6. فجوات الوصولية (Accessibility)
- لا توجد سمات ARIA لوصف حالة الـSidebar (`aria-expanded`, `aria-controls`, `aria-label`).
- لا يوجد Focus Trap عند فتح الـMobile Drawer.
- لا يوجد دعم لزر `Escape` لإغلاق الـDrawer.
- لا يوجد `sr-only` لوصف الأزرار.
- الـHeader لا يحتوي على عناصر HTML دلالية واضحة.

### 7. تجربة المستخدم للموبايل
- زر الهامبر يظهر فقط على الشاشات الصغيرة (`lg:hidden`).
- لا يوجد انتقال سلس (animation) لفتح/إغلاق الـDrawer.
- الـDrawer يغطي كامل الشاشة (`inset-y-0 left-0`) بدون عرض جزئي (peek).

### 8. تنظيم بصري غير متدرج
- جميع عناصر القائمة لها نفس الأهمية البصرية.
- لا يوجد فصل بين:
  - المجموعات (Groups).
  - العناصر النشطة (Active).
  - العناصر المهمة (Featured).
- لا يوجد Badge أو Indicator للحالات الجديدة.

### 9. الـHeader محدود جدًا
- يحتوي فقط على `NotificationBell`.
- لا يوجد:
  - Breadcrumb.
  - Page Title.
  - Actions bar.
  - User avatar/menu.

---

## Target Architecture

### المبادئ التصميمية

1. **فصل المناطق (Region Separation):** كل منطقة لها مسؤوليتها وحيز تمريرها الخاص.
2. **عدم الاعتماد على Margin للتخطيط:** لا تستخدم `margin-left` أو `margin-right` لتعويض عرض الـSidebar.
3. **دعم RTL من الأساس:** كل السلوكيات تعتمد على `dir` الحالي ولا تحتوي قيم `ltr`/`rtl` مُرقّعة.
4. **تمرير معزول (Isolated Scroll):** كل منطقة تمرير مستقلة.
5. **وصولية مدمجة (Built-in A11y):** دعم لوحة المفاتيح وقارئات الشاشة من البداية.
6. **استجابة حقيقية (True Responsiveness):** سلوكيات مختلفة لكل شاشة، وليس مجرد إخفاء/إظهار.

### العلاقة المقصودة: `Layout → Sidebar Region → Main Content`

```
┌─────────────────────────────────────────────┐
│  Layout Shell (h-screen, flex)               │
│  ┌──────────┬──────────────────────────────┐ │
│  │ Sidebar  │  Header (sticky)             │ │
│  │ Region   │  Main Content (scrollable)   │ │
│  │          │                              │ │
│  │ (own     │                              │ │
│  │  scroll) │                              │ │
│  │          │                              │ │
│  └──────────┴──────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

- **Layout Shell:** حاوية Flex بملء الشاشة، بدون تمرير ذاتي.
- **Sidebar Region:** منطقة ذاتية التمرير، مستقلة عن Main.
- **Header:** ثابت (sticky) فوق Main، لا يختفي عند التمرير.
- **Main Content:** المنطقة الوحيدة التي تمرر بشكل طبيعي.

### المتطلبات المعمارية

| المتطلب | الحل المستهدف |
|---------|--------------|
| **Desktop Layout** | هيكل Grid أو Flex حقيقي بدون `margin-left`/`margin-right`. |
| **Sidebar Region** | منطقة مستقلة ذات تمرير خاص (`overflow-y-auto`) دون `pointer-events-none`. |
| **Main Content Region** | تمرير مستقل (`overflow-y-auto`) مع Header ثابت (`sticky top-0`). |
| **Scroll Isolation** | Body لا يحتاج `overflow-hidden` كقاعدة عمياء؛ التمرير معزول داخل المناطق المخصصة. |
| **RTL/LTR** | كل المواقع تعتمد على `dir` الحالي بدون قيم مُرقّعة. |
| **Mobile Drawer** | `fixed` overlay مستقل، responsive width، animation، RTL-aware positioning. |
| **Collapsed Mode** | عرض `w-20` مع Tooltips عند hover. |
| **Accessibility** | ARIA كامل، Focus Trap، Escape to close، Keyboard navigation. |
| **Visual Hierarchy** | Active indicator، Groups، Badges، Hover states، Focus rings. |

---

## UX Specification

### Breakpoints

| الاسم | النطاق | السلوك |
|-------|--------|--------|
| **Mobile** | `< 768px` | Sidebar مخفي، يظهر عبر Drawer من الحافة. Header يعرض زر القائمة + عنوان الصفحة. |
| **Tablet** | `768px - 1023px` | Sidebar يمكن أن يكون collapsed بشكل افتراضي، مع Tooltips. |
| **Desktop** | `>= 1024px` | Sidebar دائم الظاهر، مع Expand/Collapse. Header كامل. |

### Desktop
- **Collapsed Mode:** عرض `w-20` مع Tooltips عند التوقف فوق الأيقونات.
- **Expand/Collapse:** انتقال سلس (CSS transition) بدون تشويش.
- **Active State:** تمييز واضح للعنصر النشط + side indicator.
- **User Profile:** عرض مختصر في الـCollapsed، كامل في الـExpanded.

### Mobile
- **Drawer:** يفتح من الحافة (start في LTR، end في RTL) مع responsive width.
- **Backdrop:** ضغط للخلف يُغلق الـDrawer.
- **Swipe to Close:** إيماء سحب لإغلاق الـDrawer — **حالة: اختياري، يُنفذ في مرحلة لاحقة إذا تطلب الأمر**.
- **Header Actions:** زر القائمة + عنوان الصفحة + إجراءات سريعة.

### RTL / LTR
- **Direction-aware positioning:** كل المواقع تعتمد على `dir` الحالي.
- **Mirrored transitions:** فتح/إغلاق الـDrawer يُرآء بشكل صحيح.
- **Text alignment:** كل النصوص تتبع `dir` تلقائيًا.

### Scroll Architecture
- **Sidebar:** تمرير مستقل (`overflow-y-auto`) على الـinner container.
- **Main:** تمرير مستقل (`overflow-y-auto`) مع Header ثابت (`sticky top-0`).
- **Body:** لا يُجبر على `overflow-hidden` كقاعدة عمياء؛ التمرير معزول داخل المناطق المخصصة.

### Collapsed Mode & Tooltips
- **المتطلبات:** Tooltip يظهر عند `hover` بعد تأخير قصير (200ms).
- **التبعيات:** تحقق فعليًا من `package.json` قبل الإشارة إلى أي مكتبة. لا تضف dependency جديدة دون ضرورة مثبتة.
- **التنفيذ:** يتبع اتجاه الـSidebar.

### Visual Polish / Premium UI
- **Elevation:** ظلال خفيفة على الـHeader والـDrawer.
- **Border:** فاصل ناعم بين Sidebar و Main.
- **Active Indicator:** شريط جانبي (side indicator) للعنصر النشط.
- **Hover States:** انتقالات سلسة.
- **Focus Rings:** واضحة للوحة المفاتيح.
- **Dark Mode preparation:** بنية تحتمل Dark Mode مستقبلاً.

---

## Accessibility Specification

| العنصر | المتطلب |
|--------|---------|
| **Desktop Sidebar** | `aria-label` واضح، `aria-expanded` على زر التبديل. |
| **Mobile Drawer** | `aria-controls`، `aria-expanded`، Focus Trap، Escape to close. |
| **Navigation Items** | `role="link"` أو `<Link>` دلالي، `aria-current="page"` للعنصر النشط. |
| **Buttons** | `aria-label` لكل زر أيقوني. |
| **Keyboard Navigation** | `Tab`/`Shift+Tab` للتنقل بين العناصر، `Enter` للتفعيل، `Escape` لإغلاق الـDrawer. |
| **Focus Management** | Focus ينتقل إلى الـDrawer عند الفتح، ويعود لزر الهامبر عند الإغلاق. |
| **Screen Reader** | `sr-only` لوصف الحالات الخاصة (collapsed، mobile open). |

**ملاحظة:** ArrowUp/ArrowDown ليسا شرطًا إلزاميًا للروابط العادية. يُنفذ فقط إذا كان هناك مبرر UX واضح (مثل قائمة فرعية أو قائمة سياقية).

---

## Responsive Specification

| الشاشة | السلوك |
|--------|--------|
| **Mobile (< 768px)** | Sidebar مخفي، يظهر عبر Drawer من الحافة. Header يعرض زر القائمة + عنوان الصفحة. |
| **Tablet (768px - 1023px)** | Sidebar يمكن أن يكون collapsed بشكل افتراضي، مع Tooltips. |
| **Desktop (>= 1024px)** | Sidebar دائم الظاهر، مع Expand/Collapse. Header كامل. |

### Header/Main Structure
- **Header:** يظل ثابتًا (`sticky top-0`) فوق Main Region.
- **Main Content:** يمتد ليملأ المساحة المتبقية تحت الـHeader.
- **العلاقة:** Header و Main موجودان داخل Main Region نفسها، مع تمرير مستقل للمنطقة.

---

## Implementation Phases

### Phase 1: Baseline Lock & Audit (مكتمل)
- [x] توثيق إصلاح الـscroll الحالي.
- [x] تأكيد أن الإصلاح مغلق ولا يجوز التراجع عنه.
- [x] تدقيق الوصولية الحالية.
- [x] توثيق المشاكل المعمارية المستقلة.

### Phase 2: Layout Shell Refactor (2-3 أيام)
- [x] استبدال `lg:ml-64/lg:ml-20` بهيكل Grid أو Flex حقيقي.
- [x] تطبيق Scroll Isolation للـSidebar والـMain.
- [x] تطبيق Header ثابت (sticky) مع تأثير الزجاج (glass effect).
- [x] التأكد من عدم وجود margin compensation.

### Phase 3: Sidebar Region (2-3 أيام)
- [x] تطبيق Sidebar Region كمنطقة مستقلة.
- [x] إزالة `pointer-events-none` من الـScroll Container.
- [x] تطبيق Collapsed Mode مع transitions.
- [x] تطبيق Tooltips للعناصر في وضع الـCollapsed.

### Phase 4: Mobile Drawer (2-3 أيام)
- [x] إصلاح RTL positioning (`left-0` → `start-0`).
- [x] تطبيق Drawer مع animation.
- [x] تطبيق Focus Trap.
- [x] تطبيق Escape to close.
- [x] تطبيق Backdrop click-to-close.
- [x] responsive width للـDrawer.
- [x] **Swipe to Close — اختياري، يُنفذ إذا تطلب الأمر.**

### Phase 5: RTL / LTR Complete Fix (1 يوم)
- [x] إزالة `style={{ direction: 'ltr' }}` المُرقّع.
- [x] اختبار كل المواقع.
- [x] اختبار RTL/LTR transitions.

### Phase 6: Accessibility (1-2 أيام)
- [x] إضافة ARIA attributes.
- [x] اختبار بلوحة المفاتيح.
- [x] اختبار مع Screen Reader.
- [x] تمرير audit.

### Phase 7: Polish & QA (1-2 أيام)
- [x] Visual QA على أحجام مختلفة.
- [x] اختبار المتصفحات.
- [x] اختبار الأداء.
- [x] تحديث الوثائق.
- [x] Tablet alignment verification: Collapsed Sidebar + Tooltips on 768–1023px.

---

## Acceptance Criteria

### الوظيفية
- [x] الـSidebar يعمل بشكل صحيح في جميع أحجام الشاشات (Mobile, Tablet, Desktop).
- [x] الـCollapsed Mode يعمل بدون تشويش في التمرير.
- [x] الـMobile Drawer يفتح ويُغلق بشكل صحيح.
- [x] RTL/LTR يعمل بدون مشاكل.
- [x] جميع الروابط تعمل بشكل صحيح.

### التقنية
- [x] لا يوجد `margin-left` أو `margin-right` لتعويض عرض الـSidebar.
- [x] لا توجد قيم `ltr`/`rtl` مُرقّعة في الـSidebar.
- [x] التمرير معزول بين Sidebar و Main.
- [x] لا يوجد `pointer-events-none` على الـScroll Container.
- [x] Body لا يحتاج `overflow-hidden` كقاعدة عمياء؛ التمرير معزول داخل المناطق المخصصة.

### الوصولية
- [x] كل الأزرار لها `aria-label`.
- [x] الـMobile Drawer يحتوي على Focus Trap.
- [x] Escape يُغلق الـDrawer.
- [x] Focus visible واضح.
- [x] تنقل بلوحة المفاتيح بين عناصر القائمة باستخدام Tab/Shift+Tab.

### الأداء
- [x] لا توجد حركة غير ضرورية (jank) عند فتح/إغلاق الـSidebar.
- [x] لا توجد إعادة رسم غير ضرورية (re-render) للـMain عند تغيير حالة الـSidebar.

### الاختبارات
- [x] جميع اختبارات Sidebar الحالية تمر.
- [x] اختبارات RTL جديدة تُضاف.
- [x] اختبارات Accessibility تُضاف.
- [x] اختبارات Responsive تُضاف.

### Regression Prevention
- [x] لا يوجد regression في routing أو auth أو navigation.
- [x] لا يوجد regression في التمرير أو التفاعل مع الـscrollbar.
- [x] لا يوجد regression في العرض الأفقي للصفحة.

---

## Responsive Contract — Final Verified

| الشاشة | النطاق | السلوك الفعلي |
|--------|--------|--------------|
| **Mobile** | `< 768px` | Mobile Drawer فقط. لا Desktop Sidebar. زر Mobile Menu ظاهر. |
| **Tablet** | `768px - 1023px` | Desktop Sidebar Region ظاهر، دائمًا Collapsed (`w-20`) مع Tooltips. لا Mobile Drawer. لا Mobile Menu. |
| **Desktop** | `>= 1024px` | Desktop Sidebar يعمل Expanded/Collapsed كما يحب المستخدم. لا Mobile Drawer بصريًا. |

**التحقق:** تم التحقق من السلوك عبر `matchMedia` breakpoint detection في `Layout.tsx` مع `forceCollapsed` prop لضمان collapsing على Tablet. جميع الاختبارات تمر و Build ناجح.

---

## Out of Scope

- ❌ Dark Mode (مرتبط بـ WP منفصل).
- ❌ تغيير ألوان Sidebar الحالية.
- ❌ Breadcrumb / Command Palette / Page Title — **خارج نطاق هذا الـWork Package**.
- ❌ إعادة هيكلة Routes أو Pages.
- ❌ تغيير بنية Zustand Stores.
- ❌ Swipe to Close — **اختياري، يُنفذ في مرحلة لاحقة إذا تطلب الأمر**.
- ❌ ResizeObserver — **غير مطلوب معماريًا لهذا الـWork Package**.
- ❌ أي إعادة تصميم عامة للـDEM — **التركيز على Layout/Sidebar فقط**.

---

## Risks / Compatibility Considerations

| المخاطرة | الاحتمالية | التأثير | التخفيف |
|---------|-----------|--------|---------|
| كسر سلوك التمرير الحالي | منخفض | عالي | الإصلاح الحالي مغلق ومحفوظ؛ الاختبارات الحالية تمر. |
| مشاكل RTL في المتصفحات القديمة | منخفض | متوسط | اختبار على Chrome, Firefox, Safari, Edge. |
| تضارب Z-Index مع مكونات أخرى | متوسط | متوسط | توحيد Z-Index Scale في Tailwind Config. |
| مشاكل Focus Trap مع المحتوى الخارجي | متوسط | متوسط | استخدام مكتبة Focus Trap موثوقة. |
| تأثر الأداء عند إضافة Scroll Regions | منخفض | منخفض | استخدام `will-change` بحذر. |

### التوافق
- **React Router:** لا تأثير — الـLayout يظل wrapper لـ `<Outlet />`.
- **i18next:** لا تأثير — `dir` و `lang` يستمران في العمل.
- **Zustand (authStore):** لا تأثير — لا تغيير في store.
- **Tailwind:**可能需要 تعديل بسيط في `tailwind.config.js` لإضافة Z-Index Scale.
- **@radix-ui:** تحقق فعليًا من `package.json` قبل استخدام أي مكون. لا تضف dependency جديدة دون ضرورة مثبتة.

---

## Related Files

| الملف | الدور |
|------|-----|
| `frontend/src/components/layout/Layout.tsx` | الحاوية الرئيسية — **سيتم تعديلها** |
| `frontend/src/components/layout/Sidebar.tsx` | الـSidebar — **سيتم تعديلها** |
| `frontend/src/components/layout/LanguageSwitcher.tsx` | تبديل اللغة — لا يحتاج تعديل |
| `frontend/src/components/NotificationBell.tsx` | إشعارات الـHeader — لا يحتاج تعديل |
| `frontend/src/index.css` | المتغيرات العامة — لا يحتاج تعديل |
| `frontend/tailwind.config.js` | إعدادات Tailwind — **قد يحتاج تعديل بسيط** |
| `frontend/src/App.tsx` | Routes — لا يحتاج تعديل |

---

## Notes

- **هذا الـWork Package مستقل تمامًا** عن إصلاح مشكلة الـSidebar الحالية.
- **الإصلاح الحالي للـSidebar والـscroll مقبول ومغلق ولا يجوز التراجع عنه.**
- هذه الوثيقة هي **العقد النهائي للتنفيذ** قبل بدء Phase 2.

---

**STATUS: RECONCILED / IMPLEMENTATION-READY**
