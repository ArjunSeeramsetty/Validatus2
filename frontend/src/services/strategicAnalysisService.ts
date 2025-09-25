import { apiClient } from './apiClient';

// Type definitions for Strategic Analysis
export interface TopicCreationRequest {
  topic: string;
  description?: string;
  urls: string[];
  searchQueries: string[];
  analysisType?: 'comprehensive' | 'targeted' | 'quick';
}

export interface TopicResponse {
  success: boolean;
  topic_id: string;
  message: string;
  knowledge_base_created: boolean;
  url_count: number;
  content_quality_score: number;
}

export interface AnalysisSessionRequest {
  topic_id: string;
  analysis_parameters: {
    depth: 'quick' | 'standard' | 'comprehensive';
    include_competitors: boolean;
    include_financial: boolean;
    include_market_trends: boolean;
    use_enhanced_analytics: boolean;
    monte_carlo_simulations: boolean;
    bayesian_blending: boolean;
  };
  user_preferences?: {
    focus_areas: string[];
    time_horizon: 'short' | 'medium' | 'long';
    risk_tolerance: 'low' | 'medium' | 'high';
  };
}

export interface AnalysisResponse {
  success: boolean;
  session_id: string;
  topic: string;
  user_id: string;
  enhanced_analytics: boolean;
  message: string;
  estimated_completion_time: number; // in minutes
  analysis_steps: string[];
}

export interface ProgressResponse {
  session_id: string;
  status: 'created' | 'running' | 'completed' | 'failed';
  current_step: string;
  overall_progress: number;
  step_progress: { [step: string]: number };
  estimated_remaining_time: number;
  insights_generated: string[];
  errors?: string[];
}

export interface ResultsResponse {
  session_id: string;
  topic: string;
  status: 'completed';
  analysis_metadata: {
    total_processing_time: number;
    data_sources_analyzed: number;
    insights_generated: number;
    confidence_score: number;
  };
  strategic_layers: {
    [layer: string]: {
      score: number;
      confidence: number;
      insights: string[];
      recommendations: string[];
    };
  };
  strategic_factors: {
    [factor: string]: {
      score: number;
      trend: 'increasing' | 'decreasing' | 'stable';
      impact_level: 'low' | 'medium' | 'high';
      description: string;
    };
  };
  expert_personas: {
    [persona: string]: {
      insights: string[];
      recommendations: string[];
      confidence: number;
      expertise_areas: string[];
    };
  };
  monte_carlo_results?: {
    scenarios: Array<{
      name: string;
      probability: number;
      outcome: string;
      risk_level: 'low' | 'medium' | 'high';
    }>;
    risk_metrics: {
      var_95: number;
      expected_shortfall: number;
      sharpe_ratio: number;
    };
  };
  key_insights: string[];
  strategic_recommendations: string[];
  action_items: Array<{
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
    timeline: string;
    responsible_party: string;
  }>;
  created_at: string;
  completed_at: string;
}

export interface ExportResponse {
  success: boolean;
  download_url: string;
  file_format: string;
  file_size: number;
  expires_at: string;
}

export class StrategicAnalysisService {
  // ==================== STAGE 1: KNOWLEDGE ACQUISITION ====================
  
  /**
   * Create a new topic with knowledge acquisition
   */
  static async createTopic(topicData: TopicCreationRequest): Promise<TopicResponse> {
    try {
      const response = await apiClient.post('/api/v3/topics/create', {
        topic: topicData.topic,
        description: topicData.description,
        urls: topicData.urls,
        search_queries: topicData.searchQueries,
        analysis_type: topicData.analysisType || 'comprehensive'
      });
      
      return response.data;
    } catch (error: any) {
      throw new Error(`Failed to create topic: ${error.response?.data?.detail || error.message}`);
    }
  }

  /**
   * Collect URLs using web search queries
   */
  static async collectUrls(topic: string, searchQueries: string[]): Promise<{ urls: string[], quality_scores: number[] }> {
    try {
      const response = await apiClient.post('/api/v3/topics/search-urls', {
        topic,
        search_queries,
        max_urls: 50,
        quality_threshold: 0.7
      });
      
      return response.data;
    } catch (error: any) {
      // Fallback to mock data if API not available
      return {
        urls: [
          `https://example.com/${topic.toLowerCase().replace(/\s+/g, '-')}-analysis`,
          `https://marketresearch.com/${topic.toLowerCase().replace(/\s+/g, '-')}-report`,
          `https://industryinsights.com/${topic.toLowerCase().replace(/\s+/g, '-')}-trends`
        ],
        quality_scores: [0.85, 0.92, 0.78]
      };
    }
  }

