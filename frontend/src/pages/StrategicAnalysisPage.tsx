import React, { useState } from 'react';
import { 
  Box, Typography, Button, Stepper, Step, StepLabel, Card, CardContent,
  TextField, Chip, Grid, Paper, LinearProgress 
} from '@mui/material';
import { motion } from 'framer-motion';
import { Search, Link as LinkIcon, Analytics } from '@mui/icons-material';
import KnowledgeAcquisitionWizard from '../components/KnowledgeAcquisition/KnowledgeAcquisitionWizard';
import { useNavigate } from 'react-router-dom';

const StrategicAnalysisPage: React.FC = () => {
  const [showWizard, setShowWizard] = useState(false);
  const navigate = useNavigate();

  const steps = [
    'Knowledge Acquisition',
    'Strategic Analysis',
    'Results & Insights'
  ];

  const handleStartAnalysis = () => {
    setShowWizard(true);
  };

  const handleWizardComplete = (data: any) => {
    setShowWizard(false);
    // Navigate to analysis sessions or start the analysis
    navigate('/analysis');
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto', minHeight: '100vh', backgroundColor: '#0f0f23' }}>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Hero Section */}
        <motion.div variants={itemVariants}>
          <Paper sx={{ 
            background: 'linear-gradient(135deg, #1a1a35 0%, #2d2d5f 100%)',
            border: '1px solid #3d3d56',
            borderRadius: 3,
            p: 4,
            mb: 4,
            textAlign: 'center'
          }}>
            <Typography variant="h3" sx={{ 
              color: '#e8e8f0', 
              fontWeight: 700, 
              mb: 2,
              background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Strategic Analysis Platform
            </Typography>
            <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 3, maxWidth: 600, mx: 'auto' }}>
              Transform your business insights with AI-powered strategic analysis across three comprehensive stages
            </Typography>
            
            {/* Quick Start Button */}
            <Button
              variant="contained"
              size="large"
              startIcon={<Analytics />}
              onClick={handleStartAnalysis}
              sx={{
                background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                px: 4,
                py: 1.5,
                borderRadius: 2,
                fontSize: '1.1rem',
                textTransform: 'none',
                fontWeight: 600,
                boxShadow: '0 8px 32px rgba(24, 144, 255, 0.3)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                  boxShadow: '0 12px 40px rgba(24, 144, 255, 0.4)',
                }
              }}
            >
              Start Strategic Analysis
            </Button>
          </Paper>
        </motion.div>

        {/* 3-Stage Workflow Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <motion.div variants={itemVariants}>
              <Card sx={{ 
                background: '#1a1a35', 
                border: '1px solid #3d3d56',
                height: '100%',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'translateY(-4px)' }
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Search sx={{ color: '#1890ff', fontSize: 32, mr: 2 }} />
                    <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                      Stage 1: Knowledge Acquisition
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                    Intelligent web search, URL collection, and content scraping to build comprehensive knowledge base
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <Chip size="small" label="Web Search" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} />
                    <Chip size="small" label="URL Collection" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} />
                    <Chip size="small" label="Content Processing" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={4}>
            <motion.div variants={itemVariants}>
              <Card sx={{ 
                background: '#1a1a35', 
                border: '1px solid #3d3d56',
                height: '100%',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'translateY(-4px)' }
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Analytics sx={{ color: '#52c41a', fontSize: 32, mr: 2 }} />
                    <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                      Stage 2: Strategic Analysis
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                    AI-powered analysis with 28 strategic factors, 18 action layers, and expert persona scoring
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <Chip size="small" label="Layer Scoring" sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }} />
                    <Chip size="small" label="Factor Analysis" sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }} />
                    <Chip size="small" label="Expert AI" sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }} />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} md={4}>
            <motion.div variants={itemVariants}>
              <Card sx={{ 
                background: '#1a1a35', 
                border: '1px solid #3d3d56',
                height: '100%',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'translateY(-4px)' }
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <LinkIcon sx={{ color: '#fa8c16', fontSize: 32, mr: 2 }} />
                    <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                      Stage 3: Results Dashboard
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                    Interactive visualizations, insights dashboard, and comprehensive reporting with export options
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <Chip size="small" label="Visualizations" sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }} />
                    <Chip size="small" label="Insights" sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }} />
                    <Chip size="small" label="Export" sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }} />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Current Active Analyses */}
        <motion.div variants={itemVariants}>
          <Card sx={{ background: '#1a1a35', border: '1px solid #3d3d56', mb: 4 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3, fontWeight: 600 }}>
                Recent Strategic Analyses
              </Typography>
              {/* Display recent analyses or empty state */}
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" sx={{ color: '#b8b8cc', mb: 2 }}>
                  No analyses yet. Start your first strategic analysis above.
                </Typography>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/analysis')}
                  sx={{
                    borderColor: '#1890ff',
                    color: '#1890ff',
                    '&:hover': {
                      borderColor: '#40a9ff',
                      backgroundColor: '#1890ff20'
                    }
                  }}
                >
                  View All Sessions
                </Button>
              </Box>
            </CardContent>
          </Card>
        </motion.div>

        {/* Knowledge Acquisition Wizard */}
        <KnowledgeAcquisitionWizard
          open={showWizard}
          onClose={() => setShowWizard(false)}
          onComplete={handleWizardComplete}
        />
      </motion.div>
    </Box>
  );
};

export default StrategicAnalysisPage;
