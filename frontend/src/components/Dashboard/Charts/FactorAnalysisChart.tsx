// frontend/src/components/Dashboard/Charts/FactorAnalysisChart.tsx

import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';
import { motion } from 'framer-motion';

interface FactorCalculation {
  factor_name: string;
  score: number;
  confidence: number;
  formula_components: any;
  calculation_steps: any[];
}

interface FactorAnalysisChartProps {
  data: FactorCalculation[];
  height?: number;
  animated?: boolean;
}

const FactorAnalysisChart: React.FC<FactorAnalysisChartProps> = ({
  data,
  height = 400,
  animated = true
}) => {
  const theme = useTheme();
  
  const chartData = useMemo(() => {
    return data?.map(factor => ({
      factor: factor.factor_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      score: Math.round(factor.score * 100),
      confidence: Math.round(factor.confidence * 100)
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
            {label}
          </Typography>
          <Typography variant="body2" color="primary">
            Score: {payload[0]?.value}%
          </Typography>
          <Typography variant="body2" color="secondary">
            Confidence: {payload[1]?.value}%
          </Typography>
        </Box>
      );
    }
    return null;
  };

  const chartVariants = {
    hidden: { opacity: 0, x: -50 },
    visible: { 
      opacity: 1, 
      x: 0,
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
          No factor analysis data available
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
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis 
            dataKey="factor" 
            tick={{ 
              fill: theme.palette.text.primary,
              fontSize: 11
            }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            tick={{ 
              fill: theme.palette.text.secondary,
              fontSize: 10
            }}
            domain={[0, 100]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar 
            dataKey="score" 
            fill={theme.palette.primary.main}
            name="Score"
            radius={[4, 4, 0, 0]}
          />
          <Bar 
            dataKey="confidence" 
            fill={theme.palette.secondary.main}
            name="Confidence"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

export default FactorAnalysisChart;
