import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Rocket, Loader2 } from 'lucide-react';
import { useDEMStore } from '@/store/demStore';
import { createMission } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';

const MISSION_TYPES = [
  { type: 'CREATE_SHIPMENT', defaultPayload: { origin: '', destination: '', weight: 0 } },
  { type: 'SUBMIT_INVOICE', defaultPayload: { invoice_number: '', customer_id: 0 } },
  { type: 'FILE_CUSTOMS', defaultPayload: { declaration_number: '', hs_code_id: 0 } },
  { type: 'GENERATE_DOCUMENT', defaultPayload: { document_type: 'commercial_invoice' } },
  { type: 'SEARCH_ENTITIES', defaultPayload: { query: '' } },
  { type: 'GET_DASHBOARD', defaultPayload: {} },
  { type: 'SEND_NOTIFICATION', defaultPayload: { recipient: '', template_id: 0 } },
  { type: 'TRANSITION_WORKFLOW', defaultPayload: { workflow_id: 0, target_state: '' } },
];

export function DEMMissionComposer() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { activeSession, setCurrentMission } = useDEMStore();
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [payload, setPayload] = useState<Record<string, unknown>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingTools, setIsLoadingTools] = useState(true);

  useEffect(() => {
    setIsLoadingTools(false);
  }, []);

  const handleSubmit = async () => {
    if (!activeSession || !selectedType) return;
    setIsLoading(true);
    try {
      const response = await createMission(activeSession.session_id, {
        mission_type: selectedType,
        payload,
      });
      const mission = response.data;
      setCurrentMission({
        mission_id: mission.mission_id,
        session_id: activeSession.session_id,
        status: mission.status,
        result: mission.result,
        error: mission.error,
        created_at: new Date().toISOString(),
        completed_at: mission.completed_at,
        reasoning: mission.reasoning,
        requires_approval: mission.requires_approval,
        approval_status: mission.approval_status,
      });
      toast({ title: t('dem.newMission'), description: `Mission ${mission.mission_id.slice(0, 8)}... created` });
      navigate(`/digital-export-manager/missions/${mission.mission_id}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast({ title: t('common.error'), description: error.response?.data?.detail || t('common.error'), variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTypeSelect = (type: string) => {
    setSelectedType(type);
    const found = MISSION_TYPES.find((m) => m.type === type);
    setPayload(found?.defaultPayload || {});
  };

  if (!activeSession) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 mb-4">{t('dem.connectDemFirst')}</p>
        <Button onClick={() => navigate('/digital-export-manager')}>{t('dem.goToDem')}</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t('dem.newMission')}</h1>
        <p className="text-slate-500 text-sm">{t('dem.selectMissionConfigure')}</p>
      </div>

      <Card className="p-6">
        <h2 className="font-medium text-slate-900 mb-4">{t('dem.missionType')}</h2>
        {isLoadingTools ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {MISSION_TYPES.map(({ type }) => (
              <Card
                key={type}
                className={`p-3 cursor-pointer transition-all hover:shadow-md ${selectedType === type ? 'ring-2 ring-emerald-500' : ''}`}
                onClick={() => handleTypeSelect(type)}
              >
                <p className="font-medium text-sm text-slate-900">{t(`dem.missionTypes.${type.toLowerCase()}`) || type}</p>
              </Card>
            ))}
          </div>
        )}
      </Card>

      {selectedType && (
        <Card className="p-6">
          <h2 className="font-medium text-slate-900 mb-4">{t('dem.parameters')}</h2>
          <div className="space-y-4">
            {Object.entries(MISSION_TYPES.find((m) => m.type === selectedType)?.defaultPayload || {}).map(([key, _val]) => (
              <div key={key} className="space-y-1">
                <Label htmlFor={key} className="text-sm capitalize">{key.replace(/_/g, ' ')}</Label>
                <Input
                  id={key}
                  value={String(payload[key] || '')}
                  onChange={(e) => setPayload({ ...payload, [key]: e.target.value })}
                  placeholder={`Enter ${key}`}
                />
              </div>
            ))}
          </div>
          <div className="mt-6 flex justify-end gap-2">
            <Button variant="outline" onClick={() => navigate('/digital-export-manager')}>{t('common.cancel')}</Button>
            <Button onClick={handleSubmit} disabled={isLoading} className="gap-2">
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Rocket size={16} />}
              {isLoading ? t('dem.submitting') : t('dem.submitMission')}
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
