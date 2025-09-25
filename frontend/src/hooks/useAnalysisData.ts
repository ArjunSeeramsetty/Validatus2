import { useState, useEffect, useCallback } from 'react';
import { AnalysisService, SystemStatus, Topic, AnalysisSession } from '../services/analysisService';

export const useSystemStatus = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      setLoading(true);
      const data = await AnalysisService.getSystemStatus();
      setStatus(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch system status');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return { status, loading, error, refetch: fetchStatus };
};

export const useTopics = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTopics = useCallback(async () => {
    try {
      setLoading(true);
      const data = await AnalysisService.getTopics();
      setTopics(data.topics || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch topics');
      // Return mock data if API fails
      setTopics([
        {
          id: '1',
          name: 'Market Analysis',
          description: 'Comprehensive market research and analysis',
          status: 'active',
          url_count: 25,
          knowledge_count: 150,
          created_at: '2024-09-20T10:00:00Z',
          updated_at: '2024-09-20T10:00:00Z'
        },
        {
          id: '2', 
          name: 'Competitive Intelligence',
          description: 'Competitive landscape assessment',
          status: 'active',
          url_count: 18,
          knowledge_count: 89,
          created_at: '2024-09-19T14:30:00Z',
          updated_at: '2024-09-19T14:30:00Z'
        },
        {
          id: '3',
          name: 'Financial Performance',
          description: 'Financial metrics and performance analysis',
          status: 'processing',
          url_count: 32,
          knowledge_count: 0,
          created_at: '2024-09-21T09:15:00Z',
          updated_at: '2024-09-21T09:15:00Z'
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  const createTopic = useCallback(async (topic: string, urls: string[], searchQueries?: string[]) => {
    try {
      const result = await AnalysisService.createTopic(topic, urls, searchQueries);
      await fetchTopics(); // Refresh the list
      return result;
    } catch (err: any) {
      throw new Error(err.message || 'Failed to create topic');
    }
  }, [fetchTopics]);

  useEffect(() => {
    fetchTopics();
  }, [fetchTopics]);

  return { topics, loading, error, refetch: fetchTopics, createTopic };
};

export const useAnalysisSessions = () => {
  const [sessions, setSessions] = useState<AnalysisSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock data for sessions
  useEffect(() => {
    setSessions([
      {
        id: 'session-1',
        topic: 'Market Entry Strategy',
        user_id: '1',
        status: 'completed',
        progress: 100,
        enhanced_analytics: true,
        created_at: '2024-09-20T10:00:00Z',
        updated_at: '2024-09-20T10:30:00Z',
        results: {
          insights: 15,
          recommendations: 8,
          risk_factors: 5
        }
      },
      {
        id: 'session-2',
        topic: 'Competitive Landscape',
        user_id: '1', 
        status: 'running',
        progress: 75,
        enhanced_analytics: false,
        created_at: '2024-09-21T09:00:00Z',
        updated_at: '2024-09-21T09:15:00Z'
      },
      {
        id: 'session-3',
        topic: 'Financial Performance Review',
        user_id: '1',
        status: 'running', 
        progress: 45,
        enhanced_analytics: true,
        created_at: '2024-09-21T11:00:00Z',
        updated_at: '2024-09-21T11:30:00Z'
      }
    ]);
  }, []);

  const createSession = useCallback(async (
    topic: string,
    userId: string,
    analysisParameters?: Record<string, any>,
    useEnhancedAnalytics?: boolean
  ) => {
    try {
      setLoading(true);
      const result = await AnalysisService.createAnalysisSession(
        topic, 
        userId, 
        analysisParameters, 
        useEnhancedAnalytics
      );
      
      // Add to local state
      const newSession: AnalysisSession = {
        id: result.session_id,
        topic: result.topic,
        user_id: result.user_id,
        status: 'created' as const,
        progress: 0,
        enhanced_analytics: result.enhanced_analytics,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      setSessions(prev => [newSession, ...prev]);
      return result;
    } catch (err: any) {
      throw new Error(err.message || 'Failed to create analysis session');
    } finally {
      setLoading(false);
    }
  }, []);

  return { sessions, loading, error, createSession };
};

export const usePhaseEMetrics = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      const [orchestrationHealth, cachePerformance, enhancedMetrics] = await Promise.allSettled([
        AnalysisService.getOrchestrationHealth(),
        AnalysisService.getCachePerformance(),
        AnalysisService.getEnhancedMetrics()
      ]);

      setMetrics({
        orchestration: orchestrationHealth.status === 'fulfilled' ? orchestrationHealth.value : null,
        cache: cachePerformance.status === 'fulfilled' ? cachePerformance.value : null,
        enhanced: enhancedMetrics.status === 'fulfilled' ? enhancedMetrics.value : null
      });
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch Phase E metrics');
    } finally {
      setLoading(false);
    }
  }, []);

  const invalidateCache = useCallback(async (pattern?: string) => {
    try {
      const result = await AnalysisService.invalidateCache(pattern);
      await fetchMetrics(); // Refresh metrics
      return result;
    } catch (err: any) {
      throw new Error(err.message || 'Failed to invalidate cache');
    }
  }, [fetchMetrics]);

  return { metrics, loading, error, fetchMetrics, invalidateCache };
};
