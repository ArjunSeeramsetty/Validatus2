// frontend/src/pages/SegmentResultsPage.tsx

import React from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  CircularProgress,
  Alert,
  AlertTitle,
  Button,
  Typography,
  Paper,
} from '@mui/material';
import { Refresh as RefreshIcon, Error as ErrorIcon } from '@mui/icons-material';
import { useSegmentResults } from '../hooks/useSegmentResults';
import SegmentContent from '../components/SegmentContent';
import apiService from '../services/api';

const SegmentResultsPage: React.FC = () => {
  const { topic, segment } = useParams<{ topic: string; segment: string }>();
  const { data, loading, error, refetch } = useSegmentResults(topic || '', segment || '');

  // Loading State
  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="60vh">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading {segment} analysis...
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Retrieving data-driven insights
          </Typography>
        </Box>
      </Container>
    );
  }

  // Error State - NO MOCK DATA FALLBACK
  if (error || !data) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          icon={<ErrorIcon />}
          action={
            <Button color="inherit" size="small" onClick={refetch} startIcon={<RefreshIcon />}>
              Retry
            </Button>
          }
        >
          <AlertTitle>Error Loading Results</AlertTitle>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {error || 'Unable to load results. The data may not be available yet.'}
          </Typography>
          <Typography variant="caption" component="div">
            <strong>Troubleshooting:</strong>
            <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
              <li>Ensure scoring is complete for this topic</li>
              <li>Check that results generation has finished</li>
              <li>Verify API endpoint is accessible</li>
              <li>Topic: {topic || 'Not specified'}</li>
              <li>Segment: {segment || 'Not specified'}</li>
            </ul>
          </Typography>
        </Alert>

        {/* API Status Check */}
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            API Status
          </Typography>
          <Button 
            variant="outlined" 
            onClick={async () => {
              try {
                const health = await apiService.healthCheck();
                alert(JSON.stringify(health, null, 2));
              } catch (err) {
                alert('API health check failed');
              }
            }}
          >
            Check API Health
          </Button>
        </Paper>
      </Container>
    );
  }

  // Success State - Render Actual Data
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          {segment?.charAt(0).toUpperCase() + segment?.slice(1)} Intelligence
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Topic: {topic} • 100% Data-Driven Analysis
        </Typography>
      </Box>

      <SegmentContent 
        segment={segment || ''}
        data={data}
      />
    </Container>
  );
};

export default SegmentResultsPage;
