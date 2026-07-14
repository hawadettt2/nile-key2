import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

const rawApi = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let refreshQueue: Array<{ resolve: (token: string) => void; reject: (err: unknown) => void }> = [];

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (token) => {
              error.config.headers.Authorization = `Bearer ${token}`;
              resolve(api(error.config));
            },
            reject: (err) => {
              reject(err);
            }
          });
        });
      }

      isRefreshing = true;
      try {
        const storedRefreshToken = localStorage.getItem('refresh_token');
        if (!storedRefreshToken) throw new Error('No refresh token');

        const { data } = await rawApi.post('/api/v1/auth/refresh', null, {
          headers: { Authorization: `Bearer ${storedRefreshToken}` },
        });
        const newAccessToken = data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }

        refreshQueue.forEach((item) => item.resolve(newAccessToken));
        refreshQueue = [];

        error.config.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(error.config);
      } catch (refreshError) {
        refreshQueue.forEach((item) => item.reject(refreshError));
        refreshQueue = [];
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export const login = (username: string, password: string) =>
  api.post('/api/v1/auth/login', { username, password });
export const register = (data: Record<string, string>) =>
  api.post('/api/v1/auth/register', data);
export const getMe = () => api.get('/api/v1/auth/me');
export const updateMe = (data: Record<string, unknown>) => api.put('/api/v1/auth/me', data);
export const refreshToken = (data: Record<string, unknown>) =>
  rawApi.post('/api/v1/auth/refresh', null, { headers: { Authorization: `Bearer ${data.refresh_token}` } });

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
export const getShipmentLabel = (id: number) => api.get(`/api/v1/shipping/shipments/${id}/label`);
export const trackShipment = (trackingId: string) => api.get(`/api/v1/shipping/track/${trackingId}`);
export const getShippingRates = (data: Record<string, unknown>) => api.get('/api/v1/shipping/rates', { data });

export const listInvoices = (params?: Record<string, unknown>) => api.get('/api/v1/invoices', { params });
export const getInvoice = (id: number) => api.get(`/api/v1/invoices/${id}`);
export const createInvoice = (data: Record<string, unknown>) => api.post('/api/v1/invoices', data);
export const updateInvoice = (id: number, data: Record<string, unknown>) => api.put(`/api/v1/invoices/${id}`, data);
export const validateInvoice = (id: number) => api.post(`/api/v1/invoices/${id}/validate`);
export const cancelInvoice = (id: number) => api.post(`/api/v1/invoices/${id}/cancel`);
export const getInvoiceStatus = (id: number) => api.get(`/api/v1/invoices/${id}/status`);

export const listHSCodes = (params?: Record<string, unknown>) => api.get('/api/v1/customs/hs-codes', { params });
export const getHSCode = (id: number) => api.get(`/api/v1/customs/hs-codes/${id}`);
export const calculateDuties = (data: Record<string, unknown>) => api.post('/api/v1/customs/calculate-duties', data);
export const listDeclarations = (params?: Record<string, unknown>) => api.get('/api/v1/customs/declarations', { params });
export const createDeclaration = (data: Record<string, unknown>) => api.post('/api/v1/customs/declarations', data);
export const getDeclaration = (id: number) => api.get(`/api/v1/customs/declarations/${id}`);
export const updateDeclaration = (id: number, data: Record<string, unknown>) => api.put(`/api/v1/customs/declarations/${id}`, data);
export const submitDeclaration = (id: number) => api.post(`/api/v1/customs/declarations/${id}/submit`);

export const listDocuments = (params?: Record<string, unknown>) => api.get('/api/v1/documents', { params });
export const createDocument = (data: Record<string, unknown>) => api.post('/api/v1/documents', data);
export const getDocument = (id: number) => api.get(`/api/v1/documents/${id}`);
export const updateDocument = (id: number, data: Record<string, unknown>) => api.put(`/api/v1/documents/${id}`, data);
export const uploadDocument = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/v1/documents/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
};
export const deleteDocument = (id: number) => api.delete(`/api/v1/documents/${id}`);

export const listResources = (params?: Record<string, unknown>) => api.get('/api/v1/resources', { params });
export const searchResources = (q: string) => api.get('/api/v1/resources/search', { params: { q } });
export const createResource = (data: Record<string, unknown>) => api.post('/api/v1/resources', data);
export const getResource = (id: number) => api.get(`/api/v1/resources/${id}`);
export const updateResource = (id: number, data: Record<string, unknown>) => api.put(`/api/v1/resources/${id}`, data);
export const deleteResource = (id: number) => api.delete(`/api/v1/resources/${id}`);

export const search = (query: string, entityType?: string) =>
  api.get('/api/v1/search', { params: { query, entity_type: entityType } });
export const getDashboard = () => api.get('/api/v1/dashboard');
export const sendNotification = (data: { template_id: number; recipient: string; variables?: Record<string, unknown> }) =>
  api.post('/api/v1/notifications/send', data);
export const getAuditLogs = (params?: Record<string, unknown>) =>
  api.get('/api/v1/audit/logs', { params });

export default api;
