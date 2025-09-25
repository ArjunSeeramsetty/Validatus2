import React, { useState } from 'react';
import { 
  Box, 
  Card, 
  TextField, 
  Button, 
  Typography, 
  Alert,
  CircularProgress,
  Container,
  Paper
} from '@mui/material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { loginStart, loginSuccess, loginFailure } from '../store/slices/authSlice';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('demo@validatus.com');
  const [password, setPassword] = useState('demo123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, isAuthenticated } = useAuth();
  const dispatch = useDispatch();

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      // Call AuthContext login - it handles Redux updates internally
      await login(email, password);
      
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ 
      height: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a35 100%)'
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{ width: '100%' }}
      >
        <Paper 
          elevation={24}
          sx={{ 
            p: 4, 
            background: '#1a1a35',
            border: '1px solid #3d3d56',
            borderRadius: 3
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h3" component="h1" sx={{ 
              color: '#e8e8f0', 
              fontWeight: 700,
              mb: 1,
              background: 'linear-gradient(135deg, #1890ff 0%, #52c41a 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Validatus
            </Typography>
            <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 2 }}>
              AI-Powered Strategic Analysis Platform
            </Typography>
            <Typography variant="body2" sx={{ color: '#8c8ca0' }}>
              Sign in to access your strategic analysis dashboard
            </Typography>
          </Box>

          <form onSubmit={handleSubmit}>
            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: '#252547',
                    '& fieldset': {
                      borderColor: '#3d3d56',
                    },
                    '&:hover fieldset': {
                      borderColor: '#1890ff',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1890ff',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#b8b8cc',
                  },
                  '& .MuiInputBase-input': {
                    color: '#e8e8f0',
                  },
                }}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: '#252547',
                    '& fieldset': {
                      borderColor: '#3d3d56',
                    },
                    '&:hover fieldset': {
                      borderColor: '#1890ff',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1890ff',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#b8b8cc',
                  },
                  '& .MuiInputBase-input': {
                    color: '#e8e8f0',
                  },
                }}
              />
            </Box>

            {error && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: 3,
                  backgroundColor: '#2d1b1f',
                  color: '#ff4d4f',
                  '& .MuiAlert-icon': {
                    color: '#ff4d4f'
                  }
                }}
              >
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={loading}
              sx={{
                py: 1.5,
                background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                },
                '&:disabled': {
                  background: '#3d3d56',
                },
                fontSize: '1.1rem',
                fontWeight: 600,
                textTransform: 'none',
                borderRadius: 2,
              }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          <Box sx={{ mt: 4, p: 3, backgroundColor: '#252547', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ color: '#52c41a', mb: 2, textAlign: 'center' }}>
              Demo Credentials
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
              <strong>Email:</strong> demo@validatus.com
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
              <strong>Password:</strong> demo123
            </Typography>
            <Typography variant="caption" sx={{ color: '#8c8ca0', textAlign: 'center', display: 'block' }}>
              Use these credentials to explore the Validatus platform
            </Typography>
          </Box>
        </Paper>
      </motion.div>
    </Container>
  );
};

export default LoginPage;