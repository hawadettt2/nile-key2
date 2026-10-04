import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PublicLanding } from '@/pages/PublicLanding';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/lib/i18n';

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <BrowserRouter>
      <I18nextProvider i18n={i18n}>
        {ui}
      </I18nextProvider>
    </BrowserRouter>
  );
}

describe('PublicLanding', () => {
  test('renders company name and intro sections', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.getAllByText('Nile Key').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Our Integrated Digital Platform for Managing Egyptian Export Operations')).toBeDefined();
  });

  test('renders Login and Register CTAs linking to /login', () => {
    renderWithProviders(<PublicLanding />);
    const links = screen.getAllByRole('link');
    const loginLinks = links.filter(link => link.getAttribute('href') === '/login');
    expect(loginLinks.length).toBeGreaterThanOrEqual(2);
  });

  test('does not expose internal dashboard or ERP data', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.queryByText('Dashboard')).toBeNull();
    expect(screen.queryByText('owner')).toBeNull();
    expect(screen.queryByText('manager')).toBeNull();
    expect(screen.queryByText('supplier')).toBeNull();
    expect(screen.queryByText('customer')).toBeNull();
  });

  test('renders feature cards', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.getByText('Shipment Management')).toBeDefined();
    expect(screen.getByText('E-Invoicing')).toBeDefined();
    expect(screen.getByText('Customs Clearance')).toBeDefined();
  });

  test('renders NK logo branding', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.getAllByText('NK').length).toBeGreaterThanOrEqual(1);
  });
});
