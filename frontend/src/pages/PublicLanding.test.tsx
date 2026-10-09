import { beforeEach, describe, expect, test } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PublicLanding } from '@/pages/PublicLanding';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/lib/i18n';

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <BrowserRouter>
      <I18nextProvider i18n={i18n}>{ui}</I18nextProvider>
    </BrowserRouter>,
  );
}

describe('PublicLanding', () => {
  beforeEach(async () => {
    await i18n.changeLanguage('en');
  });

  test('renders the company identity and hero message', () => {
    renderWithProviders(<PublicLanding />);

    expect(screen.getByRole('heading', { level: 1, name: 'Nile Key for Investment and International Trade LLC' })).toBeDefined();
    expect(screen.getByText('Bringing high-quality Egyptian products to global markets')).toBeDefined();
    expect(screen.getAllByText('NK').length).toBeGreaterThanOrEqual(1);
  });

  test('renders only the sections in the Arabic reference composition', () => {
    renderWithProviders(<PublicLanding />);

    expect(screen.getByText('Your Trusted Partner in International Trade')).toBeDefined();
    expect(screen.getByText('The Export Journey')).toBeDefined();
    expect(screen.getByRole('heading', { name: /Our Integrated Digital Platform\s*for Egyptian Export Operations/ })).toBeDefined();
    expect(screen.getByRole('heading', { name: 'Your Strategic Partner in Global Trade' })).toBeDefined();
    expect(screen.queryByRole('heading', { name: 'Premium Egyptian Products' })).toBeNull();
    expect(screen.queryByRole('heading', { name: 'Our Presence in Global Markets' })).toBeNull();
    expect(screen.queryByRole('heading', { name: 'Trusted by Global Partners' })).toBeNull();
  });

  test('renders exactly four export journey stages in reference order', () => {
    renderWithProviders(<PublicLanding />);

    const journey = screen.getByText('The Export Journey').parentElement?.parentElement;
    expect(journey).not.toBeNull();
    const labels = [
      'Egyptian Farms & Factories',
      'Port',
      'Transport & Shipping',
      'Global Markets',
    ];
    for (const label of labels) {
      expect(within(journey as HTMLElement).getAllByText(label).length).toBeGreaterThanOrEqual(1);
    }
  });

  test('renders six platform capabilities', () => {
    renderWithProviders(<PublicLanding />);

    const featureTitles = [
      'Invoicing & Payments',
      'Shipment Management',
      'Customer Management',
      'Product Management',
      'Reports & Analytics',
      'Global Markets',
    ];
    for (const title of featureTitles) expect(screen.getByRole('heading', { name: title })).toBeDefined();
  });

  test('uses independent homepage image assets rather than reference or design-board crops', () => {
    renderWithProviders(<PublicLanding />);

    const images = Array.from(document.querySelectorAll('main img'));
    expect(images).toHaveLength(6);
    expect(images.map((image) => image.getAttribute('src'))).toEqual([
      '/assets/home/hero-scene.png',
      '/assets/home/company-cargo-ship.jpg',
      '/assets/home/export-journey-panorama.jpg',
      '/assets/home/company-cargo-ship.jpg',
      '/assets/home/hero-produce.jpg',
      '/assets/home/global-trade-cta.jpg',
    ]);
    expect(images.some((image) => image.getAttribute('src')?.includes('design-reference'))).toBe(false);
  });

  test('keeps both account actions linked to login', () => {
    renderWithProviders(<PublicLanding />);

    const loginLinks = screen.getAllByRole('link').filter((link) => link.getAttribute('href') === '/login');
    expect(loginLinks.length).toBeGreaterThanOrEqual(2);
  });

  test('does not render fake account, shipment, or ERP records', () => {
    renderWithProviders(<PublicLanding />);

    expect(screen.queryByText('Alexandria')).toBeNull();
    expect(screen.queryByText('Aswan')).toBeNull();
    expect(screen.queryByText('Active')).toBeNull();
    expect(screen.queryByText('owner')).toBeNull();
    expect(screen.queryByText('supplier')).toBeNull();
    expect(screen.queryByText('customer')).toBeNull();
  });
});
