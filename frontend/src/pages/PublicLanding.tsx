import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  ArrowUpRight,
  Building2,
  Package,
  Workflow,
} from 'lucide-react';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const cards = [
    {
      icon: Building2,
      eyebrow: isArabic ? 'الشركة' : 'THE COMPANY',
      title: t('public.nav.about'),
      description: isArabic
        ? 'تعرف على شركة مفتاح النيل ورؤيتها في التجارة والتصدير الدولي.'
        : 'Discover Nile Key, our company, and our vision for international trade and export.',
      href: '/about',
    },
    {
      icon: Package,
      eyebrow: isArabic ? 'المنتجات' : 'PRODUCTS',
      title: t('public.nav.products'),
      description: isArabic
        ? 'اكتشف منتجات مصرية مختارة بعناية ومهيأة للأسواق العالمية.'
        : 'Explore carefully selected Egyptian products prepared for global markets.',
      href: '/products',
    },
    {
      icon: Workflow,
      eyebrow: isArabic ? 'المنظومة' : 'THE PLATFORM',
      title: t('public.nav.services'),
      description: isArabic
        ? 'استكشف خدمات التصدير والمنظومة الرقمية التي تدعم العملية من البداية إلى النهاية.'
        : 'Explore export services and the digital platform supporting the operation end to end.',
      href: '/services',
    },
  ];

  return (
    <div
      className="min-h-screen bg-[#f3f7f6] text-slate-900"
      dir={isArabic ? 'rtl' : 'ltr'}
    >
      <PublicNavbar />

      <main>
        <section className="relative overflow-hidden bg-[#00383b] text-white">
          <div className="pointer-events-none absolute -top-40 -end-40 h-96 w-96 rounded-full bg-emerald-400/10 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-48 -start-40 h-[28rem] w-[28rem] rounded-full bg-cyan-300/10 blur-3xl" />

          <div className="relative mx-auto grid max-w-7xl items-center gap-10 px-4 py-12 sm:px-6 sm:py-16 lg:grid-cols-[1fr_0.95fr] lg:gap-14 lg:px-8 lg:py-20">
            <div className="max-w-2xl">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-emerald-300/25 bg-white/5 px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-[0.2em] text-emerald-200">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                {isArabic ? 'مفتاح النيل • المنصة الرقمية للتصدير' : 'Nile Key • Digital Export Platform'}
              </div>

              <h1 className="max-w-2xl text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl">
                {t('public.home.heroTitle')}
              </h1>

              <p className="mt-5 max-w-2xl text-xl font-semibold leading-8 text-emerald-200 sm:text-2xl">
                {t('public.home.heroSubtitle')}
              </p>

              <p className="mt-5 max-w-xl text-base leading-8 text-slate-200 sm:text-lg">
                {t('public.home.heroDescription')}
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3">
                <Link to="/products">
                  <Button
                    size="lg"
                    className="bg-emerald-400 px-6 font-semibold text-slate-950 hover:bg-emerald-300"
                  >
                    {t('public.cta.exploreProducts')}
                    <ArrowRight size={18} className="ms-2" />
                  </Button>
                </Link>

                <Link to="/login">
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-white/40 bg-white/5 px-6 text-white hover:bg-white/10 hover:text-white"
                  >
                    {t('public.cta.signIn')}
                  </Button>
                </Link>

                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 px-2 text-sm font-semibold text-emerald-200 transition-colors hover:text-white"
                >
                  {t('public.cta.createAccount')}
                  <ArrowUpRight size={17} />
                </Link>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -inset-4 rounded-[2rem] border border-emerald-300/10 bg-emerald-300/5 blur-sm" />
              <div className="relative overflow-hidden rounded-[2rem] border border-white/15 bg-slate-950/20 shadow-2xl">
                <img
                  src="/assets/hero-export.jpg"
                  alt={isArabic ? 'منتجات مصرية وأسواق عالمية' : 'Egyptian products and global markets'}
                  className="block aspect-[4/3] h-full w-full object-cover"
                />
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#001f24]/75 via-[#001f24]/15 to-transparent p-5 sm:p-6">
                  <div className="flex items-end justify-between gap-4">
                    <div>
                      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-200">
                        {isArabic ? 'منظومة واحدة' : 'ONE ECOSYSTEM'}
                      </div>
                      <div className="mt-1 text-sm font-medium text-white/90">
                        {isArabic ? 'خبرة تجارية + إدارة تصدير + حلول رقمية' : 'Trade expertise + export management + digital solutions'}
                      </div>
                    </div>
                    <div className="hidden h-10 w-10 shrink-0 items-center justify-center rounded-full border border-white/20 bg-white/10 sm:flex">
                      <ArrowUpRight size={18} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="relative -mt-4 pb-4 sm:-mt-7 sm:pb-7">
          <div className="mx-auto grid max-w-7xl gap-4 px-4 sm:px-6 md:grid-cols-3 lg:px-8">
            {cards.map((card) => {
              const Icon = card.icon;

              return (
                <Link key={card.href} to={card.href} className="group">
                  <article className="h-full rounded-2xl border border-slate-200/80 bg-white/95 p-5 shadow-lg shadow-slate-900/5 backdrop-blur transition duration-200 group-hover:-translate-y-1 group-hover:border-emerald-300 group-hover:shadow-xl sm:p-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                        <Icon size={22} />
                      </div>
                      <ArrowUpRight
                        size={18}
                        className="text-slate-400 transition-colors group-hover:text-emerald-600"
                      />
                    </div>

                    <div className="mt-5 text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-700">
                      {card.eyebrow}
                    </div>
                    <h2 className="mt-2 text-xl font-bold text-slate-900">{card.title}</h2>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{card.description}</p>
                  </article>
                </Link>
              );
            })}
          </div>
        </section>

        <section className="px-4 pb-12 pt-8 sm:px-6 sm:pb-16 sm:pt-10 lg:px-8">
          <div className="mx-auto flex max-w-7xl flex-col gap-7 overflow-hidden rounded-[2rem] bg-[#00383b] px-6 py-8 text-white shadow-xl sm:px-8 sm:py-10 lg:flex-row lg:items-center lg:justify-between lg:px-10">
            <div className="max-w-2xl">
              <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-emerald-200">
                {isArabic ? 'جاهزون للخطوة التالية' : 'READY FOR THE NEXT STEP'}
              </div>
              <h2 className="mt-3 text-2xl font-bold leading-tight sm:text-3xl">
                {isArabic
                  ? 'من المنتج المصري إلى السوق العالمي، بمنظومة واحدة.'
                  : 'From Egyptian product to global market, through one connected system.'}
              </h2>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link to="/contact">
                <Button
                  size="lg"
                  className="bg-emerald-400 px-6 font-semibold text-slate-950 hover:bg-emerald-300"
                >
                  {t('public.cta.contactUs')}
                  <ArrowRight size={18} className="ms-2" />
                </Button>
              </Link>
              <Link to="/products">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-white/35 bg-white/5 px-6 text-white hover:bg-white/10 hover:text-white"
                >
                  {t('public.cta.exploreProducts')}
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
