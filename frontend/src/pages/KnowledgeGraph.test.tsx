import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/services/api', () => ({
  searchGraph: vi.fn(),
  getGraphNode: vi.fn(),
  getGraphRelationships: vi.fn(),
}));

const mockUseKnowledgeGraphStore = vi.fn();
vi.mock('@/store/knowledgeGraphStore', () => ({
  useKnowledgeGraphStore: () => mockUseKnowledgeGraphStore(),
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

import { searchGraph, getGraphNode, getGraphRelationships } from '@/services/api';
import { KnowledgeGraph } from '@/pages/KnowledgeGraph';

const mockSearchResults = [
  { id: 'node-1', entity_type: 'supplier', entity_id: 1, label: 'Supplier A' },
];

const mockNodeDetail = {
  id: 'node-1',
  entity_type: 'supplier',
  entity_id: 1,
  label: 'Supplier A',
  properties: {},
};

const mockRelationships = {
  node: mockNodeDetail,
  relationships: [
    { id: 'edge-1', source_node_id: 'node-1', target_node_id: 'node-2', relationship_type: 'SUPPLIES' },
  ],
};

describe('KnowledgeGraph', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseKnowledgeGraphStore.mockReturnValue({
      searchResults: [],
      selectedNode: null,
      relationships: null,
      isLoading: false,
      setSearchResults: vi.fn(),
      setSelectedNode: vi.fn(),
      setRelationships: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
    });
    vi.mocked(searchGraph).mockResolvedValue({ data: mockSearchResults } as any);
    vi.mocked(getGraphNode).mockResolvedValue({ data: mockNodeDetail } as any);
    vi.mocked(getGraphRelationships).mockResolvedValue({ data: mockRelationships } as any);
  });

  it('renders knowledge explorer title', () => {
    render(
      <MemoryRouter>
        <KnowledgeGraph />
      </MemoryRouter>
    );
    expect(screen.getByText('knowledgeGraph.title')).toBeInTheDocument();
  });

  it('calls searchGraph when search button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <KnowledgeGraph />
      </MemoryRouter>
    );

    const searchInput = screen.getByPlaceholderText('knowledgeGraph.searchPlaceholder');
    await user.type(searchInput, 'supplier');

    const searchButton = screen.getByRole('button', { name: 'common.search' });
    await user.click(searchButton);

    await waitFor(() => {
      expect(searchGraph).toHaveBeenCalledWith('supplier', undefined);
    });
  });

  it('loads node details when a search result is clicked', async () => {
    const user = userEvent.setup();
    const mockSetSearchResults = vi.fn();
    const mockSetSelectedNode = vi.fn();
    const mockSetRelationships = vi.fn();

    mockUseKnowledgeGraphStore.mockReturnValue({
      searchResults: mockSearchResults,
      selectedNode: null,
      relationships: null,
      isLoading: false,
      setSearchResults: mockSetSearchResults,
      setSelectedNode: mockSetSelectedNode,
      setRelationships: mockSetRelationships,
      setLoading: vi.fn(),
      setError: vi.fn(),
    });

    render(
      <MemoryRouter>
        <KnowledgeGraph />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Supplier A')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Supplier A'));

    await waitFor(() => {
      expect(getGraphNode).toHaveBeenCalledWith('supplier', 1);
      expect(getGraphRelationships).toHaveBeenCalledWith('supplier', 1);
    });
  });

  it('shows empty state when no search results', async () => {
    vi.mocked(searchGraph).mockResolvedValueOnce({ data: [] } as any);
    render(
      <MemoryRouter>
        <KnowledgeGraph />
      </MemoryRouter>
    );

    const searchInput = screen.getByPlaceholderText('knowledgeGraph.searchPlaceholder');
    await userEvent.type(searchInput, 'supplier');

    const searchButton = screen.getByRole('button', { name: 'common.search' });
    await userEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('knowledgeGraph.emptySearch')).toBeInTheDocument();
    });
  });
});
