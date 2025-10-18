// frontend/src/services/apiClient.ts - UPDATED with better error handling
import axios from 'axios';

// Force HTTPS for production, localhost for development
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 
  (window.location.hostname === 'localhost' ? 'http://localhost:8001' : 'https://validatus-backend-ssivkqhvhq-uc.a.run.app');

console.log('API Client initialized with base URL:', API_BASE_URL);
console.log('API Client timeout set to:', 90000, 'ms (90 seconds)');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 90000, // Increased to 90 seconds for heavy analysis operations - v2.1
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false, // Disable credentials for CORS compatibility
});

// Request interceptor for adding auth token and logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making API request: ${config.method?.toUpperCase()} ${config.url}`);
    
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors and logging
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API response: ${response.status} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });

    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    
    // Provide more detailed error messages
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      error.message = 'Network error: Unable to connect to the server. Please check your internet connection.';
    } else if (error.response?.status >= 500) {
      error.message = `Server error (${error.response.status}): ${error.response.data?.detail || 'Internal server error'}`;
    } else if (error.response?.status >= 400) {
      error.message = `Client error (${error.response.status}): ${error.response.data?.detail || 'Bad request'}`;
    } else if (error.code === 'ECONNABORTED') {
      error.message = 'Request timeout: The server took too long to respond.';
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
