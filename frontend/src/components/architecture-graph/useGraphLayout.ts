import { useMemo } from 'react';
import { ArchitectureNode, ArchitectureEdge } from '@/store/architectureExplorerStore';
import { NODE_HEIGHT, NODE_WIDTH } from './GraphNode';

export interface GraphNodePosition {
  id: string;
  x: number;
  y: number;
  level: number;
}

export interface GraphLayoutResult {
  positions: GraphNodePosition[];
  width: number;
  height: number;
}

const HORIZONTAL_GAP = 46;
const VERTICAL_GAP = 92;
const SIDE_PADDING = 64;
const TOP_PADDING = 54;
const MAX_REORDER_PASSES = 4;

const TYPE_PRIORITY: Record<string, number> = {
  platform: 0,
  agent_subsystem: 1,
  reasoning: 2,
  planning: 3,
  orchestration: 4,
  business_service: 5,
  knowledge_subsystem: 6,
  memory_subsystem: 7,
  tool: 8,
  external_system: 9,
  ui_component: 10,
  data_store: 11,
  infrastructure: 12,
};

export function useGraphLayout(
  nodes: ArchitectureNode[],
  edges: ArchitectureEdge[],
  containerWidth: number = 1200
): GraphLayoutResult {
  return useMemo(() => {
    if (!nodes.length) return { positions: [], width: Math.max(containerWidth, 1), height: 1 };

    const nodeMap = new Map(nodes.map((node) => [node.id, node]));
    const outgoing = new Map<string, string[]>();
    const incoming = new Map<string, string[]>();
    nodes.forEach((node) => {
      outgoing.set(node.id, []);
      incoming.set(node.id, []);
    });

    edges.forEach((edge) => {
      if (!nodeMap.has(edge.source) || !nodeMap.has(edge.target) || edge.source === edge.target) return;
      outgoing.get(edge.source)!.push(edge.target);
      incoming.get(edge.target)!.push(edge.source);
    });

    const ranks = new Map<string, number>();
    const indegree = new Map<string, number>();
    nodes.forEach((node) => indegree.set(node.id, incoming.get(node.id)?.length || 0));

    const queue: string[] = nodes.filter((node) => (indegree.get(node.id) || 0) === 0).map((node) => node.id);
    queue.sort((a, b) => (TYPE_PRIORITY[nodeMap.get(a)!.type] ?? 99) - (TYPE_PRIORITY[nodeMap.get(b)!.type] ?? 99));
    queue.forEach((id) => ranks.set(id, 0));

    for (let cursor = 0; cursor < queue.length; cursor += 1) {
      const id = queue[cursor];
      const rank = ranks.get(id) || 0;
      for (const child of outgoing.get(id) || []) {
        ranks.set(child, Math.max(ranks.get(child) ?? 0, rank + 1));
        indegree.set(child, (indegree.get(child) || 0) - 1);
        if (indegree.get(child) === 0) queue.push(child);
      }
    }

    nodes.forEach((node) => {
      if (!ranks.has(node.id)) {
        const declared = node.levels.length ? Math.min(...node.levels) : 0;
        ranks.set(node.id, Math.max(0, declared));
      }
    });

    const rankBuckets = new Map<number, string[]>();
    nodes.forEach((node) => {
      const rank = ranks.get(node.id) || 0;
      const bucket = rankBuckets.get(rank) || [];
      bucket.push(node.id);
      rankBuckets.set(rank, bucket);
    });

    for (const ids of rankBuckets.values()) {
      ids.sort((a, b) => {
        const aNode = nodeMap.get(a)!;
        const bNode = nodeMap.get(b)!;
        const typeDiff = (TYPE_PRIORITY[aNode.type] ?? 99) - (TYPE_PRIORITY[bNode.type] ?? 99);
        if (typeDiff !== 0) return typeDiff;
        const degreeDiff = (outgoing.get(b)?.length || 0) - (outgoing.get(a)?.length || 0);
        return degreeDiff || aNode.technical_name.localeCompare(bNode.technical_name);
      });
    }

    const rankIndex = new Map<string, number>();
    for (const ids of rankBuckets.values()) ids.forEach((id, index) => rankIndex.set(id, index));

    for (let pass = 0; pass < MAX_REORDER_PASSES; pass += 1) {
      for (const rank of Array.from(rankBuckets.keys()).sort((a, b) => a - b)) {
        const ids = rankBuckets.get(rank)!;
        ids.sort((a, b) => {
          const aNeighbors = (incoming.get(a) || []).concat(outgoing.get(a) || []);
          const bNeighbors = (incoming.get(b) || []).concat(outgoing.get(b) || []);
          const aScore = aNeighbors.length ? aNeighbors.reduce((sum, id) => sum + (rankIndex.get(id) ?? 0), 0) / aNeighbors.length : rankIndex.get(a) ?? 0;
          const bScore = bNeighbors.length ? bNeighbors.reduce((sum, id) => sum + (rankIndex.get(id) ?? 0), 0) / bNeighbors.length : rankIndex.get(b) ?? 0;
          if (Math.abs(aScore - bScore) > 0.01) return aScore - bScore;
          return (TYPE_PRIORITY[nodeMap.get(a)!.type] ?? 99) - (TYPE_PRIORITY[nodeMap.get(b)!.type] ?? 99);
        });
        ids.forEach((id, index) => rankIndex.set(id, index));
      }
    }

    const maxRank = Math.max(...rankBuckets.keys());
    const maxNodesInRank = Math.max(...Array.from(rankBuckets.values()).map((ids) => ids.length));
    const rowWidth = maxNodesInRank * NODE_WIDTH + Math.max(0, maxNodesInRank - 1) * HORIZONTAL_GAP;
    const width = Math.max(containerWidth, rowWidth + SIDE_PADDING * 2);
    const height = TOP_PADDING * 2 + (maxRank + 1) * NODE_HEIGHT + maxRank * VERTICAL_GAP;

    const positions: GraphNodePosition[] = [];
    for (const [rank, ids] of Array.from(rankBuckets.entries()).sort(([a], [b]) => a - b)) {
      const thisRowWidth = ids.length * NODE_WIDTH + Math.max(0, ids.length - 1) * HORIZONTAL_GAP;
      const startX = Math.max(SIDE_PADDING, (width - thisRowWidth) / 2);
      const y = TOP_PADDING + rank * (NODE_HEIGHT + VERTICAL_GAP);
      ids.forEach((id, index) => positions.push({ id, x: startX + index * (NODE_WIDTH + HORIZONTAL_GAP), y, level: rank }));
    }

    return { positions, width, height };
  }, [nodes, edges, containerWidth]);
}
