import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  listCustomers,
  getCustomer,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  importCustomers,
  importPreview,
  importReview,
  importConfirm,
  importCancel,
  getCustomerCountries,
  listCustomerProducts,
  listCustomerEvidence,
} from '@/services/api';
import { Search, Plus, Pencil, Trash2, X, Upload, ChevronDown, ChevronRight, FileSpreadsheet, Loader2 } from 'lucide-react';

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

interface PreviewResponse {
  batch_id: number;
  file_name: string;
  sheet_name?: string;
  total_rows: number;
  preview_rows: Array<{ row_number: number; sheet_name?: string; raw: Record<string, unknown> }>;
  detected_columns: string[];
  target_fields: Array<{ key: string; label_en: string; label_ar: string; required: boolean }>;
  sheets?: Array<{ name: string; preview_rows: Array<{ row_number: number; raw: Record<string, unknown> }>; row_count?: number }>;
}

type WizardStep = 'upload' | 'select' | 'map' | 'validate' | 'review' | 'confirm';

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
  const [showWizard, setShowWizard] = useState(false);
  const [wizardStep, setWizardStep] = useState<WizardStep>('upload');
  const [wizardFile, setWizardFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [fieldMapping, setFieldMapping] = useState<Record<string, string>>({});
  const [duplicatePolicy, setDuplicatePolicy] = useState('skip');
  const [importing, setImporting] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, _setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedSheets, setSelectedSheets] = useState<string[]>([]);
  const [conflicts, setConflicts] = useState<Array<{ row_number: number; sheet_name?: string; candidates: Array<{ customer: Customer; match_type: string }> }>>([]);
  const [reviewErrors, setReviewErrors] = useState<Array<{ row_number: number; sheet_name?: string; error: string }>>([]);
  const [importResult, setImportResult] = useState<{ imported: number; skipped: number; errors: Array<{ row: number; error: string }> } | null>(null);
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

  const startWizard = () => {
    setShowWizard(true);
    setWizardStep('upload');
    setWizardFile(null);
    setPreview(null);
    setFieldMapping({});
    setDuplicatePolicy('skip');
    setSelectedSheets([]);
    setConflicts([]);
    setReviewErrors([]);
    setImportResult(null);
  };

  const handleWizardUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const ext = file.name.toLowerCase().split('.').pop() || '';
    if (ext !== 'csv' && ext !== 'xlsx') {
      alert(t('customer.importFailed') || 'Unsupported format');
      return;
    }
    setWizardFile(file);
    try {
      const res = await importPreview(file);
      setPreview(res.data as PreviewResponse);
      setFieldMapping({});
      setSelectedSheets([]);
      setWizardStep('select');
    } catch {
      alert(t('common.error'));
    }
  };

  const handleWizardReview = async () => {
    if (!preview) return;
    setImporting(true);
    try {
      const res = await importReview({
        batch_id: preview.batch_id,
        field_mapping: fieldMapping,
        selected_sheets: selectedSheets.length > 0 ? selectedSheets : undefined,
      });
      setConflicts((res.data as any)?.conflicts || []);
      setReviewErrors((res.data as any)?.errors || []);
      setWizardStep('review');
    } catch {
      alert(t('common.error'));
    } finally {
      setImporting(false);
    }
  };

  const handleWizardConfirm = async () => {
    if (!preview) return;
    setImporting(true);
    try {
      const res = await importConfirm({
        batch_id: preview.batch_id,
        field_mapping: fieldMapping,
        duplicate_policy: duplicatePolicy,
        selected_sheets: selectedSheets.length > 0 ? selectedSheets : undefined,
      });
      setImportResult(res.data as { imported: number; skipped: number; errors: Array<{ row: number; error: string }> });
      setWizardStep('confirm');
    } catch {
      alert(t('common.error'));
    } finally {
      setImporting(false);
    }
  };

  const handleWizardCancel = async () => {
    if (!preview) return;
    try {
      await importCancel(preview.batch_id);
      setShowWizard(false);
      setPreview(null);
      setImportResult(null);
    } catch {
      alert(t('common.error'));
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
          <button onClick={startWizard} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors">
            <Upload size={16} /> {t('customer.importWizard') || 'Import Wizard'}
          </button>
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

      {showWizard && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowWizard(false)}>
          <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <h2 className="text-xl font-semibold">{t('customer.importWizard') || 'Import Wizard'}</h2>
              <button onClick={() => setShowWizard(false)} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
            </div>
            <div className="p-6 space-y-6">
              {wizardStep === 'upload' && (
                <div>
                  <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center">
                    <FileSpreadsheet className="mx-auto mb-3 text-slate-400" size={40} />
                    <p className="text-sm text-slate-600 mb-3">{t('customer.uploadStep') || 'Upload CSV or XLSX file'}</p>
                    <label className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm font-medium cursor-pointer inline-flex items-center gap-2">
                      <Upload size={16} /> {t('customer.uploadStep') || 'Choose File'}
                      <input type="file" accept=".csv,.xlsx" onChange={handleWizardUpload} className="hidden" />
                    </label>
                    {wizardFile && <div className="mt-3 text-sm text-slate-600">{wizardFile.name}</div>}
                  </div>
                </div>
              )}

              {wizardStep === 'select' && preview && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.sheetSelection') || 'Select Data'}</h3>
                  {preview.sheets && preview.sheets.length > 0 ? (
                    <div className="space-y-2 mb-4">
                      {preview.sheets.map((sheet) => (
                        <label key={sheet.name} className="flex items-center gap-2 border border-slate-200 rounded-lg p-3 text-sm cursor-pointer hover:bg-slate-50">
                          <input
                            type="checkbox"
                            checked={selectedSheets.includes(sheet.name)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedSheets([...selectedSheets, sheet.name]);
                              } else {
                                setSelectedSheets(selectedSheets.filter(s => s !== sheet.name));
                              }
                            }}
                          />
                          <span className="font-medium text-slate-700">{sheet.name}</span>
                          <span className="text-slate-500">({sheet.row_count || preview.total_rows} rows)</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-slate-600 mb-4">{t('customer.preview') || 'Preview'}: {preview.total_rows} rows • {preview.detected_columns.length} columns</div>
                  )}
                  <div className="space-y-2 mb-4">
                    {preview.preview_rows.map((row) => (
                      <div key={row.row_number} className="border border-slate-200 rounded-lg p-3 text-xs bg-slate-50">
                        <div className="font-medium text-slate-700 mb-1">Row {row.row_number} {row.sheet_name ? `• ${row.sheet_name}` : ''}</div>
                        <pre className="whitespace-pre-wrap break-words text-slate-700">{JSON.stringify(row.raw, null, 2)}</pre>
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-end gap-2">
                    <button onClick={handleWizardCancel} className="px-4 py-2 border border-slate-300 rounded-lg text-sm hover:bg-slate-50">{t('common.cancel')}</button>
                    <button onClick={() => setWizardStep('map')} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700">{t('customer.mapStep') || 'Map Fields'}</button>
                  </div>
                </div>
              )}

              {wizardStep === 'map' && preview && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.fieldMapping') || 'Field Mapping'}</h3>
                  <div className="space-y-2 mb-4">
                    {preview.target_fields.map((field) => (
                      <div key={field.key} className="flex items-center gap-3">
                        <label className="w-40 text-sm text-slate-700 text-right">{i18n.language === 'ar' ? field.label_ar : field.label_en}</label>
                        <select
                          value={fieldMapping[field.key] || ''}
                          onChange={(e) => setFieldMapping({ ...fieldMapping, [field.key]: e.target.value })}
                          className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm"
                        >
                          <option value="">-- Ignore --</option>
                          {preview.detected_columns.map((col) => <option key={col} value={col}>{col}</option>)}
                        </select>
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-end gap-2">
                    <button onClick={() => setWizardStep('select')} className="px-4 py-2 border border-slate-300 rounded-lg text-sm hover:bg-slate-50">Back</button>
                    <button onClick={() => setWizardStep('validate')} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700">{t('customer.reviewStep') || 'Review & Confirm'}</button>
                  </div>
                </div>
              )}

              {wizardStep === 'validate' && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.validationErrors') || 'Validation'}</h3>
                  <div className="text-sm text-slate-600 mb-4">{t('customer.duplicatePolicy') || 'Duplicate Policy'}:</div>
                  <select value={duplicatePolicy} onChange={(e) => setDuplicatePolicy(e.target.value)} className="px-3 py-2 border border-slate-300 rounded-lg text-sm mb-4">
                    <option value="skip">Skip</option>
                    <option value="create_new">Create New</option>
                    <option value="merge">Merge</option>
                    <option value="error">Error</option>
                  </select>
                  <div className="flex justify-end gap-2">
                    <button onClick={() => setWizardStep('map')} className="px-4 py-2 border border-slate-300 rounded-lg text-sm hover:bg-slate-50">Back</button>
                    <button onClick={handleWizardReview} disabled={importing} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700 inline-flex items-center gap-2">
                      {importing && <Loader2 className="animate-spin" size={16} />}
                      {importing ? t('customer.reviewing') || 'Reviewing...' : t('customer.reviewConflicts') || 'Review Conflicts'}
                    </button>
                  </div>
                </div>
              )}

              {wizardStep === 'review' && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.reviewConflicts') || 'Review Conflicts'}</h3>
                  {reviewErrors.length === 0 && conflicts.length === 0 ? (
                    <div className="text-sm text-emerald-700 mb-4">{t('customer.noConflicts') || 'No conflicts detected. You can proceed to confirm.'}</div>
                  ) : (
                    <div className="space-y-3 mb-4">
                      {reviewErrors.map((err, idx) => (
                        <div key={`err-${idx}`} className="border border-red-200 rounded-lg p-3 text-sm text-red-700">
                          Row {err.row_number} {err.sheet_name ? `• ${err.sheet_name}` : ''}: {err.error}
                        </div>
                      ))}
                      {conflicts.map((conflict, idx) => (
                        <div key={`conflict-${idx}`} className="border border-amber-200 rounded-lg p-3 text-sm">
                          <div className="font-medium text-slate-700 mb-1">Row {conflict.row_number} {conflict.sheet_name ? `• ${conflict.sheet_name}` : ''}</div>
                          <div className="text-slate-600">{t('customer.duplicateCandidates') || 'Duplicate candidates'}:</div>
                          {conflict.candidates.map((candidate, cidx) => (
                            <div key={cidx} className="ml-4 text-xs text-slate-500">
                              {candidate.match_type}: {candidate.customer.name} / {candidate.customer.country}
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="flex justify-end gap-2">
                    <button onClick={() => setWizardStep('validate')} className="px-4 py-2 border border-slate-300 rounded-lg text-sm hover:bg-slate-50">Back</button>
                    <button onClick={handleWizardConfirm} disabled={importing} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700 inline-flex items-center gap-2">
                      {importing && <Loader2 className="animate-spin" size={16} />}
                      {importing ? t('customer.importing') || 'Importing...' : t('customer.confirmImport') || 'Confirm Import'}
                    </button>
                  </div>
                </div>
              )}

              {wizardStep === 'confirm' && importResult && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-500 uppercase mb-3">{t('customer.importSummary') || 'Import Summary'}</h3>
                  <div className="grid grid-cols-3 gap-3 mb-4 text-sm">
                    <div className="border border-slate-200 rounded-lg p-3 text-center">
                      <div className="text-lg font-semibold text-emerald-700">{importResult.imported}</div>
                      <div className="text-slate-500">{t('customer.importedCount') || 'Imported'}</div>
                    </div>
                    <div className="border border-slate-200 rounded-lg p-3 text-center">
                      <div className="text-lg font-semibold text-amber-700">{importResult.skipped}</div>
                      <div className="text-slate-500">{t('customer.skippedCount') || 'Skipped'}</div>
                    </div>
                    <div className="border border-slate-200 rounded-lg p-3 text-center">
                      <div className="text-lg font-semibold text-red-700">{importResult.errors.length}</div>
                      <div className="text-slate-500">{t('customer.errorCount') || 'Errors'}</div>
                    </div>
                  </div>
                  {importResult.errors.length > 0 && (
                    <div className="border border-red-200 rounded-lg p-3 text-sm text-red-700 mb-4">
                      {importResult.errors.map((err) => <div key={err.row}>Row {err.row}: {err.error}</div>)}
                    </div>
                  )}
                  <div className="flex justify-end">
                    <button onClick={() => { setShowWizard(false); setPreview(null); setImportResult(null); }} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700">{t('common.save') || 'Close'}</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
