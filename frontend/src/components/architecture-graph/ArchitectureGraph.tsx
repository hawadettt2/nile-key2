import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ArchitectureNode, ArchitectureEdge } from '@/store/architectureExplorerStore';
import { GraphNode } from './GraphNode';
import { GraphEdge, markerId, RELATION_COLORS } from './GraphEdge';
import { GraphNodePosition, useGraphLayout } from './useGraphLayout';

interface ArchitectureGraphProps {
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
  onNodeClick: (nodeId: string) => void;
  selectedNodeId: string | null;
  expandedNodeId: string | null;
}

const VIEWPORT_HEIGHT = 680;
const MIN_ZOOM = 0.7;
const MAX_ZOOM = 2.5;

const LEVEL_BG: Record<number, { label: string; fill: string; border: string; accent: string }> = {
  0: { label: 'Flow Tier 0', fill: '#f8fafc', border: '#cbd5e1', accent: '#64748b' },
  1: { label: 'Flow Tier 1', fill: '#eef2ff', border: '#c7d2fe', accent: '#4f46e5' },
  2: { label: 'Flow Tier 2', fill: '#fffbeb', border: '#fde68a', accent: '#d97706' },
  3: { label: 'Flow Tier 3', fill: '#fdf4ff', border: '#e9d5ff', accent: '#9333ea' },
  4: { label: 'Flow Tier 4+', fill: '#f0fdfa', border: '#99f6e4', accent: '#0d9488' },
};

const LEGEND = [
  { label: 'Core', color: '#2563eb' },
  { label: 'Business', color: '#059669' },
  { label: 'Agent', color: '#7c3aed' },
  { label: 'External', color: '#d97706' },
  { label: 'UI / Data', color: '#0891b2' },
];

const MARKER_COLORS = Array.from(new Set(Object.values(RELATION_COLORS).concat('#d97706', '#ea580c')));

