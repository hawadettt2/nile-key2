import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export function PublicFooter() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  return (
    <footer className="bg-[#022F32] border-t border-white/10 py-16">
      <div className="mx-auto w-[min(92vw,1280px)]">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-8 lg:gap-12">
          {/* Column 1: Logo + Brand + Tagline */}
          <div>
            <Link to="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#19D8B0] font-bold text-[#022F32]">
                NK
              </div>
              <div>
                <div className="font-bold leading-tight text-white">{isArabic ? 'مفتاح النيل' : 'Nile Key'}</div>
                <div className="text-[10px] text-white/50">{isArabic ? 'المنصة الرقمية للتصدير' : 'Digital Export Platform'}</div>
              </div>
            </Link>
            <p className="mt-4 text-sm text-white/60">
              {isArabic
                ? 'شركة مفتاح النيل للاستثمار والتجارة الدولية - شريكك الاستراتيجي في التجارة العالمية.'
                : 'Nile Key for Investment and International Trade - Your strategic partner in global trade.'}
            </p>
          </div>

          {/* Column 2: Quick Links */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-[#19D8B0]">
              {isArabic ? 'روابط سريعة' : 'Quick Links'}
            </h3>
            <ul className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm text-white/60">
              <li><Link to="/" className="hover:text-white transition-colors">{t('public.nav.home')}</Link></li>
              <li><Link to="/about" className="hover:text-white transition-colors">{t('public.nav.about')}</Link></li>
              <li><Link to="/products" className="hover:text-white transition-colors">{t('public.nav.products')}</Link></li>
              <li><Link to="/services" className="hover:text-white transition-colors">{t('public.nav.services')}</Link></li>
              <li><Link to="/markets" className="hover:text-white transition-colors">{t('public.nav.markets')}</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">{t('public.nav.contact')}</Link></li>
            </ul>
          </div>

          {/* Column 3: Contact Us — only data existing in the project (location: Egypt) */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-[#19D8B0]">
              {isArabic ? 'تواصل معنا' : 'Contact Us'}
            </h3>
            <ul className="mt-3 space-y-2 text-sm text-white/60">
              <li>{t('public.contact.locationText')}</li>
            </ul>
          </div>

          {/* Column 4: Follow Us — G11 Asset Gap: no verified social platforms exist in the project or content source; no platforms invented, no fake glyphs */}
          <div data-asset-gap="G11">
            <h3 className="text-xs font-semibold uppercase tracking-[0.16em] text-[#19D8B0]">
              {isArabic ? 'تابعنا' : 'Follow Us'}
            </h3>
            <div className="mt-3">
              {/* G11 Gap: verified social platform links/assets required — none exist in the project; left empty intentionally (no invented platforms) */}
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 mt-8 pt-8 text-center">
          <p className="text-white/50 text-sm">
            {t('public.footer.copyright')}
          </p>
        </div>
      </div>
    </footer>
  );
}
