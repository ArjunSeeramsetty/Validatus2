// frontend/src/components/Progress/RealTimeProgress.tsx

import React from 'react';
import { Box, Card, CardContent, Typography, LinearProgress, CircularProgress } from '@mui/material';
import { Analytics as AnalyticsIcon } from '@mui/icons-material';

interface RealTimeProgressProps {
  sessionId: string;
}

const RealTimeProgress: React.FC<RealTimeProgressProps> = ({ sessionId }) => {
  return (
    <Card elevation={2}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <AnalyticsIcon color="primary" />
          <Typography variant="h6">
            Analysis Progress
          </Typography>
          <CircularProgress size={20} />
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Processing session: {sessionId}
          </Typography>
          <LinearProgress />
        </Box>

        <Typography variant="body2" color="text.secondary">
          Real-time progress tracking coming soon...
        </Typography>
      </CardContent>
    </Card>
  );
};

export default RealTimeProgress;
