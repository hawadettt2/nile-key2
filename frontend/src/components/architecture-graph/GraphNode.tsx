import { ArchitectureNode } from '@/store/architectureExplorerStore';

export interface GraphNodeProps {
  node: ArchitectureNode;
  x: number;
  y: number;
  isSelected: boolean;
  isExpanded: boolean;
  onClick: (id: string) => void;
}

export const NODE_WIDTH = 236;
export const NODE_HEIGHT = 82;

const TYPE_COLORS: Record<string, string> = {
  platform: '#4f46e5',
  agent_subsystem: '#7c3aed',
  agent_component: '#9333ea',
  knowledge_subsystem: '#0891b2',
  memory_subsystem: '#0284c7',
  reasoning: '#2563eb',
  planning: '#0d9488',
  orchestration: '#d97706',
  business_service: '#059669',
  tool: '#ea580c',
  external_system: '#64748b',
  ui_component: '#db2777',
  data_store: '#475569',
  infrastructure: '#57534e',
};

const STATUS_COLORS: Record<string, string> = {
  implemented_runtime: '#059669',
  implemented_non_primary: '#4f46e5',
  conditional: '#d97706',
  planned_future: '#64748b',
  reserved_minimal: '#57534e',
  external: '#0891b2',
  unverified: '#dc2626',
  architectural_root: '#4f46e5',
};

function humanize(value: string): string {
  return value.replace(/_/g, ' ');
}

function truncate(value: string, max: number): string {
  return value.length > max ? `${value.slice(0, max - 1)}…` : value;
}

export function GraphNode({ node, x, y, isSelected, isExpanded, onClick }: GraphNodeProps) {
  const typeColor = TYPE_COLORS[node.type] || '#64748b';
  const statusColor = STATUS_COLORS[node.status] || '#64748b';
  const typeLabel = truncate(humanize(node.type), 22);
  const statusLabel = truncate(humanize(node.status), 20);
  const isPrimary = node.type === 'platform' || node.status === 'architectural_root';

  return (
    <g
      className="graph-node"
      data-graph-node="true"
      transform={`translate(${x}, ${y})`}
      onClick={(event) => {
        event.stopPropagation();
        onClick(node.id);
      }}
      style={{ cursor: 'pointer' }}
      role="button"
      aria-label={`${node.technical_name} — ${node.arabic_meaning}`}
    >
      <rect width={NODE_WIDTH} height={NODE_HEIGHT} rx={12} fill={isPrimary ? '#ffffff' : '#fbfdff'} stroke={isSelected ? '#0f172a' : isPrimary ? typeColor : '#cbd5e1'} strokeWidth={isSelected ? 2.7 : isPrimary ? 1.8 : 1.15} filter={isSelected ? 'url(#architecture-shadow-selected)' : 'url(#architecture-shadow)'} />
      <rect width={7} height={NODE_HEIGHT} rx={3.5} fill={typeColor} />
      <text x={18} y={20} fill="#0f172a" fontSize={13} fontWeight={750}>{truncate(node.technical_name, 33)}</text>
      <text x={18} y={37} fill="#64748b" fontSize={10.5}>{truncate(node.arabic_meaning, 40)}</text>
      <rect x={18} y={48} width={Math.min(124, Math.max(62, typeLabel.length * 5.2 + 18))} height={19} rx={9.5} fill={typeColor} fillOpacity={0.10} />
      <text x={27} y={61.5} fill={typeColor} fontSize={8.5} fontWeight={700}>{typeLabel}</text>
      <circle cx={NODE_WIDTH - 18} cy={15} r={5} fill={statusColor} />
      <text x={NODE_WIDTH - 28} y={30} textAnchor="end" fill="#64748b" fontSize={8.1} fontWeight={650}>{statusLabel}</text>
      {isExpanded && <text x={NODE_WIDTH - 14} y={62} textAnchor="end" fill="#059669" fontSize={8.2} fontWeight={750}>EXPANDED</text>}
    </g>
  );
}
