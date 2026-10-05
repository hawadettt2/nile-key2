## VISUAL SOURCE OF TRUTH OVERRIDE — APPROVED CONCEPT 1

**الأولوية القصوى للتصميم البصري:** هذا القسم يصحح أي تعارض بصري في بقية هذه الخطة، ويعلو عليها جميعًا في كل ما يخص PublicHome.

**المصدر البصري الوحيد:** frontend/public/design-reference/concept1.png = **Concept 1 الفعلي** (اللوحة اليسرى فقط من ملف المفاهيم).
الصور المرجعية الأخرى، وConcept 2، وConcept 3، وأي Blueprint سابق ناتج عن دمجها **ليست مصادر تصميم بديلة**.

**التكوين الفعلي لـ PublicHome حسب Concept 1:**
1. Navbar فوق الـHero.
2. Hero واحد كبير **Full-bleed photographic background** داخل القسم، وليس عمود Text/Image 45/55. الصورة هي الخلفية الرئيسية للـHero وتغطي المشهد.
3. داخل الـHero: eyebrow، عنوان "Bringing the Best of Egypt to the World"، وصف قصير، وزران فقط: **Get Started** و **Learn More**.
4. أسفل الـHero مباشرة Feature Band داكن واحد يحتوي 4 عناصر متساوية:
   - Premium Egyptian Products
   - Global Markets
   - Trusted Partnerships
   - Digital Solutions
5. Our Company: قسم فاتح، نص يسار + صورة مصرية يمين.
6. Premium Egyptian Products: قسم فاتح، 3 صور/عناصر متساوية: Vegetables، Fruits، Factory Products، مع رابط **View All Products**.
7. Closing Global CTA/Banner: قسم داكن بصري بصورة/مشهد عالمي للتصدير، بعنوان **From Egyptian Fields and Factories to Global Markets** ووصف **Quality. Trust. Sustainable Growth.**
8. Footer داكن.

**بالتالي PublicHome لا يحتوي على هذه الأقسام المنفصلة:** The Export Journey، Digital Platform، Global Markets بإحصائيات، Trusted Partners / CTA split. هذه العناصر من Concept 2/3 أو من Blueprint سابق وليست أجزاء من Concept 1.

**قيود تنفيذ حاسمة:**
- لا تعاد صياغة Concept 1 إلى 45/55 columns أو 9-section homepage.
- لا تستخدم Concept 2 أو Concept 3 كمرجع بصري.
- concept1.png مرجع فقط ولا يُستخدم Runtime.
- الأصول التشغيلية فقط من جدول الأصول المسموحة في هذه الخطة.
- أي نص غير ظاهر/غير مستمد من المحتوى الحالي لا يُخترع.
- إذا تعارض أي نص لاحق في هذه الخطة مع هذا القسم، **هذا القسم هو الحاكم**.

---

# خطة تنفيذ الواجهة العامة لموقع Nile Key

## 1. الصفحات والمسارات العامة المطلوبة

### الصفحات الجديدة (Public Website Pages)

| المسار | المكون | الوصف |
|--------|---------|-------|
| `/` | `PublicHome` (概念名：概念上稱 PublicHome，實際實作檔案維持 `PublicLanding.tsx`) | الصفحة الرئيسية - تعرض هوية الشركة والـ Hero و CTA |
| `/about` | `PublicAbout` (جديد) | من نحن - التفاصيل المؤسسية والرسالة |
| `/products` | `PublicProducts` (جديد) | صفحة المنتجات المستقلة |
| `/services` | `PublicServices` (جديد) | الخدمات والمنظومة الرقمية |
| `/markets` | `PublicMarkets` (جديد) | رحلة التصدير والوصول للأسواق العالمية |
| `/contact` | `PublicContact` (جديد) | صفحة الاتصال المؤسسية مع نموذج اتصال كامل |
| `/login` | `Login` | موجودة بالفعل - لا تغيير |

### هيكل المسارات في `App.tsx`

يجب أن تكون `/`, `/about`, `/products`, `/services`, `/markets`, `/contact` **Public routes مستقلة وخارج `PrivateRoute`** تمامًا. يحافظ `RoleRedirect` وجميع المسارات الداخلية والمصادقة كما هي دون إعادة تصميمها.

```
/login                                         → Login (موجود، public)
/about                                         → PublicAbout (جديد، public)
/products                                      → PublicProducts (جديد، public)
/services                                      → PublicServices (جديد، public)
/markets                                       → PublicMarkets (جديد، public)
/contact                                       → PublicContact (جديد، public)

/                                              → PublicHome (概念名稱，實際檔案：PublicLanding.tsx，不創建新檔)
/*                                            → Redirect to / (موجود)
```

### ملاحظة على `PublicLanding` الحالي
- `PublicHome` 為概念名稱，實際實作檔案維持 `PublicLanding.tsx`，直接修改該檔案完成，不創建新檔。
- لا يُنشَأ `PublicHome.tsx` جديد.
- لا تُعاد تسمية `PublicLanding.tsx`.
- جميع المسارات الداخلية (`/dashboard`, `/suppliers`, إلخ) تبقى داخل `PrivateRoute` كما هي.
- لا توجد مسارات عامة جديدة داخل `/` مع `PrivateRoute`.

---

## 2. مكونات الواجهة المشتركة (Shared Components)

### المكونات المطلوب إنشاؤها (الحد الأدنى الضروري)

```
frontend/src/components/public/
  PublicNavbar.tsx       # الشريط العلوي الفاخر - يُستخدم في جميع الصفحات العامة
  PublicFooter.tsx       # Footer احترافي موحد - يُستخدم في جميع الصفحات العامة
  ProductCard.tsx        # بطاقة منتج - تُستخدم في PublicProducts فقط
  ServiceCard.tsx        # بطاقة خدمة - تُستخدم في PublicServices فقط
  MarketStepCard.tsx     # بطاقة خطوة في رحلة التصدير - تُستخدم في PublicMarkets فقط
```

### ملاحظة على تقليل المكونات المشتركة
- لا يُنشَأ `HeroSection`, `CTASection`, `ImageWithOverlay`, `SectionTitle` كـ abstractions عامة إلا إذا كان استخدامها الفعلي مبررًا داخل أكثر من صفحة. الأولوية لتنفيذ التصميم مباشرةً داخل كل صفحة.
- الأولوية: تنفيذ التصميم المرجعي كما هو، وليس توسيع المعمارية.

---

## 3. توزيع محتوى التصميم المرجعي على الصفحات

### 3.1 PublicHome (الصفحة الرئيسية)

**المصدر:** القسم الرئيسي من التصميم المرجعي

**الترتيب النهائي للأقسام (من الأعلى إلى الأسفل):**
1. Navbar
2. Hero
3. Our Company
4. Premium Egyptian Products
5. The Export Journey
6. Digital Platform
7. Global Markets
8. Trusted Partners / CTA
9. Footer

**الأقسام والتفاصيل البصرية:**
1. **شريط علوي (Navbar)** - شعار `NK`، اسم `Nile Key`، `Digital Export Platform`، أزرار اللغة، Login، Create Account. الشريط أفقي فاخر ومتسق مع التصميم المرجعي.
2. **Hero Section** - هوية الشركة (الاسم بالعربية والإنجليزية)، الرسالة الرئيسية، صورة Hero قوية مرتبطة بمصر والمنتج الزراعي والتصدير والأسواق العالمية، زرّان CTA (Sign In / Create Account). الخلفية: `#002f32` dark.
3. **Our Company** - 3 فقرات عن هوية الشركة وهدف التأسيس. النص مستمد من `PublicLanding.tsx` الحالي (الفقرات عن الشركة المصرية وهدف التأسيس).

### 3.2 PublicAbout

**المصدر:** قسم "من نحن" من التصميم المرجعي

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "About Us" / "من نحن"
2. **من نحن** - الشركة المصرية، طبيعة النشاط، هدف التأسيس. النص مستمد من `PublicLanding.tsx` الحالي (فقرات هوية الشركة).
3. **الرؤية والرسالة** - صورة/مشهد مصري مناسب + نص الرسالة المؤسسية. الصورة: أصل بصري محدد المصدر (انظر القسم 4).
4. **الموقع كشريك تجاري دولي** - صياغة تجارية راقية بدون أرقام وهمية. النص مستمد من `PublicLanding.tsx` الحالي (قسم الشريك الاستراتيجي).
5. **لمحة سريعة** - أقسام صغيرة تعرض: اسم الشركة بالعربية والإنجليزية، الرخصة (الهيئة العامة للاستثمار والمناطق الحرة)، هدف التأسيس.

**الملاحظة:** استخدم فقط المحتوى الموجود فعليًا في `PublicLanding.tsx` الحالي. لا تخترع معلومات جديدة.

### 3.3 PublicProducts

**المصدر:** قسم المنتجات في التصميم المرجعي

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "Products" / "المنتجات"
2. **بطاقات المنتجات** - ثلاثة تصنيفات بصرية واضحة:
   - **Vegetables** - الخضروات
   - **Fruits** - الفواكه
   - **National Factory Products** - منتجات المصانع الوطنية
3. **عرض تجاري بصري** - كل بطاقة تحتوي على: صورة منتج (أصل بصري محدد المصدر)، عنوان، وصف قصير عام. البطاقات بتصميم `bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10`.
 4. **CTA** - زر "Request Catalog" فقط. يقود إلى `/contact`.

**الملاحظة:** لا تخترع أسماء منتجات أو شهادات أو مواصفات تجارية. استخدم الأسماء العامة فقط. الصور: أصول محددة المصدر (انظر القسم 4).

### 3.4 PublicServices

**المصدر:** قسم الخدمات في التصميم المرجعي

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "Services" / "الخدمات"
 2. **شبكة الخدمات** - عرض بصري لسبع خدمات:
    - إدارة عمليات التصدير → `Workflow`
    - الخدمات التجارية → `Handshake`
    - المنصة الرقمية → `LayoutDashboard`
    - إدارة الشحنات → `Truck`
    - الفواتير والمستندات → `FileText`
    - الإجراءات الجمركية → `ClipboardCheck`
    - الربط بين الموردين والعملاء والجهات اللوجستية → `Network`
    كل خدمة: أيقونة (`lucide-react`) + عنوان + وصف قصير. البطاقات بتصميم موحد.
3. **Why Choose Nile Key** - قسم بصري يعرض لماذا نختار Nile Key كشريك. أسلوب بصري: قائمة punti forza.
4. **CTA** - زر "Contact Us" فقط. يقود إلى `/contact`.

### 3.5 PublicMarkets

**المصدر:** فكرة "From Egyptian Fields and Factories to Global Markets" من التصميم المرجعي

**القاعدة:** PublicHome = 5-step journey فقط. PublicMarkets = standalone page تحتوي على 6 مراحل، وتنتهي بـ Global Markets.

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "Markets" / "الأسواق العالمية"
2. **رحلة التصدير بصريًا** - مسار خطوات متتالية بتصميم بصري واضح:
   - Farm / Factory (المزرعة/المصنع)
   - Packing & Quality (التغليف والجودة)
   - Export Documents (مستندات التصدير)
   - Shipping (الشحن)
   - Port & Delivery (الميناء والتسليم)
   - Global Markets (الأسواق العالمية) — هذه الخطوة تخص PublicMarkets فقط، لا تنتقل إلى PublicHome
   كل خطوة: أيقونة + عنوان + وصف قصير. التصميم: مسار خطي يربط الخطوات.
3. **CTA** - زر "Contact Us" فقط. يقود إلى `/contact`.

### 3.6 PublicContact

**المصدر:** التصميم المرجعي

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "Contact" / "اتصل بنا"
2. **وسائل الاتصال** - الموقع، البريد/الهاتف (البيانات الموجودة فعلياً في المشروع فقط). لا تخترع عناوين أو أرقام هواتف.
3. **نموذج اتصال كامل** - واجهة نموذج اتصال مع:
   - حقول: الاسم، البريد الإلكتروني، الموضوع، الرسالة
   - التحقق من المدخلات (client-side validation)
   - حالات الإرسال: idle, submitting, success, error
    - الربط بالـbackend: يُرسل إلى endpoint الاتصالات الحالي في المشروع فقط.
    - إذا لم يوجد endpoint مناسب، يُعتبر ذلك Blocker قبل التنفيذ ولا يُنشَأ Backend جديد ضمن هذه الخطة.
    - بعد التعديل يجب أن يبقى Backend وDEM والأنظمة الداخلية دون تعديل.
4. **CTA تجاري واضح** - "Send Message"
5. **Footer احترافي** - متسق مع باقي الصفحات.

---

