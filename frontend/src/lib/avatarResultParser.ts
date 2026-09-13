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
  recommendations: string[];
  risks: string[];
  opportunities: string[];
  limitations: string[];
  missionId: string | null;
  sessionId: string | null;
  hasStructuredContent: boolean;
  hasBusinessAnswer: boolean;
  rawResponse: string;
}

function safeString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function safeStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === 'string');
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : null;
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

function formatFinding(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) return value.trim();
  const finding = asRecord(value);
  if (!finding) return null;
  const content = safeString(finding.content).trim();
  const topic = safeString(finding.topic).trim();
  return content || topic || null;
}

function formatRecommendation(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) return value.trim();
  const recommendation = asRecord(value);
  if (!recommendation) return null;
  const action = safeString(recommendation.action).trim();
  const rationale = safeString(recommendation.rationale).trim();
  if (action && rationale) return `${action} — ${rationale}`;
  return action || rationale || null;
}

function formatRisk(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) return value.trim();
  const risk = asRecord(value);
  if (!risk) return null;
  const description = safeString(risk.description).trim();
  const severity = safeString(risk.severity).trim();
  if (description && severity) return `${description} (${severity})`;
  return description || null;
}

function formatOpportunity(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) return value.trim();
  const opportunity = asRecord(value);
  if (!opportunity) return null;
  return safeString(opportunity.description).trim() || null;
}

function formatLimitation(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) return value.trim();
  const limitation = asRecord(value);
  if (!limitation) return null;
  const missing = safeString(limitation.what_is_missing).trim();
  const why = safeString(limitation.why_it_matters).trim();
  const needed = safeString(limitation.what_evidence_is_needed).trim();
  return [missing, why, needed].filter(Boolean).join(' — ') || null;
}

function extractBusinessAnswerSources(businessAnswer: Record<string, unknown>): string[] {
  const sources = safeStringArray(businessAnswer.sources);
  if (sources.length > 0) return Array.from(new Set(sources));

  const evidence = Array.isArray(businessAnswer.evidence) ? businessAnswer.evidence : [];
  const derived: string[] = [];
  for (const item of evidence) {
    const evidenceItem = asRecord(item);
    if (!evidenceItem) continue;
    const sourceId = safeString(evidenceItem.source_id).trim();
    const sourceUrl = safeString(evidenceItem.source_url).trim();
    const value = sourceId || sourceUrl;
    if (value) derived.push(value);
  }
  return Array.from(new Set(derived));
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
    recommendations: [],
    risks: [],
    opportunities: [],
    limitations: [],
    missionId: null,
    sessionId: null,
    hasStructuredContent: false,
    hasBusinessAnswer: false,
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
  const content = asRecord(parsed.content) || {};
  const result = asRecord(content.result) || {};
  const businessAnswer = asRecord(content.business_answer);
  const context = asRecord(parsed.context) || {};
  const suggestedActions = safeStringArray(parsed.suggested_actions);

  const outcome = safeString(content.outcome);
  const missionStatus = safeString(result.mission_status);
  const legacyGoal = safeString(result.goal);
  const legacySummary = safeString(result.summary);
  const legacyFindings = extractFindings(result);
  const legacySources = extractSources(result);

  const businessFindings = businessAnswer
    ? (Array.isArray(businessAnswer.key_findings) ? businessAnswer.key_findings : [])
        .map(formatFinding)
        .filter((value): value is string => Boolean(value))
    : [];
  const businessSources = businessAnswer ? extractBusinessAnswerSources(businessAnswer) : [];
  const recommendations = businessAnswer
    ? (Array.isArray(businessAnswer.recommendations) ? businessAnswer.recommendations : [])
        .map(formatRecommendation)
        .filter((value): value is string => Boolean(value))
    : [];
  const risks = businessAnswer
    ? (Array.isArray(businessAnswer.risks) ? businessAnswer.risks : [])
        .map(formatRisk)
        .filter((value): value is string => Boolean(value))
    : [];
  const opportunities = businessAnswer
    ? (Array.isArray(businessAnswer.opportunities) ? businessAnswer.opportunities : [])
        .map(formatOpportunity)
        .filter((value): value is string => Boolean(value))
    : [];
  const limitations = businessAnswer
    ? (Array.isArray(businessAnswer.limitations) ? businessAnswer.limitations : [])
        .map(formatLimitation)
        .filter((value): value is string => Boolean(value))
    : [];

  const goal = safeString(businessAnswer?.goal) || legacyGoal;
  const summary = safeString(businessAnswer?.executive_summary) || legacySummary;
  const findings = businessAnswer ? businessFindings : legacyFindings;
  const sources = businessAnswer ? businessSources : legacySources;
  const missionId = safeString(context.mission_id) || null;
  const sessionId = safeString(context.session_id) || null;

  const hasStructuredContent = Boolean(
    outcome || goal || summary || findings.length > 0 || sources.length > 0 ||
      recommendations.length > 0 || risks.length > 0 || opportunities.length > 0 ||
      limitations.length > 0 || missionId || suggestedActions.length > 0
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
    recommendations,
    risks,
    opportunities,
    limitations,
    missionId,
    sessionId,
    hasStructuredContent,
    hasBusinessAnswer: Boolean(businessAnswer),
    rawResponse: raw,
  };
}