  /**
   * Validate and preview URL content
   */
  static async validateUrl(url: string): Promise<{ valid: boolean, preview: string, quality_score: number }> {
    try {
      const response = await apiClient.post('/api/v3/topics/validate-url', {
        url,
        extract_preview: true,
        quality_assessment: true
      });
      
      return response.data;
    } catch (error: any) {
      // Fallback for URL validation
      return {
        valid: url.startsWith('http'),
        preview: `Content preview for ${url}`,
        quality_score: Math.random() * 0.4 + 0.6
      };
    }
  }

  /**
   * Get topic knowledge base status
   */
  static async getTopicStatus(topicId: string): Promise<{
    status: 'processing' | 'ready' | 'failed';
    url_count: number;
    content_processed: number;
    vector_embeddings_created: boolean;
    quality_score: number;
  }> {
    try {
      const response = await apiClient.get(`/api/v3/topics/${topicId}/status`);
      return response.data;
    } catch (error: any) {
      // Mock status for development
      return {
        status: 'ready',
        url_count: 15,
        content_processed: 15,
        vector_embeddings_created: true,
        quality_score: 0.87
      };
    }
  }

  // ==================== STAGE 2: STRATEGIC ANALYSIS ====================
  
  /**
   * Start strategic analysis session
   */
  static async startAnalysis(sessionData: AnalysisSessionRequest): Promise<AnalysisResponse> {
    try {
      const response = await apiClient.post('/api/v3/analysis/sessions/create', {
        topic_id: sessionData.topic_id,
        analysis_parameters: sessionData.analysis_parameters,
        user_preferences: sessionData.user_preferences,
        use_enhanced_analytics: sessionData.analysis_parameters.use_enhanced_analytics
      });
      
      return response.data;
    } catch (error: any) {
      throw new Error(`Failed to start analysis: ${error.response?.data?.detail || error.message}`);
    }
  }

  /**
   * Monitor analysis progress
   */
  static async monitorProgress(sessionId: string): Promise<ProgressResponse> {
    try {
      const response = await apiClient.get(`/api/v3/analysis/sessions/${sessionId}/status`);
      return response.data;
    } catch (error: any) {
      // Mock progress for development
      return {
        session_id: sessionId,
        status: 'running',
        current_step: 'Strategic Layer Scoring',
        overall_progress: Math.round(Math.random() * 40 + 30),
        step_progress: {
          'knowledge_processing': 100,
          'layer_scoring': Math.round(Math.random() * 100),
          'factor_analysis': Math.round(Math.random() * 60),
          'expert_personas': 0,
          'action_layers': 0,
          'monte_carlo': 0,
          'bayesian_blending': 0,
          'results_compilation': 0
        },
        estimated_remaining_time: Math.round(Math.random() * 15 + 5),
        insights_generated: [
          'Market size analysis completed',
          'Competitive landscape assessment in progress',
          'Risk factors identified and categorized'
        ]
      };
    }
  }

  /**
   * Get real-time analysis insights
   */
  static async getAnalysisInsights(sessionId: string): Promise<{
    current_insights: string[];
    partial_results: Partial<ResultsResponse>;
    next_steps: string[];
  }> {
    try {
      const response = await apiClient.get(`/api/v3/analysis/sessions/${sessionId}/insights`);
      return response.data;
    } catch (error: any) {
      // Mock insights for development
      return {
        current_insights: [
          'Strategic layer analysis shows strong market positioning',
          'Factor analysis reveals growth opportunities in emerging segments',
          'Expert persona analysis indicates high confidence in recommendations'
        ],
        partial_results: {
          strategic_layers: {
            'Strategic Planning': { score: 85, confidence: 0.92, insights: [], recommendations: [] },
            'Market Analysis': { score: 78, confidence: 0.88, insights: [], recommendations: [] }
          },
          strategic_factors: {
            'Market Size': { score: 92, trend: 'increasing', impact_level: 'high', description: 'Large and growing market' },
            'Growth Rate': { score: 87, trend: 'increasing', impact_level: 'high', description: 'Strong growth trajectory' }
          }
        },
        next_steps: [
          'Complete expert persona analysis',
          'Run Monte Carlo simulations',
          'Generate final recommendations'
        ]
      };
    }
  }

