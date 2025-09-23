// frontend/src/store/store.ts
import { configureStore } from '@reduxjs/toolkit';

// Slice imports
import authSlice from './slices/authSlice';
import topicsSlice from './slices/topicsSlice';
import analysisSlice from './slices/analysisSlice';
import resultsSlice from './slices/resultsSlice';
import uiSlice from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    topics: topicsSlice,
    analysis: analysisSlice,
    results: resultsSlice,
    ui: uiSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
