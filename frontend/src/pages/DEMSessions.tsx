import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Calendar, ChevronRight, RefreshCw } from 'lucide-react';
import { useDEMStore } from '@/store/demStore';
import { getDEMSessions, getDEMSession, getDEMExecutionState } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

interface SessionSummary {
  session_id: string;
  user_id: number;
  status: string;
  started_at: string;
  ended_at?: string;
  mission_count: number;
}

export function DEMSessions() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { setMissions } = useDEMStore();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [executionSummaries, setExecutionSummaries] = useState<Record<string, { completed: number; failed: number; pending_approval: number }>>({});
  const [isLoading, setIsLoading] = useState(true);

  const loadSessions = async () => {
    setIsLoading(true);
    try {
      const res = await getDEMSessions();
      const data = res.data;
      setSessions(data || []);
      const summaries: Record<string, { completed: number; failed: number; pending_approval: number }> = {};
      for (const session of data || []) {
        try {
          const stateRes = await getDEMExecutionState(session.session_id);
          const state = stateRes.data;
          summaries[session.session_id] = {
            completed: state.completed_missions || 0,
            failed: state.failed_missions || 0,
            pending_approval: state.pending_approval_missions || 0,
          };
        } catch {
          summaries[session.session_id] = { completed: 0, failed: 0, pending_approval: 0 };
        }
      }
      setExecutionSummaries(summaries);
    } catch {
      toast({ title: t('common.error'), description: 'Failed to load sessions', variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadSessions(); }, []);

  const handleSessionClick = async (sessionId: string) => {
    try {
      const res = await getDEMSession(sessionId);
      const data = res.data;
      if (data.missions) {
        setMissions(data.missions.map((m: Record<string, unknown>) => ({
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
        })));
      }
      navigate(`/digital-export-manager/sessions/${sessionId}`);
    } catch {
      toast({ title: t('common.error'), description: 'Failed to load session details', variant: 'destructive' });
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      active: 'default',
      completed: 'secondary',
      failed: 'destructive',
      pending_approval: 'outline',
    };
    return <Badge variant={variants[status] || 'secondary'}>{status}</Badge>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('dem.sessions')}</h1>
          <p className="text-slate-500 text-sm">{t('dem.sessionHistory')}</p>
        </div>
        <Button variant="outline" size="sm" onClick={loadSessions} className="gap-2">
          <RefreshCw size={14} />
          {t('common.loading')}
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-4">
              <Skeleton className="h-5 w-1/3 mb-2" />
              <Skeleton className="h-4 w-1/2" />
            </Card>
          ))}
        </div>
      ) : sessions.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-slate-500">{t('dem.noSessions')}</p>
          <Button className="mt-4" onClick={() => navigate('/digital-export-manager')}>
            {t('dem.connect')}
          </Button>
        </Card>
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => (
            <Card key={session.session_id} className="p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleSessionClick(session.session_id)}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Calendar className="text-slate-400" size={20} />
                  <div>
                    <p className="font-medium text-slate-900">Session {session.session_id.slice(0, 8)}...</p>
                    <p className="text-xs text-slate-500">
                      {new Date(session.started_at).toLocaleString()} · {session.mission_count} missions
                    </p>
                    {executionSummaries[session.session_id] && (
                      <p className="text-xs text-slate-500">
                        Completed: {executionSummaries[session.session_id].completed} · Failed: {executionSummaries[session.session_id].failed} · Pending Approval: {executionSummaries[session.session_id].pending_approval}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(session.status)}
                  <ChevronRight className="text-slate-400" size={16} />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
