// frontend/src/hooks/useDataDrivenResults.ts

import { useState, useEffect } from 'react';
import axios from 'axios';

interface ResultsStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress_percentage: number;
  current_stage: string;
  completed_segments: number;
  total_segments: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

interface SegmentResults {
  session_id: string;
  segment: string;
  factors: Record<string, any>;
  patterns: any[];
  scenarios: any[];
  personas?: any[];
  rich_content?: any;
  loaded_from_cache: boolean;
  timestamp: string;
}

export const useDataDrivenResults = (sessionId: string, segment: string) => {
  const [data, setData] = useState<SegmentResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<ResultsStatus | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      if (!sessionId || !segment) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        console.log(`[Data-Driven Results] Fetching results for session ${sessionId}, segment ${segment}`);
        
        // First check generation status
        const statusResponse = await axios.get(`/api/v3/data-driven-results/status/${sessionId}`);
        setStatus(statusResponse.data);
        
        console.log(`[Data-Driven Results] Status: ${statusResponse.data.status}`);
        
        if (statusResponse.data.status === 'completed') {
          // Load results from database
          const response = await axios.get(`/api/v3/data-driven-results/segment/${sessionId}/${segment}`);
          setData(response.data);
          console.log(`[Data-Driven Results] Loaded ${segment} results:`, response.data);
        } else if (statusResponse.data.status === 'processing') {
          // Poll for completion
          console.log(`[Data-Driven Results] Results generation in progress: ${statusResponse.data.progress_percentage}%`);
          setTimeout(fetchResults, 3000); // Check again in 3 seconds
        } else if (statusResponse.data.status === 'failed') {
          setError(`Results generation failed: ${statusResponse.data.error_message || 'Unknown error'}`);
        } else {
          // Results not generated yet
          setError('Results not yet generated. Please wait for scoring to complete.');
        }
        
      } catch (err: any) {
        console.error(`[Data-Driven Results] Error:`, err);
        setError(err.response?.data?.detail || err.message || 'Failed to load results');
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [sessionId, segment]);

  const triggerGeneration = async (topic: string) => {
    try {
      console.log(`[Data-Driven Results] Triggering generation for session ${sessionId}, topic ${topic}`);
      const response = await axios.post(`/api/v3/data-driven-results/generate/${sessionId}/${topic}`);
      console.log(`[Data-Driven Results] Generation triggered:`, response.data);
      return response.data;
    } catch (err: any) {
      console.error(`[Data-Driven Results] Error triggering generation:`, err);
      throw new Error(err.response?.data?.detail || err.message || 'Failed to trigger generation');
    }
  };

  const clearResults = async () => {
    try {
      console.log(`[Data-Driven Results] Clearing results for session ${sessionId}`);
      const response = await axios.delete(`/api/v3/data-driven-results/clear/${sessionId}`);
      console.log(`[Data-Driven Results] Results cleared:`, response.data);
      setData(null);
      setStatus(null);
      return response.data;
    } catch (err: any) {
      console.error(`[Data-Driven Results] Error clearing results:`, err);
      throw new Error(err.response?.data?.detail || err.message || 'Failed to clear results');
    }
  };

  return {
    data,
    loading,
    error,
    status,
    triggerGeneration,
    clearResults,
    // NO MOCK DATA - only real data or error
    hasData: !!data,
    isProcessing: status?.status === 'processing',
    isCompleted: status?.status === 'completed',
    isFailed: status?.status === 'failed'
  };
};
