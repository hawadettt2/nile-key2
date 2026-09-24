import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  listCustomers,
  getCustomer,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  importCustomers,
  getCustomerCountries,
  listCustomerProducts,
  listCustomerEvidence,
} from '@/services/api';
import { Search, Plus, Pencil, Trash2, X, Upload, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';

interface Customer {
  id: number;
  name: string;
  name_en?: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  whatsapp?: string;
  website?: string;
  address?: string;
  city?: string;
  country: string;
  tax_id?: string;
  import_license?: string;
  category?: string;
  notes?: string;
  status: string;
  data_status?: string;
  verification_status?: string;
  crm_status?: string;
  activity_status?: string;
  activity_window_label?: string;
}

interface Product {
  id: number;
  product_description?: string;
  hs_code?: string;
  hs_code_description?: string;
  quantity?: number;
  unit?: string;
}

interface Evidence {
  id: number;
  evidence_type: string;
  evidence_data?: Record<string, unknown>;
  observed_at?: string;
  activity_window_label?: string;
}

interface SourceBatch {
  id: number;
  source_type: string;
  source_format?: string;
  source_name?: string;
  file_name?: string;
  status: string;
  imported_at?: string;
}

interface RawRecord {
  id: number;
  row_number?: number;
  sheet_name?: string;
  raw_data: Record<string, unknown>;
  conflict_resolution?: string;
}

export function Customers() {
  const { t, i18n } = useTranslation();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [dataStatusFilter, setDataStatusFilter] = useState('');
  const [crmStatusFilter, setCrmStatusFilter] = useState('');
  const [activityStatusFilter, setActivityStatusFilter] = useState('');
  const [countries, setCountries] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Customer | null>(null);
  const [form, setForm] = useState({
    name: '',
    name_en: '',
    contact_person: '',
    email: '',
    phone: '',
    mobile: '',
    whatsapp: '',
    website: '',
    address: '',
    city: '',
    country: '',
    tax_id: '',
    import_license: '',
    category: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [detailCustomer, setDetailCustomer] = useState<Customer | null>(null);
  const [detailProducts, setDetailProducts] = useState<Product[]>([]);
  const [detailEvidence, setDetailEvidence] = useState<Evidence[]>([]);
  const [detailBatches, setDetailBatches] = useState<SourceBatch[]>([]);
  const [detailRawRecords, setDetailRawRecords] = useState<RawRecord[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, _setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [expandedRaw, setExpandedRaw] = useState<number | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (search) params.search = search;
      if (countryFilter) params.country = countryFilter;
      if (dataStatusFilter) params.data_status = dataStatusFilter;
      if (crmStatusFilter) params.crm_status = crmStatusFilter;
      if (activityStatusFilter) params.activity_status = activityStatusFilter;
      params.skip = (page - 1) * pageSize;
      params.limit = pageSize;
      const res = await listCustomers(params);
      setCustomers(res.data || []);
      setTotalCount((res as any)?.headers?.['x-total-count'] || (res.data?.length || 0));
    } catch {
      setCustomers([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [page, pageSize, search, countryFilter, dataStatusFilter, crmStatusFilter, activityStatusFilter]);

  useEffect(() => {
    getCustomerCountries().then((list) => setCountries(list.data || []));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      if (editing) await updateCustomer(editing.id, form); else await createCustomer(form);
      setShowForm(false);
      setEditing(null);
      setForm({
        name: '', name_en: '', contact_person: '', email: '', phone: '', mobile: '', whatsapp: '', website: '',
        address: '', city: '', country: '', tax_id: '', import_license: '', category: '', notes: '',
      });
      load();
    } catch {
      alert(t('common.error'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('customer.delete') || 'Delete?')) return;
    try {
      await deleteCustomer(id);
      if (detailCustomer?.id === id) {
        setDetailCustomer(null);
      }
      load();
    } catch {
      alert(t('common.error'));
    }
  };

  const handleLegacyImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await importCustomers(file);
      load();
    } catch {
      alert(t('common.error'));
    }
  };

  const openDetail = async (c: Customer) => {
    setDetailCustomer(c);
    setDetailLoading(true);
    setExpandedRaw(null);
    try {
      const [productsRes, evidenceRes] = await Promise.all([
        listCustomerProducts(c.id),
        listCustomerEvidence(c.id),
      ]);
      setDetailProducts(productsRes.data || []);
      setDetailEvidence(evidenceRes.data || []);
      const rawRes = await getCustomer(c.id);
      const rawRecords = (rawRes.data as any)?.raw_records || [];
      const batches = (rawRes.data as any)?.source_batches || [];
      setDetailRawRecords(rawRecords);
      setDetailBatches(batches);
    } catch {
      setDetailProducts([]);
      setDetailEvidence([]);
      setDetailRawRecords([]);
      setDetailBatches([]);
    } finally {
      setDetailLoading(false);
    }
  };

  const openEdit = (c: Customer) => {
    setEditing(c);
    setForm({
      name: c.name,
      name_en: c.name_en || '',
      contact_person: c.contact_person || '',
      email: c.email || '',
      phone: c.phone || '',
      mobile: c.mobile || '',
      whatsapp: c.whatsapp || '',
      website: c.website || '',
      address: c.address || '',
      city: c.city || '',
      country: c.country,
      tax_id: c.tax_id || '',
      import_license: c.import_license || '',
      category: c.category || '',
      notes: c.notes || '',
    });
    setShowForm(true);
  };

  const statusBadge = (value?: string) => {
    const colors: Record<string, string> = {
      active: 'bg-emerald-100 text-emerald-700',
      inactive: 'bg-slate-100 text-slate-600',
      raw: 'bg-slate-100 text-slate-600',
      normalized: 'bg-blue-100 text-blue-700',
      verified: 'bg-emerald-100 text-emerald-700',
      enriched: 'bg-purple-100 text-purple-700',
      unverified: 'bg-amber-100 text-amber-700',
      pending: 'bg-amber-100 text-amber-700',
      rejected: 'bg-red-100 text-red-700',
      prospect: 'bg-slate-100 text-slate-600',
      active_customer: 'bg-emerald-100 text-emerald-700',
      unknown: 'bg-slate-100 text-slate-600',
      observed_active: 'bg-emerald-100 text-emerald-700',
      dormant: 'bg-red-100 text-red-700',
      not_observed: 'bg-slate-100 text-slate-600',
    };
    const cls = colors[value || ''] || 'bg-slate-100 text-slate-600';
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${cls}`}>{value || '-'}</span>;
  };

  return (
    <div dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('customer.title')}</h1>
        <div className="flex gap-2">
          <label className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium cursor-pointer transition-colors">
            <Upload size={16} /> {t('customer.importCSV')}
            <input type="file" accept=".csv" onChange={handleLegacyImport} className="hidden" />
          </label>
          <button onClick={() => { setShowForm(true); setEditing(null); }} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors">
            <Plus size={16} /> {t('customer.addCustomer')}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        <select value={countryFilter} onChange={(e) => setCountryFilter(e.target.value)} className="px-3 py-2 border border-slate-300 rounded-lg text-sm">
          <option value="">{t('customer.country') || 'Country'}</option>
          {countries.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={dataStatusFilter} onChange={(e) => setDataStatusFilter(e.target.value)} className="px-3 py-2 border border-slate-300 rounded-lg text-sm">
          <option value="">{t('customer.dataStatus') || 'Data Status'}</option>
          <option value="raw">{t('customer.raw') || 'Raw'}</option>
          <option value="normalized">{t('customer.normalized') || 'Normalized'}</option>
          <option value="verified">{t('customer.verified') || 'Verified'}</option>
          <option value="enriched">{t('customer.enriched') || 'Enriched'}</option>
        </select>
        <select value={crmStatusFilter} onChange={(e) => setCrmStatusFilter(e.target.value)} className="px-3 py-2 border border-slate-300 rounded-lg text-sm">
          <option value="">{t('customer.crmStatus') || 'CRM Status'}</option>
          <option value="prospect">{t('customer.prospect') || 'Prospect'}</option>
          <option value="active_customer">{t('customer.activeCustomer') || 'Active Customer'}</option>
          <option value="inactive">{t('customer.inactive') || 'Inactive'}</option>
        </select>
        <select value={activityStatusFilter} onChange={(e) => setActivityStatusFilter(e.target.value)} className="px-3 py-2 border border-slate-300 rounded-lg text-sm">
          <option value="">{t('customer.activityStatus') || 'Activity Status'}</option>
          <option value="unknown">{t('customer.unknown') || 'Unknown'}</option>
          <option value="observed_active">{t('customer.activeImporter') || 'Active Importer'}</option>
          <option value="dormant">{t('customer.dormant') || 'Dormant'}</option>
          <option value="not_observed">{t('customer.notObserved') || 'Not Observed'}</option>
        </select>
        <input value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && load()} placeholder={t('common.search')} className="flex-1 min-w-[200px] px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
        <button onClick={load} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg transition-colors"><Search size={16} /></button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{editing ? t('customer.editCustomer') : t('customer.addCustomer')}</h3>
            <button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
          </div>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.name')} <span className="text-red-500 ml-1">*</span></label>
              <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.nameEn') || 'Name (EN)'}</label>
              <input value={form.name_en} onChange={(e) => setForm({ ...form, name_en: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.contact')}</label>
              <input value={form.contact_person} onChange={(e) => setForm({ ...form, contact_person: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.email')}</label>
              <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.phone')}</label>
              <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.mobile') || 'Mobile'}</label>
              <input value={form.mobile} onChange={(e) => setForm({ ...form, mobile: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.whatsapp') || 'WhatsApp'}</label>
              <input value={form.whatsapp} onChange={(e) => setForm({ ...form, whatsapp: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.website') || 'Website'}</label>
              <input value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.address') || 'Address'}</label>
              <input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.city')}</label>
              <input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.country')} <span className="text-red-500 ml-1">*</span></label>
              <input required value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.taxId') || 'Tax ID'}</label>
              <input value={form.tax_id} onChange={(e) => setForm({ ...form, tax_id: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.importLicense') || 'Import License'}</label>
              <input value={form.import_license} onChange={(e) => setForm({ ...form, import_license: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.category')}</label>
              <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('customer.notes') || 'Notes'}</label>
              <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={2} className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none text-sm w-full" />
            </div>
            <div className="md:col-span-2">
              <button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2">
                {submitting && <Loader2 className="animate-spin" size={16} />}
                {submitting ? t('common.saving') : t('common.save')}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.name')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.contact')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.country')}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.dataStatus') || 'Data Status'}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.crmStatus') || 'CRM Status'}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.activityStatus') || 'Activity Status'}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{t('common.actions')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {customers.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50 transition-colors cursor-pointer" onClick={() => openDetail(c)}>
                    <td className="px-4 py-3 text-sm font-medium text-slate-900">{c.name}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{c.contact_person || '-'} {c.email ? `(${c.email})` : ''}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{c.country}</td>
                    <td className="px-4 py-3">{statusBadge(c.data_status)}</td>
                    <td className="px-4 py-3">{statusBadge(c.crm_status)}</td>
                    <td className="px-4 py-3">{statusBadge(c.activity_status)}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                        <button onClick={() => openEdit(c)} className="text-blue-600 hover:text-blue-700"><Pencil size={14} /></button>
                        <button onClick={() => handleDelete(c.id)} className="text-red-600 hover:text-red-700"><Trash2 size={14} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
                {customers.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-sm text-slate-500">{t('common.noData')}</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {customers.length > 0 && (
        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-slate-600">
            {t('common.showing') || 'Showing'} {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, totalCount || customers.length)} {t('common.of') || 'of'} {totalCount || customers.length}
          </div>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border border-slate-300 rounded text-sm disabled:opacity-50">{t('common.previous') || 'Previous'}</button>
            <button onClick={() => setPage(p => p + 1)} disabled={customers.length < pageSize} className="px-3 py-1 border border-slate-300 rounded text-sm disabled:opacity-50">{t('common.next') || 'Next'}</button>
          </div>
        </div>
      )}

      {detailCustomer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setDetailCustomer(null)}>
          <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <h2 className="text-xl font-semibold">{detailCustomer.name}</h2>
              <button onClick={() => setDetailCustomer(null)} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
            </div>
            {detailLoading ? (
              <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" /></div>
            ) : (
              <div className="p-6 space-y-6">
                <section>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.name') || 'Company'}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div><span className="text-slate-500">{t('customer.name')}: </span>{detailCustomer.name}</div>
                    <div><span className="text-slate-500">{t('customer.nameEn') || 'Name (EN)'}: </span>{detailCustomer.name_en || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.contact')}: </span>{detailCustomer.contact_person || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.category')}: </span>{detailCustomer.category || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.address') || 'Address'}: </span>{detailCustomer.address || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.city')}: </span>{detailCustomer.city || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.country')}: </span>{detailCustomer.country}</div>
                    <div><span className="text-slate-500">{t('customer.taxId') || 'Tax ID'}: </span>{detailCustomer.tax_id || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.importLicense') || 'Import License'}: </span>{detailCustomer.import_license || '-'}</div>
                  </div>
                </section>

                <section>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.contact') || 'Contacts'}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div><span className="text-slate-500">{t('customer.email')}: </span>{detailCustomer.email || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.phone')}: </span>{detailCustomer.phone || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.mobile') || 'Mobile'}: </span>{detailCustomer.mobile || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.whatsapp') || 'WhatsApp'}: </span>{detailCustomer.whatsapp || '-'}</div>
                    <div><span className="text-slate-500">{t('customer.website') || 'Website'}: </span>{detailCustomer.website || '-'}</div>
                  </div>
                </section>

                <section>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.products') || 'Products'}</h3>
                  {detailProducts.length === 0 ? <div className="text-sm text-slate-500">{t('common.noData')}</div> : (
                    <table className="w-full text-sm">
                      <thead className="bg-slate-50"><tr>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.productDescription') || 'Product'}</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase">HS</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.quantity') || 'Qty'}</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase">{t('customer.unit') || 'Unit'}</th>
                      </tr></thead>
                      <tbody className="divide-y divide-slate-100">
                        {detailProducts.map((p) => (
                          <tr key={p.id} className="hover:bg-slate-50">
                            <td className="px-3 py-2">{p.product_description || '-'}</td>
                            <td className="px-3 py-2">{p.hs_code || '-'}</td>
                            <td className="px-3 py-2">{p.quantity ?? '-'}</td>
                            <td className="px-3 py-2">{p.unit || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </section>

                <section>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.evidence') || 'Evidence'}</h3>
                  {detailEvidence.length === 0 ? <div className="text-sm text-slate-500">{t('common.noData')}</div> : (
                    <div className="space-y-2">
                      {detailEvidence.map((e) => (
                        <div key={e.id} className="border border-slate-200 rounded-lg p-3 text-sm">
                          <div className="font-medium text-slate-700">{e.evidence_type}</div>
                          {e.activity_window_label && <div className="text-slate-500">{e.activity_window_label}</div>}
                          {e.observed_at && <div className="text-slate-500">{new Date(e.observed_at).toLocaleString()}</div>}
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                <section>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.sourceBatch') || 'Provenance'}</h3>
                  {detailBatches.length === 0 ? <div className="text-sm text-slate-500">{t('common.noData')}</div> : (
                    <div className="space-y-2">
                      {detailBatches.map((b) => (
                        <div key={b.id} className="border border-slate-200 rounded-lg p-3 text-sm">
                          <div className="font-medium text-slate-700">{b.source_name || b.file_name || b.source_type}</div>
                          <div className="text-slate-500">{b.source_format} • {b.status} • {b.imported_at ? new Date(b.imported_at).toLocaleString() : '-'}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                <section>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.rawData') || 'Raw Source'}</h3>
                  {detailRawRecords.length === 0 ? <div className="text-sm text-slate-500">{t('common.noData')}</div> : (
                    <div className="space-y-2">
                      {detailRawRecords.map((r) => (
                        <div key={r.id} className="border border-slate-200 rounded-lg">
                          <button className="w-full flex items-center justify-between p-3 text-sm text-left" onClick={() => setExpandedRaw(expandedRaw === r.id ? null : r.id)}>
                            <span className="font-medium text-slate-700">Row {r.row_number || r.id} {r.sheet_name ? `• ${r.sheet_name}` : ''}</span>
                            {expandedRaw === r.id ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                          </button>
                          {expandedRaw === r.id && (
                            <pre className="px-3 pb-3 text-xs bg-slate-50 overflow-x-auto whitespace-pre-wrap break-words text-slate-700">
                              {JSON.stringify(r.raw_data, null, 2)}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
