import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Wrench } from 'lucide-react';
import { getDEMTools } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

interface ToolInfo {
  name: string;
  description: string;
  category: string;
  input_schema?: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
}

export function DEMTools() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getDEMTools()
      .then((res) => {
        const data = res.data;
        setTools((data.tools || []).map((t: Record<string, unknown>) => ({
          name: t.name as string,
          description: (t.description as string) || '',
          category: (t.category as string) || 'general',
          input_schema: t.input_schema as Record<string, unknown> | undefined,
          output_schema: t.output_schema as Record<string, unknown> | undefined,
        })));
      })
      .catch(() => toast({ title: t('common.error'), description: t('dem.loadApprovalsError'), variant: 'destructive' }))
      .finally(() => setIsLoading(false));
  }, [t, toast]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t('dem.toolsTitle')}</h1>
        <p className="text-slate-500 text-sm">{t('dem.toolsSubtitle')}</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="p-4">
              <Skeleton className="h-5 w-1/3 mb-2" />
              <Skeleton className="h-4 w-full" />
            </Card>
          ))}
        </div>
      ) : tools.length === 0 ? (
        <Card className="p-8 text-center">
          <Wrench className="mx-auto text-slate-300 mb-3" size={48} />
          <p className="text-slate-500">{t('dem.noToolsAvailable')}</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tools.map((tool) => (
            <Card key={tool.name} className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-slate-900">{tool.name}</h3>
                <Badge variant="secondary">{tool.category}</Badge>
              </div>
              <p className="text-sm text-slate-600">{tool.description}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
