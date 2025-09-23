// frontend/src/components/Export/ExportDialog.tsx

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Box,
  Typography,
  LinearProgress,
  Alert,
  Chip
} from '@mui/material';
import {
  PictureAsPdf as PDFIcon,
  TableChart as ExcelIcon,
  Code as JSONIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface ExportDialogProps {
  open: boolean;
  onClose: () => void;
  sessionId: string;
  onExport: (format: string) => void;
  exportStatus?: {
    format: string;
    status: 'pending' | 'success' | 'error';
    downloadUrl?: string;
  };
}

const ExportDialog: React.FC<ExportDialogProps> = ({
  open,
  onClose,
  sessionId,
  onExport,
  exportStatus
}) => {
  const [selectedFormat, setSelectedFormat] = useState('pdf');

  const exportFormats = [
    {
      value: 'pdf',
      label: 'PDF Report',
      description: 'Comprehensive analysis report with charts and insights',
      icon: <PDFIcon color="error" />,
      size: '~2-5 MB'
    },
    {
      value: 'excel',
      label: 'Excel Workbook',
      description: 'Structured data with multiple sheets for analysis',
      icon: <ExcelIcon color="success" />,
      size: '~1-3 MB'
    },
    {
      value: 'json',
      label: 'JSON Data',
      description: 'Raw structured data for programmatic access',
      icon: <JSONIcon color="info" />,
      size: '~100-500 KB'
    }
  ];

  const handleExport = () => {
    onExport(selectedFormat);
  };

  const handleDownload = () => {
    if (exportStatus?.downloadUrl) {
      window.open(exportStatus.downloadUrl, '_blank');
      onClose();
    }
  };

  const isExporting = exportStatus?.status === 'pending';
  const exportComplete = exportStatus?.status === 'success';
  const exportError = exportStatus?.status === 'error';

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        component: motion.div,
        initial: { scale: 0.8, opacity: 0 },
        animate: { scale: 1, opacity: 1 },
        exit: { scale: 0.8, opacity: 0 },
        transition: { duration: 0.2 }
      }}
    >
      <DialogTitle>
        Export Analysis Results
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Session: {sessionId}
        </Typography>
      </DialogTitle>

      <DialogContent>
        <AnimatePresence mode="wait">
          {isExporting ? (
            <motion.div
              key="exporting"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Box textAlign="center" py={3}>
                <Typography variant="h6" gutterBottom>
                  Preparing Export
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Generating {exportStatus?.format.toUpperCase()} file...
                </Typography>
                <Box mt={2}>
                  <LinearProgress />
                </Box>
              </Box>
            </motion.div>
          ) : exportComplete ? (
            <motion.div
              key="complete"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Box textAlign="center" py={3}>
                <Alert severity="success" sx={{ mb: 2 }}>
                  Export completed successfully!
                </Alert>
                <Typography variant="body1">
                  Your {exportStatus?.format.toUpperCase()} file is ready for download.
                </Typography>
              </Box>
            </motion.div>
          ) : exportError ? (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Alert severity="error">
                Export failed. Please try again.
              </Alert>
            </motion.div>
          ) : (
            <motion.div
              key="select"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <FormControl component="fieldset" fullWidth>
                <FormLabel component="legend" sx={{ mb: 2 }}>
                  Choose export format
                </FormLabel>
                <RadioGroup
                  value={selectedFormat}
                  onChange={(e) => setSelectedFormat(e.target.value)}
                >
                  {exportFormats.map((format) => (
                    <Box key={format.value} mb={1}>
                      <FormControlLabel
                        value={format.value}
                        control={<Radio />}
                        label={
                          <Box display="flex" alignItems="center" gap={2} py={1}>
                            {format.icon}
                            <Box flex={1}>
                              <Typography variant="subtitle2">
                                {format.label}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {format.description}
                              </Typography>
                            </Box>
                            <Chip 
                              label={format.size} 
                              size="small" 
                              variant="outlined" 
                            />
                          </Box>
                        }
                        sx={{
                          border: 1,
                          borderColor: 'divider',
                          borderRadius: 1,
                          m: 0,
                          p: 1,
                          '&:hover': {
                            bgcolor: 'action.hover'
                          }
                        }}
                      />
                    </Box>
                  ))}
                </RadioGroup>
              </FormControl>
            </motion.div>
          )}
        </AnimatePresence>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          Cancel
        </Button>
        {exportComplete ? (
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
          >
            Download File
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={handleExport}
            disabled={isExporting}
          >
            {isExporting ? 'Exporting...' : 'Export'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ExportDialog;
