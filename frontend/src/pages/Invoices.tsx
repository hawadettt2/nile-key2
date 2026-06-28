import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listInvoices, createInvoice, validateInvoice, cancelInvoice } from '@/services/api';
import { Plus, X, CheckCircle, XCircle } from 'lucide-react';

interface Invoice { id: number; invoice_number: string; subtotal: number; tax_amount: number; total: number; currency: string; status: string; issue_date: string; }

export function Invoices() {
  const { t } = useTranslation();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ subtotal: 0, tax_rate: 14, currency: 'EGP', issue_date: '', due_date: '', notes: '', items: [{ description: '', quantity: 1, unit_price: 0, total: 0 }] });

  const load = async () => { setLoading(true); try { const res = await listInvoices(); setInvoices(res.data || []); } catch { setInvoices([]); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try { await createInvoice({ ...form, items: form.items.map(i => ({ ...i, total: i.quantity * i.unit_price })) }); setShowForm(false); setForm({ subtotal: 0, tax_rate: 14, currency: 'EGP', issue_date: '', due_date: '', notes: '', items: [{ description: '', quantity: 1, unit_price: 0, total: 0 }] }); load(); } catch { alert('Error'); }
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
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">{t('invoice.addInvoice')}</h3><button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input type="date" required value={form.issue_date} onChange={(e) => setForm({...form, issue_date: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <input type="date" value={form.due_date} onChange={(e) => setForm({...form, due_date: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
              <input type="number" value={form.subtotal} onChange={(e) => setForm({...form, subtotal: Number(e.target.value)})} placeholder={t('invoice.subtotal')} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between"><h4 className="text-sm font-semibold text-slate-700">Items</h4><button type="button" onClick={addItem} className="text-xs text-emerald-600 hover:text-emerald-700 font-medium">+ Add Item</button></div>
              {form.items.map((item, i) => (<div key={i} className="grid grid-cols-4 gap-2">
                <input value={item.description} onChange={(e) => updateItem(i, 'description', e.target.value)} placeholder="Description" className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
                <input type="number" value={item.quantity} onChange={(e) => updateItem(i, 'quantity', Number(e.target.value))} placeholder="Qty" className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
                <input type="number" value={item.unit_price} onChange={(e) => updateItem(i, 'unit_price', Number(e.target.value))} placeholder="Price" className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
                <div className="px-3 py-2 bg-slate-50 rounded-lg text-sm font-medium text-slate-700">{item.total.toFixed(2)}</div>
              </div>))}
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-slate-200">
              <span className="text-sm text-slate-600">Total: <span className="font-bold text-slate-900">{total.toFixed(2)}</span></span>
              <button type="submit" className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">{t('common.save')}</button>
            </div>
          </form>
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div> : (
          <div className="overflow-x-auto">
            <table className="w-full"><thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.number')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.subtotal')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.tax')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.total')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('invoice.issueDate')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.status')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.actions')}</th>
            </tr></thead><tbody className="divide-y divide-slate-100">
              {invoices.map((inv) => (<tr key={inv.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-sm font-mono font-medium text-slate-900">{inv.invoice_number}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{inv.subtotal.toFixed(2)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{inv.tax_amount?.toFixed(2) || '0.00'}</td>
                <td className="px-4 py-3 text-sm font-medium text-slate-900">{inv.total.toFixed(2)} {inv.currency}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{inv.issue_date}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${inv.status === 'validated' ? 'bg-emerald-100 text-emerald-700' : inv.status === 'cancelled' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>{inv.status}</span></td>
                <td className="px-4 py-3"><div className="flex gap-2">
                  {inv.status === 'draft' && <button onClick={() => handleValidate(inv.id)} className="text-emerald-600 hover:text-emerald-700"><CheckCircle size={16} /></button>}
                  {inv.status !== 'cancelled' && <button onClick={() => handleCancel(inv.id)} className="text-red-600 hover:text-red-700"><XCircle size={16} /></button>}
                </div></td>
              </tr>))}
              {invoices.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
            </tbody></table>
          </div>
        )}
      </div>
    </div>
  );
}
