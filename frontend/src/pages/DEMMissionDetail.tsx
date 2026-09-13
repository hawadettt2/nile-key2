import { useEffect, useState, useRef, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, CheckCircle, XCircle, Clock, AlertTriangle, FileText, Brain, Loader2 } from 'lucide-react';
import { useDEMStore } from '@/store/demStore';
import { getDEMSession, getMissionById } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';

const MISSING_MISSION_MESSAGE_KEY = 'dem.missionNotFoundContext';

interface ExecutionStep {
  status: string;
  tool?: string;
  data?: unknown;
  error?: string;
}

interface MissionTraceProps {
  mission: {
    result?: Record<string, unknown>;
    reasoning?: string;
    error?: string;
    requires_approval?: boolean;
    approval_status?: string;
    intent_content?: Record<string, unknown>;
  };
}

const statusConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  completed: { icon: <CheckCircle size={16} />, color: 'text-green-600', label: 'Completed' },
  failed: { icon: <XCircle size={16} />, color: 'text-red-600', label: 'Failed' },
  pending: { icon: <Clock size={16} />, color: 'text-amber-600', label: 'Pending' },
  running: { icon: <Clock size={16} />, color: 'text-blue-600' , label: 'Running' },
  pending_approval: { icon: <AlertTriangle size={16} />, color: 'text-orange-600', label: 'Pending Approval' },
};

