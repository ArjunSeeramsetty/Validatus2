/**
 * Topic Service for Frontend
 * Handles communication with backend topic API
 */
import { apiClient } from './apiClient';

export interface TopicConfig {
  session_id: string;
  topic: string;
  description: string;
  search_queries: string[];
  initial_urls: string[];
  analysis_type: 'standard' | 'comprehensive';
  user_id: string;
  created_at: string;
  updated_at: string;
  status: 'draft' | 'created' | 'in_progress' | 'completed' | 'archived';
  metadata: Record<string, any>;
}

export interface TopicCreateRequest {
  title: string;
  description: string;
  analysis_type: 'standard' | 'comprehensive';
  user_id: string;
}

export interface TopicUpdateRequest {
  topic?: string;
  description?: string;
  search_queries?: string[];
  initial_urls?: string[];
  analysis_type?: 'standard' | 'comprehensive';
  status?: 'draft' | 'created' | 'in_progress' | 'completed' | 'archived';
  metadata?: Record<string, any>;
}

export interface TopicListResponse {
  topics: TopicConfig[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface TopicSearchRequest {
  query?: string;
  analysis_type?: 'standard' | 'comprehensive';
  status?: 'draft' | 'created' | 'in_progress' | 'completed' | 'archived';
  user_id?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

class TopicService {
  private baseUrl = '/api/v3/topics';

  /**
   * Create a new topic
   */
  async createTopic(request: TopicCreateRequest): Promise<TopicConfig> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/create`, request);
      return response.data;
    } catch (error: any) {
      console.error('Failed to create topic:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create topic');
    }
  }

  /**
   * Get a topic by session ID
   */
  async getTopic(sessionId: string): Promise<TopicConfig | null> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/${sessionId}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      console.error('Failed to get topic:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get topic');
    }
  }

  /**
   * Update an existing topic
   */
  async updateTopic(sessionId: string, request: TopicUpdateRequest): Promise<TopicConfig | null> {
    try {
      const response = await apiClient.put(`${this.baseUrl}/${sessionId}`, request);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      console.error('Failed to update topic:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update topic');
    }
  }

  /**
   * Delete a topic
   */
  async deleteTopic(sessionId: string): Promise<boolean> {
    try {
      await apiClient.delete(`${this.baseUrl}/${sessionId}`);
      return true;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false;
      }
      console.error('Failed to delete topic:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete topic');
    }
  }

  /**
   * List topics with pagination
   */
  async listTopics(
    page: number = 1,
    pageSize: number = 20,
    sortBy: string = 'created_at',
    sortOrder: 'asc' | 'desc' = 'desc'
  ): Promise<TopicListResponse> {
    try {
      const response = await apiClient.get(this.baseUrl, {
        params: {
          page,
          page_size: pageSize,
          sort_by: sortBy,
          sort_order: sortOrder
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to list topics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to list topics');
    }
  }

  /**
   * Search topics with filters
   */
  async searchTopics(request: TopicSearchRequest): Promise<TopicListResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/search`, request);
      return response.data;
    } catch (error: any) {
      console.error('Failed to search topics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to search topics');
    }
  }

  /**
   * Get topic statistics
   */
  async getTopicStats(): Promise<{
    total_topics: number;
    topics_by_status: Record<string, number>;
    topics_by_type: Record<string, number>;
  }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/stats/overview`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get topic stats:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get topic stats');
    }
  }

  /**
   * Get available analysis types
   */
  async getAnalysisTypes(): Promise<string[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/analysis-types/`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get analysis types:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get analysis types');
    }
  }

  /**
   * Get available topic statuses
   */
  async getTopicStatuses(): Promise<string[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/statuses/`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get topic statuses:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get topic statuses');
    }
  }

  /**
   * Migrate topics from localStorage to backend
   */
  async migrateFromLocalStorage(topics: TopicConfig[]): Promise<{
    migrated_count: number;
    total_topics: number;
    errors: Array<{ session_id: string; error: string }>;
    message: string;
  }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/migrate-from-localstorage`, topics);
      return response.data;
    } catch (error: any) {
      console.error('Failed to migrate topics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to migrate topics');
    }
  }

  /**
   * Get topics from localStorage (for migration)
   */
  getTopicsFromLocalStorage(): TopicConfig[] {
    try {
      const storedTopics = localStorage.getItem('created_topics');
      if (storedTopics) {
        return JSON.parse(storedTopics);
      }
      return [];
    } catch (error) {
      console.error('Failed to get topics from localStorage:', error);
      return [];
    }
  }

  /**
   * Clear topics from localStorage (after successful migration)
   */
  clearTopicsFromLocalStorage(): void {
    try {
      localStorage.removeItem('created_topics');
      console.log('Topics cleared from localStorage');
    } catch (error) {
      console.error('Failed to clear topics from localStorage:', error);
    }
  }
}

// Export singleton instance
export const topicService = new TopicService();
export default topicService;