## 4. استراتيجية الصور والأصول البصرية

### 4.1 مصادر الصور (إلزامية من البداية - لا MVP بدون صور)

**القاعدة:** الصور جزء أساسي من تنفيذ التصميم المرجعي من البداية. لا تأجيل.

### 4.2 مصادر الأصول المحددة

| الأصل | المسار في المشروع | المصدر | الاستخدام |
|-------|------------------|--------|-----------|
| Hero Image (PublicHome) | `frontend/public/assets/hero-export.jpg` | أصل بصري من مكتبة الشركة - صورة مرتبطة بمصر والمنتج الزراعي والتصدير والأسواق العالمية | Hero Section في PublicHome |
| About Image (PublicHome) | `frontend/public/assets/about-egypt.jpg` | أصل بصري من مكتبة الشركة - صورة/مشهد مصري مناسب | PublicHome / Our Company |
| Product Images (3) | `frontend/public/assets/products/vegetables.jpg`, `frontend/public/assets/products/fruits.jpg`, `frontend/public/assets/products/factory.jpg` | أصول بصرية من مكتبة الشركة - صور منتجات | بطاقات المنتجات في PublicProducts |
| Services Background | `frontend/public/assets/services/services-bg.jpg` | أصل بصري من مكتبة الشركة - خلفية قسم الخدمات | PublicServices / Why Choose Nile Key |

**ملاحظة:** إذا لم تكن الأصول متوفرة بعد في `frontend/public/assets/`، يجب أن يوفرها صاحب المشروع. لا يُسمح بـ placeholders نهائية أو اختراع صور.

**ملاحظة على `about-egypt.jpg`:** الأصل مخصص أساسًا لـ PublicHome / Our Company. يجوز إعادة استخدام نفس الأصل في PublicAbout ضمن Mission/Vision عند الحاجة، دون اعتبار ذلك أصلًا جديدًا ودون إنشاء صورة بديلة.

### 4.3 الأيقونات
- استخدم `lucide-react` (موجود في المشروع بالفعل)
- Approved icon mapping:
  - `Factory` - للمصنع / Farm
  - `CheckCircle` - للجودة / Packing
  - `FileText` - لمستندات التصدير
  - `Truck` - للشحن
  - `Ship` - للميناء والتسليم
  - `Globe` - للأسواق العالمية
  - `Package` - للمنتجات

### 4.4 مسارات الأصول
- جميع الصور توضع في: `frontend/public/assets/` ومجلداته الفرعية
- يُستخدم `<img src="/assets/..." />` في المكونات فقط

---

## 5. دعم الإنجليزية أولًا والعربية ثانيًا

### 5.1 بنية الترجمة الحالية
- **الملفات:** `en/translation.json` و `ar/translation.json`
- **المكتبة:** i18next + react-i18next
 - **الكشف التلقائي:** localStorage فقط
- **الاتجاه:** `dir="rtl"` للعربية، `dir="ltr"` للإنجليزية

### 5.2 تعديل سلوك اللغة الافتراضية

**المشكلة الحالية:** `i18next-browser-languagedetector` قد يفرض لغة من `navigator` عند أول زيارة، مما قد يجعل الموقع يبدأ بلغة غير الإنجليزية.

**الحل:** تعديل `frontend/src/lib/i18n.ts` لضمان:
1. **اللغة الافتراضية عند عدم وجود تفضيل محفوظ:** الإنجليزية (`en`)
2. **إذا كان هناك لغة محفوظة في `localStorage`:** استخدمها
3. **لا تعتمد على `navigator.language`** لفرض لغة البداية على الموقع العام
4. **لا يوجد خيار ثانوي مثل navigator**

**التنفيذ المقترح في `i18n.ts`:**
```typescript
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { ... },
    fallbackLng: 'en',
    detection: {
      order: ['localStorage'],
      caches: ['localStorage'],
    },
    ...
  });
```

**السلوك النهائي:**
- أول زيارة بدون تفضيل محفوظ → English
- وجود قيمة محفوظة في localStorage → استخدامها
- زر EN/AR يعمل للتبديل
- الصفحات العامة تدعم EN/AR
- RTL/LTR يعملان حسب اللغة

### 5.3 المفاتيح المطلوبة الجديدة

#### في `en/translation.json`:
```json
"public": {
  "nav": {
    "home": "Home",
    "about": "About",
    "products": "Products",
    "services": "Services",
    "markets": "Markets",
    "contact": "Contact"
  },
  "home": {
    "heroTitle": "Nile Key for Investment and International Trade LLC",
    "heroSubtitle": "From Egyptian Fields and Factories to Global Markets",
    "heroDescription": "We connect suppliers, customers, and logistics partners in one digital ecosystem enabling shipment tracking, invoice management, and streamlined customs procedures.",
    "ctaSignIn": "Sign In",
    "ctaCreateAccount": "Create Account",
    "companySummaryTitle": "We are Your Strategic Partner in Global Trade",
    "companySummaryP1": "Nile Key for Investment and International Trade LLC is an Egyptian limited liability company, licensed by the General Authority for Investment and Free Zones.",
    "companySummaryP2": "The purpose of establishment is to showcase the quality of Egyptian products — vegetables, fruits, and national factory products — in global markets.",
    "companySummaryP3": "We focus on marketing and exporting carefully selected Egyptian products, and connecting Egyptian suppliers and producers to clients, importers and international partners, through an integrated system combining commercial expertise, export process management, and modern digital solutions.",
    "platformTitle": "Our Integrated Digital Platform for Managing Egyptian Export Operations",
    "platformP1": "We have developed the Nile Key system to be an integrated digital environment for managing and monitoring trade and export operations — from the product and supplier, through the client, invoice, documents and shipment, and all the way to the port and global markets.",
    "platformP2": "We aim to make export operations more organized, clear, efficient and reliable, by facilitating coordination among all relevant parties and supporting commercial, logistical and customs procedures within a single digital system.",
    "trustZoneTitle": "Trusted Partner",
    "trustZoneText": "Egyptian quality products trusted globally.",
    "trustedTitle": "Let's Grow Together",
    "trustedDescription": "Partner with Nile Key for export management and global market access.",
    "trustedCta": "Contact Us"
  },
  "about": {
    "title": "About Us",
    "subtitle": "Who We Are",
    "companyNameEn": "Nile Key for Investment and International Trade LLC",
    "companyNameAr": "شركة مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م)",
    "companyType": "Egyptian Limited Liability Company",
    "license": "Licensed by the General Authority for Investment and Free Zones",
    "purpose": "The purpose of establishment is to showcase the quality of Egyptian products — vegetables, fruits, and national factory products — in global markets.",
    "missionTitle": "Our Mission",
    "missionP1": "We focus on marketing and exporting carefully selected Egyptian products, and connecting Egyptian suppliers and producers to clients, importers and international partners, through an integrated system combining commercial expertise, export process management, and modern digital solutions.",
    "missionP2": "We believe that the Egyptian product is capable of competing globally whenever the right business partner, proper marketing, precise management, and commitment to quality, specifications, and target market requirements are in place.",
    "missionP3": "Therefore, our role does not stop at executing the export process, but we work to build an integrated system aimed at delivering the right Egyptian product to the right market, in the right way, and building long-term commercial relationships with clients and international partners.",
    "visionTitle": "Our Vision",
    "visionText": "To be the leading Egyptian partner in global trade, recognized for quality, reliability, and integrated digital solutions."
  },
  "products": {
    "title": "Products",
    "subtitle": "Egyptian Quality for Global Markets",
    "vegetablesTitle": "Vegetables",
    "vegetablesDesc": "Fresh vegetables selected with precision, meeting international quality standards.",
    "fruitsTitle": "Fruits",
    "fruitsDesc": "Premium Egyptian fruits, carefully packed and ready for global markets.",
    "factoryTitle": "National Factory Products",
    "factoryDesc": "Quality products from Egyptian national factories, ready for international trade.",
    "ctaExplore": "Explore Products",
    "ctaCatalog": "Request Catalog"
  },
   "services": {
    "title": "Services",
    "subtitle": "Comprehensive Export and Trade Solutions",
    "exportManagement": "Export Operations Management",
    "exportManagementDesc": "End-to-end management of export operations from planning to delivery.",
    "tradeServices": "Trade Services",
    "tradeServicesDesc": "Professional trade services to connect Egyptian suppliers with international buyers.",
    "digitalPlatform": "Digital Platform",
    "digitalPlatformDesc": "Integrated digital platform for managing shipments, invoices, documents, and customs.",
    "shipmentManagement": "Shipment Management",
    "shipmentManagementDesc": "Complete shipment tracking and management from origin to destination.",
    "invoicingDocuments": "Invoicing & Documents",
    "invoicingDocumentsDesc": "E-invoicing and document management for seamless export operations.",
    "customsProcedures": "Customs Procedures",
    "customsProceduresDesc": "Streamlined customs clearance and regulatory compliance support.",
    "partnerNetwork": "Partner Network",
    "partnerNetworkDesc": "Connecting suppliers, customers, and logistics partners in one ecosystem.",
    "whyChooseTitle": "Why Choose Nile Key",
    "whyChooseP1": "Integrated system combining commercial expertise, export management, and modern digital solutions.",
    "whyChooseP2": "Commitment to quality, reliability, and long-term commercial relationships.",
    "whyChooseP3": "Egyptian company with deep understanding of local products and global market requirements.",
    "iconExportManagement": "Workflow",
    "iconTradeServices": "Handshake",
    "iconDigitalPlatform": "LayoutDashboard",
    "iconShipmentManagement": "Truck",
    "iconInvoicingDocuments": "FileText",
    "iconCustomsProcedures": "ClipboardCheck",
    "iconPartnerNetwork": "Network"
  },
  "markets": {
    "title": "Markets",
    "subtitle": "From Egyptian Fields and Factories to Global Markets",
    "statCountries": "Countries",
    "statPartners": "Business Partners",
    "statQuality": "Commitment to Quality",
    "journeyTitle": "Your Export Journey",
    "step1Title": "Farm / Factory",
    "step1Desc": "Sourcing quality products from Egyptian farms and national factories.",
    "step2Title": "Packing & Quality",
    "step2Desc": "Rigorous quality control and professional packing to meet international standards.",
    "step3Title": "Export Documents",
    "step3Desc": "Complete documentation and regulatory compliance for smooth export clearance.",
    "step4Title": "Shipping",
    "step4Desc": "Reliable shipping arrangements with trusted logistics partners.",
    "step5Title": "Port & Delivery",
    "step5Desc": "Efficient port handling and timely delivery to the destination.",
    "step6Title": "Global Markets",
    "step6Desc": "Reaching customers and markets worldwide with Egyptian quality products."
  },
  "contact": {
    "title": "Contact Us",
    "subtitle": "Get in Touch with Our Team",
    "nameLabel": "Full Name",
    "namePlaceholder": "Enter your full name",
    "emailLabel": "Email Address",
    "emailPlaceholder": "Enter your email address",
    "subjectLabel": "Subject",
    "subjectPlaceholder": "How can we help you?",
    "messageLabel": "Message",
    "messagePlaceholder": "Tell us about your needs...",
    "sendButton": "Send Message",
    "sendingButton": "Sending...",
    "successTitle": "Message Sent Successfully",
    "successText": "Thank you for contacting us. We will get back to you shortly.",
    "errorTitle": "Error Sending Message",
    "errorText": "Something went wrong. Please try again or contact us directly.",
    "locationTitle": "Our Location",
    "locationText": "Egypt",
    "emailTitle": "Email Us",
    "phoneTitle": "Call Us"
  },
  "cta": {
    "learnMore": "Learn More",
    "getStarted": "Get Started",
    "exploreProducts": "Explore Products",
    "contactUs": "Contact Us",
    "createAccount": "Create Account",
    "signIn": "Sign In"
  },
  "footer": {
    "copyright": "© 2026 Nile Key for Investment & International Trade. All rights reserved.",
    "companyName": "Nile Key for Investment and International Trade LLC",
    "tagline": "Digital Export Platform"
  }
}
```

