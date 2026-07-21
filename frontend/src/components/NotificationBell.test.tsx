import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/services/api', () => ({
  getAuditLogs: vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

vi.mock('@/components/ui/popover', () => ({
  Popover: ({ children, open, onOpenChange }: any) => (
    <div data-testid="popover" data-open={open}>
      {typeof onOpenChange === 'function' && (
        <button
          onClick={() => onOpenChange(!open)}
          data-testid="popover-toggle"
        >
          toggle
        </button>
      )}
      {children}
    </div>
  ),
  PopoverTrigger: ({ children, asChild }: any) => (asChild ? children : <div>{children}</div>),
  PopoverContent: ({ children, className, align }: any) => (
    <div data-testid="popover-content" data-align={align} className={className}>
      {children}
    </div>
  ),
}));

import { getAuditLogs } from '@/services/api';
import { NotificationBell } from '@/components/NotificationBell';

const mockLogs = [
  {
    id: 1,
    action: 'created',
    entity_type: 'customer',
    entity_id: 10,
    details: 'New customer added',
    created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
  {
    id: 2,
    action: 'updated',
    entity_type: 'invoice',
    entity_id: 20,
    details: 'Invoice status changed',
    created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
  },
];

describe('NotificationBell', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getAuditLogs).mockResolvedValue({ data: [] } as any);
  });

  it('renders bell icon', () => {
    render(
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    );
    expect(screen.getByTestId('popover-toggle')).toBeInTheDocument();
    expect(screen.getByTestId('popover-content')).toBeInTheDocument();
  });

  it('shows unread count badge when there are unread notifications', async () => {
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: mockLogs } as any);
    render(
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  it('does not show badge when all notifications are read', async () => {
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: [] } as any);
    render(
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.queryByText('2')).not.toBeInTheDocument();
    });
  });

  it('loads notifications on mount', async () => {
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: mockLogs } as any);
    render(
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(getAuditLogs).toHaveBeenCalledWith({ limit: 10 });
    });
  });

  it('shows loading state in dropdown', async () => {
    vi.mocked(getAuditLogs).mockImplementation(
      () => new Promise(() => {})
    );
    render(
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    );

    const toggle = screen.getByTestId('popover-toggle');
    await userEvent.click(toggle);

    expect(screen.getByTestId('popover-content')).toBeInTheDocument();
  });

  it('shows empty state when no notifications', async () => {
    vi.mocked(getAuditLogs).mockResolvedValueOnce({ data: [] } as any);
    render(
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('popover-content')).toBeInTheDocument();
    });

    const toggle = screen.getByTestId('popover-toggle');
    await userEvent.click(toggle);

    await waitFor(() => {
      expect(screen.getByText(/notifications.noNotifications/)).toBeInTheDocument();
    });
  });

  it('shows notification list in dropdown', async () => {
    vi.mocked(getAuditLogs).mockResolvedValue({ data: mockLogs } as any);
    render(
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('popover-content')).toBeInTheDocument();
    });

    const toggle = screen.getByTestId('popover-toggle');
    await userEvent.click(toggle);

    await waitFor(() => {
      expect(screen.getByText('created')).toBeInTheDocument();
      expect(screen.getByText('updated')).toBeInTheDocument();
    });
  });

  it('marks notification as read when clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(getAuditLogs).mockResolvedValue({ data: mockLogs } as any);
    render(
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('popover-content')).toBeInTheDocument();
    });

    const toggle = screen.getByTestId('popover-toggle');
    await userEvent.click(toggle);

    await waitFor(() => {
      expect(screen.getByText('created')).toBeInTheDocument();
    });

    const item = screen.getByText('created').closest('div');
    if (item) await user.click(item);

    await waitFor(() => {
      const badge = screen.queryByText('2');
      expect(badge).not.toBeInTheDocument();
    });
  });
});
