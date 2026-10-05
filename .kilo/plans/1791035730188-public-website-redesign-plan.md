# Nile Key — Public Website Redesign Plan (Corrected Single Source)

> **حالة الملف:** هذه المراجعة الجذرية تستبدل محتوى الخطة السابق بالكامل (بما في ذلك كتلة "VISUAL SOURCE OF TRUTH OVERRIDE" القديمة وكتلة "Concept 1 — Visual Design Execution Specification" القديمة). لا توجد طبقات مواصفات متعددة؛ هذا الملف كله هو المصدر الواحد.

---

## 0. Source of Truth / Content Source / Technical Constraint

| النوع | المصدر |
|-------|--------|
| **Visual Source of Truth** | `frontend/public/design-reference/concept1.png` (438 × 1199 PNG). منطقة الـRuntime تنتهي عند Footer تقريبًا عند y≈1148. المنطقة من y≈1150 حتى نهاية الصورة والتي تعرض `3. Full Homepage Concept` هي عنوان/شرح خارجي وتُتجاهل — ليست جزءًا من Runtime Home. |
| **Content Source** | المحتوى النصي الموجود فعليًا في المشروع (`src/locales/en/translation.json`, `src/locales/ar/translation.json`, المحتوى المؤسسي الحالي). لا يُخترع محتوى. |
| **Technical Constraint** | الكود والبنية الحالية (`App.tsx`, `PrivateRoute`, `Layout`, DEM, Backend). لا تُعاد هيكلتها. |

**قاعدة الحاكمية:** أي تعارض بين أي نص سابق أو Blueprint أو Override وبين هذا الملف → هذا الملف هو الأعلى. لا يُضاف Override جديد فوق تعارض؛ يُحذف التعارض نفسه.

---

## 1. Final PublicHome Composition

التكوين الحاكم الوحيد (من أعلى الصفحة إلى أسفلها):

```
Navbar
→ Hero
→ Our Company
→ Premium Egyptian Products
→ The Export Journey
→ Digital Platform
→ Our Presence in Global Markets
→ Trusted by Global Partners / Let's Grow Together
→ Footer
```

**9 عناصر إجمالًا: Navbar + 7 أقسام محتوى + Footer.**

ممنوع نهائيًا:
- Feature Band كقسم مستقل (يُحذف من التنفيذ الحالي).
- Global Closing Banner كقسم مستقل (يُحذف من التنفيذ الحالي).
- حذف The Export Journey أو Digital Platform أو Global Markets.
- تقسيم الصفحة إلى 6 أو 7 أقسام.
- alternating light/dark pattern لمجرد التنظيم.

### 1.1 النسب المرجعية للارتفاعات (من الصورة 438×1199، منطقة Runtime ≈1148px)

| # | القسم | الارتفاع المرجعي | النسبة من الصفحة | الهدف التقريبي عند Desktop |
|---|-------|------------------|------------------|----------------------------|
| 1 | Navbar | ≈46px | ≈4.0% | 64–72px |
| 2 | Hero | ≈207px | ≈18.0% | 560–720px (أطول قسم — نطاق مطلق، ليس vh) |
| 3 | Our Company | ≈151px | ≈13.2% | 420–520px |
| 4 | Premium Egyptian Products | ≈169px | ≈14.7% | 460–560px |
| 5 | The Export Journey | ≈133px | ≈11.6% | 360–440px |
| 6 | Digital Platform | ≈129px | ≈11.2% | 340–420px |
| 7 | Our Presence in Global Markets | ≈114px | ≈9.9% | 320–400px |
| 8 | Trusted by Global Partners / Let's Grow Together | ≈96px | ≈8.4% | 260–320px |
| 9 | Footer | ≈101px | ≈8.8% | 280–340px |

**القاعدة:** النسب النسبية هي الحاكمة (Hero > Products > Our Company > Journey > Digital > Markets > Footer > Trust/CTA). القيم التقريبية لـ Desktop أهداف قابلة للقياس في Visual QA، وليست CSS pixels حرفية من الصورة المصغرة.

**قاعدة ارتفاع Hero النهائية (تحل محل أي قاعدة vh في كل أجزاء الخطة):** ارتفاع Hero يُحدد بنطاق px مطلق حسب breakpoint (انظر 5.2) — **لا يُقاس بـ vh ولا ينمو مع ارتفاع الـviewport**. عند viewport أطول من 1080px يبقى Hero داخل 560–720px ولا يتضخم. النسبة البصرية ≈18% من إجمالي صفحة المرجع تُحققها النطاقات المطلقة وتُفحص في Visual QA عند 1440px و1280px.

---

## 2. Global Container & Rhythm

- المرجع يستخدم هامشًا داخليًا صغيرًا متكررًا: على عرض 438px يبدأ المحتوى عند x≈14px وينتهي عند x≈414px → **محتوى ≈91–92% من العرض، هامش جانبي ≈3.2% لكل جهة**.
- **قاعدة الـContainer النهائية (قاعدة واحدة غير قابلة لتفسيرين):**
  - **العرض الخارجي للمحتوى:** `width: min(92vw, 1280px)`، `mx-auto` — أي ≈92% من عرض الـviewport **مقفولًا (capped) بحد أقصى 1280px**.
  - عند viewport ≤1391px: المحتوى = 92vw (مثال: 1280px viewport → ≈1178px؛ 375px mobile → ≈345px).
  - عند viewport >1391px: المحتوى = 1280px (الحد الأقصى يحكم، والنسبة الفعلية تصبح <92% — وهذا مقصود وليس تعارضًا).
  - **لا يوجد padding أفقي داخلي إضافي** داخل الـwrapper عند أي breakpoint — الهامش الجانبي ≈4% لكل جهة (الناتج من قاعدة 92%) هو الـgutter نفسه ويطابق إيقاع المرجع (≈3.2% لكل جهة عند 438px). خلفيات الأقسام تبقى full-bleed (100vw).
  - هذه القاعدة تستبدل قاعدة `max-width: 1280px + px-4 sm:px-6 lg:px-8` القديمة التي كانت تُنتج ≈88.9% فقط عند 1440px.
- الأقسام full-width الخلفيات، والمحتوى داخل الـcontainer.
- **لا توجد مسافات خارجية بين الأقسام** — الأقسام متلاصقة مباشرة (section transition مباشر). المساحات البيضاء/الفارغة داخلية فقط (vertical padding داخل كل قسم).
- لا تُلمس العناصر حواف الشاشة. نفس الإيقاع الأفقي يتكرر بين الأقسام.
- لا يُستبدل التركيب الأصلي بنظام بطاقات عام أو alternating sections.

---

## 3. Palette (Single Source — مستخرجة من concept1.png)

| الدور | القيمة التقريبية |
|-------|------------------|
| Main dark teal (سطوح الأقسام الداكنة) | `#043B3E` |
| Deeper teal (Footer، العناصر الخلفية، التمييز الدقيق بين قسمين متجاورين) | `#022F32` |
| Emerald accent (eyebrows، أرقام الإحصائيات، العلامات النشطة، CTA primary) | `#19D8B0` |
| Light trust surface (اللوحة اليسرى في قسم Trust فقط) | `#F4F6F2` |
| Primary text on dark | `#FFFFFF` |
| Secondary text on dark | teal-gray ≈ white at 60–75% opacity (≈`#B9CFCC`) |

