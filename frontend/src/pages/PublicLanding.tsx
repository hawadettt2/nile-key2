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
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">NK</span>
            </div>
            <div className="flex flex-col">
              <span className="text-white font-bold text-xl">{isArabic ? 'مفتاح النيل' : 'Nile Key'}</span>
              <span className="text-slate-300 text-xs">{isArabic ? 'منصة رقمية للتصدير' : 'Digital Export Platform'}</span>
            </div>
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
          <div dir={isArabic ? 'rtl' : 'ltr'}>
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              {isArabic ? (
                <>
                  <span className="block">شركة مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م)</span>
                  <span className="block">Nile Key for Investment and International Trade LLC</span>
                </>
              ) : (
                <>
                  <span className="block">Nile Key for Investment and International Trade LLC</span>
                  <span className="block">شركة مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م)</span>
                </>
              )}
            </h1>
            <p className="text-lg text-slate-300 mb-4 max-w-4xl mx-auto leading-relaxed">
              {isArabic ? 'شركة مفتاح النيل للاستثمار والتجارة الدولية هي شركة مصرية ذات مسؤولية محدودة، مرخصة من الهيئة العامة للاستثمار والمناطق الحرة.' : 'Nile Key for Investment and International Trade LLC is an Egyptian limited liability company, licensed by the General Authority for Investment and Free Zones.'}
            </p>
            <p className="text-lg text-slate-300 mb-4 max-w-4xl mx-auto leading-relaxed">
              {isArabic ? 'هدف التأسيس هو إشهار جودة المنتج المصري من خضروات وفواكه ومنتجات المصانع الوطنية في الأسواق العالمية.' : 'The purpose of establishment is to showcase the quality of Egyptian products — vegetables, fruits, and national factory products — in global markets.'}
            </p>
            <p className="text-lg text-slate-300 mb-6 max-w-4xl mx-auto leading-relaxed">
              {isArabic ? 'نركز على تسويق وتصدير المنتجات المصرية المختارة بعناية، وربط الموردين والمنتجين المصريين بالعملاء والمستوردين والشركاء الدوليين، من خلال منظومة متكاملة تجمع بين الخبرة التجارية، وإدارة عمليات التصدير، والحلول الرقمية الحديثة.' : 'We focus on marketing and exporting carefully selected Egyptian products, and connecting Egyptian suppliers and producers to clients, importers and international partners, through an integrated system combining commercial expertise, export process management, and modern digital solutions.'}
            </p>

            <h2 className="text-2xl font-bold text-white mb-4 mt-8">
              {isArabic ? 'منصتنا الرقمية المتكاملة لإدارة عمليات التصدير المصرية' : 'Our Integrated Digital Platform for Managing Egyptian Export Operations'}
            </h2>
            <p className="text-lg text-slate-300 mb-4 max-w-4xl mx-auto leading-relaxed">
              {isArabic ? 'طوّرنا منظومة Nile Key لتكون بيئة رقمية متكاملة لإدارة ومتابعة عمليات التجارة والتصدير، بدءًا من المنتج والمورد، مرورًا بالعميل والفاتورة والمستندات والشحن، ووصولًا إلى الميناء والأسواق العالمية.' : 'We have developed the Nile Key system to be an integrated digital environment for managing and monitoring trade and export operations — from the product and supplier, through the client, invoice, documents and shipment, and all the way to the port and global markets.'}
            </p>
            <p className="text-lg text-slate-300 mb-6 max-w-4xl mx-auto leading-relaxed">
              {isArabic ? 'نهدف إلى جعل عمليات التصدير أكثر تنظيمًا ووضوحًا وكفاءة وموثوقية، مع تسهيل التنسيق بين مختلف الأطراف ذات الصلة، ودعم الإجراءات التجارية واللوجستية والجمركية ضمن منظومة رقمية واحدة.' : 'We aim to make export operations more organized, clear, efficient and reliable, by facilitating coordination among all relevant parties and supporting commercial, logistical and customs procedures within a single digital system.'}
            </p>

            <h2 className="text-2xl font-bold text-white mb-4 mt-8">
              {isArabic ? 'من المزرعة أو المصنع المصري إلى الميناء والأسواق العالمية' : 'From the Egyptian Farm or Factory to the Port and Global Markets'}
            </h2>
            <p className="text-lg text-slate-300 mb-4 max-w-4xl mx-auto leading-relaxed">
              {isArabic ? 'نؤمن بأن المنتج المصري يمتلك القدرة على المنافسة عالميًا متى وجد الشريك التجاري المناسب، والتسويق الصحيح، والإدارة الدقيقة، والالتزام بالجودة والمواصفات ومتطلبات الأسواق المستهدفة.' : 'We believe that the Egyptian product is capable of competing globally whenever the right business partner, proper marketing, precise management, and commitment to quality, specifications, and target market requirements are in place.'}
            </p>
            <p className="text-lg text-slate-300 mb-6 max-w-4xl mx-auto leading-relaxed">
              {isArabic ? 'لذلك لا يقتصر دورنا على تنفيذ عملية التصدير، بل نعمل على بناء منظومة متكاملة تهدف إلى إيصال المنتج المصري المناسب إلى السوق المناسب، وبالطريقة المناسبة، وبناء علاقات تجارية طويلة الأمد مع العملاء والشركاء الدوليين.' : 'Therefore, our role does not stop at executing the export process, but we work to build an integrated system aimed at delivering the right Egyptian product to the right market, in the right way, and building long-term commercial relationships with clients and international partners.'}
            </p>

            <h2 className="text-2xl font-bold text-white mb-4 mt-8">
              {isArabic ? 'نحن شريكك الاستراتيجي في التجارة العالمية' : 'We Are Your Strategic Partner in Global Trade'}
            </h2>
          </div>
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
