import axios, { AxiosInstance } from 'axios';

// Configure your Django API base URL here
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Token ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Patients API
  async getPatients(params?: { page?: number; search?: string }) {
    const { data } = await this.api.get('/patients/', { params });
    return data;
  }

  async getPatient(id: string) {
    const { data } = await this.api.get(`/patients/${id}/`);
    return data;
  }

  async createPatient(patientData: any) {
    const { data } = await this.api.post('/patients/', patientData);
    return data;
  }

  async updatePatient(id: string, patientData: any) {
    const { data } = await this.api.put(`/patients/${id}/`, patientData);
    return data;
  }

  async deletePatient(id: string) {
    await this.api.delete(`/patients/${id}/`);
  }

  async searchPatients(query: string) {
    const { data } = await this.api.get('/patients/search/', { params: { q: query } });
    return data;
  }

  async getPatientStatistics() {
    const { data } = await this.api.get('/patients/statistics/');
    return data;
  }

  // Medical History API
  async getMedicalHistory(patientId: string) {
    const { data } = await this.api.get('/medical-history/', { params: { patient: patientId } });
    return data;
  }

  async createMedicalHistory(historyData: any) {
    const { data } = await this.api.post('/medical-history/', historyData);
    return data;
  }

  async updateMedicalHistory(id: string, historyData: any) {
    const { data } = await this.api.put(`/medical-history/${id}/`, historyData);
    return data;
  }

  async deleteMedicalHistory(id: string) {
    await this.api.delete(`/medical-history/${id}/`);
  }

  // Allergies API
  async getAllergies(patientId: string) {
    const { data } = await this.api.get('/allergies/', { params: { patient: patientId } });
    return data;
  }

  async createAllergy(allergyData: any) {
    const { data } = await this.api.post('/allergies/', allergyData);
    return data;
  }

  async deleteAllergy(id: string) {
    await this.api.delete(`/allergies/${id}/`);
  }

  // Chronic Conditions API
  async getChronicConditions(patientId: string) {
    const { data } = await this.api.get('/chronic-conditions/', { params: { patient: patientId } });
    return data;
  }

  async createChronicCondition(conditionData: any) {
    const { data } = await this.api.post('/chronic-conditions/', conditionData);
    return data;
  }

  async deleteChronicCondition(id: string) {
    await this.api.delete(`/chronic-conditions/${id}/`);
  }

  // Documents API
  async getDocuments(patientId: string) {
    const { data } = await this.api.get('/documents/', { params: { patient: patientId } });
    return data;
  }

  async uploadDocument(formData: FormData) {
    const { data } = await this.api.post('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }

  async verifyDocument(id: string) {
    const { data } = await this.api.patch(`/documents/${id}/`, { is_verified: true });
    return data;
  }

  async unverifyDocument(id: string) {
    const { data } = await this.api.patch(`/documents/${id}/`, { is_verified: false });
    return data;
  }

  async deleteDocument(id: string) {
    await this.api.delete(`/documents/${id}/`);
  }

  // Audit Logs API
  async getAuditLogs(params?: { page?: number; patient?: string }) {
    const { data } = await this.api.get('/audit-logs/', { params });
    return data;
  }
}

export default new ApiService();