#### في `ar/translation.json`:
```json
"public": {
  "nav": {
    "home": "الرئيسية",
    "about": "من نحن",
    "products": "المنتجات",
    "services": "الخدمات",
    "markets": "الأسواق",
    "contact": "اتصل بنا"
  },
  "home": {
    "heroTitle": "شركة مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م)",
    "heroSubtitle": "من المزارع والمصانع المصرية إلى الأسواق العالمية",
    "heroDescription": "نربط الموردين والعملاء والجهات اللوجستية في منظومة رقمية واحدة تتيح تتبع الشحنات وإدارة الفواتير وتسهيل الإجراءات الجمركية.",
    "ctaSignIn": "تسجيل الدخول",
    "ctaCreateAccount": "إنشاء حساب",
    "companySummaryTitle": "نحن شريكك الاستراتيجي في التجارة العالمية",
    "companySummaryP1": "شركة مفتاح النيل للاستثمار والتجارة الدولية هي شركة مصرية ذات مسؤولية محدودة، مرخصة من الهيئة العامة للاستثمار والمناطق الحرة.",
    "companySummaryP2": "هدف التأسيس هو إشهار جودة المنتج المصري من خضروات وفواكه ومنتجات المصانع الوطنية في الأسواق العالمية.",
    "companySummaryP3": "نركز على تسويق وتصدير المنتجات المصرية المختارة بعناية، وربط الموردين والمنتجين المصريين بالعملاء والمستوردين والشركاء الدوليين، من خلال منظومة متكاملة تجمع بين الخبرة التجارية وإدارة عمليات التصدير والحلول الرقمية الحديثة.",
    "platformTitle": "منصتنا الرقمية المتكاملة لإدارة عمليات التصدير المصرية",
    "platformP1": "طوّرنا منظومة Nile Key لتكون بيئة رقمية متكاملة لإدارة ومتابعة عمليات التجارة والتصدير، بدءًا من المنتج والمورد، مرورًا بالعميل والفاتورة والمستندات والشحن، ووصولًا إلى الميناء والأسواق العالمية.",
    "platformP2": "نهدف إلى جعل عمليات التصدير أكثر تنظيمًا ووضوحًا وكفاءة وموثوقية، مع تسهيل التنسيق بين مختلف الأطراف ذات الصلة، ودعم الإجراءات التجارية واللوجستية والجمركية ضمن منظومة رقمية واحدة.",
    "trustZoneTitle": "شريك موثوق",
    "trustZoneText": "منتجات مصرية عالية الجودة موثوقة عالميًا.",
    "trustedTitle": "لننطلق معًا نحو الأسواق العالمية",
    "trustedDescription": "شريكك في إدارة عمليات التصدير وربط المنتج المصري بالمشتري العالمي.",
    "trustedCta": "تواصل معنا"
  },
  "about": {
    "title": "من نحن",
    "subtitle": "من نحن",
    "companyNameEn": "Nile Key for Investment and International Trade LLC",
    "companyNameAr": "شركة مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م)",
    "companyType": "شركة مصرية ذات مسؤولية محدودة",
    "license": "مرخصة من الهيئة العامة للاستثمار والمناطق الحرة",
    "purpose": "هدف التأسيس هو إشهار جودة المنتج المصري من خضروات وفواكه ومنتجات المصانع الوطنية في الأسواق العالمية.",
    "missionTitle": "رسالتنا",
    "missionP1": "نركز على تسويق وتصدير المنتجات المصرية المختارة بعناية، وربط الموردين والمنتجين المصريين بالعملاء والمستوردين والشركاء الدوليين، من خلال منظومة متكاملة تجمع بين الخبرة التجارية وإدارة عمليات التصدير والحلول الرقمية الحديثة.",
    "missionP2": "نؤمن بأن المنتج المصري يمتلك القدرة على المنافسة عالميًا متى وجد الشريك التجاري المناسب والتسويق الصحيح والإدارة الدقيقة والالتزام بالجودة والمواصفات ومتطلبات الأسواق المستهدفة.",
    "missionP3": "لذلك لا يقتصر دورنا على تنفيذ عملية التصدير، بل نعمل على بناء منظومة متكاملة تهدف إلى إيصال المنتج المصري المناسب إلى السوق المناسب وبالطريقة المناسبة، وبناء علاقات تجارية طويلة الأمد مع العملاء والشركاء الدوليين.",
    "visionTitle": "رؤيتنا",
    "visionText": "أن نكون الشريك المصري الرائد في التجارة العالمية، معروفين بالجودة والموثوقية والحلول الرقمية المتكاملة."
  },
  "products": {
    "title": "المنتجات",
    "subtitle": "جودة مصرية للأسواق العالمية",
    "vegetablesTitle": "الخضروات",
    "vegetablesDesc": "خضروات طازجة مختارة بدقة، تلبي معايير الجودة الدولية.",
    "fruitsTitle": "الفواكه",
    "fruitsDesc": "فواكه مصرية مميزة، معبأة بعناية وجاهزة للأسواق العالمية.",
    "factoryTitle": "منتجات المصانع الوطنية",
    "factoryDesc": "منتجات ذات جودة من المصانع الوطنية المصرية، جاهزة للتجارة الدولية.",
    "ctaExplore": "استكشف المنتجات",
    "ctaCatalog": "اطلب الكتالوج"
  },
   "services": {
    "title": "الخدمات",
    "subtitle": "حلول شاملة للتصدير والتجارة",
    "exportManagement": "إدارة عمليات التصدير",
    "exportManagementDesc": "إدارة كاملة لعمليات التصدير من التخطيط حتى التسليم.",
    "tradeServices": "الخدمات التجارية",
    "tradeServicesDesc": "خدمات تجارية احترافية لربط الموردين المصريين بالمشترين الدوليين.",
    "digitalPlatform": "المنصة الرقمية",
    "digitalPlatformDesc": "منصة رقمية متكاملة لإدارة الشحنات والفواتير والمستندات والجمارك.",
    "shipmentManagement": "إدارة الشحنات",
    "shipmentManagementDesc": "تتبع وإدارة كاملة للشحنات من المنشأ إلى الوجهة.",
    "invoicingDocuments": "الفواتير والمستندات",
    "invoicingDocumentsDesc": "فوترة إلكترونية وإدارة مستندات لعمليات تصدير سلسة.",
    "customsProcedures": "الإجراءات الجمركية",
    "customsProceduresDesc": "تسهيل التخليص الجمركي ودعم الامتثال التنظيمي.",
    "partnerNetwork": "شبكة الشركاء",
    "partnerNetworkDesc": "ربط الموردين والعملاء والجهات اللوجستية في منظومة واحدة.",
    "whyChooseTitle": "لماذا تختار مفتاح النيل",
    "whyChooseP1": "منظومة متكاملة تجمع بين الخبرة التجارية وإدارة التصدير والحلول الرقمية الحديثة.",
    "whyChooseP2": "الالتزام بالجودة والموثوقية وبناء علاقات تجارية طويلة الأمد.",
    "whyChooseP3": "شركة مصرية ذات فهم عميق للمنتجات المحلية ومتطلبات الأسواق العالمية.",
    "iconExportManagement": "Workflow",
    "iconTradeServices": "Handshake",
    "iconDigitalPlatform": "LayoutDashboard",
    "iconShipmentManagement": "Truck",
    "iconInvoicingDocuments": "FileText",
    "iconCustomsProcedures": "ClipboardCheck",
    "iconPartnerNetwork": "Network"
  },
  "markets": {
    "title": "الأسواق العالمية",
    "subtitle": "من المزارع والمصانع المصرية إلى الأسواق العالمية",
    "statCountries": "دولة",
    "statPartners": "شريكًا تجاريًا",
    "statQuality": "التزام بالجودة",
    "journeyTitle": "رحلة التصدير",
    "step1Title": "المزرعة / المصنع",
    "step1Desc": "توفير منتجات ذات جودة من المزارع والمصانع المصرية.",
    "step2Title": "التغليف والجودة",
    "step2Desc": "فحص جودة دقيق وتغليف احترافي يلبي المعايير الدولية.",
    "step3Title": "مستندات التصدير",
    "step3Desc": "توثيق كامل وامتثال تنظيمي لتسهيل التخليص الجمركي.",
    "step4Title": "الشحن",
    "step4Desc": "ترتيبات شحن موثوقة مع شركاء لوجستيين موثوقين.",
    "step5Title": "الميناء والتسليم",
    "step5Desc": "معالجة فعالة في الميناء وتسليم في الوقت المحدد إلى الوجهة.",
    "step6Title": "الأسواق العالمية",
    "step6Desc": "الوصول إلى العملاء والأسواق في جميع أنحاء العالم بمنتجات مصرية عالية الجودة."
  },
  "contact": {
    "title": "اتصل بنا",
    "subtitle": "تواصل مع فريقنا",
    "nameLabel": "الاسم الكامل",
    "namePlaceholder": "أدخل اسمك الكامل",
    "emailLabel": "البريد الإلكتروني",
    "emailPlaceholder": "أدخل بريدك الإلكتروني",
    "subjectLabel": "الموضوع",
    "subjectPlaceholder": "كيف يمكننا مساعدتك؟",
    "messageLabel": "الرسالة",
    "messagePlaceholder": "أخبرنا عن احتياجاتك...",
    "sendButton": "إرسال الرسالة",
    "sendingButton": "جاري الإرسال...",
    "successTitle": "تم إرسال الرسالة بنجاح",
    "successText": "شكرًا لتواصلك معنا. سنرد عليك قريبًا.",
    "errorTitle": "خطأ في إرسال الرسالة",
    "errorText": "حدث خطأ ما. يرجى المحاولة مرة أخرى أو الاتصال بنا مباشرة.",
    "locationTitle": "موقعنا",
    "locationText": "مصر",
    "emailTitle": "البريد الإلكتروني",
    "phoneTitle": "الهاتف"
  },
  "cta": {
    "learnMore": "معرفة المزيد",
    "getStarted": "ابدأ الآن",
    "exploreProducts": "استكشف المنتجات",
    "contactUs": "تواصل معنا",
    "createAccount": "إنشاء حساب",
    "signIn": "تسجيل الدخول"
  },
  "footer": {
    "copyright": "© 2026 مفتاح النيل للاستثمار والتجارة الدولية. جميع الحقوق محفوظة.",
    "companyName": "شركة مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م)",
    "tagline": "المنصة الرقمية للتصدير"
  }
}
```

### 5.3 القاعدة
- **اللغة الافتراضية عند الفتح لأول مرة:** الإنجليزية
- **اللغة المحفوظة في النظام:** إذا كان هناك لغة محفوظة في `localStorage`، استخدمها
- **زر العربية:** موجود ويعمل للتبديل
- **جميع الصفحات العامة تدعم اللغتين**
- **لا تغيير جوهري في نظام الترجمة الحالي** - فقط تعديل `fallbackLng` وترتيب الكشف لضمان السلوك المطلوب

### 5.4 ملاحظة على ملف `ar/translation.json`
- أضف قسم `public` في نهاية الملف أو في موقع منظم
- لا تعدل الأقسام الموجودة خارج النطاق

---

## 6. الملفات الحالية التي يجب تعديلها

| الملف | التعديل المطلوب |
|-------|----------------|
| `frontend/src/App.tsx` | إضافة المسارات العامة الجديدة (`/about`, `/products`, `/services`, `/markets`, `/contact`) كـ public routes مستقلة خارج `PrivateRoute` |
| `frontend/src/lib/i18n.ts` | تعديل `fallbackLng` إلى `'en'` وترتيب `detection.order` ليكون `['localStorage']` فقط. لا يعتمد على `navigator.language`. |
| `frontend/src/locales/en/translation.json` | إضافة قسم `public` كامل مع جميع المفاتيح الجديدة |
| `frontend/src/locales/ar/translation.json` | إضافة قسم `public` كامل مع جميع المفاتيح الجديدة |
| `frontend/src/pages/PublicLanding.tsx` | تعديل المحتوى ليكون `PublicHome` - الصفحة الرئيسية العامة |

---

## 7. الملفات الجديدة المطلوبة فقط

### ملفات الصفحات

```
frontend/src/pages/PublicAbout.tsx      # صفحة من نحن
frontend/src/pages/PublicProducts.tsx   # صفحة المنتجات
frontend/src/pages/PublicServices.tsx   # صفحة الخدمات
frontend/src/pages/PublicMarkets.tsx    # صفحة الأسواق العالمية
frontend/src/pages/PublicContact.tsx    # صفحة الاتصال مع نموذج اتصال كامل
```

**ملاحظة:** `PublicHome` 為概念名稱，實際實作檔案為 `PublicLanding.tsx`，直接修改該檔案完成，不創建新檔。

### ملفات المكونات المشتركة

```
frontend/src/components/public/
  PublicNavbar.tsx       # الشريط العلوي الموحد - يُستخدم في جميع الصفحات العامة
  PublicFooter.tsx       # Footer احترافي موحد - يُستخدم في جميع الصفحات العامة
  ProductCard.tsx        # بطاقة منتج - تُستخدم في PublicProducts فقط
  ServiceCard.tsx        # بطاقة خدمة - تُستخدم في PublicServices فقط
  MarketStepCard.tsx     # بطاقة خطوة رحلة التصدير - تُستخدم في PublicMarkets فقط
```

