import { apiClient } from './apiClient';

export interface RagQueryRequest {
  topic_id: string;
  query: string;
  max_results?: number;
  similarity_threshold?: number;
  include_metadata?: boolean;
}

export interface RagQueryResult {
  content: string;
  metadata: {
    source_url: string;
    title: string;
    similarity_score: number;
    chunk_index: number;
    scraped_at: string;
  };
  relevance_score: number;
}

export interface RagQueryResponse {
  query: string;
  results: RagQueryResult[];
  total_results: number;
  search_time_ms: number;
  query_embedding_time_ms: number;
}

export class RagQueryService {
  /**
   * Perform semantic search query on topic vector store
   */
  static async queryVectorStore(queryData: RagQueryRequest): Promise<RagQueryResponse> {
    try {
      const response = await apiClient.post(`/api/v3/topics/${queryData.topic_id}/query`, {
        query: queryData.query,
        max_results: queryData.max_results || 10,
        similarity_threshold: queryData.similarity_threshold || 0.7,
        include_metadata: queryData.include_metadata ?? true
      });

      return response.data;
    } catch (error: any) {
      // Mock response for development
      return this.generateMockQueryResponse(queryData.query, queryData.max_results || 10);
    }
  }

  /**
   * Get query suggestions based on topic content
   */
  static async getQuerySuggestions(topicId: string): Promise<string[]> {
    try {
      const response = await apiClient.get(`/api/v3/topics/${topicId}/query-suggestions`);
      return response.data.suggestions;
    } catch (error: any) {
      // Mock suggestions
      return [
        'What are the key market trends?',
        'How does competition affect market share?',
        'What are the main risk factors?',
        'What opportunities exist for growth?',
        'How is technology impacting the industry?'
      ];
    }
  }

  private static generateMockQueryResponse(query: string, maxResults: number): RagQueryResponse {
    const results: RagQueryResult[] = Array.from({ length: Math.min(maxResults, 8) }, (_, i) => ({
      content: `This content snippet discusses ${query.toLowerCase()} in detail, providing comprehensive analysis and insights based on industry research and expert opinions. The analysis covers multiple aspects including market dynamics, competitive landscape, and strategic implications for businesses operating in this space.`,
      metadata: {
        source_url: `https://example.com/source-${i + 1}`,
        title: `Analysis Report ${i + 1}: ${query}`,
        similarity_score: Math.random() * 0.3 + 0.7,
        chunk_index: i,
        scraped_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
      },
      relevance_score: Math.random() * 0.3 + 0.7
    }));

    return {
      query,
      results,
      total_results: results.length,
      search_time_ms: Math.floor(Math.random() * 200) + 50,
      query_embedding_time_ms: Math.floor(Math.random() * 50) + 10
    };
  }
}
