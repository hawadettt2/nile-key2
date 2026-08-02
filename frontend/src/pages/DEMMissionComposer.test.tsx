import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/services/api', () => ({
  createMission: vi.fn(),
}));

const mockUseDEMStore = vi.fn();
vi.mock('@/store/demStore', () => ({
  useDEMStore: () => mockUseDEMStore(),
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

import { createMission } from '@/services/api';
import { DEMMissionComposer } from '@/pages/DEMMissionComposer';

describe('DEMMissionComposer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseDEMStore.mockReturnValue({
      activeSession: { session_id: 'session-123', status: 'active' },
      setCurrentMission: vi.fn(),
    });
    vi.mocked(createMission).mockResolvedValue({ data: { mission_id: 'mission-456', status: 'pending' } } as any);
  });

  it('renders new mission title', () => {
    render(
      <MemoryRouter>
        <DEMMissionComposer />
      </MemoryRouter>
    );
    expect(screen.getByText('dem.newMission')).toBeInTheDocument();
  });

  it('shows connect prompt when no active session', () => {
    mockUseDEMStore.mockReturnValue({
      activeSession: null,
      setCurrentMission: vi.fn(),
    });
    render(
      <MemoryRouter>
        <DEMMissionComposer />
      </MemoryRouter>
    );
    expect(screen.getByText('dem.connectDemFirst')).toBeInTheDocument();
  });

  it('calls createMission when form is submitted', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <DEMMissionComposer />
      </MemoryRouter>
    );

    const createShipmentCard = screen.getByText('dem.missionTypes.create_shipment');
    await user.click(createShipmentCard);

    const submitButton = screen.getByRole('button', { name: 'dem.submitMission' });
    await user.click(submitButton);

    await waitFor(() => {
      expect(createMission).toHaveBeenCalledWith('session-123', expect.any(Object));
    });
  });

  it('renders mission type cards', () => {
    render(
      <MemoryRouter>
        <DEMMissionComposer />
      </MemoryRouter>
    );

    expect(screen.getByText('dem.missionTypes.create_shipment')).toBeInTheDocument();
    expect(screen.getByText('dem.missionTypes.submit_invoice')).toBeInTheDocument();
  });
});
