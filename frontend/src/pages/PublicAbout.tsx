import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

export function PublicAbout() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  return (
    <div className="min-h-screen bg-[#022F32] text-white" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Title Section */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 text-center md:py-20">
            <h1 className="text-3xl font-bold text-white lg:text-[34px]">{t('public.about.title')}</h1>
            <p className="mt-3 text-base text-white/70">{t('public.about.subtitle')}</p>
          </div>
        </section>

        {/* Who We Are */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
              <div>
                <h2 className="text-3xl font-bold text-white lg:text-[34px]">
                  {t('public.home.companySummaryTitle')}
                </h2>
                <div className="mt-6 space-y-4 text-base leading-7 text-white/70">
                  <p>{t('public.home.companySummaryP1')}</p>
                  <p>{t('public.home.companySummaryP2')}</p>
                  <p>{t('public.home.companySummaryP3')}</p>
                </div>
              </div>
              <div className="relative">
                <div className="absolute -bottom-6 lg:-end-6 h-full w-full rounded-2xl bg-[#022F32]" aria-hidden="true" />
                {/* G3 Asset Gap (reusable): Egyptian visual — atomic photograph, aspect 4/3 */}
                <div
                  className="relative aspect-[4/3] w-full rounded-2xl border border-white/10 bg-[#022F32]/70"
                  data-asset-gap="G3"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Mission / Vision */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
              <div className="order-2 lg:order-1">
                <h2 className="text-3xl font-bold text-[#19D8B0] lg:text-[34px]">
                  {t('public.about.missionTitle')}
                </h2>
                <div className="mt-6 space-y-4 text-base leading-7 text-white/70">
                  <p>{t('public.about.missionP1')}</p>
                  <p>{t('public.about.missionP2')}</p>
                  <p>{t('public.about.missionP3')}</p>
                </div>
                <h2 className="mt-10 text-3xl font-bold text-[#19D8B0] lg:text-[34px]">
                  {t('public.about.visionTitle')}
                </h2>
                <p className="mt-4 text-base leading-7 text-white/70">{t('public.about.visionText')}</p>
              </div>
              <div className="relative order-1 lg:order-2">
                <div className="absolute -bottom-6 lg:-end-6 h-full w-full rounded-2xl bg-[#043B3E]" aria-hidden="true" />
                {/* G3 Asset Gap (reusable): Egyptian visual — atomic photograph, aspect 4/3 */}
                <div
                  className="relative aspect-[4/3] w-full rounded-2xl border border-white/10 bg-[#043B3E]/70"
                  data-asset-gap="G3"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Position as international trade partner */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 text-center md:py-20">
            <h2 className="text-3xl font-bold text-white lg:text-[34px]">{t('public.home.trustedTitle')}</h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg leading-8 text-white/70">
              {t('public.home.trustedDescription')}
            </p>
            <Link to="/contact" className="mt-8 inline-block">
              <Button className="h-12 rounded-full bg-[#19D8B0] px-8 text-base font-semibold text-[#022F32] hover:bg-[#19D8B0]/90">
                {t('public.cta.contactUs')}
              </Button>
            </Link>
          </div>
        </section>

        {/* Quick Overview */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <h2 className="text-3xl font-bold text-white lg:text-[34px]">
              {isArabic ? 'لمحة سريعة' : 'Quick Overview'}
            </h2>
            <div className="mt-12 grid gap-8 md:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-[#19D8B0]">
                  {isArabic ? 'الاسم' : 'Company Name'}
                </h3>
                <p className="mt-3 font-semibold text-white">{t('public.about.companyNameEn')}</p>
                <p className="mt-1 text-sm text-white/60">{t('public.about.companyNameAr')}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-[#19D8B0]">
                  {isArabic ? 'الرخصة' : 'License'}
                </h3>
                <p className="mt-3 text-white">{t('public.about.license')}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-[#19D8B0]">
                  {isArabic ? 'هدف التأسيس' : 'Purpose'}
                </h3>
                <p className="mt-3 text-sm leading-6 text-white/70">{t('public.about.purpose')}</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
