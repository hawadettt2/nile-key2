import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Globe, TrendingUp, Shield, Users, Brain, Network } from 'lucide-react';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <header className="flex items-center justify-between py-6">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">NK</span>
            </div>
            <span className="text-white font-bold text-xl">{t('app.name')}</span>
          </div>
          <div className="flex gap-3">
            <LanguageSwitcher />
            <Link to="/login">
              <Button variant="ghost" className="text-white hover:text-emerald-400">
                <LogIn size={18} className="mr-2" />
                {t('auth.login')}
              </Button>
            </Link>
            <Link to="/login">
              <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
                <UserPlus size={18} className="mr-2" />
                {t('auth.register')}
              </Button>
            </Link>
          </div>
        </header>

        <main className="py-20 text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
            {isArabic ? 'مفتاح النيل للاستثمار والتجارة الدولية' : 'Nile Key for Investment & International Trade'}
          </h1>
          <p className="text-xl text-slate-300 mb-4 max-w-3xl mx-auto">
            {t('landing.hero.subtitle')}
          </p>
          <p className="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
            {t('landing.hero.description')}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">
                <LogIn size={20} className="mr-2" />
                {isArabic ? 'تسجيل الدخول' : 'Sign In'}
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 px-8">
                <UserPlus size={20} className="mr-2" />
                {isArabic ? 'إنشاء حساب' : 'Create Account'}
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-20">
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <Globe className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-white font-semibold mb-2">{t('landing.features.shipments.title')}</h3>
              <p className="text-slate-400 text-sm">{t('landing.features.shipments.description')}</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <Shield className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-white font-semibold mb-2">{t('landing.features.invoicing.title')}</h3>
              <p className="text-slate-400 text-sm">{t('landing.features.invoicing.description')}</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <Users className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-white font-semibold mb-2">{t('landing.features.customs.title')}</h3>
              <p className="text-slate-400 text-sm">{t('landing.features.customs.description')}</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <TrendingUp className="w-10 h-10 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-white font-semibold mb-2">{t('landing.features.intelligence.title')}</h3>
              <p className="text-slate-400 text-sm">{t('landing.features.intelligence.description')}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-12 max-w-4xl mx-auto">
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
        </main>

        <footer className="py-8 border-t border-white/10 text-center">
          <p className="text-slate-400 text-sm">
            {t('landing.footer.copyright')}
          </p>
        </footer>
      </div>
    </div>
  );
}
