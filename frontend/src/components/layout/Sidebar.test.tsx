import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/lib/i18n';
import { useAuthStore } from '@/store/authStore';
import { userEvent } from '@testing-library/user-event';
import { waitFor } from '@testing-library/react';

const originalAuth = useAuthStore.getState();

function renderWithProviders(ui: React.ReactElement, { route = '/' } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <I18nextProvider i18n={i18n}>
        {ui}
      </I18nextProvider>
    </MemoryRouter>
  );
}

afterEach(() => {
  useAuthStore.setState(originalAuth);
});

describe('Sidebar Accessibility', () => {
  test('mobile menu button has aria-label and aria-expanded', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    const menuButton = screen.getByLabelText('Open menu');
    expect(menuButton).toBeDefined();
    expect(menuButton.getAttribute('aria-expanded')).toBe('false');
    expect(menuButton.getAttribute('aria-controls')).toBe('mobile-drawer');
  });

  test('collapse button has aria-label and aria-expanded', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    const collapseButtons = screen.getAllByLabelText('Collapse sidebar');
    expect(collapseButtons.length).toBeGreaterThan(0);
    expect(collapseButtons[0].getAttribute('aria-expanded')).toBe('true');
  });

  test('logout button has aria-label', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    const logoutButtons = screen.getAllByLabelText('Logout');
    expect(logoutButtons.length).toBeGreaterThan(0);
  });

  test('active navigation link has aria-current=page', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />, { route: '/dashboard' });
    const dashboardLinks = screen.getAllByRole('link', { name: /Dashboard/i });
    const activeLink = dashboardLinks.find(link => link.getAttribute('aria-current') === 'page');
    expect(activeLink).toBeDefined();
  });

  test('mobile drawer opens and closes', async () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    const menuButton = screen.getByLabelText('Open menu');
    await userEvent.click(menuButton);
    expect(screen.getByLabelText('Close menu')).toBeDefined();
    const drawer = screen.getByLabelText('Mobile navigation');
    expect(drawer.getAttribute('aria-modal')).toBe('true');
    expect(drawer.classList.contains('translate-x-0')).toBe(true);
  });

  test('Escape closes mobile drawer', async () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    const menuButton = screen.getByLabelText('Open menu');
    await userEvent.click(menuButton);
    const drawer = screen.getByLabelText('Mobile navigation');
    const firstLink = drawer.querySelector('a');
    if (firstLink) firstLink.focus();
    await userEvent.keyboard('{Escape}');
    await waitFor(() => {
      expect(menuButton.getAttribute('aria-expanded')).toBe('false');
    });
    await waitFor(() => {
      expect(drawer.classList.contains('-translate-x-full')).toBe(true);
    });
  });

  test('focus returns to trigger after drawer closes', async () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    const menuButton = screen.getByLabelText('Open menu');
    await userEvent.click(menuButton);
    await userEvent.keyboard('{Escape}');
    await waitFor(() => {
      expect(document.activeElement).toBe(menuButton);
    });
  });

  test('backdrop click closes mobile drawer', async () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    const menuButton = screen.getByLabelText('Open menu');
    await userEvent.click(menuButton);
    const drawer = screen.getByLabelText('Mobile navigation');
    const backdrop = drawer.previousElementSibling as HTMLElement | null;
    expect(backdrop).toBeTruthy();
    if (backdrop) {
      await userEvent.click(backdrop);
    }
    await waitFor(() => {
      expect(menuButton.getAttribute('aria-expanded')).toBe('false');
    });
    await waitFor(() => {
      expect(drawer.classList.contains('-translate-x-full')).toBe(true);
    });
  });

  test('clicking navigation link closes mobile drawer', async () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    const menuButton = screen.getByLabelText('Open menu');
    await userEvent.click(menuButton);
    const drawer = screen.getByLabelText('Mobile navigation');
    const firstLink = drawer.querySelector('a');
    if (firstLink) {
      await userEvent.click(firstLink);
    }
    await waitFor(() => {
      expect(menuButton.getAttribute('aria-expanded')).toBe('false');
    });
    await waitFor(() => {
      expect(drawer.classList.contains('-translate-x-full')).toBe(true);
    });
  });
});
