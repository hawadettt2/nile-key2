import { useRef, useState, useMemo, useEffect, useCallback } from 'react';
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
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const isPanning = useRef(false);
  const panStart = useRef({ x: 0, y: 0 });

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

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = -e.deltaY * 0.001;
    setTransform((prev) => {
      const newScale = Math.min(Math.max(0.3, prev.scale + delta), 2.5);
      return { ...prev, scale: newScale };
    });
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as SVGElement).closest('.graph-node, .graph-edge, button')) return;
    isPanning.current = true;
    panStart.current = { x: e.clientX - transform.x, y: e.clientY - transform.y };
  }, [transform.x, transform.y]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isPanning.current) return;
    setTransform({
      x: e.clientX - panStart.current.x,
      y: e.clientY - panStart.current.y,
      scale: transform.scale,
    });
  }, [transform.scale]);

  const handleMouseUp = useCallback(() => {
    isPanning.current = false;
  }, []);

  const zoomIn = () => setTransform((prev) => ({ ...prev, scale: Math.min(prev.scale + 0.2, 2.5) }));
  const zoomOut = () => setTransform((prev) => ({ ...prev, scale: Math.max(prev.scale - 0.2, 0.3) }));
  const resetView = () => setTransform({ x: 0, y: 0, scale: 1 });

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
        groups.set(p.level, { minY: p.y, maxY: p.y + 80, minX: p.x, maxX: p.x + 220 });
      } else {
        existing.minY = Math.min(existing.minY, p.y);
        existing.maxY = Math.max(existing.maxY, p.y + 80);
        existing.minX = Math.min(existing.minX, p.x);
        existing.maxX = Math.max(existing.maxX, p.x + 220);
      }
    });
    return groups;
  }, [positions]);

  return (
    <div
      ref={containerRef}
      className="w-full border border-slate-200 rounded-lg bg-slate-50 relative overflow-hidden"
      style={{ minHeight: height + 40 }}
    >
      <div
        className="absolute top-3 right-3 z-10 flex flex-col gap-1"
        style={{ transform: 'none' }}
      >
        <button
          type="button"
          onClick={zoomIn}
          className="bg-white border border-slate-200 rounded shadow-sm hover:bg-slate-50 text-slate-700 w-8 h-8 flex items-center justify-center text-lg"
        >
          +
        </button>
        <button
          type="button"
          onClick={zoomOut}
          className="bg-white border border-slate-200 rounded shadow-sm hover:bg-slate-50 text-slate-700 w-8 h-8 flex items-center justify-center text-lg"
        >
          -
        </button>
        <button
          type="button"
          onClick={resetView}
          className="bg-white border border-slate-200 rounded shadow-sm hover:bg-slate-50 text-slate-700 w-8 h-8 flex items-center justify-center text-xs"
        >
          {Math.round(transform.scale * 100)}%
        </button>
      </div>

      <svg
        id="architecture-graph-svg"
        width={containerWidth}
        height={Math.max(height, containerRef.current?.offsetHeight || height)}
        className="block"
        style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif', cursor: isPanning.current ? 'grabbing' : 'grab' }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
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

        <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.scale})`}>
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
        </g>
      </svg>
    </div>
  );
}
