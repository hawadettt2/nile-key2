import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  CheckCircle,
  Factory,
  FileText,
  ShieldCheck,
  Ship,
  Sparkles,
  Truck,
} from 'lucide-react';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-sm font-normal uppercase tracking-[0.1em] text-emerald-400">
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
      icon: Factory,
      title: t('public.markets.step1Title'),
      description: t('public.markets.step1Desc'),
    },
    {
      icon: CheckCircle,
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
      className="min-h-screen overflow-x-hidden bg-white text-slate-900"
      dir={isArabic ? 'rtl' : 'ltr'}
    >
      <PublicNavbar />

      <main>
        {/* Hero */}
        <section className="bg-[#002f32] min-h-[90vh]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-20 sm:px-6 sm:py-14 lg:grid-cols-[5fr_6fr] lg:gap-12 lg:px-8 lg:py-20">
            <div>
              <SectionLabel>
                {isArabic ? 'منتجات مصرية • أسواق عالمية' : 'Egyptian Products • Global Markets'}
              </SectionLabel>
              <h1 className="mt-3 text-4xl font-bold tracking-tight text-white">
                {t('public.home.heroTitle')}
              </h1>
              <div className="mt-2 text-base font-semibold leading-7 text-emerald-400">
                {t('public.home.heroSubtitle')}
              </div>
              <p className="mt-4 text-sm leading-7 text-slate-300">
                {t('public.home.heroDescription')}
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link to="/login">
                  <Button className="bg-emerald-600 text-white hover:bg-emerald-700">
                    {t('public.home.ctaSignIn')}
                  </Button>
                </Link>
                <Link to="/login">
                  <Button variant="outline" className="border-white text-white hover:bg-white/10 hover:text-white">
                    {t('public.home.ctaCreateAccount')}
                  </Button>
                </Link>
              </div>
            </div>
            <div className="hidden lg:block">
              <img
                src="/assets/hero-export.jpg"
                alt={isArabic ? 'تصدير المنتجات المصرية' : 'Egyptian export'}
                className="w-full aspect-[3/2] object-cover rounded-[1.8rem] border border-white/10 shadow-2xl"
              />
            </div>
          </div>
        </section>

        {/* Our Company */}
        <section className="bg-[#f8fafc]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-20 sm:px-6 sm:py-14 lg:grid-cols-[6fr_5fr] lg:gap-12 lg:px-8 lg:py-20">
            <div className="lg:order-last">
              <img
                src="/assets/about-egypt.jpg"
                alt={isArabic ? 'مصر' : 'Egypt'}
                className="w-full aspect-[4/3] object-cover rounded-[1.5rem] border border-slate-200 shadow-xl"
              />
            </div>
            <div>
              <SectionLabel>
                {isArabic ? 'عن الشركة' : 'OUR COMPANY'}
              </SectionLabel>
              <h2 className="mt-2 text-4xl font-bold text-slate-900">
                {t('public.home.companySummaryTitle')}
              </h2>
              <p className="mt-4 max-w-[520px] text-sm leading-7 text-slate-600">
                {t('public.home.companySummaryP1')}
              </p>
              <p className="mt-3 max-w-[520px] text-sm leading-7 text-slate-600">
                {t('public.home.companySummaryP2')}
              </p>
              <p className="mt-3 max-w-[520px] text-sm leading-7 text-slate-600">
                {t('public.home.companySummaryP3')}
              </p>
              <Link to="/about" className="mt-6 inline-block text-emerald-600 underline underline-offset-4 hover:text-emerald-700">
                {t('public.cta.learnMore')}
              </Link>
            </div>
          </div>
        </section>

        {/* Premium Egyptian Products */}
        <section className="bg-[#002f32]">
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-14 lg:px-8 lg:py-20">
            <div className="text-center">
              <SectionLabel>
                {isArabic ? 'المنتجات الرئيسية' : 'KEY PRODUCTS'}
              </SectionLabel>
              <h2 className="mt-2 text-4xl font-bold text-white">
                {isArabic ? 'منتجات مصرية مميزة' : 'Premium Egyptian Products'}
              </h2>
            </div>
            <div className="mt-12 grid gap-6 md:grid-cols-3">
              {PRODUCTS.map((product) => (
                <Link key={product.title} to="/products" className="group">
                  <article className="overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm shadow-lg transition duration-200 group-hover:-translate-y-1 group-hover:border-emerald-300/30">
                    <div className="aspect-[3/2] overflow-hidden bg-[#053b3d]">
                      <img
                        src={product.image}
                        alt={product.title}
                        className="h-full w-full object-cover transition duration-200 group-hover:scale-105"
                      />
                    </div>
                    <div className="border-t border-white/10 bg-[#053b3d] p-6">
                      <h3 className="text-lg font-semibold text-white">{product.title}</h3>
                      <p className="mt-2 text-sm text-slate-300">{product.description}</p>
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* The Export Journey */}
        <section className="bg-[#f8fafc]">
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-14 lg:px-8 lg:py-20">
            <div className="mb-10 text-center">
              <SectionLabel>
                {isArabic ? 'رحلة التصدير' : 'THE EXPORT JOURNEY'}
              </SectionLabel>
              <h2 className="mt-2 text-4xl font-bold text-slate-900">
                {isArabic
                  ? 'من المزرعة أو المصنع إلى الأسواق العالمية'
                  : 'From farm or factory to global markets'}
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                {isArabic ? 'بجودة موثوقة في كل خطوة.' : 'With quality at every step.'}
              </p>
            </div>

            {/* Desktop horizontal timeline */}
            <div className="hidden md:block">
              <div className="relative">
                <div className="absolute top-6 start-0 end-0 h-[3px] bg-emerald-500" aria-hidden="true" />
                <div className="grid grid-cols-5 gap-6">
                  {journeySteps.map(({ icon: Icon, title, description }, index) => (
                    <div key={title} className="relative flex flex-col items-center text-center">
                      <div className="relative z-10 flex h-12 w-12 items-center justify-center rounded-full border border-emerald-300 bg-emerald-50 text-emerald-700">
                        <Icon size={20} />
                      </div>
                      <div className="mt-4 text-[10px] font-bold text-emerald-700">0{index + 1}</div>
                      <h3 className="mt-1 text-sm font-semibold text-slate-900">{title}</h3>
                      <p className="mt-1 text-xs leading-5 text-slate-600">{description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Mobile vertical timeline */}
            <div className="md:hidden">
              <div className="relative">
                <div className="absolute start-6 top-0 h-full w-px bg-emerald-500" aria-hidden="true" />
                <div className="space-y-8">
                  {journeySteps.map(({ icon: Icon, title, description }, index) => (
                    <div key={title} className="relative flex items-start gap-4">
                      <div className="relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-emerald-300 bg-emerald-50 text-emerald-700">
                        <Icon size={20} />
                      </div>
                      <div>
                        <div className="text-[10px] font-bold text-emerald-700">0{index + 1}</div>
                        <h3 className="mt-1 text-sm font-semibold text-slate-900">{title}</h3>
                        <p className="mt-1 text-xs leading-5 text-slate-600">{description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Digital Platform */}
        <section className="bg-[#002f32]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-20 sm:px-6 sm:py-14 lg:grid-cols-[5fr_6fr] lg:gap-12 lg:px-8 lg:py-20">
            <div className="lg:order-last">
              <div className="h-[500px] w-full rounded-[1.5rem] border border-white/10 bg-[#00383b] p-5 shadow-2xl">
                <div className="flex h-10 items-center justify-between">
                  <div className="flex gap-2">
                    <div className="h-2 w-2 rounded-full bg-emerald-400" />
                    <div className="h-2 w-2 rounded-full bg-emerald-300/50" />
                    <div className="h-2 w-2 rounded-full bg-emerald-300/50" />
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-3">
                  <div className="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                    <div className="h-1.5 w-10 rounded-full bg-emerald-400/80" />
                    <div className="mt-2 h-1.5 w-6 rounded-full bg-emerald-300/60" />
                  </div>
                  <div className="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                    <div className="h-1.5 w-8 rounded-full bg-emerald-400/80" />
                    <div className="mt-2 h-1.5 w-5 rounded-full bg-emerald-300/60" />
                  </div>
                  <div className="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                    <div className="h-1.5 w-7 rounded-full bg-emerald-400/80" />
                    <div className="mt-2 h-1.5 w-4 rounded-full bg-emerald-300/60" />
                  </div>
                  <div className="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                    <div className="h-1.5 w-9 rounded-full bg-emerald-400/80" />
                    <div className="mt-2 h-1.5 w-5 rounded-full bg-emerald-300/60" />
                  </div>
                </div>
                <div className="mt-4 h-24 rounded-xl border border-white/10 bg-white/[0.02]" />
              </div>
            </div>
            <div>
              <SectionLabel>
                {isArabic ? 'المنصة الرقمية' : 'DIGITAL PLATFORM'}
              </SectionLabel>
              <h2 className="mt-2 text-4xl font-bold leading-tight text-white">
                {t('public.home.platformTitle')}
              </h2>
              <p className="mt-4 text-sm leading-7 text-slate-200">
                {t('public.home.platformP1')}
              </p>
              <p className="mt-3 text-sm leading-7 text-slate-300">
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
                        <h3 className="text-sm font-semibold text-white">{title}</h3>
                        <p className="mt-1 text-xs leading-5 text-slate-400">{description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <Link to="/services" className="mt-6 inline-flex">
                <Button className="bg-emerald-400 font-semibold text-slate-950 hover:bg-emerald-300">
                  {t('public.cta.getStarted')}
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Global Markets */}
        <section className="bg-[#f8fafc]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-20 sm:px-6 sm:py-14 lg:grid-cols-[2fr_3fr] lg:gap-12 lg:px-8 lg:py-20">
            <div>
              <SectionLabel>
                {isArabic ? 'الأسواق العالمية' : 'OUR PRESENCE IN GLOBAL MARKETS'}
              </SectionLabel>
              <h2 className="mt-2 text-4xl font-bold text-slate-900">
                {isArabic
                  ? 'حضورنا في الأسواق العالمية'
                  : 'Our Presence in Global Markets'}
              </h2>
              <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">
                {isArabic ? 'منتجات مصرية بجودة موثوقة حول العالم.' : 'Egyptian products. Worldwide.'}
              </p>
              <div className="mt-6 flex flex-wrap gap-6">
                {[
                  ['50+', t('public.markets.statCountries')],
                  ['200+', t('public.markets.statPartners')],
                  ['100%', t('public.markets.statQuality')],
                ].map(([value, label]) => (
                  <div key={label} className="rounded-xl border border-slate-200 bg-white p-4 text-center shadow-sm">
                    <div className="text-3xl font-bold text-emerald-600">{value}</div>
                    <div className="mt-1 text-sm text-slate-600">{label}</div>
                  </div>
                ))}
              </div>
              <Link to="/markets" className="mt-6 inline-block text-emerald-600 underline underline-offset-4 hover:text-emerald-700">
                {t('public.cta.learnMore')}
              </Link>
            </div>
            <div className="hidden lg:block">
              <div className="relative h-[340px] w-full overflow-hidden rounded-[1.5rem] border border-slate-200 bg-slate-50">
                <svg viewBox="0 0 600 340" className="h-full w-full" aria-hidden="true" focusable="false">
                  {/* Simplified world map silhouette */}
                  <path d="M140,70 Q170,50 210,65 T270,85 Q300,105 285,140 T255,175 Q225,200 195,185 T140,155 Q115,130 125,95 Z" fill="#e2e8f0" opacity="0.5" />
                  <path d="M310,55 Q350,45 390,65 T415,110 Q425,145 405,165 T365,175 Q335,165 320,130 T310,90 Z" fill="#e2e8f0" opacity="0.5" />
                  <path d="M95,200 Q135,190 175,210 T200,255 Q185,290 155,300 T115,285 Q85,260 95,230 Z" fill="#e2e8f0" opacity="0.5" />
                  <path d="M245,200 Q285,190 325,215 T350,265 Q335,305 300,315 T250,295 Q220,265 240,230 Z" fill="#e2e8f0" opacity="0.5" />
                  <path d="M395,180 Q435,170 475,200 T500,255 Q485,295 450,305 T400,275 Q375,240 395,200 Z" fill="#e2e8f0" opacity="0.5" />
                  {/* Market nodes */}
                  <circle cx="175" cy="110" r="6" fill="#10b981" />
                  <circle cx="355" cy="100" r="6" fill="#10b981" />
                  <circle cx="145" cy="235" r="5" fill="#10b981" />
                  <circle cx="275" cy="245" r="6" fill="#10b981" />
                  <circle cx="415" cy="225" r="5" fill="#10b981" />
                  <circle cx="455" cy="165" r="6" fill="#10b981" />
                  {/* Connecting lines */}
                  <line x1="175" y1="110" x2="355" y2="100" stroke="#10b981" strokeWidth="1" opacity="0.3" />
                  <line x1="175" y1="110" x2="145" y2="235" stroke="#10b981" strokeWidth="1" opacity="0.3" />
                  <line x1="355" y1="100" x2="455" y2="165" stroke="#10b981" strokeWidth="1" opacity="0.3" />
                  <line x1="355" y1="100" x2="275" y2="245" stroke="#10b981" strokeWidth="1" opacity="0.3" />
                  <line x1="275" y1="245" x2="415" y2="225" stroke="#10b981" strokeWidth="1" opacity="0.3" />
                  <line x1="455" y1="165" x2="415" y2="225" stroke="#10b981" strokeWidth="1" opacity="0.3" />
                </svg>
              </div>
            </div>
          </div>
        </section>

        {/* Trusted Partners / CTA */}
        <section className="bg-[#002f32]">
          <div className="mx-auto grid max-w-7xl gap-12 px-4 py-20 sm:px-6 sm:py-14 lg:grid-cols-2 lg:gap-12 lg:px-8 lg:py-20">
            {/* Trust Zone */}
            <div className="flex flex-col justify-center">
              <SectionLabel>
                {isArabic ? 'شريك موثوق' : 'TRUSTED PARTNER'}
              </SectionLabel>
              <h2 className="mt-3 text-2xl font-bold text-white">
                {t('public.home.trustZoneTitle')}
              </h2>
              <p className="mt-2 max-w-[400px] text-sm leading-6 text-slate-400">
                {t('public.home.trustZoneText')}
              </p>
            </div>

            {/* CTA Zone */}
            <div className="flex flex-col justify-center">
              <h2 className="text-4xl font-bold text-white">
                {t('public.home.trustedTitle')}
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                {t('public.home.trustedDescription')}
              </p>
              <Link to="/contact" className="mt-5 inline-flex">
                <Button className="bg-emerald-600 text-white hover:bg-emerald-700 px-8 h-12">
                  {t('public.home.trustedCta')}
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
