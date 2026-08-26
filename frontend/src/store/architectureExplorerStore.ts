import { create } from 'zustand';

export interface ArchitectureNode {
  id: string;
  technical_name: string;
  arabic_meaning: string;
  type: string;
  levels: number[];
  status: string;
  paths: string[];
  responsibilities: string[];
  non_responsibilities: string[];
  evidence: string[];
  parent_ids: string[];
  tags: string[];
  metadata: Record<string, unknown>;
}

export interface ArchitectureEdge {
  id: string;
  source: string;
  target: string;
  relation_type: string;
  direction: string;
  status: string;
  evidence: string[];
  data: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface ArchitectureMetadata {
  artifact: string;
  version: string;
  purpose: string;
  governing_principle: string;
  source: Record<string, unknown>;
  levels: Array<Record<string, unknown>>;
  next_work: string;
}

interface ArchitectureExplorerState {
  metadata: ArchitectureMetadata | null;
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
  isLoading: boolean;
  error: string | null;
  setMetadata: (metadata: ArchitectureMetadata) => void;
  setNodes: (nodes: ArchitectureNode[]) => void;
  setEdges: (edges: ArchitectureEdge[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  metadata: null,
  nodes: [],
  edges: [],
  isLoading: false,
  error: null,
};

export const useArchitectureExplorerStore = create<ArchitectureExplorerState>((set) => ({
  ...initialState,
  setMetadata: (metadata) => set({ metadata }),
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
