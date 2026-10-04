# خطة تنفيذ الواجهة العامة لموقع Nile Key

## 1. الصفحات والمسارات العامة المطلوبة

### الصفحات الجديدة (Public Website Pages)

| المسار | المكون | الوصف |
|--------|---------|-------|
| `/` | `PublicHome` (معدّل من `PublicLanding`) | الصفحة الرئيسية - تعرض هوية الشركة والـ Hero و CTA |
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

/                                              → PublicHome (معدّل من PublicLanding، public)
/*                                            → Redirect to / (موجود)
```

### ملاحظة على `PublicLanding` الحالي
- الملف `PublicLanding.tsx` يُعدَّل مباشرة ليكون `PublicHome`. لا حاجة لإعادة تسمية أو إنشاء ملف جديد ما لم يكن التعديل جوهريًا بحيث يستدعي فصلًا.
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

**المصدر:** القسم الرئيسي من التصميم المرجعي - العمود الأيمن

**الأقسام والتفاصيل البصرية:**
1. **شريط علوي (Navbar)** - شعار `NK`، اسم `Nile Key`، `Digital Export Platform`، أزرار اللغة، Login، Create Account. الشريط أفقي فاخر ومتسق مع التصميم المرجعي.
2. **Hero Section** - هوية الشركة (الاسم بالعربية والإنجليزية)، الرسالة الرئيسية، صورة Hero قوية مرتبطة بمصر والمنتج الزراعي والتصدير والأسواق العالمية، أزرار CTA (Sign In / Create Account / Explore Products). الخلفية: تدرج داكن (`from-slate-900 via-slate-800 to-emerald-900`).
3. **Short Intro Navigation** - ملخص بصري قصير يقود إلى بقية الصفحات (About, Products, Services) بأزرار أو روابط بصرية.
4. **Company Summary** - فقرتان عن هوية الشركة وهدف التأسيس. النص مستمد من `PublicLanding.tsx` الحالي (الفقرات عن الشركة المصرية وهدف التأسيس).
5. **Platform Overview** - منظومتنا الرقمية. النص مستمد من `PublicLanding.tsx` الحالي (قسم المنصة الرقمية).
6. **Strategic Partner CTA** - "نحن شريكك الاستراتيجي في التجارة العالمية". النص مستمد من `PublicLanding.tsx` الحالي.

### 3.2 PublicAbout

**المصدر:** قسم "من نحن" من التصميم المرجعي

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "About Us" / "من نحن"
2. **من نحن** - الشركة المصرية، طبيعة النشاط، هدف التأسيس. النص مستمد من `PublicLanding.tsx` الحالي (فقرات هوية الشركة).
3. **الرؤية والرسالة** - صورة/مشهد مصري مناسب + نص الرسالة المؤسسية. الصورة: أصل بصري محدد المصدر (انظر القسم 4).
4. **الموقع كشريك تجاري دولي** - صياغة تجارية راقية بدون أرقام وهمية. النص مستمد من `PublicLanding.tsx` الحالي (قسم الشريك الاستراتيجي).
5. **لمحة سريعة** - بطاقات أو أقسام صغيرة تعرض: اسم الشركة بالعربية والإنجليزية، الرخصة (الهيئة العامة للاستثمار والمناطق الحرة)، هدف التأسيس.

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
4. **CTA** - زر "Contact Us for Catalog" أو "Explore Products" يقود إلى `/contact`.

**الملاحظة:** لا تخترع أسماء منتجات أو شهادات أو مواصفات تجارية. استخدم الأسماء العامة فقط. الصور: أصول محددة المصدر (انظر القسم 4).

### 3.4 PublicServices

**المصدر:** قسم الخدمات في التصميم المرجعي

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "Services" / "الخدمات"
2. **شبكة الخدمات** - عرض بصري لسبع خدمات:
   - إدارة عمليات التصدير
   - الخدمات التجارية
   - المنصة الرقمية
   - إدارة الشحنات
   - الفواتير والمستندات
   - الإجراءات الجمركية
   - الربط بين الموردين والعملاء والجهات اللوجستية
   كل خدمة: أيقونة (`lucide-react`) + عنوان + وصف قصير. البطاقات بتصميم موحد.
3. **Why Choose Nile Key** - قسم بصري يعرض لماذا نختار Nile Key كشريك. أسلوب بصري مشابه للمرجع: بطاقات أو قائمة punti forza.
4. **CTA** - زر "Get Started" أو "Contact Us" يقود إلى `/contact`.

### 3.5 PublicMarkets

**المصدر:** فكرة "From Egyptian Fields and Factories to Global Markets" من التصميم المرجعي

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "Markets" / "الأسواق العالمية"
2. **رحلة التصدير بصريًا** - مسار خطوات متتالية بتصميم بصري واضح:
   - Farm / Factory (المزرعة/المصنع)
   - Packing & Quality (التغليف والجودة)
   - Export Documents (مستندات التصدير)
   - Shipping (الشحن)
   - Port & Delivery (الميناء والتسليم)
   - Global Markets (الأسواق العالمية)
   كل خطوة: أيقونة + عنوان + وصف قصير. التصميم: مسار خطي أو شبكي يربط الخطوات.
3. **CTA** - زر "Start Your Export Journey" أو "Contact Us" يقود إلى `/contact`.

### 3.6 PublicContact

**المصدر:** التصميم المرجعي

**الأقسام والتفاصيل البصرية:**
1. **عنوان الصفحة** - "Contact" / "اتصل بنا"
2. **وسائل الاتصال** - الموقع، البريد/الهاتف (البيانات الموجودة فعلياً في المشروع فقط). لا تخترع عناوين أو أرقام هواتف.
3. **نموذج اتصال كامل** - واجهة نموذج اتصال مع:
   - حقول: الاسم، البريد الإلكتروني، الموضوع، الرسالة
   - التحقق من المدخلات (client-side validation)
   - حالات الإرسال: idle, submitting, success, error
   - الربط بالـbackend: يُرسل إلى endpoint الاتصالات الحالي في المشروع. إذا لم يوجد endpoint مناسب، يُنفَّذ أقل تنفيذ backend لازم داخل البنية الحالية فقط، دون إنشاء نظام أو معمارية جديدة.
4. **CTA تجاري واضح** - "Get in Touch" أو "Send Message"
5. **Footer احترافي** - متسق مع باقي الصفحات.

---

## 4. استراتيجية الصور والأصول البصرية

### 4.1 مصادر الصور (إلزامية من البداية - لا MVP بدون صور)

**القاعدة:** الصور جزء أساسي من تنفيذ التصميم المرجعي من البداية. لا تأجيل.

### 4.2 مصادر الأصول المحددة

| الأصل | المسار في المشروع | المصدر | الاستخدام |
|-------|------------------|--------|-----------|
| Hero Image (PublicHome) | `frontend/public/assets/hero-export.jpg` | أصل بصري من مكتبة الشركة - صورة مرتبطة بمصر والمنتج الزراعي والتصدير والأسواق العالمية | Hero Section في PublicHome |
| About Image (PublicAbout) | `frontend/public/assets/about-egypt.jpg` | أصل بصري من مكتبة الشركة - صورة/مشهد مصري مناسب | قسم الرؤية والرسالة في PublicAbout |
| Product Images (3) | `frontend/public/assets/products/vegetables.jpg`, `frontend/public/assets/products/fruits.jpg`, `frontend/public/assets/products/factory.jpg` | أصول بصرية من مكتبة الشركة - صور منتجات | بطاقات المنتجات في PublicProducts |
| Services Background | `frontend/public/assets/services-bg.jpg` | أصل بصري من مكتبة الشركة - خلفية قسم الخدمات | خلفية قسم Why Choose Nile Key |

**ملاحظة:** إذا لم تكن الأصول متوفرة بعد في `frontend/public/assets/`، يجب أن يوفرها صاحب المشروع. لا يُسمح بـ placeholders نهائية أو اختراع صور.

### 4.3 الأيقونات
- استخدم `lucide-react` (موجود في المشروع بالفعل)
- الأيقونات المقترحة:
  - `Globe` - للأسواق العالمية
  - `Truck` - للشحن
  - `Package` - للمنتجات
  - `FileText` - للمستندات
  - `Ship` - للشحن البحري
  - `CheckCircle` - للجودة
  - `Factory` - للمصنع
  - `Warehouse` - للتغليف والتخزين
  - `Ship` / `Anchor` - للميناء

### 4.4 مسارات الأصول
- جميع الصور توضع في: `frontend/public/assets/` ومجلداته الفرعية
- الاستيراد: `import heroImage from '@/assets/hero-export.jpg'` أو استخدام `<img src="/assets/hero-export.jpg" />`

---

## 5. دعم الإنجليزية أولًا والعربية ثانيًا

### 5.1 بنية الترجمة الحالية
- **الملفات:** `en/translation.json` و `ar/translation.json`
- **المكتبة:** i18next + react-i18next
- **الكشف التلقائي الحالي:** localStorage ثم navigator
- **الاتجاه:** `dir="rtl"` للعربية، `dir="ltr"` للإنجليزية

### 5.2 تعديل سلوك اللغة الافتراضية

**المشكلة الحالية:** `i18next-browser-languagedetector` قد يفرض لغة من `navigator` عند أول زيارة، مما قد يجعل الموقع يبدأ بلغة غير الإنجليزية.

**الحل:** تعديل `frontend/src/lib/i18n.ts` لضمان:
1. **اللغة الافتراضية عند عدم وجود تفضيل محفوظ:** الإنجليزية (`en`)
2. **إذا كان هناك لغة محفوظة في `localStorage`:** استخدمها
3. **لا تعتمد على `navigator.language`** لفرض لغة البداية على الموقع العام

**التنفيذ المقترح في `i18n.ts`:**
```typescript
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { ... },
    fallbackLng: 'en', // تغيير من 'ar' إلى 'en'
    detection: {
      order: ['localStorage'], // إزالة 'navigator' من الترتيب الأول
      caches: ['localStorage'],
    },
    ...
  });
```

**ملاحظة:** إذا كان هناك حاجة للحفاظ على `navigator` كخيار ثانوي، يُستخدم فقط إذا لم يوجد `localStorage` وكان المستخدم قد اختار لغة سابقًا في جلسة سابقة. لكن الشرط الأساسي: عند عدم وجود تفضيل محفوظ، تبدأ بالإنجليزية.

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
    "ctaExploreProducts": "Explore Products",
    "companySummaryTitle": "We are Your Strategic Partner in Global Trade",
    "companySummaryP1": "Nile Key for Investment and International Trade LLC is an Egyptian limited liability company, licensed by the General Authority for Investment and Free Zones.",
    "companySummaryP2": "The purpose of establishment is to showcase the quality of Egyptian products — vegetables, fruits, and national factory products — in global markets.",
    "companySummaryP3": "We focus on marketing and exporting carefully selected Egyptian products, and connecting Egyptian suppliers and producers to clients, importers and international partners, through an integrated system combining commercial expertise, export process management, and modern digital solutions.",
    "platformTitle": "Our Integrated Digital Platform for Managing Egyptian Export Operations",
    "platformP1": "We have developed the Nile Key system to be an integrated digital environment for managing and monitoring trade and export operations — from the product and supplier, through the client, invoice, documents and shipment, and all the way to the port and global markets.",
    "platformP2": "We aim to make export operations more organized, clear, efficient and reliable, by facilitating coordination among all relevant parties and supporting commercial, logistical and customs procedures within a single digital system."
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
    "whyChooseP3": "Egyptian company with deep understanding of local products and global market requirements."
  },
  "markets": {
    "title": "Markets",
    "subtitle": "From Egyptian Fields and Factories to Global Markets",
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
    "step6Desc": "Reaching customers and markets worldwide with Egyptian quality products.",
    "ctaJourney": "Start Your Export Journey"
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
    "ctaExploreProducts": "استكشف المنتجات",
    "companySummaryTitle": "نحن شريكك الاستراتيجي في التجارة العالمية",
    "companySummaryP1": "شركة مفتاح النيل للاستثمار والتجارة الدولية هي شركة مصرية ذات مسؤولية محدودة، مرخصة من الهيئة العامة للاستثمار والمناطق الحرة.",
    "companySummaryP2": "هدف التأسيس هو إشهار جودة المنتج المصري من خضروات وفواكه ومنتجات المصانع الوطنية في الأسواق العالمية.",
    "companySummaryP3": "نركز على تسويق وتصدير المنتجات المصرية المختارة بعناية، وربط الموردين والمنتجين المصريين بالعملاء والمستوردين والشركاء الدوليين، من خلال منظومة متكاملة تجمع بين الخبرة التجارية وإدارة عمليات التصدير والحلول الرقمية الحديثة.",
    "platformTitle": "منصتنا الرقمية المتكاملة لإدارة عمليات التصدير المصرية",
    "platformP1": "طوّرنا منظومة Nile Key لتكون بيئة رقمية متكاملة لإدارة ومتابعة عمليات التجارة والتصدير، بدءًا من المنتج والمورد، مرورًا بالعميل والفاتورة والمستندات والشحن، ووصولًا إلى الميناء والأسواق العالمية.",
    "platformP2": "نهدف إلى جعل عمليات التصدير أكثر تنظيمًا ووضوحًا وكفاءة وموثوقية، مع تسهيل التنسيق بين مختلف الأطراف ذات الصلة، ودعم الإجراءات التجارية واللوجستية والجمركية ضمن منظومة رقمية واحدة."
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
    "whyChooseP3": "شركة مصرية ذات فهم عميق للمنتجات المحلية ومتطلبات الأسواق العالمية."
  },
  "markets": {
    "title": "الأسواق العالمية",
    "subtitle": "من المزارع والمصانع المصرية إلى الأسواق العالمية",
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
    "step6Desc": "الوصول إلى العملاء والأسواق في جميع أنحاء العالم بمنتجات مصرية عالية الجودة.",
    "ctaJourney": "ابدأ رحلة التصدير"
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
| `frontend/src/lib/i18n.ts` | تعديل `fallbackLng` إلى `'en'` وترتيب `detection.order` ليكون `['localStorage']` أولاً (أو إزالة `navigator` إذا لزم الأمر) |
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

**ملاحظة:** `PublicHome` يُنفَّذ بتعديل `PublicLanding.tsx` الحالي مباشرةً. لا حاجة لملف جديد ما لم يكن التعديل جوهريًا.

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
- **الخلفيات الداكنة:** `bg-slate-900`, `bg-slate-800`
- **التدرجات:** `bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900`
- **الأخضر الزمردي:** `emerald-500`, `emerald-600`, `emerald-700`
- **النصوص:** `text-white`, `text-slate-300`, `text-slate-400`
- **البطاقات:** `bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10`

### 8.2 الأزرار
- **Primary:** `bg-emerald-600 hover:bg-emerald-700 text-white`
- **Outline:** `border-white text-black hover:bg-white/10 hover:text-emerald-500`
- **Ghost:** `text-white hover:text-emerald-400`

### 8.3 المسافات والأحجام
- **Hero padding:** `py-20`
- **Section spacing:** `mb-16`, `gap-6`
- **Card padding:** `p-6`
- **Border radius:** `rounded-2xl`, `rounded-xl`

### 8.4 التصميم المتجاوب
- **Desktop:** `≥1024px` - عرض كامل
- **Tablet:** `768px - 1023px` - شبكة تكيفية
- **Mobile:** `<768px` - عمود واحد، قائمة hamburger

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
3. يُستورد أو يُستخدم `<img src="/assets/hero-export.jpg" />` في المكونات

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
- يُرسل النموذج إلى endpoint الاتصالات الحالي في المشروع
- إذا لم يوجد endpoint مناسب، يُنفَّذ أقل تنفيذ backend لازم داخل البنية الحالية فقط
- لا إنشاء نظام أو معمارية جديدة

### 10.5 معالجة الأخطاء
- عرض رسائل خطأ واضحة للمستخدم
- إمكانية إعادة المحاولة
- في حالة فشل الإرسال، عرض وسائل اتصال بديلة (إن وجدت)

---

## 11. معايير القبول البصرية والوظيفية

### 11.1 معايير القبول البصرية
1. **الخلفيات:** داكنة (`slate-900`, `slate-800`) مع تدرجات للأخضر الزمردي
2. **الألوان:** الأخضر الزمردي (`emerald-500`, `emerald-600`, `emerald-700`) كلون أساسي
3. **البطاقات:** `bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10`
4. **الأزرار:** `bg-emerald-600 hover:bg-emerald-700 text-white`
5. **الخطوط:** واضحة، بسيطة، مؤسسية راقية
6. **المساحات:** generous spacing (py-20, mb-16, gap-6)
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
- إذا كان التعديل جوهريًا بحيث يستدعي فصلًا، يُنشَأ `PublicHome.tsx` جديد ويُزال `PublicLanding.tsx`

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
