import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listDocuments, createDocument, uploadDocument, deleteDocument, getDocument, updateDocument } from '@/services/api';
import { Plus, Upload, Trash2, X, FileText, Edit3 } from 'lucide-react';

interface Document { id: number; title: string; file_name?: string; document_type: string; created_at: string; content?: string; }

export function Documents() {
  const { t } = useTranslation();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', document_type: 'uploaded', content: '' });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editLoading, setEditLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selectedItem, setSelectedItem] = useState<Document | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const load = async () => { setLoading(true); try { const res = await listDocuments(); setDocuments(res.data || []); } catch { setDocuments([]); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      if (editingId) {
        await updateDocument(editingId, form);
      } else {
        await createDocument(form);
      }
      setEditingId(null);
      setShowForm(false);
      setForm({ title: '', document_type: 'uploaded', content: '' });
      load();
    } catch { alert('Error'); }
    setSubmitting(false);
  };
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => { const file = e.target.files?.[0]; if (!file) return; try { await uploadDocument(file); load(); } catch { alert('Error'); } };
  const handleDelete = async (id: number) => { if (!confirm('Delete?')) return; try { await deleteDocument(id); load(); } catch { alert('Error'); } };
  const openEdit = async (id: number) => {
    setEditLoading(true);
    try {
      const res = await getDocument(id);
      const doc = res.data;
      setForm({ title: doc.title || '', document_type: doc.document_type || 'uploaded', content: doc.content || '' });
      setEditingId(id);
      setShowForm(true);
    } catch { alert('Error loading document'); }
    setEditLoading(false);
  };
  const cancelEdit = () => { setEditingId(null); setForm({ title: '', document_type: 'uploaded', content: '' }); setShowForm(false); };

  const openDetails = async (id: number) => {
    setDetailLoading(true);
    setShowDetails(true);
    try {
      const res = await getDocument(id);
      setSelectedItem(res.data);
      setSelectedId(id);
    } catch { alert('Error loading document'); }
    setDetailLoading(false);
  };
  const closeDetails = () => { setShowDetails(false); setSelectedItem(null); setSelectedId(null); };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('document.title')}</h1>
        <div className="flex gap-2">
          <label className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium cursor-pointer transition-colors"><Upload size={16} /> {t('document.upload')}<input type="file" accept=".pdf,.jpg,.png" onChange={handleUpload} className="hidden" /></label>
          <button onClick={() => { setEditingId(null); setForm({ title: '', document_type: 'uploaded', content: '' }); setShowForm(true); }} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Plus size={16} /> {t('common.add')}</button>
        </div>
      </div>
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">{editingId ? 'Edit Document' : 'Create Document'}</h3><button onClick={cancelEdit} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          {editLoading ? <div className="text-sm text-slate-500">Loading...</div> : (
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input required value={form.title} onChange={(e) => setForm({...form, title: e.target.value})} placeholder="Title" className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <select value={form.document_type} onChange={(e) => setForm({...form, document_type: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm"><option value="uploaded">Uploaded</option><option value="template">Template</option><option value="generated">Generated</option></select>
              <div className="md:col-span-2"><button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">{submitting ? 'Saving...' : (editingId ? 'Update' : t('common.save'))}</button></div>
            </form>
          )}
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div> : (
          <div className="overflow-x-auto">
            <table className="w-full"><thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Title</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('document.type')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">File</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Date</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.actions')}</th>
            </tr></thead>            <tbody className="divide-y divide-slate-100">
              {documents.map((d) => (<tr key={d.id} className="hover:bg-slate-50 transition-colors cursor-pointer" onClick={() => openDetails(d.id)}>
                <td className="px-4 py-3 text-sm font-medium text-slate-900 flex items-center gap-2"><FileText size={14} className="text-slate-400" />{d.title}</td>
                <td className="px-4 py-3 text-sm text-slate-600"><span className={`px-2 py-1 rounded-full text-xs font-medium ${d.document_type === 'template' ? 'bg-purple-100 text-purple-700' : 'bg-slate-100 text-slate-600'}`}>{d.document_type}</span></td>
                <td className="px-4 py-3 text-sm text-slate-600">{d.file_name || '-'}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{new Date(d.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}><div className="flex gap-2"><button onClick={() => openEdit(d.id)} className="text-emerald-600 hover:text-emerald-700"><Edit3 size={14} /></button><button onClick={() => handleDelete(d.id)} className="text-red-600 hover:text-red-700"><Trash2 size={14} /></button></div></td>
              </tr>))}
              {documents.length === 0 && <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
            </tbody></table>
          </div>
        )}
      </div>
      {showDetails && selectedId != null && selectedItem && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 max-w-lg w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Document Details</h3>
              <button onClick={closeDetails} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            {detailLoading ? <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-600" /></div> : (
              <div className="space-y-3">
                <div><span className="text-sm font-medium text-slate-500">Title</span><p className="text-sm text-slate-900">{selectedItem.title}</p></div>
                <div><span className="text-sm font-medium text-slate-500">Type</span><p className="text-sm text-slate-900">{selectedItem.document_type}</p></div>
                <div><span className="text-sm font-medium text-slate-500">File Name</span><p className="text-sm text-slate-900">{selectedItem.file_name || '-'}</p></div>
                <div><span className="text-sm font-medium text-slate-500">Created At</span><p className="text-sm text-slate-900">{new Date(selectedItem.created_at).toLocaleString()}</p></div>
                {selectedItem.content && <div><span className="text-sm font-medium text-slate-500">Content</span><p className="text-sm text-slate-900 whitespace-pre-wrap">{selectedItem.content}</p></div>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
