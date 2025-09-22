import axios from 'axios';
import toast from 'react-hot-toast';

// Base API configuration
// Use relative URL by default so it works behind the same origin in production and via CRA proxy in development.
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for errors and retry
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Retry once on network error
    if (error.message.includes('Network Error') && !originalRequest._retry) {
      originalRequest._retry = true;
      toast.error('Network issue. Retrying...');
      await new Promise(res => setTimeout(res, 1000));
      return api(originalRequest);
    }

    const message = error.response?.data?.message || error.message || 'An error occurred';

    // Handle unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }

    toast.error(message);
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

// Tourist endpoints
export const touristAPI = {
  getProfile: (id) => api.get(id ? `/tourists/${id}` : '/tourists/me'),
  updateProfile: (updates) => api.put('/tourists/me', updates),
  logLocation: (locationData) => api.post('/tourists/me/location', locationData),
};

// Alert endpoints
export const alertAPI = {
  panic: (alertData) => api.post('/alerts/panic', alertData),
  getAlerts: () => api.get('/alerts'),
};

// Geofence endpoints
export const geofenceAPI = {
  checkGeofence: (coordinates) => api.post('/geofence/check', coordinates),
};

// Anomaly endpoints
export const anomalyAPI = {
  checkAnomalies: (touristId) => api.get(`/anomaly/${touristId}/check`),
};

export default api;