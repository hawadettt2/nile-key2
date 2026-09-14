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
  businessAnswer: {
    executiveSummary?: string;
    keyFindings: Array<{
      topic?: string;
      content: string;
      confidence?: number | null;
      limitations?: string[] | null;
      evidence: Array<{
        source_id?: string;
        source_url?: string;
        content_excerpt?: string;
      }>;
    }>;
    entities: Array<{
      name: string;
      type: string;
      attributes: Record<string, unknown>;
      evidence: Array<{
        source_id?: string;
        source_url?: string;
        content_excerpt?: string;
      }>;
    }>;
    comparisons: {
      options: string[];
      criteria: string[];
      results: Array<{
        option: string;
        criterion: string;
        value: unknown;
        evidence: Array<{
          source_id?: string;
          source_url?: string;
          content_excerpt?: string;
        }>;
      }>;
      limitations: string[];
    } | null;
    rankings: Array<{
      rank: number;
      candidate: string;
      criteria_scores: Record<string, unknown>;
      total_score: number | null;
      evidence: Array<{
        source_id?: string;
        source_url?: string;
        content_excerpt?: string;
      }>;
      explanation?: string | null;
      limitations: string[];
    }> | null;
    opportunities: Array<{
      description: string;
      evidence: Array<{
        source_id?: string;
        source_url?: string;
        content_excerpt?: string;
      }>;
      confidence: number | null;
      limitations?: string[] | null;
    }>;
    risks: Array<{
      description: string;
      evidence: Array<{
        source_id?: string;
        source_url?: string;
        content_excerpt?: string;
      }>;
      severity: string | null;
      mitigation: string | null;
      limitations?: string[] | null;
    }>;
    recommendations: Array<{
      action: string;
      type: string;
      rationale: string;
      evidence: Array<{
        source_id?: string;
        source_url?: string;
        content_excerpt?: string;
      }>;
      confidence: number | null;
      limitations?: string[] | null;
    }>;
    confidence: number | null;
    limitations: string[];
    evidence: Array<{
      source_id: string;
      source_url?: string;
      content_excerpt?: string;
      retrieval_timestamp?: string;
      confidence?: number | null;
      limitations?: string[] | null;
      provenance?: Record<string, unknown> | null;
    }>;
    provenance: Record<string, unknown> | null;
  };
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

function extractEvidenceItems(
  evidence: unknown,
): Array<{
  source_id: string;
  source_url?: string;
  content_excerpt?: string;
  retrieval_timestamp?: string;
  confidence?: number | null;
  limitations?: string[] | null;
  provenance?: Record<string, unknown> | null;
}> {
  if (!Array.isArray(evidence)) return [];
  const items: Array<{
    source_id: string;
    source_url?: string;
    content_excerpt?: string;
    retrieval_timestamp?: string;
    confidence?: number | null;
    limitations?: string[] | null;
    provenance?: Record<string, unknown> | null;
  }> = [];
  for (const item of evidence) {
    if (!item || typeof item !== 'object') continue;
    const record = item as Record<string, unknown>;
    const source_id = typeof record.source_id === 'string' ? record.source_id : '';
    if (!source_id) continue;
    items.push({
      source_id,
      source_url: typeof record.source_url === 'string' ? record.source_url : undefined,
      content_excerpt: typeof record.content_excerpt === 'string' ? record.content_excerpt : undefined,
      retrieval_timestamp: typeof record.retrieval_timestamp === 'string' ? record.retrieval_timestamp : undefined,
      confidence: typeof record.confidence === 'number' ? record.confidence : null,
      limitations: Array.isArray(record.limitations)
        ? record.limitations.filter((l): l is string => typeof l === 'string')
        : null,
      provenance: record.provenance && typeof record.provenance === 'object'
        ? (record.provenance as Record<string, unknown>)
        : null,
    });
  }
  return items;
}

