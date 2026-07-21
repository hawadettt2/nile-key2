import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('@/services/api', () => ({
  getAuditLogs: vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

import { getAuditLogs } from '@/services/api';
import { Notifications } from '@/pages/Notifications';

const mockLogs = [
  {
    id: 1,
    action: 'created',
    entity_type: 'customer',
    entity_id: 10,
    details: 'New customer added',
    created_at: '2024-01-01T10:00:00Z',
  },
  {
    id: 2,
    action: 'updated',
    entity_type: 'invoice',
    entity_id: 20,
    details: 'Invoice status changed',
    created_at: '2024-01-02T11:00:00Z',
  },
  {
    id: 3,
    action: 'deleted',
    entity_type: 'shipment',
    entity_id: 30,
    details: 'Shipment cancelled',
    created_at: '2024-01-03T12:00:00Z',
  },
];

describe('Notifications', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getAuditLogs).mockResolvedValue({ data: [] } as any);
  });

  it('renders loading state initially', () => {
    vi.mocked(getAuditLogs).mockImplementation(
      () => new Promise(() => {})
    );
    render(<Notifications />);
    expect(screen.getByRole('button', { name: /refresh/i })).toBeDisabled();
  });

  it('renders error state when API fails', async () => {
    vi.mocked(getAuditLogs).mockRejectedValueOnce(new Error('API error'));
    render(<Notifications />);
    await waitFor(() => {
      expect(screen.getByText('API error')).toBeInTheDocument();
    });
  });

  it('renders empty state when no notifications', async () => {
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: [] } as any);
    render(<Notifications />);
    await waitFor(() => {
      expect(screen.getByText(/notifications.noNotifications/)).toBeInTheDocument();
    });
  });

  it('renders notification list when data is available', async () => {
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: mockLogs } as any);
    render(<Notifications />);
    await waitFor(() => {
      expect(screen.getByText('created')).toBeInTheDocument();
      expect(screen.getByText('updated')).toBeInTheDocument();
      expect(screen.getByText('deleted')).toBeInTheDocument();
    });
  });

  it('filters notifications by unread', async () => {
    const user = userEvent.setup();
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: mockLogs } as any);
    render(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('created')).toBeInTheDocument();
    });

    const unreadButton = screen.getByRole('button', { name: /notifications.unread/i });
    await user.click(unreadButton);

    expect(screen.getByText('created')).toBeInTheDocument();
  });

  it('filters notifications by entity type', async () => {
    const user = userEvent.setup();
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: mockLogs } as any);
    render(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('created')).toBeInTheDocument();
    });

    const entitySelect = screen.getByRole('combobox');
    await user.selectOptions(entitySelect, 'invoice');

    expect(screen.queryByText('created')).not.toBeInTheDocument();
    expect(screen.getByText('updated')).toBeInTheDocument();
  });

  it('marks notification as read when clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: mockLogs } as any);
    render(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('created')).toBeInTheDocument();
    });

    const item = screen.getByText('created').closest('div');
    if (item) await user.click(item);

    await waitFor(() => {
      const unreadBadge = screen.queryByText('3 unread notifications');
      expect(unreadBadge).not.toBeInTheDocument();
    });
  });

  it('marks all notifications as read when button is clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: mockLogs } as any);
    render(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('3 unread notifications')).toBeInTheDocument();
    });

    const markAllButton = screen.getByRole('button', { name: /notifications.markAllRead/i });
    await user.click(markAllButton);

    await waitFor(() => {
      const unreadCount = screen.queryByText('3 unread notifications');
      expect(unreadCount).not.toBeInTheDocument();
    });
  });

  it('refreshes notifications when refresh button is clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(getAuditLogs)
      .mockResolvedValueOnce({ data: mockLogs } as any)
      .mockResolvedValueOnce({ data: [] } as any);
    render(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('created')).toBeInTheDocument();
    });

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    await user.click(refreshButton);

    await waitFor(() => {
      expect(screen.getByText(/notifications.noNotifications/)).toBeInTheDocument();
    });
  });
});
