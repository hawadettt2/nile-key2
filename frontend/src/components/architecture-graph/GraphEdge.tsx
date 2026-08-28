import { ArchitectureEdge } from '@/store/architectureExplorerStore';
import { GraphNodePosition } from './useGraphLayout';

interface GraphEdgeProps {
  edge: ArchitectureEdge;
  sourcePos: GraphNodePosition | undefined;
  targetPos: GraphNodePosition | undefined;
}

const RELATION_COLORS: Record<string, string> = {
  contains: '#10b981',
  contains_child: '#10b981',
  parent_child: '#6366f1',
  calls: '#f59e0b',
  uses: '#8b5cf6',
  depends_on: '#ef4444',
  data_flow: '#3b82f6',
  control_flow: '#f97316',
  implements: '#14b8a6',
  extends: '#64748b',
};

export function GraphEdge({ edge, sourcePos, targetPos }: GraphEdgeProps) {
  if (!sourcePos || !targetPos) return null;

  const sourceX = sourcePos.x + 110;
  const sourceY = sourcePos.y + 32;
  const targetX = targetPos.x + 110;
  const targetY = targetPos.y;

  const isConditional = edge.status === 'conditional';
  const isReverse = sourceY > targetY;

  let path: string;
  if (isReverse) {
    const midY = targetY + (sourceY - targetY) / 2;
    path = `M ${sourceX} ${sourceY} C ${sourceX} ${midY}, ${targetX} ${midY}, ${targetX} ${targetY}`;
  } else {
    const dx = targetX - sourceX;
    const offset = Math.min(Math.abs(dx) * 0.45, 80);
    const cp1x = sourceX + offset;
    const cp1y = sourceY;
    const cp2x = targetX - offset;
    const cp2y = targetY;
    path = `M ${sourceX} ${sourceY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${targetX} ${targetY}`;
  }

  const strokeColor = isConditional ? '#f59e0b' : RELATION_COLORS[edge.relation_type] || '#94a3b8';

  return (
    <g className="graph-edge">
      <path
        d={path}
        fill="none"
        stroke={strokeColor}
        strokeWidth={isConditional ? 2.2 : 1.8}
        strokeDasharray={isConditional ? '8,5' : 'none'}
        opacity={isConditional ? 0.9 : 0.75}
        markerEnd="url(#architecture-arrow)"
      />
      {!isConditional && (
        <circle cx={targetX} cy={targetY - 16} r={3} fill={strokeColor} opacity={0.8} />
      )}
    </g>
  );
}
