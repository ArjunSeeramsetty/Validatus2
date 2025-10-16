/**
 * Custom hook for Enhanced Analysis (Sophisticated Engines)
 * Fetches pattern matches, Monte Carlo scenarios, and other advanced analytics
 */

import { useState, useEffect, useCallback } from 'react';
import enhancedAnalysisService, {
  FormulaStatus,
  PatternMatchingResponse,
  ComprehensiveScenariosResponse
} from '../services/enhancedAnalysisService';

export interface UseEnhancedAnalysisResult {
  engineStatus: FormulaStatus | null;
  patternMatches: PatternMatchingResponse | null;
  scenarios: ComprehensiveScenariosResponse | null;
  loading: boolean;
  error: string | null;
  enginesAvailable: boolean;
  refetch: () => Promise<void>;
}

export const useEnhancedAnalysis = (sessionId: string | null): UseEnhancedAnalysisResult => {
  const [engineStatus, setEngineStatus] = useState<FormulaStatus | null>(null);
  const [patternMatches, setPatternMatches] = useState<PatternMatchingResponse | null>(null);
  const [scenarios, setScenarios] = useState<ComprehensiveScenariosResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    if (!sessionId) {
      setError('No session ID provided');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Step 1: Check if engines are available
      console.log('[Enhanced Analysis] Checking engine status...');
      const status = await enhancedAnalysisService.getFormulaStatus();
      setEngineStatus(status);

      if (!status.sophisticated_engines_available) {
        console.warn('[Enhanced Analysis] Sophisticated engines not available');
        setError('Sophisticated engines not available');
        return;
      }

      console.log('[Enhanced Analysis] Engines available, fetching pattern matches...');

      // Step 2: Fetch pattern matches
      const patterns = await enhancedAnalysisService.matchPatterns(sessionId);
      setPatternMatches(patterns);

      console.log(`[Enhanced Analysis] Found ${patterns.total_matches} pattern matches`);

      // Step 3: Fetch scenarios (only if patterns matched)
      if (patterns.total_matches > 0) {
        console.log('[Enhanced Analysis] Generating Monte Carlo scenarios...');
        const scenarioData = await enhancedAnalysisService.generateScenarios(sessionId);
        setScenarios(scenarioData);
        console.log(`[Enhanced Analysis] Generated ${scenarioData.total_scenarios} scenarios`);
      } else {
        console.log('[Enhanced Analysis] No patterns matched, skipping scenario generation');
        setScenarios(null);
      }

      console.log('[Enhanced Analysis] Fetch complete');

    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch enhanced analysis';
      setError(errorMessage);
      console.error('[Enhanced Analysis] Error:', err);
      
      // Reset data on error
      setPatternMatches(null);
      setScenarios(null);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Fetch on mount and when sessionId changes
  useEffect(() => {
    if (sessionId) {
      fetchAll();
    } else {
      // Reset state when no sessionId
      setEngineStatus(null);
      setPatternMatches(null);
      setScenarios(null);
      setError(null);
    }
  }, [sessionId, fetchAll]);

  return {
    engineStatus,
    patternMatches,
    scenarios,
    loading,
    error,
    enginesAvailable: engineStatus?.sophisticated_engines_available || false,
    refetch: fetchAll
  };
};

export default useEnhancedAnalysis;