---

## 8. الهوية البصرية (Design System)

### 8.1 الألوان
- **الخلفيات الداكنة:** `#002f32`, `#00383b`
- **التدرجات:** ممنوعة في الأقسام ما عدا Hero
- **الأخضر الزمردي:** `emerald-500`, `emerald-600`, `emerald-700`
- **النصوص:** `text-white`, `text-slate-300`, `text-slate-400`
- **البطاقات:** `bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10`

### 8.2 الأزرار
- **Primary:** `bg-emerald-600 hover:bg-emerald-700 text-white`
 - **Outline:** `border-white text-white hover:bg-white/10 hover:text-emerald-500`
- **Ghost:** `text-white hover:text-emerald-400`

### 8.3 المسافات والأحجام
- **Section padding:** `py-20` desktop, `py-14` tablet, `py-10` mobile
- **Card padding:** `p-6`
- **Border radius:** `rounded-2xl`, `rounded-xl`

### 8.4 التصميم المتجاوب
- **Large desktop:** ≥1536px
- **Standard desktop:** 1280px - 1535px
- **Laptop:** 1024px - 1279px
- **Tablet landscape:** 768px - 1023px
- **Tablet portrait:** 480px - 767px
- **Large mobile:** 375px - 479px
- **Standard mobile:** 320px - 374px

---

## 9. البنية التحتية للصور

### 9.1 مسارات الأصول

```
frontend/public/assets/
  hero-export.jpg           # Hero image - مصر/زراعة/تصدير/أسواق عالمية
  about-egypt.jpg           # About image - مشهد مصري
  products/
    vegetables.jpg           # صورة خضروات
    fruits.jpg               # صورة فواكه
    factory.jpg              # صورة مصانع وطنية
  services/
    services-bg.jpg          # خلفية قسم الخدمات
```

### 9.2 كيفية إدخال الأصول
1. يوفر صاحب المشروع الأصول البصرية (صور حقيقية)
2. توضع الصور في `frontend/public/assets/` ومجلداته الفرعية
3. يُستخدم `<img src="/assets/..." />` في المكونات فقط

### 9.3 قيود المحتوى البصري
- لا يُسمح باختراع صور أو استخدام placeholders نهائية
- يجب تحديد المصدر الحقيقي لكل صورة
- إذا لم تتوفر الأصول بعد، يُعلَّق التنفيذ حتى توفرها صاحب المشروع

---

## 10. Contact Form - التنفيذ الفني

### 10.1 الحقول
- Full Name (مطلوب)
- Email Address (مطلوب، تحقق من صيغة البريد)
- Subject (مطلوب)
- Message (مطلوب، حد أدنى من الأحرف)

### 10.2 حالات النموذج
- `idle` - الحالة الابتدائية
- `submitting` - جاري الإرسال
- `success` - تم الإرسال بنجاح
- `error` - خطأ في الإرسال

### 10.3 التحقق (Client-side)
- تحقق من صحة البريد الإلكتروني
- تحقق من عدم وجود حقول فارغة
- تحقق من طول الرسالة (حد أدنى)

### 10.4 الربط بالـBackend
- يُرسل النموذج إلى endpoint الاتصالات الحالي في المشروع فقط.
- إذا لم يوجد endpoint مناسب، يُعتبر ذلك Blocker قبل التنفيذ ولا يُنشَأ Backend جديد ضمن هذه الخطة.
- بعد التعديل يجب أن يبقى Backend وDEM والأنظمة الداخلية دون تعديل.

### 10.5 معالجة الأخطاء
- عرض رسائل خطأ واضحة للمستخدم
- إمكانية إعادة المحاولة
- في حالة فشل الإرسال، عرض وسائل اتصال بديلة (إن وجدت)

---

## 11. معايير القبول البصرية والوظيفية

### 11.1 معايير القبول البصرية
1. **الخلفيات:** داكنة (`#002f32`, `#00383b`) مع الأخضر الزمردي
2. **الألوان:** الأخضر الزمردي (`emerald-500`, `emerald-600`, `emerald-700`) كلون أساسي
3. **البطاقات:** `bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10`
4. **الأزرار:** `bg-emerald-600 hover:bg-emerald-700 text-white`
5. **الخطوط:** واضحة، بسيطة، مؤسسية راقية
6. **المساحات:** generous padding داخلي (py-20 desktop, py-14 tablet, py-10 mobile)
7. **التصميم المتجاوب:** يعمل على Desktop / Tablet / Mobile
8. **الصور:** جميع الصور المحددة في القسم 4 موجودة وتُعرض بشكل صحيح

### 11.2 معايير القبول الوظيفية
1. **التنقل:** جميع روابط الشريط العلوي تعمل فعلياً وتقود إلى الصفحات الصحيحة
2. **الترجمة:** جميع الصفحات تدعم EN/AR
3. **اللغة الافتراضية:** عند أول زيارة بدون تفضيل محفوظ، تبدأ بالإنجليزية
4. **الأداء:** لا يوجد تأخير ملحوظ في التبديل بين الصفحات
5. **الأصول:** لا توجد صور مفقودة أو broken links
6. **الـ Accessibility:** أزرار التنقل يمكن الوصول إليها بـ keyboard
7. **Contact Form:** يعمل بشكل كامل مع التحقق والإرسال ومعالجة الأخطاء

### 11.3 القيود الصارمة (يجب الالتزام بها)
1. **لا تمس DEM** أو Customers أو Suppliers أو أي نظام داخلي
2. **لا تغيّر منطق المصادقة**
3. **لا تنشئ بنية معمارية جديدة**
4. **لا تنشئ محركًا جديدًا أو طبقة منطق جديدة**
5. **لا تغيّر الهوية الحالية للمنصة**
6. **لا تحذف الوظائف الموجودة**
7. **لا تضف صفحات داخلية للمستخدمين المسجلين**
8. **النطاق هو Public Website Experience فقط**

### 11.4 قيود المحتوى
1. **لا تخترع أرقامًا** مثل عدد الدول أو العملاء
2. **لا تضف شهادات أو شعارات** جهات اعتماد غير موجودة
3. **لا تضف شركاء أو عملاء وهميين**
4. **لا تضف ادعاءات تجارية غير مثبتة**
5. **استخدم فقط المحتوى الموجود فعلياً في المشروع**
6. **لا تخترع صورًا أو بيانات تجارية**

---

## 12. خطة التنفيذ المقترحة (مرتبة)

### المرحلة 1: البنية التحتية والترجمة
1. تعديل `frontend/src/lib/i18n.ts` لضمان اللغة الافتراضية الإنجليزية
2. إضافة قسم `public` كامل إلى `frontend/src/locales/en/translation.json`
3. إضافة قسم `public` كامل إلى `frontend/src/locales/ar/translation.json`
4. إنشاء مجلد `frontend/src/components/public/`
5. إنشاء `PublicNavbar.tsx`
6. إنشاء `PublicFooter.tsx`
7. تحديث `App.tsx` بإضافة المسارات العامة الجديدة كـ public routes

### المرحلة 2: الصفحات الأساسية
8. تعديل `frontend/src/pages/PublicLanding.tsx` ليكون `PublicHome`
9. إنشاء `PublicAbout.tsx`
10. إنشاء `PublicContact.tsx` مع نموذج اتصال كامل

### المرحلة 3: الصفحات الإضافية
11. إنشاء `PublicProducts.tsx`
12. إنشاء `PublicServices.tsx`
13. إنشاء `PublicMarkets.tsx`

### المرحلة 4: الأصول البصرية
14. وضع الصور المحددة في `frontend/public/assets/` ومجلداته الفرعية
15. ربط الصور بالمكونات

### المرحلة 5: التحقق والاختبار
16. اختبار جميع المسارات العامة
17. اختبار الترجمة EN/AR واللغة الافتراضية
18. اختبار الاستجابة على مختلف الأحجام
19. التحقق من عدم كسر الوظائف الموجودة
20. التحقق من وجود جميع الصور وعملها

---

## 13. ملاحظات تقنية مهمة

### 13.1 حماية المسارات
- جميع المسارات الجديدة (`/about`, `/products`, إلخ) **ليست محمية** - متاحة للجميع
- لا تحتاج إلى `PrivateRoute`
- المسارات المحمية تبقى كما هي داخل `/` مع `PrivateRoute`

### 13.2 RTL Support
- استخدم `dir={isArabic ? 'rtl' : 'ltr'}` في كل صفحة
- استخدم `useTranslation()` للحصول على اللغة الحالية
- استخدم Tailwind classes مناسبة للـ RTL (مثل `ms-*`, `me-*` بدلاً من `ml-*`, `mr-*` عند الحاجة)

### 13.3 `PublicLanding` مقابل `PublicHome`
- `PublicLanding.tsx` يُعدَّل مباشرة ليكون الصفحة الرئيسية العامة
- لا حاجة لإعادة تسمية الملف
- لا يُنشأ `PublicHome.tsx` جديد أبدًا
- لا يُزال `PublicLanding.tsx`

### 13.4 تقييد النطاق
- النطاق هو **Public Website Experience فقط**
- لا تمس DEM أو Customers أو Suppliers أو أي نظام داخلي
- لا تغيّر منطق المصادقة
- لا تنشئ بنية معمارية جديدة

---

## 14. المخاطر والقيود

### 14.1 مخاطر محتملة
1. **تعطل المسارات الموجودة:** mitigé بـ اختبار المسارات بعد كل تعديل
2. **مفاتيح ترجمة مفقودة:** mitigé بـ قائمة مفاتيح شاملة في القسم 5
3. **مشاكل RTL:** mitigé بـ اختبار كل صفحية باللغتين
4. **صور مفقودة:** mitigé بـ تحديد مصادر الصور بوضوح في القسم 4

### 14.2 قيود صارمة
- لا تغيير في ملف `ar/translation.json` خارج قسم `public` الجديد
- لا تعديل على أي ملف في `src/store/` أو `src/services/`
- لا تعديل على أي ملف في `src/components/layout/` ما عدا `LanguageSwitcher` إذا لزم الأمر
- لا إنشاء ملفات اختبار جديدة (الاختبارات الحالية كافية)
- لا اختراع صور أو بيانات تجارية
- لا placeholders نهائية للصور

---

## Concept 1 — Visual Design Execution Specification

> **المبدأ الحاكم:**
> الخطة الحالية + هذا القسم = المرجع الحاكم الكامل للتنفيذ.
> أي تعارض بين القسمين → هذا القسم (Design Execution Specification) هو الأعلى أولوية بصرية.
> أي عنصر غير محدد هنا → لا يُخترع عشوائيًا في مرحلة الكود، بل يُعالج داخل الخطة أولاً.

---

### 1. Page Composition

التكوين النهائي للصفحة العامة (PublicHome) مرتب من الأعلى إلى الأسفل:

```
Navbar
→ Hero
→ Our Company
→ Premium Egyptian Products
→ The Export Journey
→ Digital Platform
→ Global Markets
→ Trusted Partners / CTA
→ Footer
```

**القاعدة:**
- الأقسام Full-width وتنتقل مباشرة من Section إلى الذي يليه.
- لا يوجد gap أو spacing خارجي بين الأقسام.
- المساحات المطلوبة تكون داخل كل Section فقط (padding داخلي).
- Desktop: padding داخلي كبير ومتوازن.
- Tablet: أقل.
- Mobile: أقل.
- يُمنع إنشاء شرائط فراغ بيضاء/داكنة بين الأقسام.

**مواصفات كل قسم داخل الصفحة:**

| القسم | position | min-height | max-width | horizontal alignment | vertical alignment | column ratio | content density | inter-section spacing |
|--------|----------|-----------|-----------|---------------------|-------------------|--------------|----------------|----------------------|
| Navbar | fixed top | 64px | 1280px | center | center | — | low | 0px (fixed, فوق المحتوى) |
| Hero | section 1 | 90vh (min) / auto | 1280px | center | center | 45/55 text/image | medium | 0px (مباشر) |
| Our Company | section 2 | auto | 1280px | center | center | 55/45 text/image | low | 0px (مباشر) |
| Premium Egyptian Products | section 3 | auto | 1280px | center | start | 1 col / 3 equal cards | medium | 0px (مباشر) |
| The Export Journey | section 4 | auto | 1280px | center | start | 1 col / 5-step horizontal | low | 0px (مباشر) |
| Digital Platform | section 5 | auto | 1280px | center | center | 45/55 text/dashboard | medium | 0px (مباشر) |
| Global Markets | section 6 | auto | 1280px | center | center | 40/60 text/visual | low | 0px (مباشر) |
| Trusted Partners / CTA | section 7 | auto | 1280px | center | center | 50/50 trust/CTA | medium | 0px (مباشر) |
| Footer | section 8 | auto | 1280px | center | start | 4 columns | low | 0px (نهاية الصفحة) |