  // ==================== STAGE 3: RESULTS & VISUALIZATION ====================
  
  /**
   * Get comprehensive analysis results
   */
  static async getAnalysisResults(sessionId: string): Promise<ResultsResponse> {
    try {
      const response = await apiClient.get(`/api/v3/analysis/sessions/${sessionId}/results`);
      return response.data;
    } catch (error: any) {
      // Mock comprehensive results for development
      return this.generateMockResults(sessionId);
    }
  }

  /**
   * Generate mock results for development/testing
   */
  private static generateMockResults(sessionId: string): ResultsResponse {
    const baseScore = () => Math.round(Math.random() * 40 + 60);
    const confidence = () => Math.round((Math.random() * 0.3 + 0.7) * 100) / 100;
    
    return {
      session_id: sessionId,
      topic: 'Strategic Analysis',
      status: 'completed',
      analysis_metadata: {
        total_processing_time: Math.round(Math.random() * 30 + 15),
        data_sources_analyzed: Math.round(Math.random() * 20 + 10),
        insights_generated: Math.round(Math.random() * 50 + 25),
        confidence_score: confidence()
      },
      strategic_layers: {
        'Strategic Planning': {
          score: baseScore(),
          confidence: confidence(),
          insights: ['Strong strategic foundation identified', 'Clear vision and mission alignment'],
          recommendations: ['Develop comprehensive strategic roadmap', 'Establish key performance indicators']
        },
        'Market Analysis': {
          score: baseScore(),
          confidence: confidence(),
          insights: ['Market shows significant growth potential', 'Competitive landscape is dynamic'],
          recommendations: ['Focus on high-growth segments', 'Monitor competitor activities closely']
        },
        'Risk Assessment': {
          score: baseScore(),
          confidence: confidence(),
          insights: ['Key risks identified and quantified', 'Mitigation strategies available'],
          recommendations: ['Implement risk monitoring system', 'Develop contingency plans']
        },
        'Value Creation': {
          score: baseScore(),
          confidence: confidence(),
          insights: ['Multiple value creation opportunities identified', 'Strong value proposition potential'],
          recommendations: ['Optimize value delivery processes', 'Enhance customer value proposition']
        }
      },
      strategic_factors: {
        'Market Size': { score: baseScore(), trend: 'increasing', impact_level: 'high', description: 'Large and growing market opportunity' },
        'Growth Rate': { score: baseScore(), trend: 'increasing', impact_level: 'high', description: 'Strong growth trajectory identified' },
        'Competition Level': { score: baseScore(), trend: 'stable', impact_level: 'medium', description: 'Moderate competitive intensity' },
        'Technology Readiness': { score: baseScore(), trend: 'increasing', impact_level: 'high', description: 'Technology infrastructure is capable' },
        'Regulatory Environment': { score: baseScore(), trend: 'stable', impact_level: 'medium', description: 'Favorable regulatory conditions' },
        'Customer Demand': { score: baseScore(), trend: 'increasing', impact_level: 'high', description: 'Strong customer demand signals' }
      },
      expert_personas: {
        'Market Strategist': {
          insights: ['Market shows strong growth potential with emerging opportunities'],
          recommendations: ['Focus on underserved market segments', 'Develop competitive differentiation strategy'],
          confidence: confidence(),
          expertise_areas: ['Market Analysis', 'Strategic Planning', 'Competitive Intelligence']
        },
        'Financial Analyst': {
          insights: ['Strong financial fundamentals with growth investment opportunities'],
          recommendations: ['Optimize capital allocation', 'Implement performance monitoring'],
          confidence: confidence(),
          expertise_areas: ['Financial Analysis', 'Investment Strategy', 'Risk Management']
        },
        'Technology Expert': {
          insights: ['Technology infrastructure supports growth objectives'],
          recommendations: ['Invest in digital transformation', 'Leverage emerging technologies'],
          confidence: confidence(),
          expertise_areas: ['Technology Strategy', 'Digital Transformation', 'Innovation Management']
        }
      },
      monte_carlo_results: {
        scenarios: [
          { name: 'Optimistic', probability: 0.25, outcome: 'High growth with market leadership', risk_level: 'low' },
          { name: 'Realistic', probability: 0.50, outcome: 'Steady growth with competitive position', risk_level: 'medium' },
          { name: 'Pessimistic', probability: 0.25, outcome: 'Moderate growth with challenges', risk_level: 'high' }
        ],
        risk_metrics: {
          var_95: 0.15,
          expected_shortfall: 0.22,
          sharpe_ratio: 1.8
        }
      },
      key_insights: [
        'Strategic analysis reveals significant growth opportunities in target markets',
        'Technology readiness provides strong foundation for digital transformation',
        'Competitive landscape offers opportunities for differentiation',
        'Risk factors are manageable with proper mitigation strategies',
        'Financial performance shows strong fundamentals for growth investment'
      ],
      strategic_recommendations: [
        'Focus on high-potential market segments with strong growth characteristics',
        'Invest in technology infrastructure to support digital transformation initiatives',
        'Develop strategic partnerships to accelerate market penetration',
        'Implement comprehensive risk monitoring and mitigation systems',
        'Establish clear performance metrics and monitoring frameworks'
      ],
      action_items: [
        {
          title: 'Market Segment Analysis',
          description: 'Conduct detailed analysis of high-potential market segments',
          priority: 'high',
          timeline: '2-3 weeks',
          responsible_party: 'Market Research Team'
        },
        {
          title: 'Technology Roadmap Development',
          description: 'Create comprehensive technology roadmap for digital transformation',
          priority: 'high',
          timeline: '4-6 weeks',
          responsible_party: 'Technology Team'
        },
        {
          title: 'Risk Management Framework',
          description: 'Implement comprehensive risk monitoring and mitigation system',
          priority: 'medium',
          timeline: '6-8 weeks',
          responsible_party: 'Risk Management Team'
        }
      ],
      created_at: new Date(Date.now() - 3600000).toISOString(),
      completed_at: new Date().toISOString()
    };
  }

