import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Plus, Search } from 'lucide-react';
import { useDEMStore } from '@/store/demStore';
import { getDEMSession } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

const statusColors: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  completed: 'default',
  failed: 'destructive',
  pending: 'secondary',
  running: 'outline',
  pending_approval: 'outline',
};

export function DEMMissions() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { missions, activeSession, setMissions } = useDEMStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredMissions, setFilteredMissions] = useState<typeof missions>([]);

  useEffect(() => {
    if (missions.length === 0 && activeSession) {
      getDEMSession(activeSession.session_id)
        .then((res) => {
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
        })
        .catch(() => {});
    }
  }, [missions.length, activeSession, setMissions]);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredMissions(useDEMStore.getState().missions);
    } else {
      const q = searchQuery.toLowerCase();
      setFilteredMissions(
        useDEMStore.getState().missions.filter(
          (m) => m.mission_id.toLowerCase().includes(q) || m.status.toLowerCase().includes(q)
        )
      );
    }
  }, [searchQuery, missions]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('dem.missionsTitle')}</h1>
          <p className="text-slate-500 text-sm">{t('dem.missionsSubtitle')}</p>
        </div>
        <Button onClick={() => navigate('/digital-export-manager/missions/new')} className="gap-2">
          <Plus size={16} />
          {t('dem.newMission')}
        </Button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
        <Input
          placeholder={t('dem.searchMissionsPlaceholder')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      {filteredMissions.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-slate-500">{t('dem.noMissionsFound')}</p>
          <Button className="mt-4" onClick={() => navigate('/digital-export-manager/missions/new')}>
            {t('dem.createFirstMission')}
          </Button>
        </Card>
      ) : (
        <div className="space-y-3">
          {filteredMissions.map((mission) => (
            <Card key={mission.mission_id} className="p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => navigate(`/digital-export-manager/missions/${mission.mission_id}`)}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">{mission.mission_id.slice(0, 16)}...</p>
                  <p className="text-xs text-slate-500">
                    {new Date(mission.created_at).toLocaleString()} · Session {mission.session_id.slice(0, 8)}...
                  </p>
                  {mission.result && (
                    <p className="text-xs text-slate-500">
                      Outcome: {mission.result.mission_status || 'unknown'} · Steps: {(mission.result.results || []).length}
                    </p>
                  )}
                </div>
                <Badge variant={statusColors[mission.status] || 'secondary'}>{mission.status}</Badge>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
