// frontend/src/pages/DashboardPage.tsx

import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const DashboardPage: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Dashboard implementation coming soon...
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardPage;
