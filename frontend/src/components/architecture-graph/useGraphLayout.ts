import { useMemo } from 'react';
import { ArchitectureNode, ArchitectureEdge } from '@/store/architectureExplorerStore';

export interface GraphNodePosition {
  id: string;
  x: number;
  y: number;
  level: number;
}

const LEVEL_HEIGHT = 170;
const NODE_WIDTH = 220;
const HORIZONTAL_SPACING = 300;

export function useGraphLayout(
  nodes: ArchitectureNode[],
  edges: ArchitectureEdge[],
  containerWidth: number = 1200
): GraphNodePosition[] {
  return useMemo(() => {
    if (!nodes.length) return [];

    const nodeMap = new Map<string, ArchitectureNode>();
    const childrenMap = new Map<string, string[]>();
    const parentCountMap = new Map<string, number>();

    nodes.forEach((node) => nodeMap.set(node.id, node));

    edges.forEach((edge) => {
      if (!childrenMap.has(edge.source)) {
        childrenMap.set(edge.source, []);
      }
      childrenMap.get(edge.source)!.push(edge.target);
      parentCountMap.set(edge.target, (parentCountMap.get(edge.target) || 0) + 1);
    });

    const roots = nodes.filter((n) => !parentCountMap.get(n.id) || parentCountMap.get(n.id) === 0);
    const placed = new Map<string, GraphNodePosition>();

    const placeNode = (nodeId: string, x: number, y: number, level: number) => {
      placed.set(nodeId, { id: nodeId, x: Math.max(20, x), y, level });

      const children = childrenMap.get(nodeId) || [];
      const visibleChildren = children.filter((cid) => nodeMap.has(cid) && !placed.has(cid));
      if (visibleChildren.length === 0) return;

      const sortedChildren = visibleChildren.slice().sort((a, b) => {
        const aChildren = childrenMap.get(a)?.length || 0;
        const bChildren = childrenMap.get(b)?.length || 0;
        return bChildren - aChildren;
      });

      const totalChildWidth = (sortedChildren.length - 1) * HORIZONTAL_SPACING;
      let startX = x + NODE_WIDTH / 2 - totalChildWidth / 2;
      const childY = y + LEVEL_HEIGHT;

      sortedChildren.forEach((childId, index) => {
        placeNode(childId, startX + index * HORIZONTAL_SPACING, childY, level + 1);
      });
    };

    const totalRootsWidth = (roots.length - 1) * HORIZONTAL_SPACING;
    let rootStartX = containerWidth / 2 - totalRootsWidth / 2;
    if (rootStartX < 40) rootStartX = 40;

    roots.forEach((root, index) => {
      placeNode(root.id, rootStartX + index * HORIZONTAL_SPACING, 40, 0);
    });

    const orphanNodes = nodes.filter((n) => !placed.has(n.id));
    let currentY = 40;
    let currentX = 40;

    orphanNodes.forEach((node) => {
      placeNode(node.id, currentX, currentY, 0);
      currentX += HORIZONTAL_SPACING;
      if (currentX + NODE_WIDTH > containerWidth) {
        currentX = 40;
        currentY += LEVEL_HEIGHT;
      }
    });

    return Array.from(placed.values());
  }, [nodes, edges, containerWidth]);
}
