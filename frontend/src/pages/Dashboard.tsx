import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/store/authStore';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';
import { listSuppliers, listCustomers, listShipments, listInvoices } from '@/services/api';
import { Truck, Users, UserCheck, FileText, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#059669', '#0891b2', '#d97706', '#dc2626', '#7c3aed'];

export function Dashboard() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const [stats, setStats] = useState({ suppliers: 0, customers: 0, shipments: 0, invoices: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const [supRes, custRes, shipRes, invRes] = await Promise.all([
          listSuppliers(), listCustomers(), listShipments(), listInvoices()
        ]);
        setStats({
          suppliers: supRes.data?.length || 0, customers: custRes.data?.length || 0,
          shipments: shipRes.data?.length || 0, invoices: invRes.data?.length || 0
        });
      } catch { /* silent */ } finally { setLoading(false); }
    }
    loadStats();
  }, []);

  const statCards = [
    { label: t('dashboard.totalSuppliers'), value: stats.suppliers, icon: Truck, color: 'bg-emerald-100 text-emerald-700' },
    { label: t('dashboard.totalCustomers'), value: stats.customers, icon: Users, color: 'bg-cyan-100 text-cyan-700' },
    { label: t('dashboard.activeShipments'), value: stats.shipments, icon: UserCheck, color: 'bg-amber-100 text-amber-700' },
    { label: t('dashboard.totalInvoices'), value: stats.invoices, icon: FileText, color: 'bg-rose-100 text-rose-700' },
  ];
  const chartData = [
    { name: t('nav.suppliers'), value: stats.suppliers },
    { name: t('nav.customers'), value: stats.customers },
    { name: t('nav.shipments'), value: stats.shipments },
    { name: t('nav.invoices'), value: stats.invoices },
  ];
  const barData = [
    { month: 'Jan', shipments: 4, invoices: 3 }, { month: 'Feb', shipments: 6, invoices: 5 },
    { month: 'Mar', shipments: 8, invoices: 7 }, { month: 'Apr', shipments: 5, invoices: 6 },
    { month: 'May', shipments: 9, invoices: 8 }, { month: 'Jun', shipments: 7, invoices: 9 },
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
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">{t('common.overview')}</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={barData}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} /><YAxis stroke="#64748b" fontSize={12} /><Tooltip />
                <Bar dataKey="shipments" fill="#059669" radius={[4, 4, 0, 0]} /><Bar dataKey="invoices" fill="#0891b2" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">{t('common.overview')}</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart><Pie data={chartData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                {chartData.map((_e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie><Tooltip /></PieChart>
            </ResponsiveContainer>
            <div className="flex flex-wrap justify-center gap-4 mt-2">
              {chartData.map((e, i) => (<div key={e.name} className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i] }} /><span className="text-xs text-slate-600">{e.name}</span>
              </div>))}
            </div>
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
