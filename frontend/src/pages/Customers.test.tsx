import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { Customers } from '@/pages/Customers';

const mockedListCustomers = vi.fn();
const mockedGetCustomer = vi.fn();
const mockedCreateCustomer = vi.fn();
const mockedUpdateCustomer = vi.fn();
const mockedDeleteCustomer = vi.fn();
const mockedImportCustomers = vi.fn();
const mockedGetCustomerCountries = vi.fn();
const mockedListCustomerProducts = vi.fn();
const mockedListCustomerEvidence = vi.fn();

vi.mock('@/services/api', () => ({
  listCustomers: (...args: any[]) => mockedListCustomers(...args),
  getCustomer: (...args: any[]) => mockedGetCustomer(...args),
  createCustomer: (...args: any[]) => mockedCreateCustomer(...args),
  updateCustomer: (...args: any[]) => mockedUpdateCustomer(...args),
  deleteCustomer: (...args: any[]) => mockedDeleteCustomer(...args),
  importCustomers: (...args: any[]) => mockedImportCustomers(...args),
  getCustomerCountries: (...args: any[]) => mockedGetCustomerCountries(...args),
  listCustomerProducts: (...args: any[]) => mockedListCustomerProducts(...args),
  listCustomerEvidence: (...args: any[]) => mockedListCustomerEvidence(...args),
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

describe('Customers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedListCustomers.mockResolvedValue({ data: [] } as any);
    mockedGetCustomerCountries.mockResolvedValue({ data: [] } as any);
    mockedListCustomerProducts.mockResolvedValue({ data: [] } as any);
    mockedListCustomerEvidence.mockResolvedValue({ data: [] } as any);
    mockedGetCustomer.mockResolvedValue({ data: { raw_records: [], source_batches: [] } } as any);
  });

  test('renders component without crashing', async () => {
    await act(async () => {
      renderWithProviders(<Customers />);
    });
    expect(document.body).toBeDefined();
  });
});
