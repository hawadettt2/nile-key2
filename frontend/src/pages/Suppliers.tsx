import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { listSuppliers, createSupplier, updateSupplier, deleteSupplier, listSupplierAccreditations, deleteSupplierAccreditation, createSupplierAccreditation, verifySupplierAccreditation, updateSupplierAccreditation } from '@/services/api';
import { Search, Plus, Pencil, Trash2, X } from 'lucide-react';

interface Supplier { id: number; name: string; name_en?: string; contact_person?: string; email?: string; phone?: string; address?: string; city?: string; province?: string; station_code?: string; facility_type?: string; parent_company_id?: number; country: string; status: string; data_status?: string; verification_status?: string; tax_id?: string; source_serial?: string; activity?: string; notes?: string; }

const PROVINCES = ['القاهرة', 'الجيزة', 'إسكندرية', 'البحيرة', 'مطروح', 'كفر الشيخ', 'الغربية', 'المنوفية', 'القليوبية', 'الشرقية', 'الدقهلية', 'دمياط', 'الإسماعيلية', 'بورسعيد', 'السويس', 'شمال سيناء', 'جنوب سيناء', 'الفيوم', 'بني سويف', 'المنيا', 'أسيوط', 'سوهاج', 'قنا', 'الأقصر', 'أسوان', 'البحر الأحمر', 'وادي الجديد'];
const CROPS = ['البركة', 'بابونج', 'بسلة', 'بصل أخضر', 'بصل جاف', 'بطاطا', 'بطاطس', 'بقدونس', 'بنجر', 'ترمس', 'تمور', 'ثوم', 'ثوم جاف', 'جزر', 'جوافة', 'خس', 'خرشوف', 'خوخ', 'ذرة', 'رمان', 'زبير', 'زبيب', 'زعتر', 'زهرة كالانديولا', 'سمسم', 'شمر', 'عدس', 'عنب', 'فاصوليا', 'فراولة', 'فول', 'فول بلدي', 'فول سوداني', 'كابوتشا', 'كراوية', 'كرفس', 'كرنب أبيض', 'كرنب أحمر', 'كمون', 'كوسة', 'لوبيا', 'ليمون', 'ليمون اصفر', 'ليمون مجفف', 'مانجو', 'ملوكية', 'نعناع', 'نعناع فلفلي', 'نكتارين', 'ورق لوري', 'ينسون'];

