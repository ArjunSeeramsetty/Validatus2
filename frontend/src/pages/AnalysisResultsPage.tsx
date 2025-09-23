// frontend/src/pages/AnalysisResultsPage.tsx

import React from 'react';
import { useParams } from 'react-router-dom';
import InteractiveDashboard from '../components/Dashboard/InteractiveDashboard';

const AnalysisResultsPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();

  if (!sessionId) {
    return <div>Session ID not found</div>;
  }

  return <InteractiveDashboard sessionId={sessionId} />;
};

export default AnalysisResultsPage;