function renderStructuredResultData(data: unknown): React.ReactNode {
  if (!data || typeof data !== 'object') {
    return <span className="text-sm text-slate-700">{String(data)}</span>;
  }

  const record = data as Record<string, unknown>;
  const goal = typeof record.goal === 'string' ? record.goal : undefined;
  const status = typeof record.status === 'string' ? record.status : undefined;
  const summary = typeof record.summary === 'string' ? record.summary : undefined;
  const findings = Array.isArray(record.findings) ? record.findings : undefined;
  const sourcesConsulted = Array.isArray(record.sources_consulted) ? record.sources_consulted : undefined;
  const sourcesFailed = Array.isArray(record.sources_failed) ? record.sources_failed : undefined;

  const reservedKeys = ['goal', 'status', 'summary', 'findings', 'sources_consulted', 'sources_failed'];
  const remainingKeys = Object.keys(record).filter((key) => !reservedKeys.includes(key));

  const renderValue = (value: unknown): React.ReactNode => {
    if (value === null || value === undefined) {
      return <span className="text-slate-400">-</span>;
    }
    if (typeof value === 'string') {
      return <span className="text-slate-700">{value}</span>;
    }
    if (typeof value === 'number' || typeof value === 'boolean') {
      return <span className="text-slate-700">{String(value)}</span>;
    }
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="text-slate-400">-</span>;
      }
      return (
        <ul className="list-disc list-inside text-slate-700 space-y-1">
          {value.map((item, i) => (
            <li key={i}>{renderValue(item)}</li>
          ))}
        </ul>
      );
    }
    if (typeof value === 'object') {
      return (
        <div className="space-y-1">
          {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
            <div key={k} className="text-slate-700">
              <span className="font-medium">{k}: </span>
              {renderValue(v)}
            </div>
          ))}
        </div>
      );
    }
    return <span className="text-slate-700">{String(value)}</span>;
  };

  return (
    <div className="space-y-3 text-sm">
      {goal && (
        <div>
          <p className="font-medium text-slate-900">الهدف</p>
          <p className="text-slate-700">{goal}</p>
        </div>
      )}
      {status && (
        <div>
          <p className="font-medium text-slate-900">الحالة</p>
          <p className="text-slate-700">{status}</p>
        </div>
      )}
      {summary && (
        <div>
          <p className="font-medium text-slate-900">الملخص</p>
          <p className="text-slate-700 whitespace-pre-wrap">{summary}</p>
        </div>
      )}
      {findings && findings.length > 0 && (
        <div>
          <p className="font-medium text-slate-900">النتائج</p>
          <div className="space-y-2">
            {findings.map((finding: unknown, idx: number) => {
              if (!finding || typeof finding !== 'object') return null;
              const f = finding as Record<string, unknown>;
              const topic = typeof f.topic === 'string' ? f.topic : undefined;
              const content = typeof f.content === 'string' ? f.content : undefined;
              const confidence = f.confidence !== null && f.confidence !== undefined ? String(f.confidence) : undefined;
              const sources = Array.isArray(f.sources) ? f.sources : undefined;
              const extraKeys = Object.keys(f).filter((key) => !['topic', 'content', 'confidence', 'sources'].includes(key));

              return (
                <div key={idx} className="rounded border border-slate-100 bg-slate-50 p-2 space-y-1">
                  {topic && <p className="font-medium text-slate-900">{topic}</p>}
                  {content && <p className="text-slate-700 whitespace-pre-wrap">{content}</p>}
                  {confidence && <p className="text-xs text-slate-500">درجة الثقة: {confidence}</p>}
                  {sources && sources.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-slate-700">المصادر المرتبطة</p>
                      <div className="space-y-2">
                        {sources.map((source: unknown, sIdx: number) => {
                          if (!source || typeof source !== 'object') {
                            return <div key={sIdx}>{String(source)}</div>;
                          }
                          const s = source as Record<string, unknown>;
                          const sourceId = typeof s.source_id === 'string' ? s.source_id : undefined;
                          const sourceUrl = typeof s.source_url === 'string' ? s.source_url : undefined;
                          const excerpt = typeof s.excerpt === 'string' ? s.excerpt : undefined;
                          const reservedSourceKeys = ['source_id', 'source_url', 'excerpt'];
                          const extraSourceKeys = Object.keys(s).filter((key) => !reservedSourceKeys.includes(key));

                          return (
                            <div key={sIdx} className="rounded border border-slate-100 bg-slate-50 p-2 space-y-1">
                              <div>
                                <span className="font-medium">المصدر: </span>
                                <span>{sourceId || '-'}</span>
                              </div>
                              {sourceUrl && (
                                <div>
                                  <span className="font-medium">الرابط/مرجع: </span>
                                  <span>{sourceUrl}</span>
                                </div>
                              )}
                              {excerpt && (
                                <div>
                                  <span className="font-medium">الدليل الفعلي: </span>
                                  <pre className="whitespace-pre-wrap text-xs">{excerpt}</pre>
                                </div>
                              )}
                              {extraSourceKeys.length > 0 && (
                                <div className="text-xs text-slate-500">
                                  {extraSourceKeys.map((key) => (
                                    <div key={key}>
                                      <span className="font-medium">{key}: </span>
                                      {renderValue(s[key])}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                  {extraKeys.length > 0 && (
                    <div className="text-xs text-slate-500">
                      {extraKeys.map((key) => (
                        <div key={key}>
                          <span className="font-medium">{key}: </span>
                          {renderValue(f[key])}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
      {sourcesConsulted && sourcesConsulted.length > 0 && (
        <div>
          <p className="font-medium text-slate-900">المصادر</p>
          <ul className="list-disc list-inside text-slate-700 space-y-1">
            {sourcesConsulted.map((item: unknown, idx: number) => (
              <li key={idx}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
            ))}
          </ul>
        </div>
      )}
      {sourcesFailed && sourcesFailed.length > 0 && (
        <div>
          <p className="font-medium text-slate-900">المصادر التي فشلت</p>
          <ul className="list-disc list-inside text-red-600 space-y-1">
            {sourcesFailed.map((item: unknown, idx: number) => (
              <li key={idx}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
            ))}
          </ul>
        </div>
      )}
      {remainingKeys.length > 0 && (
        <div>
          <p className="font-medium text-slate-900">بيانات إضافية</p>
          <div className="space-y-1">
            {remainingKeys.map((key) => (
              <div key={key} className="text-slate-700">
                <span className="font-medium">{key}: </span>
                {renderValue(record[key])}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ExecutionTraceViewer({ mission }: MissionTraceProps) {
  const result = mission.result as Record<string, unknown> | undefined;
  const reasoning = mission.reasoning as string | undefined;
  const error = mission.error as string | undefined;

  const stepStatusConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
    completed: { icon: <CheckCircle size={14} />, color: 'text-green-600', label: 'Completed' },
    success: { icon: <CheckCircle size={14} />, color: 'text-green-600', label: 'Completed' },
    failed: { icon: <XCircle size={14} />, color: 'text-red-600', label: 'Failed' },
    running: { icon: <Loader2 size={14} className="animate-spin" />, color: 'text-blue-600', label: 'Running' },
    pending: { icon: <Clock size={14} />, color: 'text-amber-600', label: 'Pending' },
  };

  const renderStepStatus = (stepStatus: string) => {
    const normalized = stepStatus.toLowerCase();
    const config = stepStatusConfig[normalized] || stepStatusConfig.pending;
    return (
      <span className={`inline-flex items-center gap-1 text-xs font-medium ${config.color}`}>
        {config.icon}
        {config.label}
      </span>
    );
  };

  const steps = useMemo(() => {
    if (!result) return [];
    if (Array.isArray(result.results)) return result.results as ExecutionStep[];
    if (Array.isArray(result.steps)) return result.steps as ExecutionStep[];
    return [];
  }, [result]);

  const hasStructuredSteps = steps.length > 0;
  const hasRawResult = result && !hasStructuredSteps;

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="font-medium">Error</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {hasStructuredSteps && (
        <div className="space-y-2">
          <h3 className="font-medium text-slate-900">Execution Steps</h3>
          <div className="space-y-2">
            {steps.map((step: ExecutionStep, idx: number) => (
              <Card key={idx} className="p-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-900">Step {idx + 1}</span>
                  {renderStepStatus(step.status)}
                </div>
                {step.tool && (
                  <p className="text-xs text-slate-500 mt-1">Tool: {step.tool}</p>
                )}
                {step.data !== undefined && (
                  <div className="mt-2 rounded border border-slate-200 bg-white p-3">
                    {renderStructuredResultData(step.data)}
                  </div>
                )}
                {step.error && (
                  <p className="text-sm text-red-600 mt-2">{step.error}</p>
                )}
              </Card>
            ))}
          </div>
        </div>
      )}

      {hasRawResult && (
        <div className="space-y-2">
          <h3 className="font-medium text-slate-900">Execution Result</h3>
          <pre className="bg-slate-50 p-4 rounded-lg text-xs overflow-auto max-h-96 text-slate-700">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      {!error && !hasStructuredSteps && !hasRawResult && (
        <p className="text-slate-500">No execution results available yet.</p>
      )}

      {reasoning && (
        <div className="space-y-2">
          <h3 className="font-medium text-slate-900">Reasoning</h3>
          <div className="bg-slate-50 p-4 rounded-lg text-sm text-slate-700 whitespace-pre-wrap">
            {reasoning}
          </div>
        </div>
      )}

      {mission.intent_content && (
        <div className="space-y-2">
          <h3 className="font-medium text-slate-900">Structured Business Response</h3>
          <pre className="bg-slate-50 p-4 rounded-lg text-xs overflow-auto max-h-96 text-slate-700">
            {JSON.stringify(mission.intent_content, null, 2)}
          </pre>
        </div>
      )}

      {mission.requires_approval && (
        <div className="mt-4 bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 rounded-lg">
          <p className="font-medium">Approval Required</p>
          <p className="text-sm mt-1">Status: {mission.approval_status || 'pending'}</p>
        </div>
      )}
    </div>
  );
}

export function DEMMissionDetail() {
  const { t } = useTranslation();
  const { missionId } = useParams<{ missionId: string }>();
  const navigate = useNavigate();
  const { missions, currentMission, setCurrentMission, setMissions, activeSession } = useDEMStore();
  const [isLoading, setIsLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(false);
  const [notFoundMessage, setNotFoundMessage] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const mission = currentMission || missions.find((m) => m.mission_id === missionId);

  const pollSession = async () => {
    if (!mission || !mission.session_id) return;
    try {
      const res = await getDEMSession(mission.session_id);
      const data = res.data;
      if (data.missions) {
        const updated = data.missions.map((m: Record<string, unknown>) => ({
          mission_id: m.mission_id as string,
          session_id: data.session_id,
          status: m.status as string,
          result: m.result as Record<string, unknown> | undefined,
          error: m.error as string | undefined,
          created_at: (m.created_at as string) || new Date().toISOString(),
          completed_at: m.completed_at as string | undefined,
          reasoning: m.reasoning as string | undefined,
          requires_approval: m.requires_approval as boolean | undefined,
          approval_status: m.approval_status as string | undefined,
          intent_content: m.intent_content as Record<string, unknown> | undefined,
        }));
        setMissions(updated);
        const updatedMission = updated.find((m: Record<string, unknown>) => m.mission_id === missionId);
        if (updatedMission) {
          setCurrentMission(updatedMission);
        }
      }
    } catch {
      // Silently fail during polling
    }
  };

  useEffect(() => {
    if (!mission && missionId) {
      setIsLoading(true);
      if (activeSession?.session_id) {
        getDEMSession(activeSession.session_id)
          .then((res) => {
            const data = res.data;
            if (data.missions) {
              const mapped = data.missions.map((m: Record<string, unknown>) => ({
                mission_id: m.mission_id as string,
                session_id: data.session_id,
                status: m.status as string,
                result: m.result as Record<string, unknown> | undefined,
                error: m.error as string | undefined,
                created_at: (m.created_at as string) || new Date().toISOString(),
                completed_at: m.completed_at as string | undefined,
                reasoning: m.reasoning as string | undefined,
                requires_approval: m.requires_approval as boolean | undefined,
                approval_status: m.approval_status as string | undefined,
                intent_content: m.intent_content as Record<string, unknown> | undefined,
              }));
              setMissions(mapped);
              const found = mapped.find((m: Record<string, unknown>) => m.mission_id === missionId);
              if (found) {
                setCurrentMission(found);
                setNotFoundMessage(null);
                return;
              }
            }
            return getMissionById(missionId);
          })
          .then((fallbackRes) => {
            if (fallbackRes?.data) {
              const data = fallbackRes.data;
              const found = {
                mission_id: data.mission_id,
                session_id: data.session_id,
                status: data.status,
                result: data.result,
                error: data.error,
                created_at: data.created_at,
                completed_at: data.completed_at,
                reasoning: data.reasoning,
                requires_approval: data.requires_approval,
                approval_status: data.approval_status,
                intent_content: data.intent_content,
              } as Record<string, unknown>;
              (setMissions as any)((prev: any[]) => {
                const exists = prev.find((m: Record<string, unknown>) => m.mission_id === missionId);
                if (exists) return prev;
                return [...prev, found];
              });
              setCurrentMission(found as any);
              setNotFoundMessage(null);
            } else {
              setNotFoundMessage(t(MISSING_MISSION_MESSAGE_KEY));
            }
          })
          .catch(() => setNotFoundMessage(t(MISSING_MISSION_MESSAGE_KEY)))
          .finally(() => setIsLoading(false));
      } else {
        getMissionById(missionId)
          .then((fallbackRes) => {
            if (fallbackRes?.data) {
              const data = fallbackRes.data;
              const found = {
                mission_id: data.mission_id,
                session_id: data.session_id,
                status: data.status,
                result: data.result,
                error: data.error,
                created_at: data.created_at,
                completed_at: data.completed_at,
                reasoning: data.reasoning,
                requires_approval: data.requires_approval,
                approval_status: data.approval_status,
                intent_content: data.intent_content,
              } as Record<string, unknown>;
              (setMissions as any)((prev: any[]) => {
                const exists = prev.find((m: Record<string, unknown>) => m.mission_id === missionId);
                if (exists) return prev;
                return [...prev, found];
              });
              setCurrentMission(found as any);
              setNotFoundMessage(null);
            } else {
              setNotFoundMessage(t(MISSING_MISSION_MESSAGE_KEY));
            }
          })
          .catch(() => setNotFoundMessage(t(MISSING_MISSION_MESSAGE_KEY)))
          .finally(() => setIsLoading(false));
      }
      return;
    }
    setIsLoading(false);
  }, [mission, missionId, activeSession, setCurrentMission, setMissions, t]);

  useEffect(() => {
    if (mission && (mission.status === 'pending' || mission.status === 'running')) {
      setIsPolling(true);
      intervalRef.current = setInterval(pollSession, 3000);
      return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
        setIsPolling(false);
      };
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, [mission?.status, mission?.session_id, missionId]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!mission && notFoundMessage) {
    return (
      <div className="text-center">
        <p className="text-slate-500">{notFoundMessage}</p>
        <Button variant="ghost" onClick={() => navigate('/digital-export-manager/missions')}>{t('dem.backToMissions')}</Button>
      </div>
    );
  }

  if (!mission) {
    return (
      <div className="text-center">
        <p className="text-slate-500">{t('dem.missionNotFound')}</p>
        <Button variant="ghost" onClick={() => navigate('/digital-export-manager/missions')}>{t('dem.backToMissions')}</Button>
      </div>
    );
  }

  const config = statusConfig[mission.status] || statusConfig.pending;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => navigate('/digital-export-manager/missions')}>
          <ArrowLeft size={20} />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className={config.color}>{config.icon}</span>
            <h1 className="text-2xl font-bold text-slate-900">{t('dem.missionsTitle').slice(0, -1)} {mission.mission_id.slice(0, 16)}...</h1>
            {isPolling && <Loader2 size={16} className="animate-spin text-blue-600" />}
          </div>
          <p className="text-slate-500 text-sm">
            {t('dem.createdOn')} {new Date(mission.created_at).toLocaleString()} · {mission.status}
          </p>
        </div>
        {mission.status === 'pending_approval' && (
          <Button onClick={() => navigate('/digital-export-manager/approvals')}>
            {t('dem.viewApprovalInbox')}
          </Button>
        )}
      </div>

      <Tabs defaultValue="results">
        <TabsList>
          <TabsTrigger value="results" className="gap-2"><FileText size={14} /> {t('dem.resultsTab')}</TabsTrigger>
          <TabsTrigger value="reasoning" className="gap-2"><Brain size={14} /> {t('dem.reasoningTab')}</TabsTrigger>
        </TabsList>
        <TabsContent value="results" className="mt-4">
          <Card className="p-6">
            {(mission.status === 'pending' || mission.status === 'running') ? (
              <div className="flex items-center gap-3">
                <Loader2 className="animate-spin text-blue-600" size={24} />
                <div>
                  <p className="font-medium text-slate-900">{t('dem.missionInProgress')}</p>
                  <p className="text-sm text-slate-500">{t('dem.pollingUpdates')}</p>
                </div>
              </div>
            ) : (
              <ExecutionTraceViewer mission={mission} />
            )}
          </Card>
        </TabsContent>
        <TabsContent value="reasoning" className="mt-4">
          <Card className="p-6">
            {mission.reasoning ? (
              <div>
                <h3 className="font-medium text-slate-900 mb-2">{t('dem.decisionTrace')}</h3>
                <p className="text-sm text-slate-700 whitespace-pre-wrap">{mission.reasoning}</p>
                {mission.requires_approval && (
                  <div className="mt-4 bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 rounded-lg">
                    <p className="font-medium">{t('dem.approvalRequired')}</p>
                    <p className="text-sm mt-1">{t('dem.approvalStatus')}: {mission.approval_status || 'pending'}</p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-slate-500">{t('dem.noReasoningTrace')}</p>
            )}
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
