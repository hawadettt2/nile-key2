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
    const bend = Math.min(160, Math.max(40, gap * 0.45));
    const horizontalDelta = targetX - sourceX;
    const lateral = Math.min(140, Math.max(24, Math.abs(horizontalDelta) * 0.3));
    const sign = horizontalDelta >= 0 ? 1 : -1;
    return `M ${sourceX} ${sourceY} C ${sourceX + lateral * sign} ${sourceY + bend}, ${targetX - lateral * sign} ${targetY - bend}, ${targetX} ${targetY}`;
  }

  const loop = 60 + Math.min(110, Math.abs(targetX - sourceX) * 0.18);
  return `M ${sourceX} ${sourceY} C ${sourceX} ${sourceY + loop}, ${targetX} ${targetY - loop}, ${targetX} ${targetY}`;
}

export function GraphEdge({ edge, sourcePos, targetPos }: GraphEdgeProps) {
  if (!sourcePos || !targetPos) return null;

  const isConditional = edge.status === 'conditional';
  const isStructural = edge.relation_type === 'contains' || edge.relation_type === 'contains_child' || edge.relation_type === 'parent_child';
  const strokeColor = isConditional ? '#ea580c' : RELATION_COLORS[edge.relation_type] || '#94a3b8';
  const path = buildPath(sourcePos, targetPos);

  return (
    <g className="graph-edge" data-graph-edge="true" opacity={isConditional ? 1 : isStructural ? 0.7 : 0.9}>
      <path d={path} fill="none" stroke="#ffffff" strokeOpacity="0.95" strokeWidth={isConditional ? 6 : 5} />
      <path
        d={path}
        fill="none"
        stroke={strokeColor}
        strokeWidth={isConditional ? 3.2 : isStructural ? 1.9 : 2.2}
        strokeDasharray={isConditional ? '12 6' : isStructural ? '5 5' : undefined}
        strokeLinecap="round"
        strokeLinejoin="round"
        markerEnd={`url(#${markerId(strokeColor)})`}
      />
    </g>
  );
}
