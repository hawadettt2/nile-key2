import { useState } from 'react';
import { TrendingUp, BarChart3, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTradeIntelligenceStore } from '@/store/tradeIntelligenceStore';
import { analyzeSupplier, detectTrends } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export function TradeIntelligence() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const { supplierAnalysis, trends, setSupplierAnalysis, setTrends, setLoading, setError } = useTradeIntelligenceStore();
  const [supplierId, setSupplierId] = useState('');
  const [entityType, setEntityType] = useState('supplier');
  const [analyzing, setAnalyzing] = useState(false);

  const handleSupplierAnalysis = async () => {
    if (!supplierId) return;
    setAnalyzing(true);
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeSupplier({ supplier_id: parseInt(supplierId), analysis_type: 'full' });
      setSupplierAnalysis({
        supplier_id: parseInt(supplierId),
        analysis_type: 'full',
        results: res.data as Record<string, unknown>,
        generated_at: new Date().toISOString(),
      });
      toast({ title: t('tradeIntelligence.analysisComplete'), description: t('tradeIntelligence.analysisGenerated') });
    } catch {
      setError('Analysis failed');
      toast({ title: t('common.error'), description: t('tradeIntelligence.analyzeFailed'), variant: 'destructive' });
    } finally {
      setAnalyzing(false);
      setLoading(false);
    }
  };

  const handleTrendDetection = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await detectTrends({ entity_type: entityType, trend_parameters: {} });
      const trendsData = (res.data as Record<string, unknown>) || {};
      setTrends({
        entity_type: entityType,
        trends: Array.isArray(trendsData.trends) ? trendsData.trends as Record<string, unknown>[] : [],
        generated_at: new Date().toISOString(),
      });
      toast({ title: t('tradeIntelligence.detectedTrends'), description: t('tradeIntelligence.selectEntityTrends') });
    } catch {
      setError('Trend detection failed');
      toast({ title: t('common.error'), description: t('tradeIntelligence.analyzeFailed'), variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t('tradeIntelligence.title')}</h1>
        <p className="text-slate-500 text-sm">{t('tradeIntelligence.subtitle')}</p>
      </div>

      <Tabs defaultValue="supplier">
        <TabsList>
          <TabsTrigger value="supplier" className="gap-2"><BarChart3 size={14} /> {t('tradeIntelligence.supplierAnalysis')}</TabsTrigger>
          <TabsTrigger value="trends" className="gap-2"><TrendingUp size={14} /> {t('tradeIntelligence.trends')}</TabsTrigger>
        </TabsList>
        <TabsContent value="supplier" className="mt-4 space-y-4">
          <Card className="p-4">
            <div className="flex gap-2">
              <Input
                type="number"
                placeholder={t('tradeIntelligence.supplierId')}
                value={supplierId}
                onChange={(e) => setSupplierId(e.target.value)}
                className="max-w-xs"
              />
              <Button onClick={handleSupplierAnalysis} disabled={analyzing || !supplierId} className="gap-2">
                {analyzing ? <Loader2 size={14} className="animate-spin" /> : <BarChart3 size={14} />}
                {analyzing ? t('tradeIntelligence.analyzing') : t('tradeIntelligence.analyze')}
              </Button>
            </div>
          </Card>
          {supplierAnalysis ? (
            <Card className="p-6">
              <h3 className="font-medium text-slate-900 mb-4">{t('tradeIntelligence.supplierAnalysisResults')}</h3>
              <pre className="bg-slate-50 p-4 rounded-lg text-xs overflow-auto max-h-96 text-slate-700">
                {JSON.stringify(supplierAnalysis.results, null, 2)}
              </pre>
            </Card>
          ) : (
            <Card className="p-8 text-center">
              <BarChart3 className="mx-auto text-slate-300 mb-3" size={48} />
              <p className="text-slate-500">{t('tradeIntelligence.enterSupplierId')}</p>
            </Card>
          )}
        </TabsContent>
        <TabsContent value="trends" className="mt-4 space-y-4">
          <Card className="p-4">
            <div className="flex gap-2">
              <select
                value={entityType}
                onChange={(e) => setEntityType(e.target.value)}
                className="border border-slate-200 rounded-md px-3 text-sm"
              >
                <option value="supplier">{t('knowledgeGraph.supplier')}</option>
                <option value="customer">{t('knowledgeGraph.customer')}</option>
                <option value="shipment">{t('knowledgeGraph.shipment')}</option>
              </select>
              <Button onClick={handleTrendDetection} className="gap-2">
                <TrendingUp size={14} />
                {t('tradeIntelligence.detectTrends')}
              </Button>
            </div>
          </Card>
          {trends && trends.trends.length > 0 ? (
            <Card className="p-6">
              <h3 className="font-medium text-slate-900 mb-4">{t('tradeIntelligence.detectedTrends')}</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trends.trends as Record<string, unknown>[]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#10b981" />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          ) : (
            <Card className="p-8 text-center">
              <TrendingUp className="mx-auto text-slate-300 mb-3" size={48} />
              <p className="text-slate-500">{t('tradeIntelligence.selectEntityTrends')}</p>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
