import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  Building2,
  FileText,
  Package,
  ShieldCheck,
  Ship,
  Sparkles,
  Truck,
} from 'lucide-react';
import { PublicNavbar } from '@/components/public/PublicNavbar';

const HERO_BG = '/assets/hero-export.jpg';

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-emerald-300">
      {children}
    </div>
  );
}

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const PRODUCTS = [
    {
      title: t('public.products.vegetablesTitle'),
      description: t('public.products.vegetablesDesc'),
      image: '/assets/products/vegetables.jpg',
    },
    {
      title: t('public.products.fruitsTitle'),
      description: t('public.products.fruitsDesc'),
      image: '/assets/products/fruits.jpg',
    },
    {
      title: t('public.products.factoryTitle'),
      description: t('public.products.factoryDesc'),
      image: '/assets/products/factory.jpg',
    },
  ];

  const journeySteps = [
    {
      icon: Building2,
      title: t('public.markets.step1Title'),
      description: t('public.markets.step1Desc'),
    },
    {
      icon: Package,
      title: t('public.markets.step2Title'),
      description: t('public.markets.step2Desc'),
    },
    {
      icon: FileText,
      title: t('public.markets.step3Title'),
      description: t('public.markets.step3Desc'),
    },
    {
      icon: Truck,
      title: t('public.markets.step4Title'),
      description: t('public.markets.step4Desc'),
    },
    {
      icon: Ship,
      title: t('public.markets.step5Title'),
      description: t('public.markets.step5Desc'),
    },
  ];

  const platformFeatures = [
    {
      icon: Truck,
      title: t('landing.features.shipments.title'),
      description: t('landing.features.shipments.description'),
    },
    {
      icon: FileText,
      title: t('landing.features.invoicing.title'),
      description: t('landing.features.invoicing.description'),
    },
    {
      icon: ShieldCheck,
      title: t('landing.features.customs.title'),
      description: t('landing.features.customs.description'),
    },
    {
      icon: Sparkles,
      title: t('landing.features.intelligence.title'),
      description: t('landing.features.intelligence.description'),
    },
  ];

  return (
    <div
      className="min-h-screen overflow-x-hidden bg-[#002f32] text-white"
      dir={isArabic ? 'rtl' : 'ltr'}
    >
      <PublicNavbar />

      <main>
        {/* Concept 1 — Hero */}
        <section className="border-b border-white/10 bg-[#002f32]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-10 sm:px-6 sm:py-14 lg:grid-cols-[1fr_1fr] lg:gap-10 lg:px-8 lg:py-20">
            <div>
              <SectionLabel>
                {isArabic ? 'منتجات مصرية • أسواق عالمية' : 'Egyptian Products • Global Markets'}
              </SectionLabel>
              <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                Nile Key
              </h1>
              <div className="mt-2 max-w-2xl text-base font-semibold leading-7 text-white sm:text-lg">
                {t('public.home.heroTitle')}
              </div>
              <p className="mt-4 max-w-xl text-sm leading-7 text-emerald-100 sm:text-base">
                {isArabic
                  ? 'إحضار المنتجات المصرية المتميزة إلى الأسواق العالمية من خلال حلول تجارية ورقمية موثوقة.'
                  : 'Bringing premium Egyptian products to global markets through trusted trade and digital solutions.'}
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link to="/products">
                  <Button size="lg" className="bg-emerald-400 px-6 font-semibold text-slate-950 hover:bg-emerald-300">
                    {t('public.cta.getStarted')}
                    <ArrowRight size={17} className="ms-2" />
                  </Button>
                </Link>
                <Link to="/about">
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-white/45 bg-transparent px-6 text-white hover:bg-white/10 hover:text-white"
                  >
                    {t('public.cta.learnMore')}
                    <ArrowRight size={17} className="ms-2" />
                  </Button>
                </Link>
              </div>
            </div>
            <div className="hidden lg:block">
              <img
                src={HERO_BG}
                alt={isArabic ? 'شحنات التصدير' : 'Export shipments'}
                className="h-[320px] w-full rounded-[1.8rem] border border-white/10 object-cover shadow-2xl"
              />
            </div>
          </div>
        </section>

        {/* Concept 1 — Our Company */}
        <section className="border-t border-white/10 bg-[#002f32]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-10 sm:px-6 sm:py-12 lg:grid-cols-[1fr_1fr] lg:gap-12 lg:px-8 lg:py-14">
            <div>
              <SectionLabel>
                {isArabic ? 'عن الشركة' : 'OUR COMPANY'}
              </SectionLabel>
              <h2 className="mt-2 text-3xl font-bold sm:text-4xl">
                {t('public.home.companySummaryTitle')}
              </h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-200">
                {t('public.home.companySummaryP1')}
              </p>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
                {t('public.home.companySummaryP2')}
              </p>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
                {t('public.home.companySummaryP3')}
              </p>
              <Link to="/about" className="mt-6 inline-flex">
                <Button
                  variant="outline"
                  className="border-emerald-300/50 bg-transparent text-emerald-200 hover:bg-emerald-300/10 hover:text-white"
                >
                  {t('public.cta.learnMore')}
                  <ArrowRight size={17} className="ms-2" />
                </Button>
              </Link>
            </div>
            <div className="hidden lg:block">
              <img
                src="/assets/about-egypt.jpg"
                alt={isArabic ? 'مصر' : 'Egypt'}
                className="h-[280px] w-full rounded-[1.5rem] border border-white/10 object-cover shadow-xl"
              />
            </div>
          </div>
        </section>

        {/* Concept 1 — Premium Egyptian Products */}
        <section className="border-t border-white/10 bg-[#00383b]">
          <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 sm:py-12 lg:px-8 lg:py-14">
            <div className="flex items-end justify-between gap-4">
              <div>
                <SectionLabel>
                  {isArabic ? 'المنتجات الرئيسية' : 'KEY PRODUCTS'}
                </SectionLabel>
                <h2 className="mt-2 text-3xl font-bold sm:text-4xl">
                  {isArabic ? 'منتجات مصرية مميزة' : 'Premium Egyptian Products'}
                </h2>
              </div>
              <Link
                to="/products"
                className="hidden items-center text-xs font-semibold text-emerald-300 hover:text-emerald-200 sm:inline-flex"
              >
                {isArabic ? 'عرض كل المنتجات' : 'View All Products'}
                <ArrowRight size={15} className="ms-2" />
              </Link>
            </div>

            <div className="mt-7 grid gap-4 md:grid-cols-3">
              {PRODUCTS.map((product) => (
                <Link key={product.title} to="/products" className="group">
                  <article className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] transition duration-200 group-hover:-translate-y-1 group-hover:border-emerald-300/30">
                    <div className="aspect-[1.43/1] overflow-hidden bg-[#053b3d]">
                      <img
                        src={product.image}
                        alt={product.title}
                        className="h-full w-full object-cover transition duration-200 group-hover:scale-105"
                      />
                    </div>
                    <div className="border-t border-white/10 bg-[#053b3d] p-4">
                      <h3 className="font-semibold text-white">{product.title}</h3>
                      <p className="mt-1 text-xs leading-5 text-slate-400">{product.description}</p>
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* Concept 1 — The Export Journey */}
        <section className="border-t border-white/10 bg-[#002f32]">
          <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 sm:py-12 lg:px-8 lg:py-14">
            <div className="mb-7">
              <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-emerald-300">
                {isArabic ? 'رحلة التصدير' : 'THE EXPORT JOURNEY'}
              </div>
              <h2 className="mt-2 text-3xl font-bold sm:text-4xl">
                {isArabic
                  ? 'من المزرعة أو المصنع إلى الأسواق العالمية'
                  : 'From farm or factory to global markets'}
              </h2>
              <p className="mt-2 text-sm text-slate-300">
                {isArabic ? 'بجودة موثوقة في كل خطوة.' : 'With quality at every step.'}
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              {journeySteps.map(({ icon: Icon, title, description }, index) => (
                <div key={title} className="relative">
                  <article className="h-full rounded-2xl border border-white/10 bg-white/[0.025] p-4 text-center">
                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-emerald-300/20 bg-emerald-300/10 text-emerald-300">
                      <Icon size={20} />
                    </div>
                    <div className="mt-3 text-[10px] font-bold text-emerald-300">0{index + 1}</div>
                    <h3 className="mt-1 text-sm font-semibold">{title}</h3>
                    <p className="mt-1 text-xs leading-5 text-slate-400">{description}</p>
                  </article>

                  {index < journeySteps.length - 1 && (
                    <div className="pointer-events-none absolute -end-3 top-1/2 hidden -translate-y-1/2 text-emerald-300 lg:block">
                      <ArrowRight size={15} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Concept 1 — Digital Platform */}
        <section className="border-t border-white/10 bg-[#00383b]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-10 sm:px-6 sm:py-12 lg:grid-cols-[1fr_1fr] lg:gap-12 lg:px-8 lg:py-14">
            <div className="hidden lg:block">
              <img
                src="/assets/services/services-bg.jpg"
                alt={isArabic ? 'المنصة الرقمية' : 'Digital platform'}
                className="h-[300px] w-full rounded-[1.5rem] border border-white/10 object-cover"
              />
            </div>
            <div>
              <SectionLabel>
                {isArabic ? 'المنصة الرقمية' : 'DIGITAL PLATFORM'}
              </SectionLabel>
              <h2 className="mt-2 text-3xl font-bold leading-tight sm:text-4xl">
                {t('public.home.platformTitle')}
              </h2>
              <p className="mt-4 text-sm leading-7 text-slate-200 sm:text-base">
                {t('public.home.platformP1')}
              </p>
              <p className="mt-3 text-sm leading-7 text-slate-300 sm:text-base">
                {t('public.home.platformP2')}
              </p>

              <div className="mt-6 grid gap-3 sm:grid-cols-2">
                {platformFeatures.map(({ icon: Icon, title, description }) => (
                  <div key={title} className="rounded-xl border border-white/10 bg-white/[0.025] p-3.5">
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 text-emerald-300">
                        <Icon size={17} />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold">{title}</h3>
                        <p className="mt-1 text-xs leading-5 text-slate-400">{description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <Link to="/services" className="mt-6 inline-flex">
                <Button className="bg-emerald-400 font-semibold text-slate-950 hover:bg-emerald-300">
                  {t('public.cta.learnMore')}
                  <ArrowRight size={17} className="ms-2" />
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Concept 1 — Global Markets */}
        <section className="relative overflow-hidden border-t border-white/10 bg-[#00383b]">
          <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 sm:py-12 lg:px-8 lg:py-14">
            <div className="grid items-center gap-8 lg:grid-cols-[1fr_1fr] lg:gap-12">
              <div>
                <SectionLabel>
                  {isArabic ? 'الأسواق العالمية' : 'OUR PRESENCE IN GLOBAL MARKETS'}
                </SectionLabel>
                <h2 className="mt-2 text-3xl font-bold sm:text-4xl">
                  {isArabic
                    ? 'حضورنا في الأسواق العالمية'
                    : 'Our Presence in Global Markets'}
                </h2>
                <p className="mt-3 max-w-xl text-sm leading-6 text-slate-300">
                  {isArabic ? 'منتجات مصرية بجودة موثوقة حول العالم.' : 'Egyptian products. Worldwide.'}
                </p>
              </div>
              <div className="hidden lg:block" aria-hidden="true" />
            </div>

            <div className="mt-8 grid grid-cols-3 border-t border-white/10">
              {[
                ['50+', isArabic ? 'دولة' : 'Countries'],
                ['200+', isArabic ? 'شريكًا تجاريًا' : 'Business Partners'],
                ['100%', isArabic ? 'التزام بالجودة' : 'Commitment to Quality'],
              ].map(([value, label]) => (
                <div key={label} className="border-e border-white/10 p-5 text-center last:border-e-0">
                  <div className="text-2xl font-bold sm:text-3xl">{value}</div>
                  <div className="mt-1 text-xs text-slate-400">{label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Concept 1 — Trusted Partners / CTA */}
        <section className="border-t border-slate-200/10 bg-slate-50">
          <div className="mx-auto grid max-w-7xl lg:grid-cols-2">
            <div className="p-7 sm:p-9 lg:p-10">
              <SectionLabel>
                {isArabic ? 'شركاء عالميون موثوقون' : 'TRUSTED GLOBAL PARTNERS'}
              </SectionLabel>
              <div className="mt-6 flex flex-wrap items-center gap-x-8 gap-y-4 text-sm font-bold text-slate-600">
                <span>SGS</span>
                <span>ISO</span>
                <span>HACCP</span>
                <span>GLOBALG.A.P.</span>
              </div>
            </div>

            <div className="relative min-h-[220px] overflow-hidden bg-[#0a2528]">
              <div className="absolute inset-0 bg-gradient-to-l from-[#002d31]/15 via-[#002d31]/45 to-[#071b1e]/70" />
              <div className="relative z-10 p-7 text-white sm:p-9 lg:p-10">
                <SectionLabel>
                  {isArabic ? 'شريكك في التصدير' : 'YOUR STRATEGIC PARTNER'}
                </SectionLabel>
                <h2 className="mt-3 text-2xl font-bold sm:text-3xl">
                  {isArabic ? 'لننطلق معًا نحو الأسواق العالمية' : "Let's Grow Together"}
                </h2>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-300">
                  {isArabic
                    ? 'شريكك في إدارة عمليات التصدير وربط المنتج المصري بالمشتري العالمي.'
                    : 'Partner with Nile Key for export management and global market access.'}
                </p>
                <Link to="/contact" className="mt-5 inline-flex">
                  <Button className="bg-emerald-400 font-semibold text-slate-950 hover:bg-emerald-300">
                    {t('public.cta.contactUs')}
                    <ArrowRight size={17} className="ms-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Concept 1 — Footer */}
        <footer className="border-t border-white/10 bg-[#002f32]">
          <div className="mx-auto grid max-w-7xl gap-8 px-4 py-9 sm:px-6 md:grid-cols-4 lg:px-8">
            <div className="md:col-span-1">
              <Link to="/" className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500 font-bold">
                  NK
                </div>
                <div>
                  <div className="font-bold leading-tight text-white">مفتاح النيل</div>
                  <div className="font-bold leading-tight text-white">Nile Key</div>
                  <div className="text-[10px] text-slate-400">Digital Export Platform</div>
                </div>
              </Link>
            </div>

            <div>
              <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
                {isArabic ? 'روابط سريعة' : 'Quick Links'}
              </h3>
              <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm text-slate-400">
                <Link to="/about" className="hover:text-white">{t('public.nav.about')}</Link>
                <Link to="/products" className="hover:text-white">{t('public.nav.products')}</Link>
                <Link to="/services" className="hover:text-white">{t('public.nav.services')}</Link>
                <Link to="/markets" className="hover:text-white">{t('public.nav.markets')}</Link>
              </div>
            </div>

            <div>
              <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
                {isArabic ? 'تواصل معنا' : 'Contact Us'}
              </h3>
              <div className="mt-3 space-y-2 text-sm text-slate-400">
                <div>info@nilekey.com</div>
                <div>+20 10 0000 0000</div>
                <div>{isArabic ? 'مصر' : 'Cairo, Egypt'}</div>
              </div>
            </div>

            <div>
              <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
                {isArabic ? 'تابعنا' : 'Follow Us'}
              </h3>
              <div className="mt-3 flex gap-2 text-xs text-slate-400">
                <span className="rounded-full border border-white/10 px-2.5 py-1">in</span>
                <span className="rounded-full border border-white/10 px-2.5 py-1">f</span>
                <span className="rounded-full border border-white/10 px-2.5 py-1">◎</span>
              </div>
            </div>
          </div>

          <div className="border-t border-white/10 px-4 py-4 text-center text-[11px] text-slate-500">
            © 2026 Nile Key for Investment & International Trade. All rights reserved.
          </div>
        </footer>
      </main>
    </div>
  );
}
