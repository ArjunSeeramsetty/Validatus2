// frontend/src/components/Dashboard/Charts/LayerScoresChart.tsx

import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';
import { motion } from 'framer-motion';

interface LayerScore {
  layer_name: string;
  score: number;
  confidence: number;
  insights: string[];
}

interface LayerScoresChartProps {
  data: LayerScore[];
  height?: number;
  animated?: boolean;
}

const LayerScoresChart: React.FC<LayerScoresChartProps> = ({
  data,
  height = 400,
  animated = true
}) => {
  const theme = useTheme();
  
  const chartData = useMemo(() => {
    return data?.map(layer => ({
      layer: layer.layer_name.charAt(0).toUpperCase() + layer.layer_name.slice(1),
      score: Math.round(layer.score * 100),
      confidence: Math.round(layer.confidence * 100),
      fullMark: 100
    })) || [];
  }, [data]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            bgcolor: 'background.paper',
            p: 2,
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            boxShadow: 2
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            {label} Layer
          </Typography>
          <Typography variant="body2" color="primary">
            Score: {payload[0].value}%
          </Typography>
          <Typography variant="body2" color="secondary">
            Confidence: {payload[1]?.value || payload[0].payload.confidence}%
          </Typography>
        </Box>
      );
    }
    return null;
  };

  const chartVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { duration: 0.8, ease: "easeOut" }
    }
  };

  if (!chartData.length) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height={height}
      >
        <Typography color="text.secondary">
          No layer score data available
        </Typography>
      </Box>
    );
  }

  return (
    <motion.div
      initial={animated ? "hidden" : "visible"}
      animate="visible"
      variants={chartVariants}
    >
      <ResponsiveContainer width="100%" height={height}>
        <RadarChart data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
          <PolarGrid stroke={theme.palette.divider} />
          <PolarAngleAxis 
            dataKey="layer" 
            tick={{ 
              fill: theme.palette.text.primary,
              fontSize: 12
            }}
          />
          <PolarRadiusAxis 
            angle={45} 
            domain={[0, 100]}
            tick={{ 
              fill: theme.palette.text.secondary,
              fontSize: 10
            }}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke={theme.palette.primary.main}
            fill={theme.palette.primary.main}
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Radar
            name="Confidence"
            dataKey="confidence"
            stroke={theme.palette.secondary.main}
            fill={theme.palette.secondary.main}
            fillOpacity={0.1}
            strokeWidth={1}
            strokeDasharray="5 5"
          />
          <Legend />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

export default LayerScoresChart;
