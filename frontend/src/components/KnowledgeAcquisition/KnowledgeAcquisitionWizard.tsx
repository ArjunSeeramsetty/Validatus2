import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Stepper, Step, StepLabel, Box, TextField, Button,
  Typography, IconButton, LinearProgress, Chip, Alert
} from '@mui/material';
import { Add, Delete, Search, CheckCircle } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useTopics } from '../../hooks/useAnalysisData';

interface KnowledgeAcquisitionWizardProps {
  open: boolean;
  onClose: () => void;
  onComplete: (data: any) => void;
}

const KnowledgeAcquisitionWizard: React.FC<KnowledgeAcquisitionWizardProps> = ({
  open, onClose, onComplete
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [topic, setTopic] = useState('');
  const [description, setDescription] = useState('');
  const [urls, setUrls] = useState<string[]>(['']);
  const [searchQueries, setSearchQueries] = useState<string[]>(['']);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const { createTopic } = useTopics();
  const steps = ['Topic Setup', 'Web Search & URLs', 'Content Processing', 'Vector Store Creation'];

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      handleStartProcessing();
    } else {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleStartProcessing = async () => {
    setProcessing(true);
    setError(null);
    
    try {
      const topicData = {
        topic,
        description,
        urls: urls.filter(url => url.trim()),
        searchQueries: searchQueries.filter(query => query.trim())
      };

      await createTopic(
        topic,
        topicData.urls,
        topicData.searchQueries.length > 0 ? topicData.searchQueries : undefined
      );

      const processingSteps = [
        { progress: 20, message: 'Creating topic in database...' },
        { progress: 40, message: 'Initiating web search queries...' },
        { progress: 60, message: 'Collecting and validating URLs...' },
        { progress: 80, message: 'Scraping content from sources...' },
        { progress: 90, message: 'Processing and analyzing content quality...' },
        { progress: 100, message: 'Creating vector embeddings and knowledge base...' }
      ];

      for (const step of processingSteps) {
        setProgress(step.progress);
        await new Promise(resolve => setTimeout(resolve, 800));
      }

      onComplete(topicData);
    } catch (error: any) {
      setError(error.message || 'Failed to create knowledge base');
      setProcessing(false);
    }
  };

  const addUrl = () => setUrls([...urls, '']);
  const removeUrl = (index: number) => setUrls(urls.filter((_, i) => i !== index));
  const updateUrl = (index: number, value: string) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const addSearchQuery = () => setSearchQueries([...searchQueries, '']);
  const removeSearchQuery = (index: number) => setSearchQueries(searchQueries.filter((_, i) => i !== index));
  const updateSearchQuery = (index: number, value: string) => {
    const newSearchQueries = [...searchQueries];
    newSearchQueries[index] = value;
    setSearchQueries(newSearchQueries);
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ py: 2 }}>
            <TextField
              fullWidth
              label="Analysis Topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Electric Vehicle Market Analysis"
              sx={{ mb: 3 }}
            />
            <TextField
              fullWidth
              label="Description (Optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              multiline
              rows={3}
              placeholder="Brief description of your strategic analysis goals"
            />
          </Box>
        );

      case 1:
        return (
          <Box sx={{ py: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Web Search Queries</Typography>
            {searchQueries.map((query, index) => (
              <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TextField
                  fullWidth
                  label={`Search Query ${index + 1}`}
                  value={query}
                  onChange={(e) => updateSearchQuery(index, e.target.value)}
                  placeholder="e.g., electric vehicle market trends 2024"
                  sx={{ mr: 1 }}
                />
                <IconButton 
                  onClick={() => removeSearchQuery(index)} 
                  disabled={searchQueries.length === 1}
                  sx={{ color: '#ff4d4f' }}
                >
                  <Delete />
                </IconButton>
              </Box>
            ))}
            <Button startIcon={<Add />} onClick={addSearchQuery} sx={{ mb: 3 }}>
              Add Search Query
            </Button>

            <Typography variant="h6" sx={{ mb: 2 }}>Direct URLs (Optional)</Typography>
            {urls.map((url, index) => (
              <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TextField
                  fullWidth
                  label={`URL ${index + 1}`}
                  value={url}
                  onChange={(e) => updateUrl(index, e.target.value)}
                  placeholder="https://example.com/industry-report"
                  sx={{ mr: 1 }}
                />
                <IconButton 
                  onClick={() => removeUrl(index)} 
                  disabled={urls.length === 1}
                  sx={{ color: '#ff4d4f' }}
                >
                  <Delete />
                </IconButton>
              </Box>
            ))}
            <Button startIcon={<Add />} onClick={addUrl}>
              Add URL
            </Button>
          </Box>
        );

      case 2:
        return (
          <Box sx={{ py: 2, textAlign: 'center' }}>
            {!processing ? (
              <>
                <Search sx={{ fontSize: 64, color: '#1890ff', mb: 2 }} />
                <Typography variant="h6" sx={{ mb: 2 }}>Ready to Process Content</Typography>
                <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 3 }}>
                  We'll search the web, collect URLs, scrape content, and create your knowledge base
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
                  <Chip label="Web Search" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} size="small" />
                  <Chip label="Content Extraction" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} size="small" />
                  <Chip label="Quality Analysis" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} size="small" />
                  <Chip label="Vector Embeddings" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} size="small" />
                </Box>
              </>
            ) : (
              <>
                <LinearProgress 
                  variant="determinate" 
                  value={progress} 
                  sx={{ mb: 2, height: 8, borderRadius: 4 }} 
                />
                <Typography variant="h6" sx={{ mb: 2 }}>Processing Content... {progress}%</Typography>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  {progress < 20 && 'Creating topic in database...'}
                  {progress >= 20 && progress < 40 && 'Initiating web search queries...'}
                  {progress >= 40 && progress < 60 && 'Collecting and validating URLs...'}
                  {progress >= 60 && progress < 80 && 'Scraping content from sources...'}
                  {progress >= 80 && progress < 90 && 'Processing and analyzing content quality...'}
                  {progress >= 90 && 'Creating vector embeddings and knowledge base...'}
                </Typography>
              </>
            )}
          </Box>
        );

      case 3:
        return (
          <Box sx={{ py: 2, textAlign: 'center' }}>
            <CheckCircle sx={{ fontSize: 64, color: '#52c41a', mb: 2 }} />
            <Typography variant="h6" sx={{ mb: 2 }}>Knowledge Base Created!</Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 3 }}>
              Your topic is ready for strategic analysis. You can now proceed to Stage 2.
            </Typography>
            <Alert severity="success" sx={{ textAlign: 'left' }}>
              <Typography variant="body2">
                <strong>Next Steps:</strong><br />
                • Review collected knowledge<br />
                • Start strategic analysis<br />
                • View results dashboard
              </Typography>
            </Alert>
          </Box>
        );

      default:
        return null;
    }
  };

  const canProceed = () => {
    if (activeStep === 0) return topic.trim().length > 0;
    if (activeStep === 1) return true;
    return true;
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { 
          background: '#1a1a35', 
          border: '1px solid #3d3d56',
          borderRadius: 2
        }
      }}
    >
      <DialogTitle sx={{ color: '#e8e8f0', borderBottom: '1px solid #3d3d56' }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          Stage 1: Knowledge Acquisition
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel sx={{ 
                '& .MuiStepLabel-label': { color: '#b8b8cc' },
                '& .Mui-active .MuiStepLabel-label': { color: '#1890ff' },
                '& .Mui-completed .MuiStepLabel-label': { color: '#52c41a' }
              }}>
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <AnimatePresence mode="wait">
          <motion.div
            key={activeStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderStepContent(activeStep)}
          </motion.div>
        </AnimatePresence>
      </DialogContent>

      <DialogActions sx={{ p: 3, borderTop: '1px solid #3d3d56' }}>
        <Button onClick={onClose} sx={{ color: '#b8b8cc' }}>
          Cancel
        </Button>
        {activeStep > 0 && (
          <Button onClick={() => setActiveStep(prev => prev - 1)} sx={{ color: '#1890ff' }}>
            Back
          </Button>
        )}
        <Button 
          variant="contained" 
          onClick={handleNext}
          disabled={processing || !canProceed()}
          sx={{
            background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
            }
          }}
        >
          {activeStep === steps.length - 1 ? 'Create Knowledge Base' : 'Next'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KnowledgeAcquisitionWizard;