import { describe, it, expect, vi } from 'vitest';
import { render, screen, act, waitFor } from '@testing-library/react';
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

  it('renders evidence inside each key finding with source_url', () => {
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [
          {
            topic: 'Trade',
            content: 'Trade fact.',
            evidence: [
              {
                source_id: 'src-1',
                source_url: 'https://example.com/trade',
                content_excerpt: 'Excerpt trade',
              },
            ],
            limitations: ['Finding limitation'],
          },
        ],
        entities: [],
        opportunities: [],
        risks: [],
        recommendations: [],
        limitations: [],
        evidence: [],
        comparisons: null,
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getByText('src-1')).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('https://example.com/trade'))).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('Excerpt trade'))).toBeDefined();
    expect(screen.getByText('Finding limitation')).toBeDefined();
  });

   it('renders evidence inside each entity', () => {
     const biParsed: ParsedAvatarResult = {
       ...baseParsed,
       businessAnswer: {
         keyFindings: [],
         entities: [
           {
             name: 'Egypt',
             type: 'country',
             attributes: {},
             evidence: [
               {
                 source_id: 'src-2',
                 source_url: 'https://example.com/egypt',
                 content_excerpt: 'Egypt excerpt',
               },
             ],
           },
         ],
         opportunities: [],
         risks: [],
         recommendations: [],
         limitations: [],
         evidence: [],
         comparisons: null,
         rankings: null,
         confidence: null,
         provenance: null,
       },
     };
     render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
     expect(screen.getByText('Egypt')).toBeDefined();
     expect(screen.getByText('src-2')).toBeDefined();
     expect(screen.getByText((content, element) => content.includes('https://example.com/egypt'))).toBeDefined();
   });

  it('renders evidence per comparison result with limitations', () => {
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
        comparisons: {
          options: ['Egypt', 'Jordan'],
          criteria: ['volume'],
          results: [
            {
              option: 'Egypt',
              criterion: 'volume',
              value: 2000,
              evidence: [
                {
                  source_id: 'src-egypt',
                  source_url: 'https://example.com/egypt',
                  content_excerpt: 'Egypt volume',
                },
              ],
            },
            {
              option: 'Jordan',
              criterion: 'volume',
              value: 1000,
              evidence: [
                {
                  source_id: 'src-jordan',
                  source_url: 'https://example.com/jordan',
                  content_excerpt: 'Jordan volume',
                },
              ],
            },
          ],
          limitations: ['Comparison limitation'],
        },
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getByText('src-egypt')).toBeDefined();
    expect(screen.getByText('Egypt')).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('2000'))).toBeDefined();
    expect(screen.getByText('src-jordan')).toBeDefined();
    expect(screen.getByText('Jordan')).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('1000'))).toBeDefined();
    expect(screen.getByText('Comparison limitation')).toBeDefined();
  });

  it('renders ranking evidence, explanation, and limitations', () => {
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
        comparisons: null,
        rankings: [
          {
            rank: 1,
            candidate: 'Egypt',
            criteria_scores: { volume: 0.9 },
            total_score: 0.9,
            evidence: [
              {
                source_id: 'src-rank',
                source_url: 'https://example.com/rank',
                content_excerpt: 'Rank excerpt',
              },
            ],
            explanation: 'Top candidate due to volume',
            limitations: ['Ranking limitation'],
          },
        ],
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getByText('src-rank')).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('Rank excerpt'))).toBeDefined();
    expect(screen.getByText('Top candidate due to volume')).toBeDefined();
    expect(screen.getByText('Ranking limitation')).toBeDefined();
  });

  it('renders opportunity evidence and limitations', () => {
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [],
        entities: [],
        opportunities: [
          {
            description: 'Growing demand',
            evidence: [
              {
                source_id: 'src-opp',
                source_url: 'https://example.com/opp',
                content_excerpt: 'Opportunity excerpt',
              },
            ],
            confidence: 0.8,
            limitations: ['Opportunity limitation'],
          },
        ],
        risks: [],
        recommendations: [],
        limitations: [],
        evidence: [],
        comparisons: null,
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getByText('src-opp')).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('Opportunity excerpt'))).toBeDefined();
    expect(screen.getByText('Opportunity limitation')).toBeDefined();
  });

  it('renders risk evidence, severity, mitigation, and limitations', () => {
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [],
        entities: [],
        opportunities: [],
        risks: [
          {
            description: 'Tariff changes',
            evidence: [
              {
                source_id: 'src-risk',
                source_url: 'https://example.com/risk',
                content_excerpt: 'Risk excerpt',
              },
            ],
            severity: 'medium',
            mitigation: 'Monitor regulations',
            limitations: ['Risk limitation'],
          },
        ],
        recommendations: [],
        limitations: [],
        evidence: [],
        comparisons: null,
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getByText('src-risk')).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('Risk excerpt'))).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('severity: medium'))).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('Monitor regulations'))).toBeDefined();
    expect(screen.getByText('Risk limitation')).toBeDefined();
  });

  it('renders recommendation evidence and limitations', () => {
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [],
        entities: [],
        opportunities: [],
        risks: [],
        recommendations: [
          {
            action: 'Review tariffs',
            type: 'next_evidence_requirement',
            rationale: 'Tariff data needed',
            evidence: [
              {
                source_id: 'src-rec',
                source_url: 'https://example.com/rec',
                content_excerpt: 'Recommendation excerpt',
              },
            ],
            confidence: null,
            limitations: ['Recommendation limitation'],
          },
        ],
        limitations: [],
        evidence: [],
        comparisons: null,
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getByText('src-rec')).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('Recommendation excerpt'))).toBeDefined();
    expect(screen.getByText('Recommendation limitation')).toBeDefined();
  });

  it('does not render evidence sections when no evidence is present', () => {
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [
          {
            topic: 'Trade',
            content: 'Trade fact.',
            evidence: [],
          },
        ],
        entities: [
          {
            name: 'Egypt',
            type: 'country',
            attributes: {},
            evidence: [],
          },
        ],
        opportunities: [
          {
            description: 'Growing demand',
            evidence: [],
            confidence: 0.8,
          },
        ],
        risks: [
          {
            description: 'Tariff changes',
            evidence: [],
            severity: 'medium',
            mitigation: 'Monitor regulations',
          },
        ],
        recommendations: [
          {
            action: 'Review tariffs',
            type: 'next_evidence_requirement',
            rationale: 'Tariff data needed',
            evidence: [],
          },
        ],
        limitations: [],
        evidence: [],
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
          limitations: [],
        },
        rankings: [
          {
            rank: 1,
            candidate: 'Egypt',
            criteria_scores: {},
            total_score: null,
            evidence: [],
            limitations: [],
          },
        ],
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.queryByText('evidence')).toBeNull();
  });

  it('shows compact cross-reference when evidence is duplicated across sections', () => {
    const sharedEvidence = {
      source_id: 'src-shared',
      source_url: 'https://example.com/shared',
      content_excerpt: 'Shared excerpt',
    };
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [
          {
            topic: 'Trade',
            content: 'Trade fact.',
            evidence: [sharedEvidence],
          },
        ],
        entities: [
          {
            name: 'Egypt',
            type: 'country',
            attributes: {},
            evidence: [sharedEvidence],
          },
        ],
        opportunities: [],
        risks: [],
        recommendations: [],
        limitations: [],
        evidence: [],
        comparisons: null,
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getAllByText('src-shared').length).toBe(1);
    expect(screen.getAllByText((content, element) => content.includes('Also cited in')).length).toBe(1);
  });

  it('does not show cross-reference for unique evidence', () => {
    const uniqueEvidence = {
      source_id: 'src-unique',
      source_url: 'https://example.com/unique',
      content_excerpt: 'Unique excerpt',
    };
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [
          {
            topic: 'Trade',
            content: 'Trade fact.',
            evidence: [uniqueEvidence],
          },
        ],
        entities: [],
        opportunities: [],
        risks: [],
        recommendations: [],
        limitations: [],
        evidence: [],
        comparisons: null,
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getByText('src-unique')).toBeDefined();
    expect(screen.queryByText((content, element) => content.includes('Also cited in'))).toBeNull();
  });

  it('renders duplicated evidence once and shows cross-reference only in later sections', () => {
    const sharedEvidence = {
      source_id: 'src-shared',
      source_url: 'https://example.com/shared',
      content_excerpt: 'Shared excerpt',
    };
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [
          {
            topic: 'Trade',
            content: 'Trade fact.',
            evidence: [sharedEvidence],
          },
        ],
        entities: [
          {
            name: 'Egypt',
            type: 'country',
            attributes: {},
            evidence: [sharedEvidence],
          },
        ],
        opportunities: [],
        risks: [],
        recommendations: [],
        limitations: [],
        evidence: [],
        comparisons: null,
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getAllByText('src-shared').length).toBe(1);
    expect(screen.getAllByText((content, element) => content.includes('Also cited in')).length).toBe(1);
    expect(screen.queryByText((content, element) => content.includes('https://example.com/shared') && element.textContent?.includes('src-shared'))).toBeDefined();
  });

  it('groups evidence by source and allows drill-down', () => {
    const groupedEvidence = [
      {
        source_id: 'src-grouped',
        source_url: 'https://example.com/grouped',
        content_excerpt: 'First excerpt',
        retrieval_timestamp: '2026-09-14T12:57:54.075566',
        confidence: 0.8,
        limitations: ['Limitation 1'],
        provenance: { research_status: 'completed' },
      },
      {
        source_id: 'src-grouped',
        source_url: 'https://example.com/grouped',
        content_excerpt: 'Second excerpt',
        retrieval_timestamp: '2026-09-14T12:58:00.000000',
        confidence: 0.9,
        limitations: ['Limitation 2'],
        provenance: { research_status: 'completed' },
      },
    ];
    const biParsed: ParsedAvatarResult = {
      ...baseParsed,
      businessAnswer: {
        keyFindings: [
          {
            topic: 'Trade',
            content: 'Trade fact.',
            evidence: groupedEvidence,
          },
        ],
        entities: [],
        opportunities: [],
        risks: [],
        recommendations: [],
        limitations: [],
        evidence: [],
        comparisons: null,
        rankings: null,
        confidence: null,
        provenance: null,
      },
    };
    render(<ExecutiveResultCard parsed={biParsed} rawResponse="{}" locale="en" />, { wrapper: WrapperEnglish });
    expect(screen.getAllByText('src-grouped').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText((content, element) => content.includes('First excerpt'))).toBeDefined();
    expect(screen.queryByText((content, element) => content.includes('Second excerpt'))).toBeNull();
    expect(screen.getByText('Show more')).toBeDefined();
    act(() => {
      screen.getByText('Show more').click();
    });
    expect(screen.getByText((content, element) => content.includes('Second excerpt'))).toBeDefined();
    expect(screen.getByText('Show less')).toBeDefined();
    expect(screen.getByText('Retrieval Timestamp: 2026-09-14T12:57:54.075566')).toBeDefined();
    expect(screen.getByText('Confidence: 0.8')).toBeDefined();
    expect(screen.getByText((content, element) => content.includes('Limitation 1'))).toBeDefined();
    expect(screen.getAllByText(/Provenance:/).length).toBeGreaterThanOrEqual(2);
  });
});
