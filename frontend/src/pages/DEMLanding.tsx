import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Rocket, LogOut, History, Zap, Brain } from 'lucide-react';
import { useDEMStore } from '@/store/demStore';
import { useAuthStore } from '@/store/authStore';
import { connectToDEM, disconnectDEM, getDEMSession } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export function DEMLanding() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const user = useAuthStore((s) => s.user);
  const { activeSession, isLoading, error, setActiveSession, setLoading, setError, reset } = useDEMStore();

  useEffect(() => {
    if (activeSession) {
      getDEMSession(activeSession.session_id)
        .then((res) => {
          const data = res.data;
          setActiveSession({
            session_id: data.session_id,
            status: data.status,
            started_at: data.started_at,
            ended_at: data.ended_at,
          });
        })
        .catch(() => {});
    }
  }, [activeSession, setActiveSession]);

  const handleConnect = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await connectToDEM({ user_id: user?.id || 1 });
      const session = {
        session_id: response.data.session_id,
        status: response.data.status,
        started_at: response.data.created_at,
      };
      setActiveSession(session);
      toast({ title: t('dem.connected'), description: response.data.message });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to connect');
      toast({ title: t('common.error'), description: error.response?.data?.detail || 'Failed to connect', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!activeSession) return;
    setLoading(true);
    try {
      await disconnectDEM(activeSession.session_id);
      reset();
      toast({ title: t('dem.disconnected'), description: 'Session closed successfully' });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast({ title: t('common.error'), description: error.response?.data?.detail || 'Failed to disconnect', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
          <Brain className="text-white" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('dem.title')}</h1>
          <p className="text-slate-500 text-sm">{t('dem.subtitle')}</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">{t('dem.sessionStatus')}</h2>
            <p className="text-slate-500 text-sm mt-1">
              {activeSession ? (
                <span className="flex items-center gap-2">
                  <Badge variant={activeSession.status === 'active' ? 'default' : 'secondary'}>
                    {activeSession.status}
                  </Badge>
                  <span className="text-xs text-slate-400">
                    Started: {new Date(activeSession.started_at).toLocaleString()}
                  </span>
                </span>
              ) : (
                t('dem.noActiveSession')
              )}
            </p>
          </div>
          <div className="flex gap-2">
            {!activeSession ? (
              <Button onClick={handleConnect} disabled={isLoading} className="gap-2">
                <Rocket size={16} />
                {isLoading ? t('common.loading') : t('dem.connect')}
              </Button>
            ) : (
              <>
                <Button variant="outline" onClick={() => navigate('/digital-export-manager/missions/new')} className="gap-2">
                  <Zap size={16} />
                  {t('dem.newMission')}
                </Button>
                <Button variant="outline" onClick={() => navigate('/digital-export-manager/sessions')} className="gap-2">
                  <History size={16} />
                  {t('dem.sessionHistory')}
                </Button>
                <Button variant="destructive" onClick={handleDisconnect} disabled={isLoading} className="gap-2">
                  <LogOut size={16} />
                  {t('dem.disconnect')}
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate('/digital-export-manager/missions')}>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <Zap className="text-blue-600" size={18} />
            </div>
            <div>
              <p className="font-medium text-slate-900">{t('dem.missions')}</p>
              <p className="text-xs text-slate-500">{t('dem.viewMissions')}</p>
            </div>
          </div>
        </Card>
        <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate('/digital-export-manager/approvals')}>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
              <Brain className="text-amber-600" size={18} />
            </div>
            <div>
              <p className="font-medium text-slate-900">{t('dem.approvals')}</p>
              <p className="text-xs text-slate-500">{t('dem.reviewApprovals')}</p>
            </div>
          </div>
        </Card>
        <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate('/knowledge-graph')}>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <Brain className="text-purple-600" size={18} />
            </div>
            <div>
              <p className="font-medium text-slate-900">{t('dem.knowledgeGraph')}</p>
              <p className="text-xs text-slate-500">{t('dem.exploreKnowledge')}</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
