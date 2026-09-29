import { render, screen, fireEvent, waitFor, act, within } from '@testing-library/react';
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

vi.mock('@/store/authStore', () => {
  const mockUseAuthStore = vi.fn((selector?: (state: any) => any) => {
    const state = { user: { role: 'owner' } };
    if (typeof selector === 'function') {
      return selector(state);
    }
    return state;
  });
  return { useAuthStore: mockUseAuthStore };
});

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

  test('renders potential customers button', async () => {
    await act(async () => {
      renderWithProviders(<Customers />);
    });
    expect(screen.getByText('العملاء المحتملين')).toBeDefined();
  });

  test('renders status fields in add customer form', async () => {
    await act(async () => {
      renderWithProviders(<Customers />);
    });
    fireEvent.click(screen.getByText('customer.addCustomer'));
    const crmCount = screen.getAllByText('customer.crmStatus').length;
    const verificationCount = screen.getAllByText('customer.verificationStatus').length;
    const activityCount = screen.getAllByText('customer.activityStatus').length;
    expect(crmCount).toBeGreaterThan(0);
    expect(verificationCount).toBeGreaterThan(0);
    expect(activityCount).toBeGreaterThan(0);
  });

  test('submits create customer with status values', async () => {
    mockedCreateCustomer.mockResolvedValue({ id: 1, message: 'Customer created successfully' } as any);
    await act(async () => {
      renderWithProviders(<Customers />);
    });
    fireEvent.click(screen.getByText('customer.addCustomer'));

    const formContainers = document.querySelectorAll('.bg-white.rounded-xl.p-6');
    const formContainer = formContainers[0] as HTMLElement;

    const textboxes = within(formContainer).getAllByRole('textbox');
    fireEvent.change(textboxes[0], { target: { value: 'Test Corp' } });
    fireEvent.change(textboxes[2], { target: { value: 'UAE' } });

    const comboboxes = within(formContainer).getAllByRole('combobox');
    fireEvent.change(comboboxes[0], { target: { value: 'active_customer' } });
    fireEvent.change(comboboxes[1], { target: { value: 'verified' } });
    fireEvent.change(comboboxes[2], { target: { value: 'observed_active' } });

    fireEvent.click(screen.getByText('common.save'));

    await waitFor(() => {
      expect(mockedCreateCustomer).toHaveBeenCalledWith(
        expect.objectContaining({
          crm_status: 'active_customer',
          verification_status: 'verified',
          activity_status: 'observed_active',
        })
      );
    });
  });

  test('populates status fields when editing customer', async () => {
    mockedListCustomers.mockResolvedValue({
      data: [{
        id: 1,
        name: 'Test Corp',
        country: 'UAE',
        crm_status: 'active_customer',
        verification_status: 'verified',
        activity_status: 'observed_active',
      }],
    } as any);

    await act(async () => {
      renderWithProviders(<Customers />);
    });

    const row = screen.getByText('Test Corp').closest('tr')!;
    const editButton = within(row).getAllByRole('button')[0];
    fireEvent.click(editButton);

    const formContainers = document.querySelectorAll('.bg-white.rounded-xl.p-6');
    const formContainer = formContainers[0] as HTMLElement;
    const comboboxes = within(formContainer).getAllByRole('combobox');

    expect(comboboxes[0]).toHaveValue('active_customer');
    expect(comboboxes[1]).toHaveValue('verified');
    expect(comboboxes[2]).toHaveValue('observed_active');
  });
});
