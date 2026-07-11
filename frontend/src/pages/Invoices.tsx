import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listInvoices, createInvoice, updateInvoice, getInvoice, validateInvoice, cancelInvoice } from '@/services/api';
import { Plus, X, CheckCircle, XCircle, Edit } from 'lucide-react';

interface Invoice { id: number; invoice_number: string; subtotal: number; tax_amount: number; total: number; currency: string; status: string; issue_date: string; items?: { description: string; quantity: number; unit_price: number; total: number }[]; }

export function Invoices() {
  const { t } = useTranslation();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selectedItem, setSelectedItem] = useState<Invoice | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [form, setForm] = useState({ subtotal: 0, tax_rate: 14, currency: 'EGP', issue_date: '', due_date: '', notes: '', items: [{ description: '', quantity: 1, unit_price: 0, total: 0 }] });

  const load = async () => { setLoading(true); try { const res = await listInvoices(); setInvoices(res.data || []); } catch { setInvoices([]); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);

  const openEdit = (invoice: Invoice) => {
    setEditingId(invoice.id);
    setForm({ subtotal: invoice.subtotal, tax_rate: 14, currency: invoice.currency, issue_date: invoice.issue_date, due_date: '', notes: '', items: invoice.items || [] });
    setShowForm(true);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm({ subtotal: 0, tax_rate: 14, currency: 'EGP', issue_date: '', due_date: '', notes: '', items: [{ description: '', quantity: 1, unit_price: 0, total: 0 }] });
    setShowForm(false);
  };

  const openDetails = async (id: number) => {
    setDetailLoading(true);
    setShowDetails(true);
    try {
      const res = await getInvoice(id);
      setSelectedItem(res.data);
      setSelectedId(id);
    } catch { alert('Error loading invoice'); }
    setDetailLoading(false);
  };
  const closeDetails = () => { setShowDetails(false); setSelectedItem(null); setSelectedId(null); };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      if (editingId != null) {
        await updateInvoice(editingId, { ...form, total, items: form.items.map(i => ({ ...i, total: i.quantity * i.unit_price })) });
      } else {
        await createInvoice({ ...form, total, items: form.items.map(i => ({ ...i, total: i.quantity * i.unit_price })) });
      }
      setEditingId(null);
      setForm({ subtotal: 0, tax_rate: 14, currency: 'EGP', issue_date: '', due_date: '', notes: '', items: [{ description: '', quantity: 1, unit_price: 0, total: 0 }] });
      setShowForm(false);
      load();
    } catch {
      alert('Error');
    } finally {
      setSubmitting(false);
    }
  };
  const handleValidate = async (id: number) => { try { await validateInvoice(id); load(); } catch { alert('Error'); } };
  const handleCancel = async (id: number) => { if (!confirm('Cancel?')) return; try { await cancelInvoice(id); load(); } catch { alert('Error'); } };
  const addItem = () => setForm({ ...form, items: [...form.items, { description: '', quantity: 1, unit_price: 0, total: 0 }] });
  const updateItem = (i: number, field: string, value: string | number) => { const items = [...form.items]; items[i] = { ...items[i], [field]: value }; if (field === 'quantity' || field === 'unit_price') items[i].total = items[i].quantity * items[i].unit_price; setForm({ ...form, items }); };
  const total = form.items.reduce((s, i) => s + i.total, 0);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('invoice.title')}</h1>
        <button onClick={() => setShowForm(true)} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Plus size={16} /> {t('invoice.addInvoice')}</button>
      </div>
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{editingId ? t('invoice.editInvoice') : t('invoice.addInvoice')}</h3>
            <button onClick={cancelEdit} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input type="date" required value={form.issue_date} onChange={(e) => setForm({...form, issue_date: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <input type="date" value={form.due_date} onChange={(e) => setForm({...form, due_date: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <input type="number" value={form.subtotal} onChange={(e) => setForm({...form, subtotal: Number(e.target.value)})} placeholder={t('invoice.subtotal')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-slate-700">{t('invoice.items')}</h4>
                <button type="button" onClick={addItem} className="text-xs text-emerald-600 hover:text-emerald-700 font-medium">{t('invoice.addItem')}</button>
              </div>
              {form.items.map((item, i) => (<div key={i} className="grid grid-cols-4 gap-2">
                <input value={item.description} onChange={(e) => updateItem(i, 'description', e.target.value)} placeholder={t('invoice.description')} className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
                <input type="number" value={item.quantity} onChange={(e) => updateItem(i, 'quantity', Number(e.target.value))} placeholder={t('invoice.quantity')} className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
                <input type="number" value={item.unit_price} onChange={(e) => updateItem(i, 'unit_price', Number(e.target.value))} placeholder={t('invoice.price')} className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
                <div className="px-3 py-2 bg-slate-50 rounded-lg text-sm font-medium text-slate-700">{item.total.toFixed(2)}</div>
              </div>))}
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-slate-200">
              <span className="text-sm text-slate-600">Total: <span className="font-bold text-slate-900">{total.toFixed(2)}</span></span>
              <button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50">{submitting ? t('common.saving') : editingId ? t('common.update') : t('common.save')}</button>
            </div>
          </form>
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.number')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.subtotal')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.tax')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.total')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.issueDate')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.status')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.actions')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {invoices.map((inv) => (<tr key={inv.id} className="hover:bg-slate-50 transition-colors cursor-pointer" onClick={() => openDetails(inv.id)}>
                  <td className="px-4 py-3 text-sm font-mono font-medium text-slate-900">{inv.invoice_number}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{inv.subtotal.toFixed(2)}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{inv.tax_amount?.toFixed(2) || '0.00'}</td>
                  <td className="px-4 py-3 text-sm font-medium text-slate-900">{inv.total.toFixed(2)} {inv.currency}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{inv.issue_date}</td>
                  <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${inv.status === 'validated' ? 'bg-emerald-100 text-emerald-700' : inv.status === 'cancelled' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>{inv.status}</span></td>
                  <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                    <div className="flex gap-2">
                      {inv.status === 'draft' && <button onClick={() => handleValidate(inv.id)} className="text-emerald-600 hover:text-emerald-700"><CheckCircle size={16} /></button>}
                      {inv.status === 'draft' && <button onClick={() => openEdit(inv)} className="text-slate-600 hover:text-slate-900"><Edit size={16} /></button>}
                      {inv.status !== 'cancelled' && <button onClick={() => handleCancel(inv.id)} className="text-red-600 hover:text-red-700"><XCircle size={16} /></button>}
                    </div>
                  </td>
                </tr>))}
                {invoices.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {showDetails && selectedId != null && selectedItem && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 max-w-lg w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">{t('invoice.details')}</h3>
              <button onClick={closeDetails} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            {detailLoading ? <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-600" /></div> : (
              <div className="space-y-3">
                <div><span className="text-sm font-medium text-slate-500">{t('invoice.invoiceNumber')}</span><p className="text-sm text-slate-900 font-mono">{selectedItem.invoice_number}</p></div>
                <div className="grid grid-cols-2 gap-3">
                  <div><span className="text-sm font-medium text-slate-500">Subtotal</span><p className="text-sm text-slate-900">{selectedItem.subtotal.toFixed(2)}</p></div>
                  <div><span className="text-sm font-medium text-slate-500">Tax</span><p className="text-sm text-slate-900">{selectedItem.tax_amount?.toFixed(2) || '0.00'}</p></div>
                  <div><span className="text-sm font-medium text-slate-500">Total</span><p className="text-sm text-slate-900 font-semibold">{selectedItem.total.toFixed(2)} {selectedItem.currency}</p></div>
                  <div><span className="text-sm font-medium text-slate-500">Status</span><p className="text-sm text-slate-900">{selectedItem.status}</p></div>
                  <div><span className="text-sm font-medium text-slate-500">Issue Date</span><p className="text-sm text-slate-900">{selectedItem.issue_date}</p></div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
