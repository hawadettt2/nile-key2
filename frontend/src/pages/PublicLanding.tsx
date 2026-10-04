import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  ArrowUpRight,
  Building2,
  Factory,
  FileText,
  Globe2,
  Package,
  Ship,
  ShieldCheck,
  Sparkles,
  Truck,
} from 'lucide-react';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const journeySteps = [
    {
      icon: Factory,
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

  const products = [
    {
      image: '/assets/products/vegetables.jpg',
      title: t('public.products.vegetablesTitle'),
      description: t('public.products.vegetablesDesc'),
    },
    {
      image: '/assets/products/fruits.jpg',
      title: t('public.products.fruitsTitle'),
      description: t('public.products.fruitsDesc'),
    },
    {
      image: '/assets/products/factory.jpg',
      title: t('public.products.factoryTitle'),
      description: t('public.products.factoryDesc'),
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
      className="min-h-screen bg-[#002f32] text-white"
      dir={isArabic ? 'rtl' : 'ltr'}
    >
      <PublicNavbar />

      <main>
        {/* Concept 1 — full homepage composition */}
        <section className="relative overflow-hidden bg-[#00383b]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_82%_18%,rgba(52,211,153,0.13),transparent_28%),radial-gradient(circle_at_8%_70%,rgba(45,212,191,0.10),transparent_30%)]" />

          <div className="relative mx-auto grid max-w-7xl items-center gap-8 px-4 pb-10 pt-8 sm:px-6 sm:pb-14 sm:pt-10 lg:grid-cols-[0.92fr_1.08fr] lg:gap-10 lg:px-8 lg:pb-16">
            <div className="order-2 max-w-xl lg:order-1">
              <div className="mb-4 text-[11px] font-semibold uppercase tracking-[0.22em] text-emerald-300">
                {isArabic ? 'منتجات مصرية • أسواق عالمية' : 'Egyptian Products • Global Markets'}
              </div>

              <h1 className="text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl">
                {isArabic ? 'Nile Key' : 'Nile Key'}
              </h1>

              <div className="mt-3 text-base font-semibold leading-7 text-white sm:text-lg">
                {t('public.home.heroTitle')}
              </div>

              <p className="mt-4 max-w-xl text-sm leading-7 text-slate-200 sm:text-base">
                {t('public.home.heroSubtitle')}
              </p>

              <p className="mt-3 max-w-xl text-sm leading-7 text-slate-300 sm:text-[15px]">
                {isArabic
                  ? 'نربط الموردين والعملاء والجهات اللوجستية في منظومة رقمية واحدة تدعم التصدير المصري بكفاءة ووضوح.'
                  : 'We connect suppliers, customers, and logistics partners in one digital ecosystem supporting Egyptian exports with clarity and efficiency.'}
              </p>

              <div className="mt-7 flex flex-wrap gap-3">
                <Link to="/products">
                  <Button
                    size="lg"
                    className="bg-emerald-400 px-6 font-semibold text-slate-950 hover:bg-emerald-300"
                  >
                    {t('public.cta.exploreProducts')}
                    <ArrowRight size={18} className="ms-2" />
                  </Button>
                </Link>

                <Link to="/about">
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-white/45 bg-transparent px-6 text-white hover:bg-white/10 hover:text-white"
                  >
                    {t('public.cta.learnMore')}
                    <ArrowRight size={18} className="ms-2" />
                  </Button>
                </Link>
              </div>
            </div>

            <div className="order-1 lg:order-2">
              <div className="relative overflow-hidden rounded-[2rem] border border-white/10 shadow-2xl">
                <img
                  src="/assets/hero-export.jpg"
                  alt={isArabic ? 'منتجات مصرية وأسواق عالمية' : 'Egyptian products and global markets'}
                  className="block aspect-[4/3] w-full object-cover"
                />
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#001f24]/85 via-[#001f24]/20 to-transparent p-5 sm:p-6">
                  <div className="flex items-end justify-between gap-4">
                    <div>
                      <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-200">
                        {isArabic ? 'مفتاح النيل' : 'NILE KEY'}
                      </div>
                      <div className="mt-1 text-sm font-medium text-white/95">
                        {isArabic ? 'المنصة الرقمية للتصدير' : 'Digital Export Platform'}
                      </div>
                    </div>
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-white/20 bg-white/10">
                      <ArrowUpRight size={17} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="border-t border-white/10 bg-[#003437]">
          <div className="mx-auto grid max-w-7xl gap-6 px-4 py-9 sm:px-6 sm:py-10 md:grid-cols-3 lg:px-8">
            {[
              {
                icon: Building2,
                title: t('public.nav.about'),
                description: isArabic ? 'تعرف على الشركة ورؤيتها ورسالتها.' : 'Meet the company, its vision, and its mission.',
                href: '/about',
              },
              {
                icon: Package,
                title: t('public.nav.products'),
                description: isArabic ? 'منتجات مصرية مختارة للأسواق العالمية.' : 'Selected Egyptian products for global markets.',
                href: '/products',
              },
              {
                icon: Globe2,
                title: t('public.nav.services'),
                description: isArabic ? 'منظومة رقمية متكاملة لدعم عمليات التصدير.' : 'An integrated digital platform supporting export operations.',
                href: '/services',
              },
            ].map(({ icon: Icon, title, description, href }) => (
              <Link key={href} to={href} className="group">
                <article className="flex h-full items-start gap-4 rounded-2xl border border-white/10 bg-white/[0.035] p-5 transition duration-200 group-hover:-translate-y-1 group-hover:border-emerald-300/30 group-hover:bg-white/[0.055]">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-300 ring-1 ring-emerald-300/15">
                    <Icon size={21} />
                  </div>
                  <div className="min-w-0">
                    <div className="mb-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
                      {isArabic ? 'اكتشف' : 'EXPLORE'}
                    </div>
                    <h2 className="text-lg font-bold text-white">{title}</h2>
                    <p className="mt-1 text-sm leading-6 text-slate-300">{description}</p>
                  </div>
                  <ArrowUpRight size={16} className="ms-auto mt-1 shrink-0 text-slate-500 transition-colors group-hover:text-emerald-300" />
                </article>
              </Link>
            ))}
          </div>
        </section>

        <section className="bg-[#00383b]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_0.78fr] lg:px-8 lg:py-14">
            <div>
              <div className="mb-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
                {isArabic ? 'عن الشركة' : 'OUR COMPANY'}
              </div>
              <h2 className="max-w-2xl text-3xl font-bold leading-tight sm:text-4xl">
                {t('public.home.companySummaryTitle')}
              </h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
                {t('public.home.companySummaryP1')}
              </p>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
                {t('public.home.companySummaryP2')}
              </p>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
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

            <div className="overflow-hidden rounded-[1.8rem] border border-white/10 bg-white/5">
              <img
                src="/assets/about-egypt.jpg"
                alt={isArabic ? 'مشهد مصري' : 'Egyptian scene'}
                className="block aspect-[4/3] w-full object-cover"
              />
            </div>
          </div>
        </section>

        <section className="border-t border-white/10 bg-[#003337]">
          <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-14">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
                  {isArabic ? 'المنتجات الرئيسية' : 'KEY PRODUCTS'}
                </div>
                <h2 className="mt-2 text-3xl font-bold sm:text-4xl">
                  {isArabic ? 'منتجات مصرية مميزة' : 'Premium Egyptian Products'}
                </h2>
              </div>
              <Link to="/products" className="text-sm font-semibold text-emerald-300 hover:text-emerald-200">
                {isArabic ? 'عرض كل المنتجات' : 'View All Products'}
                <ArrowRight size={15} className="ms-2 inline" />
              </Link>
            </div>

            <div className="mt-7 grid gap-4 md:grid-cols-3">
              {products.map((product) => (
                <Link key={product.image} to="/products" className="group">
                  <article className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.035] transition duration-200 group-hover:-translate-y-1 group-hover:border-emerald-300/30">
                    <div className="aspect-[4/3] overflow-hidden">
                      <img
                        src={product.image}
                        alt={product.title}
                        className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.03]"
                      />
                    </div>
                    <div className="border-t border-white/10 p-4">
                      <h3 className="font-semibold text-white">{product.title}</h3>
                      <p className="mt-1 text-xs leading-5 text-slate-400">{product.description}</p>
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="bg-[#00383b]">
          <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-14">
            <div className="mb-8">
              <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
                {isArabic ? 'رحلة التصدير' : 'THE EXPORT JOURNEY'}
              </div>
              <h2 className="mt-2 text-3xl font-bold sm:text-4xl">
                {t('public.markets.journeyTitle')}
              </h2>
              <p className="mt-2 max-w-2xl text-sm text-slate-300">
                {isArabic ? 'من المزرعة أو المصنع إلى الأسواق العالمية — بجودة موثوقة في كل خطوة.' : 'From farm or factory to global markets — with quality at every step.'}
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              {journeySteps.map((step, index) => {
                const Icon = step.icon;

                return (
                  <div key={step.title} className="relative">
                    <article className="h-full rounded-2xl border border-white/10 bg-white/[0.035] p-4 text-center">
                      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-emerald-300/20 bg-emerald-300/10 text-emerald-300">
                        <Icon size={21} />
                      </div>
                      <div className="mt-3 text-[10px] font-bold text-emerald-300">
                        0{index + 1}
                      </div>
                      <h3 className="mt-1 text-sm font-semibold">{step.title}</h3>
                      <p className="mt-1 text-xs leading-5 text-slate-400">{step.description}</p>
                    </article>

                    {index < journeySteps.length - 1 && (
                      <div className="pointer-events-none absolute -end-3 top-1/2 hidden -translate-y-1/2 text-emerald-300 lg:block">
                        <ArrowRight size={16} />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="border-t border-white/10 bg-[#003337]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[0.86fr_1.14fr] lg:px-8 lg:py-14">
            <div className="relative mx-auto w-full max-w-lg overflow-hidden rounded-[1.75rem] border border-white/10 bg-slate-950/70 p-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-emerald-400" />
                  <span className="text-xs font-semibold text-slate-200">Nile Key</span>
                </div>
                <span className="text-[9px] uppercase tracking-[0.18em] text-slate-500">
                  Digital Platform
                </span>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-2">
                <div className="col-span-2 h-28 rounded-xl border border-emerald-300/15 bg-emerald-300/5 p-3">
                  <div className="h-2 w-24 rounded bg-white/15" />
                  <div className="mt-3 h-16 rounded-lg bg-[radial-gradient(circle_at_65%_35%,rgba(52,211,153,0.35),transparent_16%),linear-gradient(135deg,rgba(15,23,42,0.9),rgba(6,78,59,0.25))] border border-white/5" />
                </div>
                <div className="h-28 rounded-xl border border-white/10 bg-white/[0.03] p-3">
                  <div className="h-2 w-14 rounded bg-white/10" />
                  <div className="mt-4 h-10 rounded bg-white/5" />
                  <div className="mt-2 h-2 w-10 rounded bg-emerald-300/35" />
                </div>
              </div>

              <div className="mt-3 grid grid-cols-4 gap-2">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div key={index} className="rounded-lg border border-white/10 bg-white/[0.025] p-2">
                    <div className="h-6 w-6 rounded-md bg-emerald-300/10" />
                    <div className="mt-2 h-1.5 w-12 rounded bg-white/10" />
                    <div className="mt-1 h-1.5 w-8 rounded bg-white/5" />
                  </div>
                ))}
              </div>

              <div className="mt-3 flex items-center justify-between border-t border-white/10 pt-3 text-[9px] text-slate-500">
                <span>Shipments</span>
                <span>Invoices</span>
                <span>Documents</span>
                <span>Customs</span>
              </div>
            </div>

            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
                {isArabic ? 'المنصة الرقمية' : 'DIGITAL PLATFORM'}
              </div>
              <h2 className="mt-2 text-3xl font-bold leading-tight sm:text-4xl">
                {t('public.home.platformTitle')}
              </h2>
              <p className="mt-4 text-sm leading-7 text-slate-300 sm:text-base">
                {t('public.home.platformP1')}
              </p>
              <p className="mt-3 text-sm leading-7 text-slate-300 sm:text-base">
                {t('public.home.platformP2')}
              </p>

              <div className="mt-6 grid gap-3 sm:grid-cols-2">
                {platformFeatures.map((feature) => {
                  const Icon = feature.icon;

                  return (
                    <div key={feature.title} className="rounded-xl border border-white/10 bg-white/[0.035] p-3.5">
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 text-emerald-300">
                          <Icon size={17} />
                        </div>
                        <div>
                          <h3 className="text-sm font-semibold text-white">{feature.title}</h3>
                          <p className="mt-1 text-xs leading-5 text-slate-400">{feature.description}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
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

        <section className="relative overflow-hidden border-t border-white/10 bg-[#00383b]">
          <div className="absolute inset-0 opacity-70 bg-[radial-gradient(circle_at_50%_45%,rgba(52,211,153,0.13),transparent_38%)]" />

          <div className="relative mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-14">
            <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
                  {isArabic ? 'الأسواق العالمية' : 'GLOBAL MARKETS'}
                </div>
                <h2 className="mt-2 max-w-3xl text-3xl font-bold leading-tight sm:text-4xl">
                  {isArabic
                    ? 'من الحقول والمصانع المصرية إلى الأسواق العالمية'
                    : 'From Egyptian fields and factories to global markets'}
                </h2>
                <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
                  {isArabic ? 'جودة، ثقة، ونمو مستدام عبر شبكة تجارية ولوجستية متكاملة.' : 'Quality, trust, and sustainable growth through an integrated trade and logistics network.'}
                </p>
              </div>

              <div className="relative flex h-48 w-full max-w-md items-center justify-center overflow-hidden rounded-[1.75rem] border border-emerald-300/10 bg-emerald-300/[0.03]">
                <div className="absolute h-36 w-36 rounded-full border border-emerald-300/15" />
                <div className="absolute h-52 w-52 rounded-full border border-emerald-300/10" />
                <Globe2 className="relative h-24 w-24 text-emerald-200/75" strokeWidth={1.1} />
                <div className="absolute inset-x-8 bottom-4 h-px bg-gradient-to-r from-transparent via-emerald-300/25 to-transparent" />
              </div>
            </div>

            <div className="mt-8 grid grid-cols-3 border-t border-white/10">
              {[
                ['50+', isArabic ? 'دولة' : 'Countries'],
                ['200+', isArabic ? 'شريكًا تجاريًا' : 'Business Partners'],
                ['100%', isArabic ? 'التزام بالجودة' : 'Commitment to Quality'],
              ].map(([value, label]) => (
                <div key={label} className="border-e border-white/10 p-5 text-center last:border-e-0">
                  <div className="text-2xl font-bold text-white sm:text-3xl">{value}</div>
                  <div className="mt-1 text-xs text-slate-400">{label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-white/10 bg-slate-50">
          <div className="mx-auto grid max-w-7xl lg:grid-cols-2">
            <div className="p-7 sm:p-9 lg:p-10">
              <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-700">
                {isArabic ? 'شركاء عالميون موثوقون' : 'TRUSTED GLOBAL PARTNERS'}
              </div>
              <div className="mt-5 flex flex-wrap items-center gap-x-8 gap-y-4 text-sm font-bold text-slate-600">
                <span>SGS</span>
                <span>ISO</span>
                <span>HACCP</span>
                <span>GLOBALG.A.P.</span>
              </div>
            </div>

            <div className="relative min-h-[220px] overflow-hidden bg-slate-900 p-7 text-white sm:p-9 lg:p-10">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_30%,rgba(52,211,153,0.15),transparent_30%),linear-gradient(135deg,rgba(2,44,47,0.95),rgba(15,23,42,0.97))]" />
              <div className="relative">
                <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
                  {isArabic ? 'شريكك في التصدير' : 'YOUR STRATEGIC PARTNER'}
                </div>
                <h2 className="mt-3 text-2xl font-bold sm:text-3xl">
                  {isArabic ? 'لننطلق معًا نحو الأسواق العالمية' : "Let's Grow Together"}
                </h2>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-300">
                  {isArabic ? 'من المنتج المصري إلى المشتري العالمي عبر منظومة متكاملة.' : 'From Egyptian product to global buyer through one connected system.'}
                </p>
                <Link to="/contact" className="mt-6 inline-flex">
                  <Button className="bg-emerald-400 font-semibold text-slate-950 hover:bg-emerald-300">
                    {t('public.cta.contactUs')}
                    <ArrowRight size={17} className="ms-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
