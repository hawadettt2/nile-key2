import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { PotentialCustomers } from '@/pages/PotentialCustomers';

const mockedListPotentialCustomerCountries = vi.fn();

vi.mock('@/services/api', () => ({
  listPotentialCustomerCountries: (...args: any[]) => mockedListPotentialCustomerCountries(...args),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en' },
  }),
  I18nextProvider: ({ children }: { children: React.ReactNode }) => children,
  initReactI18next: vi.fn(),
}));

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MemoryRouter>
      {ui}
    </MemoryRouter>
  );
}

describe('PotentialCustomers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedListPotentialCustomerCountries.mockResolvedValue({
      data: {
        countries: [
          {
            id: 'country-uae',
            name: 'UAE',
            file_count: 1,
            files: [
              {
                id: 'file-uae-001',
                name: 'UAE_Raw_Buyers.xlsx',
                source: 'Google Drive',
                sheet_count: 4,
                row_count: 100,
                size_bytes: 1024,
              },
            ],
          },
        ],
        total_countries: 1,
        total_files: 1,
        source: 'google-drive',
      },
    } as any);
  });

  test('renders page title', async () => {
    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });
    expect(screen.getByText('Potential Customers')).toBeDefined();
  });

  test('renders country cards', async () => {
    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });
    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });
  });

  test('opens country detail when clicking country card', async () => {
    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });
    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });
    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });
    expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
  });
});
