import { useEffect, useState, useRef, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, CheckCircle, XCircle, Clock, AlertTriangle, FileText, Brain, Loader2 } from 'lucide-react';
import { useDEMStore } from '@/store/demStore';
import { getDEMSession } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

const MISSING_MISSION_MESSAGE_KEY = 'dem.missionNotFoundContext';

const statusConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  completed: { icon: <CheckCircle size={16} />, color: 'text-green-600', label: 'Completed' },
  failed: { icon: <XCircle size={16} />, color: 'text-red-600', label: 'Failed' },
  pending: { icon: <Clock size={16} />, color: 'text-amber-600', label: 'Pending' },
  running: { icon: <Clock size={16} />, color: 'text-blue-600' , label: 'Running' },
  pending_approval: { icon: <AlertTriangle size={16} />, color: 'text-orange-600', label: 'Pending Approval' },
};

function ExecutionTraceViewer({ mission }: { mission: Record<string, unknown> }) {
  const result = mission.result as Record<string, unknown> | undefined;
  const reasoning = mission.reasoning as string | undefined;
  const error = mission.error as string | undefined;
  const missionStatus = (mission.status as string) || 'pending';

  const stepStatusConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
    completed: { icon: <CheckCircle size={14} />, color: 'text-green-600', label: 'Completed' },
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
    if (Array.isArray(result.results)) return result.results as Record<string, unknown>[];
    if (Array.isArray(result.steps)) return result.steps as Record<string, unknown>[];
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
            {steps.map((step: Record<string, unknown>, idx: number) => (
              <Card key={idx} className="p-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-900">Step {idx + 1}</span>
                  {renderStepStatus((step.status as string) || 'pending')}
                </div>
                {step.tool && (
                  <p className="text-xs text-slate-500 mt-1">Tool: {step.tool as string}</p>
                )}
                {step.output !== undefined && (
                  <pre className="bg-slate-50 p-2 rounded text-xs overflow-auto mt-2 text-slate-700">
                    {JSON.stringify(step.output, null, 2)}
                  </pre>
                )}
                {step.error && (
                  <p className="text-sm text-red-600 mt-2">{step.error as string}</p>
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
      if (activeSession?.session_id) {
        setIsLoading(true);
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
              }));
              setMissions(mapped);
              const found = mapped.find((m: Record<string, unknown>) => m.mission_id === missionId);
              if (found) {
                setCurrentMission(found);
                setNotFoundMessage(null);
              } else {
                setNotFoundMessage(t(MISSING_MISSION_MESSAGE_KEY));
              }
            }
          })
          .catch(() => setNotFoundMessage(t(MISSING_MISSION_MESSAGE_KEY)))
          .finally(() => setIsLoading(false));
      } else {
        setNotFoundMessage(t(MISSING_MISSION_MESSAGE_KEY));
        setIsLoading(false);
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
