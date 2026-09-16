import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ParsedAvatarResult } from '@/lib/avatarResultParser';

interface ExecutiveResultCardProps {
  parsed: ParsedAvatarResult;
  rawResponse: string;
  locale: 'ar' | 'en';
}

type SectionName = 'keyFindings' | 'entities' | 'comparisons' | 'rankings' | 'opportunities' | 'risks' | 'recommendations' | 'evidence';

function getEvidenceKey(item: { source_id?: string; source_url?: string; content_excerpt?: string }) {
  return `${item.source_id || ''}|${item.source_url || ''}|${item.content_excerpt || ''}`;
}

function buildEvidenceSectionMap(bi: ParsedAvatarResult['businessAnswer']) {
  const firstSection = new Map<string, SectionName>();
  const sections: Array<{ name: SectionName; items: Array<{ source_id?: string; source_url?: string; content_excerpt?: string }> }> = [
    { name: 'keyFindings', items: bi.keyFindings.flatMap(f => f.evidence) },
    { name: 'entities', items: bi.entities.flatMap(e => e.evidence) },
    { name: 'comparisons', items: bi.comparisons?.results.flatMap(r => r.evidence) ?? [] },
    { name: 'rankings', items: bi.rankings?.flatMap(r => r.evidence) ?? [] },
    { name: 'opportunities', items: bi.opportunities.flatMap(o => o.evidence) },
    { name: 'risks', items: bi.risks.flatMap(r => r.evidence) },
    { name: 'recommendations', items: bi.recommendations.flatMap(r => r.evidence) },
    { name: 'evidence', items: bi.evidence },
  ];

  for (const section of sections) {
    for (const item of section.items) {
      const key = getEvidenceKey(item);
      if (!firstSection.has(key)) {
        firstSection.set(key, section.name);
      }
    }
  }

  return firstSection;
}

function groupEvidenceBySource(
  evidence: Array<{
    source_id?: string;
    source_url?: string;
    content_excerpt?: string;
    retrieval_timestamp?: string;
    confidence?: number | null;
    limitations?: string[] | null;
    provenance?: Record<string, unknown> | null;
  }>,
) {
  const groups = new Map<string, Array<{
    source_id?: string;
    source_url?: string;
    content_excerpt?: string;
    retrieval_timestamp?: string;
    confidence?: number | null;
    limitations?: string[] | null;
    provenance?: Record<string, unknown> | null;
  }>>();

  for (const item of evidence) {
    const key = item.source_id || 'unknown';
    const list = groups.get(key) || [];
    list.push(item);
    groups.set(key, list);
  }

  return groups;
}

