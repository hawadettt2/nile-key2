import { ArchitectureEdge } from '@/store/architectureExplorerStore';
import { GraphNodePosition } from './useGraphLayout';
import { NODE_HEIGHT, NODE_WIDTH } from './GraphNode';

interface GraphEdgeProps {
  edge: ArchitectureEdge;
  sourcePos: GraphNodePosition | undefined;
  targetPos: GraphNodePosition | undefined;
}

export const RELATION_COLORS: Record<string, string> = {
  contains: '#059669',
  contains_child: '#059669',
  parent_child: '#4f46e5',
  calls: '#d97706',
  uses: '#7c3aed',
  depends_on: '#dc2626',
  data_flow: '#2563eb',
  control_flow: '#ea580c',
  implements: '#0d9488',
  extends: '#64748b',
};

export function markerId(color: string): string {
  return `architecture-arrow-${color.replace('#', '')}`;
}

function buildPath(source: GraphNodePosition, target: GraphNodePosition): string {
  const sourceX = source.x + NODE_WIDTH / 2;
  const sourceY = source.y + NODE_HEIGHT;
  const targetX = target.x + NODE_WIDTH / 2;
  const targetY = target.y;

  if (targetY >= sourceY) {
    const gap = targetY - sourceY;
    const bend = Math.min(120, Math.max(34, gap * 0.42));
    const horizontalDelta = targetX - sourceX;
    const lateral = Math.min(90, Math.max(18, Math.abs(horizontalDelta) * 0.22));
    const sign = horizontalDelta >= 0 ? 1 : -1;
    return `M ${sourceX} ${sourceY} C ${sourceX + lateral * sign} ${sourceY + bend}, ${targetX - lateral * sign} ${targetY - bend}, ${targetX} ${targetY}`;
  }

  const loop = 54 + Math.min(90, Math.abs(targetX - sourceX) * 0.14);
  return `M ${sourceX} ${sourceY} C ${sourceX} ${sourceY + loop}, ${targetX} ${targetY - loop}, ${targetX} ${targetY}`;
}

export function GraphEdge({ edge, sourcePos, targetPos }: GraphEdgeProps) {
  if (!sourcePos || !targetPos) return null;

  const isConditional = edge.status === 'conditional';
  const isStructural = edge.relation_type === 'contains' || edge.relation_type === 'contains_child' || edge.relation_type === 'parent_child';
  const strokeColor = isConditional ? '#d97706' : RELATION_COLORS[edge.relation_type] || '#94a3b8';
  const path = buildPath(sourcePos, targetPos);

  return (
    <g className="graph-edge" data-graph-edge="true" opacity={isConditional ? 0.96 : isStructural ? 0.68 : 0.86}>
      <path d={path} fill="none" stroke="#ffffff" strokeOpacity="0.94" strokeWidth={isConditional ? 5 : 4.5} />
      <path
        d={path}
        fill="none"
        stroke={strokeColor}
        strokeWidth={isConditional ? 2.5 : isStructural ? 1.8 : 2.1}
        strokeDasharray={isConditional ? '8 5' : isStructural ? '5 5' : undefined}
        strokeLinecap="round"
        strokeLinejoin="round"
        markerEnd={`url(#${markerId(strokeColor)})`}
      />
    </g>
  );
}
