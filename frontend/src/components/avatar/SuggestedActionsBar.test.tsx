import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslations from '@/locales/en/translation.json';
import arTranslations from '@/locales/ar/translation.json';
import { SuggestedActionsBar } from '@/components/avatar/SuggestedActionsBar';
import { ParsedAvatarResult } from '@/lib/avatarResultParser';

function createI18n(lng: 'ar' | 'en' = 'ar') {
  const instance = i18n.createInstance();
  instance.use(initReactI18next).init({
    resources: {
      en: { translation: enTranslations },
      ar: { translation: arTranslations },
    },
    lng,
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });
  return instance;
}

function WrapperArabic({ children }: { children: React.ReactNode }) {
  const i18nInstance = createI18n('ar');
  return (
    <BrowserRouter>
      <I18nextProvider i18n={i18nInstance}>{children}</I18nextProvider>
    </BrowserRouter>
  );
}

function WrapperEnglish({ children }: { children: React.ReactNode }) {
  const i18nInstance = createI18n('en');
  return (
    <BrowserRouter>
      <I18nextProvider i18n={i18nInstance}>{children}</I18nextProvider>
    </BrowserRouter>
  );
}

const baseParsed: ParsedAvatarResult = {
  intentType: 'mission_completed',
  missionStatus: 'completed',
  suggestedActions: ['view_result', 'create_another', 'retry', 'view_error'],
  statusLabel: 'مكتملة',
  goal: '',
  outcome: '',
  summary: '',
  findings: [],
  sources: [],
  missionId: 'mission-123',
  sessionId: 'session-456',
  hasStructuredContent: true,
  rawResponse: '{}',
};

describe('SuggestedActionsBar', () => {
  it('renders suggested actions in Arabic', () => {
    const onAction = vi.fn();
    render(<SuggestedActionsBar parsed={baseParsed} locale="ar" onAction={onAction} />, { wrapper: WrapperArabic });
    expect(screen.getByText('عرض النتيجة')).toBeDefined();
    expect(screen.getByText('إنشاء مهمة جديدة')).toBeDefined();
  });

  it('calls onAction when enabled button clicked', () => {
    const onAction = vi.fn();
    render(<SuggestedActionsBar parsed={baseParsed} locale="ar" onAction={onAction} />, { wrapper: WrapperArabic });
    fireEvent.click(screen.getByText('إنشاء مهمة جديدة'));
    expect(onAction).toHaveBeenCalledWith('create_another');
  });

  it('disables view_result when missionId missing', () => {
    const onAction = vi.fn();
    const parsed = { ...baseParsed, missionId: null };
    render(<SuggestedActionsBar parsed={parsed} locale="ar" onAction={onAction} disabledActions={{ view_result: { disabled: true, reason: 'needs mission' } }} />, { wrapper: WrapperArabic });
    const button = screen.getByText('عرض النتيجة').closest('button');
    expect(button?.hasAttribute('disabled')).toBe(true);
  });

  it('does not call onAction for disabled button', () => {
    const onAction = vi.fn();
    render(<SuggestedActionsBar parsed={baseParsed} locale="ar" onAction={onAction} disabledActions={{ view_result: { disabled: true, reason: 'needs mission' } }} />, { wrapper: WrapperArabic });
    fireEvent.click(screen.getByText('عرض النتيجة'));
    expect(onAction).not.toHaveBeenCalled();
  });

  it('returns null when no suggested actions', () => {
    const onAction = vi.fn();
    const parsed = { ...baseParsed, suggestedActions: [] };
    const { container } = render(<SuggestedActionsBar parsed={parsed} locale="ar" onAction={onAction} />, { wrapper: WrapperArabic });
    expect(container.firstChild).toBeNull();
  });

  it('renders English labels when locale is en', () => {
    const onAction = vi.fn();
    render(<SuggestedActionsBar parsed={baseParsed} locale="en" onAction={onAction} />, { wrapper: WrapperEnglish });
    expect(screen.getByText('View Result')).toBeDefined();
  });
});
