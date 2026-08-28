import { ArchitectureEdge } from '@/store/architectureExplorerStore';
import { GraphNodePosition } from './useGraphLayout';

interface GraphEdgeProps {
  edge: ArchitectureEdge;
  sourcePos: GraphNodePosition | undefined;
  targetPos: GraphNodePosition | undefined;
}

const RELATION_COLORS: Record<string, string> = {
  contains: '#059669', contains_child: '#059669', parent_child: '#4f46e5', calls: '#d97706', uses: '#7c3aed',
  depends_on: '#dc2626', data_flow: '#2563eb', control_flow: '#ea580c', implements: '#0d9488', extends: '#64748b',
};

const NODE_WIDTH = 236;
const NODE_HEIGHT = 76;

function markerId(color: string) { return `architecture-arrow-${color.replace('#', '')}`; }

export function GraphEdge({ edge, sourcePos, targetPos }: GraphEdgeProps) {
  if (!sourcePos || !targetPos) return null;
  const sourceX = sourcePos.x + NODE_WIDTH / 2;
  const sourceY = sourcePos.y + NODE_HEIGHT;
  const targetX = targetPos.x + NODE_WIDTH / 2;
  const targetY = targetPos.y;
  const isConditional = edge.status === 'conditional';
  const strokeColor = isConditional ? '#d97706' : RELATION_COLORS[edge.relation_type] || '#94a3b8';
  const isReverse = sourceY > targetY;
  const bend = Math.min(110, Math.max(40, Math.abs(targetY - sourceY) * 0.42));
  const path = isReverse
    ? `M ${sourceX} ${sourceY} C ${sourceX} ${sourceY + 60}, ${targetX} ${targetY - 60}, ${targetX} ${targetY}`
    : `M ${sourceX} ${sourceY} C ${sourceX} ${sourceY + bend}, ${targetX} ${targetY - bend}, ${targetX} ${targetY}`;

  return (
    <g className="graph-edge" opacity={isConditional ? 0.95 : 0.82}>
      <path d={path} fill="none" stroke={strokeColor} strokeWidth={isConditional ? 2.4 : 1.8} strokeDasharray={isConditional ? '8 5' : undefined} strokeLinecap="round" markerEnd={`url(#${markerId(strokeColor)})`} />
    </g>
  );
}

export { NODE_WIDTH, NODE_HEIGHT, RELATION_COLORS, markerId };