**قواعد Palette:**
- الصفحة تعتمد بدرجة كبيرة على dark teal surfaces.
- Light surface يظهر **فقط** في اللوحة اليسرى لقسم Trusted by Global Partners.
- لا alternating light/dark pattern لمجرد التنظيم.
- لا gradients كحل عام في الأقسام. الاستثناء الوحيد المسموح: scrim اتجاهي لقراءة النص في Hero، وscrim داكن خلف نص عناصر المنتجات (كلاهما جزء من المرجع وليس حلًا عامًا).
- لا glass cards غير الموجودة في المرجع.
- Our Company وProducts أقسام **داكنة** (ليست فاتحة/بيضاء).

---

## 4. Typography Specification

نفس الـfont family الموجود في المشروع (Tailwind default sans) للإنجليزية والعربية. لا fonts خارجية جديدة.

| العنصر | الحجم | الوزن | ملاحظات |
|--------|-------|-------|---------|
| Eyebrow | 12–14px | 400 | uppercase، tracking 0.12–0.16em، لون `#19D8B0` |
| Section title | 28–36px (Desktop) | 700 | أبيض، line-height 1.2 |
| Subtitle | 15–18px | 400–600 | white-80 |
| Body | 14–16px | 400 | line-height 1.6 (EN) / 1.8 (AR) |
| CTA text | 14–16px | 500–600 | — |
| Hero main title | 44–64px (Desktop) | 800 | أبيض، line-height 1.1 |
| Stat number | 28–36px | 700 | `#19D8B0` |
| Footer column heading | 11–13px | 600 | uppercase، tracking 0.14–0.18em، accent |

- العربية: نفس الأحجام والأوزان، line-height 1.8.
- جميع الـsection headings في PublicHome بنفس المستوى (28–36px/700). لا hierarchy متضاربة.
- spacing قياسي: eyebrow→title 12–16px، title→subtitle/description 12–20px، description→CTA 24–32px.

---

## 5. Section-by-Section Visual Specification

### 5.1 Navbar

- **Surface:** شريط Dark Teal مستقل وواضح (`#043B3E`، sticky top، border-b white/10).
- **الارتفاع:** 64–72px Desktop، 56–60px Mobile.
- **التركيب الأفقي (LTR):** Logo+Brand (يسار) → روابط التنقل (وسط: Home / About / Products / Services / Markets / Contact) → Language switcher + Login + Create Account (يمين).
- **Logo:** علامة "NK" داخل مربع/دائرة accent + "Nile Key" + سطر صغير "Digital Export Platform".
- **الحالة النشطة:** Home هو الرابط النشط بصريًا بعلامة accent أسفل/حول الرابط.
- **Mobile:** hamburger menu يحتوي كل الروابط + Language + Login + Create Account.
- **لا يتحول إلى private shell** — يبقى public navigation.
- **الحالة الحالية:** `PublicNavbar.tsx` قريب من المرجع؛ المطلوب فقط: (1) إضافة Home active accent mark، (2) تحديث الألوان للـPalette الجديدة. لا إعادة تصميم من الصفر.

### 5.2 Hero

- **الارتفاع المرجعي:** ≈18% من الصفحة.
- **قاعدة الارتفاع النهائية (واحدة فقط — لا vh):**
  - Desktop (≥1280px): **560–720px** (هدف ≈640px). نطاق مطلق **لا يُقاس بـ vh ولا ينمو مع ارتفاع الـviewport** — عند viewport أطول من 1080px يبقى Hero داخل 720px كحد أقصى.
  - Laptop (1024–1279px): 480–600px.
  - Tablet (768–1023px): 420–520px.
  - Mobile (<768px): 420–520px (content-driven؛ يُسمح بـ `min-height: 420px` كحد أدنى فقط، وأي استخدام لـ vh يجب أن يكون **مقفولًا بسقف 520px** — ممنوع `min-height: 60vh` غير المقفول لأنه يُضخّم Hero على الشاشات الطويلة).
  - التحقق: النسبة البصرية ≈18% من إجمالي الصفحة تُفحص في Visual QA عند 1440px و1280px.
- **الخلفية:** صورة فوتوغرافية ممتدة بعرض الصفحة كاملًا (Nile / Egyptian landscape / pyramids / palm scenery) — `absolute inset-0`, `object-cover`.
- **الـScrim:** تعتيم Dark Teal واضح في جهة النص (يسار في LTR): overlay اتجاهي من `#022F32`/90 (جهة النص) عبر `#022F32`/50 إلى شفاف. هذا scrim اتجاهي لقراءة النص فقط وليس gradient عامًا.
- **طبقة foreground:** طبقة بصرية واضحة للخضروات المصرية في أسفل/يمين Hero (عنصر foreground قوي) — **ASSET GAP** (انظر القسم 6). في RTL تنعكس تلقائيًا (أسفل/يسار).
- **النص:** الجهة اليسرى في LTR، عرض ≈46–50% من عرض الـcontainer أو أقل بقليل، محاذاة رأسية center. النص لا يتوسط الصفحة.
- **محتوى النص (بالترتيب):**
  1. Eyebrow: `EGYPTIAN PRODUCTS • GLOBAL MARKETS` / `منتجات مصرية • أسواق عالمية`
  2. العنوان الرئيسي: `Nile Key` / `مفتاح النيل` (44–64px/800)
  3. سطر عربي للمسمى المؤسسي: `شركة مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م)`
  4. سطر إنجليزي للمسمى المؤسسي: `Nile Key for Investment and International Trade LLC` (السطران يظهران في كلتا اللغتين كما في المرجع)
  5. Description قصير (`public.home.heroDescription`)، 15–16px، white-70، max-width ≈520px
  6. زران متجاوران مباشرة أسفل الوصف (ليسا على حافة القسم)
- **CTA:** كلاهما **pill-shaped / very high radius** (`rounded-full`)، ارتفاع ≈44–48px، gap 12–16px:
  - Primary: Filled Emerald — خلفية `#19D8B0`، نص `#022F32`، `Get Started` → `/services`
  - Secondary: Transparent/Dark مع outline واضح — border white/40، نص white، `Learn More` → `/about`
- **Spacing الداخلي:** py-20 Desktop / py-14 Tablet / py-10 Mobile (داخل الـcontainer).
- **Mobile:** stacked — النص أولًا مع الحفاظ على prominence، طبقة الخضروات تُ reposition أسفل/خلف النص، CTA stacked عموديًا full-width، لا تتحول الصورة إلى thumbnail.
- **Transition:** مباشر إلى Our Company (كلاهما داكن، لا gap).
- **ممنوع:** Hero ككتلة بيضاء، Hero كـrounded standalone card، فرض نسبة 45/55 كثابت، استخدام screenshot كامل كـHero asset، اعتبار `hero-export.jpg` صالحًا قبل Asset Audit (ثبت أنه composite — ممنوع).

### 5.3 Our Company

- **الارتفاع المرجعي:** ≈13.2% (420–520px Desktop).
- **Surface:** Dark Teal solid `#043B3E`. **ممنوع تحويله إلى Light surface.**
- **التركيب:** two-column:
  - النص: الجهة اليسرى في LTR، ≈48–50% من inner width.
  - الصورة: الجهة اليمنى في LTR، ≈42–44% من inner width.
  - فجوة واضحة بين العمودين: 32–48px.
  - المحاذاة الرأسية: center.
