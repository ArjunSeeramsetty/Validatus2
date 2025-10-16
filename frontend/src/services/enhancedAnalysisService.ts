/**
 * Enhanced Analysis Service
 * Connects frontend to sophisticated analytical engines (Pattern Library, Monte Carlo, etc.)
 */

import { apiClient } from './apiClient';

export interface PatternMatch {
  pattern_id: string;
  pattern_name: string;
  pattern_type: string;
  confidence: number;
  segments_involved: string[];
  factors_triggered: string[];
  strategic_response: string;
  effect_size_hints: string;
  outcome_measures: string[];
  evidence_strength: number;
}

export interface MonteCarloScenario {
  pattern_id: string;
  pattern_name: string;
  expected_outcomes: Record<string, {
    mean: number;
    median: number;
    std_dev: number;
    percentile_5: number;
    percentile_95: number;
    confidence_interval_90: [number, number];
    confidence_interval_95: [number, number];
    confidence_interval_99: [number, number];
    probability_positive: number;
  }>;
  simulation_count: number;
}

export interface FormulaStatus {
  sophisticated_engines_available: boolean;
  engines: Record<string, string>;
  data_driven: boolean;
  formula_source: string;
  status: string;
}

export interface PatternMatchingResponse {
  success: boolean;
  session_id: string;
  pattern_matches: PatternMatch[];
  total_matches: number;
  segment_scores_used: Record<string, number>;
  factor_count_used: number;
  methodology: string;
  data_driven: boolean;
}

export interface ComprehensiveScenariosResponse {
  success: boolean;
  session_id: string;
  scenarios: Record<string, MonteCarloScenario>;
  total_patterns: number;
  total_scenarios: number;
  simulation_config: {
    iterations_per_kpi: number;
    confidence_levels: number[];
  };
}

export interface FactorResult {
  factor_id: string;
  value: number;
  confidence: number;
  formula_applied: string;
  calculation_metadata: Record<string, any>;
}

export interface ActionLayerResult {
  layer_name: string;
  score: number;
  confidence: number;
  components: Record<string, number>;
  strategic_insights: string[];
  recommendations: string[];
}

class EnhancedAnalysisService {
  private baseUrl = '/api/v3/enhanced-analysis';

  /**
   * Check if sophisticated engines are available
   */
  async getFormulaStatus(): Promise<FormulaStatus> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/formula-status`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get formula status:', error);
      throw new Error(error.response?.data?.detail || 'Failed to check engine status');
    }
  }

  /**
   * Match patterns from Pattern Library (P001-P041) to actual scores
   */
  async matchPatterns(sessionId: string): Promise<PatternMatchingResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/pattern-matching/${sessionId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to match patterns:', error);
      throw new Error(error.response?.data?.detail || 'Failed to match patterns');
    }
  }

  /**
   * Generate Monte Carlo scenarios for matched patterns
   */
  async generateScenarios(sessionId: string): Promise<ComprehensiveScenariosResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/comprehensive-scenarios/${sessionId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to generate scenarios:', error);
      throw new Error(error.response?.data?.detail || 'Failed to generate scenarios');
    }
  }

  /**
   * Calculate F1-F28 factors using documented PDF formulas
   */
  async calculateFormulas(sessionId: string): Promise<{
    success: boolean;
    session_id: string;
    factors: FactorResult[];
    total_factors: number;
    data_driven: boolean;
  }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/calculate-formulas/${sessionId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to calculate formulas:', error);
      throw new Error(error.response?.data?.detail || 'Failed to calculate formulas');
    }
  }

  /**
   * Calculate 18 Action Layer strategic assessments
   */
  async calculateActionLayers(sessionId: string): Promise<{
    success: boolean;
    session_id: string;
    action_layers: ActionLayerResult[];
    total_layers: number;
  }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/calculate-action-layers/${sessionId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to calculate action layers:', error);
      throw new Error(error.response?.data?.detail || 'Failed to calculate action layers');
    }
  }

  /**
   * Run Monte Carlo simulation
   */
  async runMonteCarlo(sessionId: string, iterations: number = 1000): Promise<any> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/monte-carlo/${sessionId}`, {
        params: { iterations }
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to run Monte Carlo:', error);
      throw new Error(error.response?.data?.detail || 'Failed to run Monte Carlo simulation');
    }
  }

  /**
   * Get comprehensive enhanced analysis (all sophisticated engines)
   */
  async getComprehensiveAnalysis(sessionId: string): Promise<{
    patterns: PatternMatchingResponse;
    scenarios: ComprehensiveScenariosResponse;
    formulas?: any;
    actionLayers?: any;
  }> {
    try {
      // Check if engines available first
      const status = await this.getFormulaStatus();
      
      if (!status.sophisticated_engines_available) {
        throw new Error('Sophisticated engines not available');
      }

      // Fetch all data in parallel
      const [patterns, scenarios] = await Promise.all([
        this.matchPatterns(sessionId),
        this.generateScenarios(sessionId)
      ]);

      return {
        patterns,
        scenarios
      };
    } catch (error: any) {
      console.error('Failed to get comprehensive analysis:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const enhancedAnalysisService = new EnhancedAnalysisService();
export default enhancedAnalysisService;

