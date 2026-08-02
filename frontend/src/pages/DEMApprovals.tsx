import { useEffect, useState } from 'react';
import { Check, X, Brain, AlertTriangle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useApprovalStore } from '@/store/approvalStore';
import { useAuthStore } from '@/store/authStore';
import { getApprovals, approveMission, rejectMission } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

export function DEMApprovals() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const { approvals, setApprovals, removeApproval } = useApprovalStore();
  const user = useAuthStore((s) => s.user);
  const [isLoading, setIsLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);

  const loadApprovals = async () => {
    setIsLoading(true);
    try {
      const res = await getApprovals();
      const data = res.data;
      setApprovals(Array.isArray(data) ? data : []);
    } catch {
      toast({ title: t('common.error'), description: t('dem.loadApprovalsError'), variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadApprovals(); }, []);

  const handleApprove = async (approvalId: string) => {
    setActionId(approvalId);
    try {
      await approveMission(approvalId);
      removeApproval(approvalId);
      toast({ title: t('dem.approved'), description: t('dem.approvalRecorded') });
    } catch {
      toast({ title: t('common.error'), description: t('dem.approveError'), variant: 'destructive' });
    } finally {
      setActionId(null);
    }
  };

  const handleReject = async (approvalId: string) => {
    setActionId(approvalId);
    try {
      await rejectMission(approvalId);
      removeApproval(approvalId);
      toast({ title: t('dem.rejected'), description: t('dem.rejectionRecorded') });
    } catch {
      toast({ title: t('common.error'), description: t('dem.rejectError'), variant: 'destructive' });
    } finally {
      setActionId(null);
    }
  };

  if (user?.role !== 'owner' && user?.role !== 'manager') {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">{t('dem.noPermissionApprovals')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('dem.approvalInbox')}</h1>
          <p className="text-slate-500 text-sm">{t('dem.reviewApprovals')}</p>
        </div>
        <Button variant="outline" size="sm" onClick={loadApprovals}>{t('dem.refresh')}</Button>
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
      ) : approvals.length === 0 ? (
        <Card className="p-8 text-center">
          <Brain className="mx-auto text-slate-300 mb-3" size={48} />
          <p className="text-slate-500">{t('dem.noPendingApprovals')}</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {approvals.map((approval) => (
            <Card key={approval.mission_id} className="p-5">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="text-orange-500" size={18} />
                    <Badge variant="outline">{approval.mission_type || 'Unknown'}</Badge>
                    <Badge variant="secondary">{t('dem.pendingApprovalBadge')}</Badge>
                  </div>
                  <p className="text-sm text-slate-600 mb-1">
                    Mission: {approval.mission_id.slice(0, 16)}...
                  </p>
                  <p className="text-sm text-slate-600 mb-1">
                    Session: {approval.session_id.slice(0, 8)}...
                  </p>
                  {approval.reasoning && (
                    <div className="mt-3 bg-slate-50 p-3 rounded-lg">
                      <p className="text-xs font-medium text-slate-700 mb-1">{t('dem.reasoning')}</p>
                      <p className="text-xs text-slate-600">{approval.reasoning}</p>
                    </div>
                  )}
                </div>
                <div className="flex gap-2 ml-4">
                  <Button
                    size="sm"
                    onClick={() => handleApprove(approval.mission_id)}
                    disabled={actionId === approval.mission_id}
                    className="gap-1"
                  >
                    <Check size={14} />
                    {t('dem.approve')}
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleReject(approval.mission_id)}
                    disabled={actionId === approval.mission_id}
                    className="gap-1"
                  >
                    <X size={14} />
                    {t('dem.reject')}
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
