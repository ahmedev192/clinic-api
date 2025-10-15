import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Endpoints
export const appointmentsApi = {
  list: (params?: any) => api.get('/appointments/', { params }),
  get: (id: string) => api.get(`/appointments/${id}/`),
  create: (data: any) => api.post('/appointments/', data),
  update: (id: string, data: any) => api.patch(`/appointments/${id}/`, data),
  delete: (id: string) => api.delete(`/appointments/${id}/`),
  search: (params: any) => api.get('/appointments/search/', { params }),
  statistics: () => api.get('/appointments/statistics/'),
  reschedule: (id: string, data: any) => api.post(`/appointments/${id}/reschedule/`, data),
  cancel: (id: string, data: any) => api.post(`/appointments/${id}/cancel/`, data),
  complete: (id: string) => api.post(`/appointments/${id}/complete/`),
};

export const doctorAvailabilityApi = {
  list: (params?: any) => api.get('/doctor-availability/', { params }),
  get: (id: string) => api.get(`/doctor-availability/${id}/`),
  create: (data: any) => api.post('/doctor-availability/', data),
  update: (id: string, data: any) => api.patch(`/doctor-availability/${id}/`, data),
  delete: (id: string) => api.delete(`/doctor-availability/${id}/`),
  availableSlots: (params: any) => api.get('/doctor-availability/available-slots/', { params }),
  blockSlot: (id: string, data: any) => api.post(`/doctor-availability/${id}/block/`, data),
};

export const waitingListApi = {
  list: (params?: any) => api.get('/waiting-list/', { params }),
  get: (id: string) => api.get(`/waiting-list/${id}/`),
  create: (data: any) => api.post('/waiting-list/', data),
  update: (id: string, data: any) => api.patch(`/waiting-list/${id}/`, data),
  delete: (id: string) => api.delete(`/waiting-list/${id}/`),
  promote: (id: string, data: any) => api.post(`/waiting-list/${id}/promote/`, data),
};

export const remindersApi = {
  list: (params?: any) => api.get('/reminders/', { params }),
  get: (id: string) => api.get(`/reminders/${id}/`),
  create: (data: any) => api.post('/reminders/', data),
  update: (id: string, data: any) => api.patch(`/reminders/${id}/`, data),
  delete: (id: string) => api.delete(`/reminders/${id}/`),
  send: (id: string) => api.post(`/reminders/${id}/send/`),
};

export const authApi = {
  login: (credentials: { username: string; password: string }) => 
    api.post('/auth/login/', credentials),
  logout: () => api.post('/auth/logout/'),
  refresh: (token: string) => api.post('/auth/refresh/', { token }),
};