- **العنوان:** `Our Company` / `شركتنا` (eyebrow `OUR COMPANY` / `عن الشركة`). **ممنوع** استخدام `More Than a Trading Company / We Are Your Global Partner` كعنوان تصميمي (نص من Override سابق وليس من المرجع).
- **النص:** مختصر ومتكامل (1–2 جملة تصف الشركة ومنتجاتها) مبني من المحتوى المؤسسي الموجود (`public.home.companySummaryP1` مختصرًا). ليس 3 فقرات.
- **CTA:** `Learn More` → `/about` (رابط accent 15–16px/600).
- **الصورة:** Egyptian visual (أهرامات/نيل/قارب شراعي)، واضحة وكبيرة، **aspect ratio 4/3**، `border-radius: 16px` (rounded-2xl)، prominence عالية، **وليست thumbnail**. يوجد إحساس بسيط بوجود backing/offset teal element خلف الصورة (كتلة `#022F32` أو accent/20 offset ≈16–24px خلف الصورة).
- **Mobile:** stacked، الصورة فوق النص (الحفاظ على hierarchy)، aspect ratio محفوظ.
- **Transition:** مباشر.

### 5.4 Premium Egyptian Products

- **الارتفاع المرجعي:** ≈14.7% (460–560px Desktop).
- **Surface:** Dark Teal `#043B3E`. **ممنوع قسم أبيض أو Light cards.**
- **Header (صف واحد):**
  - الجهة اليسرى (LTR): eyebrow `KEY PRODUCTS` / `منتجات رئيسية` + title `Premium Egyptian Products` / `منتجات مصرية مميزة`.
  - الجهة المقابلة (يمين في LTR): `View All Products` / `عرض جميع المنتجات` → `/products` (رابط accent 14–16px/600). **هذا هو الموقع الوحيد لـ View All Products — لا CTA منفصل أسفل القسم.**
- **العناصر:** 3 عناصر متساوية أفقيًا (`grid-cols-3`، gap 24–32px)، **نفس الارتفاع تقريبًا**.
- **كل عنصر:**
  - الصورة هي العنصر البصري الرئيسي، **top-heavy**: aspect ratio ≈4/5 (portrait)، تشغل ≈60–65% من ارتفاع العنصر، `border-radius: 12px`.
  - العنوان (16–18px/600 أبيض) + وصف قصير (13–14px، white-60) مرتبطان مباشرة بالصورة.
  - **overlay/gradient داكن خفيف خلف النص السفلي**: النص يظهر فوق الجزء السفلي من الصورة مع scrim داكن (من شفاف إلى `#022F32`/85) لقراءة النص.
  - borders/radius خفيفة.
- **العناصر الثلاثة:** Vegetables / Fruits / Factory Products (العناوين من `public.products.vegetablesTitle` / `fruitsTitle` / `factoryTitle`، الأوصاف من `*Desc`).
- **Mobile:** عمود واحد (أو 2 ثم 1)، الصور تبقى prominent، لا thumbnails.
- **Transition:** مباشر.

### 5.5 The Export Journey

- **الارتفاع المرجعي:** ≈11.6% (360–440px Desktop).
- **Surface:** Dark Teal (`#022F32` — أعمق قليلًا لتمييز دقيق عن القسم السابق؛ لا alternating pattern).
- **Header:** عنوان `The Export Journey` / `رحلة التصدير` + وصف قصير تحته.
- **الخطوات:** **5 خطوات فقط في Home**، توزيع أفقي:
  - 5 nodes دائرية متقاربة التساوي (قطر 48–56px)، موزعة بالتساوي على عرض الـcontainer (`justify-between` / `grid-cols-5`).
  - كل node يحتوي icon (lucide) + title أسفل الـnode (13–15px/600 أبيض، centered تحت الـnode).
  - **رابط بصري متصل بين الخطوات:** خط أفقي (2–3px، white/15 أو accent/40) يربط مراكز الـnodes، مع **arrows/chevrons** بين الـnodes تدل على الاتجاه.
- **الخطوات الخمس (بالترتيب):**
  1. Farm / Factory — icon `Factory`
  2. Packing & Quality — icon `CheckCircle`
  3. Export Documents — icon `FileText`
  4. Shipping — icon `Truck`
  5. Port & Delivery — icon `Ship`
  - العناوين من `public.markets.step1Title` … `step5Title` (موجودة). الأوصاف (`step*Desc`) تبقى في PublicMarkets فقط، لا تُعرض في Home.
- **Mobile:** تحوّل عمودي/stacked مقروء مع الحفاظ على نفس الخمس خطوات والتسلسل (خط connector عمودي مع arrows)، لا حذف nodes، لا اختراع diagram مختلف.
- **هذا القسم ليس optional.** PublicMarkets صفحة مستقلة يمكن أن تحتوي 6 مراحل حسب محتواها الحالي — لا تُخلط بين Home (5) وPublicMarkets.
- **Transition:** مباشر.

### 5.6 Digital Platform

- **الارتفاع المرجعي:** ≈11.2% (340–420px Desktop).
- **Surface:** Dark Teal `#043B3E`.
- **التركيب:** split visual composition — **Visual في اليسار (≈50–52%)، Text في اليمين (≈48–50%)** (معكوس عن التركيب المعتاد — هذا ما يظهره المرجع)، gap 32–48px، محاذاة رأسية center.
- **Visual:** laptop/interface composition حقيقي — إطار laptop (CSS/HTML build: إطار داكن، rounded 12–16px) بداخله interface/map visual (خريطة/واجهة مبسطة). **ليس abstract illustration، وليس Dashboard مختلقًا من الصفر.** aspect ratio ≈16/10، ارتفاع ≈360–440px Desktop. prominence عالية (نقطة الجذب الأساسية في القسم).
  - **G7 — Visual-Fidelity Constraint:** لا يوجد أصل نظيف لهذا الـvisual في المشروع. CSS/HTML مسموح **كوسيلة تنفيذ فقط** لإعادة بناء composition بصريًا **بنفس هندسة المرجع وعناصره البصرية الأساسية** (إطار laptop + interface/map بداخله) — **ليس كترخيص لتصميم Dashboard جديد**. ممنوع: Dashboard مختلق، بيانات وهمية، UI invented، أرقام أو metrics. **إذا كانت المطابقة البصرية الأمينة للمرجع غير ممكنة → يُسجل Visual/Asset Gap صريحًا، ولا يُعتبر القسم PASS تلقائيًا.**
- **النص (الجهة اليمنى):**
  - eyebrow: `DIGITAL PLATFORM` / `المنصة الرقمية`
  - title بسطرين: `Our Integrated Digital Platform` ثم `for Export Operations` (28–36px/700)
  - description مختصر (من `public.home.platformP1` مختصرًا)
  - CTA: `Learn More` → `/services`
- **ممنوع:** fake operational data، أرقام وهمية، اختلاق محتوى Dashboard، تغيير التركيب إلى device card مختلفة جذريًا.
- **Mobile:** stacked، الـvisual أولًا (الحفاظ على prominence) ثم النص.
- **Transition:** مباشر.

### 5.7 Our Presence in Global Markets

