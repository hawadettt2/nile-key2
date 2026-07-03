import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LayoutDashboard, Truck, Users, FileText, Globe, FileArchive, BookOpen, Settings, LogOut, Menu, X, User } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useState } from 'react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'dashboard' },
  { path: '/suppliers', icon: Truck, label: 'suppliers' },
  { path: '/customers', icon: Users, label: 'customers' },
  { path: '/shipments', icon: Globe, label: 'shipments' },
  { path: '/invoices', icon: FileText, label: 'invoices' },
  { path: '/customs', icon: FileArchive, label: 'customs' },
  { path: '/documents', icon: BookOpen, label: 'documents' },
  { path: '/resources', icon: Settings, label: 'resources' },
  { path: '/profile', icon: User, label: 'profile' },
];

export function Sidebar() {
  const { t } = useTranslation();
  const location = useLocation();
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebarContent = (
    <div className={`h-full bg-slate-900 text-white flex flex-col transition-all duration-300 ${collapsed ? 'w-20' : 'w-64'}`}>
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
              <span className="font-bold text-white text-sm">NK</span>
            </div>
            <span className="font-bold text-lg">{t('app.name')}</span>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center mx-auto">
            <span className="font-bold text-white text-sm">NK</span>
          </div>
        )}
        <button onClick={() => setCollapsed(!collapsed)} className="hidden lg:block text-slate-400 hover:text-white">
          {collapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-4">
        <nav className="space-y-1 px-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link key={item.path} to={item.path} onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  isActive ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}>
                <Icon size={20} />
                {!collapsed && <span className="text-sm font-medium">{t(`nav.${item.label}`)}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="border-t border-slate-700 p-4">
        {!collapsed && user && (
          <div className="mb-3 px-3">
            <p className="text-sm font-medium text-white">{user.full_name}</p>
            <p className="text-xs text-slate-400">{user.role}</p>
          </div>
        )}
        <button onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 text-slate-300 hover:text-red-400 hover:bg-slate-800 rounded-lg w-full transition-colors">
          <LogOut size={20} />
          {!collapsed && <span className="text-sm font-medium">{t('app.logout')}</span>}
        </button>
      </div>
    </div>
  );

  return (
    <>
      <button onClick={() => setMobileOpen(!mobileOpen)} className="lg:hidden fixed top-4 left-4 z-50 bg-slate-900 text-white p-2 rounded-lg">
        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
      {mobileOpen && <div className="lg:hidden fixed inset-0 bg-black/50 z-40" onClick={() => setMobileOpen(false)} />}
      <aside className="hidden lg:block fixed h-screen z-30" style={{ direction: 'ltr' }}>{sidebarContent}</aside>
      {mobileOpen && <aside className="lg:hidden fixed inset-y-0 left-0 z-50" style={{ direction: 'ltr' }}>{sidebarContent}</aside>}
    </>
  );
}
