// frontend/src/store/slices/topicsSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Topic {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  document_count: number;
  status: string;
}

interface TopicsState {
  topics: Topic[];
  selectedTopic: Topic | null;
  loading: boolean;
  error: string | null;
}

const initialState: TopicsState = {
  topics: [],
  selectedTopic: null,
  loading: false,
  error: null,
};

const topicsSlice = createSlice({
  name: 'topics',
  initialState,
  reducers: {
    setTopics: (state, action: PayloadAction<Topic[]>) => {
      state.topics = action.payload;
    },
    setSelectedTopic: (state, action: PayloadAction<Topic>) => {
      state.selectedTopic = action.payload;
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

export const { setTopics, setSelectedTopic, setLoading, setError, clearError } = topicsSlice.actions;
export default topicsSlice.reducer;
