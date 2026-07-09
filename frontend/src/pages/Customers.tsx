import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listCustomers, createCustomer, updateCustomer, deleteCustomer, importCustomers } from '@/services/api';
import { Search, Plus, Pencil, Trash2, X, Upload } from 'lucide-react';

interface Customer { id: number; name: string; contact_person?: string; email?: string; country: string; category?: string; status: string; }

export function Customers() {
  const { t } = useTranslation();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Customer | null>(null);
  const [form, setForm] = useState({ name: '', contact_person: '', email: '', phone: '', city: '', country: '', category: '' });
  const [submitting, setSubmitting] = useState(false);

  const load = async () => { setLoading(true); try { const res = await listCustomers(search ? { search } : {}); setCustomers(res.data || []); } catch { setCustomers([]); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      if (editing) await updateCustomer(editing.id, form); else await createCustomer(form);
      setShowForm(false); setEditing(null); setForm({ name: '', contact_person: '', email: '', phone: '', city: '', country: '', category: '' }); load();
    } catch { alert('Error'); } finally { setSubmitting(false); }
  };
  const handleDelete = async (id: number) => { if (!confirm('Sure?')) return; try { await deleteCustomer(id); load(); } catch { alert('Error'); } };
  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => { const file = e.target.files?.[0]; if (!file) return; try { await importCustomers(file); load(); } catch { alert('Error'); } };
  const openEdit = (c: Customer) => { setEditing(c); setForm({ name: c.name, contact_person: c.contact_person || '', email: c.email || '', phone: c.phone || '', city: c.city || '', country: c.country, category: c.category || '' }); setShowForm(true); };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('customer.title')}</h1>
        <div className="flex gap-2">
          <label className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium cursor-pointer transition-colors">
            <Upload size={16} /> {t('customer.importCSV')}<input type="file" accept=".csv" onChange={handleImport} className="hidden" /></label>
          <button onClick={() => { setShowForm(true); setEditing(null); }} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Plus size={16} /> {t('customer.addCustomer')}</button>
        </div>
      </div>
      <div className="flex gap-2 mb-4">
        <input value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && load()} placeholder={t('common.search')} className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
        <button onClick={load} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg transition-colors"><Search size={16} /></button>
      </div>
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">{editing ? t('customer.editCustomer') : t('customer.addCustomer')}</h3><button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input required value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} placeholder={t('customer.name')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input value={form.contact_person} onChange={(e) => setForm({...form, contact_person: e.target.value})} placeholder={t('customer.contact')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} placeholder={t('customer.email')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input required value={form.country} onChange={(e) => setForm({...form, country: e.target.value})} placeholder={t('customer.country')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <div className="md:col-span-2"><button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">{submitting ? 'Saving...' : t('common.save')}</button></div>
          </form>
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div> : (
          <div className="overflow-x-auto">
            <table className="w-full"><thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.name')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.contact')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.country')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.category')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.status')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.actions')}</th>
            </tr></thead><tbody className="divide-y divide-slate-100">
              {customers.map((c) => (<tr key={c.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-sm font-medium text-slate-900">{c.name}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{c.contact_person || '-'} {c.email ? `(${c.email})` : ''}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{c.country}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{c.category || '-'}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${c.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>{c.status}</span></td>
                <td className="px-4 py-3"><div className="flex gap-2"><button onClick={() => openEdit(c)} className="text-blue-600 hover:text-blue-700"><Pencil size={14} /></button><button onClick={() => handleDelete(c.id)} className="text-red-600 hover:text-red-700"><Trash2 size={14} /></button></div></td>
              </tr>))}
              {customers.length === 0 && <tr><td colSpan={6} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
            </tbody></table>
          </div>
        )}
      </div>
    </div>
  );
}