export function ArchitectureGraph({ nodes, edges, onNodeClick, selectedNodeId, expandedNodeId }: ArchitectureGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(1200);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const panStart = useRef({ x: 0, y: 0, panX: 0, panY: 0 });
  const isPanningRef = useRef(false);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const measure = () => setContainerWidth(Math.max(360, el.clientWidth || 1200));
    measure();
    if (typeof ResizeObserver === 'undefined') return;
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const { positions, width: graphWidth, height: graphHeight } = useGraphLayout(nodes, edges, containerWidth);
  const positionMap = useMemo(
    () => new Map<string, GraphNodePosition>(positions.map((position) => [position.id, position])),
    [positions]
  );
  const visibleEdges = useMemo(
    () => edges.filter((edge) => positionMap.has(edge.source) && positionMap.has(edge.target)),
    [edges, positionMap]
  );

  const fitToViewport = useCallback(() => {
    if (!graphWidth || !graphHeight) return;
    const safeWidth = Math.max(300, containerWidth - 56);
    const safeHeight = VIEWPORT_HEIGHT - 56;
    const nextZoom = Math.min(1.18, Math.max(MIN_ZOOM, Math.min(safeWidth / graphWidth, safeHeight / graphHeight)));
    const scaledWidth = graphWidth * nextZoom;
    const scaledHeight = graphHeight * nextZoom;
    setZoom(nextZoom);
    setPan({
      x: Math.max(28, (containerWidth - scaledWidth) / 2),
      y: Math.max(28, (VIEWPORT_HEIGHT - scaledHeight) / 2),
    });
  }, [containerWidth, graphHeight, graphWidth]);

  useEffect(() => {
    fitToViewport();
  }, [fitToViewport, nodes.length, edges.length]);

  const applyZoom = useCallback((nextZoom: number, center?: { x: number; y: number }) => {
    const clamped = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, nextZoom));
    if (!center) {
      setZoom(clamped);
      return;
    }
    setPan((current) => ({
      x: center.x - ((center.x - current.x) / zoom) * clamped,
      y: center.y - ((center.y - current.y) / zoom) * clamped,
    }));
    setZoom(clamped);
  }, [zoom]);

  const handleWheel = useCallback((event: React.WheelEvent<SVGSVGElement>) => {
    event.preventDefault();
    const rect = event.currentTarget.getBoundingClientRect();
    const center = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    applyZoom(zoom * (event.deltaY < 0 ? 1.1 : 0.9), center);
  }, [applyZoom, zoom]);

  const handlePointerDown = useCallback((event: React.PointerEvent<SVGSVGElement>) => {
    if (event.button !== 0) return;
    const target = event.target as Element | null;
    if (target?.closest('.graph-node, .graph-edge, button')) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    panStart.current = { x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y };
    isPanningRef.current = true;
    setIsPanning(true);
  }, [pan.x, pan.y]);

  const handlePointerMove = useCallback((event: React.PointerEvent<SVGSVGElement>) => {
    if (!isPanningRef.current) return;
    const start = panStart.current;
    setPan({ x: start.panX + (event.clientX - start.x), y: start.panY + (event.clientY - start.y) });
  }, []);

  const handlePointerEnd = useCallback((event: React.PointerEvent<SVGSVGElement>) => {
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
    isPanningRef.current = false;
    setIsPanning(false);
  }, []);

  const tierRows = useMemo(() => {
    const rows = new Map<number, { minY: number; maxY: number }>();
    positions.forEach((position) => {
      const current = rows.get(position.level);
      rows.set(position.level, {
        minY: Math.min(current?.minY ?? position.y, position.y),
        maxY: Math.max(current?.maxY ?? position.y + 82, position.y + 82),
      });
    });
    return Array.from(rows.entries()).sort(([a], [b]) => a - b);
  }, [positions]);

  return (
    <div ref={containerRef} className="relative w-full overflow-hidden rounded-xl border border-slate-200 bg-slate-100 shadow-sm" style={{ height: VIEWPORT_HEIGHT, touchAction: 'none' }}>
      <div className="pointer-events-none absolute inset-x-3 top-3 z-20 flex items-start justify-between gap-4">
        <div className="pointer-events-auto flex items-center gap-1 rounded-lg border border-slate-200 bg-white/95 p-1.5 shadow-md backdrop-blur">
          <button type="button" onClick={() => applyZoom(zoom * 1.15)} className="h-8 w-8 rounded-md text-lg font-medium text-slate-700 hover:bg-slate-100" aria-label="تكبير">+</button>
          <button type="button" onClick={() => applyZoom(zoom * 0.87)} className="h-8 w-8 rounded-md text-lg font-medium text-slate-700 hover:bg-slate-100" aria-label="تصغير">−</button>
          <button type="button" onClick={fitToViewport} className="h-8 rounded-md px-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-100" aria-label="ملاءمة الرسم">Fit</button>
          <span className="min-w-12 px-1 text-center text-[11px] tabular-nums text-slate-500">{Math.round(zoom * 100)}%</span>
        </div>

        <div className="pointer-events-auto flex max-w-[70%] flex-wrap items-center justify-end gap-x-3 gap-y-1 rounded-lg border border-slate-200 bg-white/95 px-3 py-2 text-[10px] font-medium text-slate-600 shadow-md backdrop-blur">
          {LEGEND.map((item) => (
            <span key={item.label} className="inline-flex items-center gap-1.5 whitespace-nowrap">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
              {item.label}
            </span>
          ))}
        </div>
      </div>

      <svg
        width="100%"
        height={VIEWPORT_HEIGHT}
        className={isPanning ? 'block cursor-grabbing' : 'block cursor-grab'}
        role="application"
        aria-label="Architecture graph"
        onWheel={handleWheel}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerEnd}
        onPointerCancel={handlePointerEnd}
      >
        <defs>
          <pattern id="architecture-grid" width="28" height="28" patternUnits="userSpaceOnUse">
            <path d="M 28 0 L 0 0 0 28" fill="none" stroke="#cbd5e1" strokeOpacity="0.35" strokeWidth="1" />
          </pattern>
          {MARKER_COLORS.map((color) => (
            <marker key={color} id={markerId(color)} markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
              <polygon points="0 0, 9 3.5, 0 7" fill={color} />
            </marker>
          ))}
          <filter id="architecture-shadow" x="-25%" y="-25%" width="150%" height="150%">
            <feDropShadow dx="0" dy="2" stdDeviation="2.5" floodColor="#0f172a" floodOpacity="0.12" />
          </filter>
          <filter id="architecture-shadow-selected" x="-30%" y="-30%" width="160%" height="160%">
            <feDropShadow dx="0" dy="4" stdDeviation="5" floodColor="#0f172a" floodOpacity="0.22" />
          </filter>
        </defs>

        <rect width="100%" height={VIEWPORT_HEIGHT} fill="#f8fafc" />
        <rect width="100%" height={VIEWPORT_HEIGHT} fill="url(#architecture-grid)" />

        <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
          <g className="architecture-tiers">
            {tierRows.map(([tier, row]) => {
              const cfg = LEVEL_BG[Math.min(tier, 4)];
              const bandY = row.minY - 30;
              const bandHeight = row.maxY - row.minY + 60;
              return (
                <g key={`tier-${tier}`}>
                  <rect x={0} y={bandY} width={graphWidth} height={bandHeight} rx={18} fill={cfg.fill} stroke={cfg.border} strokeWidth={1.4} />
                  <rect x={0} y={bandY} width={7} height={bandHeight} rx={3.5} fill={cfg.accent} />
                  <rect x={20} y={bandY + 14} width={132} height={22} rx={11} fill="#ffffff" fillOpacity={0.88} />
                  <text x={32} y={bandY + 29} fontSize={10.5} fill="#334155" fontWeight={750}>{cfg.label}</text>
                </g>
              );
            })}
          </g>

          <g className="edges">
            {visibleEdges.map((edge) => (
              <GraphEdge key={edge.id} edge={edge} sourcePos={positionMap.get(edge.source)} targetPos={positionMap.get(edge.target)} />
            ))}
          </g>

          <g className="nodes">
            {nodes.map((node) => {
              const position = positionMap.get(node.id);
              if (!position) return null;
              return <GraphNode key={node.id} node={node} x={position.x} y={position.y} isSelected={selectedNodeId === node.id} isExpanded={expandedNodeId === node.id} onClick={onNodeClick} />;
            })}
          </g>
        </g>
      </svg>
    </div>
  );
}
