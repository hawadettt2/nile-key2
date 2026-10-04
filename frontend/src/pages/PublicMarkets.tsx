import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';
import { MarketStepCard } from '@/components/public/MarketStepCard';
import { Button } from '@/components/ui/button';
import { ArrowRight, Factory, Shield, FileText, Ship, Anchor, Globe } from 'lucide-react';

export function PublicMarkets() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const steps = [
    {
      icon: <Factory size={32} />,
      title: t('public.markets.step1Title'),
      description: t('public.markets.step1Desc'),
    },
    {
      icon: <Shield size={32} />,
      title: t('public.markets.step2Title'),
      description: t('public.markets.step2Desc'),
    },
    {
      icon: <FileText size={32} />,
      title: t('public.markets.step3Title'),
      description: t('public.markets.step3Desc'),
    },
    {
      icon: <Ship size={32} />,
      title: t('public.markets.step4Title'),
      description: t('public.markets.step4Desc'),
    },
    {
      icon: <Anchor size={32} />,
      title: t('public.markets.step5Title'),
      description: t('public.markets.step5Desc'),
    },
    {
      icon: <Globe size={32} />,
      title: t('public.markets.step6Title'),
      description: t('public.markets.step6Desc'),
    },
  ];

  return (
    <div className="min-h-screen bg-slate-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="py-20 bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
              {t('public.markets.title')}
            </h1>
            <p className="text-xl text-slate-300">
              {t('public.markets.subtitle')}
            </p>
          </div>
        </section>

        {/* Journey Section */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-emerald-400 mb-12 text-center">
              {t('public.markets.journeyTitle')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {steps.map((step, index) => (
                <MarketStepCard
                  key={index}
                  stepNumber={index + 1}
                  icon={step.icon}
                  title={step.title}
                  description={step.description}
                />
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-slate-800">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-8">
              {isArabic ? 'ابدأ رحلة التصدير الخاصة بك' : 'Start Your Export Journey'}
            </h2>
            <p className="text-lg text-slate-300 mb-8">
              {isArabic
                ? 'نحن هنا لمساعدتك في كل خطوة من رحلة التصدير.'
                : 'We are here to help you at every step of your export journey.'}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/contact">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">
                  {t('public.cta.contactUs')}
                </Button>
              </Link>
              <Link to="/services">
                <Button size="lg" variant="outline" className="border-white text-black hover:bg-white/10 hover:text-emerald-500 px-8">
                  {t('public.cta.learnMore')}
                  <ArrowRight size={20} className="ms-2" />
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
