import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/store/authStore';
import { useArchitectureExplorerStore, type ArchitectureNode } from '@/store/architectureExplorerStore';
import { getArchitectureMetadata, getArchitectureNode, projectArchitectureLevel } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ChevronDown, ChevronRight, FileText, Settings } from 'lucide-react';

export function ArchitectureExplorer() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const { metadata, nodes, edges, isLoading, error, setMetadata, setNodes, setEdges, setLoading, setError } = useArchitectureExplorerStore();
  const [expandedNode, setExpandedNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<ArchitectureNode | null>(null);

  const loadArchitecture = async () => {
    setLoading(true);
    setError(null);
    try {
      const metadataRes = await getArchitectureMetadata();
      setMetadata(metadataRes.data);

      const level0Res = await projectArchitectureLevel(0);
      setNodes(level0Res.data.nodes || []);
      setEdges(level0Res.data.edges || []);
    } catch {
      setError(t('architectureExplorer.error'));
      toast({ title: t('common.error'), description: t('architectureExplorer.error'), variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadArchitecture();
  }, []);

  const nodeMap = nodes.reduce<Record<string, ArchitectureNode>>((acc, node) => {
    acc[node.id] = node;
    return acc;
  }, {});

  const spineNodes = nodes;

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
          <Button variant="outline" size="sm" onClick={loadArchitecture} disabled={isLoading}>
            {t('architectureExplorer.retry')}
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Layers className="text-emerald-600" size={20} />
          <h2 className="text-lg font-semibold text-slate-900">{t('architectureExplorer.level0')}</h2>
        </div>
        <p className="text-slate-500 text-sm mb-6">{t('architectureExplorer.description')}</p>

        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        ) : spineNodes.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-slate-500">{t('common.noData')}</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {spineNodes.map((node, index) => {
              if (!node) return null;
              const Icon = NODE_ICONS[node.id] || Settings;
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
                        children.map(child => {
                          return (
                            <Card key={child.id} className="p-3 bg-slate-50 border-slate-200">
                              <div className="flex items-center gap-2">
                                <Settings size={16} className="text-slate-400" />
                                <div>
                                  <p className="text-sm font-medium text-slate-700">{child.technical_name}</p>
                                  <p className="text-xs text-slate-500">{child.arabic_meaning}</p>
                                </div>
                              </div>
                            </Card>
                          );
                        })
                      )}
                    </div>
                  )}

                  {index < spineNodes.length - 1 && (
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