- **الارتفاع المرجعي:** ≈9.9% (320–400px Desktop).
- **Surface:** Dark Teal `#022F32` مع **world visual قوي في الخلفية** (خريطة عالمية مبسطة تمتد عبر السطح، خطوط/nodes بلون accent، شفافية منخفضة تُبقي النص مقروءًا).
  - الـworld visual: **G8 — Visual-Fidelity Constraint:** خريطة عالمية واضحة **بنفس الوظيفة والهيمنة البصرية التي تظهر في المرجع**. CSS/SVG مسموح **كوسيلة تنفيذ مطابقة للمرجع فقط** — silhouette خريطة عالمية حقيقية، لا اختراع شكل جديد. ممنوع: random dots، divs عشوائية، invented map treatment. **إذا كان الوصول إلى visual مطابق بأمانة غير ممكن → يُسجل Visual/Asset Gap صريحًا، ولا يُعتبر القسم PASS تلقائيًا.**
- **المحتوى:** eyebrow صغير + title `Our Presence in Global Markets` / `وجودنا في الأسواق العالمية` + subtitle قصير.
- **الإحصائيات:** في الجزء السفلي من القسم، **3 أعمدة متساوية تقريبًا**، مع **vertical separators** (border-l white/10) بين الإحصائيات:
  - `50+` — Countries (`public.markets.statCountries`)
  - `200+` — Business Partners (`public.markets.statPartners`)
  - `100%` — Commitment to Quality (`public.markets.statQuality`)
  - الرقم: 28–36px/700 `#19D8B0`؛ الـlabel: 13–14px white-60.
- **ممنوع:** قسم أبيض مستقل، نقل القسم إلى Closing Banner، إحصائيات إضافية (فقط الثلاث المعتمدة)، خريطة بديلة عشوائية.
- **Mobile:** stacked، الـworld visual يبقى خلفية، الإحصائيات stacked مع separators أفقية.
- **Transition:** مباشر إلى قسم Trust/CTA.

### 5.8 Trusted by Global Partners / Let's Grow Together

- **الارتفاع المرجعي:** ≈8.4% (260–320px Desktop).
- **التركيب:** Split section متجاور (لوحتان متلاصقتان بدون gap بينهما)، النسبة ≈**51/49**:
  - **اليسار (≈51%): Light/off-white surface `#F4F6F2`** — عنوان `Trusted by Global Partners` / `موثوق من شركاء عالميين` (24–30px/700، نص داكن `#022F32`) + مجموعة trust marks/logos: **أربعة علامات رئيسية: SGS، ISO، HACCP، GLOBALG.A.P.**
  - **اليمين (≈49%): Dark image-based CTA panel** — خلفية صورة مرتبطة بالتجارة/الشحن والسفينة + overlay داكن، title `Let's Grow Together` (`public.home.trustedTitle`)، subtitle (`public.home.trustedDescription`)، CTA button `Contact Us` (`public.home.trustedCta`) → `/contact` (pill، filled accent).
- **ممنوع:** تحويل القسم إلى dark 50/50 text-only، Trust logos كـfake text، SVG fake logos، اختلاق شركاء.
- **ASSET GAPS (إلزامية):**
  1. **G10 — قاعدة العلامات الرسمية:** علامات SGS / ISO / HACCP / GLOBALG.A.P. علامات تجارية خارجية. استخدامها يتطلب **أصلًا رسميًا موجودًا مسبقًا في المشروع، أو أصلًا يقدمه المستخدم/المصدر المعتمد**. ممنوع على Kilo: كتابة اسم العلامة كنص بدل الشعار، رسم SVG من اختراعه، أو اقتباس علامة غير موثقة من مصدر غير معتمد. **إذا لم تتوفر الأصول الرسمية → يبقى Gap، ولا يُعتبر القسم مكتملًا بصريًا.**
  2. صورة الشحن/السفينة للوحة اليمنى (G9) — **Asset Gap** (لا أصل نظيف في المشروع).
- **Mobile:** stacked blocks بنفس الترتيب (Trust أولًا ثم CTA) ونفس الدلالة.
- **Transition:** مباشر إلى Footer.

### 5.9 Footer

- **الارتفاع المرجعي:** ≈8.8% (280–340px Desktop).
- **Surface:** Deep teal `#022F32`، border-t white/10.
- **4 أعمدة على Desktop** (`grid-cols-4`، gap 32–48px):
  1. **Logo + Brand + Digital Export Platform** (علامة NK + Nile Key + السطر الصغير + سطر تعريفي قصير)
  2. **Quick Links** (6 روابط: Home / About / Products / Services / Markets / Contact)
  3. **Contact Us** (فقط بيانات موجودة في المشروع — الموقع: Egypt. **يُحذف أي بريد/هاتف مختلق** مثل `info@nilekey.com` أو `+20 10 0000 0000` الموجودان حاليًا في `PublicFooter.tsx` ولا يوجد مصدر لهما في المشروع)
  4. **Follow Us** — **G11 — قاعدة المنصات المثبتة:** الأحرف النصية الحالية `in` / `f` / `◎` في `PublicFooter.tsx` glyphs مختلقة **ولا تثبت وحدها أسماء المنصات** ويجب إزالتها. **ممنوع افتراض LinkedIn / Facebook / Instagram أو غيرها إلا إذا كانت المنصات/الروابط موجودة فعليًا في المشروع أو مصدر المحتوى الحالي.** إذا كانت الروابط غير موجودة → لا تُخترع المنصات؛ الأيقونات تُستخدم فقط للمنصات المثبتة؛ عدم وجود المنصات/الأيقونات الصحيحة = **Gap** وليس اختراعًا.
- **Copyright** في الأسفل: centered، 13–14px، white-50 (`public.footer.copyright`).
- **لا Services column مستقل. لا عمود خامس.**
- Tablet: 2 أعمدة؛ Mobile: عمود واحد.
- **الحالة الحالية:** `PublicFooter.tsx` قريب من المرجع في التركيب (4 أعمدة + Copyright، بدون Services column) — المطلوب فقط: (1) حذف البريد/الهاتف المختلقين، (2) إزالة علامات المتابعة المختلقة وتسجيلها Asset Gap، (3) تحديث الألوان للـPalette الجديدة.

---

## 6. Asset Validity / Asset Remediation

### 6.1 نتيجة الفحص البصري الفعلي للأصول الحالية (ليس بأسماء الملفات)

| # | الأصل | الحالة | السبب |
|---|-------|--------|-------|
| 1 | `frontend/public/assets/hero-export.jpg` (1920×1080) | **INVALID — COMPOSITE SCREENSHOT** | يحتوي أجزاء واضحة من تصميم Concept 1 نفسه: Navbar + نص Hero + أزرار Hero + Our Company وغيرها. ليست صورة فوتوغرافية Atomic مستقلة. |
| 2 | `frontend/public/assets/about-egypt.jpg` (800×600) | **INVALID — COMPOSITE SCREENSHOT** | تحتوي نصوص وأجزاء متعددة من صفحات/sections وتصميم UI. ليست atomic image. |
| 3 | `frontend/public/assets/products/vegetables.jpg` (800×600) | **INVALID — COMPOSITE SCREENSHOT** | تحتوي أجزاء من عدة sections ونصوص وتصميم الصفحة. |
| 4 | `frontend/public/assets/products/fruits.jpg` (800×600) | **INVALID — COMPOSITE SCREENSHOT** | تحتوي أجزاء من عدة sections ونصوص وتصميم الصفحة. |
| 5 | `frontend/public/assets/products/factory.jpg` (800×600) | **INVALID — COMPOSITE SCREENSHOT** | تحتوي أجزاء من عدة sections ونصوص وتصميم الصفحة. |
| 6 | `frontend/public/assets/services/services-bg.jpg` (437×1199) | **INVALID — COMPOSITE SCREENSHOT — FORBIDDEN** | تحتوي بوضوح على مادة Concept 2 / `Export Journey Concept`. أبعادها 437×1199 قريبة جدًا من `concept1.png` (438×1199). **لا يجوز استخدامها إطلاقًا كـRuntime asset.** |

