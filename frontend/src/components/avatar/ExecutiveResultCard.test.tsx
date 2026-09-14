import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslations from '@/locales/en/translation.json';
import arTranslations from '@/locales/ar/translation.json';
import { ExecutiveResultCard } from '@/components/avatar/ExecutiveResultCard';
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
  suggestedActions: [],
  statusLabel: 'مكتملة',
  goal: 'Goal text',
  outcome: 'Outcome text',
  summary: 'Summary text',
  findings: ['Finding 1'],
  sources: ['Source A'],
  missionId: 'mission-123',
  sessionId: 'session-456',
  hasStructuredContent: true,
  rawResponse: '{}',
  businessAnswer: {
    keyFindings: [],
    entities: [],
    opportunities: [],
    risks: [],
    recommendations: [],
    limitations: [],
    evidence: [],
    comparisons: null,
    rankings: null,
    provenance: null,
  },
};

describe('ExecutiveResultCard', () => {
  it('renders status section in Arabic', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('مكتملة')).toBeDefined();
  });

  it('renders mission status when present', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('completed')).toBeDefined();
  });

  it('renders goal section', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('Goal text')).toBeDefined();
  });

  it('renders outcome section', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('Outcome text')).toBeDefined();
  });

  it('renders summary section', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('Summary text')).toBeDefined();
  });

  it('renders findings list', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('Finding 1')).toBeDefined();
  });

  it('renders sources chips', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('Source A')).toBeDefined();
  });

  it('renders identifiers', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText(/mission-123/)).toBeDefined();
    expect(screen.getByText(/session-456/)).toBeDefined();
  });

  it('does not render mission status when empty', () => {
    const parsed = { ...baseParsed, missionStatus: '' };
    render(<ExecutiveResultCard parsed={parsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.queryByText('completed')).toBeNull();
  });

  it('does not render goal when empty', () => {
    const parsed = { ...baseParsed, goal: '' };
    render(<ExecutiveResultCard parsed={parsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.queryByText('Goal text')).toBeNull();
  });

  it('does not render outcome when empty', () => {
    const parsed = { ...baseParsed, outcome: '' };
    render(<ExecutiveResultCard parsed={parsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.queryByText('Outcome text')).toBeNull();
  });

  it('does not render summary when empty', () => {
    const parsed = { ...baseParsed, summary: '' };
    render(<ExecutiveResultCard parsed={parsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.queryByText('Summary text')).toBeNull();
  });

  it('does not render findings when empty', () => {
    const parsed = { ...baseParsed, findings: [] };
    render(<ExecutiveResultCard parsed={parsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.queryByText('Finding 1')).toBeNull();
  });

  it('does not render sources when empty', () => {
    const parsed = { ...baseParsed, sources: [] };
    render(<ExecutiveResultCard parsed={parsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.queryByText('Source A')).toBeNull();
  });

  it('renders in English when locale is en', () => {
    render(<ExecutiveResultCard parsed={baseParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getByText('Status')).toBeDefined();
    expect(screen.getByText('Goal')).toBeDefined();
  });

  it('renders BI-parsed summary, findings, and sources', () => {
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      summary: 'BI Executive Summary',
      findings: ['BI Finding 1', 'BI Finding 2'],
      sources: ['BI Source A'],
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('BI Executive Summary')).toBeDefined();
    expect(screen.getByText('BI Finding 1')).toBeDefined();
    expect(screen.getByText('BI Finding 2')).toBeDefined();
    expect(screen.getByText('BI Source A')).toBeDefined();
  });

  it('renders BI optional sections when present', () => {
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [
          {
            topic: 'Trade Intelligence',
            content: 'Retrieved 1 evidence item(s) from source un-comtrade.',
            evidence: [
              {
                source_id: 'un-comtrade',
                source_url: '2026-08-15',
                content_excerpt: 'HS 07 ...',
              },
            ],
          },
        ],
        entities: [
          {
            name: 'Egypt',
            type: 'country',
            attributes: { code: '818' },
            evidence: [],
          },
        ],
        comparisons: {
          options: ['Egypt', 'Jordan'],
          criteria: ['volume'],
          results: [
            {
              option: 'Jordan',
              criterion: 'volume',
              value: 1000,
              evidence: [],
            },
          ],
          limitations: ['Limited data'],
        },
        rankings: [
          {
            rank: 1,
            candidate: 'Egypt-Jordan',
            criteria_scores: { volume: 0.9 },
            total_score: 0.9,
            evidence: [],
            limitations: [],
          },
        ],
        opportunities: [
          {
            description: 'Growing demand',
            evidence: [],
            confidence: 0.8,
            limitations: null,
          },
        ],
        risks: [
          {
            description: 'Tariff changes',
            evidence: [],
            severity: 'medium',
            mitigation: 'Monitor regulations',
            limitations: null,
          },
        ],
        recommendations: [
          {
            action: 'Review tariffs',
            type: 'next_evidence_requirement',
            rationale: 'Tariff data needed',
            evidence: [],
            confidence: null,
            limitations: null,
          },
        ],
        confidence: 0.7,
        limitations: ['No structured research findings are available.'],
        evidence: [
          {
            source_id: 'un-comtrade',
            source_url: '2026-08-15',
            content_excerpt: 'HS 07 ...',
            retrieval_timestamp: '2026-09-14T12:57:54.075566',
            confidence: null,
            limitations: null,
            provenance: { research_status: 'completed' },
          },
        ],
        provenance: { research_status: 'completed' },
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.getByText('النتائج الرئيسية')).toBeDefined();
    expect(screen.getByText('Trade Intelligence')).toBeDefined();
    expect(screen.getByText('الكيانات')).toBeDefined();
    expect(screen.getByText('Egypt')).toBeDefined();
    expect(screen.getByText('المقارنات')).toBeDefined();
    expect(screen.getByText('التصنيفات')).toBeDefined();
    expect(screen.getByText('الفرص')).toBeDefined();
    expect(screen.getByText('المخاطر')).toBeDefined();
    expect(screen.getByText('التوصيات')).toBeDefined();
    expect(screen.getByText('مستوى الثقة')).toBeDefined();
    expect(screen.getByText('0.7')).toBeDefined();
    expect(screen.getByText('القيود')).toBeDefined();
    expect(screen.getByText('الأدلة')).toBeDefined();
  });

  it('does not render empty BI optional sections', () => {
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [],
        entities: [],
        opportunities: [],
        risks: [],
        recommendations: [],
        limitations: [],
        evidence: [],
        provenance: null,
        comparisons: null,
        rankings: null,
        confidence: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="ar" />, { wrapper: WrapperArabic });
    expect(screen.queryByText('النتائج الرئيسية')).toBeNull();
    expect(screen.queryByText('الكيانات')).toBeNull();
    expect(screen.queryByText('المقارنات')).toBeNull();
    expect(screen.queryByText('التصنيفات')).toBeNull();
    expect(screen.queryByText('الفرص')).toBeNull();
    expect(screen.queryByText('المخاطر')).toBeNull();
    expect(screen.queryByText('التوصيات')).toBeNull();
    expect(screen.queryByText('القيود')).toBeNull();
    expect(screen.queryByText('الأدلة')).toBeNull();
  });
});
