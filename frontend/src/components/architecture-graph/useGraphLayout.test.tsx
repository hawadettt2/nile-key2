import { renderHook } from '@testing-library/react';
import { useGraphLayout } from './useGraphLayout';
import type { ArchitectureNode, ArchitectureEdge } from '@/store/architectureExplorerStore';

function makeNode(id: string, type: string, rank: number): ArchitectureNode {
  return {
    id,
    technical_name: `Node ${id}`,
    arabic_meaning: `عقدة ${id}`,
    type,
    levels: [rank],
    status: 'implemented_runtime',
    paths: [],
    responsibilities: [],
    non_responsibilities: [],
    evidence: [],
    parent_ids: [],
    tags: [],
    metadata: {},
  };
}

function makeEdge(source: string, target: string): ArchitectureEdge {
  return {
    id: `${source}-${target}`,
    source,
    target,
    relation_type: 'depends_on',
    direction: 'outgoing',
    status: 'active',
    evidence: [],
    data: {},
    metadata: {},
  };
}

describe('useGraphLayout', () => {
  test('returns empty result for 0 nodes', () => {
    const { result } = renderHook(() => useGraphLayout([], [], 1200));
    expect(result.current.positions).toEqual([]);
    expect(result.current.width).toBeGreaterThanOrEqual(1);
    expect(result.current.height).toBeGreaterThanOrEqual(1);
  });

  test('positions less than 6 nodes in a single row', () => {
    const nodes = [0, 1, 2].map((i) => makeNode(`n${i}`, 'platform', 0));
    const edges: ArchitectureEdge[] = [];
    const { result } = renderHook(() => useGraphLayout(nodes, edges, 1200));

    expect(result.current.positions).toHaveLength(3);
    const ys = new Set(result.current.positions.map((p) => p.y));
    expect(ys.size).toBe(1);
    expect(result.current.height).toBeGreaterThan(0);
  });

  test('positions exactly 6 nodes without splitting', () => {
    const nodes = Array.from({ length: 6 }, (_, i) => makeNode(`n${i}`, 'platform', 0));
    const edges: ArchitectureEdge[] = [];
    const { result } = renderHook(() => useGraphLayout(nodes, edges, 1200));

    expect(result.current.positions).toHaveLength(6);
    const ys = new Set(result.current.positions.map((p) => p.y));
    expect(ys.size).toBe(1);
  });

  test('splits 7 nodes into two visual rows', () => {
    const nodes = Array.from({ length: 7 }, (_, i) => makeNode(`n${i}`, 'platform', 0));
    const edges: ArchitectureEdge[] = [];
    const { result } = renderHook(() => useGraphLayout(nodes, edges, 1200));

    expect(result.current.positions).toHaveLength(7);
    const ys = Array.from(new Set(result.current.positions.map((p) => p.y))).sort((a, b) => a - b);
    expect(ys).toHaveLength(2);
  });

  test('splits 12 nodes into two visual rows of 6', () => {
    const nodes = Array.from({ length: 12 }, (_, i) => makeNode(`n${i}`, 'platform', 0));
    const edges: ArchitectureEdge[] = [];
    const { result } = renderHook(() => useGraphLayout(nodes, edges, 1200));

    expect(result.current.positions).toHaveLength(12);
    const ys = Array.from(new Set(result.current.positions.map((p) => p.y))).sort((a, b) => a - b);
    expect(ys).toHaveLength(2);
    const firstRow = result.current.positions.filter((p) => p.y === ys[0]);
    const secondRow = result.current.positions.filter((p) => p.y === ys[1]);
    expect(firstRow).toHaveLength(6);
    expect(secondRow).toHaveLength(6);
  });

  test('splits more than 12 nodes into multiple visual rows', () => {
    const nodes = Array.from({ length: 15 }, (_, i) => makeNode(`n${i}`, 'platform', 0));
    const edges: ArchitectureEdge[] = [];
    const { result } = renderHook(() => useGraphLayout(nodes, edges, 1200));

    expect(result.current.positions).toHaveLength(15);
    const ys = Array.from(new Set(result.current.positions.map((p) => p.y))).sort((a, b) => a - b);
    expect(ys.length).toBeGreaterThanOrEqual(3);
  });

  test('does not create empty visual rows', () => {
    const nodes = Array.from({ length: 7 }, (_, i) => makeNode(`n${i}`, 'platform', 0));
    const edges: ArchitectureEdge[] = [];
    const { result } = renderHook(() => useGraphLayout(nodes, edges, 1200));

    const rowMap = new Map<number, number>();
    result.current.positions.forEach((p) => {
      rowMap.set(p.y, (rowMap.get(p.y) || 0) + 1);
    });

    for (const count of rowMap.values()) {
      expect(count).toBeGreaterThan(0);
    }
  });

  test('produces consistent height and y coordinates', () => {
    const nodes = Array.from({ length: 8 }, (_, i) => makeNode(`n${i}`, 'platform', 0));
    const edges: ArchitectureEdge[] = [];
    const { result } = renderHook(() => useGraphLayout(nodes, edges, 1200));

    expect(result.current.height).toBeGreaterThan(0);
    const maxY = Math.max(...result.current.positions.map((p) => p.y));
    expect(maxY + 82).toBeLessThanOrEqual(result.current.height + 1);
  });

  test('distributes nodes across multiple ranks into separate visual rows', () => {
    const nodes = [
      makeNode('a', 'platform', 0),
      makeNode('b', 'platform', 0),
      makeNode('c', 'platform', 1),
      makeNode('d', 'platform', 1),
      makeNode('e', 'platform', 1),
      makeNode('f', 'platform', 1),
      makeNode('g', 'platform', 1),
      makeNode('h', 'platform', 1),
      makeNode('i', 'platform', 1),
      makeNode('j', 'platform', 1),
    ];
    const edges: ArchitectureEdge[] = [];
    const { result } = renderHook(() => useGraphLayout(nodes, edges, 1200));

    expect(result.current.positions).toHaveLength(10);
    const ys = Array.from(new Set(result.current.positions.map((p) => p.y))).sort((a, b) => a - b);
    expect(ys.length).toBeGreaterThanOrEqual(2);
  });
});