export function Suppliers() {
  const { t } = useTranslation();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [companies, setCompanies] = useState<Supplier[]>([]);
  const [search, setSearch] = useState('');
  const [filterFacility, setFilterFacility] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterProvince, setFilterProvince] = useState('');
  const [filterCrop, setFilterCrop] = useState('');
  const [filterSeason, setFilterSeason] = useState('');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Supplier | null>(null);
  const [form, setForm] = useState({ name: '', name_en: '', contact_person: '', email: '', phone: '', address: '', city: '', province: '', country: 'Egypt', tax_id: '', facility_type: 'company', station_code: '', parent_company_id: '' as string | number, data_status: 'raw', verification_status: 'unverified', source_serial: '', activity: '', notes: '' });
  const [submitting, setSubmitting] = useState(false);
  const [expandedSupplier, setExpandedSupplier] = useState<number | null>(null);
  const [accreditations, setAccreditations] = useState<Record<number, any[]>>({});
  const [accForm, setAccForm] = useState({ source_type: 'CAPQ', accrediting_body: '', accreditation_number: '', scope: '', crops: '', season: '', accreditation_date: '', validity_date: '', source_document: '', source_page: '', source_reference: '' });
  const [showAccForm, setShowAccForm] = useState(false);
  const [editingAccId, setEditingAccId] = useState<number | null>(null);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const PAGE_SIZE = 20;

  const facilityTypeLabel = (ft: string | undefined): string => {
    if (!ft) return '-';
    if (ft === 'company') return t('supplier.company');
    if (ft === 'packing_station') return t('supplier.packingStation');
    if (ft === 'farm') return t('supplier.farm');
    return ft;
  };

  const statusLabel = (st: string | undefined): string => {
    if (!st) return '-';
    if (st === 'active') return t('supplier.active');
    if (st === 'inactive') return t('supplier.inactive');
    return st;
  };

  const load = async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (search) params.search = search;
      if (filterFacility) params.facility_type = filterFacility;
      if (filterStatus) params.status = filterStatus;
      if (filterProvince) params.province = filterProvince;
      if (filterCrop) params.crop = filterCrop;
      if (filterSeason) params.season = filterSeason;
      // Fetch ALL suppliers (no limit) so we can paginate client-side
      params.limit = 500;
      const res = await listSuppliers(params);
      const list = res.data || [];
      setSuppliers(list);
      setTotal(list.length);
      setCompanies(list.filter((s: Supplier) => s.facility_type === 'company' || !s.facility_type));
    } catch { setSuppliers([]); setCompanies([]); } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);
  useEffect(() => { setPage(0); }, [search, filterFacility, filterStatus, filterProvince, filterCrop, filterSeason]);

  const visible = suppliers.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(total / PAGE_SIZE);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      const payload: Record<string, unknown> = {
        name: form.name,
        name_en: form.name_en || undefined,
        contact_person: form.contact_person || undefined,
        email: form.email || undefined,
        phone: form.phone || undefined,
        address: form.address || undefined,
        city: form.city || undefined,
        province: form.province || undefined,
        country: form.country || 'Egypt',
        tax_id: form.tax_id || undefined,
        facility_type: form.facility_type || undefined,
        station_code: form.station_code || undefined,
        parent_company_id: form.parent_company_id ? Number(form.parent_company_id) : undefined,
        data_status: form.data_status,
        verification_status: form.verification_status,
        source_serial: form.source_serial || undefined,
        activity: form.activity || undefined,
        notes: form.notes || undefined,
      };
      if (editing) await updateSupplier(editing.id, payload); else await createSupplier(payload);
      setShowForm(false); setEditing(null); setForm({ name: '', name_en: '', contact_person: '', email: '', phone: '', address: '', city: '', province: '', country: 'Egypt', tax_id: '', facility_type: '', station_code: '', parent_company_id: '', data_status: 'raw', verification_status: 'unverified', source_serial: '', activity: '', notes: '' }); load();
    } catch { alert('Error'); } finally { setSubmitting(false); }
  };
  const handleDelete = async (id: number) => { if (!confirm('Are you sure?')) return; try { await deleteSupplier(id); load(); } catch { alert('Error'); } };
  const toggleAccreditations = async (id: number) => {
    if (expandedSupplier === id) { setExpandedSupplier(null); return; }
    setExpandedSupplier(id);
    if (!accreditations[id]) {
      try {
        const res = await listSupplierAccreditations(id);
        setAccreditations((prev) => ({ ...prev, [id]: res.data || [] }));
      } catch { setAccreditations((prev) => ({ ...prev, [id]: [] })); }
    }
  };
  const openEdit = (s: Supplier) => { setEditing(s); setForm({ name: s.name, name_en: s.name_en || '', contact_person: s.contact_person || '', email: s.email || '', phone: s.phone || '', address: s.address || '', city: s.city || '', province: s.province || '', country: s.country || 'Egypt', tax_id: s.tax_id || '', facility_type: s.facility_type || '', station_code: s.station_code || '', parent_company_id: s.parent_company_id || '', data_status: s.data_status || 'raw', verification_status: s.verification_status || 'unverified', source_serial: s.source_serial || '', activity: s.activity || '', notes: s.notes || '' }); setShowForm(true); };

  const handleAddAccreditation = async (supplierId: number, data: Record<string, unknown>) => {
    try {
      const payload = { ...data };
      if (typeof payload.crops === 'string') {
        payload.crops = (payload.crops as string).split(',').map((c: string) => c.trim()).filter(Boolean);
      }
      await createSupplierAccreditation(supplierId, payload);
      const res = await listSupplierAccreditations(supplierId);
      setAccreditations((prev) => ({ ...prev, [supplierId]: res.data || [] }));
    } catch { alert('Error adding accreditation'); }
  };


  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('supplier.title')}</h1>
        <button onClick={() => { setShowForm(true); setEditing(null); }} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors">
          <Plus size={16} /> {t('supplier.addSupplier')}</button>
      </div>
