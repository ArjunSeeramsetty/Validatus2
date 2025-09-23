// frontend/src/store/slices/resultsSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiClient } from '../../services/apiClient';

interface AnalysisResults {
  session_id: string;
  topic: string;
  user_id: string;
  status: string;
  layer_scores: LayerScore[];
  factor_calculations: FactorCalculation[];
  segment_scores: SegmentScore[];
  overall_metrics: any;
  insights: string[];
  recommendations: string[];
  metadata: any;
}

interface LayerScore {
  layer_name: string;
  score: number;
  confidence: number;
  insights: string[];
  evidence_summary: string;
}

interface FactorCalculation {
  factor_name: string;
  score: number;
  confidence: number;
  formula_components: any;
  calculation_steps: any[];
}

interface SegmentScore {
  segment_name: string;
  attractiveness_score: number;
  risk_factors: string[];
  opportunities: string[];
  market_size_estimate: number;
}

interface ResultsState {
  currentResults: AnalysisResults | null;
  resultsList: AnalysisResults[];
  loading: boolean;
  error: string | null;
  selectedSession: string | null;
  exportStatus: {
    [sessionId: string]: {
      format: string;
      status: 'pending' | 'success' | 'error';
      downloadUrl?: string;
    };
  };
}

const initialState: ResultsState = {
  currentResults: null,
  resultsList: [],
  loading: false,
  error: null,
  selectedSession: null,
  exportStatus: {},
};

// Async thunks
export const fetchAnalysisResults = createAsyncThunk(
  'results/fetchAnalysisResults',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`/api/v3/analysis/sessions/${sessionId}/results`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch results');
    }
  }
);

export const fetchResultsList = createAsyncThunk(
  'results/fetchResultsList',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`/api/v3/analysis/results/summary?user_id=${userId}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch results list');
    }
  }
);

export const exportResults = createAsyncThunk(
  'results/exportResults',
  async ({ sessionId, format, userId }: { sessionId: string; format: string; userId: string }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/api/v3/analysis/sessions/${sessionId}/export`, {
        format,
        user_id: userId,
      });
      return { sessionId, format, ...response.data };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Export failed');
    }
  }
);

const resultsSlice = createSlice({
  name: 'results',
  initialState,
  reducers: {
    setSelectedSession: (state, action: PayloadAction<string>) => {
      state.selectedSession = action.payload;
    },
    clearResults: (state) => {
      state.currentResults = null;
      state.selectedSession = null;
      state.error = null;
    },
    resetExportStatus: (state, action: PayloadAction<string>) => {
      delete state.exportStatus[action.payload];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch analysis results
      .addCase(fetchAnalysisResults.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnalysisResults.fulfilled, (state, action) => {
        state.loading = false;
        state.currentResults = action.payload;
      })
      .addCase(fetchAnalysisResults.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch results list
      .addCase(fetchResultsList.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchResultsList.fulfilled, (state, action) => {
        state.loading = false;
        state.resultsList = action.payload;
      })
      .addCase(fetchResultsList.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Export results
      .addCase(exportResults.pending, (state, action) => {
        const { sessionId, format } = action.meta.arg;
        state.exportStatus[sessionId] = { format, status: 'pending' };
      })
      .addCase(exportResults.fulfilled, (state, action) => {
        const { sessionId, downloadUrl } = action.payload;
        if (state.exportStatus[sessionId]) {
          state.exportStatus[sessionId].status = 'success';
          state.exportStatus[sessionId].downloadUrl = downloadUrl;
        }
      })
      .addCase(exportResults.rejected, (state, action) => {
        const { sessionId } = action.meta.arg;
        if (state.exportStatus[sessionId]) {
          state.exportStatus[sessionId].status = 'error';
        }
      });
  },
});

export const { setSelectedSession, clearResults, resetExportStatus } = resultsSlice.actions;
export default resultsSlice.reducer;