  // ==================== EXPORT & SHARING ====================
  
  /**
   * Export analysis results
   */
  static async exportResults(sessionId: string, format: 'pdf' | 'excel' | 'powerpoint'): Promise<ExportResponse> {
    try {
      const response = await apiClient.post(`/api/v3/analysis/sessions/${sessionId}/export`, {
        format,
        include_charts: true,
        include_data: true,
        custom_template: false
      });
      
      return response.data;
    } catch (error: any) {
      // Mock export response for development
      return {
        success: true,
        download_url: `https://api.validatus.com/exports/${sessionId}.${format}`,
        file_format: format,
        file_size: Math.round(Math.random() * 5000000 + 1000000), // 1-6MB
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days
      };
    }
  }

  /**
   * Share analysis results
   */
  static async shareResults(sessionId: string, shareOptions: {
    recipients: string[];
    access_level: 'view' | 'comment' | 'edit';
    expires_in_days?: number;
    include_data?: boolean;
  }): Promise<{ success: boolean; share_url: string; share_id: string }> {
    try {
      const response = await apiClient.post(`/api/v3/analysis/sessions/${sessionId}/share`, shareOptions);
      return response.data;
    } catch (error: any) {
      // Mock share response for development
      return {
        success: true,
        share_url: `https://validatus.com/shared/${sessionId}`,
        share_id: `share_${sessionId}_${Date.now()}`
      };
    }
  }

  /**
   * Get analysis history for a user
   */
  static async getAnalysisHistory(userId?: string): Promise<{
    analyses: Array<{
      session_id: string;
      topic: string;
      status: string;
      created_at: string;
      completed_at?: string;
      confidence_score: number;
    }>;
    total_count: number;
  }> {
    try {
      const response = await apiClient.get(`/api/v3/analysis/sessions/history${userId ? `?user_id=${userId}` : ''}`);
      return response.data;
    } catch (error: any) {
      // Mock history for development
      return {
        analyses: [
          {
            session_id: 'session-1',
            topic: 'Electric Vehicle Market Analysis',
            status: 'completed',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            completed_at: new Date(Date.now() - 82800000).toISOString(),
            confidence_score: 0.92
          },
          {
            session_id: 'session-2',
            topic: 'Financial Services Digital Transformation',
            status: 'completed',
            created_at: new Date(Date.now() - 172800000).toISOString(),
            completed_at: new Date(Date.now() - 169200000).toISOString(),
            confidence_score: 0.87
          }
        ],
        total_count: 2
      };
    }
  }
}

export default StrategicAnalysisService;
