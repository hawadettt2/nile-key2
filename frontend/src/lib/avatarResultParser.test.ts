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
});
