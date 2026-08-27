import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useArchitectureExplorerStore, type ArchitectureNode } from '@/store/architectureExplorerStore';
import { getArchitectureMetadata, getArchitectureNode, projectArchitectureLevel } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ChevronDown, ChevronRight, FileText, Settings, Box, Cpu, Workflow, Cog } from 'lucide-react';

type LevelView = 0 | 1 | 2 | 3;

const LEVEL_CONFIG: Record<LevelView, { key: string; icon: typeof Box; color: string }> = {
  0: { key: 'level0', icon: Box, color: 'text-emerald-600' },
  1: { key: 'level1', icon: Cpu, color: 'text-indigo-600' },
  2: { key: 'level2', icon: Cog, color: 'text-amber-600' },
  3: { key: 'level3', icon: Workflow, color: 'text-purple-600' },
};

export function ArchitectureExplorer() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const { metadata, nodes, edges, isLoading, error, setMetadata, setNodes, setEdges, setLoading, setError } = useArchitectureExplorerStore();
  const [activeLevel, setActiveLevel] = useState<LevelView>(0);
  const [expandedNode, setExpandedNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<ArchitectureNode | null>(null);

  const loadLevel = async (level: LevelView) => {
    setLoading(true);
    setError(null);
    try {
      const metadataRes = await getArchitectureMetadata();
      setMetadata(metadataRes.data);

      const levelRes = await projectArchitectureLevel(level);
      setNodes(levelRes.data.nodes || []);
      setEdges(levelRes.data.edges || []);
    } catch {
      setError(t('architectureExplorer.error'));
      toast({ title: t('common.error'), description: t('architectureExplorer.error'), variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLevel(0);
  }, []);

  const handleLevelChange = (value: string) => {
    const level = Number(value) as LevelView;
    setActiveLevel(level);
    setExpandedNode(null);
    setSelectedNode(null);
    loadLevel(level);
  };

  const nodeMap = nodes.reduce<Record<string, ArchitectureNode>>((acc, node) => {
    acc[node.id] = node;
    return acc;
  }, {});

  const getChildren = (nodeId: string): ArchitectureNode[] => {
    return edges
      .filter(edge => edge.source === nodeId && edge.direction === 'outbound')
      .map(edge => nodeMap[edge.target])
      .filter((node): node is ArchitectureNode => Boolean(node));
  };

  const handleNodeClick = async (nodeId: string) => {
    setExpandedNode(expandedNode === nodeId ? null : nodeId);
    if (expandedNode !== nodeId) {
      try {
        const res = await getArchitectureNode(nodeId);
        setSelectedNode(res.data);
      } catch {
        toast({ title: t('common.error'), description: 'Failed to load node details', variant: 'destructive' });
      }
    }
  };

  const levelConfig = LEVEL_CONFIG[activeLevel];
  const LevelIcon = levelConfig.icon;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('architectureExplorer.title')}</h1>
          <p className="text-slate-500 text-sm mt-1">{t('architectureExplorer.subtitle')}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs">
            {metadata?.version || '...'}
          </Badge>
          <Button variant="outline" size="sm" onClick={() => loadLevel(activeLevel)} disabled={isLoading}>
            {t('architectureExplorer.retry')}
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <Tabs value={String(activeLevel)} onValueChange={handleLevelChange}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="0" className="flex items-center gap-2">
            <Box size={16} />
            {t('architectureExplorer.level0')}
          </TabsTrigger>
          <TabsTrigger value="1" className="flex items-center gap-2">
            <Cpu size={16} />
            {t('architectureExplorer.level1')}
          </TabsTrigger>
          <TabsTrigger value="2" className="flex items-center gap-2">
            <Cog size={16} />
            {t('architectureExplorer.level2')}
          </TabsTrigger>
          <TabsTrigger value="3" className="flex items-center gap-2">
            <Workflow size={16} />
            {t('architectureExplorer.level3')}
          </TabsTrigger>
        </TabsList>

        {([0, 1, 2, 3] as LevelView[]).map((level) => (
          <TabsContent key={level} value={String(level)} className="mt-4">
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <LevelIcon className={levelConfig.color} size={20} />
                <h2 className="text-lg font-semibold text-slate-900">{t(`architectureExplorer.${LEVEL_CONFIG[level].key}`)}</h2>
              </div>

              {isLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Skeleton key={i} className="h-24 w-full" />
                  ))}
                </div>
              ) : nodes.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-slate-500">{t('common.noData')}</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {nodes.map((node, index) => {
                    const isExpanded = expandedNode === node.id;
                    const children = getChildren(node.id);

                    return (
                      <div key={node.id} className="relative">
                        <Card
                          className="p-4 cursor-pointer transition-all hover:shadow-md border bg-white border-slate-200"
                          onClick={() => handleNodeClick(node.id)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-lg bg-white/80 flex items-center justify-center">
                                <Settings size={24} />
                              </div>
                              <div>
                                <p className="font-medium text-slate-900">{node.technical_name}</p>
                                <p className="text-xs text-slate-500">{node.arabic_meaning}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge variant="secondary" className="text-xs">
                                {node.type}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {node.status}
                              </Badge>
                              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                            </div>
                          </div>
                        </Card>

                        {isExpanded && (
                          <div className="mr-12 mt-2 space-y-2">
                            {children.length === 0 ? (
                              <p className="text-xs text-slate-400 italic">{t('common.noData')}</p>
                            ) : (
                              children.map((child) => (
                                <Card key={child.id} className="p-3 bg-slate-50 border-slate-200">
                                  <div className="flex items-center gap-2">
                                    <Settings size={16} className="text-slate-400" />
                                    <div>
                                      <p className="text-sm font-medium text-slate-700">{child.technical_name}</p>
                                      <p className="text-xs text-slate-500">{child.arabic_meaning}</p>
                                    </div>
                                  </div>
                                </Card>
                              ))
                            )}
                          </div>
                        )}

                        {index < nodes.length - 1 && (
                          <div className="flex justify-center my-1">
                            <ChevronDown className="text-slate-300" size={20} />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {selectedNode && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Node Details</h3>
            <Button variant="ghost" size="sm" onClick={() => setSelectedNode(null)}>
              Close
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-slate-500">ID</p>
              <p className="text-sm text-slate-900 font-mono">{selectedNode.id}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Type</p>
              <p className="text-sm text-slate-900">{selectedNode.type}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Status</p>
              <Badge variant="secondary">{selectedNode.status}</Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">Levels</p>
              <p className="text-sm text-slate-900">{selectedNode.levels.join(', ')}</p>
            </div>
            <div className="md:col-span-2">
              <p className="text-sm font-medium text-slate-500 mb-1">Responsibilities</p>
              <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                {selectedNode.responsibilities.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="md:col-span-2">
              <p className="text-sm font-medium text-slate-500 mb-1">Non-Responsibilities</p>
              <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                {selectedNode.non_responsibilities.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="md:col-span-2">
              <p className="text-sm font-medium text-slate-500 mb-1">Evidence</p>
              <div className="space-y-1">
                {selectedNode.evidence.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm text-slate-700">
                    <FileText size={14} className="text-slate-400" />
                    <span className="font-mono text-xs">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
