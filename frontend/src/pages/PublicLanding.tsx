import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  Globe,
  TrendingUp,
  Shield,
  Users,
  Brain,
  Network,
  Factory,
  Truck,
  FileText,
  Anchor,
  Package,
} from 'lucide-react';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const journeySteps = [
    {
      icon: <Factory size={24} />,
      title: t('public.markets.step1Title'),
      description: t('public.markets.step1Desc'),
    },
    {
      icon: <Package size={24} />,
      title: t('public.markets.step2Title'),
      description: t('public.markets.step2Desc'),
    },
    {
      icon: <FileText size={24} />,
      title: t('public.markets.step3Title'),
      description: t('public.markets.step3Desc'),
    },
    {
      icon: <Truck size={24} />,
      title: t('public.markets.step4Title'),
      description: t('public.markets.step4Desc'),
    },
    {
      icon: <Anchor size={24} />,
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
      icon: <Globe className="h-5 w-5" />,
      title: t('landing.features.shipments.title'),
      description: t('landing.features.shipments.description'),
    },
    {
      icon: <Shield className="h-5 w-5" />,
      title: t('landing.features.invoicing.title'),
      description: t('landing.features.invoicing.description'),
    },
    {
      icon: <Users className="h-5 w-5" />,
      title: t('landing.features.customs.title'),
      description: t('landing.features.customs.description'),
    },
    {
      icon: <TrendingUp className="h-5 w-5" />,
      title: t('landing.features.intelligence.title'),
      description: t('landing.features.intelligence.description'),
    },
    {
      icon: <Brain className="h-5 w-5" />,
      title: t('landing.features.dem.title'),
      description: t('landing.features.dem.description'),
    },
    {
      icon: <Network className="h-5 w-5" />,
      title: t('landing.features.knowledgeGraph.title'),
      description: t('landing.features.knowledgeGraph.description'),
    },
  ];

  const heroTitle = t('public.home.heroTitle');
  const heroSubtitle = t('public.home.heroSubtitle');
  const heroDescription = t('public.home.heroDescription');

  return (
    <div
      className="min-h-screen bg-[#f3f7f6] text-slate-900"
      dir={isArabic ? 'rtl' : 'ltr'}
    >
      <PublicNavbar />

      <main>
        {/* Concept 1 — Full Homepage: Hero */}
        <section className="bg-[#00383b] text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
            <div className="grid lg:grid-cols-[1.02fr_0.98fr] items-center gap-10 lg:gap-14">
              <div className="max-w-2xl">
                <div className="text-xs sm:text-sm font-semibold tracking-[0.22em] text-emerald-300 uppercase mb-5">
                  {isArabic ? 'منتجات مصرية • أسواق عالمية' : 'Egyptian Products • Global Markets'}
                </div>

                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-[1.05] mb-6">
                  {heroTitle}
                </h1>

                <p className="text-xl sm:text-2xl font-semibold text-emerald-300 mb-5">
                  {heroSubtitle}
                </p>

                <p className="text-base sm:text-lg leading-8 text-slate-200 max-w-xl mb-8">
                  {heroDescription}
                </p>

                <div className="flex flex-wrap gap-3">
                  <Link to="/products">
                    <Button size="lg" className="bg-emerald-400 hover:bg-emerald-300 text-slate-950 px-7 font-semibold">
                      {t('public.cta.exploreProducts')}
                      <ArrowRight size={18} className="ms-2" />
                    </Button>
                  </Link>
                  <Link to="/about">
                    <Button
                      size="lg"
                      variant="outline"
                      className="border-white/70 bg-transparent text-white hover:bg-white/10 hover:text-white px-7"
                    >
                      {t('public.cta.learnMore')}
                      <ArrowRight size={18} className="ms-2" />
                    </Button>
                  </Link>
                  <Link to="/login">
                    <Button
                      size="lg"
                      variant="ghost"
                      className="text-white hover:bg-white/10 hover:text-emerald-300 px-5"
                    >
                      {t('public.cta.signIn')}
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="relative">
                <div className="overflow-hidden rounded-[1.75rem] border border-white/10 shadow-2xl">
                  <img
                    src="/assets/hero-export.jpg"
                    alt={isArabic ? 'منتجات مصرية وأسواق عالمية' : 'Egyptian products and global markets'}
                    className="w-full aspect-[4/3] object-cover"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Concept 1 — Company */}
        <section className="bg-[#00383b] border-t border-white/10 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
            <div className="grid lg:grid-cols-[1fr_0.95fr] items-center gap-10 lg:gap-14">
              <div className="max-w-2xl">
                <div className="text-xs font-semibold tracking-[0.18em] text-emerald-300 uppercase mb-3">
                  {isArabic ? 'عن الشركة' : 'Our Company'}
                </div>
                <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                  {t('public.home.companySummaryTitle')}
                </h2>
                <div className="space-y-4 text-slate-200 leading-8">
                  <p>{t('public.home.companySummaryP1')}</p>
                  <p>{t('public.home.companySummaryP2')}</p>
                  <p>{t('public.home.companySummaryP3')}</p>
                </div>
                <Link to="/about" className="inline-flex mt-7">
                  <Button className="bg-transparent border border-emerald-400 text-emerald-300 hover:bg-emerald-400 hover:text-slate-950">
                    {t('public.cta.learnMore')}
                    <ArrowRight size={18} className="ms-2" />
                  </Button>
                </Link>
              </div>

              <div className="overflow-hidden rounded-[1.5rem] border border-white/10 bg-white/5">
                <img
                  src="/assets/about-egypt.jpg"
                  alt={isArabic ? 'مشهد مصري' : 'Egyptian scene'}
                  className="w-full aspect-[4/3] object-cover"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Concept 1 — Products */}
        <section className="bg-[#00383b] border-t border-white/10 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8">
              <div>
                <div className="text-xs font-semibold tracking-[0.18em] text-emerald-300 uppercase mb-3">
                  {isArabic ? 'منتجاتنا' : 'Key Products'}
                </div>
                <h2 className="text-3xl sm:text-4xl font-bold">
                  {isArabic ? 'المنتجات المصرية المميزة' : 'Premium Egyptian Products'}
                </h2>
              </div>
              <Link
                to="/products"
                className="inline-flex items-center text-sm font-semibold text-emerald-300 hover:text-emerald-200"
              >
                {isArabic ? 'عرض جميع المنتجات' : 'View All Products'}
                <ArrowRight size={16} className="ms-2" />
              </Link>
            </div>

            <div className="grid md:grid-cols-3 gap-5">
              {products.map((product) => (
                <Link key={product.title} to="/products" className="group">
                  <article className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] transition-all duration-200 group-hover:-translate-y-1 group-hover:border-emerald-400/40">
                    <div className="aspect-[4/3] overflow-hidden">
                      <img
                        src={product.image}
                        alt={product.title}
                        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
                      />
                    </div>
                    <div className="p-5">
                      <h3 className="font-semibold text-lg mb-2 group-hover:text-emerald-300">
                        {product.title}
                      </h3>
                      <p className="text-sm leading-6 text-slate-300">
                        {product.description}
                      </p>
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* Concept 1 — Export Journey */}
        <section className="bg-[#00383b] border-t border-white/10 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
            <div className="mb-9">
              <div className="text-xs font-semibold tracking-[0.18em] text-emerald-300 uppercase mb-3">
                {isArabic ? 'رحلة التصدير' : 'The Export Journey'}
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-3">
                {isArabic
                  ? 'من المزرعة أو المصنع إلى الأسواق العالمية'
                  : 'From farm or factory to global markets'}
              </h2>
              <p className="text-slate-300">
                {isArabic
                  ? 'جودة موثوقة في كل خطوة من خطوات التصدير.'
                  : 'With quality at every step.'}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
              {journeySteps.map((step, index) => (
                <div key={index} className="relative">
                  <div className="h-full rounded-2xl border border-white/10 bg-white/[0.04] p-5 text-center">
                    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-400/15 text-emerald-300 border border-emerald-400/30">
                      {step.icon}
                    </div>
                    <div className="text-xs font-semibold text-emerald-300 mb-2">
                      {index + 1}
                    </div>
                    <h3 className="font-semibold mb-2">{step.title}</h3>
                    <p className="text-xs leading-5 text-slate-300">{step.description}</p>
                  </div>
                  {index < journeySteps.length - 1 && (
                    <div className="hidden lg:block absolute top-1/2 -end-4 -translate-y-1/2 text-emerald-300/80">
                      <ArrowRight size={16} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Concept 1 — Digital Platform */}
        <section className="bg-[#00383b] border-t border-white/10 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
            <div className="grid lg:grid-cols-[1fr_1fr] items-center gap-10 lg:gap-14">
              <div className="relative rounded-[1.5rem] border border-white/10 bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 p-5 min-h-[290px] overflow-hidden">
                <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_20%_20%,rgba(52,211,153,0.45),transparent_35%),radial-gradient(circle_at_80%_75%,rgba(45,212,191,0.35),transparent_30%)]" />
                <div className="relative rounded-xl border border-white/10 bg-slate-950/80 shadow-2xl p-4 lg:p-6 max-w-lg mx-auto">
                  <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-emerald-400" />
                      <span className="text-xs text-slate-300">Nile Key</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Digital Export Platform</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 mb-5">
                    <div className="h-20 rounded-lg bg-emerald-400/10 border border-emerald-400/20" />
                    <div className="h-20 rounded-lg bg-white/5 border border-white/10" />
                    <div className="h-20 rounded-lg bg-white/5 border border-white/10" />
                  </div>
                  <div className="space-y-2">
                    <div className="h-2 rounded bg-white/10 w-4/5" />
                    <div className="h-2 rounded bg-white/10 w-3/5" />
                    <div className="h-2 rounded bg-emerald-400/40 w-2/5" />
                  </div>
                </div>
              </div>

              <div>
                <div className="text-xs font-semibold tracking-[0.18em] text-emerald-300 uppercase mb-3">
                  {isArabic ? 'المنصة الرقمية' : 'Digital Platform'}
                </div>
                <h2 className="text-3xl sm:text-4xl font-bold mb-5">
                  {t('public.home.platformTitle')}
                </h2>
                <div className="space-y-4 text-slate-200 leading-8 mb-8">
                  <p>{t('public.home.platformP1')}</p>
                  <p>{t('public.home.platformP2')}</p>
                </div>

                <div className="grid sm:grid-cols-2 gap-3">
                  {platformFeatures.map((feature) => (
                    <div
                      key={feature.title}
                      className="rounded-xl border border-white/10 bg-white/[0.04] p-3.5"
                    >
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 text-emerald-300 shrink-0">{feature.icon}</div>
                        <div>
                          <h3 className="text-sm font-semibold text-white">{feature.title}</h3>
                          <p className="text-xs leading-5 text-slate-400 mt-1">{feature.description}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <Link to="/services" className="inline-flex mt-7">
                  <Button className="bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-semibold">
                    {t('public.cta.learnMore')}
                    <ArrowRight size={18} className="ms-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Concept 1 — Global Markets */}
        <section className="bg-[#00383b] border-t border-white/10 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
            <div className="rounded-[1.75rem] border border-white/10 bg-gradient-to-br from-[#00383b] via-[#004d4e] to-[#00383b] overflow-hidden">
              <div className="grid lg:grid-cols-[1.05fr_0.95fr] items-center">
                <div className="p-8 lg:p-12">
                  <div className="text-xs font-semibold tracking-[0.18em] text-emerald-300 uppercase mb-3">
                    {isArabic ? 'الأسواق العالمية' : 'Global Markets'}
                  </div>
                  <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                    {isArabic
                      ? 'من الحقول والمصانع المصرية إلى الأسواق العالمية'
                      : 'From Egyptian fields and factories to global markets'}
                  </h2>
                  <p className="text-slate-200 max-w-xl">
                    {isArabic
                      ? 'جودة، ثقة، ونمو مستدام عبر شبكة تجارية ولوجستية متكاملة.'
                      : 'Quality, trust, and sustainable growth through an integrated trade and logistics network.'}
                  </p>
                </div>

                <div className="min-h-[260px] p-8 flex items-center justify-center">
                  <div className="relative flex h-56 w-56 items-center justify-center rounded-full border border-emerald-300/20 bg-emerald-300/5">
                    <div className="absolute inset-4 rounded-full border border-emerald-300/15" />
                    <div className="absolute inset-10 rounded-full border border-emerald-300/10" />
                    <Globe className="h-28 w-28 text-emerald-200/80" strokeWidth={1.25} />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 border-t border-white/10">
                {[
                  ['50+', isArabic ? 'دولة' : 'Countries'],
                  ['200+', isArabic ? 'شريكًا تجاريًا' : 'Business Partners'],
                  ['100%', isArabic ? 'التزام بالجودة' : 'Commitment to Quality'],
                ].map(([value, label]) => (
                  <div key={label} className="p-6 text-center border-b sm:border-b-0 sm:border-e last:border-e-0 border-white/10">
                    <div className="text-3xl font-bold text-white mb-1">{value}</div>
                    <div className="text-sm text-slate-300">{label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Concept 1 — Partners / CTA */}
        <section className="bg-[#00383b] border-t border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-10">
            <div className="grid lg:grid-cols-[1fr_1fr] overflow-hidden rounded-2xl border border-slate-200 bg-white">
              <div className="p-8 lg:p-10">
                <div className="text-xs font-semibold tracking-[0.16em] text-emerald-700 uppercase mb-3">
                  {isArabic ? 'شركاء عالميون موثوقون' : 'Trusted Global Partners'}
                </div>
                <div className="flex flex-wrap gap-x-6 gap-y-4 text-slate-600 text-sm font-semibold">
                  <span>SGS</span>
                  <span>ISO</span>
                  <span>HACCP</span>
                  <span>GLOBALG.A.P.</span>
                </div>
              </div>

              <div className="relative overflow-hidden bg-slate-900 min-h-[210px]">
                <img
                  src="/assets/hero-export.jpg"
                  alt=""
                  aria-hidden="true"
                  className="absolute inset-0 h-full w-full object-cover opacity-45"
                />
                <div className="absolute inset-0 bg-gradient-to-l from-slate-950/70 to-slate-950/20" />
                <div className="relative z-10 p-8 lg:p-10 text-white">
                  <div className="text-xs font-semibold tracking-[0.16em] text-emerald-300 uppercase mb-3">
                    {isArabic ? 'شريكك في التصدير' : 'Your Strategic Partner'}
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-bold mb-5">
                    {isArabic
                      ? 'لننطلق معًا نحو الأسواق العالمية'
                      : "Let's Grow Together"}
                  </h2>
                  <Link to="/contact">
                    <Button className="bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-semibold">
                      {t('public.cta.contactUs')}
                      <ArrowRight size={18} className="ms-2" />
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
