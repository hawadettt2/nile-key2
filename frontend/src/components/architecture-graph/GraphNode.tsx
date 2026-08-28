import { ArchitectureNode } from '@/store/architectureExplorerStore';

interface GraphNodeProps {
  node: ArchitectureNode;
  x: number;
  y: number;
  isSelected: boolean;
  isExpanded: boolean;
  onClick: (id: string) => void;
}

const TYPE_COLORS: Record<string, string> = {
  platform: '#6366f1',
  agent_subsystem: '#8b5cf6',
  agent_component: '#a855f7',
  knowledge_subsystem: '#06b6d4',
  memory_subsystem: '#0ea5e9',
  reasoning: '#3b82f6',
  planning: '#14b8a6',
  orchestration: '#f59e0b',
  business_service: '#10b981',
  tool: '#f97316',
  external_system: '#94a3b8',
  ui_component: '#ec4899',
  data_store: '#64748b',
  infrastructure: '#78716c',
};

const STATUS_COLORS: Record<string, string> = {
  implemented_runtime: '#10b981',
  implemented_non_primary: '#6366f1',
  conditional: '#f59e0b',
  planned_future: '#94a3b8',
  reserved_minimal: '#78716c',
  external: '#06b6d4',
  unverified: '#ef4444',
  architectural_root: '#6366f1',
};

export function GraphNode({ node, x, y, isSelected, isExpanded, onClick }: GraphNodeProps) {
  const borderColor = TYPE_COLORS[node.type] || '#94a3b8';
  const statusColor = STATUS_COLORS[node.status] || '#94a3b8';

  return (
    <g
      transform={`translate(${x}, ${y})`}
      onClick={() => onClick(node.id)}
      style={{ cursor: 'pointer' }}
    >
      <rect
        width={220}
        height={64}
        rx={8}
        ry={8}
        fill="white"
        stroke={isSelected ? '#0f172a' : borderColor}
        strokeWidth={isSelected ? 3 : 1.5}
        filter={isSelected ? 'url(#shadow-selected)' : 'url(#shadow)'}
      />
      <rect
        x={0}
        y={0}
        width={6}
        height={64}
        rx={3}
        fill={borderColor}
      />
      <text x={12} y={20} className="text-sm font-semibold" fill="#0f172a" fontSize={13}>
        {node.technical_name}
      </text>
      <text x={12} y={35} className="text-xs" fill="#64748b" fontSize={11}>
        {node.arabic_meaning}
      </text>
      <circle cx={205} cy={13} r={5} fill={statusColor} />
      <text x={213} y={17} className="text-[10px]" fill="#64748b" fontSize={9}>
        {node.status}
      </text>
      {isExpanded && (
        <text x={12} y={53} className="text-[10px]" fill="#10b981" fontSize={10}>
          ● Expanded
        </text>
      )}
    </g>
  );
}
