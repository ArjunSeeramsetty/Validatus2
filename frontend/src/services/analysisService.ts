import { apiClient } from './apiClient';

export interface Topic {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'processing';
  created_at: string;
  updated_at: string;
  url_count: number;
  knowledge_count: number;
}

export interface AnalysisSession {
  id: string;
  topic: string;
  user_id: string;
  status: 'created' | 'running' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  updated_at: string;
  results?: any;
  enhanced_analytics: boolean;
}

export interface SystemStatus {
  system_status: string;
  core_services_count: number;
  enhanced_services_count: number;
  phase_c_services_count: number;
  phase_e_services_count: number;
  available_services: {
    core: string[];
    enhanced: string[];
    phase_c: string[];
    phase_e: string[];
  };
  feature_flags: Record<string, boolean>;
  enabled_phases: string[];
}

export class AnalysisService {
  // System & Health
  static async getSystemStatus(): Promise<SystemStatus> {
    const response = await apiClient.get('/api/v3/system/status');
    return response.data;
  }

  static async getHealthCheck() {
    const response = await apiClient.get('/health');
    return response.data;
  }

  // Topics Management
  static async getTopics(): Promise<{ topics: Topic[] }> {
    const response = await apiClient.get('/api/v3/topics');
    return response.data;
  }

  static async createTopic(
    topic: string, 
    urls: string[], 
    searchQueries?: string[]
  ): Promise<{ success: boolean; topic_id: string; message: string }> {
    const response = await apiClient.post('/api/v3/topics/create', null, {
      params: {
        topic,
        urls: urls.join(','),
        search_queries: searchQueries?.join(',')
      }
    });
    return response.data;
  }

  // Analysis Sessions
  static async createAnalysisSession(
    topic: string,
    userId: string,
    analysisParameters?: Record<string, any>,
    useEnhancedAnalytics: boolean = false
  ): Promise<{
    success: boolean;
    session_id: string;
    topic: string;
    user_id: string;
    enhanced_analytics: boolean;
    message: string;
  }> {
    const response = await apiClient.post('/api/v3/analysis/sessions/create', {
      topic,
      user_id: userId,
      analysis_parameters: analysisParameters,
      use_enhanced_analytics: useEnhancedAnalytics
    });
    return response.data;
  }

  // Enhanced Analysis (Phase B)
  static async runEnhancedAnalysis(
    sessionId: string,
    topic: string,
    userId: string,
    enhancedOptions?: Record<string, any>
  ) {
    const response = await apiClient.post('/api/v3/analysis/enhanced', {
      session_id: sessionId,
      topic,
      user_id: userId,
      enhanced_options: enhancedOptions
    });
    return response.data;
  }

  // Comprehensive Analysis (Phase C)
  static async runComprehensiveAnalysis(
    sessionId: string,
    topic: string,
    userId: string,
    analysisOptions?: Record<string, any>
  ) {
    const response = await apiClient.post('/api/v3/analysis/comprehensive', {
      session_id: sessionId,
      topic,
      user_id: userId,
      analysis_options: analysisOptions
    });
    return response.data;
  }

  // Phase E - Advanced Orchestration
  static async getOrchestrationHealth() {
    try {
      const response = await apiClient.get('/api/v3/orchestration/health');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 503) {
        return { success: false, message: 'Phase E orchestration not enabled' };
      }
      throw error;
    }
  }

  static async getCachePerformance() {
    try {
      const response = await apiClient.get('/api/v3/cache/performance');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 503) {
        return { success: false, message: 'Multi-level cache not enabled' };
      }
      throw error;
    }
  }

  static async invalidateCache(pattern?: string) {
    const response = await apiClient.post('/api/v3/cache/invalidate', {
      pattern: pattern || '*'
    });
    return response.data;
  }

  static async getEnhancedMetrics() {
    try {
      const response = await apiClient.get('/api/v3/optimization/enhanced-metrics');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 503) {
        return { success: false, message: 'Phase E enhanced optimization not enabled' };
      }
      throw error;
    }
  }
}

export default AnalysisService;
