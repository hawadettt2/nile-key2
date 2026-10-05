import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';
import { Button } from '@/components/ui/button';
import {
  CheckCircle,
  Factory,
  FileText,
  Globe,
  Ship,
  Truck,
} from 'lucide-react';

export function PublicMarkets() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const steps = [
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
    {
      icon: Globe,
      title: t('public.markets.step6Title'),
      description: t('public.markets.step6Desc'),
    },
  ];

  return (
    <div className="min-h-screen bg-slate-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="bg-[#002f32] py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-bold text-white mb-4">{t('public.markets.title')}</h1>
            <p className="text-base text-slate-300">{t('public.markets.subtitle')}</p>
          </div>
        </section>

        {/* Journey Section */}
        <section className="bg-slate-900 py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-10 text-center">
              <h2 className="text-4xl font-bold text-emerald-400 mb-4">{t('public.markets.journeyTitle')}</h2>
            </div>

            {/* Desktop horizontal timeline */}
            <div className="hidden md:block">
              <div className="relative">
                <div className="absolute top-6 start-0 end-0 h-[3px] bg-emerald-500" aria-hidden="true" />
                <div className="grid grid-cols-6 gap-4">
                  {steps.map(({ icon: Icon, title, description }, index) => (
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
                  {steps.map(({ icon: Icon, title, description }, index) => (
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

        {/* CTA Section */}
        <section className="bg-slate-800 py-20">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
            <div className="flex justify-center">
              <Link to="/contact">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">{t('public.cta.contactUs')}</Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
