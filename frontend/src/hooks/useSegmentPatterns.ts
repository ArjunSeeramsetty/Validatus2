/**
 * Hook for fetching patterns by segment
 * Enables pattern display in ALL segments (Market, Product, Brand, Experience, Consumer)
 */
import { useState, useEffect } from 'react';
import axios from 'axios';

interface PatternMatch {
  pattern_id: string;
  pattern_name: string;
  pattern_type: string;
  confidence: number;
  probability_range: [number, number];
  segments_involved: string[];
  factors_triggered: string[];
  strategic_response: string;
  effect_size_hints: string;
  outcome_measures: string[];
  evidence_strength: number;
}

interface MonteCarloKPI {
  mean: number;
  median: number;
  std_dev: number;
  percentile_5: number;
  percentile_95: number;
  confidence_interval_90: [number, number];
  probability_positive: number;
  distribution: string;
  simulations: number;
}

interface MonteCarloScenario {
  pattern_name: string;
  pattern_type: string;
  confidence: number;
  strategic_response: string;
  effect_size_hints: string;
  kpi_simulations: Record<string, MonteCarloKPI>;
  segments_involved: string[];
}

interface SegmentPatternsResponse {
  session_id: string;
  segment: string;
  pattern_matches: PatternMatch[];
  scenarios: Record<string, MonteCarloScenario>;
  total_patterns_available: number;
  patterns_matched: number;
  data_driven: boolean;
  methodology: string;
}

export const useSegmentPatterns = (
  sessionId: string | null,
  segment: 'consumer' | 'market' | 'product' | 'brand' | 'experience'
) => {
  const [patternMatches, setPatternMatches] = useState<PatternMatch[]>([]);
  const [scenarios, setScenarios] = useState<Record<string, MonteCarloScenario>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId || !segment) {
      setPatternMatches([]);
      setScenarios({});
      return;
    }

    const fetchSegmentPatterns = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get<SegmentPatternsResponse>(
          `/api/v3/enhanced-analysis/patterns-by-segment/${sessionId}/${segment}`
        );
        
        setPatternMatches(response.data.pattern_matches);
        setScenarios(response.data.scenarios);
      } catch (err: any) {
        console.error(`Segment patterns fetch error for ${segment}:`, err);
        setError(err.response?.data?.detail || err.message);
        setPatternMatches([]);
        setScenarios({});
      } finally {
        setLoading(false);
      }
    };

    fetchSegmentPatterns();
  }, [sessionId, segment]);

  return {
    patternMatches,
    scenarios,
    loading,
    error,
    hasPatterns: patternMatches.length > 0
  };
};