function extractBusinessAnswerFields(
  content: Record<string, unknown>,
): {
  goal?: string;
  summary?: string;
  findings: string[];
  sources: string[];
  businessAnswer: ParsedAvatarResult['businessAnswer'];
} {
  const businessAnswer = content.business_answer;
  if (!businessAnswer || typeof businessAnswer !== 'object') {
    return { findings: [], sources: [], businessAnswer: {
      keyFindings: [],
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
    } };
  }

  const ba = businessAnswer as Record<string, unknown>;
  const findings: string[] = [];
  const sources: string[] = [];

  if (Array.isArray(ba.key_findings)) {
    for (const item of ba.key_findings) {
      if (!item || typeof item !== 'object') continue;
      const finding = item as Record<string, unknown>;
      const contentValue = finding.content;
      if (typeof contentValue === 'string' && contentValue.trim().length > 0) {
        findings.push(contentValue);
      } else if (typeof finding.topic === 'string') {
        findings.push(finding.topic);
      }
    }
  }

  if (Array.isArray(ba.sources)) {
    for (const source of ba.sources) {
      if (typeof source === 'string') {
        sources.push(source);
      }
    }
  }

  const keyFindings: ParsedAvatarResult['businessAnswer']['keyFindings'] = Array.isArray(ba.key_findings)
    ? ba.key_findings.map((item) => {
        if (!item || typeof item !== 'object') {
          return { content: '', evidence: [] };
        }
        const finding = item as Record<string, unknown>;
        return {
          topic: typeof finding.topic === 'string' ? finding.topic : undefined,
          content: typeof finding.content === 'string' ? finding.content : '',
          confidence: typeof finding.confidence === 'number' ? finding.confidence : null,
          limitations: Array.isArray(finding.limitations)
            ? finding.limitations.filter((l): l is string => typeof l === 'string')
            : null,
          evidence: extractEvidenceItems(finding.evidence),
        };
      })
    : [];

  const entities: ParsedAvatarResult['businessAnswer']['entities'] = Array.isArray(ba.entities)
    ? ba.entities.map((item) => {
        if (!item || typeof item !== 'object') {
          return { name: '', type: '', attributes: {}, evidence: [] };
        }
        const entity = item as Record<string, unknown>;
        return {
          name: typeof entity.name === 'string' ? entity.name : '',
          type: typeof entity.type === 'string' ? entity.type : '',
          attributes: entity.attributes && typeof entity.attributes === 'object'
            ? (entity.attributes as Record<string, unknown>)
            : {},
          evidence: extractEvidenceItems(entity.evidence),
        };
      })
    : [];

  let comparisons: ParsedAvatarResult['businessAnswer']['comparisons'] = null;
  if (ba.comparisons && typeof ba.comparisons === 'object') {
    const comp = ba.comparisons as Record<string, unknown>;
    comparisons = {
      options: safeStringArray(comp.options),
      criteria: safeStringArray(comp.criteria),
      results: Array.isArray(comp.results)
        ? comp.results.map((r) => {
            if (!r || typeof r !== 'object') {
              return { option: '', criterion: '', value: null, evidence: [] };
            }
            const result = r as Record<string, unknown>;
            return {
              option: typeof result.option === 'string' ? result.option : '',
              criterion: typeof result.criterion === 'string' ? result.criterion : '',
              value: result.value,
              evidence: extractEvidenceItems(result.evidence),
            };
          })
        : [],
      limitations: safeStringArray(comp.limitations),
    };
  }

  const rankings: ParsedAvatarResult['businessAnswer']['rankings'] = Array.isArray(ba.rankings)
    ? ba.rankings.map((item) => {
        if (!item || typeof item !== 'object') {
          return { rank: 0, candidate: '', criteria_scores: {}, total_score: null, evidence: [], limitations: [] };
        }
        const ranking = item as Record<string, unknown>;
        return {
          rank: typeof ranking.rank === 'number' ? ranking.rank : 0,
          candidate: typeof ranking.candidate === 'string' ? ranking.candidate : '',
          criteria_scores: ranking.criteria_scores && typeof ranking.criteria_scores === 'object'
            ? (ranking.criteria_scores as Record<string, unknown>)
            : {},
          total_score: typeof ranking.total_score === 'number' ? ranking.total_score : null,
          evidence: extractEvidenceItems(ranking.evidence),
          explanation: typeof ranking.explanation === 'string' ? ranking.explanation : null,
          limitations: safeStringArray(ranking.limitations),
        };
      })
    : null;

  const opportunities: ParsedAvatarResult['businessAnswer']['opportunities'] = Array.isArray(ba.opportunities)
    ? ba.opportunities.map((item) => {
        if (!item || typeof item !== 'object') {
          return { description: '', evidence: [], confidence: null };
        }
        const opportunity = item as Record<string, unknown>;
        return {
          description: typeof opportunity.description === 'string' ? opportunity.description : '',
          evidence: extractEvidenceItems(opportunity.evidence),
          confidence: typeof opportunity.confidence === 'number' ? opportunity.confidence : null,
          limitations: Array.isArray(opportunity.limitations)
            ? opportunity.limitations.filter((l): l is string => typeof l === 'string')
            : null,
        };
      })
    : [];

  const risks: ParsedAvatarResult['businessAnswer']['risks'] = Array.isArray(ba.risks)
    ? ba.risks.map((item) => {
        if (!item || typeof item !== 'object') {
          return { description: '', evidence: [], severity: null, mitigation: null };
        }
        const risk = item as Record<string, unknown>;
        return {
          description: typeof risk.description === 'string' ? risk.description : '',
          evidence: extractEvidenceItems(risk.evidence),
          severity: typeof risk.severity === 'string' ? risk.severity : null,
          mitigation: typeof risk.mitigation === 'string' ? risk.mitigation : null,
          limitations: Array.isArray(risk.limitations)
            ? risk.limitations.filter((l): l is string => typeof l === 'string')
            : null,
        };
      })
    : [];

  const recommendations: ParsedAvatarResult['businessAnswer']['recommendations'] = Array.isArray(ba.recommendations)
    ? ba.recommendations.map((item) => {
        if (!item || typeof item !== 'object') {
          return { action: '', type: '', rationale: '', evidence: [], confidence: null };
        }
        const recommendation = item as Record<string, unknown>;
        return {
          action: typeof recommendation.action === 'string' ? recommendation.action : '',
          type: typeof recommendation.type === 'string' ? recommendation.type : '',
          rationale: typeof recommendation.rationale === 'string' ? recommendation.rationale : '',
          evidence: extractEvidenceItems(recommendation.evidence),
          confidence: typeof recommendation.confidence === 'number' ? recommendation.confidence : null,
          limitations: Array.isArray(recommendation.limitations)
            ? recommendation.limitations.filter((l): l is string => typeof l === 'string')
            : null,
        };
      })
    : [];

  return {
    goal: typeof ba.goal === 'string' ? ba.goal : undefined,
    summary: typeof ba.executive_summary === 'string' ? ba.executive_summary : undefined,
    findings,
    sources,
    businessAnswer: {
      executiveSummary: typeof ba.executive_summary === 'string' ? ba.executive_summary : undefined,
      keyFindings,
      entities,
      comparisons,
      rankings,
      opportunities,
      risks,
      recommendations,
      confidence: typeof ba.confidence === 'number' ? ba.confidence : null,
      limitations: safeStringArray(ba.limitations),
      evidence: extractEvidenceItems(ba.evidence),
      provenance: ba.provenance && typeof ba.provenance === 'object'
        ? (ba.provenance as Record<string, unknown>)
        : null,
    },
  };
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
      confidence: null,
      provenance: null,
    },
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
  const businessAnswerFields = extractBusinessAnswerFields(content);
  const goal = safeString(businessAnswerFields.goal ?? result.goal);
  const summary = safeString(businessAnswerFields.summary ?? result.summary);
  const findings = businessAnswerFields.findings.length > 0 ? businessAnswerFields.findings : extractFindings(result);
  const sources = businessAnswerFields.sources.length > 0 ? businessAnswerFields.sources : extractSources(result);
  const missionId = safeString(context.mission_id) || null;
  const sessionId = safeString(context.session_id) || null;

  const hasBusinessAnswer = Boolean(content.business_answer && typeof content.business_answer === 'object');

  const hasStructuredContent = Boolean(
    outcome || goal || summary || findings.length > 0 || sources.length > 0 || missionId || suggestedActions.length > 0
      || (hasBusinessAnswer && (
        businessAnswerFields.businessAnswer.keyFindings.length > 0
        || businessAnswerFields.businessAnswer.entities.length > 0
        || businessAnswerFields.businessAnswer.opportunities.length > 0
        || businessAnswerFields.businessAnswer.risks.length > 0
        || businessAnswerFields.businessAnswer.recommendations.length > 0
        || businessAnswerFields.businessAnswer.limitations.length > 0
        || businessAnswerFields.businessAnswer.evidence.length > 0
        || businessAnswerFields.businessAnswer.comparisons !== null
        || businessAnswerFields.businessAnswer.rankings !== null
      ))
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
    businessAnswer: businessAnswerFields.businessAnswer,
  };
}