function EvidenceGroup({
  sourceId,
  items,
  firstSectionMap,
  currentSection,
  t,
}: {
  sourceId: string;
  items: Array<{
    source_id?: string;
    source_url?: string;
    content_excerpt?: string;
    retrieval_timestamp?: string;
    confidence?: number | null;
    limitations?: string[] | null;
    provenance?: Record<string, unknown> | null;
  }>;
  firstSectionMap: Map<string, SectionName>;
  currentSection: SectionName;
  t: (key: string) => string;
}) {
  const [expanded, setExpanded] = useState(false);
  const first = items[0];
  const firstKey = first ? getEvidenceKey(first) : '';
  const firstSection = firstSectionMap.get(firstKey);
  const firstIsDuplicate = firstSection !== undefined && firstSection !== currentSection;

  return (
    <div className="space-y-1">
      <div className="text-sm text-slate-800">
        <span className="font-medium">{sourceId || 'evidence'}</span>
        {first?.source_url ? (
          <span className="text-slate-500"> — {first.source_url}</span>
        ) : null}
        {first?.content_excerpt ? (
          <span className="text-slate-600"> — {first.content_excerpt.slice(0, 180)}</span>
        ) : null}
        {firstIsDuplicate && firstSection ? (
          <span className="text-slate-500"> — {t('avatar.bi.also_cited_in')}: {firstSection}</span>
        ) : null}
        {items.length > 1 ? (
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-slate-500 hover:text-slate-700 ml-2"
          >
            {expanded ? t('avatar.bi.show_less') : t('avatar.bi.show_more')}
          </button>
        ) : null}
      </div>
      {expanded && (
        <div className="ml-4 space-y-1">
          {items.map((item, idx) => {
            const key = getEvidenceKey(item);
            const itemFirstSection = firstSectionMap.get(key);
            const isDuplicate = itemFirstSection !== undefined && itemFirstSection !== currentSection;
            return (
              <div key={idx} className="text-xs text-slate-600">
                <div>
                  <span className="font-medium">{item.source_id || 'evidence'}</span>
                  {item.source_url ? (
                    <span className="text-slate-500"> — {item.source_url}</span>
                  ) : null}
                  {item.content_excerpt ? (
                    <span className="text-slate-600"> — {item.content_excerpt.slice(0, 180)}</span>
                  ) : null}
                  {isDuplicate && itemFirstSection ? (
                    <span className="text-slate-500"> — {t('avatar.bi.also_cited_in')}: {itemFirstSection}</span>
                  ) : null}
                </div>
                {item.retrieval_timestamp || item.confidence !== null || item.limitations?.length || item.provenance ? (
                  <div className="mt-1 text-slate-500">
                    {item.retrieval_timestamp ? <div>Retrieved: {item.retrieval_timestamp}</div> : null}
                    {item.confidence !== null ? <div>Confidence: {item.confidence}</div> : null}
                    {item.limitations?.length ? <div>Limitations: {item.limitations.join(', ')}</div> : null}
                    {item.provenance ? <div>Provenance: {JSON.stringify(item.provenance)}</div> : null}
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function renderEvidenceItems(
  evidence: Array<{
    source_id?: string;
    source_url?: string;
    content_excerpt?: string;
    retrieval_timestamp?: string;
    confidence?: number | null;
    limitations?: string[] | null;
    provenance?: Record<string, unknown> | null;
  }>,
  firstSectionMap: Map<string, SectionName>,
  currentSection: SectionName,
  t: (key: string) => string,
) {
  if (!evidence.length) return null;
  const grouped = groupEvidenceBySource(evidence);
  const groups = Array.from(grouped.entries());

  if (groups.length === 0) return null;

  return (
    <ul className="list-disc list-inside space-y-1 text-sm text-slate-800">
      {groups.map(([sourceId, items]) => (
        <li key={sourceId}>
          <EvidenceGroup
            sourceId={sourceId}
            items={items}
            firstSectionMap={firstSectionMap}
            currentSection={currentSection}
            t={t}
          />
        </li>
      ))}
    </ul>
  );
}

function renderKeyFindings(findings: ParsedAvatarResult['businessAnswer']['keyFindings'], firstSectionMap: Map<string, SectionName>, t: (key: string) => string) {
  if (!findings.length) return null;
  return (
    <ul className="list-disc list-inside space-y-2 text-sm text-slate-800">
      {findings.map((finding, idx) => (
        <li key={idx}>
          <div className="font-medium text-slate-700">{finding.topic || finding.content}</div>
          <div className="text-slate-600">{finding.content}</div>
          {renderEvidenceItems(finding.evidence, firstSectionMap, 'keyFindings', t)}
          {finding.limitations && finding.limitations.length > 0 ? (
            <ul className="list-disc list-inside space-y-1 text-xs text-slate-500 mt-1">
              {finding.limitations.map((limitation, lidx) => (
                <li key={lidx}>{limitation}</li>
              ))}
            </ul>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

function renderEntities(entities: ParsedAvatarResult['businessAnswer']['entities'], firstSectionMap: Map<string, SectionName>, t: (key: string) => string) {
  if (!entities.length) return null;
  return (
    <ul className="list-disc list-inside space-y-2 text-sm text-slate-800">
      {entities.map((entity, idx) => (
        <li key={idx}>
          <span className="font-medium">{entity.name}</span>
          <span className="text-slate-600"> — {entity.type}</span>
          {Object.keys(entity.attributes).length > 0 ? (
            <span className="text-slate-500"> | {JSON.stringify(entity.attributes)}</span>
          ) : null}
          {renderEvidenceItems(entity.evidence, firstSectionMap, 'entities', t)}
        </li>
      ))}
    </ul>
  );
}

function renderComparisons(
  comparisons: ParsedAvatarResult['businessAnswer']['comparisons'],
  firstSectionMap: Map<string, SectionName>,
  t: (key: string) => string,
) {
  if (!comparisons) return null;
  return (
    <div className="space-y-2 text-sm text-slate-800">
      <div>
        <span className="font-medium">Options:</span> {comparisons.options.join(', ')}
      </div>
      <div>
        <span className="font-medium">Criteria:</span> {comparisons.criteria.join(', ')}
      </div>
      <ul className="list-disc list-inside space-y-2">
        {comparisons.results.map((result, idx) => (
          <li key={idx}>
            <span className="font-medium">{result.option}</span>
            <span className="text-slate-600"> — {result.criterion}: {String(result.value)}</span>
            {renderEvidenceItems(result.evidence, firstSectionMap, 'comparisons', t)}
          </li>
        ))}
      </ul>
      {comparisons.limitations && comparisons.limitations.length > 0 ? (
        <ul className="list-disc list-inside space-y-1 text-xs text-slate-500 mt-1">
          {comparisons.limitations.map((limitation, lidx) => (
            <li key={lidx}>{limitation}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

function renderRankings(
  rankings: ParsedAvatarResult['businessAnswer']['rankings'],
  firstSectionMap: Map<string, SectionName>,
  t: (key: string) => string,
) {
  if (!rankings || !rankings.length) return null;
  return (
    <ul className="list-disc list-inside space-y-2 text-sm text-slate-800">
      {rankings.map((ranking, idx) => (
        <li key={idx}>
          <span className="font-medium">#{ranking.rank} {ranking.candidate}</span>
          {ranking.total_score !== null ? (
            <span className="text-slate-600"> — score: {ranking.total_score}</span>
          ) : null}
          {ranking.criteria_scores && Object.keys(ranking.criteria_scores).length > 0 ? (
            <span className="text-slate-500"> — criteria: {JSON.stringify(ranking.criteria_scores)}</span>
          ) : null}
          {ranking.explanation ? (
            <div className="text-slate-600">{ranking.explanation}</div>
          ) : null}
          {renderEvidenceItems(ranking.evidence, firstSectionMap, 'rankings', t)}
          {ranking.limitations && ranking.limitations.length > 0 ? (
            <ul className="list-disc list-inside space-y-1 text-xs text-slate-500 mt-1">
              {ranking.limitations.map((limitation, lidx) => (
                <li key={lidx}>{limitation}</li>
              ))}
            </ul>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

function renderOpportunities(opportunities: ParsedAvatarResult['businessAnswer']['opportunities'], firstSectionMap: Map<string, SectionName>, t: (key: string) => string) {
  if (!opportunities.length) return null;
  return (
    <ul className="list-disc list-inside space-y-2 text-sm text-slate-800">
      {opportunities.map((item, idx) => (
        <li key={idx}>
          <span className="font-medium">{item.description}</span>
          {item.confidence !== null ? (
            <span className="text-slate-600"> — confidence: {item.confidence}</span>
          ) : null}
          {renderEvidenceItems(item.evidence, firstSectionMap, 'opportunities', t)}
          {item.limitations && item.limitations.length > 0 ? (
            <ul className="list-disc list-inside space-y-1 text-xs text-slate-500 mt-1">
              {item.limitations.map((limitation, lidx) => (
                <li key={lidx}>{limitation}</li>
              ))}
            </ul>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

function renderRisks(risks: ParsedAvatarResult['businessAnswer']['risks'], firstSectionMap: Map<string, SectionName>, t: (key: string) => string) {
  if (!risks.length) return null;
  return (
    <ul className="list-disc list-inside space-y-2 text-sm text-slate-800">
      {risks.map((item, idx) => (
        <li key={idx}>
          <span className="font-medium">{item.description}</span>
          {item.severity ? <span className="text-slate-600"> — severity: {item.severity}</span> : null}
          {item.mitigation ? <span className="text-slate-500"> — mitigation: {item.mitigation}</span> : null}
          {renderEvidenceItems(item.evidence, firstSectionMap, 'risks', t)}
          {item.limitations && item.limitations.length > 0 ? (
            <ul className="list-disc list-inside space-y-1 text-xs text-slate-500 mt-1">
              {item.limitations.map((limitation, lidx) => (
                <li key={lidx}>{limitation}</li>
              ))}
            </ul>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

function renderRecommendations(recommendations: ParsedAvatarResult['businessAnswer']['recommendations'], firstSectionMap: Map<string, SectionName>, t: (key: string) => string) {
  if (!recommendations.length) return null;
  return (
    <ul className="list-disc list-inside space-y-2 text-sm text-slate-800">
      {recommendations.map((item, idx) => (
        <li key={idx}>
          <span className="font-medium">{item.action}</span>
          <span className="text-slate-600"> — {item.type}</span>
          <div className="text-slate-600">{item.rationale}</div>
          {renderEvidenceItems(item.evidence, firstSectionMap, 'recommendations', t)}
          {item.limitations && item.limitations.length > 0 ? (
            <ul className="list-disc list-inside space-y-1 text-xs text-slate-500 mt-1">
              {item.limitations.map((limitation, lidx) => (
                <li key={lidx}>{limitation}</li>
              ))}
            </ul>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

export function ExecutiveResultCard({ parsed, locale }: ExecutiveResultCardProps) {
  const { t } = useTranslation();
  const bi = parsed.businessAnswer;
  const firstSectionMap = buildEvidenceSectionMap(bi);

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

      {bi.executiveSummary && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.executive_summary')}</p>
          <p className="text-sm text-slate-800 whitespace-pre-wrap">{bi.executiveSummary}</p>
        </div>
      )}

      {bi.keyFindings.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.key_findings')}</p>
          {renderKeyFindings(bi.keyFindings, firstSectionMap, t)}
        </div>
      )}

      {bi.entities.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.entities')}</p>
          {renderEntities(bi.entities, firstSectionMap, t)}
        </div>
      )}

      {bi.comparisons && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.comparisons')}</p>
          {renderComparisons(bi.comparisons, firstSectionMap, t)}
        </div>
      )}

      {bi.rankings && bi.rankings.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.rankings')}</p>
          {renderRankings(bi.rankings, firstSectionMap, t)}
        </div>
      )}

      {bi.opportunities.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.opportunities')}</p>
          {renderOpportunities(bi.opportunities, firstSectionMap, t)}
        </div>
      )}

      {bi.risks.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.risks')}</p>
          {renderRisks(bi.risks, firstSectionMap, t)}
        </div>
      )}

      {bi.recommendations.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.recommendations')}</p>
          {renderRecommendations(bi.recommendations, firstSectionMap, t)}
        </div>
      )}

      {bi.confidence !== null && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.confidence')}</p>
          <p className="text-sm text-slate-800">{bi.confidence}</p>
        </div>
      )}

      {bi.limitations.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.limitations')}</p>
          <ul className="list-disc list-inside space-y-1 text-sm text-slate-800">
            {bi.limitations.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {bi.evidence.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.bi.evidence')}</p>
          {renderEvidenceItems(bi.evidence, firstSectionMap, 'evidence', t)}
        </div>
      )}

      {parsed.summary && !bi.executiveSummary && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.summary')}</p>
          <p className="text-sm text-slate-800 whitespace-pre-wrap">{parsed.summary}</p>
        </div>
      )}

      {parsed.findings.length > 0 && bi.keyFindings.length === 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-3">
          <p className="text-xs font-semibold text-slate-500 mb-1">{t('avatar.fields.findings')}</p>
          <ul className="list-disc list-inside space-y-1 text-sm text-slate-800">
            {parsed.findings.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {parsed.sources.length > 0 && bi.evidence.length === 0 && (
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
