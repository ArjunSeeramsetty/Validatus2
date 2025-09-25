// frontend/src/pages/AnalysisResultsPage.tsx

import React from 'react';
import { useParams } from 'react-router-dom';
import AnalysisResultsDashboard from '../components/Results/AnalysisResultsDashboard';
import InteractiveDashboard from '../components/Dashboard/InteractiveDashboard';

const AnalysisResultsPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();

  // If no sessionId, show the general results dashboard
  if (!sessionId) {
    return <AnalysisResultsDashboard />;
  }

  // If sessionId provided, show the interactive dashboard for that session
  return <InteractiveDashboard sessionId={sessionId} />;
};

export default AnalysisResultsPage;
