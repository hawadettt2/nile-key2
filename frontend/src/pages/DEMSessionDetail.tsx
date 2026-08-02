import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { useDEMStore } from '@/store/demStore';
import { getDEMSession } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';

const statusIcons: Record<string, React.ReactNode> = {
  completed: <CheckCircle className="text-green-600" size={16} />,
  failed: <XCircle className="text-red-600" size={16} />,
  pending: <Clock className="text-amber-600" size={16} />,
  running: <Clock className="text-blue-600" size={16} />,
  pending_approval: <AlertTriangle className="text-orange-600" size={16} />,
};

export function DEMSessionDetail() {
  const { t } = useTranslation();
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { missions, setMissions } = useDEMStore();
  const [session, setSession] = useState<Record<string, unknown> | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    setIsLoading(true);
    getDEMSession(sessionId)
      .then((res) => {
        const data = res.data;
        setSession(data);
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
      })
      .catch(() => toast({ title: t('common.error'), description: t('dem.loadApprovalsError'), variant: 'destructive' }))
      .finally(() => setIsLoading(false));
  }, [sessionId, t, toast]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!session) {
    return <div className="text-center text-slate-500">{t('dem.sessionNotFound')}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => navigate('/digital-export-manager/sessions')}>
          <ArrowLeft size={20} />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('dem.sessions')} {session.session_id?.toString().slice(0, 8)}...</h1>
          <p className="text-slate-500 text-sm">
            {t('dem.createdOn')} {new Date(session.started_at as string).toLocaleString()}
          </p>
        </div>
      </div>

      <Tabs defaultValue="missions">
        <TabsList>
          <TabsTrigger value="missions">{t('dem.missionsTab')} ({missions.length})</TabsTrigger>
          <TabsTrigger value="context">{t('dem.contextTab')}</TabsTrigger>
        </TabsList>
        <TabsContent value="missions" className="space-y-3 mt-4">
          {missions.length === 0 ? (
            <Card className="p-6 text-center text-slate-500">{t('dem.noMissionsInSession')}</Card>
          ) : (
            missions.map((mission) => (
              <Card key={mission.mission_id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {statusIcons[mission.status] || <Clock size={16} />}
                    <div>
                      <p className="font-medium text-slate-900">{mission.mission_id.slice(0, 12)}...</p>
                      <p className="text-xs text-slate-500">{new Date(mission.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={mission.status === 'completed' ? 'default' : mission.status === 'failed' ? 'destructive' : 'secondary'}>
                      {mission.status}
                    </Badge>
                    <Button variant="ghost" size="sm" onClick={() => navigate(`/digital-export-manager/missions/${mission.mission_id}`)}>
                      {t('common.view')}
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </TabsContent>
        <TabsContent value="context" className="mt-4">
          <Card className="p-4">
            <pre className="text-xs text-slate-600 overflow-auto max-h-96">
              {JSON.stringify(session.context || {}, null, 2)}
            </pre>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
