import { useTranslation } from 'react-i18next';
import { ParsedAvatarResult } from '@/lib/avatarResultParser';

interface SuggestedActionsBarProps {
  parsed: ParsedAvatarResult;
  locale: 'ar' | 'en';
  onAction: (action: string) => void;
  disabledActions?: Record<string, { disabled: boolean; reason?: string }>;
}

const ACTION_ICONS: Record<string, string> = {
  view_result: '📋',
  create_another: '➕',
  retry: '🔄',
  view_error: '⚠️',
  approve: '✅',
  reject: '❌',
  view_details: '📄',
};

export function SuggestedActionsBar({ parsed, locale, onAction, disabledActions = {} }: SuggestedActionsBarProps) {
  const { t } = useTranslation();

  if (!parsed.suggestedActions.length) return null;

  return (
    <div dir={locale === 'ar' ? 'rtl' : 'ltr'} className="bg-slate-50 border border-slate-100 rounded-xl p-3">
      <p className="text-xs font-semibold text-slate-500 mb-2">{t('avatar.fields.suggested_actions')}</p>
      <div className="flex flex-wrap gap-2">
        {parsed.suggestedActions.map((action) => {
          const disabledInfo = disabledActions[action];
          const isDisabled = Boolean(disabledInfo?.disabled);
          return (
            <button
              key={action}
              type="button"
              disabled={isDisabled}
              onClick={() => !isDisabled && onAction(action)}
              title={disabledInfo?.reason}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors ${
                isDisabled
                  ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                  : 'bg-white border-slate-200 text-slate-700 hover:border-emerald-300 hover:text-emerald-700'
              }`}
            >
              <span aria-hidden="true">{ACTION_ICONS[action] || '•'}</span>
              <span>{t(`avatar.actions.${action}`, action)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
