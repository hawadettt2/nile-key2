import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listResources, searchResources, createResource, deleteResource, getResource, updateResource } from '@/services/api';
import { Search, Plus, Trash2, X, Globe, Edit3 } from 'lucide-react';

interface Resource { id: number; title: string; resource_type: string; category?: string; country?: string; url?: string; is_active: number; }

export function Resources() {
  const { t } = useTranslation();
  const [resources, setResources] = useState<Resource[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', title_ar: '', description: '', resource_type: 'guide', category: '', url: '', country: '' });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editLoading, setEditLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selectedItem, setSelectedItem] = useState<Resource | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const load = async () => { setLoading(true); try { const res = await listResources(); setResources(res.data || []); } catch { setResources([]); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);

  const handleSearch = async () => { if (!search) { load(); return; } try { const res = await searchResources(search); setResources(res.data || []); } catch { /* silent */ } };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      if (editingId) {
        await updateResource(editingId, form);
      } else {
        await createResource(form);
      }
      setEditingId(null);
      setShowForm(false);
      setForm({ title: '', title_ar: '', description: '', resource_type: 'guide', category: '', url: '', country: '' });
      load();
    } catch { alert('Error'); }
    setSubmitting(false);
  };
  const handleDelete = async (id: number) => { if (!confirm('Delete?')) return; try { await deleteResource(id); load(); } catch { alert('Error'); } };
  const openEdit = async (id: number) => {
    setEditLoading(true);
    try {
      const res = await getResource(id);
      const doc = res.data;
      setForm({ title: doc.title || '', title_ar: doc.title_ar || '', description: doc.description || '', resource_type: doc.resource_type || 'guide', category: doc.category || '', url: doc.url || '', country: doc.country || '' });
      setEditingId(id);
      setShowForm(true);
    } catch { alert('Error loading resource'); }
    setEditLoading(false);
  };
  const cancelEdit = () => { setEditingId(null); setForm({ title: '', title_ar: '', description: '', resource_type: 'guide', category: '', url: '', country: '' }); setShowForm(false); };

  const openDetails = async (id: number) => {
    setDetailLoading(true);
    setShowDetails(true);
    try {
      const res = await getResource(id);
      setSelectedItem(res.data);
      setSelectedId(id);
    } catch { alert('Error loading resource'); }
    setDetailLoading(false);
  };
  const closeDetails = () => { setShowDetails(false); setSelectedItem(null); setSelectedId(null); };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('resource.title')}</h1>
        <button onClick={() => { setEditingId(null); setForm({ title: '', title_ar: '', description: '', resource_type: 'guide', category: '', url: '', country: '' }); setShowForm(true); }} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Plus size={16} /> {t('common.add')}</button>
      </div>
      <div className="flex gap-2 mb-4">
        <input value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSearch()} placeholder={t('common.search')} className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
        <button onClick={handleSearch} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg transition-colors"><Search size={16} /></button>
      </div>
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">{editingId ? t('resource.editResource') : t('resource.addResource')}</h3><button onClick={cancelEdit} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          {editLoading ? <div className="text-sm text-slate-500">Loading...</div> : (
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input required value={form.title} onChange={(e) => setForm({...form, title: e.target.value})} placeholder={t('resource.fieldTitle')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <select value={form.resource_type} onChange={(e) => setForm({...form, resource_type: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm"><option value="guide">Guide</option><option value="regulation">Regulation</option><option value="opportunity">Opportunity</option><option value="contact">Contact</option></select>
              <input value={form.category} onChange={(e) => setForm({...form, category: e.target.value})} placeholder={t('resource.category')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <input value={form.url} onChange={(e) => setForm({...form, url: e.target.value})} placeholder={t('resource.url')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <input value={form.country} onChange={(e) => setForm({...form, country: e.target.value})} placeholder={t('resource.country')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <div className="md:col-span-2"><button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">{submitting ? 'Saving...' : (editingId ? 'Update' : t('common.save'))}</button></div>
            </form>
          )}
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {resources.map((r) => (
          <div key={r.id} className="bg-white rounded-xl p-5 shadow-sm border border-slate-100 hover:shadow-md transition-shadow cursor-pointer" onClick={() => openDetails(r.id)}>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2"><div className="p-2 bg-emerald-100 rounded-lg"><Globe size={16} className="text-emerald-600" /></div><span className="px-2 py-1 bg-slate-100 rounded-full text-xs font-medium text-slate-600">{r.resource_type}</span></div>
              <div className="flex gap-2" onClick={(e) => e.stopPropagation()}><button onClick={() => openEdit(r.id)} className="text-slate-400 hover:text-emerald-600"><Edit3 size={14} /></button><button onClick={() => handleDelete(r.id)} className="text-slate-400 hover:text-red-600"><Trash2 size={14} /></button></div>
            </div>
            <h3 className="mt-3 font-semibold text-slate-900">{r.title}</h3>
            <p className="text-sm text-slate-500 mt-1">{r.category} {r.country ? `• ${r.country}` : ''}</p>
            {r.url && <a href={r.url} target="_blank" rel="noopener noreferrer" className="text-sm text-emerald-600 hover:text-emerald-700 mt-2 inline-block">Visit →</a>}
          </div>
        ))}
        {resources.length === 0 && !loading && <div className="md:col-span-3 text-center py-12 text-sm text-slate-500">{t('common.noData')}</div>}
      </div>
      {showDetails && selectedId != null && selectedItem && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 max-w-lg w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">{t('resource.details')}</h3>
              <button onClick={closeDetails} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            {detailLoading ? <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-600" /></div> : (
              <div className="space-y-3">
                <div><span className="text-sm font-medium text-slate-500">{t('resource.fieldTitle')}</span><p className="text-sm text-slate-900">{selectedItem.title}</p></div>
                <div><span className="text-sm font-medium text-slate-500">{t('resource.type')}</span><p className="text-sm text-slate-900">{selectedItem.resource_type}</p></div>
                <div><span className="text-sm font-medium text-slate-500">{t('resource.category')}</span><p className="text-sm text-slate-900">{selectedItem.category || '-'}</p></div>
                <div><span className="text-sm font-medium text-slate-500">{t('resource.country')}</span><p className="text-sm text-slate-900">{selectedItem.country || '-'}</p></div>
                <div><span className="text-sm font-medium text-slate-500">{t('resource.url')}</span><p className="text-sm text-slate-900">{selectedItem.url ? <a href={selectedItem.url} target="_blank" rel="noopener noreferrer" className="text-emerald-600 hover:text-emerald-700">{selectedItem.url}</a> : '-'}</p></div>
                <div><span className="text-sm font-medium text-slate-500">{t('resource.status')}</span><p className="text-sm text-slate-900">{selectedItem.is_active ? 'Active' : 'Inactive'}</p></div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
