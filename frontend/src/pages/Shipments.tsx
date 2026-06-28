import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listShipments, createShipment, updateShipment, getShippingRates } from '@/services/api';
import { Plus, Pencil, X, Calculator } from 'lucide-react';

interface Shipment { id: number; tracking_number: string; origin: string; destination: string; carrier?: string; status: string; }
interface ShippingRate { carrier: string; service: string; cost: number; estimated_days: number; currency: string; }

export function Shipments() {
  const { t } = useTranslation();
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showRates, setShowRates] = useState(false);
  const [editing, setEditing] = useState<Shipment | null>(null);
  const [rates, setRates] = useState<ShippingRate[]>([]);
  const [form, setForm] = useState({ origin: '', destination: '', carrier: '', service_type: '', weight: 0, weight_unit: 'kg', value: 0, currency: 'USD', items_count: 1, description: '', reference: '' });
  const [rateForm, setRateForm] = useState({ origin: '', destination: '', weight: 1, weight_unit: 'kg' });

  const load = async () => { setLoading(true); try { const res = await listShipments(); setShipments(res.data || []); } catch { setShipments([]); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => { e.preventDefault(); try { if (editing) await updateShipment(editing.id, form); else await createShipment(form); setShowForm(false); setEditing(null); setForm({ origin: '', destination: '', carrier: '', service_type: '', weight: 0, weight_unit: 'kg', value: 0, currency: 'USD', items_count: 1, description: '', reference: '' }); load(); } catch { alert('Error'); } };
  const handleGetRates = async () => { try { const res = await getShippingRates(rateForm); setRates(res.data || []); } catch { alert('Error'); } };
  const openEdit = (s: Shipment) => { setEditing(s); setForm({ origin: s.origin, destination: s.destination, carrier: s.carrier || '', service_type: '', weight: 0, weight_unit: 'kg', value: 0, currency: 'USD', items_count: 1, description: '', reference: '' }); setShowForm(true); };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('shipment.title')}</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowRates(true)} className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Calculator size={16} /> {t('shipment.getRates')}</button>
          <button onClick={() => { setShowForm(true); setEditing(null); }} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Plus size={16} /> {t('shipment.addShipment')}</button>
        </div>
      </div>
      {showRates && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">{t('shipment.getRates')}</h3><button onClick={() => { setShowRates(false); setRates([]); }} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          <div className="flex gap-2 mb-4">
            <input value={rateForm.origin} onChange={(e) => setRateForm({...rateForm, origin: e.target.value})} placeholder={t('shipment.origin')} className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input value={rateForm.destination} onChange={(e) => setRateForm({...rateForm, destination: e.target.value})} placeholder={t('shipment.destination')} className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input type="number" value={rateForm.weight} onChange={(e) => setRateForm({...rateForm, weight: Number(e.target.value)})} placeholder={t('shipment.weight')} className="w-24 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <button onClick={handleGetRates} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm font-medium">{t('shipment.getRates')}</button>
          </div>
          {rates.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {rates.map((r, i) => (<div key={i} className="border border-slate-200 rounded-lg p-4">
                <div className="flex items-center justify-between"><span className="font-semibold text-slate-900">{r.carrier}</span><span className="text-emerald-600 font-bold">${r.cost}</span></div>
                <p className="text-sm text-slate-500 mt-1">{r.service} — {r.estimated_days} days</p>
              </div>))}
            </div>
          )}
        </div>
      )}
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">{editing ? t('common.edit') : t('shipment.addShipment')}</h3><button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input required value={form.origin} onChange={(e) => setForm({...form, origin: e.target.value})} placeholder={t('shipment.origin')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input required value={form.destination} onChange={(e) => setForm({...form, destination: e.target.value})} placeholder={t('shipment.destination')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input value={form.carrier} onChange={(e) => setForm({...form, carrier: e.target.value})} placeholder={t('shipment.carrier')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input type="number" value={form.weight} onChange={(e) => setForm({...form, weight: Number(e.target.value)})} placeholder={t('shipment.weight')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input type="number" value={form.value} onChange={(e) => setForm({...form, value: Number(e.target.value)})} placeholder={t('shipment.value')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} placeholder="Description" className="md:col-span-2 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <div className="md:col-span-2"><button type="submit" className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">{t('common.save')}</button></div>
          </form>
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div> : (
          <div className="overflow-x-auto">
            <table className="w-full"><thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('shipment.tracking')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('shipment.origin')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('shipment.destination')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('shipment.carrier')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.status')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.actions')}</th>
            </tr></thead><tbody className="divide-y divide-slate-100">
              {shipments.map((s) => (<tr key={s.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-sm font-mono text-slate-900">{s.tracking_number}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{s.origin}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{s.destination}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{s.carrier || '-'}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${s.status === 'delivered' ? 'bg-emerald-100 text-emerald-700' : s.status === 'in_transit' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>{s.status}</span></td>
                <td className="px-4 py-3"><div className="flex gap-2"><button onClick={() => openEdit(s)} className="text-blue-600 hover:text-blue-700"><Pencil size={14} /></button></div></td>
              </tr>))}
              {shipments.length === 0 && <tr><td colSpan={6} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
            </tbody></table>
          </div>
        )}
      </div>
    </div>
  );
}
