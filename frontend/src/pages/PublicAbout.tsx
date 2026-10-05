import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

export function PublicAbout() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  return (
    <div className="min-h-screen bg-slate-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Title Section */}
        <section className="bg-[#002f32] py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-bold text-white">{t('public.about.title')}</h1>
            <p className="mt-2 text-base text-slate-300">{t('public.about.subtitle')}</p>
          </div>
        </section>

        {/* Who We Are */}
        <section className="bg-slate-900 py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-4xl font-bold text-white mb-6">{t('public.home.companySummaryTitle')}</h2>
                <div className="space-y-4 text-slate-300">
                  <p>{t('public.home.companySummaryP1')}</p>
                  <p>{t('public.home.companySummaryP2')}</p>
                  <p>{t('public.home.companySummaryP3')}</p>
                </div>
              </div>
              <div className="aspect-[4/3] rounded-2xl overflow-hidden bg-slate-800">
                <img
                  src="/assets/about-egypt.jpg"
                  alt={isArabic ? 'مشهد مصري' : 'Egyptian scene'}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Mission/Vision */}
        <section className="bg-slate-800 py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div className="order-2 lg:order-1">
                <h2 className="text-4xl font-bold text-emerald-400 mb-8">{t('public.about.missionTitle')}</h2>
                <div className="space-y-6 text-slate-300">
                  <p>{t('public.about.missionP1')}</p>
                  <p>{t('public.about.missionP2')}</p>
                  <p>{t('public.about.missionP3')}</p>
                </div>
              </div>
              <div className="order-1 lg:order-2">
                <img
                  src="/assets/about-egypt.jpg"
                  alt={isArabic ? 'مشهد مصري' : 'Egyptian scene'}
                  className="w-full aspect-[4/3] object-cover rounded-2xl"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Position as international trade partner */}
        <section className="bg-slate-900 py-20">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-4xl font-bold text-white mb-6">{t('public.home.trustedTitle')}</h2>
            <p className="text-lg text-slate-300 mb-8">{t('public.home.trustedDescription')}</p>
            <Link to="/contact">
              <Button className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">{t('public.cta.contactUs')}</Button>
            </Link>
          </div>
        </section>

        {/* Quick Overview */}
        <section className="bg-slate-800 py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <h2 className="text-4xl font-bold text-white mb-12 text-center">{isArabic ? 'لمحة سريعة' : 'Quick Overview'}</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-emerald-300 mb-2">{isArabic ? 'الاسم' : 'Company Name'}</h3>
                <p className="text-white font-semibold">{t('public.about.companyNameEn')}</p>
                <p className="text-slate-400 text-sm mt-1">{t('public.about.companyNameAr')}</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-emerald-300 mb-2">{isArabic ? 'الرخصة' : 'License'}</h3>
                <p className="text-white">{t('public.about.license')}</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-emerald-300 mb-2">{isArabic ? 'هدف التأسيس' : 'Purpose'}</h3>
                <p className="text-slate-300 text-sm">{t('public.about.purpose')}</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
