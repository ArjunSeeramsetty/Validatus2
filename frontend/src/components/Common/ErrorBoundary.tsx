import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { ErrorOutline, Refresh } from '@mui/icons-material';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      error,
      errorInfo
    });
    
    // Log the error to console for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            backgroundColor: '#0f0f23',
            p: 3
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Paper 
              sx={{ 
                p: 4, 
                maxWidth: 500, 
                textAlign: 'center',
                background: '#1a1a35',
                border: '1px solid #3d3d56'
              }}
            >
              <ErrorOutline 
                sx={{ 
                  fontSize: 64, 
                  color: '#ff4d4f', 
                  mb: 2 
                }} 
              />
              
              <Typography 
                variant="h5" 
                sx={{ 
                  color: '#e8e8f0', 
                  fontWeight: 600, 
                  mb: 2 
                }}
              >
                Something went wrong
              </Typography>
              
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#b8b8cc', 
                  mb: 3,
                  lineHeight: 1.6
                }}
              >
                We're sorry, but something unexpected happened. 
                Please try refreshing the page or contact support if the problem persists.
              </Typography>
              
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <Box 
                  sx={{ 
                    p: 2, 
                    backgroundColor: '#252547', 
                    borderRadius: 1, 
                    mb: 3,
                    textAlign: 'left'
                  }}
                >
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      color: '#ff4d4f',
                      fontFamily: 'monospace',
                      wordBreak: 'break-word'
                    }}
                  >
                    {this.state.error.toString()}
                  </Typography>
                </Box>
              )}
              
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={this.handleReload}
                sx={{
                  background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                  },
                  textTransform: 'none',
                  fontWeight: 600
                }}
              >
                Reload Page
              </Button>
            </Paper>
          </motion.div>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;