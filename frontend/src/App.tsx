// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { motion } from 'framer-motion';

// Store and services
import { store } from './store/store';
import { AuthProvider } from './contexts/AuthContext';
import { SocketProvider } from './contexts/SocketContext';

// Layout components
import MainLayout from './components/Layout/MainLayout';
import LoadingScreen from './components/Common/LoadingScreen';
import ErrorBoundary from './components/Common/ErrorBoundary';

// Page components
import DashboardPage from './pages/DashboardPage';
import TopicManagementPage from './pages/TopicManagementPage';
import AnalysisSessionsPage from './pages/AnalysisSessionsPage';
import AnalysisResultsPage from './pages/AnalysisResultsPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import EnhancedAnalyticsPage from './pages/EnhancedAnalyticsPage';

// Protected route component
import ProtectedRoute from './components/Auth/ProtectedRoute';

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Create theme with dark mode support
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1890ff',
      light: '#40a9ff',
      dark: '#096dd9',
    },
    secondary: {
      main: '#52c41a',
      light: '#73d13d',
      dark: '#389e0d',
    },
    background: {
      default: '#0f0f23',
      paper: '#1a1a35',
    },
    text: {
      primary: '#e8e8f0',
      secondary: '#b8b8cc',
    },
    divider: '#3d3d56',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 600,
      color: '#e8e8f0',
    },
    h2: {
      fontWeight: 600,
      color: '#e8e8f0',
    },
    h3: {
      fontWeight: 600,
      color: '#e8e8f0',
    },
    h4: {
      fontWeight: 600,
      color: '#e8e8f0',
    },
    h5: {
      fontWeight: 600,
      color: '#e8e8f0',
    },
    h6: {
      fontWeight: 600,
      color: '#e8e8f0',
    },
    body1: {
      color: '#e8e8f0',
    },
    body2: {
      color: '#b8b8cc',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1a35',
          border: '1px solid #3d3d56',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1a35',
          border: '1px solid #3d3d56',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <SnackbarProvider 
              maxSnack={3}
              anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
              dense
              preventDuplicate
            >
              <AuthProvider>
                <SocketProvider>
                <Router
                  future={{
                    v7_startTransition: true,
                    v7_relativeSplatPath: true
                  }}
                >
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Routes>
                      {/* Public routes */}
                      <Route path="/login" element={<LoginPage />} />
                      
                      {/* Protected routes */}
                      <Route path="/" element={
                        <ProtectedRoute>
                          <MainLayout />
                        </ProtectedRoute>
                      }>
                        <Route index element={<Navigate to="/dashboard" replace />} />
                        <Route path="dashboard" element={<DashboardPage />} />
                        <Route path="topics" element={<TopicManagementPage />} />
                        <Route path="analysis" element={<AnalysisSessionsPage />} />
                        <Route path="results/:sessionId" element={<AnalysisResultsPage />} />
                        <Route path="enhanced-analytics" element={<EnhancedAnalyticsPage />} />
                        <Route path="enhanced-analytics/:sessionId" element={<EnhancedAnalyticsPage />} />
                        <Route path="settings" element={<SettingsPage />} />
                      </Route>
                      
                      {/* Catch all route */}
                      <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                  </motion.div>
                </Router>
                </SocketProvider>
              </AuthProvider>
            </SnackbarProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </Provider>
    </ErrorBoundary>
  );
};

export default App;