- **horizontal alignment** لكل قسم: container بحد أقصى 1280px، محاذاة `mx-auto`.
- **vertical alignment** لكل قسم: padding عمودي `py-20` على Desktop، `py-14` على Tablet، `py-10` على Mobile.
- **content density**: low = مساحة سلبية كبيرة، medium = توازن بين العنصر والسلبية.
- **العناصر لا تحتاج spacing إضافي داخلي**: الـ padding المحدد لكل قسم يكفي.

---

### 2. Visual Hierarchy

لكل قسم من أقسام PublicHome:

**Hero**
- Primary: Hero Image (يمين، 55% من العرض)
- Secondary: Heading + Description (يسار، 45% من العرض)
- ما يلفت النظر أولًا: Hero Image
- ما لا ينافس: وصف الشركة (لا يوجد وصف طويل في Hero)
- مستوى الكثافة: medium (هيكل قوي + صورة + 2 CTA)
- مساحة سلبية: 24px بين heading و description، 32px بين description وأول CTA

**Our Company**
- Primary: Image Block (يمين، 45%)
- Secondary: Heading + Paragraphs (يسار، 55%)
- ما يلفت النظر أولًا: Heading (نصي)
- ما لا ينافس: الصورة (داعمة فقط، لا تطفو على النص)
- مستوى الكثافة: low (نص قليل + مساحة سلبية)
- مساحة سلبية: 48px بين النص والصورة

**Premium Egyptian Products**
- Primary: Section Heading
- Secondary: 3 Cards متساوية (كل card: صورة منتج + عنوان)
- ما يلفت النظر أولًا: Section Heading ثم Cards الثلاث
- ما لا ينافس: لا يوجد عنصر ثالث يستهلك الانتباه
- مستوى الكثافة: medium (3 عناصر متساوية الأهمية)
- مساحة سلبية: 24px بين الصورة والعنوان داخل كل card

**The Export Journey**
- Primary: Step title + connector line
- Secondary: Step description
- ما يلفت النظر أولًا: السطر المتصل + النقاط
- ما لا ينافس: أي design زخرفي يشتت عن المسار
- مستوى الكثافة: low (مسار واحد واضح)
- مساحة سلبية: 16px بين الخطوة والتالية

**Digital Platform**
- Primary: Dashboard/UI Composition (يمين، 55%)
- Secondary: Heading + 4 Features (يسار، 45%)
- ما يلفت النظر أولًا: Dashboard UI
- ما لا ينافس: قائمة الميزات الطويلة (4 فقط، مختصرة)
- مستوى الكثافة: medium (UI + features)
- مساحة سلبية: 16px بين كل ميزة والأخرى

**Global Markets**
- Primary: World/Global Visual (يمين، 60%)
- Secondary: Statistics + Heading (يسار، 40%)
- ما يلفت النظر أولًا: World Visual
- ما لا ينافس: الإحصائيات (3 فقط، قصيرة)
- مستوى الكثافة: low
- مساحة سلبية: 32px بين الإحصائيات

**Trusted Partners / CTA**
- Primary: CTA Zone (نصف القسم)
- Secondary: Trust Zone (نصف القسم)
- ما يلفت النظر أولًا: CTA
- ما لا ينافس: نص Trust (عرضي قصير)
- مستوى الكثافة: medium
- مساحة سلبية: 24px بين القسمين
- Trust Zone uses `public.home.trustZoneTitle` + `public.home.trustZoneText`
- CTA Zone uses `public.home.trustedTitle` + `public.home.trustedDescription` + `public.home.trustedCta`

**Footer**
- Primary: Logo + Brand
- Secondary: 3 columns of links
- ما يلفت النظر أولًا: Logo
- ما لا ينافس: روابط مفككة (كل عمود منفصل)
- مستوى الكثافة: low
- مساحة سلبية: 32px بين الأعمدة

---

### 3. Exact Section Geometry

المواصفات الهندسية لكل قسم:

**Navbar**
- height: 64px ثابتة (desktop و tablet)
- height: 56px (mobile)
- max-width container: 1280px
- padding: px-6
- spacing بين العناصر: 32px بين logo و nav، 24px بين nav و language/auth
- logo zone width: ~120px
- nav zone: flexible (6 روابط)
- language zone width: ~80px
- auth CTA zone width: ~200px

**Hero**
- min-height: 90vh
- max-width: 1280px
- padding: py-20 desktop, py-14 tablet, py-10 mobile
- column ratio: 45/55 (text/image) على desktop
 - column ratio: 1 col (image فوق، text تحت) على mobile
 - image fills the available visual height of the Hero content area and remains a large primary visual; minimum rendered height is 400px on desktop/laptop
- image width: 100% من عمودها
- content width للـ text: 480px max
- gap بين العمودين: 48px
- spacing بين CTA buttons: 16px
- vertical alignment: center لكل عمود

**Our Company**
- min-height: auto
- max-width: 1280px
- padding: py-20 desktop, py-14 tablet, py-10 mobile
- column ratio: 55/45 (text/image) على desktop
- column ratio: 1 col (image فوق، text تحت) على mobile
- image width: 100% من عمودها
- image height ratio: 4/3 (aspect-ratio)
- content width للـ text: 520px max
- gap بين العمودين: 48px

**Premium Egyptian Products**
- min-height: auto
- max-width: 1280px
- padding: py-20 desktop, py-14 tablet, py-10 mobile
- 3 cards: width متساوية (each ~33.33% - 16px gap)
- card width: 100% من العمود على mobile
- card padding: p-6
- card border-radius: rounded-2xl
- card border: border border-white/10
- card shadow: shadow-lg
- image height ratio داخل كل card: 3/2 (aspect-ratio)
- gap بين cards: 24px
- content density: medium
- section heading padding-bottom: 48px

**The Export Journey**
- min-height: auto
- max-width: 1280px
- padding: py-20 desktop, py-14 tablet, py-10 mobile
- 5 steps: flex-row على desktop
- 5 steps: flex-col على mobile
- step width: ~20% على desktop (5 متساوية)
- node size: 48px diameter (الدائرة المتصلة)
- connector line: height 3px، width 100% بين العقد
- spacing بين الخطوات: 32px على desktop
- spacing بين الخطوات: 24px على mobile (stacked)
- content width لكل step: 200px max

**Digital Platform**
- min-height: auto
- max-width: 1280px
- padding: py-20 desktop, py-14 tablet, py-10 mobile
- column ratio: 45/55 (text/dashboard) على desktop
- column ratio: 1 col على mobile
- dashboard width: 100% من عمودها
 - dashboard height: ~500px على desktop
 - dashboard height: ~400px على tablet
 - dashboard height: ~350px على mobile
- gap بين العمودين: 48px
- 4 features: gap 16px
- feature icon size: 24px
- feature heading size: 18px

**Global Markets**
- min-height: auto
- max-width: 1280px
- padding: py-20 desktop, py-14 tablet, py-10 mobile
- column ratio: 40/60 (text/visual) على desktop
- column ratio: 1 col على mobile
- visual width: 100% من عمودها
- visual height ratio: 16/9 على desktop
- visual height: ~400px
- content width للـ text: 400px max
- gap بين العمودين: 48px
 - 3 statistics: 50+ (`public.markets.statCountries`), 200+ (`public.markets.statPartners`), 100% (`public.markets.statQuality`). gap 24px

**Trusted Partners / CTA**
- min-height: auto
- max-width: 1280px
- padding: py-20 desktop, py-14 tablet, py-10 mobile
- column ratio: 50/50 (trust/CTA) على desktop
- column ratio: 1 col على mobile
- gap بين القسمين: 48px
- CTA button size: height 48px، padding 16px 32px
- Trust Zone uses `public.home.trustZoneTitle` + `public.home.trustZoneText`
- CTA Zone uses `public.home.trustedTitle` + `public.home.trustedDescription` + `public.home.trustedCta`

**Footer**
- min-height: auto
- max-width: 1280px
- padding: py-16 desktop, py-12 tablet, py-10 mobile
- 4 columns على desktop: gap 48px
- 2 columns على tablet: gap 32px
- 1 column على mobile: gap 24px
- column width: ~25% على desktop
- logo zone: ~150px width
- links: Quick Links = 6，Services = 4

---

### 4. Image / Asset Specification

| Concept Element | Actual Project Asset | Section | Position | Aspect Ratio | Display Treatment | Allowed Usage | Prohibited Usage |
|----------------|---------------------|---------|----------|--------------|------------------|--------------|-----------------|
| Hero image (concept: product Egypt/export/global) | `hero-export.jpg` | Hero | Right column، full width of its column | 3/2 (aspect-ratio container) | object-cover، full bleed dentro del container | استخدام كصورة رئيسية في Hero section | concept1.png / crop من Concept / thumbnail |
| About image (concept: Egypt/mission) | `about-egypt.jpg` | Our Company | Right column، full width of its column | 4/3 | object-cover، rounded corners (rounded-2xl) | صورة داعمة في قسم Our Company في PublicHome. يجوز إعادة استخدام نفس الأصل في PublicAbout ضمن Mission/Vision عند الحاجة، دون اعتبار ذلك أصلًا جديدًا. | concept1.png / أي صورة عامة / crop |
| Product Vegetables image | `vegetables.jpg` | Premium Egyptian Products (Card 1) | داخل Card، top area | 3/2 | object-cover، full width dentro card | صورة المنتج داخل Card | concept1.png / أي placeholder |
| Product Fruits image | `fruits.jpg` | Premium Egyptian Products (Card 2) | داخل Card، top area | 3/2 | object-cover، full width dentro card | صورة المنتج داخل Card | concept1.png / أي placeholder |
| Product National Factory image | `factory.jpg` | Premium Egyptian Products (Card 3) | داخل Card، top area | 3/2 | object-cover، full width dentro card | صورة المنتج داخل Card | concept1.png / أي placeholder |
| Dashboard/Platform UI composition | Composition UI مبنية بـ HTML/CSS (non-data) | Digital Platform | Right column، full width | 16/10 (aspect-ratio container) | dark background، panels، visual cues | تمثيل بصري للوحة التحكم فقط بدون بيانات حقيقية | fake metrics / fake counts / invented data |
| World/Global Visual | Composition مبنية بـ SVG/CSS | Global Markets | Right column، full width | 16/9 | Stylized World Map + Connected Market Nodes | عنصر بصري واضح يحقق معنى الانتشار العالمي | div فارغ / dots عشوائية / decorative SVG |
| Services background | `services-bg.jpg` | PublicServices / Why Choose Nile Key | خلفية قسم | 16/9 | object-cover، opacity 20% | خلفية شفافة لقسم | concept1.png / خلفية صلبة بدون صورة |
| Trusted Partners visual | لا يوجد | Trusted Partners | — | — | لا يوجد | لا يُستخدم صورة هنا | لا يُضاف صورة لا يوجد لها أصل |

**القواعد العامة:**
- جميع الصور تُستورد من `frontend/public/assets/` أو تُبنى كـ composition بـ CSS/HTML/SVG.
- لا يُستخدم `concept1.png` أبدًا في Runtime.
- لا يُستخدم `nile-key-global-export-platform-en.jpg` أو `nile-key-export-platform-homepage-ar.jpg`.
- لا يُستخدم `ReferenceVisual` أو أي crop من Concept 1.
- كل صورة يجب أن يكون لها أصل محدد في هذا الجدول.

---

### 5. Typography Specification

**الخطوط:** استخدم Font Stack الموجود في المشروع (Tailwind default sans). لا تضف fonts خارجية جديدة. نفس الـ font family يُستخدم في English و العربية.

**لـ English:**
- Heading: `text-4xl` (36px)، weight 700، line-height 1.2
- Subheading: `text-2xl` (24px)، weight 600، line-height 1.3
- Body: `text-base` (16px)، weight 400، line-height 1.6
- Caption/small: `text-sm` (14px)، weight 400، line-height 1.5
- max-width للـ body: 65ch (1040px)
- spacing بين heading و body: 24px
- spacing بين body و CTA: 32px
- spacing بين CTA buttons: 16px

**لـ العربية:**
- Heading: `text-4xl` (36px)، weight 700، line-height 1.4
- Subheading: `text-2xl` (24px)، weight 600، line-height 1.5
- Body: `text-base` (16px)، weight 400، line-height 1.8
- Caption/small: `text-sm` (14px)، weight 400، line-height 1.6
- max-width للـ body: 65ch (1040px)
- spacing بين heading و body: 24px
- spacing بين body و CTA: 32px
- spacing بين CTA buttons: 16px

