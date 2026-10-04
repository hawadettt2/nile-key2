import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Globe, TrendingUp, Shield, Users, Brain, Network, ArrowRight } from 'lucide-react';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  return (
    <div className="min-h-screen bg-slate-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
          <img
            src="/assets/hero-export.jpg"
            alt="Egyptian export - fields, factories, and global markets"
            className="absolute inset-0 w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/40" />
          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-6">
              {t('public.home.heroTitle')}
            </h1>
            <p className="text-xl sm:text-2xl text-emerald-400 mb-4">
              {t('public.home.heroSubtitle')}
            </p>
            <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-10">
              {t('public.home.heroDescription')}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/login">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">
                  <LogIn size={20} className="ms-2" />
                  {t('public.cta.signIn')}
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="outline" className="border-white text-black hover:bg-white/10 hover:text-emerald-500 px-8">
                  <UserPlus size={20} className="ms-2" />
                  {t('public.cta.createAccount')}
                </Button>
              </Link>
              <Link to="/products">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">
                  {t('public.cta.exploreProducts')}
                  <ArrowRight size={20} className="ms-2" />
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Short Intro Navigation */}
        <section className="py-16 bg-slate-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <Link to="/about" className="group">
                <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8 text-center hover:border-emerald-500/30 transition-colors">
                  <h3 className="text-white font-semibold text-xl mb-2 group-hover:text-emerald-400 transition-colors">
                    {t('public.nav.about')}
                  </h3>
                  <p className="text-slate-400 text-sm">
                    {isArabic ? 'تعرف على شركتنا ورسالتنا' : 'Learn about our company and mission'}
                  </p>
                </div>
              </Link>
              <Link to="/products" className="group">
                <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8 text-center hover:border-emerald-500/30 transition-colors">
                  <h3 className="text-white font-semibold text-xl mb-2 group-hover:text-emerald-400 transition-colors">
                    {t('public.nav.products')}
                  </h3>
                  <p className="text-slate-400 text-sm">
                    {isArabic ? 'اكتشف منتجاتنا المصرية' : 'Discover our Egyptian products'}
                  </p>
                </div>
              </Link>
              <Link to="/services" className="group">
                <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8 text-center hover:border-emerald-500/30 transition-colors">
                  <h3 className="text-white font-semibold text-xl mb-2 group-hover:text-emerald-400 transition-colors">
                    {t('public.nav.services')}
                  </h3>
                  <p className="text-slate-400 text-sm">
                    {isArabic ? 'خدماتنا ومنظومتنا الرقمية' : 'Our services and digital platform'}
                  </p>
                </div>
              </Link>
            </div>
          </div>
        </section>

        {/* Company Summary */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-emerald-400 mb-8">
              {t('public.home.companySummaryTitle')}
            </h2>
            <p className="text-lg text-slate-300 mb-6 leading-relaxed">
              {t('public.home.companySummaryP1')}
            </p>
            <p className="text-lg text-slate-300 mb-6 leading-relaxed">
              {t('public.home.companySummaryP2')}
            </p>
            <p className="text-lg text-slate-300 mb-6 leading-relaxed">
              {t('public.home.companySummaryP3')}
            </p>
          </div>
        </section>

        {/* Platform Overview */}
        <section className="py-20 bg-slate-800">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">
              {t('public.home.platformTitle')}
            </h2>
            <p className="text-lg text-slate-300 mb-6 leading-relaxed">
              {t('public.home.platformP1')}
            </p>
            <p className="text-lg text-slate-300 mb-10 leading-relaxed">
              {t('public.home.platformP2')}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 text-center">
                <Globe className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-white font-semibold mb-2">{t('landing.features.shipments.title')}</h3>
                <p className="text-slate-400 text-sm">{t('landing.features.shipments.description')}</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 text-center">
                <Shield className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-white font-semibold mb-2">{t('landing.features.invoicing.title')}</h3>
                <p className="text-slate-400 text-sm">{t('landing.features.invoicing.description')}</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 text-center">
                <Users className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-white font-semibold mb-2">{t('landing.features.customs.title')}</h3>
                <p className="text-slate-400 text-sm">{t('landing.features.customs.description')}</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 text-center">
                <TrendingUp className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-white font-semibold mb-2">{t('landing.features.intelligence.title')}</h3>
                <p className="text-slate-400 text-sm">{t('landing.features.intelligence.description')}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-4xl mx-auto mt-6">
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 text-center">
                <Brain className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-white font-semibold mb-2">{t('landing.features.dem.title')}</h3>
                <p className="text-slate-400 text-sm">{t('landing.features.dem.description')}</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 text-center">
                <Network className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-white font-semibold mb-2">{t('landing.features.knowledgeGraph.title')}</h3>
                <p className="text-slate-400 text-sm">{t('landing.features.knowledgeGraph.description')}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Strategic Partner CTA */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-emerald-400 mb-8">
              {isArabic ? 'نحن شريكك الاستراتيجي في التجارة العالمية' : 'We Are Your Strategic Partner in Global Trade'}
            </h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/about">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">
                  {t('public.cta.learnMore')}
                  <ArrowRight size={20} className="ms-2" />
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
