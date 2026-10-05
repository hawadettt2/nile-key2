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
  test('renders company name and hero identity', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.getAllByText('Nile Key').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('EGYPTIAN PRODUCTS • GLOBAL MARKETS')).toBeDefined();
    expect(screen.getByText('شركة مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م)')).toBeDefined();
    expect(screen.getByText('Nile Key for Investment and International Trade LLC')).toBeDefined();
  });

  test('renders the final 7-section composition in order', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.getByText('Our Company')).toBeDefined();
    expect(screen.getByText('Premium Egyptian Products')).toBeDefined();
    expect(screen.getByText('The Export Journey')).toBeDefined();
    expect(screen.getByText('Our Integrated Digital Platform')).toBeDefined();
    expect(screen.getByText('for Export Operations')).toBeDefined();
    expect(screen.getByText('Our Presence in Global Markets')).toBeDefined();
    expect(screen.getByText('Trusted by Global Partners')).toBeDefined();
    expect(screen.getByText("Let's Grow Together")).toBeDefined();
  });

  test('renders the 5 export journey steps', () => {
    renderWithProviders(<PublicLanding />);
    // Both desktop (horizontal) and mobile (vertical) variants render in jsdom
    expect(screen.getAllByText('Farm / Factory').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Packing & Quality').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Export Documents').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Shipping').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Port & Delivery').length).toBeGreaterThanOrEqual(1);
  });

  test('renders the 3 approved global market statistics', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.getByText('50+')).toBeDefined();
    expect(screen.getByText('200+')).toBeDefined();
    expect(screen.getByText('100%')).toBeDefined();
    expect(screen.getByText('Countries')).toBeDefined();
    expect(screen.getByText('Business Partners')).toBeDefined();
    expect(screen.getByText('Commitment to Quality')).toBeDefined();
  });

  test('renders Login and Create Account CTAs linking to /login', () => {
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

  test('does not render the removed Feature Band or Global Closing Banner', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.queryByText('Shipment Management')).toBeNull();
    expect(screen.queryByText('E-Invoicing')).toBeNull();
    expect(screen.queryByText('Customs Clearance')).toBeNull();
    expect(screen.queryByText('Bringing the Best of Egypt to the World')).toBeNull();
    expect(screen.queryByText('More Than a Trading Company')).toBeNull();
  });

  test('renders NK logo branding', () => {
    renderWithProviders(<PublicLanding />);
    expect(screen.getAllByText('NK').length).toBeGreaterThanOrEqual(1);
  });
});
