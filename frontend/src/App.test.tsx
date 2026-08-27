import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { Sidebar } from '@/components/layout/Sidebar';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/lib/i18n';
import { useAuthStore } from '@/store/authStore';

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

describe('WP-42-C: Role-Based Workspace & Navigation', () => {
  test('supplier and customer cannot access DEM via navigation', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'supplier' },
    });
    renderWithProviders(<Layout />);
    expect(screen.queryByText('Digital Export Manager')).toBeNull();
    expect(screen.queryByText('Knowledge Graph')).toBeNull();
    expect(screen.queryByText('Trade Intelligence')).toBeNull();
  });

  test('customer cannot access DEM via navigation', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'customer' },
    });
    renderWithProviders(<Layout />);
    expect(screen.queryByText('Digital Export Manager')).toBeNull();
  });

  test('internal roles can access DEM via navigation', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      isLoading: false,
      user: { ...originalAuth.user, role: 'sales' },
      loadUser: async () => {},
    });
    renderWithProviders(<Layout />);
    expect(screen.getByText('Digital Export Manager')).toBeDefined();
  });

  test('navigation updates dynamically when user role changes', () => {
    const { rerender } = renderWithProviders(<Layout />);
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'supplier' },
    });
    rerender(
      <MemoryRouter>
        <I18nextProvider i18n={i18n}>
          <Layout />
        </I18nextProvider>
      </MemoryRouter>
    );
    expect(screen.queryByText('Digital Export Manager')).toBeNull();
  });

  test('sidebar hides DEM KG TI for external roles', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'supplier' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    expect(screen.queryByText('Digital Export Manager')).toBeNull();
    expect(screen.queryByText('Knowledge Graph')).toBeNull();
    expect(screen.queryByText('Trade Intelligence')).toBeNull();
  });

  test('sidebar shows DEM KG TI for internal roles', () => {
    useAuthStore.setState({
      ...originalAuth,
      isAuthenticated: true,
      user: { ...originalAuth.user, role: 'owner' },
    });
    renderWithProviders(<Sidebar collapsed={false} onToggleCollapsed={() => {}} />);
    expect(screen.getByText('Digital Export Manager')).toBeDefined();
    expect(screen.getByText('Knowledge Graph')).toBeDefined();
    expect(screen.getByText('Trade Intelligence')).toBeDefined();
  });
});