**لكل قسم:**
| القسم | eyebrow | heading | supporting text | CTA text |
|--------|---------|---------|----------------|----------|
| Hero | 14px/400 uppercase text-emerald-400 | 36px/700 | 16px/400 | 16px/500 |
| Our Company | 14px/400 uppercase text-emerald-400 | 36px/700 | 16px/400 | 16px/500 |
| Premium Egyptian Products | 14px/400 uppercase text-emerald-400 | 36px/700 | 14px/400 (inside cards) | 16px/500 |
| The Export Journey | 14px/400 uppercase text-emerald-400 | 36px/700 | 14px/400 | 16px/500 |
| Digital Platform | 14px/400 uppercase text-emerald-400 | 36px/700 | 16px/400 | 16px/500 |
| Global Markets | 14px/400 uppercase text-emerald-400 | 36px/700 | 16px/400 | 16px/500 |
| Trusted Partners / CTA | 14px/400 uppercase text-emerald-400 | 36px/700 | 16px/400 | 18px/600 |
| Footer | لا يوجد | 18px/600 | 14px/400 | 14px/400 |

**القاعدة:** جميع section headings في PublicHome تستخدم `text-4xl` (36px). ممنوع استخدام `text-3xl` لأي section heading في PublicHome.

**سلوك النص:**
- English: `dir="ltr"`، alignment left
- Arabic: `dir="rtl"`، alignment right
- جميع النصوص تستخدم نفس الـ class structure لكن مع `dir` مختلف
- الخط لا يحتوي على weights مخصصة للعربية فقط؛ يستخدم نفس weights في كلتا اللغتين

---

### 6. Color / Surface System

**Palette ثابتة (Concept 1 المعتمد):**

Dark:
`#002f32` / `#00383b`

Light:
`#f8fafc` / white

Accent:
`#10b981` / `#059669`

التكوين البصري بين الأقسام (ألوان مطلقة، ليس نسبية):

**Hero**
- background: `#002f32`
- text color: `#ffffff` (white)
- accent: `#10b981` (emerald-500)
- border: لا يوجد حدود ظاهرة
- card surface: لا يوجد بطاقات في هذا القسم
- shadow: لا يوجد
- contrast level: high (white على dark)

**Our Company**
- background: `#f8fafc`
- text color: `#1e293b` (slate-800)
- accent: `#059669` (emerald-600)
- border: لا يوجد حدود ظاهرة
- card surface: لا يوجد بطاقات
- shadow: لا يوجد
- contrast level: high (dark على light)

**Premium Egyptian Products**
- background: `#002f32`
- text color: `#ffffff` (white)
- accent: `#10b981` (emerald-500)
- border: لا يوجد حدود ظاهرة
- card surface: `rgba(255, 255, 255, 0.05)` + `backdrop-blur-sm` + `rounded-2xl` + `border border-white/10`
- shadow: `shadow-lg` على البطاقات
- contrast level: high

**The Export Journey**
- background: `#f8fafc`
- text color: `#1e293b` (slate-800)
- accent: `#059669` (emerald-600)
- border: لا يوجد حدود ظاهرة
- card surface: لا يوجد بطاقات (خطوات على خط متصل)
- shadow: لا يوجد
- contrast level: high

**Digital Platform**
- background: `#002f32`
- text color: `#ffffff` (white)
- accent: `#10b981` (emerald-500)
- border: لا يوجد حدود ظاهرة
- card surface: لا يوجد بطاقات (dashboard composition)
- shadow: لا يوجد
- contrast level: high

**Global Markets**
- background: `#f8fafc`
- text color: `#1e293b` (slate-800)
- accent: `#059669` (emerald-600)
- border: لا يوجد حدود ظاهرة
- card surface: لا يوجد بطاقات
- shadow: لا يوجد
- contrast level: high

**Trusted Partners / CTA**
- background: `#002f32`
- text color: `#ffffff` (white)
- accent: `#10b981` (emerald-500)
- border: لا يوجد حدود ظاهرة
- card surface: لا يوجد بطاقات (split composition داخلي)
- shadow: لا يوجد
- contrast level: high

**Footer**
- background: `#001a1c` (أغمق من `#002f32`)
- text color: `#94a3b8` (slate-400)
- accent: `#10b981` (emerald-500)
- border: `border-white/10` على حدود الروابط
- card surface: لا يوجد
- shadow: لا يوجد
- contrast level: medium (text أفتح من الخلفية)

**الانتقال بين الأقسام:**
- Dark → Light: transition مباشر، لا يوجد gradient بين الأقسام
- Light → Dark: transition مباشر، لا يوجد gradient بين الأقسام
- Hero background: `#002f32` solid color only. ممنوع استخدام gradient في Hero بأي شكل.

---

### 7. Component Composition

#### 7.1 Navbar

التكوين الأفقي:

```
[Logo Zone (120px)]  [Navigation Zone (flex)]  [Language Zone (80px)]  [Auth CTA Zone (200px)]
```

- **Logo Zone**: حرف "NK" في دائرة + نص "Nile Key" بجانبه
- **Navigation Zone**: 6 روابط (Home, About, Products, Services, Markets, Contact)
- **Language Zone**: زر EN / AR (تبديل لغة)
- **Auth CTA Zone**: زر Sign In (outline) + Create Account (filled)
- **spacing**: 32px بين كل zone
- **horizontal padding**: 24px على كل جانب من الـ container
- **desktop**: Logo + 6 navigation links + Language + Sign In + Create Account
- **tablet (768px - 1023px)**: Logo + Language + Hamburger. لا Auth CTA ظاهر في الشريط.
- **mobile (< 768px)**: Logo + Language + Create Account + Hamburger

**Mobile Menu (hamburger):**
- Opens as full-width dropdown below navbar
- Contains: Logo, all nav links, language switcher, Sign In, Create Account
- Closes on link click or outside click
- Animation: slide down, 200ms

#### 7.2 Hero

التكوين:

```
+------------------------------------------+
|  [Text Zone 45%]  |  [Image Zone 55%]  |
|                   |                     |
|  Eyebrow (14px)   |                     |
|  Heading (36px)   |    [Hero Image     |
|  Description      |     object-cover   |
|  (16px)           |     aspect-3/2]    |
|                   |                     |
|  [CTA 1] [CTA 2]  |                     |
+------------------------------------------+
```

- **Text Zone**: vertical-align center، max-width 480px
- **Image Zone**: vertical-align center، full height of hero
- **Image**: `aspect-ratio: 3/2`، `object-fit: cover`، `border-radius: rounded-2xl`
- **Eyebrow**: text-emerald-400، uppercase، letter-spacing 0.1em
- **Heading**: text-4xl، weight 700، mb-6
- **Description**: text-base، weight 400، color slate-300، mb-8
- **CTA Buttons**: 2 buttons فقط. لا CTA ثالث.
  - CTA 1 (primary): Sign In
  - CTA 2 (outline): Create Account
- **Hero background**: `#002f32`، لا background image، لا text فوق الصورة، لا thumbnail treatment
- **Image prominence**: الصورة هي العنصر البصري الأكبر في Hero
- **Desktop / Laptop**: صف واحد 45/55
- **Tablet/Mobile**: stacked بدون فقدان prominence للصورة

#### 7.3 Our Company

التكوين:

```
+------------------------------------------+
|  [Heading Zone (spanning)]               |
|  [Text Zone 55%]  |  [Image Zone 45%]  |
|                   |  Heading           |
|   Heading         |  [About Image    |
|   Paragraph 1     |    aspect-4/3     |
|   Paragraph 2     |    rounded-2xl]   |
|   Paragraph 3     |                   |
|   [Learn More CTA]|                   |
+------------------------------------------+
```

- **Text Zone**: max-width 520px، vertical-align center
- **Image Zone**: `aspect-ratio: 4/3`، `object-fit: cover`، `border-radius: rounded-2xl`
 - **Heading**: text-4xl، weight 700، mb-6
- **Paragraphs**: 3 فقرات، text-base، color slate-600، line-height 1.8، spacing 16px بين كل فقرة
 - **CTA**: "Learn More" → `/about` (use `public.cta.learnMore`), text-emerald-600، underline

#### 7.4 Premium Egyptian Products

التكوين:

```
+------------------------------------------+
|  [Section Heading (center)]              |
|  "Premium Egyptian Products"             |
+------------------------------------------+
|  [Card 1]  |  [Card 2]  |  [Card 3]   |
|  [Image  ]  |  [Image  ]  |  [Image  ]  |
|  aspect-3/2 | aspect-3/2 | aspect-3/2  |
|  Title     |  Title     |  Title      |
|  Desc      |  Desc      |  Desc       |
+------------------------------------------+
|  [CTA Button (center): "Explore Products" → `/products`]                   |
+------------------------------------------+
```

- **3 Cards**: equal width (33.33% each - 16px gap)
- **Card**: `bg-white/5`، `backdrop-blur-sm`، `rounded-2xl`، `border border-white/10`، `shadow-lg`
- **Card padding**: p-6
- **Card image**: `aspect-ratio: 3/2`، `object-fit: cover`، `border-radius: rounded-xl`
- **Card title**: text-lg، weight 600، mt-4
- **Card description**: text-sm، weight 400، color slate-300، mt-2
- **Mobile**: 1 card per row

#### 7.5 The Export Journey

التكوين:

```
+------------------------------------------+
|  [Section Heading (center)]              |
|  "The Export Journey"                    |
+------------------------------------------+
|  [Node1] --- [Node2] --- [Node3] --- [Node4] --- [Node5]
|  [Title1]    [Title2]    [Title3]    [Title4]    [Title5]
|  [Desc1]     [Desc2]     [Desc3]     [Desc4]     [Desc5]
+------------------------------------------+
```

- **Connector**: خط أفقي واحد، height 3px، background `#10b981`، width 100% بين العقد
- **Nodes**: 5 دوائر، size 48px diameter، background `#10b981`، white icon في كل دائرة
- **Icons داخل العقد**: lucide-react icons
  - Node 1: Factory (المزرعة/المصنع)
  - Node 2: CheckCircle (التغليف والجودة)
  - Node 3: FileText (مستندات التصدير)
  - Node 4: Truck (الشحن)
  - Node 5: Ship (الميناء والتسليم)
- **Step spacing**: 32px بين كل خطوة
- **Title**: text-sm، weight 600، mt-4
- **Description**: text-xs، weight 400، color slate-400، mt-1
- **Mobile transformation**: خط عمودي (vertical timeline)، nodes stacked، connector على اليسار

#### 7.6 Digital Platform — Dashboard/UI Composition

التكوين:

```
+------------------------------------------+
|  [Text Zone 45%]  |  [Dashboard Zone 55%]|
|                   |                      |
|  Heading          |  [Frame]             |
|  Description      |  +-Header--------+   |
|                   |  | Nav           |   |
|  [Feature 1]      |  | [Panel 1][P2] |   |
|  [Feature 2]      |  | [Panel 3]     |   |
|  [Feature 3]      |  | [Chart Place] |   |
|  [Feature 4]      |  +----------------+   |
|                   |                      |
|  [CTA Button]     |                      |
+------------------------------------------+
```

**Dashboard Composition (شكل فقط، بدون بيانات):**
- **Frame**: dark background (`#00383b`)، rounded-2xl، border border-white/10، shadow-lg
 - **Header**: height 40px، nav cues (3 dots)، neutral visual logo mark
- **Sidebar/Nav**: width 48px، vertical icons (4-5 icons) - decoration only
- **Panels**: 3 panels inside frame:
  - Panel 1: rectángulo، width ~40%، height ~150px، border border-white/5
  - Panel 2: rectángulo، width ~55%، height ~150px، border border-white/5
  - Panel 3: rectángulo، width ~100%، height ~120px، border border-white/5
  - Chart placeholder: rectángulo con líneas decorativas (no data)
- **Color treatment**: all panels use bg-slate-800، borders border-white/5، no gradients
- **No data**: ممنوع تمامًا كتابة أرقام أو نسب أو counts أو performance figures أو fake operational data أو نصوص توحي ببيانات تشغيلية حقيقية داخل الـ panels أو الـ chart
- **Proportions**: frame height ~500px desktop، ~350px mobile
- **Spacing**: 16px بين panels

**Text Zone:**
 - Heading: text-4xl، weight 700، mb-4
