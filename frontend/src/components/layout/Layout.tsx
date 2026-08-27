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

  useEffect(() => {
    document.documentElement.dir = i18n.language === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50" dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
      <Sidebar collapsed={sidebarCollapsed} onToggleCollapsed={() => setSidebarCollapsed((v) => !v)} />
      <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-64'}`}>
        <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-end px-6">
          <NotificationBell />
        </header>
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
