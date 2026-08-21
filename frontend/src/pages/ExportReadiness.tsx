import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { analyzeExportReadiness, type ExportReadinessReport } from '@/services/exportReadiness';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Rocket, Loader2, AlertCircle, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

const AVAILABILITY_CONFIG = {
  available: { labelKey: 'exportReadiness.available', variant: 'default' as const, icon: CheckCircle2, className: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  partial: { labelKey: 'exportReadiness.partial', variant: 'secondary' as const, icon: AlertTriangle, className: 'bg-amber-50 text-amber-700 border-amber-200' },
  not_available: { labelKey: 'exportReadiness.notAvailable', variant: 'destructive' as const, icon: AlertCircle, className: 'bg-red-50 text-red-700 border-red-200' },
};

export function ExportReadiness() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const [productId, setProductId] = useState('');
  const [hsCode, setHsCode] = useState('');
  const [productName, setProductName] = useState('');
  const [targetMarket, setTargetMarket] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ExportReadinessReport | null>(null);

  const handleAnalyze = async () => {
    if (!targetMarket.trim()) {
      setError('Target market is required');
      return;
    }
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const response = await analyzeExportReadiness({
        product_id: productId ? parseInt(productId) : undefined,
        hs_code: hsCode || undefined,
        product_name: productName || undefined,
        target_market: targetMarket.trim(),
      });
      setReport(response.data);
      toast({ title: t('common.success', 'Success'), description: 'Export readiness analysis completed' });
    } catch {
      setError('Analysis failed. Please try again.');
      toast({ title: t('common.error'), description: 'Failed to analyze export readiness', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const renderSection = (section: ExportReadinessSection) => {
    const config = AVAILABILITY_CONFIG[section.availability];
    const Icon = config.icon;

    return (
      <Card key={section.title} className="p-5 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="font-semibold text-slate-900">{section.title}</h3>
            <p className="text-xs text-slate-500 mt-0.5">Source: {section.source}</p>
          </div>
          <div className="flex flex-col items-end gap-1.5">
            <Badge variant={config.variant} className={`gap-1 ${config.className}`}>
              <Icon size={12} />
              {t(config.labelKey)}
            </Badge>
            {section.confidence !== null && section.confidence !== undefined && (
              <span className="text-[10px] text-slate-500">
                Confidence: {(section.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </div>

        {section.availability === 'not_available' && section.notes && (
          <Alert variant="destructive" className="py-2.5">
            <AlertCircle size={14} />
            <AlertDescription className="text-xs">{section.notes}</AlertDescription>
          </Alert>
        )}

        {section.availability === 'partial' && section.notes && (
          <Alert className="py-2.5 border-amber-200 bg-amber-50">
            <AlertTriangle size={14} className="text-amber-600" />
            <AlertDescription className="text-xs text-amber-800">{section.notes}</AlertDescription>
          </Alert>
        )}

        {section.data && (
          <div className="bg-slate-50 rounded-lg p-3 max-h-64 overflow-auto">
            <pre className="text-[11px] leading-relaxed text-slate-700 whitespace-pre-wrap">
              {JSON.stringify(section.data, null, 2)}
            </pre>
          </div>
        )}

        {section.availability !== 'not_available' && !section.data && (
          <p className="text-xs text-slate-500 italic">{t('exportReadiness.noDataSection')}</p>
        )}
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t('exportReadiness.title')}</h1>
        <p className="text-slate-500 text-sm">{t('exportReadiness.subtitle')}</p>
      </div>

      <Card className="p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="productId">{t('exportReadiness.productId')}</Label>
            <Input
              id="productId"
              type="number"
              placeholder="Optional"
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="hsCode">{t('exportReadiness.hsCode')}</Label>
            <Input
              id="hsCode"
              placeholder="Optional"
              value={hsCode}
              onChange={(e) => setHsCode(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="productName">{t('exportReadiness.productName')}</Label>
            <Input
              id="productName"
              placeholder="Optional"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="targetMarket">{t('exportReadiness.targetMarket')}</Label>
            <Input
              id="targetMarket"
              placeholder={t('exportReadiness.targetMarketPlaceholder')}
              value={targetMarket}
              onChange={(e) => setTargetMarket(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>
        <Button onClick={handleAnalyze} disabled={loading || !targetMarket.trim()} className="gap-2">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Rocket size={16} />}
          {loading ? t('exportReadiness.analyzing') : t('exportReadiness.analyze')}
        </Button>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircle size={16} />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading && !report && (
        <Card className="p-5 space-y-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-32 w-full" />
        </Card>
      )}

      {report && (
        <div className="space-y-5">
          <Card className="p-5">
            <h3 className="font-semibold text-slate-900 mb-1">{t('exportReadiness.productSummary')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div>
                <span className="text-slate-500">Product:</span>{' '}
                <span className="font-medium">{report.product.name || '—'}</span>
              </div>
              <div>
                <span className="text-slate-500">HS Code:</span>{' '}
                <span className="font-medium">{report.product.hs_code || '—'}</span>
              </div>
              <div>
                <span className="text-slate-500">Target Market:</span>{' '}
                <span className="font-medium">{report.target_market}</span>
              </div>
            </div>
            <p className="text-[11px] text-slate-400 mt-2">Report ID: {report.report_id}</p>
          </Card>

          <div className="space-y-3">
            <h3 className="font-semibold text-slate-900">{t('exportReadiness.analysisSections', 'Analysis Sections')}</h3>
            {report.sections.map(renderSection)}
          </div>

          <Card className="p-5">
            <h3 className="font-semibold text-slate-900 mb-2">{t('exportReadiness.actionChecklist')}</h3>
            {report.action_checklist.length > 0 ? (
              <ul className="space-y-1.5">
                {report.action_checklist.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">{t('exportReadiness.noActions')}</p>
            )}
          </Card>

          <Card className="p-5">
            <h3 className="font-semibold text-slate-900 mb-2">{t('exportReadiness.recommendation')}</h3>
            {report.recommendation ? (
              <p className="text-sm text-slate-700 whitespace-pre-wrap">{report.recommendation}</p>
            ) : (
              <div className="flex items-start gap-2 text-sm text-slate-500">
                <Info size={16} className="shrink-0 mt-0.5" />
                <span>{t('exportReadiness.noRecommendation')}</span>
              </div>
            )}
          </Card>

          <Alert className="border-slate-200 bg-slate-50">
            <Info size={16} />
            <AlertTitle>{t('exportReadiness.dataQualityNote')}</AlertTitle>
            <AlertDescription>{report.data_quality_note}</AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
