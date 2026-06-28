import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export function Layout() {
  const loadUser = useAuthStore((s) => s.loadUser);
  const isLoading = useAuthStore((s) => s.isLoading);
  const { i18n } = useTranslation();

  useEffect(() => { loadUser(); }, []);
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
      <Sidebar />
      <main className="flex-1 lg:ml-64 p-6 pt-16 lg:pt-6">
        <Outlet />
      </main>
    </div>
  );
}
