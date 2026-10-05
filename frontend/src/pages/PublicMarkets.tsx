import { Fragment } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';
import { Button } from '@/components/ui/button';
import {
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Factory,
  FileText,
  Globe,
  Ship,
  Truck,
  type LucideIcon,
} from 'lucide-react';

export function PublicMarkets() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const steps: { icon: LucideIcon; title: string; description: string }[] = [
    { icon: Factory, title: t('public.markets.step1Title'), description: t('public.markets.step1Desc') },
    { icon: CheckCircle, title: t('public.markets.step2Title'), description: t('public.markets.step2Desc') },
    { icon: FileText, title: t('public.markets.step3Title'), description: t('public.markets.step3Desc') },
    { icon: Truck, title: t('public.markets.step4Title'), description: t('public.markets.step4Desc') },
    { icon: Ship, title: t('public.markets.step5Title'), description: t('public.markets.step5Desc') },
    { icon: Globe, title: t('public.markets.step6Title'), description: t('public.markets.step6Desc') },
  ];

  const stats = [
    { value: '50+', label: t('public.markets.statCountries') },
    { value: '200+', label: t('public.markets.statPartners') },
    { value: '100%', label: t('public.markets.statQuality') },
  ];

  return (
    <div className="min-h-screen bg-[#022F32] text-white" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 text-center md:py-20">
            <h1 className="text-3xl font-bold text-white lg:text-[34px]">{t('public.markets.title')}</h1>
            <p className="mt-3 text-base text-white/70">{t('public.markets.subtitle')}</p>
          </div>
        </section>

        {/* Journey Section — 6 stages (this page keeps its full 6-stage content; Home shows the first 5) */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <div className="mb-12 text-center">
              <h2 className="text-3xl font-bold text-white lg:text-[34px]">
                {t('public.markets.journeyTitle')}
              </h2>
            </div>

            {/* Desktop horizontal timeline */}
            <div className="relative hidden md:block">
              <div className="absolute inset-x-0 top-7 h-[3px] bg-white/15" aria-hidden="true" />
              <div className="absolute inset-x-0 top-7" aria-hidden="true">
                {[16.66, 33.33, 50, 66.66, 83.33].map((left) => (
                  <ChevronRight
                    key={left}
                    className="absolute -top-[9px] text-[#19D8B0]"
                    style={{ left: `${left}%`, transform: 'translateX(-50%)' }}
                    size={18}
                  />
                ))}
              </div>
              <div className="relative grid grid-cols-6 gap-4">
                {steps.map(({ icon: Icon, title, description }) => (
                  <div key={title} className="flex flex-col items-center text-center">
                    <div className="relative z-10 flex h-14 w-14 items-center justify-center rounded-full border border-white/15 bg-[#022F32] text-[#19D8B0]">
                      <Icon size={22} />
                    </div>
                    <h3 className="mt-4 text-sm font-semibold leading-5 text-white">{title}</h3>
                    <p className="mt-2 max-w-[170px] text-xs leading-5 text-white/60">{description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Mobile vertical timeline */}
            <div className="flex flex-col md:hidden">
              {steps.map(({ icon: Icon, title, description }, index) => (
                <Fragment key={title}>
                  <div className="flex items-start gap-4">
                    <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-white/15 bg-[#022F32] text-[#19D8B0]">
                      <Icon size={22} />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-white">{title}</h3>
                      <p className="mt-1 text-sm leading-6 text-white/60">{description}</p>
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <div className="relative ms-7 mt-2 h-10 w-[3px] bg-white/15" aria-hidden="true">
                      <ChevronDown
                        className="absolute -left-[7.5px] top-1/2 -translate-y-1/2 text-[#19D8B0]"
                        size={18}
                      />
                    </div>
                  )}
                </Fragment>
              ))}
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <div className="grid gap-8 sm:grid-cols-3">
              {stats.map((stat, index) => (
                <div key={stat.value} className={index > 0 ? 'border-s border-white/10 ps-8' : ''}>
                  <div className="text-3xl font-bold leading-tight text-[#19D8B0] lg:text-[36px]">
                    {stat.value}
                  </div>
                  <div className="mt-2 text-sm text-white/60">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 text-center md:py-20">
            <Link to="/contact">
              <Button className="h-12 rounded-full bg-[#19D8B0] px-8 text-base font-semibold text-[#022F32] hover:bg-[#19D8B0]/90">
                {t('public.cta.contactUs')}
              </Button>
            </Link>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
