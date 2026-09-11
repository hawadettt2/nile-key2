import { useTranslation } from 'react-i18next';
import { ParsedAvatarResult } from '@/lib/avatarResultParser';

interface ExecutiveResultCardProps {
  parsed: ParsedAvatarResult;
  rawResponse: string;
  locale: 'ar' | 'en';
}

export function ExecutiveResultCard({ parsed, locale }: ExecutiveResultCardProps) {
  const { t } = useTranslation();

  return (
    <div dir={locale === 'ar' ? 'rtl' : 'ltr'} className="space-y-4 text-sm text-slate-700">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.status')}</p>
          <p className="text-sm font-medium text-slate-800">{parsed.statusLabel}</p>
        </div>
        {parsed.missionStatus && (
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
            <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.mission_status')}</p>
            <p className="text-sm font-medium text-slate-800">{parsed.missionStatus}</p>
          </div>
        )}
      </div>

      {parsed.goal && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.goal')}</p>
          <p className="text-sm text-slate-800">{parsed.goal}</p>
        </div>
      )}

      {parsed.outcome && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.outcome')}</p>
          <p className="text-sm text-slate-800">{parsed.outcome}</p>
        </div>
      )}

      {parsed.summary && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.summary')}</p>
          <p className="text-sm text-slate-800 whitespace-pre-wrap">{parsed.summary}</p>
        </div>
      )}

      {parsed.findings.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.findings')}</p>
          <ul className="list-disc list-inside space-y-1 text-sm text-slate-800">
            {parsed.findings.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {parsed.sources.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.sources')}</p>
          <div className="flex flex-wrap gap-2">
            {parsed.sources.map((source, idx) => (
              <span key={idx} className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-xs font-medium text-slate-700">
                {source}
              </span>
            ))}
          </div>
        </div>
      )}

      {(parsed.missionId || parsed.sessionId) && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.identifiers')}</p>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600 font-mono">
            {parsed.missionId && <span>{t('avatar.identifiers.mission_id')}: {parsed.missionId}</span>}
            {parsed.sessionId && <span>{t('avatar.identifiers.session_id')}: {parsed.sessionId}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
