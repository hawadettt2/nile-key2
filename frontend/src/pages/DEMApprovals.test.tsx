import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/services/api', () => ({
  getApprovals: vi.fn(),
  approveMission: vi.fn(),
  rejectMission: vi.fn(),
}));

const mockUseAuthStore = vi.fn();
vi.mock('@/store/authStore', () => ({
  useAuthStore: (selector?: (s: any) => any) => {
    const state = mockUseAuthStore();
    if (typeof selector === 'function') {
      return selector(state);
    }
    return state;
  },
}));

const mockApprovalsState: any[] = [];
const mockSetApprovals = vi.fn((vals: any[]) => { mockApprovalsState.length = 0; mockApprovalsState.push(...vals); });
const mockRemoveApproval = vi.fn((id: string) => {
  const idx = mockApprovalsState.findIndex((a: any) => a.mission_id === id);
  if (idx >= 0) mockApprovalsState.splice(idx, 1);
});

vi.mock('@/store/approvalStore', () => ({
  useApprovalStore: () => ({
    approvals: mockApprovalsState,
    setApprovals: mockSetApprovals,
    removeApproval: mockRemoveApproval,
  }),
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

import { getApprovals, approveMission, rejectMission } from '@/services/api';
import { DEMApprovals } from '@/pages/DEMApprovals';

const mockApprovals = [
  {
    mission_id: 'mission-123',
    session_id: 'session-456',
    user_id: 1,
    mission_type: 'CREATE_SHIPMENT',
    status: 'pending_approval',
    requires_approval: true,
    approval_status: 'pending',
    reasoning: 'Test reasoning',
    created_at: new Date().toISOString(),
  },
];

describe('DEMApprovals', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApprovalsState.length = 0;
    mockUseAuthStore.mockReturnValue({ user: { role: 'manager' }, logout: vi.fn() });
    vi.mocked(getApprovals).mockResolvedValue({ data: mockApprovals } as any);
    vi.mocked(approveMission).mockResolvedValue({ data: { decision: 'approved' } } as any);
    vi.mocked(rejectMission).mockResolvedValue({ data: { decision: 'rejected' } } as any);
  });

  it('renders approval inbox title', async () => {
    render(
      <MemoryRouter>
        <DEMApprovals />
      </MemoryRouter>
    );
    expect(screen.getByText('dem.approvalInbox')).toBeInTheDocument();
  });

  it('loads approvals on mount', async () => {
    render(
      <MemoryRouter>
        <DEMApprovals />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(getApprovals).toHaveBeenCalled();
    });
  });

  it('calls approve when approve button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <DEMApprovals />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/mission-123/)).toBeInTheDocument());

    const approveButtons = screen.getAllByRole('button', { name: /dem.approve/ });
    await user.click(approveButtons[0]);

    await waitFor(() => {
      expect(approveMission).toHaveBeenCalledWith('mission-123');
    });
  });

  it('calls reject when reject button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <DEMApprovals />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/mission-123/)).toBeInTheDocument());

    const rejectButtons = screen.getAllByRole('button', { name: /dem.reject/ });
    await user.click(rejectButtons[0]);

    await waitFor(() => {
      expect(rejectMission).toHaveBeenCalledWith('mission-123');
    });
  });

  it('shows empty state when no approvals', async () => {
    vi.mocked(getApprovals).mockResolvedValueOnce({ data: [] } as any);
    render(
      <MemoryRouter>
        <DEMApprovals />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('dem.noPendingApprovals')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('shows permission denied for non-manager role', () => {
    mockUseAuthStore.mockReturnValue({ user: { role: 'staff' }, logout: vi.fn() });
    render(
      <MemoryRouter>
        <DEMApprovals />
      </MemoryRouter>
    );

    expect(screen.getByText('dem.noPermissionApprovals')).toBeInTheDocument();
  });
});
