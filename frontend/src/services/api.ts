// frontend/src/services/api.ts

import axios, { AxiosInstance, AxiosError } from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://validatus-backend-ssivkqhvhq-uc.a.run.app';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 90000, // 90 seconds for heavy analysis operations
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        console.error('❌ API Error:', {
          url: error.config?.url,
          status: error.response?.status,
          message: error.message,
          data: error.response?.data
        });
        return Promise.reject(error);
      }
    );
  }

  // Health Check
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Get Results for Segment (using actual endpoint)
  async getSegmentResults(topic: string, segment: string) {
    try {
      // Try new data-driven endpoint first
      const response = await this.client.get(`/api/v3/data-driven-results/segment/${topic}/${segment}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        // Fallback to enhanced segment results
        console.warn('⚠️ Data-driven endpoint not found, trying enhanced endpoint...');
        const response = await this.client.get(`/api/v3/enhanced-segment-results/${topic}/${segment}`);
        return response.data;
      }
      throw error;
    }
  }

  // Get Results Generation Status
  async getResultsStatus(sessionId: string) {
    const response = await this.client.get(`/api/v3/data-driven-results/status/${sessionId}`);
    return response.data;
  }

  // Trigger Results Generation
  async triggerResultsGeneration(sessionId: string, topic: string) {
    const response = await this.client.post(`/api/v3/data-driven-results/generate/${sessionId}/${topic}`);
    return response.data;
  }

  // Get Complete Analysis
  async getCompleteAnalysis(topic: string) {
    const response = await this.client.get(`/api/v3/results/${topic}`);
    return response.data;
  }

  // Expose client for direct access
  get axiosClient() {
    return this.client;
  }
}

export const apiService = new ApiService();
export default apiService;
