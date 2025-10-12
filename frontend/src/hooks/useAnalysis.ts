/**
 * Custom hook for Results Analysis data fetching
 * Handles loading states and API communication for all analysis dimensions
 */

import { useState, useCallback } from 'react';
import axios from 'axios';

// API base URL from environment or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface CompleteAnalysisResult {
  session_id: string;
  topic_name: string;
  analysis_timestamp: string;
  business_case?: any;
  market: MarketAnalysisData;
  consumer: ConsumerAnalysisData;
  product: ProductAnalysisData;
  brand: BrandAnalysisData;
  experience: ExperienceAnalysisData;
  confidence_scores: Record<string, number>;
}

export interface MarketAnalysisData {
  competitor_analysis: Record<string, any>;
  opportunities: string[];
  opportunities_rationale?: string;
  market_share: Record<string, number>;
  pricing_switching: Record<string, any>;
  regulation_tariffs: Record<string, any>;
  growth_demand: Record<string, any>;
  market_fit: Record<string, number>;
}

export interface ConsumerAnalysisData {
  recommendations: Array<{type?: string; timeline?: string; description: string}>;
  challenges: string[];
  top_motivators: string[];
  relevant_personas: Array<{name: string; age?: number; description: string}>;
  target_audience: Record<string, any>;
  consumer_fit: Record<string, number>;
  additional_recommendations?: string[];
}

export interface ProductAnalysisData {
  product_features: Array<{name: string; description: string; importance?: number; category?: string}>;
  competitive_positioning: Record<string, any>;
  innovation_opportunities: string[];
  technical_specifications: Record<string, any>;
  product_roadmap: Array<{phase: string; features: string; timeline: string}>;
  product_fit: Record<string, number>;
}

export interface BrandAnalysisData {
  brand_positioning: Record<string, number>;
  brand_perception: Record<string, number>;
  competitor_brands: Array<{name: string; positioning: string; strength: number}>;
  brand_opportunities: string[];
  messaging_strategy: Record<string, any>;
  brand_fit: Record<string, number>;
}

export interface ExperienceAnalysisData {
  user_journey: Array<{stage: string; phase: string; description: string; pain_points: string[]; opportunities: string[]}>;
  touchpoints: Array<{name: string; importance: number; current_quality: number; improvement_potential: number}>;
  pain_points: string[];
  experience_metrics: Record<string, number>;
  improvement_recommendations: string[];
  experience_fit: Record<string, number>;
}

export const useAnalysis = () => {
  const [analysisData, setAnalysisData] = useState<CompleteAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCompleteAnalysis = useCallback(async (sessionId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v3/results/complete/${sessionId}`);
      setAnalysisData(response.data);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch analysis';
      setError(errorMessage);
      console.error('Analysis fetch error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSpecificAnalysis = useCallback(async (sessionId: string, analysisType: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v3/results/${analysisType}/${sessionId}`);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch specific analysis';
      setError(errorMessage);
      console.error(`${analysisType} analysis fetch error:`, err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const checkAnalysisStatus = useCallback(async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v3/results/status/${sessionId}`);
      return response.data;
    } catch (err: any) {
      console.error('Status check error:', err);
      return null;
    }
  }, []);

  const resetAnalysis = useCallback(() => {
    setAnalysisData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    analysisData,
    loading,
    error,
    fetchCompleteAnalysis,
    fetchSpecificAnalysis,
    checkAnalysisStatus,
    resetAnalysis
  };
};

