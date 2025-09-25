import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  FormControl, InputLabel, Select, MenuItem, Box, Typography,
  FormControlLabel, Checkbox, Chip, LinearProgress, Alert,
  Grid, Card, CardContent, List, ListItem, ListItemIcon,
  ListItemText, Divider
} from '@mui/material';
import {
  Download, PictureAsPdf, TableChart, Slideshow, Share,
  CheckCircle, Schedule, Error, CloudDownload
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { StrategicAnalysisService } from '../../services/strategicAnalysisService';

interface ExportDialogProps {
  open: boolean;
  onClose: () => void;
  sessionId: string;
  analysisData?: any;
}

interface ExportOption {
  format: 'pdf' | 'excel' | 'powerpoint';
  name: string;
  description: string;
  icon: React.ReactNode;
  features: string[];
  estimatedSize: string;
}

const ExportDialog: React.FC<ExportDialogProps> = ({
  open, onClose, sessionId, analysisData
}) => {
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'excel' | 'powerpoint'>('pdf');
  const [includeCharts, setIncludeCharts] = useState(true);
  const [includeData, setIncludeData] = useState(true);
  const [includeInsights, setIncludeInsights] = useState(true);
  const [includeRecommendations, setIncludeRecommendations] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const exportOptions: ExportOption[] = [
    {
      format: 'pdf',
      name: 'PDF Report',
      description: 'Professional report with charts and insights',
      icon: <PictureAsPdf sx={{ color: '#ff4d4f' }} />,
      features: ['Executive Summary', 'Interactive Charts', 'Detailed Analysis', 'Recommendations'],
      estimatedSize: '2-5 MB'
    },
    {
      format: 'excel',
      name: 'Excel Workbook',
      description: 'Data analysis with raw data and calculations',
      icon: <TableChart sx={{ color: '#52c41a' }} />,
      features: ['Raw Data Tables', 'Calculation Sheets', 'Pivot Tables', 'Charts'],
      estimatedSize: '1-3 MB'
    },
    {
      format: 'powerpoint',
      name: 'PowerPoint Presentation',
      description: 'Executive presentation with key insights',
      icon: <Slideshow sx={{ color: '#1890ff' }} />,
      features: ['Executive Summary', 'Key Insights', 'Strategic Recommendations', 'Visual Charts'],
      estimatedSize: '3-8 MB'
    }
  ];

  const handleExport = async () => {
    setExporting(true);
    setError(null);
    setProgress(0);

    try {
      // Simulate export progress
      const progressSteps = [
        { progress: 20, message: 'Preparing analysis data...' },
        { progress: 40, message: 'Generating charts and visualizations...' },
        { progress: 60, message: 'Formatting content for export...' },
        { progress: 80, message: 'Compiling final document...' },
        { progress: 100, message: 'Export complete!' }
      ];

      for (const step of progressSteps) {
        setProgress(step.progress);
        await new Promise(resolve => setTimeout(resolve, 800));
      }

      // Call the actual export service
      const result = await StrategicAnalysisService.exportResults(sessionId, selectedFormat);
      
      setDownloadUrl(result.download_url);
      setExporting(false);
    } catch (err: any) {
      setError(err.message || 'Export failed');
      setExporting(false);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      window.open(downloadUrl, '_blank');
      onClose();
    }
  };

  const selectedOption = exportOptions.find(option => option.format === selectedFormat);

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
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Download sx={{ color: '#1890ff' }} />
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Export Analysis Results
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {!exporting && !downloadUrl ? (
          <>
            {/* Format Selection */}
            <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2, fontWeight: 600 }}>
              Choose Export Format
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 4 }}>
              {exportOptions.map((option) => (
                <Grid item xs={12} md={4} key={option.format}>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      sx={{
                        background: selectedFormat === option.format ? '#1890ff20' : '#252547',
                        border: selectedFormat === option.format ? '2px solid #1890ff' : '1px solid #3d3d56',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        '&:hover': {
                          borderColor: '#1890ff',
                          backgroundColor: '#1890ff10'
                        }
                      }}
                      onClick={() => setSelectedFormat(option.format)}
                    >
                      <CardContent sx={{ p: 3, textAlign: 'center' }}>
                        <Box sx={{ mb: 2 }}>
                          {option.icon}
                        </Box>
                        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 1, fontWeight: 600 }}>
                          {option.name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                          {option.description}
                        </Typography>
                        <Box sx={{ mb: 2 }}>
                          {option.features.map((feature, index) => (
                            <Chip
                              key={index}
                              label={feature}
                              size="small"
                              sx={{
                                backgroundColor: '#1890ff20',
                                color: '#1890ff',
                                mr: 0.5,
                                mb: 0.5,
                                fontSize: '0.75rem'
                              }}
                            />
                          ))}
                        </Box>
                        <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                          Estimated size: {option.estimatedSize}
                        </Typography>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>

            {/* Export Options */}
            <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2, fontWeight: 600 }}>
              Export Options
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeCharts}
                    onChange={(e) => setIncludeCharts(e.target.checked)}
                    sx={{
                      color: '#1890ff',
                      '&.Mui-checked': { color: '#1890ff' }
                    }}
                  />
                }
                label={
                  <Box>
                    <Typography sx={{ color: '#e8e8f0' }}>Include Charts & Visualizations</Typography>
                    <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                      Add interactive charts, graphs, and visual analysis
                    </Typography>
                  </Box>
                }
              />
              
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeData}
                    onChange={(e) => setIncludeData(e.target.checked)}
                    sx={{
                      color: '#1890ff',
                      '&.Mui-checked': { color: '#1890ff' }
                    }}
                  />
                }
                label={
                  <Box>
                    <Typography sx={{ color: '#e8e8f0' }}>Include Raw Data</Typography>
                    <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                      Include underlying data tables and calculations
                    </Typography>
                  </Box>
                }
              />
              
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeInsights}
                    onChange={(e) => setIncludeInsights(e.target.checked)}
                    sx={{
                      color: '#1890ff',
                      '&.Mui-checked': { color: '#1890ff' }
                    }}
                  />
                }
                label={
                  <Box>
                    <Typography sx={{ color: '#e8e8f0' }}>Include Key Insights</Typography>
                    <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                      Add strategic insights and analysis findings
                    </Typography>
                  </Box>
                }
              />
              
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeRecommendations}
                    onChange={(e) => setIncludeRecommendations(e.target.checked)}
                    sx={{
                      color: '#1890ff',
                      '&.Mui-checked': { color: '#1890ff' }
                    }}
                  />
                }
                label={
                  <Box>
                    <Typography sx={{ color: '#e8e8f0' }}>Include Recommendations</Typography>
                    <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                      Add strategic recommendations and action items
                    </Typography>
                  </Box>
                }
              />
            </Box>

            {/* Export Summary */}
            {selectedOption && (
              <Box sx={{ p: 2, backgroundColor: '#252547', borderRadius: 1, border: '1px solid #3d3d56' }}>
                <Typography variant="subtitle1" sx={{ color: '#e8e8f0', mb: 1, fontWeight: 600 }}>
                  Export Summary
                </Typography>
                <List dense>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      {selectedOption.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={`Format: ${selectedOption.name}`}
                      primaryTypographyProps={{ color: '#e8e8f0', fontSize: '0.9rem' }}
                    />
                  </ListItem>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CheckCircle sx={{ color: '#52c41a', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary={`Size: ${selectedOption.estimatedSize}`}
                      primaryTypographyProps={{ color: '#b8b8cc', fontSize: '0.9rem' }}
                    />
                  </ListItem>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Schedule sx={{ color: '#fa8c16', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Estimated time: 30-60 seconds"
                      primaryTypographyProps={{ color: '#b8b8cc', fontSize: '0.9rem' }}
                    />
                  </ListItem>
                </List>
              </Box>
            )}
          </>
        ) : exporting ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CloudDownload sx={{ fontSize: 64, color: '#1890ff', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
              Generating Export...
            </Typography>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                mb: 2,
                height: 8,
                borderRadius: 4,
                backgroundColor: '#3d3d56',
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #1890ff 0%, #52c41a 100%)',
                  borderRadius: 4
                }
              }}
            />
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              {progress < 20 && 'Preparing analysis data...'}
              {progress >= 20 && progress < 40 && 'Generating charts and visualizations...'}
              {progress >= 40 && progress < 60 && 'Formatting content for export...'}
              {progress >= 60 && progress < 80 && 'Compiling final document...'}
              {progress >= 80 && 'Export complete!'}
            </Typography>
          </Box>
        ) : downloadUrl ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CheckCircle sx={{ fontSize: 64, color: '#52c41a', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
              Export Ready!
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 3 }}>
              Your {selectedFormat.toUpperCase()} export has been generated successfully.
            </Typography>
            <Alert severity="info" sx={{ backgroundColor: '#1890ff10', border: '1px solid #1890ff30', mb: 3 }}>
              <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                Download link will expire in 7 days. Save the file to your device.
              </Typography>
            </Alert>
          </Box>
        ) : null}

        {error && (
          <Alert severity="error" sx={{ backgroundColor: '#2d1b1f', border: '1px solid #ef4444', mt: 2 }}>
            {error}
          </Alert>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3, borderTop: '1px solid #3d3d56' }}>
        <Button onClick={onClose} sx={{ color: '#b8b8cc' }}>
          Cancel
        </Button>
        {downloadUrl ? (
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleDownload}
            sx={{
              background: 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #389e0d 0%, #52c41a 100%)',
              }
            }}
          >
            Download {selectedFormat.toUpperCase()}
          </Button>
        ) : (
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleExport}
            disabled={exporting}
            sx={{
              background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
              },
              '&:disabled': {
                backgroundColor: '#3d3d56',
                color: '#8c8ca0'
              }
            }}
          >
            {exporting ? 'Exporting...' : 'Export'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ExportDialog;