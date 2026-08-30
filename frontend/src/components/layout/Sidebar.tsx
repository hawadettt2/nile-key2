import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LayoutDashboard, Truck, Users, FileText, Globe, FileArchive, BookOpen, Settings, LogOut, Menu, X, User, Bell, Brain, Network, BarChart3, Target, Layers } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useState, useRef, useEffect } from 'react';
import * as Tooltip from '@radix-ui/react-tooltip';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapsed: () => void;
  forceCollapsed?: boolean;
}

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'dashboard', roles: ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics', 'supplier', 'customer'] },
  { path: '/digital-export-manager', icon: Brain, label: 'digitalExportManager', roles: ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics'] },
  { path: '/knowledge-graph', icon: Network, label: 'knowledgeGraph', roles: ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics'] },
  { path: '/trade-intelligence', icon: BarChart3, label: 'tradeIntelligence', roles: ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics'] },
  { path: '/export-readiness', icon: Target, label: 'exportReadiness', roles: ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics'] },
  { path: '/architecture-explorer', icon: Layers, label: 'architectureExplorer', roles: ['owner', 'manager', 'admin_staff'] },
  { path: '/suppliers', icon: Truck, label: 'suppliers', roles: ['owner', 'manager', 'admin_staff', 'logistics'] },
  { path: '/customers', icon: Users, label: 'customers', roles: ['owner', 'manager', 'sales', 'admin_staff'] },
  { path: '/shipments', icon: Globe, label: 'shipments', roles: ['owner', 'manager', 'sales', 'admin_staff', 'logistics', 'customer'] },
  { path: '/invoices', icon: FileText, label: 'invoices', roles: ['owner', 'manager', 'sales', 'accountant', 'customer'] },
  { path: '/customs', icon: FileArchive, label: 'customs', roles: ['owner', 'manager', 'admin_staff', 'logistics'] },
  { path: '/documents', icon: BookOpen, label: 'documents', roles: ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics'] },
  { path: '/resources', icon: Settings, label: 'resources', roles: ['owner', 'manager', 'admin_staff'] },
  { path: '/profile', icon: User, label: 'profile', roles: ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics', 'supplier', 'customer'] },
  { path: '/notifications', icon: Bell, label: 'notifications', roles: ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics', 'supplier', 'customer'] },
];

function NavItem({ item, collapsed, onLinkClick }: { item: typeof navItems[0]; collapsed: boolean; onLinkClick?: () => void }) {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const isActive = location.pathname === item.path;
  const Icon = item.icon;
  const isRTL = i18n.language === 'ar';

  const link = (
    <Link
      to={item.path}
      aria-current={isActive ? 'page' : undefined}
      onClick={onLinkClick}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors border-s-2 border-transparent ${
        isActive ? 'bg-emerald-600 text-white border-emerald-400' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
      }`}
    >
      <Icon size={20} />
      {!collapsed && <span className="text-sm font-medium">{t(`nav.${item.label}`)}</span>}
    </Link>
  );

  if (collapsed) {
    return (
      <Tooltip.Provider delayDuration={200} key={item.path}>
        <Tooltip.Root>
          <Tooltip.Trigger asChild>{link}</Tooltip.Trigger>
          <Tooltip.Portal>
            <Tooltip.Content side={isRTL ? 'left' : 'right'} align="center" sideOffset={8}>
              <div className="rounded-md bg-slate-800 px-2.5 py-1.5 text-xs text-white shadow-md">
                {t(`nav.${item.label}`)}
              </div>
              <Tooltip.Arrow className="fill-slate-800" />
            </Tooltip.Content>
          </Tooltip.Portal>
        </Tooltip.Root>
      </Tooltip.Provider>
    );
  }

  return link;
}

export function Sidebar({ collapsed, onToggleCollapsed, forceCollapsed }: SidebarProps) {
  const { t, i18n } = useTranslation();
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);
  const [mobileOpen, setMobileOpen] = useState(false);

  const isRTL = i18n.language === 'ar';
  const drawerRef = useRef<HTMLElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const visibleNavItems = user
    ? navItems.filter(item => item.roles.includes(user.role))
    : navItems;

  const isCollapsed = forceCollapsed || collapsed;

  const sidebarContent = (
    <div className={`h-full bg-slate-900 text-white flex flex-col transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'}`}>
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
        <button
          type="button"
          onClick={onToggleCollapsed}
          className="hidden lg:block text-slate-400 hover:text-white transition-colors"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-expanded={!collapsed}
        >
          {collapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
      </div>

      <div className="flex-1 py-4">
        <nav className="space-y-1 px-2" aria-label="Main navigation">
          {visibleNavItems.map((item) => (
            <NavItem key={item.path} item={item} collapsed={isCollapsed} onLinkClick={() => setMobileOpen(false)} />
          ))}
        </nav>
      </div>

      <div className="border-t border-slate-700 p-4">
        {!collapsed && user && (
          <div className="mb-3 px-3">
            <p className="text-sm font-medium text-white">{user.full_name}</p>
            <p className="text-xs text-slate-400">{user.role}</p>
          </div>
        )}
        <button
          type="button"
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 text-slate-300 hover:text-red-400 hover:bg-slate-800 rounded-lg w-full transition-colors"
          aria-label={t('app.logout')}
        >
          <LogOut size={20} />
          {!collapsed && <span className="text-sm font-medium">{t('app.logout')}</span>}
        </button>
      </div>
    </div>
  );

  const drawerClosedTransform = isRTL ? 'translate-x-full' : '-translate-x-full';

  useEffect(() => {
    if (!mobileOpen) return;

    const drawer = drawerRef.current;
    if (!drawer) return;

    const focusableSelector = 'a[href], button, [tabindex]:not([tabindex="-1"])';

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setMobileOpen(false);
        return;
      }

      if (event.key !== 'Tab') return;

      const focusableElements = drawer.querySelectorAll<HTMLElement>(focusableSelector);
      if (focusableElements.length === 0) {
        event.preventDefault();
        return;
      }

      const first = focusableElements[0];
      const last = focusableElements[focusableElements.length - 1];

      if (event.shiftKey) {
        if (document.activeElement === first || !drawer.contains(document.activeElement)) {
          event.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last || !drawer.contains(document.activeElement)) {
          event.preventDefault();
          first.focus();
        }
      }
    };

    const focusFirst = () => {
      const first = drawer.querySelector<HTMLElement>(focusableSelector);
      if (first) first.focus();
    };

    const timeoutId = setTimeout(focusFirst, 0);

    drawer.addEventListener('keydown', handleKeyDown);
    return () => {
      clearTimeout(timeoutId);
      drawer.removeEventListener('keydown', handleKeyDown);
    };
  }, [mobileOpen]);

  useEffect(() => {
    if (!mobileOpen) {
      triggerRef.current?.focus();
    }
  }, [mobileOpen]);

  return (
    <Tooltip.Provider delayDuration={200}>
      <>
        <button
          ref={triggerRef}
          type="button"
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden fixed top-4 start-4 z-50 bg-slate-900 text-white p-2 rounded-lg transition-colors"
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileOpen}
          aria-controls="mobile-drawer"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <div
          className={`md:hidden fixed inset-0 bg-black/50 z-40 transition-opacity duration-300 ${
            mobileOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
          }`}
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
        <aside
          id="mobile-drawer"
          ref={drawerRef}
          className={`md:hidden fixed inset-y-0 start-0 z-50 pointer-events-none transition-transform duration-300 ${
            mobileOpen ? 'translate-x-0' : drawerClosedTransform
          }`}
          role="dialog"
          aria-modal="true"
          aria-label="Mobile navigation"
          {...(mobileOpen ? {} : { inert: 'true' })}
        >
          <div className="pointer-events-auto h-full w-80 max-w-[85vw] overflow-y-auto">
            {sidebarContent}
          </div>
        </aside>
        <aside className="hidden md:flex md:flex-col h-screen shadow-md" aria-label="Main navigation">
          <div className="pointer-events-auto flex flex-col h-full overflow-y-auto">
            {sidebarContent}
          </div>
        </aside>
      </>
    </Tooltip.Provider>
  );
}
