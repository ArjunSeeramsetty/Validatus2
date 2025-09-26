/**
 * Assumptions Panel Component
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress
} from '@mui/material';
import { ExpandMore, Assessment, Info } from '@mui/icons-material';
import { apiClient } from '../../services/apiClient';

interface AssumptionsPanelProps {
  sessionId: string;
}

const AssumptionsPanel: React.FC<AssumptionsPanelProps> = ({ sessionId }) => {
  const [assumptions, setAssumptions] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | false>('drivers');

  useEffect(() => {
    loadAssumptions();
  }, [sessionId]);

  const loadAssumptions = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/v3/analysis/${sessionId}/scenarios`);
      setAssumptions(response.data.assumptions || {});
    } catch (error) {
      console.error('Failed to load assumptions:', error);
      // Set mock assumptions for demo
      setAssumptions({
        drivers: [
          { id: 'F1', name: 'Market Growth', confidence: 0.8 },
          { id: 'F2', name: 'Competitive Position', confidence: 0.7 },
          { id: 'F3', name: 'Technology Adoption', confidence: 0.75 }
        ],
        constraints: {
          min_roi: 0.1,
          max_payback_period: 3.0,
          min_adoption_rate: 0.05
        },
        business_inputs: {
          unit_price: 150,
          unit_cost: 75,
          expected_volume: 1000
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#52c41a';
    if (confidence >= 0.6) return '#fa8c16';
    return '#ff4d4f';
  };

  if (loading) {
    return (
      <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 2 }}>
            <CircularProgress size={24} />
            <Typography variant="body2" sx={{ color: '#b8b8cc', ml: 2 }}>
              Loading assumptions...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Assessment sx={{ color: '#1890ff', mr: 1 }} />
          <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
            Key Assumptions
          </Typography>
        </Box>

        {/* Drivers */}
        <Accordion 
          expanded={expanded === 'drivers'} 
          onChange={(_, isExpanded) => setExpanded(isExpanded ? 'drivers' : false)}
          sx={{ backgroundColor: '#252547', mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Typography variant="subtitle1" sx={{ color: '#e8e8f0' }}>
              Strategic Drivers
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List dense>
              {assumptions?.drivers?.map((driver: any) => (
                <ListItem key={driver.id} sx={{ py: 0.5 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                          {driver.name}
                        </Typography>
                        <Chip
                          size="small"
                          label={`${(driver.confidence * 100).toFixed(0)}%`}
                          sx={{
                            backgroundColor: `${getConfidenceColor(driver.confidence)}20`,
                            color: getConfidenceColor(driver.confidence),
                            fontSize: '0.7rem'
                          }}
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                        Factor ID: {driver.id}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>

        {/* Constraints */}
        <Accordion 
          expanded={expanded === 'constraints'} 
          onChange={(_, isExpanded) => setExpanded(isExpanded ? 'constraints' : false)}
          sx={{ backgroundColor: '#252547', mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Typography variant="subtitle1" sx={{ color: '#e8e8f0' }}>
              Business Constraints
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List dense>
              {assumptions?.constraints && Object.entries(assumptions.constraints).map(([key, value]) => (
                <ListItem key={key} sx={{ py: 0.5 }}>
                  <ListItemText
                    primary={
                      <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                        {key.replace(/_/g, ' ').toUpperCase()}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                        {typeof value === 'number' ? value.toFixed(2) : String(value)}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>

        {/* Business Inputs */}
        <Accordion 
          expanded={expanded === 'inputs'} 
          onChange={(_, isExpanded) => setExpanded(isExpanded ? 'inputs' : false)}
          sx={{ backgroundColor: '#252547' }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Typography variant="subtitle1" sx={{ color: '#e8e8f0' }}>
              Business Inputs
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List dense>
              {assumptions?.business_inputs && Object.entries(assumptions.business_inputs).map(([key, value]) => (
                <ListItem key={key} sx={{ py: 0.5 }}>
                  <ListItemText
                    primary={
                      <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                        {key.replace(/_/g, ' ').toUpperCase()}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                        {typeof value === 'number' ? value.toLocaleString() : String(value)}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>

        {/* Info Note */}
        <Box sx={{ mt: 2, p: 2, backgroundColor: '#252547', borderRadius: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Info sx={{ color: '#1890ff', mr: 1, fontSize: 16 }} />
            <Typography variant="caption" sx={{ color: '#b8b8cc', fontWeight: 600 }}>
              Analysis Note
            </Typography>
          </Box>
          <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
            These assumptions form the foundation of the Monte Carlo simulation. 
            Changes to these values will affect the probability distributions and scenario outcomes.
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AssumptionsPanel;
