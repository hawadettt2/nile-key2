import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { PotentialCustomers } from '@/pages/PotentialCustomers';

const mockedListPotentialCustomerCountries = vi.fn();
const mockedGetPotentialCustomerFileContent = vi.fn();

vi.mock('@/services/api', () => ({
  listPotentialCustomerCountries: (...args: any[]) => mockedListPotentialCustomerCountries(...args),
  getPotentialCustomerFileContent: (...args: any[]) => mockedGetPotentialCustomerFileContent(...args),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en' },
  }),
  I18nextProvider: ({ children }: { children: React.ReactNode }) => children,
  initReactI18next: vi.fn(),
}));

beforeEach(() => {
  navigator.clipboard = {
    writeText: vi.fn(() => Promise.resolve()),
  } as any;
});

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
                sheet_count: 1,
                row_count: 5,
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

    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'UAE_Raw_Buyers.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'Company Name', '2': 'Mobile', '3': 'Email', '4': 'Address' },
          { '1': 'Acme Corp', '2': '0501234567', '3': 'info@acme.com', '4': 'Dubai' },
          { '1': '', '2': '0507654321', '3': 'test@example.com', '4': '' },
          { '1': 'Beta Ltd', '2': '', '3': 'beta@beta.com', '4': '' },
          { '1': '', '2': '', '3': '', '4': '' },
        ],
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

  test('limits concurrent translation requests and deduplicates in-flight text', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => [[['مرحبا', 'Hello']]],
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🌐 عرض بالعربية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🌐 عرض بالعربية'));
    });

    await waitFor(() => {
      expect(screen.getAllByText('مرحبا').length).toBeGreaterThan(0);
    });

    const translateCalls = fetchSpy.mock.calls.filter((call: any) =>
      call[0].includes('translate.googleapis.com')
    );

    const uniqueTexts = new Set(translateCalls.map((call: any) => call[0]));
    expect(translateCalls.length).toBeGreaterThan(0);
    expect(translateCalls.length).toBe(uniqueTexts.size);

    fetchSpy.mockRestore();
  });

  test('renders smart filter button and opens filter panel', async () => {
    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    expect(screen.getByText('شروط الفلترة')).toBeDefined();
    expect(screen.getByText('اسم الشركة')).toBeDefined();
    expect(screen.getByText('الموبايل')).toBeDefined();
  });

  test('filters rows by company name and updates count', async () => {
    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await waitFor(() => {
      expect(screen.getByText('اسم الشركة')).toBeDefined();
    });

    const companyCheckbox = screen.getByLabelText('اسم الشركة');
    expect(companyCheckbox).not.toBeChecked();

    await act(async () => {
      fireEvent.click(companyCheckbox);
    });

    await waitFor(() => {
      expect(companyCheckbox).toBeChecked();
    });

    await waitFor(() => {
      expect(screen.getAllByText(/2 \/ 5 rows/).length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Acme Corp')).toBeDefined();
    expect(screen.getByText('Beta Ltd')).toBeDefined();
  });

  test('filters rows by multiple conditions with AND logic', async () => {
    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await waitFor(() => {
      expect(screen.getByText('اسم الشركة')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('اسم الشركة'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/2 \/ 5 rows/).length).toBeGreaterThan(0);
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('الموبايل'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/1 \/ 5 rows/).length).toBeGreaterThan(0);
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('البريد الإلكتروني'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/1 \/ 5 rows/).length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Acme Corp')).toBeDefined();
    expect(screen.queryByText('Beta Ltd')).not.toBeInTheDocument();
  });

  test('resets smart filters and shows all rows', async () => {
    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'UAE_Raw_Buyers.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'Company', '2': 'Mobile', '3': 'Email' },
          { '1': 'Acme Corp', '2': '0501234567', '3': 'info@acme.com' },
          { '1': '', '2': '0507654321', '3': 'test@example.com' },
          { '1': 'Beta Ltd', '2': '', '3': 'beta@beta.com' },
          { '1': 'Gamma Inc', '2': '0509999999', '3': 'gamma@gamma.com' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('اسم الشركة'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/3 \/ 5 rows/).length).toBeGreaterThan(0);
    });

    await act(async () => {
      fireEvent.click(screen.getByText('إعادة تعيين'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/4 \/ 5 rows/).length).toBeGreaterThan(0);
    });
  });

  test('maps numeric column keys to headers and filters by company name', async () => {
    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('اسم الشركة'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/2 \/ 5 rows/).length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Acme Corp')).toBeDefined();
    expect(screen.getByText('Beta Ltd')).toBeDefined();
  });

  test('maps numeric column keys to headers and filters by mobile', async () => {
    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('الموبايل'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/2 \/ 5 rows/).length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Acme Corp')).toBeDefined();
    expect(screen.queryByText('Beta Ltd')).not.toBeInTheDocument();
  });

  test('detects header after intro rows and filters by company name', async () => {
    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'UAE_Raw_Buyers.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'This file contains buyer data', '2': 'Generated from public sources', '3': '', '4': '' },
          { '1': 'Note: Blank means unavailable', '2': '', '3': '', '4': '' },
          { '1': 'Company Name', '2': 'Mobile', '3': 'Email', '4': 'Address' },
          { '1': 'Acme Corp', '2': '0501234567', '3': 'info@acme.com', '4': 'Dubai' },
          { '1': '', '2': '0507654321', '3': 'test@example.com', '4': '' },
          { '1': 'Beta Ltd', '2': '', '3': 'beta@beta.com', '4': '' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('اسم الشركة'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/2 \/ 6 rows/).length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Acme Corp')).toBeDefined();
    expect(screen.getByText('Beta Ltd')).toBeDefined();
  });

  test('detects header after intro rows and filters by mobile', async () => {
    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'UAE_Raw_Buyers.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'Header row at index 1', '2': '', '3': '', '4': '' },
          { '1': 'Company Name', '2': 'Mobile', '3': 'Email', '4': 'Address' },
          { '1': 'Acme Corp', '2': '0501234567', '3': 'info@acme.com', '4': 'Dubai' },
          { '1': '', '2': '0507654321', '3': 'test@example.com', '4': '' },
          { '1': 'Beta Ltd', '2': '', '3': 'beta@beta.com', '4': '' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('الموبايل'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/2 \/ 5 rows/).length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Acme Corp')).toBeDefined();
    expect(screen.queryByText('Beta Ltd')).not.toBeInTheDocument();
  });

  test('detects Arabic header after intro rows and filters by company and mobile', async () => {
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
                name: 'UAE_Fresh_Fruit_Vegetable_Buyers_MAX_FREE_EVIDENCE.xlsx',
                source: 'Google Drive',
                sheet_count: 1,
                row_count: 6,
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

    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'UAE_Fresh_Fruit_Vegetable_Buyers_MAX_FREE_EVIDENCE.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'This file contains buyer data', '2': 'Generated from public sources', '3': '', '4': '' },
          { '1': 'Note: Blank means unavailable', '2': '', '3': '', '4': '' },
          { '1': 'الشركة', '2': 'الجوال', '3': 'البريد الإلكتروني', '4': 'العنوان' },
          { '1': 'Acme Corp', '2': '0501234567', '3': 'info@acme.com', '4': 'Dubai' },
          { '1': '', '2': '0507654321', '3': 'test@example.com', '4': '' },
          { '1': 'Beta Ltd', '2': '', '3': 'beta@beta.com', '4': '' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Fresh_Fruit_Vegetable_Buyers_MAX_FREE_EVIDENCE.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('اسم الشركة'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/2 \/ 6 rows/).length).toBeGreaterThan(0);
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('الموبايل'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/1 \/ 6 rows/).length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Acme Corp')).toBeDefined();
    expect(screen.queryByText('Beta Ltd')).not.toBeInTheDocument();
  });

  test('detects Arabic header with slash and filters by email', async () => {
    mockedListPotentialCustomerCountries.mockResolvedValue({
      data: {
        countries: [
          {
            id: 'country-oman',
            name: 'Oman',
            file_count: 1,
            files: [
              {
                id: 'file-oman-001',
                name: 'Oman_Buyers.xlsx',
                source: 'Google Drive',
                sheet_count: 1,
                row_count: 4,
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

    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'Oman_Buyers.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'الشركة', '2': 'هاتف عمومي/جوال', '3': 'البريد الإلكتروني', '4': 'العنوان' },
          { '1': 'Acme Corp', '2': '0501234567', '3': 'info@acme.com', '4': 'Dubai' },
          { '1': '', '2': '0507654321', '3': 'test@example.com', '4': '' },
          { '1': 'Beta Ltd', '2': '', '3': 'beta@beta.com', '4': '' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('Oman')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Oman'));
    });

    await waitFor(() => {
      expect(screen.getByText('Oman_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('البريد الإلكتروني'));
    });

    await waitFor(() => {
      expect(screen.getAllByText(/3 \/ 4 rows/).length).toBeGreaterThan(0);
    });

    expect(screen.getByText('Acme Corp')).toBeDefined();
    expect(screen.getByText('Beta Ltd')).toBeDefined();
  });

  test('filters by Email ID and E-mail Address column names', async () => {
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
                name: 'UAE_Buyers_Email_Variants.xlsx',
                source: 'Google Drive',
                sheet_count: 1,
                row_count: 5,
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

    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'UAE_Buyers_Email_Variants.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'Company Name', '2': 'Email ID', '3': 'E-mail Address', '4': 'Mobile No.' },
          { '1': 'Acme Corp', '2': 'info@acme.com', '3': 'contact@acme.com', '4': '0501234567' },
          { '1': 'Beta Ltd', '2': 'beta@beta.com', '3': '', '4': '0507654321' },
          { '1': 'Gamma Inc', '2': '', '3': 'gamma@gamma.com', '4': '' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Buyers_Email_Variants.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('البريد الإلكتروني'));
    });

    await waitFor(() => {
      expect(screen.getByText('Acme Corp')).toBeDefined();
    });

    expect(screen.getByText('Beta Ltd')).toBeDefined();
    expect(screen.getByText('Gamma Inc')).toBeDefined();
  });

  test('filters by Address Line and WhatsApp Contact column names', async () => {
    mockedListPotentialCustomerCountries.mockResolvedValue({
      data: {
        countries: [
          {
            id: 'country-saudi',
            name: 'Saudi Arabia',
            file_count: 1,
            files: [
              {
                id: 'file-saudi-001',
                name: 'Saudi_Buyers_Address_WhatsApp.xlsx',
                source: 'Google Drive',
                sheet_count: 1,
                row_count: 4,
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

    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'Saudi_Buyers_Address_WhatsApp.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'Company', '2': 'Address Line', '3': 'WhatsApp Contact', '4': 'Site URL' },
          { '1': 'Acme Corp', '2': 'Riyadh', '3': '0501234567', '4': 'https://acme.com' },
          { '1': 'Beta Ltd', '2': 'Jeddah', '3': '', '4': 'https://beta.com' },
          { '1': 'Gamma Inc', '2': '', '3': '0509999999', '4': '' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('Saudi Arabia')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Saudi Arabia'));
    });

    await waitFor(() => {
      expect(screen.getByText('Saudi_Buyers_Address_WhatsApp.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('العنوان'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('WhatsApp'));
    });

    await waitFor(() => {
      expect(screen.getByText('Acme Corp')).toBeDefined();
    });

    expect(screen.queryByText('Beta Ltd')).not.toBeInTheDocument();
    expect(screen.queryByText('Gamma Inc')).not.toBeInTheDocument();
  });

  test('filters by Site URL and Website Link column names', async () => {
    mockedListPotentialCustomerCountries.mockResolvedValue({
      data: {
        countries: [
          {
            id: 'country-jordan',
            name: 'Jordan',
            file_count: 1,
            files: [
              {
                id: 'file-jordan-001',
                name: 'Jordan_Buyers_Website.xlsx',
                source: 'Google Drive',
                sheet_count: 1,
                row_count: 4,
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

    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'Jordan_Buyers_Website.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'Company', '2': 'Website Link', '3': 'Site URL', '4': 'Web URL' },
          { '1': 'Acme Corp', '2': 'https://acme.com', '3': 'https://acme.com/jo', '4': 'http://acme.net' },
          { '1': 'Beta Ltd', '2': '', '3': 'https://beta.com', '4': '' },
          { '1': 'Gamma Inc', '2': 'https://gamma.com', '3': '', '4': '' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('Jordan')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Jordan'));
    });

    await waitFor(() => {
      expect(screen.getByText('Jordan_Buyers_Website.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('🎯 فلترة ذكية'));
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('الموقع الإلكتروني'));
    });

    await waitFor(() => {
      expect(screen.getByText('Acme Corp')).toBeDefined();
    });

    expect(screen.getByText('Beta Ltd')).toBeDefined();
    expect(screen.getByText('Gamma Inc')).toBeDefined();
  });

  test('marks contact-ready rows first and opens company detail modal', async () => {
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
                sheet_count: 1,
                row_count: 5,
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

    mockedGetPotentialCustomerFileContent.mockResolvedValue({
      data: {
        file_name: 'UAE_Raw_Buyers.xlsx',
        sheets: [{ name: 'Sheet1' }],
        active_sheet: 'Sheet1',
        rows: [
          { '1': 'Company Name', '2': 'Contact Person', '3': 'Mobile', '4': 'WhatsApp', '5': 'Email', '6': 'Address', '7': 'City', '8': 'Country', '9': 'Public address', '10': 'Category match', '11': 'Source URL' },
          { '1': 'Acme Corp', '2': 'John Doe', '3': '0501234567', '4': '', '5': 'info@acme.com', '6': 'Dubai', '7': 'Dubai', '8': 'UAE', '9': 'Knowledge Village', '10': 'High', '11': 'https://example.com/acme' },
          { '1': 'Beta Ltd', '2': '', '3': '', '4': '', '5': 'beta@beta.com', '6': '', '7': '', '8': '', '9': '', '10': '', '11': '' },
          { '1': 'Gamma Inc', '2': 'Jane Smith', '3': '0509999999', '4': '0509999999', '5': '', '6': 'Abu Dhabi', '7': 'Abu Dhabi', '8': 'UAE', '9': 'Masdar City', '10': 'Medium', '11': '' },
        ],
      },
    } as any);

    await act(async () => {
      renderWithProviders(<PotentialCustomers />);
    });

    await waitFor(() => {
      expect(screen.getByText('UAE')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('UAE'));
    });

    await waitFor(() => {
      expect(screen.getByText('UAE_Raw_Buyers.xlsx')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Open'));
    });

    await waitFor(() => {
      expect(screen.getByText('🎯 فلترة ذكية')).toBeDefined();
    });

    await waitFor(() => {
      expect(screen.getByText('Acme Corp')).toBeDefined();
      expect(screen.getByText('Gamma Inc')).toBeDefined();
      expect(screen.getByText('Beta Ltd')).toBeDefined();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Acme Corp'));
    });

    await waitFor(() => {
      expect(screen.getByText('جاهز للتواصل')).toBeDefined();
    });

    expect(screen.getAllByText('Acme Corp').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('0501234567').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('info@acme.com').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Dubai').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('1 / 3')).toBeDefined();
    expect(screen.getAllByText('John Doe').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('UAE').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Knowledge Village').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('High').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('https://example.com/acme').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(1);

    const copyButtons = screen.getAllByText('نسخ');
    expect(copyButtons.length).toBeGreaterThanOrEqual(1);
    await act(async () => {
      fireEvent.click(copyButtons[0]);
    });
    await waitFor(() => {
      expect(screen.getByText('تم النسخ')).toBeDefined();
    });

    const emptyFields = screen.getAllByText('—');
    expect(emptyFields.length).toBeGreaterThanOrEqual(1);
    emptyFields.forEach((emptyField) => {
      const card = emptyField.closest('div[class*="rounded-lg border"]');
      if (card) {
        expect(card.textContent).not.toContain('نسخ');
      }
    });

    await act(async () => {
      fireEvent.click(screen.getByLabelText('Next'));
    });

    await waitFor(() => {
      expect(screen.getAllByText('Gamma Inc').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText('جاهز للتواصل')).toBeDefined();
    expect(screen.getByText('2 / 3')).toBeDefined();

    await act(async () => {
      fireEvent.click(screen.getByLabelText('Next'));
    });

    await waitFor(() => {
      expect(screen.getAllByText('Beta Ltd').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText('بيانات غير مكتملة للتواصل')).toBeDefined();
    expect(screen.getByText('3 / 3')).toBeDefined();
    expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(8);

    await act(async () => {
      fireEvent.click(screen.getByLabelText('Previous'));
    });

    await waitFor(() => {
      expect(screen.getAllByText('Gamma Inc').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText('جاهز للتواصل')).toBeDefined();
    expect(screen.getByText('2 / 3')).toBeDefined();

    await act(async () => {
      fireEvent.click(screen.getByLabelText('Previous'));
    });

    await waitFor(() => {
      expect(screen.getAllByText('Acme Corp').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText('1 / 3')).toBeDefined();
  });
});
