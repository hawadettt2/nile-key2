import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Menu, X } from 'lucide-react';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';
import { useState } from 'react';

export function PublicNavbar() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { path: '/', label: t('public.nav.home') },
    { path: '/about', label: t('public.nav.about') },
    { path: '/products', label: t('public.nav.products') },
    { path: '/services', label: t('public.nav.services') },
    { path: '/markets', label: t('public.nav.markets') },
    { path: '/contact', label: t('public.nav.contact') },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">NK</span>
              </div>
              <div className="hidden sm:flex flex-col">
                <span className="text-white font-bold text-lg leading-tight">مفتاح النيل</span>
                <span className="text-white font-bold text-lg leading-tight">Nile Key</span>
                <span className="text-slate-300 text-xs leading-tight">Digital Export Platform</span>
              </div>
            </Link>
          </div>

          <nav className="hidden lg:flex items-center gap-6">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="text-slate-300 hover:text-emerald-400 transition-colors text-sm font-medium"
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="hidden lg:flex items-center gap-3">
            <LanguageSwitcher />
            <Link to="/login">
              <Button variant="ghost" className="text-white hover:text-emerald-400">
                <LogIn size={18} className="ms-2" />
                {t('public.cta.signIn')}
              </Button>
            </Link>
            <Link to="/login">
              <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
                <UserPlus size={18} className="ms-2" />
                {t('public.cta.createAccount')}
              </Button>
            </Link>
          </div>

          <button
            className="lg:hidden text-white p-2"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {mobileOpen && (
          <div className="lg:hidden py-4 border-t border-white/10">
            <nav className="flex flex-col gap-3">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className="text-slate-300 hover:text-emerald-400 transition-colors text-sm font-medium py-2"
                  onClick={() => setMobileOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
              <div className="flex flex-col gap-2 pt-3 border-t border-white/10">
                <div className="flex justify-center">
                  <LanguageSwitcher />
                </div>
                <Link to="/login" onClick={() => setMobileOpen(false)}>
                  <Button variant="ghost" className="text-white hover:text-emerald-400 w-full">
                    <LogIn size={18} className="ms-2" />
                    {t('public.cta.signIn')}
                  </Button>
                </Link>
                <Link to="/login" onClick={() => setMobileOpen(false)}>
                  <Button className="bg-emerald-600 hover:bg-emerald-700 text-white w-full">
                    <UserPlus size={18} className="ms-2" />
                    {t('public.cta.createAccount')}
                  </Button>
                </Link>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
