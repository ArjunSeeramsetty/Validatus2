import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress
} from '@mui/material';
import { Business, TrendingUp, Star, Speed } from '@mui/icons-material';

interface CompetitorData {
  name: string;
  market_share: number;
  usp: string;
  positioning: string;
  strengths: string[];
}

interface CompetitorLandscapeProps {
  data: {
    market_leaders?: CompetitorData[];
    market_concentration?: any;
    competitive_insights?: string[];
    emerging_trends?: string[];
  };
}

export default function CompetitorLandscape({ data }: CompetitorLandscapeProps) {
  // Ensure data is not undefined
  const safeData = data || {};
  
  // Default competitor data
  const defaultCompetitors = [
    {
      name: "Renson",
      market_share: 12.5,
      usp: "Premium architectural solutions",
      positioning: "High-end design leader",
      strengths: ["Innovation", "Quality", "Brand recognition"]
    },
    {
      name: "Corradi",
      market_share: 8.7,
      usp: "Italian craftsmanship",
      positioning: "Luxury outdoor living",
      strengths: ["Design excellence", "Premium materials", "Customization"]
    },
    {
      name: "Luxos",
      market_share: 6.8,
      usp: "Smart technology integration",
      positioning: "Tech-forward solutions",
      strengths: ["IoT integration", "Automation", "Energy efficiency"]
    },
    {
      name: "IQ Outdoor Living",
      market_share: 5.2,
      usp: "Modular systems",
      positioning: "Flexible installations",
      strengths: ["Modularity", "Quick installation", "Cost efficiency"]
    }
  ];

  const competitors = safeData?.market_leaders || defaultCompetitors;
  const marketConcentration = safeData?.market_concentration || {
    top_5_share: 38.7,
    hhi_index: 0.15,
    competitive_intensity: "High"
  };
  const emergingTrends = safeData?.emerging_trends || [
    "Sustainability focus driving material innovation",
    "Direct-to-consumer channels gaining traction",
    "Customization and personalization increasing",
    "Smart technology becoming standard"
  ];

  const getMarketShareColor = (share: number) => {
    if (share >= 10) return 'success';
    if (share >= 5) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Market Concentration Overview */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Business />
                Market Concentration Analysis
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary" gutterBottom>
                      {marketConcentration.top_5_share}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Top 5 Market Share
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="secondary" gutterBottom>
                      {marketConcentration.hhi_index}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      HHI Index
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box textAlign="center">
                    <Chip
                      label={marketConcentration.competitive_intensity}
                      color={marketConcentration.competitive_intensity === 'High' ? 'error' : 'warning'}
                      variant="filled"
                      sx={{ fontSize: '1rem', padding: '8px 16px' }}
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Competitive Intensity
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Competitor Analysis Table */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp />
                Market Leaders Analysis
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Company</TableCell>
                      <TableCell>Market Share</TableCell>
                      <TableCell>Unique Selling Proposition</TableCell>
                      <TableCell>Positioning</TableCell>
                      <TableCell>Key Strengths</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {competitors.map((competitor, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {competitor.name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={competitor.market_share}
                              sx={{ width: 60, height: 8 }}
                              color={getMarketShareColor(competitor.market_share)}
                            />
                            <Typography variant="body2">
                              {competitor.market_share}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {competitor.usp}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {competitor.positioning}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {(competitor.strengths || []).map((strength, strengthIndex) => (
                              <Chip
                                key={strengthIndex}
                                label={strength}
                                size="small"
                                variant="outlined"
                                sx={{ fontSize: '0.7rem' }}
                              />
                            ))}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Emerging Trends */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Star />
                Emerging Trends
              </Typography>
              <Box sx={{ mt: 2 }}>
                {(emergingTrends || []).map((trend, index) => (
                  <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="body2">
                      {trend}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Competitive Insights */}
        {safeData?.competitive_insights && safeData.competitive_insights.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Speed />
                  Competitive Insights
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {(safeData.competitive_insights || []).map((insight, index) => (
                    <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                      <Typography variant="body2">
                        {insight}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