### 6.2 قواعد الأصول النهائية

- لا composite screenshot في Runtime.
- لا Runtime asset يحتوي: page text، Navbar، buttons، UI، page chrome، borders الخاصة بالتصميم، screenshot كامل، أو crop يحتوي Layout الصفحة.
- الصور المطلوبة في Home يجب أن تكون **atomic images مستقلة**.
- Concept 2 وConcept 3 ممنوعان تمامًا كـRuntime assets.
- `concept1.png` مرجع بصري فقط، لا يُستخدم Runtime.

### 6.3 Asset Gaps المطلوبة قبل Code (لا أصل نظيف موجود في المشروع لأي منها)

| # | الأصل المطلوب | القسم | ملاحظات |
|---|--------------|-------|---------|
| G1 | صورة خلفية Hero: Egyptian landscape (Nile / pyramids / palm scenery) | Hero | atomic photograph |
| G2 | طبقة خضروات مصرية (foreground layer) | Hero | atomic photograph، تُوضع أسفل/يمين |
| G3 | Egyptian visual (أهرامات/نيل/قارب شراعي) | Our Company | atomic photograph، aspect 4/3 |
| G4 | صورة خضروات | Products item 1 | atomic photograph |
| G5 | صورة فواكه | Products item 2 | atomic photograph |
| G6 | صورة منتجات المصانع | Products item 3 | atomic photograph |
| G7 | Laptop/interface composition | Digital Platform | **Visual-Fidelity Gate:** CSS/HTML كوسيلة تنفيذ فقط لإعادة بناء هندسة المرجع وعناصره الأساسية — لا Dashboard مختلق ولا بيانات وهمية؛ إذا تعذرت المطابقة الأمينة للمرجع → Visual Gap يمنع PASS |
| G8 | World map visual | Global Markets | **Visual-Fidelity Gate:** خريطة عالمية واضحة بنفس الوظيفة والهيمنة البصرية؛ CSS/SVG كوسيلة تنفيذ مطابقة فقط — لا random dots ولا اختراع شكل؛ إذا تعذرت المطابقة الأمينة للمرجع → Visual Gap يمنع PASS |
| G9 | صورة تجارة/شحن/سفينة | Trust/CTA right panel | atomic photograph |
| G10 | علامات SGS / ISO / HACCP / GLOBALG.A.P. الرسمية | Trust left panel | أصل رسمي موجود في المشروع أو يقدمه المستخدم/المصدر المعتمد فقط — لا نص بدل شعار، لا SVG مختلق، لا مصدر غير معتمد |
| G11 | منصات وأيقونات Follow Us | Footer | فقط منصات/روابط مثبتة فعليًا في المشروع أو مصدر المحتوى — لا افتراض منصات من glyphs، لا اختراع |
| G12 | **Contact submission endpoint** | `/contact` | **محسوم:** endpoint موجود ومعتمد — الـBackend: `backend/app/routers/contact.py:18` (`@router.post("/contact")` على `APIRouter()` بلا prefix، مُركَّب في `backend/main.py:659`) والـFrontend service: `frontend/src/services/api.ts:289-290` (`submitContact`). مسار الخدمة صُحِّح من `/api/v1/contact` إلى `/contact` ليتطابق مع المسار الفعلي المخدم. لا يُنشأ Backend جديد |

### 6.4 سياسة الاستخراج من المرجع (لاحقًا فقط — لا تُنفذ الآن)

يُسمح باقتراح استخراج المحتوى الفوتوغرافي نفسه من `concept1.png` عند الضرورة القصوى فقط إذا:
1. الناتج image-only.
2. بدون text.
3. بدون Navbar.
4. بدون UI.
5. بدون borders أو page elements.
6. يُحفظ كملف مستقل Runtime Asset.
7. يُسجل مصدره في الخطة.

**لا تنفذ الاستخراج في مرحلة الخطة.** هذه مرحلة Plan فقط.

### 6.5 قاعدة الـGating الموحدة

- **G1–G6, G9–G11 (أصول نظيفة):** Code لا يبدأ للأقسام المعتمدة عليها قبل توفير الأصول النظيفة أو تنفيذ سياسة الاستخراج المعتمدة (6.4).
- **G7–G8 (مسار تنفيذي افتراضي + Visual-Fidelity Gate):** لهما مسار تنفيذي افتراضي (إعادة بناء مطابقة للمرجع بـCSS/HTML/SVG)، لكنهما **ليسا "غير Blocker" بصورة مطلقة**: إذا تعذرت المطابقة البصرية الأمينة للمرجع، يتحولان إلى Visual Gap ويمنعان إعلان PASS للقسمين المعتمدين عليهما.
- **G12 (Contact endpoint):** endpoint موجود ومعتمد (`POST /contact` — `backend/app/routers/contact.py:18` مُركَّب في `main.py:659`، و`submitContact` في `frontend/src/services/api.ts:289-290` بعد تصحيح مساره من `/api/v1/contact` إلى `/contact`). النموذج يُربط به مباشرة؛ لا يُنشأ Backend جديد ضمن هذه الخطة.

---

## 7. Responsive Contract

| Breakpoint | العرض | السلوك |
|-----------|-------|--------|
| Desktop | ≥1280px | composition المرجعي كاملًا، container = min(92vw, 1280px)، النسب كما في القسم 1.1 |
| Laptop | 1024–1279px | نفس composition، تقليل الأحجام والـspacing فقط دون تغيير الهوية |
| Tablet | 768–1023px | إعادة ترتيب محدود عند الحاجة (Products: 2 ثم 1، Trust/CTA: stacked) دون اختراع تصميم جديد |
| Mobile | <768px (بما فيه 375px) | نفس ترتيب الصفحة، لا حذف أقسام، الصور تبقى prominent، لا thumbnails، image/text stacking يحافظ على hierarchy، لا قلب عشوائي، لا Layout جديد، **no horizontal overflow** |

**قواعد محددة:**
- The Export Journey: Desktop = 5 nodes أفقية بconnector وarrows؛ Mobile = stacked/vertical يحافظ على التسلسل والمعنى.
- Trust/CTA: Desktop = split 51/49؛ Mobile = stacked blocks بنفس الترتيب والدلالة.
- Hero: Mobile = نص أولًا، طبقة الخضروات تُreposition، CTA stacked، ارتفاع 420–520px (أي vh مقفول بسقف 520px — ممنوع min-height: 60vh غير المقفول).
- Digital Platform: Mobile = visual أولًا ثم نص.
- Global Markets: Mobile = world visual يبقى خلفية، stats stacked.
- **لا توجد قواعد Responsive لأقسام ملغاة** (Feature Band / Global Closing Banner — غير موجودتين).
- Typography scaling: heading يقل تدريجيًا (36→32→28px)؛ body يبقى 14–16px على كل breakpoints.

---

## 8. Translation Contract

