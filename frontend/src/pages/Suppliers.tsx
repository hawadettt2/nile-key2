import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listSuppliers, createSupplier, updateSupplier, deleteSupplier } from '@/services/api';
import { Search, Plus, Pencil, Trash2, X } from 'lucide-react';

interface Supplier { id: number; name: string; contact_person?: string; email?: string; phone?: string; city?: string; status: string; }

export function Suppliers() {
  const { t } = useTranslation();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Supplier | null>(null);
  const [form, setForm] = useState({ name: '', name_en: '', contact_person: '', email: '', phone: '', city: '', country: 'Egypt', tax_id: '' });
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    setLoading(true);
    try { const res = await listSuppliers(search ? { search } : {}); setSuppliers(res.data || []); }
    catch { setSuppliers([]); } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try { if (editing) await updateSupplier(editing.id, form); else await createSupplier(form);
      setShowForm(false); setEditing(null); setForm({ name: '', name_en: '', contact_person: '', email: '', phone: '', city: '', country: 'Egypt', tax_id: '' }); load();
    } catch { alert('Error'); } finally { setSubmitting(false); }
  };
  const handleDelete = async (id: number) => { if (!confirm('Are you sure?')) return; try { await deleteSupplier(id); load(); } catch { alert('Error'); } };
  const openEdit = (s: Supplier) => { setEditing(s); setForm({ name: s.name, name_en: '', contact_person: s.contact_person || '', email: s.email || '', phone: s.phone || '', city: s.city || '', country: 'Egypt', tax_id: '' }); setShowForm(true); };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('supplier.title')}</h1>
        <button onClick={() => { setShowForm(true); setEditing(null); }} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors">
          <Plus size={16} /> {t('supplier.addSupplier')}</button>
      </div>
      <div className="flex gap-2 mb-4">
        <input value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && load()}
          placeholder={t('common.search')} className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
        <button onClick={load} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg transition-colors"><Search size={16} /></button>
      </div>
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{editing ? t('supplier.editSupplier') : t('supplier.addSupplier')}</h3>
            <button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
          </div>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input required value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} placeholder={t('supplier.name')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input value={form.contact_person} onChange={(e) => setForm({...form, contact_person: e.target.value})} placeholder={t('supplier.contact')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} placeholder={t('supplier.email')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input value={form.phone} onChange={(e) => setForm({...form, phone: e.target.value})} placeholder={t('supplier.phone')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input value={form.city} onChange={(e) => setForm({...form, city: e.target.value})} placeholder={t('supplier.city')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input value={form.country} onChange={(e) => setForm({...form, country: e.target.value})} placeholder={t('supplier.country')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <div className="md:col-span-2"><button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">{submitting ? 'Saving...' : t('common.save')}</button></div>
          </form>
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div> : (
          <div className="overflow-x-auto">
            <table className="w-full"><thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('supplier.name')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('supplier.contact')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('supplier.email')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('supplier.phone')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('supplier.city')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.status')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.actions')}</th>
            </tr></thead><tbody className="divide-y divide-slate-100">
              {suppliers.map((s) => (<tr key={s.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-sm font-medium text-slate-900">{s.name}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{s.contact_person || '-'}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{s.email || '-'}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{s.phone || '-'}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{s.city || '-'}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${s.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>{s.status}</span></td>
                <td className="px-4 py-3"><div className="flex gap-2"><button onClick={() => openEdit(s)} className="text-blue-600 hover:text-blue-700"><Pencil size={14} /></button><button onClick={() => handleDelete(s.id)} className="text-red-600 hover:text-red-700"><Trash2 size={14} /></button></div></td>
              </tr>))}
              {suppliers.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
            </tbody></table>
          </div>
        )}
      </div>
    </div>
  );
}
