import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export function PublicFooter() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  return (
    <footer className="bg-[#001a1c] border-t border-white/10 py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-8 lg:gap-12">
          {/* Column 1: Logo + Brand + Tagline */}
          <div>
            <Link to="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500 font-bold text-white">
                NK
              </div>
              <div>
                <div className="font-bold leading-tight text-white">{isArabic ? 'مفتاح النيل' : 'Nile Key'}</div>
                <div className="text-[10px] text-slate-400">{isArabic ? 'المنصة الرقمية للتصدير' : 'Digital Export Platform'}</div>
              </div>
            </Link>
            <p className="mt-4 text-sm text-slate-400">
              {isArabic
                ? 'شركة مفتاح النيل للاستثمار والتجارة الدولية - شريكك الاستراتيجي في التجارة العالمية.'
                : 'Nile Key for Investment and International Trade - Your strategic partner in global trade.'}
            </p>
          </div>

          {/* Column 2: Quick Links */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
              {isArabic ? 'روابط سريعة' : 'Quick Links'}
            </h3>
            <ul className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm text-slate-400">
              <li><Link to="/" className="hover:text-white transition-colors">{t('public.nav.home')}</Link></li>
              <li><Link to="/about" className="hover:text-white transition-colors">{t('public.nav.about')}</Link></li>
              <li><Link to="/products" className="hover:text-white transition-colors">{t('public.nav.products')}</Link></li>
              <li><Link to="/services" className="hover:text-white transition-colors">{t('public.nav.services')}</Link></li>
              <li><Link to="/markets" className="hover:text-white transition-colors">{t('public.nav.markets')}</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">{t('public.nav.contact')}</Link></li>
            </ul>
          </div>

          {/* Column 3: Contact Us */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
              {isArabic ? 'تواصل معنا' : 'Contact Us'}
            </h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-400">
              <li>{t('public.contact.locationText')}</li>
              <li>info@nilekey.com</li>
              <li>+20 10 0000 0000</li>
            </ul>
          </div>

          {/* Column 4: Follow Us */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
              {isArabic ? 'تابعنا' : 'Follow Us'}
            </h3>
            <div className="mt-3 flex gap-2 text-xs text-slate-400">
              <span className="rounded-full border border-white/10 px-2.5 py-1">in</span>
              <span className="rounded-full border border-white/10 px-2.5 py-1">f</span>
              <span className="rounded-full border border-white/10 px-2.5 py-1">◎</span>
            </div>
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
