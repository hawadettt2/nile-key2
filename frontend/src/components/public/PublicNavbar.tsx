import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Menu, X } from 'lucide-react';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';
import { useState } from 'react';

export function PublicNavbar() {
  const { t } = useTranslation();
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
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#002f32]/95 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500 font-bold text-white">
              NK
            </div>
            <div className="hidden sm:flex flex-col">
              <span className="text-white font-bold text-base leading-tight">Nile Key</span>
              <span className="text-slate-400 text-[10px] leading-tight tracking-wide">
                Digital Export Platform
              </span>
            </div>
          </Link>

          <nav className="hidden lg:flex items-center gap-7">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="text-sm font-medium text-slate-300 transition-colors hover:text-emerald-400"
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="hidden lg:flex items-center gap-2">
            <LanguageSwitcher />
            <Link to="/login">
              <Button
                variant="ghost"
                className="text-white hover:text-emerald-400 hover:bg-white/5"
              >
                <LogIn size={16} />
                <span className="ms-2 text-sm">{t('public.cta.signIn')}</span>
              </Button>
            </Link>
            <Link to="/login">
              <Button className="bg-emerald-600 text-white hover:bg-emerald-700">
                <UserPlus size={16} />
                <span className="ms-2 text-sm">{t('public.cta.createAccount')}</span>
              </Button>
            </Link>
          </div>

          <button
            className="lg:hidden rounded-md p-2 text-slate-300 hover:text-white hover:bg-white/5"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>

        {mobileOpen && (
          <div className="lg:hidden border-t border-white/10 pb-4 pt-3">
            <nav className="flex flex-col gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className="rounded-md px-3 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-white/5 hover:text-emerald-400"
                  onClick={() => setMobileOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
              <div className="mt-3 flex flex-col gap-2 border-t border-white/10 pt-3">
                <div className="flex justify-center">
                  <LanguageSwitcher />
                </div>
                <Link to="/login" onClick={() => setMobileOpen(false)}>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-white hover:text-emerald-400 hover:bg-white/5"
                  >
                    <LogIn size={16} />
                    <span className="ms-2 text-sm">{t('public.cta.signIn')}</span>
                  </Button>
                </Link>
                <Link to="/login" onClick={() => setMobileOpen(false)}>
                  <Button className="w-full bg-emerald-600 text-white hover:bg-emerald-700">
                    <UserPlus size={16} />
                    <span className="ms-2 text-sm">{t('public.cta.createAccount')}</span>
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
