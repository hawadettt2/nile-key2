import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/services/exportReadiness', () => ({
  analyzeExportReadiness: vi.fn(),
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

import { analyzeExportReadiness } from '@/services/exportReadiness';
import { ExportReadiness } from '@/pages/ExportReadiness';

const mockReport = {
  report_id: 'export-readiness-1-20260820131128',
  product: { product_id: 1, hs_code: '080510', name: 'Oranges' },
  target_market: 'DE',
  sections: [
    {
      title: 'Regulatory Requirements',
      source: 'moaah, zatca',
      confidence: 0.85,
      data: { results: [{ content: 'MRL: 0.05 ppm', confidence: 0.85, source_id: 'moaah' }] },
      availability: 'available',
      notes: null,
    },
    {
      title: 'Market Access Conditions',
      source: 'moaah, zatca, tradedata',
      confidence: 0.85,
      data: { results: [{ content: 'MRL: 0.05 ppm', confidence: 0.85, source_id: 'moaah' }] },
      availability: 'available',
      notes: null,
    },
    {
      title: 'Logistics Profile',
      source: 'World Bank LPI',
      confidence: null,
      data: null,
      availability: 'not_available',
      notes: 'No logistics data returned for DE from World Bank LPI.',
    },
    {
      title: 'Historical Trade Context',
      source: 'un-comtrade, tradedata',
      confidence: 0.85,
      data: { results: [{ content: 'MRL: 0.05 ppm', confidence: 0.85, source_id: 'moaah' }] },
      availability: 'available',
      notes: null,
    },
  ],
  action_checklist: [
    'Review regulatory requirements from the selected providers.',
    'Check tariff rates and market access conditions.',
    'Validate logistics options and shipping costs with carriers.',
    'Review historical trade patterns for this product-market pair.',
    'Prepare required documentation for export compliance.',
    'Confirm commercial and financial terms with the buyer.',
  ],
  recommendation: 'Test recommendation',
  data_quality_note: 'Unavailable sections: Logistics Profile. Manual verification required.',
  generated_at: '2026-08-20T13:11:28Z',
};

describe('ExportReadiness', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(analyzeExportReadiness).mockResolvedValue({ data: mockReport } as any);
  });

  it('renders export readiness title', () => {
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );
    expect(screen.getByText('exportReadiness.title')).toBeInTheDocument();
  });

  it('renders input fields for product and market', () => {
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );
    expect(screen.getByLabelText('exportReadiness.productId')).toBeInTheDocument();
    expect(screen.getByLabelText('exportReadiness.hsCode')).toBeInTheDocument();
    expect(screen.getByLabelText('exportReadiness.productName')).toBeInTheDocument();
    expect(screen.getByLabelText('exportReadiness.targetMarket')).toBeInTheDocument();
  });

  it('shows loading state when analyzing', async () => {
    vi.mocked(analyzeExportReadiness).mockImplementation(
      () => new Promise(() => {})
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );

    const targetInput = screen.getByLabelText('exportReadiness.targetMarket');
    await user.type(targetInput, 'DE');

    const analyzeButton = screen.getByRole('button', { name: 'exportReadiness.analyze' });
    await user.click(analyzeButton);

    await waitFor(() => {
      expect(analyzeButton).toBeDisabled();
    });
  });

  it('calls analyzeExportReadiness with correct payload', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText('exportReadiness.productId'), '1');
    await user.type(screen.getByLabelText('exportReadiness.hsCode'), '080510');
    await user.type(screen.getByLabelText('exportReadiness.productName'), 'Oranges');
    await user.type(screen.getByLabelText('exportReadiness.targetMarket'), 'DE');

    const analyzeButton = screen.getByRole('button', { name: 'exportReadiness.analyze' });
    await user.click(analyzeButton);

    await waitFor(() => {
      expect(analyzeExportReadiness).toHaveBeenCalledWith({
        product_id: 1,
        hs_code: '080510',
        product_name: 'Oranges',
        target_market: 'DE',
      });
    });
  });

  it('displays successful report with all sections', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText('exportReadiness.targetMarket'), 'DE');
    await user.click(screen.getByRole('button', { name: 'exportReadiness.analyze' }));

    await waitFor(() => {
      expect(screen.getByText('exportReadiness.productSummary')).toBeInTheDocument();
    });

    expect(screen.getByText('Regulatory Requirements')).toBeInTheDocument();
    expect(screen.getByText('Market Access Conditions')).toBeInTheDocument();
    expect(screen.getByText('Logistics Profile')).toBeInTheDocument();
    expect(screen.getByText('Historical Trade Context')).toBeInTheDocument();
    expect(screen.getByText('exportReadiness.actionChecklist')).toBeInTheDocument();
    expect(screen.getByText('exportReadiness.recommendation')).toBeInTheDocument();
    expect(screen.getByText('exportReadiness.dataQualityNote')).toBeInTheDocument();
  });

  it('shows availability states correctly', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText('exportReadiness.targetMarket'), 'DE');
    await user.click(screen.getByRole('button', { name: 'exportReadiness.analyze' }));

    await waitFor(() => {
      expect(screen.getAllByText('exportReadiness.available').length).toBeGreaterThan(0);
    });
    expect(screen.getByText('exportReadiness.notAvailable')).toBeInTheDocument();
  });

  it('displays recommendation when available', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText('exportReadiness.targetMarket'), 'DE');
    await user.click(screen.getByRole('button', { name: 'exportReadiness.analyze' }));

    await waitFor(() => {
      expect(screen.getByText('Test recommendation')).toBeInTheDocument();
    });
  });

  it('shows graceful state when recommendation is null', async () => {
    vi.mocked(analyzeExportReadiness).mockResolvedValue({
      data: { ...mockReport, recommendation: null },
    } as any);

    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText('exportReadiness.targetMarket'), 'DE');
    await user.click(screen.getByRole('button', { name: 'exportReadiness.analyze' }));

    await waitFor(() => {
      expect(screen.getByText('exportReadiness.noRecommendation')).toBeInTheDocument();
    });
  });

  it('shows error state on API failure', async () => {
    vi.mocked(analyzeExportReadiness).mockRejectedValue(new Error('API Error'));
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ExportReadiness />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText('exportReadiness.targetMarket'), 'DE');
    await user.click(screen.getByRole('button', { name: 'exportReadiness.analyze' }));

    await waitFor(() => {
      expect(screen.getByText('Analysis failed. Please try again.')).toBeInTheDocument();
    });
  });
});
