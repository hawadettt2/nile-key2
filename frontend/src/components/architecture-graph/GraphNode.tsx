import { ArchitectureNode } from '@/store/architectureExplorerStore';

interface GraphNodeProps {
  node: ArchitectureNode;
  x: number;
  y: number;
  isSelected: boolean;
  isExpanded: boolean;
  onClick: (id: string) => void;
}

const NODE_WIDTH = 236;
const NODE_HEIGHT = 76;

const TYPE_COLORS: Record<string, string> = {
  platform: '#4f46e5', agent_subsystem: '#7c3aed', agent_component: '#9333ea', knowledge_subsystem: '#0891b2',
  memory_subsystem: '#0284c7', reasoning: '#2563eb', planning: '#0d9488', orchestration: '#d97706',
  business_service: '#059669', tool: '#ea580c', external_system: '#64748b', ui_component: '#db2777',
  data_store: '#475569', infrastructure: '#57534e',
};

const STATUS_COLORS: Record<string, string> = {
  implemented_runtime: '#059669', implemented_non_primary: '#4f46e5', conditional: '#d97706',
  planned_future: '#64748b', reserved_minimal: '#57534e', external: '#0891b2', unverified: '#dc2626', architectural_root: '#4f46e5',
};

export function GraphNode({ node, x, y, isSelected, isExpanded, onClick }: GraphNodeProps) {
  const typeColor = TYPE_COLORS[node.type] || '#64748b';
  const statusColor = STATUS_COLORS[node.status] || '#64748b';
  const typeLabel = node.type.replaceAll('_', ' ');
  const statusLabel = node.status.replaceAll('_', ' ');
  const typeWidth = Math.min(122, Math.max(58, typeLabel.length * 5.4 + 18));

  return (
    <g className="graph-node" transform={`translate(${x}, ${y})`} onClick={(event) => { event.stopPropagation(); onClick(node.id); }} style={{ cursor: 'pointer' }}>
      <rect width={NODE_WIDTH} height={NODE_HEIGHT} rx={10} fill="#fff" stroke={isSelected ? '#0f172a' : '#cbd5e1'} strokeWidth={isSelected ? 2.5 : 1} filter={isSelected ? 'url(#architecture-shadow-selected)' : 'url(#architecture-shadow)'} />
      <rect width={6} height={NODE_HEIGHT} rx={3} fill={typeColor} />
      <text x={18} y={21} fill="#0f172a" fontSize={12.5} fontWeight={700}>{node.technical_name}</text>
      <text x={18} y={38} fill="#64748b" fontSize={10.5}>{node.arabic_meaning}</text>
      <rect x={18} y={48} width={typeWidth} height={18} rx={9} fill={typeColor} fillOpacity={0.10} />
      <text x={27} y={60.5} fill={typeColor} fontSize={8.5} fontWeight={700}>{typeLabel}</text>
      <circle cx={NODE_WIDTH - 18} cy={18} r={5} fill={statusColor} />
      <text x={NODE_WIDTH - 28} y={33} textAnchor="end" fill="#64748b" fontSize={8} fontWeight={600}>{statusLabel}</text>
      {isExpanded && <text x={NODE_WIDTH - 12} y={61} textAnchor="end" fill="#059669" fontSize={8.5} fontWeight={700}>EXPANDED</text>}
    </g>
  );
}