- **لا تُنشأ namespace موازية للتصميم** مثل `public.concept1`. النطاق الحالي `public.concept1.*` في ملفات الترجمة يحتوي محتوى قديم متعارض مع المرجع (`heroTitle: "Bringing the Best of Egypt to the World"`, `ourCompany.title: "More Than a Trading Company"`, `featureBand.*`, `closingBanner.*`) → **يُحذف/يُستبدل** بالمفاتيح النهائية.
- **المفاتيح الموجودة التي تُعاد استخدامها:** `public.nav.*`، `public.home.heroDescription`، `public.home.platformP1`، `public.products.vegetablesTitle/vegetablesDesc/fruitsTitle/fruitsDesc/factoryTitle/factoryDesc`، `public.markets.step1Title…step5Title`، `public.markets.statCountries/statPartners/statQuality`، `public.home.trustedTitle/trustedDescription/trustedCta`، `public.cta.learnMore/getStarted/contactUs/signIn/createAccount`، `public.footer.copyright`، `public.about.companyNameEn/companyNameAr`.
- **المفاتيح الجديدة المطلوبة (فقط هذه — لا اختراع غيرها):**
  - `public.home.heroEyebrow`، `public.home.heroTitle`، `public.home.heroCorporateAr`، `public.home.heroCorporateEn`
  - `public.home.ourCompanyEyebrow`، `public.home.ourCompanyTitle`، `public.home.ourCompanyText`
  - `public.home.productsEyebrow`، `public.home.productsTitle`، `public.home.viewAllProducts`
  - `public.home.journeyTitle`، `public.home.journeyDescription`
  - `public.home.platformEyebrow`، `public.home.platformTitleLine1`، `public.home.platformTitleLine2`، `public.home.platformShortDesc`
  - `public.home.marketsEyebrow`، `public.home.marketsTitle`، `public.home.marketsSubtitle`
  - `public.home.trustedByTitle`
- **Digital Platform text:** `public.home.*` فقط. `landing.features.*` موجودة في ملفات الترجمة لكنها تخص الـinternal landing القديم — **لا تُستخدم في الموقع العام**.
- EN/AR مدعومتان، `dir="ltr"` / `dir="rtl"` على الصفحات العامة، RTL/LTR يعملان.
- **لا يُغيّر** محتوى `PublicAbout` / `PublicProducts` / `PublicServices` / `PublicMarkets` / `PublicContact` بلا سبب مباشر لهذا التصميم.
- اللغة الافتراضية عند أول زيارة بدون تفضيل محفوظ: **الإنجليزية** (`i18n.ts`: `fallbackLng: 'en'`، `detection.order: ['localStorage']` فقط، لا `navigator.language`).

---

## 9. App Routing Contract (Technical Constraint)

- `/` → `PublicLanding` **دائمًا**، public route خارج `PrivateRoute` تمامًا. **لا يجوز أبدًا أن يتحول `/` إلى authenticated Layout أو private shell.**
- جميع المسارات الداخلية الحالية (`/dashboard`, `/suppliers`, `/customers`, `/shipments`, `/invoices`, `/customs`, `/documents`, `/resources`, `/profile`, `/notifications`, `/avatar`, `/digital-export-manager` وفروعه, `/knowledge-graph`, `/trade-intelligence`, `/export-readiness`, `/architecture-explorer`, `/potential-customers`) تحتفظ بالبنية الحالية: **Layout + Sidebar + Header + Outlet + PrivateRoute** وprivate shell behavior كما هي.
- ممنوع: إعادة هيكلة Private app، حذف Layout، إعادة توزيع المسارات الداخلية بما يغير shell، ربط PublicLanding بالـPrivate shell.
- المسارات العامة الأخرى (`/about`, `/products`, `/services`, `/markets`, `/contact`) تبقى public routes مستقلة خارج `PrivateRoute`.
- `/login` → `Login` (موجود، public). `/*` → Redirect to `/`.

---

## 10. Other Public Pages (مُنظّفة — لا تعارض مع المرجع)

المرجع البصري يخص PublicHome فقط. الصفحات التالية تُنفذ بالمحتوى الموجود وبنفس قواعد الأصول والترجمة:

| المسار | المكون | المحتوى | ملاحظات الأصول |
|--------|--------|---------|----------------|
| `/about` | `PublicAbout.tsx` (جديد) | `public.about.*` (موجود) | أي صورة مصرية تخضع لنفس قواعد Asset Validity (G3 قابلة لإعادة الاستخدام هنا عند الحاجة) |
| `/products` | `PublicProducts.tsx` (جديد) | `public.products.*` (موجود) | G4/G5/G6 + CTA `Request Catalog` → `/contact` |
| `/services` | `PublicServices.tsx` (جديد) | `public.services.*` (موجود) | **`services-bg.jpg` ممنوع تمامًا** (composite من Concept 2) — خلفية القسم إما `#043B3E` صلبة أو أصل نظيف جديد (Asset Gap) |
| `/markets` | `PublicMarkets.tsx` (جديد) | `public.markets.*` (موجود، 6 مراحل بما فيها Global Markets) | صفحة مستقلة — لا تُخلط مع Home (5 خطوات) |
| `/contact` | `PublicContact.tsx` (جديد) | `public.contact.*` (موجود) | نموذج اتصال كامل: الاسم، البريد، الموضوع، الرسالة + client-side validation + حالات idle/submitting/success/error. **G12 محسوم:** endpoint موجود ومعتمد (`POST /contact` — `backend/app/routers/contact.py:18`، مُركَّب في `main.py:659`) و`submitContact` في `api.ts:289-290` (مساره صُحِّح إلى `/contact`) — النموذج يُربط به؛ **ممنوع إنشاء Backend جديد** |

**مكونات مشتركة موجودة فعلًا** (`frontend/src/components/public/`): `PublicNavbar.tsx`، `PublicFooter.tsx`، `ProductCard.tsx`، `ServiceCard.tsx`، `MarketStepCard.tsx` — تُستخدم وتُصحح حسب هذه الخطة، لا تُعاد تسميتها. لا يُنشأ `HeroSection`/`CTASection`/`ImageWithOverlay`/`SectionTitle` كـabstractions عامة.

---

## 11. Current Implementation State vs. Required (لمرحلة Code)

`PublicLanding.tsx` الحالي (225 سطرًا) يحتوي على:
1. Hero بـ`hero-export.jpg` full-bleed + 2 CTA — **يُعاد بناؤه** حسب 5.2 (العنوان `Nile Key`، السطران المؤسسيان، pill CTAs، طبقة الخضروات، scrim اتجاهي).
2. **Feature Band (4 عناصر) — يُحذف** (غير موجود في المرجع).
3. Our Company بسطح **فاتح** `#f8fafc` وعنوان `More Than a Trading Company` — **يُصحح**: سطح داكن `#043B3E`، عنوان `Our Company`، نص مختصر.
4. Products بسطح **أبيض** و`View All Products` كـCTA منفصل أسفل القسم — **يُصحح**: سطح داكن، `View All Products` في الجهة المقابلة من الـheader، عناصر بscrim داكن.
5. **Global Closing Banner (SVG globe) — يُحذف** ويُستبدل بـ: The Export Journey + Digital Platform + Our Presence in Global Markets + Trusted by Global Partners / Let's Grow Together (أقسام غير موجودة حاليًا ويجب إنشاؤها).

`PublicNavbar.tsx`: قريب — يُضاف Home active accent mark + تحديث Palette.
`PublicFooter.tsx`: قريب — يُحذف البريد/الهاتف المختلقان، تُزال علامات المتابعة المختلقة (Asset Gap G11)، تحديث Palette.

---

