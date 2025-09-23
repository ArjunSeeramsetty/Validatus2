// frontend/src/store/slices/analysisSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AnalysisSession {
  session_id: string;
  topic: string;
  user_id: string;
  status: string;
  created_at: string;
  completed_at?: string;
  progress_percentage: number;
}

interface AnalysisState {
  sessions: AnalysisSession[];
  currentSession: AnalysisSession | null;
  loading: boolean;
  error: string | null;
}

const initialState: AnalysisState = {
  sessions: [],
  currentSession: null,
  loading: false,
  error: null,
};

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    setSessions: (state, action: PayloadAction<AnalysisSession[]>) => {
      state.sessions = action.payload;
    },
    setCurrentSession: (state, action: PayloadAction<AnalysisSession>) => {
      state.currentSession = action.payload;
    },
    updateSessionProgress: (state, action: PayloadAction<{ sessionId: string; progress: number }>) => {
      const session = state.sessions.find(s => s.session_id === action.payload.sessionId);
      if (session) {
        session.progress_percentage = action.payload.progress;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const { 
  setSessions, 
  setCurrentSession, 
  updateSessionProgress, 
  setLoading, 
  setError, 
  clearError 
} = analysisSlice.actions;
export default analysisSlice.reducer;
