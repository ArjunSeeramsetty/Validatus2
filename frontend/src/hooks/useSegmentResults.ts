// frontend/src/hooks/useSegmentResults.ts

import { useState, useEffect } from 'react';
import apiService from '../services/api';

interface SegmentResults {
  topic_id: string;
  segment: string;
  factors: Record<string, any>;
  matched_patterns: any[];
  monte_carlo_scenarios: any[];
  personas: any[];
  rich_content: any;
}

interface UseSegmentResultsReturn {
  data: SegmentResults | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useSegmentResults = (
  topic: string,
  segment: string
): UseSegmentResultsReturn => {
  const [data, setData] = useState<SegmentResults | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!topic || !segment) {
      setError('Topic and segment are required');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      console.log(`📊 Fetching results for topic: ${topic}, segment: ${segment}`);
      
      const result = await apiService.getSegmentResults(topic, segment);
      
      console.log('✅ Data received:', result);
      setData(result);

    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load results';
      console.error('❌ Error fetching segment results:', errorMessage);
      setError(errorMessage);
      
      // NO MOCK DATA FALLBACK - Set data to null on error
      setData(null);

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [topic, segment]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
};
