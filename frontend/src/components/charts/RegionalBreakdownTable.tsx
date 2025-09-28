import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Typography,
  Chip
} from '@mui/material';
import { TrendingUp } from '@mui/icons-material';

interface RegionalData {
  region: string;
  size_2024: number;
  forecast_2033: number;
  cagr: number;
  key_drivers: string[];
}

interface RegionalBreakdownTableProps {
  data: RegionalData[];
}

export default function RegionalBreakdownTable({ data }: RegionalBreakdownTableProps) {
  // Default data if not provided
  const defaultData = [
    {
      region: "Global",
      size_2024: 3500.0,
      forecast_2033: 5800.0,
      cagr: 6.5,
      key_drivers: [
        "Post-COVID outdoor living trends",
        "Smart home technology integration",
        "Premium lifestyle investments"
      ]
    },
    {
      region: "North America",
      size_2024: 997.6,
      forecast_2033: 1580.2,
      cagr: 5.4,
      key_drivers: [
        "High disposable income",
        "Smart pergola adoption",
        "Premium segment growth"
      ]
    },
    {
      region: "Europe",
      size_2024: 1200.0,
      forecast_2033: 2100.0,
      cagr: 7.2,
      key_drivers: [
        "Sustainability focus",
        "Regulatory support",
        "Design innovation"
      ]
    },
    {
      region: "Asia-Pacific",
      size_2024: 890.5,
      forecast_2033: 1680.8,
      cagr: 8.1,
      key_drivers: [
        "Urbanization trends",
        "Rising middle class",
        "Climate adaptation"
      ]
    }
  ];

  const tableData = data && data.length > 0 ? data : defaultData;

  const getCAGRColor = (cagr: number) => {
    if (cagr >= 7) return 'success';
    if (cagr >= 6) return 'warning';
    return 'error';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value * 1000000); // Convert millions to actual currency
  };

  return (
    <Box>
      <TableContainer component={Paper} sx={{ maxHeight: 500 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>
                Region
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>
                2024 Market Size
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>
                2033 Forecast
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>
                CAGR
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>
                Key Growth Drivers
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tableData.map((region, index) => (
              <TableRow key={index} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {region.region}
                    </Typography>
                    {region.region === 'Global' && (
                      <Chip 
                        label="Total" 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {formatCurrency(region.size_2024)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {region.size_2024.toFixed(1)}M
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {formatCurrency(region.forecast_2033)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {region.forecast_2033.toFixed(1)}M
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    icon={<TrendingUp />}
                    label={`${region.cagr.toFixed(1)}%`}
                    color={getCAGRColor(region.cagr)}
                    variant="outlined"
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {(region.key_drivers || []).slice(0, 2).map((driver, driverIndex) => (
                      <Chip
                        key={driverIndex}
                        label={driver}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                    {(region.key_drivers || []).length > 2 && (
                      <Chip
                        label={`+${(region.key_drivers || []).length - 2} more`}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.7rem', fontStyle: 'italic' }}
                      />
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
