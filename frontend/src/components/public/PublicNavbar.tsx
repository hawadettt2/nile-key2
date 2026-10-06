import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Menu, X } from 'lucide-react';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';
import { useState } from 'react';

type PublicNavbarProps = {
  overlay?: boolean;
};

export function PublicNavbar({ overlay = false }: PublicNavbarProps) {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isArabic = i18n.language.startsWith('ar');

  const navItems = [
    { path: '/', label: t('public.nav.home') },
    { path: '/about', label: t('public.nav.about') },
    { path: '/products', label: t('public.nav.products') },
    { path: '/markets', label: t('public.nav.markets') },
    { path: '/services', label: t('public.nav.services') },
    { path: '/contact', label: t('public.nav.contact') },
  ];

  const isActive = (path: string) =>
    path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);

  return (
    <header
      dir="ltr"
      className={overlay
        ? `absolute inset-x-0 top-0 z-50 border-b border-white/10 ${mobileOpen ? 'bg-[#043B3E]/95 backdrop-blur-md' : 'bg-transparent'}`
        : 'sticky top-0 z-50 border-b border-white/10 bg-[#043B3E]/95 backdrop-blur-md'}
    >
      <div className="mx-auto w-[min(92vw,1280px)]">
        <div className="flex h-14 items-center justify-between lg:h-[68px]">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-[#22bd75] to-[#0ca55f] font-bold text-white shadow-sm">
              NK
            </div>
            <div className="hidden flex-col sm:flex" dir={isArabic ? 'rtl' : 'ltr'}>
              <span className="text-base font-bold leading-tight text-white">{isArabic ? 'مفتاح النيل' : 'Nile Key'}</span>
              <span className="text-[10px] leading-tight tracking-wide text-white/70">
                {t('public.footer.tagline')}
              </span>
            </div>
          </Link>

          <nav className="hidden items-center gap-6 lg:flex" dir={isArabic ? 'rtl' : 'ltr'}>
            {navItems.map((item) => {
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`relative text-[13px] font-medium transition-colors ${
                    active ? 'text-white' : 'text-white/70 hover:text-[#19D8B0]'
                  }`}
                >
                  {item.label}
                  {active && (
                  <span className="absolute -bottom-[17px] start-0 h-0.5 w-full rounded-full bg-[#19D8B0]" aria-hidden="true" />
                  )}
                </Link>
              );
            })}
          </nav>

          <div className="hidden items-center gap-2 lg:flex">
            <LanguageSwitcher variant="header" />
            <Button asChild variant="outline" className="border-white/70 bg-transparent text-white hover:bg-white/10 hover:text-white">
              <Link to="/login">
                <UserPlus size={16} />
                <span className="ms-2 text-sm">{t('public.cta.createAccount')}</span>
              </Link>
            </Button>
            <Button asChild className="bg-[#19D8B0] text-[#022F32] hover:bg-[#19D8B0]/90">
              <Link to="/login">
                <LogIn size={16} />
                <span className="ms-2 text-sm">{t('public.cta.signIn')}</span>
              </Link>
            </Button>
          </div>

          <button
            type="button"
            className="rounded-md p-2 text-white/80 hover:bg-white/10 hover:text-white lg:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label={isArabic ? (mobileOpen ? 'إغلاق القائمة' : 'فتح القائمة') : (mobileOpen ? 'Close menu' : 'Open menu')}
            aria-expanded={mobileOpen}
            aria-controls="public-mobile-navigation"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>

        <div
          id="public-mobile-navigation"
          className={`${mobileOpen ? 'block' : 'hidden'} border-t border-white/10 bg-[#043B3E]/95 pb-4 pt-3 backdrop-blur-md lg:hidden`}
        >
            <nav className="flex flex-col gap-1">
              {navItems.map((item) => {
                const active = isActive(item.path);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                      active
                        ? 'bg-white/5 text-white'
                        : 'text-white/70 hover:bg-white/5 hover:text-[#19D8B0]'
                    }`}
                    onClick={() => setMobileOpen(false)}
                  >
                    {item.label}
                  </Link>
                );
              })}
              <div className="mt-3 flex flex-col gap-2 border-t border-white/10 pt-3">
                <div className="flex justify-center">
                  <LanguageSwitcher variant="dark" />
                </div>
                <Button asChild variant="ghost" className="w-full justify-start text-white hover:bg-white/5 hover:text-[#19D8B0]">
                  <Link to="/login" onClick={() => setMobileOpen(false)}>
                    <LogIn size={16} />
                    <span className="ms-2 text-sm">{t('public.cta.signIn')}</span>
                  </Link>
                </Button>
                <Button asChild className="w-full bg-[#19D8B0] text-[#022F32] hover:bg-[#19D8B0]/90">
                  <Link to="/login" onClick={() => setMobileOpen(false)}>
                    <UserPlus size={16} />
                    <span className="ms-2 text-sm">{t('public.cta.createAccount')}</span>
                  </Link>
                </Button>
              </div>
            </nav>
        </div>
      </div>
    </header>
  );
}