## 12. Acceptance Contract (جديد بالكامل — يلغي القديم)

PASS لا يعني TypeScript passed أو Build passed أو ظهور أسماء الأقسام فقط. PASS النهائي يتطلب **الجميع**:

1. ترتيب الصفحة يطابق المرجع الفعلي (9 عناصر بالترتيب المحدد).
2. عدد الأقسام يطابق المرجع (لا Feature Band، لا Global Closing Banner).
3. geometry متوافقة (نسب الأعمدة: Hero نص ≈46–50%، Our Company 48–50/42–44، Digital Platform visual-left/text-right، Trust 51/49).
4. section heights متوافقة نسبيًا (الترتيب: Hero > Products > Our Company > Journey > Digital > Markets > Footer > Trust).
5. text/image ratios متوافقة بصريًا.
6. image prominence متوافقة (Hero ليس thumbnail، صور المنتجات top-heavy).
7. spacing متوافق (المحتوى = `min(92vw, 1280px)` centered بدون padding أفقي داخلي إضافي، لا gaps خارجية بين الأقسام).
8. surfaces متوافقة (داكنة باستثناء لوحة Trust اليسرى `#F4F6F2`).
9. palette متوافقة (`#043B3E` / `#022F32` / `#19D8B0` / `#F4F6F2`).
10. typography hierarchy متوافقة.
11. CTA shapes/placement متوافقة (pill-shaped، مواضعها كما في المرجع).
12. لا توجد عناصر من Concept 2/3.
13. لا توجد composite screenshot assets في Runtime.
14. لا توجد fake logos أو fake statistics أو بيانات مختلقة.
15. Private app shell لم يتضرر (Layout/Sidebar/Header/Outlet/PrivateRoute كما هي).
16. EN/AR وRTL/LTR تعملان.
17. G7/G8: الـvisuals مطابقة للمرجع بأمانة (لا Dashboard مختلق، لا بيانات وهمية، لا random dots، لا اختراع شكل) — وإلا Visual Gap مسجل ولا PASS للقسمين.
18. G12: نموذج الاتصال غير مربوط بـendpoint غير موجود، ولا Backend جديد مُنشأ.
19. Hero height ضمن النطاق المطلق لـbreakpoint (لا تضخيم vh) وContainer = `min(92vw, 1280px)`.

---

## 13. Visual QA Protocol (اختبار فعلي — بعد Code)

1. شغّل التطبيق فعليًا.
2. التقط Screenshots فعلية للـHome على الأقل عند:
   - Desktop ≈1440px
   - Desktop ≈1280px
   - Tablet ≈768px
   - Mobile ≈375px
3. قارن كل Screenshot مع `frontend/public/design-reference/concept1.png` **Section-by-Section**.
4. الفحص يشمل: geometry، section heights، text/image ratio، image scale، image placement، spacing، typography hierarchy، CTA location، CTA shape، surfaces، palette، section transitions، responsive transformation.
5. **`Build passed` ≠ `Visual QA passed`.** لا يُكتب "مطابق بصريًا" إلا بعد مشاهدة الناتج الفعلي ومقارنته بالمرجع.
6. أي mismatch بصري جوهري → Code لا يعتبر PASS.

---

## 14. Prohibited Items (موحّدة)

- Feature Band كقسم مستقل.
- Global Closing Banner كقسم مستقل.
- حذف The Export Journey / Digital Platform / Global Markets.
- Light Our Company / White Products section / Global Markets light surface.
- Trusted Partners dark 50/50 text-only.
- Hero 45/55 كثابت / Hero background solid only / Hero rounded card / Hero ككتلة بيضاء.
- alternating light/dark pattern لمجرد التنظيم.
- gradients كحل عام / glass cards غير موجودة.
- أي composite screenshot كـRuntime asset (بما فيها `hero-export.jpg`, `about-egypt.jpg`, `products/*.jpg`, `services-bg.jpg`).
- أي Asset من Concept 2 أو Concept 3 كـRuntime asset.
- `concept1.png` كـRuntime asset.
- fake logos (SGS/ISO/HACCP/GLOBALG.A.P. كنص أو SVG مختلق) أو fake social glyphs.
- fake statistics (فقط 50+ / 200+ / 100% معتمدة) أو fake operational data أو أرقام وهمية.
- بيانات اتصال مختلقة (بريد/هاتف غير موجودة في المشروع).
- `landing.features.*` في الموقع العام.
- Services column في Footer أو عمود خامس.
- Responsive rules لأقسام ملغاة.
- تحويل `/` إلى authenticated Layout / private shell.
- إعادة هيكلة Private app أو حذف Layout.
- اختراع محتوى أو translation keys غير ضرورية أو namespace `public.concept1` كتصميم.
- Acceptance يجعل Build وحده كافيًا.

---

## 15. Implementation Phases (مرتبة)

1. **Assets Remediation (Gating):** توفير G1–G6, G9–G11 (أصول نظيفة atomic) أو تنفيذ سياسة الاستخراج المعتمدة (6.4). G7/G8: مسار تنفيذي افتراضي بإعادة بناء مطابقة للمرجع بـCSS/HTML/SVG — خاضع لـVisual-Fidelity Gate (تعذر المطابقة الأمينة = Visual Gap يمنع PASS). G12: التحقق من contact endpoint معتمد قبل ربط النموذج (لا Backend جديد).
2. **i18n + Translation:** تعديل `i18n.ts` (default English، localStorage-only)، حذف `public.concept1.*`، إضافة المفاتيح الجديدة (القسم 8) في EN وAR.
3. **Shared Components:** تصحيح `PublicNavbar.tsx` (Home active mark + Palette) و`PublicFooter.tsx` (حذف بيانات مختلقة + G11 + Palette).
4. **PublicHome:** إعادة بناء `PublicLanding.tsx` بالكامل حسب الأقسام 5.1–5.9 (حذف Feature Band وGlobal Closing Banner، إنشاء الأقسام الخمسة المفقودة).
5. **Other Public Pages:** `PublicAbout` / `PublicProducts` / `PublicServices` / `PublicMarkets` / `PublicContact` حسب القسم 10.
6. **Routing:** التأكد من عقد الـRouting (القسم 9) في `App.tsx`.
7. **Visual QA:** حسب القسم 13 على 4 viewports.

---

## FINAL EXECUTION CONTRACT

> هذا القسم هو **المرجع النهائي الوحيد** لمرحلة Code القادمة. كل أجزاء الخطة السابقة متوافقة معه؛ لا يوجد قسم قديم يقول عكسه.

**Source of Truth:** `frontend/public/design-reference/concept1.png` (438×1199، منطقة Runtime حتى y≈1148، يُتجاهل النص الخارجي أسفل الصورة). المحتوى من ملفات الترجمة الحالية. الكود الحالي Technical Constraint.

**Final Section Order (9 عناصر):** Navbar → Hero → Our Company → Premium Egyptian Products → The Export Journey → Digital Platform → Our Presence in Global Markets → Trusted by Global Partners / Let's Grow Together → Footer.

