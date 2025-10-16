/**
 * Hook for fetching generated consumer personas
 * Fixes the "Consumer personas will be generated from analysis" placeholder
 */
import { useState, useEffect } from 'react';
import axios from 'axios';

interface Persona {
  name: string;
  age: string;
  description: string;
  demographics: {
    location: string;
    income_range: string;
    occupation: string;
    family_status: string;
  };
  psychographics: {
    values: string[];
    lifestyle: string;
    motivations: string[];
  };
  pain_points: string[];
  goals: string[];
  buying_behavior: {
    research_style: string;
    decision_timeline: string;
    influences: string[];
    price_sensitivity: string;
  };
  market_share: number;
  value_tier: string;
  key_messaging: string[];
}

interface PersonasResponse {
  session_id: string;
  personas: Persona[];
  total_personas: number;
  generation_method: string;
  data_driven: boolean;
  generated_at: string;
}

export const usePersonas = (sessionId: string | null) => {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setPersonas([]);
      return;
    }

    const fetchPersonas = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get<PersonasResponse>(
          `/api/v3/enhanced-analysis/personas/${sessionId}`
        );
        setPersonas(response.data.personas);
      } catch (err: any) {
        console.error('Personas fetch error:', err);
        setError(err.response?.data?.detail || err.message);
        setPersonas([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPersonas();
  }, [sessionId]);

  return {
    personas,
    loading,
    error
  };
};

