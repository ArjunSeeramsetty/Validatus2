/**
 * React Hook for Sequential Stage Analysis Workflow
 */
import { useState, useCallback } from 'react';
import { apiClient } from '../services/apiClient';

interface StageStatus {
  stage: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  progress: number;
  results_path?: string;
  error_message?: string;
}

interface SessionOverview {
  session_id: string;
  topic_id: string;
  user_id: string;
  created_at: string;
  current_stage: number;
  stages: Record<number, StageStatus>;
  overall_status: string;
}

interface Stage1Results {
  session_id: string;
  topic_id: string;
  strategic_layers: Record<string, any>;
  strategic_factors: Record<string, any>;
  expert_personas: Record<string, any>;
  analysis_metadata: any;
}

interface Stage2Results {
  session_id: string;
  topic_id: string;
  query: string;
  results: Array<{
    content: string;
    metadata: any;
    similarity_score: number;
    relevance_score: number;
  }>;
  total_results: number;
  search_metadata: any;
}

interface Stage3Results {
  session_id: string;
  formula_calculations: Record<string, any>;
  action_items: Array<{
    title: string;
    description: string;
    priority: string;
    timeline: string;
    responsible_party: string;
  }>;
  overall_score: number;
  financial_projections: any;
  risk_assessment: any;
  action_metadata: any;
}

export function useSequentialAnalysis() {
  const [sessionId, setSessionId] = useState<string>();
  const [currentStage, setCurrentStage] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const [sessionOverview, setSessionOverview] = useState<SessionOverview | null>(null);
  const [stage1Results, setStage1Results] = useState<Stage1Results | null>(null);
  const [stage2Results, setStage2Results] = useState<Stage2Results | null>(null);
  const [stage3Results, setStage3Results] = useState<Stage3Results | null>(null);

  const createSession = useCallback(async (topicId: string, userId: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post(`/api/v3/topics/${topicId}/analysis/create`, {
        topic_id: topicId,
        user_id: userId
      });
      
      setSessionId(response.data.session_id);
      setCurrentStage(0);
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create session');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const startStage1 = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post(`/api/v3/analysis/${sessionId}/stage1/start`);
      setCurrentStage(1);
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start Stage 1');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const checkStage1Status = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    const response = await apiClient.get(`/api/v3/analysis/${sessionId}/stage1/status`);
    return response.data;
  }, [sessionId]);

  const getStage1Results = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    const response = await apiClient.get(`/api/v3/analysis/${sessionId}/stage1/results`);
    setStage1Results(response.data.results);
    return response.data;
  }, [sessionId]);

  const startStage2 = useCallback(async (query: string) => {
    if (!sessionId) throw new Error('No session ID');
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post(`/api/v3/analysis/${sessionId}/stage2/start`, {
        query
      });
      setCurrentStage(2);
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start Stage 2');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const checkStage2Status = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    const response = await apiClient.get(`/api/v3/analysis/${sessionId}/stage2/status`);
    return response.data;
  }, [sessionId]);

  const getStage2Results = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    const response = await apiClient.get(`/api/v3/analysis/${sessionId}/stage2/results`);
    setStage2Results(response.data.results);
    return response.data;
  }, [sessionId]);

  const startStage3 = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post(`/api/v3/analysis/${sessionId}/stage3/start`);
      setCurrentStage(3);
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start Stage 3');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const checkStage3Status = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    const response = await apiClient.get(`/api/v3/analysis/${sessionId}/stage3/status`);
    return response.data;
  }, [sessionId]);

  const getStage3Results = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    const response = await apiClient.get(`/api/v3/analysis/${sessionId}/stage3/results`);
    setStage3Results(response.data.results);
    return response.data;
  }, [sessionId]);

  const getSessionOverview = useCallback(async () => {
    if (!sessionId) throw new Error('No session ID');
    
    const response = await apiClient.get(`/api/v3/analysis/${sessionId}/overview`);
    setSessionOverview(response.data);
    return response.data;
  }, [sessionId]);

  const reset = useCallback(() => {
    setSessionId(undefined);
    setCurrentStage(0);
    setLoading(false);
    setError(null);
    setSessionOverview(null);
    setStage1Results(null);
    setStage2Results(null);
    setStage3Results(null);
  }, []);

  return {
    // State
    sessionId,
    currentStage,
    loading,
    error,
    sessionOverview,
    stage1Results,
    stage2Results,
    stage3Results,
    
    // Actions
    createSession,
    startStage1,
    checkStage1Status,
    getStage1Results,
    startStage2,
    checkStage2Status,
    getStage2Results,
    startStage3,
    checkStage3Status,
    getStage3Results,
    getSessionOverview,
    reset
  };
}
