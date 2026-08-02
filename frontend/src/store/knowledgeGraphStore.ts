import { create } from 'zustand';

export interface GraphNode {
  id: string;
  entity_type: string;
  entity_id: number;
  label?: string;
  properties?: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relationship_type: string;
  properties?: Record<string, unknown>;
}

export interface KnowledgeGraphState {
  searchResults: GraphNode[];
  selectedNode: GraphNode | null;
  relationships: { node: GraphNode; relationships: GraphEdge[] } | null;
  traversalResult: { nodes: GraphNode[]; edges: GraphEdge[] } | null;
  isLoading: boolean;
  error: string | null;
  setSearchResults: (results: GraphNode[]) => void;
  setSelectedNode: (node: GraphNode | null) => void;
  setRelationships: (data: { node: GraphNode; relationships: GraphEdge[] } | null) => void;
  setTraversalResult: (result: { nodes: GraphNode[]; edges: GraphEdge[] } | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  searchResults: [],
  selectedNode: null,
  relationships: null,
  traversalResult: null,
  isLoading: false,
  error: null,
};

export const useKnowledgeGraphStore = create<KnowledgeGraphState>((set) => ({
  ...initialState,
  setSearchResults: (searchResults) => set({ searchResults }),
  setSelectedNode: (selectedNode) => set({ selectedNode }),
  setRelationships: (relationships) => set({ relationships }),
  setTraversalResult: (traversalResult) => set({ traversalResult }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
