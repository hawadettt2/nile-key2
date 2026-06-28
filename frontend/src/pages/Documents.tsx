import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listDocuments, createDocument, uploadDocument, deleteDocument } from '@/services/api';
import { Plus, Upload, Trash2, X, FileText } from 'lucide-react';

interface Document { id: number; title: string; file_name?: string; document_type: string; created_at: string; }

export function Documents() {
  const { t } = useTranslation();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', document_type: 'uploaded', content: '' });

  const load = async () => { setLoading(true); try { const res = await listDocuments(); setDocuments(res.data || []); } catch { setDocuments([]); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => { e.preventDefault(); try { await createDocument(form); setShowForm(false); setForm({ title: '', document_type: 'uploaded', content: '' }); load(); } catch { alert('Error'); } };
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => { const file = e.target.files?.[0]; if (!file) return; try { await uploadDocument(file); load(); } catch { alert('Error'); } };
  const handleDelete = async (id: number) => { if (!confirm('Delete?')) return; try { await deleteDocument(id); load(); } catch { alert('Error'); } };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('document.title')}</h1>
        <div className="flex gap-2">
          <label className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium cursor-pointer transition-colors"><Upload size={16} /> {t('document.upload')}<input type="file" accept=".pdf,.jpg,.png" onChange={handleUpload} className="hidden" /></label>
          <button onClick={() => setShowForm(true)} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Plus size={16} /> {t('common.add')}</button>
        </div>
      </div>
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">Create Document</h3><button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input required value={form.title} onChange={(e) => setForm({...form, title: e.target.value})} placeholder="Title" className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <select value={form.document_type} onChange={(e) => setForm({...form, document_type: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm"><option value="uploaded">Uploaded</option><option value="template">Template</option><option value="generated">Generated</option></select>
            <div className="md:col-span-2"><button type="submit" className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">{t('common.save')}</button></div>
          </form>
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
            </tr></thead><tbody className="divide-y divide-slate-100">
              {documents.map((d) => (<tr key={d.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-sm font-medium text-slate-900 flex items-center gap-2"><FileText size={14} className="text-slate-400" />{d.title}</td>
                <td className="px-4 py-3 text-sm text-slate-600"><span className={`px-2 py-1 rounded-full text-xs font-medium ${d.document_type === 'template' ? 'bg-purple-100 text-purple-700' : 'bg-slate-100 text-slate-600'}`}>{d.document_type}</span></td>
                <td className="px-4 py-3 text-sm text-slate-600">{d.file_name || '-'}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{new Date(d.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3"><button onClick={() => handleDelete(d.id)} className="text-red-600 hover:text-red-700"><Trash2 size={14} /></button></td>
              </tr>))}
              {documents.length === 0 && <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
            </tbody></table>
          </div>
        )}
      </div>
    </div>
  );
}
