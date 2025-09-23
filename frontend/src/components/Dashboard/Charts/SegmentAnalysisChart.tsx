// frontend/src/components/Dashboard/Charts/SegmentAnalysisChart.tsx

import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';
import { motion } from 'framer-motion';

interface SegmentScore {
  segment_name: string;
  attractiveness_score: number;
  risk_factors: string[];
  opportunities: string[];
  market_size_estimate: number;
}

interface SegmentAnalysisChartProps {
  data: SegmentScore[];
  height?: number;
  animated?: boolean;
}

const SegmentAnalysisChart: React.FC<SegmentAnalysisChartProps> = ({
  data,
  height = 400,
  animated = true
}) => {
  const theme = useTheme();
  
  const chartData = useMemo(() => {
    return data?.map((segment, index) => ({
      segment: segment.segment_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      attractiveness: Math.round(segment.attractiveness_score * 100),
      marketSize: segment.market_size_estimate,
      riskCount: segment.risk_factors?.length || 0,
      opportunityCount: segment.opportunities?.length || 0,
      index
    })) || [];
  }, [data]);

  const COLORS = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.info.main,
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
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
            {data.segment}
          </Typography>
          <Typography variant="body2" color="primary">
            Attractiveness: {data.attractiveness}%
          </Typography>
          <Typography variant="body2" color="secondary">
            Market Size: {data.marketSize?.toLocaleString() || 'N/A'}
          </Typography>
          <Typography variant="body2" color="error">
            Risk Factors: {data.riskCount}
          </Typography>
          <Typography variant="body2" color="success">
            Opportunities: {data.opportunityCount}
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
          No segment analysis data available
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
        <ScatterChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis 
            type="number" 
            dataKey="attractiveness" 
            name="Attractiveness"
            domain={[0, 100]}
            tick={{ 
              fill: theme.palette.text.secondary,
              fontSize: 10
            }}
            label={{ 
              value: 'Attractiveness Score (%)', 
              position: 'insideBottom', 
              offset: -10,
              style: { textAnchor: 'middle', fill: theme.palette.text.secondary }
            }}
          />
          <YAxis 
            type="number" 
            dataKey="marketSize" 
            name="Market Size"
            tick={{ 
              fill: theme.palette.text.secondary,
              fontSize: 10
            }}
            label={{ 
              value: 'Market Size', 
              angle: -90, 
              position: 'insideLeft',
              style: { textAnchor: 'middle', fill: theme.palette.text.secondary }
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Scatter 
            dataKey="attractiveness" 
            fill={theme.palette.primary.main}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

export default SegmentAnalysisChart;