<div className="flex gap-2 mb-4 flex-wrap">
        <input value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && load()}
          placeholder={t('common.search')} className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
        <select value={filterFacility} onChange={(e) => { setFilterFacility(e.target.value); }} className="px-4 py-2 border border-slate-300 rounded-lg text-sm">
          <option value="">{t('supplier.allFacilityTypes')}</option>
          <option value="company">{t('supplier.company')}</option>
          <option value="packing_station">{t('supplier.packingStation')}</option>
          <option value="farm">{t('supplier.farm')}</option>
        </select>
        <select value={filterStatus} onChange={(e) => { setFilterStatus(e.target.value); }} className="px-4 py-2 border border-slate-300 rounded-lg text-sm">
          <option value="">{t('supplier.allStatus')}</option>
          <option value="active">{t('supplier.active')}</option>
          <option value="inactive">{t('supplier.inactive')}</option>
        </select>
        <button onClick={load} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg transition-colors"><Search size={16} /></button>
      </div>
      <div className="flex gap-2 mb-4 flex-wrap">
        <select value={filterProvince} onChange={(e) => { setFilterProvince(e.target.value); }} className="px-4 py-2 border border-slate-300 rounded-lg text-sm">
          <option value="">{t('supplier.allProvinces') || 'كل المحافظات'}</option>
          {PROVINCES.map((p: string) => <option key={p} value={p}>{p}</option>)}
        </select>
        <select value={filterCrop} onChange={(e) => { setFilterCrop(e.target.value); }} className="px-4 py-2 border border-slate-300 rounded-lg text-sm">
          <option value="">{t('supplier.allCrops') || 'كل المحاصيل'}</option>
          {CROPS.map((c: string) => <option key={c} value={c}>{c}</option>)}
        </select>
        <input value={filterSeason} onChange={(e) => setFilterSeason(e.target.value)} placeholder={t('supplier.season')} className="px-4 py-2 border border-slate-300 rounded-lg text-sm" />
      </div>
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{editing ? t('supplier.editSupplier') : t('supplier.addSupplier')}</h3>
            <button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
          </div>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('supplier.name')} <span className="text-red-500 ml-1">*</span></label>
              <input required value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('supplier.contact')}</label>
              <input value={form.contact_person} onChange={(e) => setForm({...form, contact_person: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('supplier.email')}</label>
              <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('supplier.taxId') || 'Tax ID'}</label>
              <input value={form.tax_id} onChange={(e) => setForm({...form, tax_id: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Facility Type</label>
              <select value={form.facility_type} onChange={(e) => setForm({...form, facility_type: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" required>
                <option value="">-- Unclassified --</option>
                <option value="company">Company</option>
                <option value="packing_station">Packing Station</option>
                <option value="farm">Farm</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Station Code</label>
              <input value={form.station_code} onChange={(e) => setForm({...form, station_code: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Province</label>
              <input value={form.province} onChange={(e) => setForm({...form, province: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            {form.facility_type !== 'company' && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Parent Company</label>
                <select value={form.parent_company_id} onChange={(e) => setForm({...form, parent_company_id: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm">
                  <option value="">-- Select --</option>
                  {companies.map((c) => (<option key={c.id} value={c.id}>{c.name}</option>))}
                </select>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Data Status</label>
              <select value={form.data_status} onChange={(e) => setForm({...form, data_status: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm">
                <option value="raw">Raw</option>
                <option value="verified">Verified</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Verification Status</label>
              <select value={form.verification_status} onChange={(e) => setForm({...form, verification_status: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm">
                <option value="unverified">Unverified</option>
                <option value="verified">Verified</option>
                <option value="disputed">Disputed</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('supplier.city')}</label>
              <input value={form.city} onChange={(e) => setForm({...form, city: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('supplier.country')}</label>
              <input value={form.country} onChange={(e) => setForm({...form, country: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Serial (م)</label>
              <input value={form.source_serial} onChange={(e) => setForm({...form, source_serial: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">النشاط</label>
              <input value={form.activity} onChange={(e) => setForm({...form, activity: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('supplier.address') || 'Address'}</label>
              <input value={form.address} onChange={(e) => setForm({...form, address: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('supplier.notes') || 'Notes'}</label>
              <input value={form.notes} onChange={(e) => setForm({...form, notes: e.target.value})} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
             <div className="md:col-span-2"><button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2">{submitting ? <><span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>Saving...</> : t('common.save')}</button></div>
          </form>
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div> : (<>
<div className="overflow-x-auto">
            <table className="w-full min-w-[1100px] text-[13px]"><thead className="bg-slate-50"><tr>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('supplier.serial')}</th>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('supplier.name')}</th>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('supplier.activity')}</th>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('supplier.address')}</th>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('supplier.phone')}</th>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('supplier.notes')}</th>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('supplier.facilityType')}</th>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('common.status')}</th>
            <th className="px-3 py-2 text-left text-[12px] font-semibold text-slate-500 uppercase whitespace-nowrap">{t('common.actions')}</th>
            </tr></thead><tbody className="divide-y divide-slate-100">
              {visible.map((s) => (<tr key={s.id} className="hover:bg-slate-50 transition-colors align-top">
                <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{s.source_serial || '-'}</td>
                <td className="px-3 py-2 font-medium text-slate-900 align-top"><div className="whitespace-pre-wrap break-words" style={{wordBreak: 'break-word'}}>{s.name}{s.station_code ? ` (${s.station_code})` : ''}</div></td>
                <td className="px-3 py-2 text-slate-700 align-top" style={{maxWidth: '260px'}}><div className="whitespace-pre-wrap break-words" style={{wordBreak: 'break-word'}}>{s.activity || '-'}</div></td>
                <td className="px-3 py-2 text-slate-700 align-top" style={{maxWidth: '340px', minWidth: '240px'}}><div className="whitespace-pre-wrap break-words" style={{wordBreak: 'break-word'}}>{s.address || '-'}</div></td>
                <td className="px-3 py-2 text-slate-600 align-top" style={{minWidth: '130px'}}><div className="flex flex-col gap-1">{(s.phone || '-').split('\n').map((ph: string, idx: number) => <span key={idx} className="whitespace-nowrap">{ph.trim() || '-'}</span>)}</div></td>
                <td className="px-3 py-2 text-slate-700 align-top" style={{maxWidth: '220px'}}><div className="whitespace-pre-wrap break-words" style={{wordBreak: 'break-word'}}>{s.notes || '-'}</div></td>
                <td className="px-3 py-2 text-slate-600 align-top">{facilityTypeLabel(s.facility_type)}</td>
                <td className="px-3 py-2 align-top"><span className={`px-2 py-1 rounded-full text-xs font-medium ${s.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>{statusLabel(s.status)}</span></td>
                <td className="px-3 py-2 align-top"><div className="flex flex-col gap-1"><button onClick={() => openEdit(s)} className="text-blue-600 hover:text-blue-700 text-sm"><Pencil size={14} /></button><button onClick={() => handleDelete(s.id)} className="text-red-600 hover:text-red-700 text-sm"><Trash2 size={14} /></button><button onClick={() => toggleAccreditations(s.id)} className="text-emerald-600 hover:text-emerald-700 text-xs">{t('supplier.accreditations')}</button></div></td>
              </tr>))}
              {visible.length === 0 && <tr><td colSpan={9} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
            </tbody></table>
          </div>
          {total > PAGE_SIZE && (
            <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-t border-slate-200">
              <div className="text-sm text-slate-600">
                {t('supplier.pageOf', { current: page + 1, total: totalPages })} — {t('supplier.totalRecords')}: {total}
              </div>
              <div className="flex gap-2">
                <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="px-3 py-1 text-sm border border-slate-300 rounded hover:bg-slate-100 disabled:opacity-50">{t('supplier.previous')}</button>
<button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="px-3 py-1 text-sm border border-slate-300 rounded hover:bg-slate-100 disabled:opacity-50">{t('supplier.next')}</button>
              </div>
            </div>
          )}
        </>
      )}
      </div>
      {expandedSupplier !== null && accreditations[expandedSupplier] && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 mt-4 p-4">
          <div className="space-y-2">
            <p className="text-sm font-semibold text-slate-900">{t('supplier.accreditations')} {t('supplier.totalRecords')}: {accreditations[expandedSupplier]?.length || 0}</p>
            <button onClick={() => { setEditingAccId(null); setAccForm({ source_type: 'CAPQ', accrediting_body: '', accreditation_number: '', scope: '', crops: '', season: '', accreditation_date: '', validity_date: '', source_document: '', source_page: '', source_reference: '' }); setShowAccForm(!showAccForm); }} className="text-xs bg-emerald-600 text-white px-2 py-1 rounded">{showAccForm ? t('common.cancel') : (editingAccId ? t('common.edit') : t('supplier.accreditations'))}</button>
            {showAccForm && (
              <form onSubmit={async (e) => { e.preventDefault(); const payload: Record<string, unknown> = { ...accForm, crops: accForm.crops.split(',').map((c: string) => c.trim()).filter(Boolean) }; if (editingAccId) { await updateSupplierAccreditation(editingAccId, payload); } else { await handleAddAccreditation(expandedSupplier!, payload); } setShowAccForm(false); setEditingAccId(null); setAccForm({ source_type: 'CAPQ', accrediting_body: '', accreditation_number: '', scope: '', crops: '', season: '', accreditation_date: '', validity_date: '', source_document: '', source_page: '', source_reference: '' }); const res = await listSupplierAccreditations(expandedSupplier!); setAccreditations((prev) => ({ ...prev, [expandedSupplier!]: res.data || [] })); }} className="grid grid-cols-2 gap-2 border p-2 rounded">
                <input placeholder="Source Type" value={accForm.source_type} onChange={(e) => setAccForm({...accForm, source_type: e.target.value})} className="px-2 py-1 border rounded text-sm" required />
                <input placeholder="Accrediting Body" value={accForm.accrediting_body} onChange={(e) => setAccForm({...accForm, accrediting_body: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Accreditation Number" value={accForm.accreditation_number} onChange={(e) => setAccForm({...accForm, accreditation_number: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Scope (crops)" value={accForm.scope} onChange={(e) => setAccForm({...accForm, scope: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Crops (comma-separated)" value={accForm.crops} onChange={(e) => setAccForm({...accForm, crops: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Season" value={accForm.season} onChange={(e) => setAccForm({...accForm, season: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Accreditation Date" value={accForm.accreditation_date} onChange={(e) => setAccForm({...accForm, accreditation_date: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Validity Date" value={accForm.validity_date} onChange={(e) => setAccForm({...accForm, validity_date: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Source Document" value={accForm.source_document} onChange={(e) => setAccForm({...accForm, source_document: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Source Page" value={accForm.source_page} onChange={(e) => setAccForm({...accForm, source_page: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <input placeholder="Source Reference" value={accForm.source_reference} onChange={(e) => setAccForm({...accForm, source_reference: e.target.value})} className="px-2 py-1 border rounded text-sm" />
                <button type="submit" className="col-span-2 bg-emerald-600 text-white px-2 py-1 rounded text-sm">{t('common.save')}</button>
              </form>
            )}
            {(accreditations[expandedSupplier] || []).map((a: any) => (
              <div key={a.id} className="text-sm border rounded p-2 flex justify-between items-center">
                <span>{a.source_type} — {a.accrediting_body || ''} — {a.status} — {a.accreditation_date || ''} to {a.validity_date || ''} — crops: {(a.crops && a.crops.length ? a.crops.join(', ') : a.scope) || '-'} — season: {a.season || '-'} — doc: {a.source_document || ''} p.{a.source_page || ''}</span>
                <div className="flex gap-2">
                  <button onClick={() => { setEditingAccId(a.id); setAccForm({ source_type: a.source_type || 'CAPQ', accrediting_body: a.accrediting_body || '', accreditation_number: a.accreditation_number || '', scope: a.scope || '', crops: (a.crops || []).join(', '), season: a.season || '', accreditation_date: a.accreditation_date || '', validity_date: a.validity_date || '', source_document: a.source_document || '', source_page: a.source_page || '', source_reference: a.source_reference || '' }); setShowAccForm(true); }} className="text-blue-600 text-xs">{t('common.edit')}</button>
                  <button onClick={() => { if (confirm('Verify this accreditation?')) verifySupplierAccreditation(a.id).then(() => toggleAccreditations(expandedSupplier!)); }} className="text-blue-600 text-xs">Verify</button>
                  <button onClick={() => { deleteSupplierAccreditation(a.id).then(() => toggleAccreditations(expandedSupplier!)); }} className="text-red-600 text-xs">{t('common.delete')}</button>
                </div>
              </div>
            ))}
            {(accreditations[expandedSupplier] || []).length === 0 && <p className="text-sm text-slate-500">{t('common.noData')}</p>}
          </div>
        </div>
      )}
    </div>
  );
}