import { useRef, useState, useMemo, useEffect } from 'react';
import { ArchitectureNode, ArchitectureEdge } from '@/store/architectureExplorerStore';
import { GraphNode } from './GraphNode';
import { GraphEdge } from './GraphEdge';
import { useGraphLayout, GraphNodePosition } from './useGraphLayout';

interface ArchitectureGraphProps {
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
  onNodeClick: (nodeId: string) => void;
  selectedNodeId: string | null;
  expandedNodeId: string | null;
}

const LEVEL_BG: Record<number, { label: string; color: string; border: string }> = {
  0: { label: 'L0 - DEM Universe', color: '#ecfdf5', border: '#a7f3d0' },
  1: { label: 'L1 - Operating Platform', color: '#eef2ff', border: '#c7d2fe' },
  2: { label: 'L2 - Subsystem Architecture', color: '#fffbeb', border: '#fde68a' },
  3: { label: 'L3 - Code Architecture', color: '#fdf4ff', border: '#e9d5ff' },
};

export function ArchitectureGraph({
  nodes,
  edges,
  onNodeClick,
  selectedNodeId,
  expandedNodeId,
}: ArchitectureGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(1200);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const measure = () => setContainerWidth(el.offsetWidth || 1200);
    measure();

    if (typeof ResizeObserver !== 'undefined') {
      const ro = new ResizeObserver(measure);
      ro.observe(el);
      return () => ro.disconnect();
    }
  }, []);

  const positions = useGraphLayout(nodes, edges, containerWidth);
  const positionMap = useMemo(() => {
    const map = new Map<string, GraphNodePosition>();
    positions.forEach((p) => map.set(p.id, p));
    return map;
  }, [positions]);

  const height = useMemo(() => {
    if (positions.length === 0) return 520;
    return Math.max(520, Math.max(...positions.map((p) => p.y + 160)) + 60);
  }, [positions]);

  const visibleEdges = useMemo(() => {
    return edges.filter((e) => positionMap.has(e.source) && positionMap.has(e.target));
  }, [edges, positionMap]);

  const levelGroups = useMemo(() => {
    const groups = new Map<number, { minY: number; maxY: number; minX: number; maxX: number }>();
    positions.forEach((p) => {
      const existing = groups.get(p.level);
      if (!existing) {
        groups.set(p.level, { minY: p.y, maxY: p.y + 80, minX: p.x, maxX: p.x + 240 });
      } else {
        existing.minY = Math.min(existing.minY, p.y);
        existing.maxY = Math.max(existing.maxY, p.y + 80);
        existing.minX = Math.min(existing.minX, p.x);
        existing.maxX = Math.max(existing.maxX, p.x + 240);
      }
    });
    return groups;
  }, [positions]);

  return (
    <div
      ref={containerRef}
      className="w-full border border-slate-200 rounded-lg bg-slate-50"
      style={{ minHeight: height + 40 }}
    >
      <svg
        id="architecture-graph-svg"
        width={containerWidth}
        height={height}
        className="block"
        style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif' }}
      >
        <defs>
          <marker
            id="architecture-arrow"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
          </marker>
          <filter id="architecture-shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="1" stdDeviation="2" floodOpacity="0.08" />
          </filter>
          <filter id="architecture-shadow-selected" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="3" stdDeviation="5" floodOpacity="0.18" />
          </filter>
        </defs>

        <g className="layers">
          {Array.from(levelGroups.entries()).map(([level, bounds]) => {
            const cfg = LEVEL_BG[level];
            if (!cfg) return null;
            return (
              <g key={`layer-${level}`}>
                <rect
                  x={Math.max(0, bounds.minX - 24)}
                  y={bounds.minY - 40}
                  width={Math.max(10, bounds.maxX - bounds.minX + 48)}
                  height={Math.max(10, bounds.maxY - bounds.minY + 56)}
                  rx={10}
                  fill={cfg.color}
                  stroke={cfg.border}
                  strokeWidth={1}
                />
                <text x={bounds.minX - 8} y={bounds.minY - 22} fontSize={11} fill="#475569" fontWeight={600}>
                  {cfg.label}
                </text>
              </g>
            );
          })}
        </g>

        <g className="edges">
          {visibleEdges.map((edge) => {
            const sourcePos = positionMap.get(edge.source);
            const targetPos = positionMap.get(edge.target);
            return (
              <GraphEdge
                key={edge.id}
                edge={edge}
                sourcePos={sourcePos}
                targetPos={targetPos}
              />
            );
          })}
        </g>

        <g className="nodes">
          {nodes.map((node) => {
            const pos = positionMap.get(node.id);
            if (!pos) return null;
            return (
              <GraphNode
                key={node.id}
                node={node}
                x={pos.x}
                y={pos.y}
                isSelected={selectedNodeId === node.id}
                isExpanded={expandedNodeId === node.id}
                onClick={onNodeClick}
              />
            );
          })}
        </g>
      </svg>
    </div>
  );
}
