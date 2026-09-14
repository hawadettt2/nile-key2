import { describe, it, expect } from 'vitest';
import { parseIntentContent } from '@/lib/avatarResultParser';

const buildIntentContent = (overrides: Record<string, unknown> = {}): string => {
  const base = {
    intent_type: 'mission_completed',
    content: {
      outcome: 'Export mission completed',
      result: {
        mission_status: 'completed',
        goal: 'Export vegetables to Jordan',
        summary: 'Mission completed successfully.',
        results: [
          {
            data: {
              findings: ['Finding 1', 'Finding 2'],
              sources_consulted: ['Source A', 'Source B'],
            },
          },
        ],
      },
      progress: {},
    },
    context: {
      session_id: 'session-123',
      mission_id: 'mission-456',
    },
    suggested_actions: ['view_result', 'create_another'],
  };
  return JSON.stringify({ ...base, ...overrides });
};

describe('parseIntentContent', () => {
  it('parses full structured IntentContent', () => {
    const raw = buildIntentContent();
    const result = parseIntentContent(raw);
    expect(result.intentType).toBe('mission_completed');
    expect(result.missionStatus).toBe('completed');
    expect(result.suggestedActions).toEqual(['view_result', 'create_another']);
    expect(result.statusLabel).toBe('مكتملة');
    expect(result.goal).toBe('Export vegetables to Jordan');
    expect(result.outcome).toBe('Export mission completed');
    expect(result.summary).toBe('Mission completed successfully.');
    expect(result.findings).toEqual(['Finding 1', 'Finding 2']);
    expect(result.sources).toEqual(['Source A', 'Source B']);
    expect(result.missionId).toBe('mission-456');
    expect(result.sessionId).toBe('session-123');
    expect(result.hasStructuredContent).toBe(true);
    expect(result.rawResponse).toBe(raw);
  });

  it('returns fallback for malformed JSON', () => {
    const raw = 'not valid json';
    const result = parseIntentContent(raw);
    expect(result.intentType).toBe('');
    expect(result.hasStructuredContent).toBe(false);
    expect(result.rawResponse).toBe(raw);
  });

  it('returns fallback for null/undefined input', () => {
    expect(parseIntentContent('').hasStructuredContent).toBe(false);
    expect(parseIntentContent('   ').hasStructuredContent).toBe(false);
  });

  it('maps failed intent to failed label', () => {
    const raw = buildIntentContent({ intent_type: 'mission_failed' });
    const result = parseIntentContent(raw);
    expect(result.statusLabel).toBe('فشلت');
  });

  it('maps approval_required intent to approval label', () => {
    const raw = buildIntentContent({ intent_type: 'approval_required' });
    const result = parseIntentContent(raw);
    expect(result.statusLabel).toBe('تتطلب موافقة');
  });

  it('maps unknown intent to unknown label', () => {
    const raw = buildIntentContent({ intent_type: 'unknown_type' });
    const result = parseIntentContent(raw);
    expect(result.statusLabel).toBe('غير معروف');
  });

  it('returns unknown label for empty intent_type', () => {
    const raw = buildIntentContent({ intent_type: '' });
    const result = parseIntentContent(raw);
    expect(result.statusLabel).toBe('غير معروف');
  });

  it('aggregates findings and sources from all results', () => {
    const raw = buildIntentContent({
      content: {
        outcome: 'done',
        result: {
          mission_status: 'completed',
          results: [
            { data: { findings: ['F1'], sources_consulted: ['S1'] } },
            { data: { findings: ['F2'], sources_consulted: ['S2'] } },
          ],
        },
      },
    });
    const result = parseIntentContent(raw);
    expect(result.findings).toEqual(['F1', 'F2']);
    expect(result.sources).toEqual(['S1', 'S2']);
  });

  it('handles missing results array', () => {
    const raw = buildIntentContent({
      content: {
        outcome: 'done',
        result: {
          mission_status: 'completed',
          results: null,
        },
      },
    });
    const result = parseIntentContent(raw);
    expect(result.findings).toEqual([]);
    expect(result.sources).toEqual([]);
  });

  it('handles missing content.result', () => {
    const raw = buildIntentContent({
      content: {
        outcome: 'done',
      },
    });
    const result = parseIntentContent(raw);
    expect(result.goal).toBe('');
    expect(result.summary).toBe('');
    expect(result.findings).toEqual([]);
    expect(result.sources).toEqual([]);
  });

  it('handles missing context', () => {
    const raw = buildIntentContent({
      context: null,
    });
    const result = parseIntentContent(raw);
    expect(result.missionId).toBeNull();
    expect(result.sessionId).toBeNull();
  });

  it('handles missing suggested_actions', () => {
    const raw = buildIntentContent({
      suggested_actions: null,
    });
    const result = parseIntentContent(raw);
    expect(result.suggestedActions).toEqual([]);
  });

  it('preserves original values unchanged', () => {
    const raw = buildIntentContent();
    const result = parseIntentContent(raw);
    expect(result.intentType).toBe('mission_completed');
    expect(result.missionStatus).toBe('completed');
    expect(result.suggestedActions).toEqual(['view_result', 'create_another']);
  });

  it('handles non-object parsed JSON', () => {
    const raw = JSON.stringify('just a string');
    const result = parseIntentContent(raw);
    expect(result.hasStructuredContent).toBe(false);
    expect(result.rawResponse).toBe(raw);
  });

  it('handles array JSON', () => {
    const raw = JSON.stringify([1, 2, 3]);
    const result = parseIntentContent(raw);
    expect(result.hasStructuredContent).toBe(false);
    expect(result.rawResponse).toBe(raw);
  });

  it('returns hasStructuredContent false when all fields empty', () => {
    const raw = JSON.stringify({
      intent_type: 'mission_unknown',
      content: { outcome: '', result: {} },
      context: {},
      suggested_actions: [],
    });
    const result = parseIntentContent(raw);
    expect(result.hasStructuredContent).toBe(false);
  });

  it('returns hasStructuredContent true when at least one field present', () => {
    const raw = JSON.stringify({
      intent_type: 'mission_completed',
      content: { outcome: 'ok' },
      context: {},
      suggested_actions: [],
    });
    const result = parseIntentContent(raw);
    expect(result.hasStructuredContent).toBe(true);
  });

  it('parses business_answer as primary source when present', () => {
    const raw = JSON.stringify({
      intent_type: 'mission_completed',
      content: {
        outcome: 'legacy outcome',
        business_answer: {
          goal: 'BI Goal',
          executive_summary: 'BI Executive Summary',
          key_findings: [
            { topic: 'Finding Topic 1', content: 'Finding Content 1' },
            { content: 'Finding Content 2' },
          ],
          sources: ['BI Source A', 'BI Source B'],
        },
        result: {
          mission_status: 'completed',
          goal: 'Legacy Goal',
          summary: 'Legacy Summary',
          results: [
            {
              data: {
                findings: ['Legacy Finding'],
                sources_consulted: ['Legacy Source'],
              },
            },
          ],
        },
      },
      context: {
        session_id: 'session-123',
        mission_id: 'mission-456',
      },
      suggested_actions: ['view_result'],
    });
    const result = parseIntentContent(raw);
    expect(result.goal).toBe('BI Goal');
    expect(result.summary).toBe('BI Executive Summary');
    expect(result.findings).toEqual(['Finding Content 1', 'Finding Content 2']);
    expect(result.sources).toEqual(['BI Source A', 'BI Source B']);
  });

  it('falls back to legacy result when business_answer is absent', () => {
    const raw = JSON.stringify({
      intent_type: 'mission_completed',
      content: {
        outcome: 'legacy outcome',
        result: {
          mission_status: 'completed',
          goal: 'Legacy Goal',
          summary: 'Legacy Summary',
          results: [
            {
              data: {
                findings: ['Legacy Finding'],
                sources_consulted: ['Legacy Source'],
              },
            },
          ],
        },
      },
      context: {
        session_id: 'session-123',
        mission_id: 'mission-456',
      },
      suggested_actions: ['view_result'],
    });
    const result = parseIntentContent(raw);
    expect(result.goal).toBe('Legacy Goal');
    expect(result.summary).toBe('Legacy Summary');
    expect(result.findings).toEqual(['Legacy Finding']);
    expect(result.sources).toEqual(['Legacy Source']);
  });

  it('uses legacy result fields when business_answer has partial data', () => {
    const raw = JSON.stringify({
      intent_type: 'mission_completed',
      content: {
        outcome: 'legacy outcome',
        business_answer: {
          executive_summary: 'BI Summary Only',
        },
        result: {
          mission_status: 'completed',
          goal: 'Legacy Goal',
          summary: 'Legacy Summary',
          results: [
            {
              data: {
                findings: ['Legacy Finding'],
                sources_consulted: ['Legacy Source'],
              },
            },
          ],
        },
      },
      context: {},
      suggested_actions: [],
    });
    const result = parseIntentContent(raw);
    expect(result.summary).toBe('BI Summary Only');
    expect(result.goal).toBe('Legacy Goal');
    expect(result.findings).toEqual(['Legacy Finding']);
    expect(result.sources).toEqual(['Legacy Source']);
  });

  it('handles empty business_answer object gracefully', () => {
    const raw = JSON.stringify({
      intent_type: 'mission_completed',
      content: {
        outcome: 'legacy outcome',
        business_answer: {},
        result: {
          mission_status: 'completed',
          goal: 'Legacy Goal',
          summary: 'Legacy Summary',
        },
      },
      context: {},
      suggested_actions: [],
    });
    const result = parseIntentContent(raw);
    expect(result.goal).toBe('Legacy Goal');
    expect(result.summary).toBe('Legacy Summary');
  });

  it('parses full business_answer BI sections when present', () => {
    const raw = JSON.stringify({
      intent_type: 'mission_completed',
      content: {
        outcome: 'research completed successfully',
        business_answer: {
          goal: 'export vegetables Egypt Jordan',
          executive_summary: '4 structured finding(s) were identified.',
          key_findings: [
            {
              topic: '[trade_intelligence] Findings from un-comtrade',
              content: 'Retrieved 1 evidence item(s) from source un-comtrade.',
              confidence: null,
              limitations: null,
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
            criteria: ['volume', 'growth'],
            results: [
              {
                option: 'Egypt',
                criterion: 'volume',
                value: 28496743.65,
                evidence: [],
              },
            ],
            limitations: ['Limited to 2025 data'],
          },
          rankings: [
            {
              rank: 1,
              candidate: 'Egypt-Jordan route',
              criteria_scores: { volume: 0.9 },
              total_score: 0.9,
              evidence: [],
              explanation: 'Top route by volume',
              limitations: [],
            },
          ],
          opportunities: [
            {
              description: 'Growing demand in Jordan',
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
          confidence: null,
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
          sources: ['un-comtrade'],
          provenance: { research_status: 'completed' },
        },
        result: {
          mission_status: 'completed',
          goal: 'Legacy Goal',
          summary: 'Legacy Summary',
          results: [],
        },
      },
      context: {
        session_id: 'session-123',
        mission_id: 'mission-456',
      },
      suggested_actions: ['view_result'],
    });
    const result = parseIntentContent(raw);
    expect(result.goal).toBe('export vegetables Egypt Jordan');
    expect(result.summary).toBe('4 structured finding(s) were identified.');
    expect(result.findings).toEqual([
      'Retrieved 1 evidence item(s) from source un-comtrade.',
    ]);
    expect(result.sources).toEqual(['un-comtrade']);
    expect(result.businessAnswer.executiveSummary).toBe('4 structured finding(s) were identified.');
    expect(result.businessAnswer.keyFindings).toHaveLength(1);
    expect(result.businessAnswer.keyFindings[0].topic).toBe('[trade_intelligence] Findings from un-comtrade');
    expect(result.businessAnswer.entities).toHaveLength(1);
    expect(result.businessAnswer.entities[0].name).toBe('Egypt');
    expect(result.businessAnswer.comparisons?.options).toEqual(['Egypt', 'Jordan']);
    expect(result.businessAnswer.rankings).toHaveLength(1);
    expect(result.businessAnswer.opportunities).toHaveLength(1);
    expect(result.businessAnswer.risks).toHaveLength(1);
    expect(result.businessAnswer.recommendations).toHaveLength(1);
    expect(result.businessAnswer.confidence).toBeNull();
    expect(result.businessAnswer.limitations).toEqual(['No structured research findings are available.']);
    expect(result.businessAnswer.evidence).toHaveLength(1);
    expect(result.businessAnswer.provenance).toEqual({ research_status: 'completed' });
  });

  it('returns empty businessAnswer when business_answer is absent', () => {
    const raw = JSON.stringify({
      intent_type: 'mission_completed',
      content: {
        outcome: 'legacy outcome',
        result: {
          mission_status: 'completed',
          goal: 'Legacy Goal',
          summary: 'Legacy Summary',
          results: [
            {
              data: {
                findings: ['Legacy Finding'],
                sources_consulted: ['Legacy Source'],
              },
            },
          ],
        },
      },
      context: {},
      suggested_actions: [],
    });
    const result = parseIntentContent(raw);
    expect(result.businessAnswer.keyFindings).toEqual([]);
    expect(result.businessAnswer.entities).toEqual([]);
    expect(result.businessAnswer.opportunities).toEqual([]);
    expect(result.businessAnswer.risks).toEqual([]);
    expect(result.businessAnswer.recommendations).toEqual([]);
    expect(result.businessAnswer.limitations).toEqual([]);
    expect(result.businessAnswer.evidence).toEqual([]);
    expect(result.businessAnswer.comparisons).toBeNull();
    expect(result.businessAnswer.rankings).toBeNull();
  });
});
