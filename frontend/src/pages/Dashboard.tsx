import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/store/authStore';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';
import { getDashboard } from '@/services/api';
import { Truck, Users, UserCheck, FileText, TrendingUp, Bell, Activity } from 'lucide-react';

interface DashboardStats {
  suppliers: number;
  customers: number;
  shipments: number;
  invoices: number;
  customs_declarations: number;
  documents: number;
  resources: number;
  eta_connectors: number;
}

interface DashboardTimeline {
  recent_activities: Array<{ action: string; entity_type: string; details: string; created_at: string }>;
  upcoming_shipments: Array<{ id: number; tracking_number: string; status: string; origin: string; destination: string; eta?: string }>;
  pending_invoices: Array<{ id: number; invoice_number: string; status: string; total?: number; currency?: string }>;
}

interface DashboardResponse {
  stats: DashboardStats;
  timeline: DashboardTimeline;
  notifications_count: number;
}

const POLL_INTERVAL_MS = 30000;

export function Dashboard() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    try {
      const res = await getDashboard();
      setDashboard(res.data as DashboardResponse);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    const timer = setInterval(loadDashboard, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [loadDashboard]);

  const stats = dashboard?.stats;
  const notificationsCount = dashboard?.notifications_count || 0;
  const recentActivities = dashboard?.timeline?.recent_activities || [];
  const upcomingShipments = dashboard?.timeline?.upcoming_shipments || [];

  const statCards = [
    { label: t('dashboard.totalSuppliers'), value: stats?.suppliers || 0, icon: Truck, color: 'bg-emerald-100 text-emerald-700' },
    { label: t('dashboard.totalCustomers'), value: stats?.customers || 0, icon: Users, color: 'bg-cyan-100 text-cyan-700' },
    { label: t('dashboard.activeShipments'), value: stats?.shipments || 0, icon: UserCheck, color: 'bg-amber-100 text-amber-700' },
    { label: t('dashboard.totalInvoices'), value: stats?.invoices || 0, icon: FileText, color: 'bg-rose-100 text-rose-700' },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-slate-900">{t('common.welcome')}, {user?.full_name || 'User'}!</h1>
          <p className="text-slate-500 text-sm mt-1">{t('dashboard.title')}</p></div>
        <LanguageSwitcher />
      </div>
      {loading ? (
        <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 rounded-xl p-4 text-sm">{error}</div>
      ) : (<>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statCards.map((card) => (
            <div key={card.label} className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
              <div className="flex items-center justify-between">
                <div><p className="text-sm text-slate-500">{card.label}</p><p className="text-2xl font-bold text-slate-900 mt-1">{card.value}</p></div>
                <div className={`p-3 rounded-lg ${card.color}`}><card.icon size={24} /></div>
              </div>
            </div>
          ))}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
            <div className="flex items-center justify-between">
              <div><p className="text-sm text-slate-500">{t('dashboard.notifications')}</p><p className="text-2xl font-bold text-slate-900 mt-1">{notificationsCount}</p></div>
              <div className="p-3 rounded-lg bg-violet-100 text-violet-700"><Bell size={24} /></div>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2"><Activity size={20} /> {t('dashboard.recentActivity')}</h3>
            {recentActivities.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">{t('dashboard.noAnalytics')}</p>
            ) : (
              <ul className="space-y-3">
                {recentActivities.slice(0, 8).map((item, idx) => (
                  <li key={idx} className="text-sm text-slate-700 border-b border-slate-100 pb-2 last:border-0">
                    <span className="font-medium capitalize">{item.action}</span> — {item.entity_type}
                    <span className="text-slate-500"> — {item.details}</span>
                    <div className="text-xs text-slate-400 mt-1">{new Date(item.created_at).toLocaleString()}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">{t('dashboard.upcomingShipments')}</h3>
            {upcomingShipments.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">{t('dashboard.noAnalytics')}</p>
            ) : (
              <ul className="space-y-3">
                {upcomingShipments.slice(0, 8).map((item) => (
                  <li key={item.id} className="text-sm text-slate-700 border-b border-slate-100 pb-2 last:border-0">
                    <span className="font-medium">{item.tracking_number}</span>
                    <span className="text-slate-500"> — {item.origin} → {item.destination}</span>
                    <div className="text-xs text-slate-400 mt-1 capitalize">{item.status}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <div className="bg-gradient-to-r from-emerald-600 to-cyan-600 rounded-xl p-6 text-white">
          <div className="flex items-center gap-3">
            <TrendingUp size={28} />
            <div><h3 className="text-lg font-semibold">Nile Key Platform v1.0</h3>
              <p className="text-emerald-100 text-sm">Your digital gateway for Egyptian exports.</p></div>
          </div>
        </div>
      </>)}
    </div>
  );
}