- Description: text-base، color slate-300، mb-6
  - 4 Features: icon + title + description, sourced from existing PublicLanding.tsx Digital Platform content. Translation keys: `landing.features.shipments.title`, `landing.features.shipments.description`, `landing.features.invoicing.title`, `landing.features.invoicing.description`, `landing.features.customs.title`, `landing.features.customs.description`, `landing.features.intelligence.title`, `landing.features.intelligence.description`
  - Feature icon: 24px، emerald-500
  - Feature title: text-base، weight 600
  - Feature description: text-sm، color slate-400
  - spacing بين features: 16px
 - CTA: "Get Started" → `/services` (use `public.cta.getStarted`), mt-6

#### 7.7 Global Markets — Stylized World Map + Connected Market Nodes

التكوين:

```
+------------------------------------------+
|  [Text Zone 40%]  |  [Visual Zone 60%]  |
|                   |                      |
|  Heading          |  [World Visual]      |
|  Statistics:      |  16/9 aspect ratio   |
|  [50+] [200+] [100%] |  stylized map    |
|                   |  + connected nodes   |
|  Description      |                      |
|                   |                      |
|  [CTA Button]     |                      |
+------------------------------------------+
```

**World Visual Composition:**
- **Type**: Stylized World Map + connected market nodes فقط. لا خيار آخر.
- **Aspect ratio**: 16/9
- **Background**: transparent
- **Content**: world-map silhouette واضحة + 6-8 market nodes + thin connecting lines + subtle glow على nodes
- **Style**: minimal، institutional، not decorative
- **No text inside visual**: ممنوع كتابة أسماء دول أو أرقام داخل الـ visual
- **Size**: full width of its column، height ~400px desktop
- **Proportions**: 60% width، aspect-ratio 16/9
- **Color**: `#10b981` dots/lines
- **Background**: transparent

**Statistics Integration (في Text Zone، ليس داخل الـ visual):**
- 3 statistics: 50+ / 200+ / 100%
- layout: horizontal، gap 24px
- each stat: number (text-3xl، weight 700، emerald-500) + label (text-sm، color slate-400)
 - spacing بين الإحصائيات والوصف: 24px
 - **CTA**: "Contact Us" → `/contact` (use `public.cta.contactUs`)

#### 7.8 Trusted Partners / CTA

التكوين:

```
+------------------------------------------+
|  [Trust Zone 50%]  |  [CTA Zone 50%]    |
|                   |                      |
|  trustZoneTitle   |  trustedTitle        |
|  trustZoneText    |  trustedDescription  |
|                   |  [trustedCta Button] |
|                   |                      |
+------------------------------------------+
```

- **Trust Zone**: text only، max-width 400px، vertical-align center
  - heading: text-2xl، uses `public.home.trustZoneTitle`
  - text: text-base، color slate-400، max 2 lines، uses `public.home.trustZoneText`
- **CTA Zone**: vertical-align center
   - heading: text-4xl، uses `public.home.trustedTitle`
  - description: text-base، color slate-300، uses `public.home.trustedDescription`
  - CTA button: height 48px، px-8، uses `public.home.trustedCta`
- **gap بين القسمين**: 48px
- **No vertical divider. Spacing only.**
- **القاعدة:** Trust Zone و CTA Zone محتوى مختلف ومفاتيح ترجمة مختلفة. لا تكرار.

#### 7.9 Footer

التكوين:

```
+------------------------------------------+
|  [Logo + Brand]  [Links Col 1] [Col 2] [Contact + Social]
+------------------------------------------+
|  Copyright                                |
+------------------------------------------+
```

- **4 columns على desktop**:
  1. Logo + Brand + Tagline (width ~25%)
  2. Quick Links (width ~20%)
  3. Services (width ~25%)
   4. Contact + Social (width ~30%)
- **2 columns على tablet**: (Logo+Links) | (Services+Contact+Social)
- **1 column على mobile**: كل العناصر stacked
- **gap بين الأعمدة**: 48px desktop، 32px tablet، 24px mobile
- **padding vertical**: py-16 desktop، py-12 tablet، py-10 mobile
- **border top**: border-t border-white/10
- **Copyright**: mt-8، text-center، text-sm، color slate-500

---

### 8. Responsive Design Contract

الموقع يعمل احترافيًا على 7 breakpoints:

| Breakpoint | اسم | عرض الشاشة | container behavior |
|-----------|------|-----------|------------------|
| 1 | Large desktop | ≥1536px | 1280px centered، full composition |
| 2 | Standard desktop | 1280px - 1535px | 1280px centered، full composition |
| 3 | Laptop | 1024px - 1279px | 960px centered، full composition |
| 4 | Tablet landscape | 768px - 1023px | 720px centered، adapted columns |
| 5 | Tablet portrait | 480px - 767px | 100% padding px-6، stacked |
| 6 | Large mobile | 375px - 479px | 100% padding px-5، stacked |
| 7 | Standard mobile | 320px - 374px | 100% padding px-4، stacked |

**لكل breakpoint:**

**Container behavior:**
- Desktop (1-3): max-width 1280px / 960px، mx-auto، px-6
- Tablet landscape (4): max-width 720px، mx-auto، px-6
- Mobile (5-7): max-width 100%، px-6/5/4، no horizontal scroll

**Column changes:**
- Desktop: جميع الأقسام تستخدم column ratios المحددة
- Laptop (3): نفس composition، content width يقل قليلاً
 - Tablet landscape (4): 2 columns بدل 3 في Products، 5-step horizontal connected timeline واحدة أيضًا
- Mobile (5-7): كل الأقسام تصبح 1 column

**Stacking order:**
- Desktop: text/image أو image/text حسب القسم
- Mobile: image دائماً فوق النص في Our Company و Products و Digital Platform و Global Markets

**Image scaling:**
- Desktop: width 100% من العمود، aspect-ratio محفوظ
- Tablet: width 100%، aspect-ratio محفوظ، max-height يقل
- Mobile: width 100%، aspect-ratio محفوظ، object-fit cover

**Typography scaling:**
- Desktop: sizes المحددة في القسم 5
- Tablet: heading يقل 4px (text-3xl بدل text-4xl)
- Mobile: heading يقل 8px (text-2xl بدل text-4xl)
- Body: يبقى text-base على جميع breakpoints

**Spacing scaling:**
- Desktop: py-20
- Tablet: py-14
- Mobile: py-10

**CTA wrapping:**
- Desktop: 2 CTA في سطر واحد
 - Tablet: 2 CTA في صف واحد بدون wrap
- Mobile: CTA stacked عمودياً

**Timeline transformation (Export Journey):**
- Desktop: 5 steps horizontal
 - Tablet: 5-step horizontal connected timeline واحدة أيضًا، مع تقليل المسافات الداخلية فقط
- Mobile: 5 steps vertical (vertical timeline)

**Dashboard scaling (Digital Platform):**
- Desktop: height 500px
- Tablet: height 400px
 - Mobile: height 350px، dashboard أولاً ثم Text / Features

**Global Markets visualization scaling:**
- Desktop: aspect-ratio 16/9، height ~400px
- Tablet: aspect-ratio 16/9، height ~300px
- Mobile: aspect-ratio 16/9، height ~250px

**Navbar behavior:**
- Desktop: full nav visible
- Tablet: hamburger menu، auth CTA يختفي
- Mobile: hamburger menu + Create Account فقط

**Mobile menu:**
- Opens below navbar
- Full width
- All nav links vertical
- Language switcher visible
- Sign In + Create Account visible
- Closes on outside click أو link click

**الممنوع:**
- shrink غير مقصود يجعل العناصر تبدو كthumbnails
- horizontal overflow على أي breakpoint
- text scaling يجعل النص غير مقروء
- image cropping يخفي محتوى الصورة

---

### 9. Browser / Rendering Stability

**CSS/Tailwind deterministic layout:**
- استخدم flexbox و grid بكل ثبات
- لا تعتمد على floats
- لا تعتمد على table layout
- لا تعتمد على inline-block للـ layout الرئيسي

**Browser-specific rendering:**
- لا تستخدم `-webkit-*` prefixes إلا إذا كانت ضرورية
- لا تعتمد على browser-specific font rendering
- لا تستخدم CSS filters complex قد تختلف بين Chrome و Edge

**Positioning:**
- لا تستخدم `position: absolute` للعناصر الرئيسية
- exceptions: أيقونات داخل العقد (nodes) في Export Journey، أو decorative elements
- لا تستخدم `position: fixed` إلا لـ Navbar فقط

**Overflow prevention:**
- جميع الصور: `max-width: 100%`، `object-fit: cover`
- جميع containers: `overflow-x: hidden`
- لا تستخدم widths أكبر من container

**Font behavior:**
- لا تعتمد على font smoothing differences بين browsers
- لا تستخدم `font-display: swap` بدون fallback font
- استخدم system fonts stack كـ fallback

**Aspect ratios:**
- جميع الصور تستخدم `aspect-ratio` CSS property
- لا تستخدم padding-bottom hack
- لا تعتمد على image intrinsic dimensions

**Testing requirement:**
- اختبر على Chrome (أحدث إصدار مستقر)
- اختبر على Edge (Chromium-based)
- اختبر على أحجام الشاشات المحددة في القسم 8
- اختبر RTL/LTR

---

### 10. Content Lock

**ممنوع اختراع:**

| النوع | الحالة |
|--------|--------|
| أرقام (إلا 50+ / 200+ / 100%) | ممنوع |
| عملاء | ممنوع |
| شركاء | ممنوع |
| شهادات | ممنوع |
| إحصائيات (إلا 3 المعتمدة) | ممنوع |
| Dashboard metrics | ممنوع |
| Market claims | ممنوع |
| Country counts | ممنوع |
| Performance figures | ممنوع |

**الإحصائيات المعتمدة حاليًا فقط:**
- `50+`
- `200+`
- `100%`

ولا يجوز إضافة أرقام أخرى.

**المحتوى المسموح:**
- النصوص الموجودة فعلياً في `PublicLanding.tsx` الحالي
- الأسماء العامة للمنتجات (Vegetables, Fruits, National Factory Products)
- أسماء الخدمات الموجودة في الملفات الحالية
 - الخطوات الـ 5 في Home Export Journey (المحددة في القسم 7.5). ملاحظة: PublicMarkets تحتوي على 6 مراحل بما في ذلك Global Markets.

---

### 11. Runtime Restrictions

**Contract صريح:**

ممنوع استخدام العناصر التالية في Runtime (الكود المُنشأ):

1. `concept1.png`
2. `nile-key-global-export-platform-en.jpg`
3. `nile-key-export-platform-homepage-ar.jpg`
4. أي ملف اسمه `ReferenceVisual` أو `reference-visual`
5. أي crop أو extract من Concept 1
6. أي صورة من مجلد `concept/` أو `reference/` في المشروع

**Concept 1 = المرجع البصري فقط:**
- يُستخدم لفهم التكوين البصري
- يُستخدم لتحديد نسب الأعمدة
- يُستخدم لتحديد الألوان
- لا يُستخدم كـ Runtime Asset

**الأصول المسموحة فقط:**
- الأصول المحددة في القسم 4 (`hero-export.jpg`, `about-egypt.jpg`, `vegetables.jpg`, `fruits.jpg`, `factory.jpg`, `services-bg.jpg`)
- Compositions مبنية بـ CSS/HTML/SVG (Dashboard UI, World Visual)

---

### 12. Implementation Must Not Interpret the Design

**قواعد صريحة تمنع Kilo في مرحلة Code من:**

| # | الممنوع | السبب |
|---|---------|-------|
| 1 | تغيير Layout | التكوين محدد بدقة في هذه الخطة |
| 2 | استبدال عنصر بصري بعنصر آخر | كل عنصر له role محدد |
| 3 | تحويل visual composition إلى Cards | Concept 1 لا يستخدم cards لكل شيء |
| 4 | تقليل حجم العناصر الرئيسية بشكل مفرط | Hero ليس thumbnail |
| 5 | إنشاء فراغات ضخمة بلا سبب بصري | المساحة السلبية محددة |
| 6 | استخدام صور عامة كبدائل | يجب استخدام أصول محددة المصدر |
| 7 | استخدام decorative SVG بدل visual concept المطلوب | World Visual يجب أن يحقق معنى الانتشار العالمي |
| 8 | حذف عنصر بحجة التبسيط | كل قسم من Concept 1 مطلوب |
| 9 | إضافة قسم جديد | التكوين محدد: 9 أقسام فقط |
| 10 | إعادة ترتيب الأقسام | الترتيب محدد في القسم 1 |
| 11 | تغيير المحتوى | المحتوى محدد في القسم 5 (i18n) |

