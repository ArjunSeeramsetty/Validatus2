/**
 * Hook for fetching Growth & Demand analysis
 * Fixes the Market Size and Growth Rate zero scores issue
 */
import { useState, useEffect } from 'react';
import axios from 'axios';

interface GrowthDemandData {
  session_id: string;
  market_size: {
    score: number;
    confidence: number;
    value: number | null;
    currency: string;
    evidence: string;
    data_found: boolean;
  };
  growth_rate: {
    score: number;
    confidence: number;
    cagr: number | null;
    period: string;
    evidence: string;
    data_found: boolean;
  };
  demand_drivers: string[];
  market_dynamics: any;
  analyzed_at: string;
}

export const useGrowthDemand = (sessionId: string | null) => {
  const [growthDemandData, setGrowthDemandData] = useState<GrowthDemandData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setGrowthDemandData(null);
      return;
    }

    const fetchGrowthDemand = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get(
          `/api/v3/enhanced-analysis/growth-demand/${sessionId}`
        );
        setGrowthDemandData(response.data);
      } catch (err: any) {
        console.error('Growth/Demand fetch error:', err);
        setError(err.response?.data?.detail || err.message);
        setGrowthDemandData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchGrowthDemand();
  }, [sessionId]);

  return {
    growthDemandData,
    loading,
    error
  };
};

