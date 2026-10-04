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
        {/* Hero / Title Section */}
        <section className="py-20 bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
              {t('public.about.title')}
            </h1>
            <p className="text-xl text-slate-300">
              {t('public.about.subtitle')}
            </p>
          </div>
        </section>

        {/* Who We Are */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold text-white mb-6">
                  {isArabic ? 'من نحن' : 'Who We Are'}
                </h2>
                <div className="space-y-4 text-slate-300">
                  <p className="text-lg">
                    <span className="text-emerald-400 font-semibold">{t('public.about.companyNameEn')}</span>
                    <br />
                    <span className="text-emerald-400 font-semibold">{t('public.about.companyNameAr')}</span>
                  </p>
                  <p>{t('public.about.companyType')}</p>
                  <p>{t('public.about.license')}</p>
                  <p>{t('public.about.purpose')}</p>
                </div>
              </div>
              <div className="aspect-square bg-slate-800 rounded-2xl overflow-hidden">
                <img
                  src="/assets/about-egypt.jpg"
                  alt={isArabic ? 'مشهد مصري' : 'Egyptian scene'}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Mission */}
        <section className="py-20 bg-slate-800">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-emerald-400 mb-8 text-center">
              {t('public.about.missionTitle')}
            </h2>
            <div className="space-y-6 text-slate-300 text-lg leading-relaxed">
              <p>{t('public.about.missionP1')}</p>
              <p>{t('public.about.missionP2')}</p>
              <p>{t('public.about.missionP3')}</p>
            </div>
          </div>
        </section>

        {/* Vision */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-emerald-400 mb-8">
              {t('public.about.visionTitle')}
            </h2>
            <p className="text-xl text-slate-300 leading-relaxed">
              {t('public.about.visionText')}
            </p>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 bg-slate-800">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-8">
              {isArabic ? 'انضم إلينا في رحلة التصدير' : 'Join Us on the Export Journey'}
            </h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/products">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">
                  {t('public.cta.exploreProducts')}
                </Button>
              </Link>
              <Link to="/contact">
                <Button size="lg" variant="outline" className="border-white text-black hover:bg-white/10 hover:text-emerald-500 px-8">
                  {t('public.cta.contactUs')}
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
