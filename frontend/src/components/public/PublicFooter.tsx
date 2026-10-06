import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Linkedin, MessageCircle, Youtube } from 'lucide-react';

export function PublicFooter() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language.startsWith('ar');
  const links = [
    { path: '/', label: t('public.nav.home') },
    { path: '/about', label: t('public.nav.about') },
    { path: '/products', label: t('public.nav.products') },
    { path: '/markets', label: t('public.nav.markets') },
    { path: '/services', label: t('public.nav.services') },
    { path: '/contact', label: t('public.nav.contact') },
  ];

  return (
    <footer className="bg-[#022725] text-white" dir="ltr">
      <div className="mx-auto w-[min(88vw,1200px)] py-5 sm:py-6">
        <div className="flex flex-col items-center justify-between gap-5 sm:flex-row sm:gap-8">
          <Link to="/" className="flex shrink-0 items-center gap-3" dir={isArabic ? 'rtl' : 'ltr'}>
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-[#22bd75] to-[#0ca55f] text-sm font-extrabold text-white">NK</span>
            <span className="flex flex-col">
              <span className="text-sm font-bold leading-tight">{isArabic ? 'مفتاح النيل' : 'Nile Key'}</span>
              <span className="mt-0.5 text-[9px] leading-tight text-white/60">{t('public.footer.tagline')}</span>
            </span>
          </Link>

          <nav aria-label={isArabic ? 'روابط التذييل' : 'Footer navigation'}>
            <ul className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2" dir={isArabic ? 'rtl' : 'ltr'}>
              {links.map(({ path, label }) => (
                <li key={path}>
                  <Link to={path} className="text-[11px] text-white/75 transition-colors hover:text-[#4ee58e] sm:text-xs">
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        <div className="mt-4 flex flex-col-reverse items-center justify-between gap-3 border-t border-white/10 pt-3 sm:flex-row">
          <p className="text-center text-[10px] leading-5 text-white/50 sm:text-left" dir={isArabic ? 'rtl' : 'ltr'}>
            {t('public.footer.copyright')}
          </p>
          <div className="flex items-center gap-3 text-white/85" aria-hidden="true">
            <Linkedin className="h-3.5 w-3.5" />
            <Youtube className="h-4 w-4" />
            <MessageCircle className="h-3.5 w-3.5" />
          </div>
        </div>
      </div>
    </footer>
  );
}
