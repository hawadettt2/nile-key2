import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/services/api', () => ({
  analyzeSupplier: vi.fn(),
  detectTrends: vi.fn(),
}));

const mockUseTradeIntelligenceStore = vi.fn();
vi.mock('@/store/tradeIntelligenceStore', () => ({
  useTradeIntelligenceStore: () => mockUseTradeIntelligenceStore(),
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

import { analyzeSupplier, detectTrends } from '@/services/api';
import { TradeIntelligence } from '@/pages/TradeIntelligence';

describe('TradeIntelligence', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseTradeIntelligenceStore.mockReturnValue({
      supplierAnalysis: null,
      trends: null,
      setSupplierAnalysis: vi.fn(),
      setTrends: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
    });
    vi.mocked(analyzeSupplier).mockResolvedValue({ data: { trends: [] } } as any);
    vi.mocked(detectTrends).mockResolvedValue({ data: { trends: [{ period: '2024-01', value: 100 }] } } as any);
  });

  it('renders trade intelligence title', () => {
    render(
      <MemoryRouter>
        <TradeIntelligence />
      </MemoryRouter>
    );
    expect(screen.getByText('tradeIntelligence.title')).toBeInTheDocument();
  });

  it('calls analyzeSupplier when analyze button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <TradeIntelligence />
      </MemoryRouter>
    );

    const supplierInput = screen.getByPlaceholderText('tradeIntelligence.supplierId');
    await user.type(supplierInput, '1');

    const analyzeButton = screen.getByRole('button', { name: 'tradeIntelligence.analyze' });
    await user.click(analyzeButton);

    await waitFor(() => {
      expect(analyzeSupplier).toHaveBeenCalledWith({ supplier_id: 1, analysis_type: 'full' });
    });
  });

  it('calls detectTrends when detect trends button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <TradeIntelligence />
      </MemoryRouter>
    );

    const trendsTab = screen.getByRole('tab', { name: 'tradeIntelligence.trends' });
    await user.click(trendsTab);

    const detectButton = screen.getByRole('button', { name: 'tradeIntelligence.detectTrends' });
    await user.click(detectButton);

    await waitFor(() => {
      expect(detectTrends).toHaveBeenCalledWith({ entity_type: 'supplier', trend_parameters: {} });
    });
  });

  it('shows supplier analysis results when analysis completes', async () => {
    const user = userEvent.setup();
    const mockSetSupplierAnalysis = vi.fn();
    mockUseTradeIntelligenceStore.mockReturnValue({
      supplierAnalysis: null,
      trends: null,
      setSupplierAnalysis: mockSetSupplierAnalysis,
      setTrends: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
    });

    vi.mocked(analyzeSupplier).mockResolvedValueOnce({ data: { result: 'test' } } as any);

    render(
      <MemoryRouter>
        <TradeIntelligence />
      </MemoryRouter>
    );

    const supplierInput = screen.getByPlaceholderText('tradeIntelligence.supplierId');
    await user.type(supplierInput, '1');

    const analyzeButton = screen.getByRole('button', { name: 'tradeIntelligence.analyze' });
    await user.click(analyzeButton);

    await waitFor(() => {
      expect(mockSetSupplierAnalysis).toHaveBeenCalled();
    });
  });
});
