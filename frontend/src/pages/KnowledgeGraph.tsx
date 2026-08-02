import { useState } from 'react';
import { Search, Network } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useKnowledgeGraphStore, type GraphNode, type GraphEdge } from '@/store/knowledgeGraphStore';
import { searchGraph, getGraphNode, getGraphRelationships } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';

export function KnowledgeGraph() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const { searchResults, selectedNode, relationships, isLoading, setSearchResults, setSelectedNode, setRelationships, setLoading, setError } = useKnowledgeGraphStore();
  const [query, setQuery] = useState('');
  const [entityType, setEntityType] = useState('');
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setLoading(true);
    setError(null);
    try {
      const res = await searchGraph(query, entityType || undefined);
      setSearchResults(res.data || []);
    } catch {
      setError('Search failed');
      toast({ title: t('common.error'), description: 'Search failed', variant: 'destructive' });
    } finally {
      setSearching(false);
      setLoading(false);
    }
  };

  const handleNodeClick = async (node: GraphNode) => {
    setSelectedNode(node);
    setLoading(true);
    try {
      const [nodeRes, relRes] = await Promise.all([
        getGraphNode(node.entity_type, node.entity_id),
        getGraphRelationships(node.entity_type, node.entity_id),
      ]);
      setRelationships({ node: nodeRes.data, relationships: (relRes.data?.relationships || []) as GraphEdge[] });
    } catch {
      setError('Failed to load node details');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t('knowledgeGraph.title')}</h1>
        <p className="text-slate-500 text-sm">{t('knowledgeGraph.subtitle')}</p>
      </div>

      <Card className="p-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <Input
              placeholder={t('knowledgeGraph.searchPlaceholder')}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-9"
            />
          </div>
          <select
            value={entityType}
            onChange={(e) => setEntityType(e.target.value)}
            className="border border-slate-200 rounded-md px-3 text-sm"
          >
            <option value="">{t('knowledgeGraph.allTypes')}</option>
            <option value="supplier">{t('knowledgeGraph.supplier')}</option>
            <option value="customer">{t('knowledgeGraph.customer')}</option>
            <option value="shipment">{t('knowledgeGraph.shipment')}</option>
          </select>
          <Button onClick={handleSearch} disabled={searching}>
            {searching ? t('knowledgeGraph.searching') : t('common.search')}
          </Button>
        </div>
      </Card>

      <Tabs defaultValue="search">
        <TabsList>
          <TabsTrigger value="search">{t('knowledgeGraph.searchResults')}</TabsTrigger>
          <TabsTrigger value="detail">{t('knowledgeGraph.entityDetail')}</TabsTrigger>
        </TabsList>
        <TabsContent value="search" className="mt-4">
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : searchResults.length === 0 ? (
            <Card className="p-8 text-center">
              <Network className="mx-auto text-slate-300 mb-3" size={48} />
              <p className="text-slate-500">{t('knowledgeGraph.emptySearch')}</p>
            </Card>
          ) : (
            <div className="space-y-2">
              {searchResults.map((node) => (
                <Card key={node.id} className="p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => handleNodeClick(node)}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-900">{node.label || node.id}</p>
                      <p className="text-xs text-slate-500">{t('knowledgeGraph.type')}: {node.entity_type} · {t('knowledgeGraph.id')}: {node.entity_id}</p>
                    </div>
                    <Badge variant="secondary">{node.entity_type}</Badge>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
        <TabsContent value="detail" className="mt-4">
          {selectedNode ? (
            <div className="space-y-4">
              <Card className="p-4">
                <h3 className="font-medium text-slate-900 mb-2">{t('knowledgeGraph.selectedEntity')}</h3>
                <p className="text-sm text-slate-600">{t('knowledgeGraph.id')}: {selectedNode.id}</p>
                <p className="text-sm text-slate-600">{t('knowledgeGraph.type')}: {selectedNode.entity_type}</p>
                <p className="text-sm text-slate-600">{t('knowledgeGraph.label')}: {selectedNode.label}</p>
              </Card>
              {relationships && (
                <Card className="p-4">
                  <h3 className="font-medium text-slate-900 mb-3">
                    {t('knowledgeGraph.relationships')} ({relationships.relationships.length})
                  </h3>
                  {relationships.relationships.length === 0 ? (
                    <p className="text-sm text-slate-500">{t('knowledgeGraph.noRelationshipsFound')}</p>
                  ) : (
                    <div className="space-y-2">
                      {relationships.relationships.map((edge) => (
                        <div key={edge.id} className="flex items-center justify-between text-sm">
                          <span className="text-slate-600">{edge.relationship_type}</span>
                          <span className="text-slate-400">{edge.source_node_id} → {edge.target_node_id}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              )}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <p className="text-slate-500">{t('knowledgeGraph.selectDetail')}</p>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
