import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useAuthStore } from '@/store/authStore';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { NotificationBell } from '@/components/NotificationBell';

export function Layout() {
  const isLoading = useAuthStore((s) => s.isLoading);
  const { i18n } = useTranslation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    document.documentElement.dir = i18n.language === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mql = window.matchMedia('(min-width: 768px) and (max-width: 1023px)');
    const onChange = () => setIsTablet(mql.matches);
    mql.addEventListener('change', onChange);
    setIsTablet(mql.matches);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-slate-50" dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
      <Sidebar collapsed={sidebarCollapsed} onToggleCollapsed={() => setSidebarCollapsed((v) => !v)} forceCollapsed={isTablet} />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 bg-white border-b border-slate-200 shadow-sm flex items-center justify-end px-6 flex-shrink-0">
          <NotificationBell />
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