**Visual Composition (ملخص تنفيذي):**
- Container: المحتوى = `min(92vw, 1280px)` centered (≈92% من الـviewport مقفولًا بحد أقصى 1280px، بدون padding أفقي داخلي إضافي)، أقسام متلاصقة بدون gaps خارجية، خلفيات full-bleed.
- Palette: `#043B3E` (main dark teal)، `#022F32` (deeper teal/Footer)، `#19D8B0` (emerald accent)، `#F4F6F2` (Trust left panel فقط)، أبيض/teal-gray للنصوص.
- Navbar: شريط داكن، logo+brand يسار، 6 روابط وسط، language+Login+Create Account يمين، Home active بعلامة accent.
- Hero: خلفية فوتوغرافية ممتدة + scrim داكن اتجاهي جهة النص + طبقة خضروات مصرية أسفل/يمين + نص يسار ≈46–50% (eyebrow `EGYPTIAN PRODUCTS • GLOBAL MARKETS`، عنوان `Nile Key`، سطران مؤسسيان عربي/إنجليزي، وصف قصير، 2 pill CTAs: Get Started filled emerald + Learn More outline).
- Our Company: داكن، نص يسار 48–50%، صورة مصرية يمين 42–44% (aspect 4/3، rounded-2xl، offset teal backing)، عنوان `Our Company`، نص مختصر، Learn More.
- Products: داكن، header (eyebrow `KEY PRODUCTS` + عنوان + `View All Products` في الجهة المقابلة)، 3 عناصر متساوية (صورة top-heavy aspect ≈4/5 + عنوان + وصف قصير + scrim داكن خلف النص السفلي)، لا CTA منفصل.
- Export Journey: داكن، عنوان + وصف قصير، 5 nodes دائرية أفقية بconnector وarrows وعناوين أسفلها (Farm/Factory → Packing & Quality → Export Documents → Shipping → Port & Delivery)، mobile vertical.
- Digital Platform: داكن، visual يسار (laptop/interface composition بـCSS/HTML، بدون بيانات) + نص يمين (eyebrow `DIGITAL PLATFORM`، عنوان بسطرين، وصف قصير، Learn More).
- Global Markets: داكن مع world map visual في الخلفية، عنوان `Our Presence in Global Markets`، إحصائيات سفلية 3 أعمدة بفواصل رأسية (50+ Countries / 200+ Business Partners / 100% Commitment to Quality).
- Trust/CTA: split 51/49 متجاور — يسار `#F4F6F2` (`Trusted by Global Partners` + علامات SGS/ISO/HACCP/GLOBALG.A.P. الرسمية) ويمين لوحة داكنة بصورة شحن/سفينة (`Let's Grow Together` + subtitle + CTA Contact Us).
- Footer: داكن `#022F32`، 4 أعمدة (Logo+Brand+Digital Export Platform / Quick Links / Contact Us / Follow Us) + Copyright، لا Services column.

**Assets Policy:** لا composite screenshots في Runtime (الأصول الستة الحالية كلها INVALID). الأصول النظيفة المطلوبة: G1–G12 (القسم 6.3). الاستخراج من المرجع مسموح لاحقًا بشروط image-only فقط. Concept 2/3 ممنوعان.

**Execution Gates (إلزامية — تمنع PASS حتى تُحسم):**
- **Hero geometry final rule:** ارتفاع Hero نطاق px مطلق حسب breakpoint (Desktop 560–720px، Laptop 480–600px، Tablet 420–520px، Mobile 420–520px) — **لا vh غير مقفول**، ولا تضخيم على الشاشات الطويلة، والنسبة ≈18% تُفحص في Visual QA عند 1440/1280.
- **Container final rule:** المحتوى = `min(92vw, 1280px)` centered، بدون padding أفقي داخلي إضافي؛ الخلفيات full-bleed.
- **G7/G8 Visual-Fidelity Constraint:** CSS/HTML/SVG وسيلة تنفيذ مطابقة للمرجع فقط (هندسة المرجع وعناصره الأساسية في Digital Platform، وخريطة عالمية واضحة بنفس الهيمنة في Global Markets) — لا Dashboard مختلق، لا بيانات وهمية، لا random dots، لا اختراع شكل جديد؛ تعذر المطابقة الأمينة = Visual Gap مسجل يمنع PASS للقسمين.
- **Contact endpoint gate (G12) — RESOLVED:** endpoint موجود ومعتمد: `POST /contact` (`backend/app/routers/contact.py:18`، مُركَّب في `backend/main.py:659`) مع `submitContact` في `frontend/src/services/api.ts:289-290` (مسار الخدمة صُحِّح من `/api/v1/contact` إلى `/contact` ليتطابق مع المسار المخدم). النموذج يُربط به؛ ممنوع إنشاء Backend جديد.
- **G10 official trust-mark rule:** SGS/ISO/HACCP/GLOBALG.A.P. تُستخدم فقط بأصول رسمية موجودة في المشروع أو يقدمها المستخدم/المصدر المعتمد — لا نص بدل شعار، لا SVG مختلق، لا مصدر غير معتمد؛ عدم التوفر = Gap والقسم غير مكتمل بصريًا.
- **G11 verified social-platform rule:** منصات Follow Us فقط إذا كانت مثبتة فعليًا في المشروع أو مصدر المحتوى — لا افتراض من glyphs (`in`/`f`/`◎` مُحذفة)، لا اختراع منصات؛ عدم التوفر = Gap.
- **Gaps التي تمنع الأقسام المعتمدة عليها من إعلان PASS:** G1–G6 (Hero background/foreground، Our Company image، 3 product images)، G9 (صورة الشحن/السفينة)، G10 (علامات الثقة)، G11 (منصات المتابعة) — أقسامها لا تُعلن PASS قبل توفير الأصول. G7/G8 تمنعان PASS فقط إذا تعذرت المطابقة الأمينة. G12 يمنع ربط النموذج (لا يمنع بناء واجهته).

**Typography:** eyebrow 12–14px/400 uppercase accent، section title 28–36px/700 أبيض، body 14–16px/400 (leading 1.6 EN / 1.8 AR)، Hero title 44–64px/800، CTA 14–16px/500–600 pill.

**Responsive:** Desktop يحافظ على composition؛ Laptop يقلل أحجامًا فقط؛ Tablet إعادة ترتيب محدودة؛ Mobile نفس الترتيب بدون حذف أو قلب عشوائي أو overflow. Journey: أفقي→عمودي. Trust/CTA: split→stacked.

**Translation:** `public.*` فقط؛ حذف `public.concept1.*`؛ المفاتيح الجديدة المحددة في القسم 8 فقط؛ `landing.features.*` غير مستخدمة؛ EN/AR + LTR/RTL؛ default English.

**Routing:** `/` → `PublicLanding` دائمًا public؛ المسارات الداخلية تحتفظ بـ Layout/Sidebar/Header/Outlet/PrivateRoute دون تغيير.

**Acceptance:** النقاط الـ19 في القسم 12 — Build وحده لا يكفي.

**Visual QA:** Screenshots فعلية عند 1440/1280/768/375 مقارنة بـconcept1.png section-by-section؛ mismatch جوهري = FAIL.

**Prohibited:** القائمة الموحدة في القسم 14.

**Open Gaps قبل Code:** G1–G6, G9–G11 (أصول نظيفة) — لا يمكن إكمال الأقسام المعتمدة عليها بأمانة قبل توفيرها. G7/G8 — مسار تنفيذي افتراضي خاضع لـVisual-Fidelity Gate (تعذر المطابقة الأمينة = Visual Gap يمنع PASS). G12 — **محسوم:** endpoint الاتصالات موجود ومعتمد (`POST /contact` في `backend/app/routers/contact.py:18` + `submitContact` في `api.ts:289-290` بعد تصحيح المسار) والنموذج يُربط به.
