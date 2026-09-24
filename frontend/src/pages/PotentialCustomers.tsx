import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  listPotentialCustomerCountries,
  type PotentialCustomerCountry,
} from '@/services/api';
import {
  FolderOpen,
  FileSpreadsheet,
  ExternalLink,
  ChevronRight,
  Globe,
  Loader2,
  ArrowLeft,
} from 'lucide-react';

function formatBytes(bytes?: number): string {
  if (!bytes) return '-';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value?: string): string {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' });
}

type ViewMode = 'countries' | 'country-detail';

export function PotentialCustomers() {
  const { t, i18n } = useTranslation();
  const [view, setView] = useState<ViewMode>('countries');
  const [countries, setCountries] = useState<PotentialCustomerCountry[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<PotentialCustomerCountry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openFileId, setOpenFileId] = useState<string | null>(null);

  const loadCountries = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listPotentialCustomerCountries();
      setCountries(res.data.countries || []);
      if (res.data.error) {
        setError(res.data.error);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load potential customers.');
      setCountries([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCountries();
  }, []);

  const openCountry = async (country: PotentialCustomerCountry) => {
    setSelectedCountry(country);
    setView('country-detail');
    setOpenFileId(null);
  };

  const backToCountries = () => {
    setView('countries');
    setSelectedCountry(null);
    setOpenFileId(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="animate-spin" size={20} />
          <span>{t('common.loading') || 'Loading...'}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div dir={i18n.language === 'ar' ? 'rtl' : 'ltr'} className="max-w-3xl mx-auto mt-10">
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-6 text-sm">
          <h2 className="text-lg font-semibold mb-2">Potential Customers data unavailable</h2>
          <p className="mb-2">Real data import from Google Drive is required to use this page.</p>
          <p className="mb-2">Error: {error}</p>
          <p className="text-xs text-red-600">
            To enable real data import, provide Google Drive credentials via one of:
            <br />- GOOGLE_SERVICE_ACCOUNT_JSON environment variable
            <br />- GOOGLE_OAUTH_CREDENTIALS_JSON environment variable
            <br />Then run: python scripts/import_google_drive.py
          </p>
        </div>
      </div>
    );
  }

  if (view === 'country-detail' && selectedCountry) {
    return (
      <div dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={backToCountries}
            className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-3 py-2 rounded-lg transition-colors"
          >
            <ArrowLeft size={16} />
            {t('common.back') || 'Back'}
          </button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{selectedCountry.name}</h1>
            <p className="text-sm text-slate-500">
              {selectedCountry.file_count} {t('common.files') || 'files'}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {selectedCountry.files.map((file) => (
            <div
              key={file.id}
              className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
            >
              <div className="flex items-center justify-between p-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-emerald-50 rounded-lg">
                    <FileSpreadsheet className="text-emerald-600" size={22} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">{file.name}</h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1">
                      {file.source && (
                        <span className="inline-flex items-center gap-1">
                          <Globe size={12} /> {file.source}
                        </span>
                      )}
                      {file.sheet_count != null && (
                        <span>{file.sheet_count} sheets</span>
                      )}
                      {file.row_count != null && (
                        <span>{file.row_count.toLocaleString()} rows</span>
                      )}
                      <span>{formatBytes(file.size_bytes)}</span>
                      <span>Modified: {formatDate(file.modified_time)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setOpenFileId(openFileId === file.id ? null : file.id)}
                    className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg transition-colors"
                  >
                    {openFileId === file.id ? 'Hide Details' : 'Details'}
                  </button>
                  {file.view_url && (
                    <a
                      href={file.view_url}
                      target="_blank"
                      rel="noreferrer noopener"
                      className="inline-flex items-center gap-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-2 rounded-lg transition-colors"
                    >
                      <ExternalLink size={14} />
                      Open
                    </a>
                  )}
                </div>
              </div>

              {openFileId === file.id && (
                <div className="border-t border-slate-100 bg-slate-50 p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-slate-500">File ID: </span>
                      <span className="font-mono text-slate-700">{file.id}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Source: </span>
                      <span className="text-slate-700">{file.source || '-'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Sheets: </span>
                      <span className="text-slate-700">{file.sheet_count ?? '-'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Rows: </span>
                      <span className="text-slate-700">{file.row_count?.toLocaleString() || '-'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Size: </span>
                      <span className="text-slate-700">{formatBytes(file.size_bytes)}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Created: </span>
                      <span className="text-slate-700">{formatDate(file.created_time)}</span>
                    </div>
                    <div className="md:col-span-2">
                      <span className="text-slate-500">Modified: </span>
                      <span className="text-slate-700">{formatDate(file.modified_time)}</span>
                    </div>
                  </div>
                  {file.view_url && (
                    <div className="mt-4">
                      <a
                        href={file.view_url}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                      >
                        <ExternalLink size={16} />
                        Open in Google Drive
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {selectedCountry.files.length === 0 && (
            <div className="bg-white rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
              {t('common.noData') || 'No files found for this country.'}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Potential Customers</h1>
          <p className="text-sm text-slate-500">
            {countries.length} {t('common.countries') || 'countries'} · {countries.reduce((sum, c) => sum + c.file_count, 0)} files
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {countries.map((country) => (
          <button
            key={country.id}
            onClick={() => openCountry(country)}
            className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 text-left hover:border-blue-300 hover:shadow-md transition-all group"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                  <FolderOpen className="text-blue-600" size={22} />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">{country.name}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {country.file_count} {country.file_count === 1 ? 'file' : 'files'}
                  </p>
                </div>
              </div>
              <ChevronRight className="text-slate-400 group-hover:text-blue-500 transition-colors" size={18} />
            </div>
          </button>
        ))}
      </div>

      {countries.length === 0 && (
        <div className="bg-white rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
          {t('common.noData') || 'No countries found.'}
        </div>
      )}
    </div>
  );
}