**القاعدة الذهبية:**
إذا كان شيء غير محدد داخل الخطة → لا يتم اختراعه عشوائيًا. يُعالج داخل الخطة أولًا، ثم يُنفَّذ.

**Kilo في مرحلة Code:**
- يقرأ هذه الخطة كمرجع حاكم
- ينفذ كما هو مكتوب
- لا يضيف اجتهادات خاصة
- لا يغير التكوين البصري

---

### 13. Section-by-Section Blueprint

#### 13.1 Navbar

- **exact horizontal composition**: Logo (120px) → Navigation (flex, 6 روابط) → Language (80px) → Auth CTA (200px)
- **logo zone**: حرف "NK" في دائرة خضراء (emerald-500) + نص "Nile Key" أبيض
- **navigation zone**: 6 روابط نصية، color white، hover: text-emerald-400
- **language zone**: زر EN / AR، border border-white/20، rounded-full، px-3
- **auth CTA zone**: Sign In (outline، border-white) + Create Account (filled، bg-emerald-600)
- **spacing**: 32px بين كل zone
- **desktop**: full nav visible
- **tablet/mobile**: hamburger menu (3 lines icon)، nav collapses

#### 13.2 Hero

- **45/55 approximate desktop composition**: text/image
- **text zone**: vertical-align center، max-width 480px
  - Eyebrow: "From Egyptian Fields..." text-emerald-400، uppercase، letter-spacing 0.1em
  - Heading: "Nile Key for Investment..." text-4xl، weight 700، text-white
  - Description: text-base، color slate-300، line-height 1.6
   - 2 CTA buttons: Sign In (primary)، Create Account (outline)
- **image zone**: vertical-align center، full height
  - Hero image: aspect-ratio 3/2، object-fit cover، rounded-2xl
  - prominence: full height of hero section، لا تقل عن 400px height
- **vertical center**: كل من text و image محاذيان عمودياً في منتصف الـ 90vh
- **hierarchy**: Image > Heading > Description > CTA
 - **CTA behavior**: 2 buttons inline على desktop، stacked على mobile
- **responsive behavior**: يتحول إلى column على mobile، image فوق النص

#### 13.3 Our Company

- **light surface**: `#f8fafc`
- **55/45 approximate composition**: text/image
- **text block**: max-width 520px، vertical-align center
   - Heading: "We are Your Strategic Partner..." text-4xl، weight 700
  - 3 paragraphs من PublicLanding.tsx
  - CTA: "Learn More" → /about
- **image block**: aspect-ratio 4/3، object-fit cover، rounded-2xl
  - about-egypt.jpg
- **spacing**: 48px بين text و image
- **hierarchy**: Heading > Paragraphs > CTA
- **responsive behavior**: image فوق النص على mobile، column واحد

#### 13.4 Premium Egyptian Products

- **dark surface**: `#002f32`
- **heading zone**: "Premium Egyptian Products" text-4xl، center، mb-12
- **3 equal cards**: width متساوية، gap 24px
  - Card 1: Vegetables (vegetables.jpg)
  - Card 2: Fruits (fruits.jpg)
  - Card 3: National Factory Products (factory.jpg)
- **image dominance**: كل card صورة تأخذ ~60% من ارتفاع Card
- **text area**: title + description، p-6
- **card spacing**: gap 24px بين cards
- **responsive behavior**: 3 cols → 2 cols (tablet) → 1 col (mobile)

#### 13.5 The Export Journey

- **light surface**: `#f8fafc`
- **5-step connected horizontal timeline**: 5 nodes متصلة بـ خط واحد
  - Step 1: Farm / Factory (Factory icon)
  - Step 2: Packing & Quality (CheckCircle icon)
  - Step 3: Export Documents (FileText icon)
  - Step 4: Shipping (Truck icon)
  - Step 5: Port & Delivery (Ship icon)
- **continuous connector**: خط أفقي، height 3px، bg-emerald-500
- **node size**: 48px diameter، bg-emerald-500، rounded-full
- **step spacing**: 32px على desktop
- **text hierarchy**: icon (48px) → title (text-sm، weight 600) → description (text-xs، color slate-400)
- **mobile vertical transformation**: vertical timeline، nodes stacked على اليسار، connector عمودي

#### 13.6 Digital Platform

- **dark surface**: `#002f32`
- **45/55 approximate composition**: text/dashboard
- **dashboard visual zone**: aspect-ratio 16/10، height ~500px
  - Composition UI (شكل فقط):
    - Frame: `#00383b`، rounded-2xl، border border-white/10
    - Header: 40px height، 3 nav cues
    - 3 Panels + Chart placeholder
    - No data inside
 - **text/features zone**: max-width 480px
   - Heading: "Our Integrated Digital Platform..."
   - Description: text-base، color slate-300
   - 4 Features: icon + title + description. Translation keys: `landing.features.shipments.title`, `landing.features.shipments.description`, `landing.features.invoicing.title`, `landing.features.invoicing.description`, `landing.features.customs.title`, `landing.features.customs.description`, `landing.features.intelligence.title`, `landing.features.intelligence.description`
 - **CTA**: "Get Started" → /services
- **responsive scaling**: dashboard height ~350px على mobile، dashboard أولاً ثم Text / Features

#### 13.7 Global Markets

- **light surface**: `#f8fafc`
- **text/visual split**: 40/60
- **strong world/global visual**: Stylized World Map + Connected Market Nodes فقط. لا خيار آخر.
  - Aspect ratio 16/9
  - world-map silhouette واضحة + 6-8 market nodes + thin connecting lines + subtle glow على nodes
  - Background: transparent
  - emerald-500 color
  - No text inside visual
- **integrated statistics**: 3 statistics (50+, 200+, 100%) في Text Zone. Labels use translation keys: `public.markets.statCountries`, `public.markets.statPartners`, `public.markets.statQuality`
  - Layout: horizontal، gap 24px
  - Each: number (text-3xl، weight 700، emerald-500) + label (text-sm، color slate-400)
- **responsive behavior**: stacked على mobile، visual فوق النص

#### 13.8 Trusted Partners / CTA

- **two-part composition**: 50/50
- **dark surface**: `#002f32`
 - **trust zone**: uses `public.home.trustZoneTitle` + `public.home.trustZoneText`، max-width 400px
  - heading: text-2xl
  - text: max 2 lines، color slate-400
 - **CTA zone**: heading (`public.home.trustedTitle`) + description (`public.home.trustedDescription`) + CTA button (`public.home.trustedCta`)
  - CTA button: height 48px، px-8، bg-emerald-600
- **visual balance**: both zones vertically centered
- **responsive stacking**: trust فوق CTA على mobile

#### 13.9 Footer

- **dark surface**: `#001a1c`
- **4 columns على desktop**:
  1. Logo + Brand + Tagline (~25%)
  2. Quick Links (~20%): Home, About, Products, Services, Markets, Contact
   3. Services (~25%): 4 خدمات
   4. Contact + Social (~30%): Location (Egypt), Email, Phone, Social icons
- **social**: icons صغيرة داخل عمود Contact
- **responsive behavior**: 2 cols (tablet)، 1 col (mobile)
- **border top**: border-t border-white/10
- **copyright**: "© 2026 Nile Key for Investment & International Trade. All rights reserved."

---

### 14. Visual Acceptance Contract

يعتبر التصميم PASS فقط إذا تم التحقق من جميع الشروط التالية:

1. ✅ الترتيب مطابق: Navbar → Hero → Our Company → Premium Egyptian Products → The Export Journey → Digital Platform → Global Markets → Trusted Partners / CTA → Footer
2. ✅ نسب الأعمدة مطابقة للمواصفة: 45/55 Hero، 55/45 Our Company، 3 equal cards Products، 40/60 Global Markets
3. ✅ أحجام العناصر الرئيسية مناسبة: Hero ليس thumbnail، Dashboard محترم، World Visual واضح
4. ✅ Hero ليس thumbnail: ارتفاع Hero على الأقل 90vh، الصورة تأخذ 55% من العرض
5. ✅ Our Company ليس dark: `#f8fafc` light surface
6. ✅ Products ثلاث Cards متساوية: width متساوية، gap متساوي، height متساوٍ
7. ✅ Journey مسار واحد متصل: خط أفقي/عمودي واحد، 5 nodes متصلة، ليست cards مستقلة
8. ✅ Digital Platform يحتوي UI حقيقي غير ادعائي: frame + header + panels + chart placeholder بدون بيانات
9. ✅ Global Markets يحتوي visual عالمي واضح: Stylized World Map + Connected Market Nodes، لا div فارغ
10. ✅ الإحصائيات الثلاث فقط هي الموجودة: 50+ / 200+ / 100%
11. ✅ لا توجد عناصر بصرية فارغة: كل عنصر له purpose محدد
12. ✅ لا توجد Concept images في Runtime: لا concept1.png ولا ReferenceVisual
13. ✅ لا توجد بيانات وهمية: Dashboard بدون metrics، لا fake counts
14. ✅ الصفحة تعمل على Desktop/Laptop/Tablet/Mobile: جميع breakpoints تعمل
15. ✅ RTL/LTR يعملان: الاتجاه يتغير، النصوص تتغير، التخطيط يحترم الاتجاه
16. ✅ لا توجد تغييرات خارج Public Website: Backend, DEM, Customers unchanged
17. ✅ Build ينجح: لا أخطاء في compilation
18. ✅ The implementation must reproduce the approved Concept 1 composition, visual hierarchy, proportions, spacing, asset placement and section transitions without interpretation or substitution.
19. ✅ لا أقسام إضافية
20. ✅ لا مسافات خارجية وهمية
21. ✅ لا خيارات تصميم بديلة
22. ✅ لا Assets غير مصرح بها
23. ✅ لا بيانات وهمية
24. ✅ لا visual placeholders فارغة
25. ✅ لا thumbnail treatment
26. ✅ لا layout reinterpretation

---

### 15. Visual QA Protocol

آلية تحقق بصرية بعد مرحلة Code:

**الأحجام المطلوبة للاختبار:**

| Device | Breakpoint | ما يتم فحصه |
|--------|-----------|-------------|
| Desktop wide | ≥1536px | composition، spacing، hierarchy، image prominence |
| Desktop standard | 1280px | composition، spacing، hierarchy |
| Laptop | 1024px | column changes، image scaling |
| Tablet landscape | 768px | stacking، timeline transformation، navbar behavior |
| Tablet portrait | 480px | stacking، typography scaling، CTA behavior |
| Mobile | 375px | full stacking، CTA wrapping، typography scaling، no overflow |
| Standard mobile | 320px | full stacking، CTA wrapping، typography scaling، no overflow |

**قائمة الفحص لكل device:**

- [ ] **Composition**: ترتيب الأقسام مطابق
- [ ] **Spacing**: المسافات بين الأقسام مباشرة (لا gaps خارجية)
- [ ] **Hierarchy**: العناصر تلفت النظر بالترتيب المحدد
- [ ] **Image prominence**: Hero ليس thumbnail، الصور الرئيسية واضحة
- [ ] **Section transitions**: الانتقال بين dark/light واضح
- [ ] **Alignment**: كل العناصر محاذية بشكل صحيح
- [ ] **Overflow**: لا يوجد horizontal scroll على أي breakpoint
- [ ] **Typography**: النصوص مقروءة على جميع breakpoints
- [ ] **RTL/LTR**: كلا الاتجاهين يعملان بشكل صحيح

**المعاينة البصرية هي الحكم النهائي، وليس عبارة "Build passed".**

**Build passed ≠ Visual QA passed.**

يجب فحص كل نقطة في هذه القائمة بصرياً قبل اعتماد التصميم.

---

### القاعدة النهائية — Single Source of Truth

بعد هذه التعديلات، هذه الخطة تصبح **المرجع الحاكم الوحيد** لتنفيذ الواجهة العامة (Public Website).

ولا يجوز في مرحلة Code:
- إعادة تفسير التصميم
- تعديل النسب
- اختيار بديل بصري
- إضافة عنصر
- حذف عنصر
- تغيير ترتيب
- تغيير Palette
- تغيير Asset
- اختراع محتوى
- اختراع بيانات
- استخدام OR / خيارين بديلين
- استخدام "يمكن" / "حسب الحاجة" / "أو" / "يفضل"
- إنشاء عنصر غير محدد في الخطة

إذا كان شيء غير محدد داخل الخطة → لا يتم اختراعه عشوائيًا. يُعالج داخل الخطة أولاً، ثم يُنفَّذ.

هذه الخطة = Concept 1 → Visual Execution Specification → Code Implementation.

ولا يجوز اختصار المعادلة إلى: Concept 1 → وصف عام → اجتهاد في التنفيذ.
