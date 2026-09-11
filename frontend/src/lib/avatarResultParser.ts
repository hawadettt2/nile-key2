export interface ParsedAvatarResult {
  intentType: string;
  missionStatus: string;
  suggestedActions: string[];
  statusLabel: string;
  goal: string;
  outcome: string;
  summary: string;
  findings: string[];
  sources: string[];
  missionId: string | null;
  sessionId: string | null;
  hasStructuredContent: boolean;
  rawResponse: string;
}

function safeString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function safeStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === 'string');
}

function extractFindings(result: Record<string, unknown>): string[] {
  const resultsArray = Array.isArray(result.results) ? result.results : [];
  const findings: string[] = [];
  for (const item of resultsArray) {
    if (!item || typeof item !== 'object') continue;
    const candidate = (item as Record<string, unknown>).data;
    if (!candidate || typeof candidate !== 'object') continue;
    const rawFindings = (candidate as Record<string, unknown>).findings;
    findings.push(...safeStringArray(rawFindings));
  }
  return findings;
}

function extractSources(result: Record<string, unknown>): string[] {
  const resultsArray = Array.isArray(result.results) ? result.results : [];
  const sources: string[] = [];
  for (const item of resultsArray) {
    if (!item || typeof item !== 'object') continue;
    const candidate = (item as Record<string, unknown>).data;
    if (!candidate || typeof candidate !== 'object') continue;
    const rawSources = (candidate as Record<string, unknown>).sources_consulted;
    sources.push(...safeStringArray(rawSources));
  }
  return sources;
}

function mapIntentTypeToDisplayLabel(intentType: string): string {
  const normalized = intentType.toLowerCase();
  if (normalized.includes('completed')) return 'مكتملة';
  if (normalized.includes('failed')) return 'فشلت';
  if (normalized.includes('approval')) return 'تتطلب موافقة';
  if (normalized.includes('unknown')) return 'غير معروف';
  return intentType || 'غير معروف';
}

export function parseIntentContent(raw: string): ParsedAvatarResult {
  const fallback: ParsedAvatarResult = {
    intentType: '',
    missionStatus: '',
    suggestedActions: [],
    statusLabel: 'غير معروف',
    goal: '',
    outcome: '',
    summary: '',
    findings: [],
    sources: [],
    missionId: null,
    sessionId: null,
    hasStructuredContent: false,
    rawResponse: raw,
  };

  if (!raw || typeof raw !== 'string') {
    return fallback;
  }

  let parsed: Record<string, unknown>;
  try {
    parsed = JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return { ...fallback, rawResponse: raw };
  }

  if (!parsed || typeof parsed !== 'object') {
    return { ...fallback, rawResponse: raw };
  }

  const intentType = safeString(parsed.intent_type);
  const content = (parsed.content as Record<string, unknown>) || {};
  const result = (content.result as Record<string, unknown>) || {};
  const context = (parsed.context as Record<string, unknown>) || {};
  const suggestedActions = safeStringArray(parsed.suggested_actions);

  const outcome = safeString(content.outcome);
  const missionStatus = safeString(result.mission_status);
  const goal = safeString(result.goal);
  const summary = safeString(result.summary);
  const findings = extractFindings(result);
  const sources = extractSources(result);
  const missionId = safeString(context.mission_id) || null;
  const sessionId = safeString(context.session_id) || null;

  const hasStructuredContent = Boolean(
    outcome || goal || summary || findings.length > 0 || sources.length > 0 || missionId || suggestedActions.length > 0
  );

  return {
    intentType,
    missionStatus,
    suggestedActions,
    statusLabel: mapIntentTypeToDisplayLabel(intentType),
    goal,
    outcome,
    summary,
    findings,
    sources,
    missionId,
    sessionId,
    hasStructuredContent,
    rawResponse: raw,
  };
}
