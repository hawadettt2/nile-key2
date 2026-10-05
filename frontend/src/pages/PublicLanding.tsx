import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  Globe,
  Handshake,
  LayoutDashboard,
  Package,
} from 'lucide-react';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const features = [
    {
      icon: Package,
      title: t('public.concept1.featureBand.premiumProducts'),
    },
    {
      icon: Globe,
      title: t('public.concept1.featureBand.globalMarkets'),
    },
    {
      icon: Handshake,
      title: t('public.concept1.featureBand.trustedPartnerships'),
    },
    {
      icon: LayoutDashboard,
      title: t('public.concept1.featureBand.digitalSolutions'),
    },
  ];

  const products = [
    {
      imageSrc: '/assets/products/vegetables.jpg',
      title: t('public.products.vegetablesTitle'),
      description: t('public.products.vegetablesDesc'),
    },
    {
      imageSrc: '/assets/products/fruits.jpg',
      title: t('public.products.fruitsTitle'),
      description: t('public.products.fruitsDesc'),
    },
    {
      imageSrc: '/assets/products/factory.jpg',
      title: t('public.products.factoryTitle'),
      description: t('public.products.factoryDesc'),
    },
  ];

  return (
    <div className="min-h-screen overflow-x-hidden bg-white text-slate-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero: full-bleed photographic background */}
        <section className="relative min-h-[90vh] bg-[#002f32]">
          <div className="absolute inset-0">
            <img
              src="/assets/hero-export.jpg"
              alt={isArabic ? 'الصادرات المصرية' : 'Egyptian exports'}
              className="h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-black/40" />
          </div>
          <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-14 lg:px-8 lg:py-20">
            <div className="max-w-2xl">
              <div className="text-sm font-normal uppercase tracking-[0.1em] text-emerald-300">
                {t('public.concept1.heroEyebrow')}
              </div>
              <h1 className="mt-3 text-4xl font-bold tracking-tight text-white sm:text-5xl">
                {t('public.concept1.heroTitle')}
              </h1>
              <p className="mt-4 text-base leading-7 text-slate-200">
                {t('public.concept1.heroDescription')}
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/services">
                  <Button className="bg-emerald-600 text-white hover:bg-emerald-700">
                    {t('public.cta.getStarted')}
                  </Button>
                </Link>
                <Link to="/about">
                  <Button variant="outline" className="border-white text-white hover:bg-white/10 hover:text-white">
                    {t('public.cta.learnMore')}
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* 4-Item Feature Band */}
        <section className="bg-[#002f32] py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {features.map(({ icon: Icon, title }) => (
                <div key={title} className="flex flex-col items-center text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full border border-emerald-500 text-emerald-300">
                    <Icon size={20} />
                  </div>
                  <div className="mt-3 text-sm font-semibold text-white">{title}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Our Company */}
        <section className="bg-[#f8fafc]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-20 sm:px-6 sm:py-14 lg:grid-cols-2 lg:gap-12 lg:px-8 lg:py-20">
            <div>
              <div className="text-sm font-normal uppercase tracking-[0.1em] text-emerald-600">
                {isArabic ? 'عن الشركة' : 'OUR COMPANY'}
              </div>
              <h2 className="mt-3 text-4xl font-bold text-slate-900">
                {t('public.concept1.ourCompany.title')}
              </h2>
              <div className="mt-4 text-lg font-semibold text-slate-700">
                {t('public.concept1.ourCompany.subtitle')}
              </div>
              <p className="mt-4 max-w-xl text-sm leading-7 text-slate-600">
                {t('public.concept1.ourCompany.description')}
              </p>
              <Link to="/about" className="mt-6 inline-block text-emerald-600 underline underline-offset-4 hover:text-emerald-700">
                {t('public.cta.learnMore')}
              </Link>
            </div>
            <div className="aspect-[4/3] overflow-hidden rounded-2xl bg-slate-200">
              <img
                src="/assets/about-egypt.jpg"
                alt={isArabic ? 'مصر' : 'Egypt'}
                className="h-full w-full object-cover"
              />
            </div>
          </div>
        </section>

        {/* Premium Egyptian Products */}
        <section className="bg-white">
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-14 lg:px-8 lg:py-20">
            <div className="text-center">
              <div className="text-sm font-normal uppercase tracking-[0.1em] text-emerald-600">
                {isArabic ? 'المنتجات' : 'PRODUCTS'}
              </div>
              <h2 className="mt-2 text-4xl font-bold text-slate-900">
                {isArabic ? 'منتجات مصرية مميزة' : 'Premium Egyptian Products'}
              </h2>
            </div>
            <div className="mt-12 grid gap-8 md:grid-cols-3">
              {products.map((product) => (
                <div key={product.title} className="group text-center">
                  <div className="aspect-[3/2] overflow-hidden rounded-2xl bg-slate-100">
                    <img
                      src={product.imageSrc}
                      alt={product.title}
                      className="h-full w-full object-cover transition duration-200 group-hover:scale-105"
                    />
                  </div>
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-slate-900">{product.title}</h3>
                    <p className="mt-1 text-sm text-slate-600">{product.description}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-12 text-center">
              <Link to="/products">
                <Button className="bg-emerald-600 text-white hover:bg-emerald-700 px-8">
                  {isArabic ? 'عرض جميع المنتجات' : 'View All Products'}
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Global Closing Banner */}
        <section className="bg-[#002f32]">
          <div className="mx-auto grid max-w-7xl items-center gap-8 px-4 py-20 sm:px-6 sm:py-14 lg:grid-cols-2 lg:gap-12 lg:px-8 lg:py-20">
            <div>
              <div className="text-sm font-normal uppercase tracking-[0.1em] text-emerald-300">
                {isArabic ? 'الأسواق العالمية' : 'GLOBAL REACH'}
              </div>
              <h2 className="mt-3 text-4xl font-bold text-white">
                {t('public.concept1.closingBanner.title')}
              </h2>
              <p className="mt-3 text-base text-slate-300">
                {t('public.concept1.closingBanner.subtitle')}
              </p>
            </div>
            <div className="hidden lg:flex items-center justify-center">
              <svg viewBox="0 0 400 400" className="h-64 w-64 text-emerald-500" aria-hidden="true" focusable="false">
                <circle cx="200" cy="200" r="120" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.4" />
                <circle cx="200" cy="200" r="80" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.3" />
                <circle cx="200" cy="200" r="40" fill="currentColor" opacity="0.2" />
                <circle cx="200" cy="200" r="6" fill="currentColor" />
                <circle cx="200" cy="80" r="5" fill="currentColor" />
                <circle cx="200" cy="320" r="5" fill="currentColor" />
                <circle cx="80" cy="200" r="5" fill="currentColor" />
                <circle cx="320" cy="200" r="5" fill="currentColor" />
                <circle cx="120" cy="120" r="4" fill="currentColor" />
                <circle cx="280" cy="120" r="4" fill="currentColor" />
                <circle cx="120" cy="280" r="4" fill="currentColor" />
                <circle cx="280" cy="280" r="4" fill="currentColor" />
                <line x1="200" y1="200" x2="200" y2="80" stroke="currentColor" strokeWidth="1" opacity="0.4" />
                <line x1="200" y1="200" x2="200" y2="320" stroke="currentColor" strokeWidth="1" opacity="0.4" />
                <line x1="200" y1="200" x2="80" y2="200" stroke="currentColor" strokeWidth="1" opacity="0.4" />
                <line x1="200" y1="200" x2="320" y2="200" stroke="currentColor" strokeWidth="1" opacity="0.4" />
                <line x1="200" y1="200" x2="120" y2="120" stroke="currentColor" strokeWidth="1" opacity="0.3" />
                <line x1="200" y1="200" x2="280" y2="120" stroke="currentColor" strokeWidth="1" opacity="0.3" />
                <line x1="200" y1="200" x2="120" y2="280" stroke="currentColor" strokeWidth="1" opacity="0.3" />
                <line x1="200" y1="200" x2="280" y2="280" stroke="currentColor" strokeWidth="1" opacity="0.3" />
              </svg>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
