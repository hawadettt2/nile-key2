import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Globe } from 'lucide-react';

export function PublicFooter() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  return (
    <footer className="bg-slate-900 border-t border-white/10 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">NK</span>
              </div>
              <div className="flex flex-col">
                <span className="text-white font-bold text-lg leading-tight">{isArabic ? 'مفتاح النيل' : 'Nile Key'}</span>
                <span className="text-slate-300 text-xs leading-tight">{isArabic ? 'المنصة الرقمية للتصدير' : 'Digital Export Platform'}</span>
              </div>
            </div>
            <p className="text-slate-400 text-sm">
              {isArabic
                ? 'شركة مفتاح النيل للاستثمار والتجارة الدولية - شريكك الاستراتيجي في التجارة العالمية.'
                : 'Nile Key for Investment and International Trade - Your strategic partner in global trade.'}
            </p>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4">{isArabic ? 'روابط سريعة' : 'Quick Links'}</h3>
            <ul className="space-y-2">
              <li><Link to="/about" className="text-slate-400 hover:text-emerald-400 transition-colors text-sm">{t('public.nav.about')}</Link></li>
              <li><Link to="/products" className="text-slate-400 hover:text-emerald-400 transition-colors text-sm">{t('public.nav.products')}</Link></li>
              <li><Link to="/services" className="text-slate-400 hover:text-emerald-400 transition-colors text-sm">{t('public.nav.services')}</Link></li>
              <li><Link to="/markets" className="text-slate-400 hover:text-emerald-400 transition-colors text-sm">{t('public.nav.markets')}</Link></li>
              <li><Link to="/contact" className="text-slate-400 hover:text-emerald-400 transition-colors text-sm">{t('public.nav.contact')}</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4">{isArabic ? 'تواصل معنا' : 'Contact'}</h3>
            <ul className="space-y-2 text-sm text-slate-400">
              <li className="flex items-center gap-2">
                <Globe size={16} className="text-emerald-400" />
                {t('public.contact.locationText')}
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-white/10 mt-8 pt-8 text-center">
          <p className="text-slate-400 text-sm">
            {t('public.footer.copyright')}
          </p>
        </div>
      </div>
    </footer>
  );
}
