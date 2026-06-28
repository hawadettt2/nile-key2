import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listHSCodes, calculateDuties, listDeclarations, createDeclaration } from '@/services/api';
import { Search, Plus, X, Calculator } from 'lucide-react';

interface HSCode { id: number; code: string; description: string; duty_rate: number; tax_rate: number; }
interface Declaration { id: number; declaration_number: string; status: string; destination_country: string; total_value?: number; }

export function Customs() {
  const { t } = useTranslation();
  const [hsCodes, setHsCodes] = useState<HSCode[]>([]);
  const [declarations, setDeclarations] = useState<Declaration[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCalc, setShowCalc] = useState(false);
  const [showDecl, setShowDecl] = useState(false);
  const [calcResult, setCalcResult] = useState<Record<string, number> | null>(null);
  const [calcForm, setCalcForm] = useState({ hs_code: '', value: 0, currency: 'USD', destination_country: '' });
  const [declForm, setDeclForm] = useState({ destination_country: '', total_value: 0, currency: 'USD' });

  const load = async () => { setLoading(true); try { const [hsRes, declRes] = await Promise.all([listHSCodes(), listDeclarations()]); setHsCodes(hsRes.data || []); setDeclarations(declRes.data || []); } catch { /* silent */ } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);

  const handleCalc = async () => { try { const res = await calculateDuties(calcForm); setCalcResult(res.data); } catch { alert('Error'); } };
  const handleCreateDecl = async (e: React.FormEvent) => { e.preventDefault(); try { await createDeclaration(declForm); setShowDecl(false); load(); } catch { alert('Error'); } };
  const filteredHs = hsCodes.filter(h => !search || h.code.includes(search) || h.description.toLowerCase().includes(search.toLowerCase()));

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('customs.title')}</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowCalc(true)} className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Calculator size={16} /> {t('customs.calculateDuties')}</button>
          <button onClick={() => setShowDecl(true)} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"><Plus size={16} /> {t('customs.addDeclaration')}</button>
        </div>
      </div>
      {showCalc && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">{t('customs.calculateDuties')}</h3><button onClick={() => { setShowCalc(false); setCalcResult(null); }} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          <div className="flex gap-2 mb-4">
            <input value={calcForm.hs_code} onChange={(e) => setCalcForm({...calcForm, hs_code: e.target.value})} placeholder={t('customs.hsCode')} className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input type="number" value={calcForm.value} onChange={(e) => setCalcForm({...calcForm, value: Number(e.target.value)})} placeholder="Value" className="w-28 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <button onClick={handleCalc} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm font-medium">{t('customs.calculateDuties')}</button>
          </div>
          {calcResult && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">Duty Rate</p><p className="text-lg font-bold text-slate-900">{calcResult.duty_rate}%</p></div>
              <div className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">Duty Amount</p><p className="text-lg font-bold text-emerald-600">${calcResult.duty_amount?.toFixed(2)}</p></div>
              <div className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">Tax Amount</p><p className="text-lg font-bold text-cyan-600">${calcResult.tax_amount?.toFixed(2)}</p></div>
              <div className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">Total</p><p className="text-lg font-bold text-rose-600">${calcResult.total_duties?.toFixed(2)}</p></div>
            </div>
          )}
        </div>
      )}
      {showDecl && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">{t('customs.addDeclaration')}</h3><button onClick={() => setShowDecl(false)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button></div>
          <form onSubmit={handleCreateDecl} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input value={declForm.destination_country} onChange={(e) => setDeclForm({...declForm, destination_country: e.target.value})} placeholder={t('shipment.destination')} required className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <input type="number" value={declForm.total_value} onChange={(e) => setDeclForm({...declForm, total_value: Number(e.target.value)})} placeholder="Total Value" className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            <div className="md:col-span-3"><button type="submit" className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">{t('common.save')}</button></div>
          </form>
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden mb-6">
        <div className="px-4 py-3 border-b border-slate-100 font-semibold text-slate-900">{t('customs.declarations')}</div>
        {declarations.length === 0 ? <div className="px-4 py-6 text-center text-sm text-slate-500">{t('common.noData')}</div> : (
          <div className="overflow-x-auto">
            <table className="w-full"><thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">#</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('shipment.destination')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Value</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.status')}</th>
            </tr></thead><tbody className="divide-y divide-slate-100">
              {declarations.map((d) => (<tr key={d.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-sm font-mono">{d.declaration_number}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{d.destination_country}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{d.total_value?.toFixed(2) || '-'}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${d.status === 'approved' ? 'bg-emerald-100 text-emerald-700' : d.status === 'submitted' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>{d.status}</span></td>
              </tr>))}
            </tbody></table>
          </div>
        )}
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-100">
          <div className="flex items-center gap-2 mb-2"><Search size={16} className="text-slate-500" /><h3 className="font-semibold text-slate-900">{t('customs.hsCode')} Database</h3></div>
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search HS codes..." className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
        </div>
        {loading ? <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div> : (
          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full"><thead className="bg-slate-50 sticky top-0"><tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customs.hsCode')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customs.description')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customs.dutyRate')}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customs.taxRate')}</th>
            </tr></thead><tbody className="divide-y divide-slate-100">
              {filteredHs.map((h) => (<tr key={h.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-sm font-mono font-medium text-slate-900">{h.code}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{h.description}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{h.duty_rate}%</td>
                <td className="px-4 py-3 text-sm text-slate-600">{h.tax_rate}%</td>
              </tr>))}
              {filteredHs.length === 0 && <tr><td colSpan={4} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
            </tbody></table>
          </div>
        )}
      </div>
    </div>
  );
}
