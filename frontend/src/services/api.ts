import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const login = (username: string, password: string) =>
  api.post('/api/v1/auth/login', { username, password });
export const register = (data: Record<string, string>) =>
  api.post('/api/v1/auth/register', data);
export const getMe = () => api.get('/api/v1/auth/me');

export const listSuppliers = (params?: Record<string, unknown>) => api.get('/api/v1/suppliers', { params });
export const getSupplier = (id: number) => api.get(`/api/v1/suppliers/${id}`);
export const createSupplier = (data: Record<string, unknown>) => api.post('/api/v1/suppliers', data);
export const updateSupplier = (id: number, data: Record<string, unknown>) => api.put(`/api/v1/suppliers/${id}`, data);
export const deleteSupplier = (id: number) => api.delete(`/api/v1/suppliers/${id}`);

export const listCustomers = (params?: Record<string, unknown>) => api.get('/api/v1/customers', { params });
export const getCustomer = (id: number) => api.get(`/api/v1/customers/${id}`);
export const createCustomer = (data: Record<string, unknown>) => api.post('/api/v1/customers', data);
export const updateCustomer = (id: number, data: Record<string, unknown>) => api.put(`/api/v1/customers/${id}`, data);
export const deleteCustomer = (id: number) => api.delete(`/api/v1/customers/${id}`);
export const importCustomers = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/v1/customers/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
};

export const listShipments = (params?: Record<string, unknown>) => api.get('/api/v1/shipping/shipments', { params });
export const getShipment = (id: number) => api.get(`/api/v1/shipping/shipments/${id}`);
export const createShipment = (data: Record<string, unknown>) => api.post('/api/v1/shipping/shipments', data);
export const updateShipment = (id: number, data: Record<string, unknown>) => api.put(`/api/v1/shipping/shipments/${id}`, data);
export const getShippingRates = (data: Record<string, unknown>) => api.get('/api/v1/shipping/rates', { params: data });

export const listInvoices = (params?: Record<string, unknown>) => api.get('/api/v1/invoices', { params });
export const getInvoice = (id: number) => api.get(`/api/v1/invoices/${id}`);
export const createInvoice = (data: Record<string, unknown>) => api.post('/api/v1/invoices', data);
export const validateInvoice = (id: number) => api.post(`/api/v1/invoices/${id}/validate`);
export const cancelInvoice = (id: number) => api.post(`/api/v1/invoices/${id}/cancel`);

export const listHSCodes = (params?: Record<string, unknown>) => api.get('/api/v1/customs/hs-codes', { params });
export const calculateDuties = (data: Record<string, unknown>) => api.post('/api/v1/customs/calculate-duties', data);
export const listDeclarations = (params?: Record<string, unknown>) => api.get('/api/v1/customs/declarations', { params });
export const createDeclaration = (data: Record<string, unknown>) => api.post('/api/v1/customs/declarations', data);

export const listDocuments = (params?: Record<string, unknown>) => api.get('/api/v1/documents', { params });
export const createDocument = (data: Record<string, unknown>) => api.post('/api/v1/documents', data);
export const uploadDocument = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/v1/documents/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
};
export const deleteDocument = (id: number) => api.delete(`/api/v1/documents/${id}`);

export const listResources = (params?: Record<string, unknown>) => api.get('/api/v1/resources', { params });
export const searchResources = (q: string) => api.get('/api/v1/resources/search', { params: { q } });
export const createResource = (data: Record<string, unknown>) => api.post('/api/v1/resources', data);
export const deleteResource = (id: number) => api.delete(`/api/v1/resources/${id}`);

export default api;
