/**
 * Market Results Component
 * Displays comprehensive market analysis including competitors, opportunities, pricing, and growth
 */

import React from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress
} from '@mui/material';
import { 
  TrendingUp, 
  AttachMoney,
  Policy,
  ShowChart
} from '@mui/icons-material';

import type { MarketAnalysisData } from '../../hooks/useAnalysis';

export interface MarketResultsProps {
  data: MarketAnalysisData;  sessionId?: string;
}

const MarketResults: React.FC<MarketResultsProps> = ({ data , sessionId }) => {
  if (!data) {
    return (
      <Typography sx={{ color: '#888' }}>
        No market analysis data available
      </Typography>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        
        {/* Competitor Analysis Section */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#4A148C', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                Competitor Analysis
              </Typography>
              
              {data.competitor_analysis && Object.keys(data.competitor_analysis).length > 0 ? (
                Object.entries(data.competitor_analysis).map(([competitor, details]: [string, any]) => (
                  <Box key={competitor} sx={{ mb: 2, pb: 2, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                    <Typography variant="subtitle2" sx={{ color: '#E1BEE7', fontWeight: 'bold' }}>
                      {competitor}
                    </Typography>
                    <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#F3E5F5', mt: 0.5 }}>
                      {typeof details === 'string' ? details : details.description || 'Competitor information'}
                    </Typography>
                    {details.market_share !== undefined && (
                      <>
                        <Typography variant="caption" sx={{ color: '#E1BEE7', mt: 1, display: 'block' }}>
                          Market Share: {(details.market_share * 100).toFixed(1)}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={details.market_share * 100} 
                          sx={{ 
                            mt: 0.5, 
                            bgcolor: '#7B1FA2',
                            '& .MuiLinearProgress-bar': { bgcolor: '#E1BEE7' }
                          }} 
                        />
                      </>
                    )}
                  </Box>
                ))
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Competitor analysis will appear here after processing market data.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Opportunities Section */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#66BB6A', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Opportunities
              </Typography>
              
              {data.opportunities && data.opportunities.length > 0 ? (
                <List dense>
                  {data.opportunities.slice(0, 5).map((opportunity, index) => (
                    <ListItem key={index} sx={{ px: 0, alignItems: 'flex-start' }}>
                      <ListItemIcon sx={{ minWidth: 28, mt: 0.5 }}>
                        <TrendingUp sx={{ color: 'white', fontSize: 18 }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={opportunity}
                        primaryTypographyProps={{ 
                          fontSize: '0.9rem',
                          color: 'white',
                          fontWeight: 500
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                  Market opportunities will be identified from analysis.
                </Typography>
              )}

              {data.opportunities_rationale && (
                <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic', fontSize: '0.85rem' }}>
                  <strong>Why:</strong> {data.opportunities_rationale}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Market Share Section */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#FFA726', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Market Share
              </Typography>
              
              <Typography variant="body2" sx={{ mb: 2, opacity: 0.9 }}>
                Distribution
              </Typography>
              
              {data.market_share && Object.keys(data.market_share).length > 0 ? (
                Object.entries(data.market_share).map(([segment, share]) => (
                  <Box key={segment} sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>{segment}</Typography>
                      <Typography variant="h6">{(share * 100).toFixed(1)}%</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={share * 100} 
                      sx={{ 
                        bgcolor: '#FFB74D',
                        height: 8,
                        borderRadius: 1,
                        '& .MuiLinearProgress-bar': { bgcolor: 'white', borderRadius: 1 }
                      }} 
                    />
                  </Box>
                ))
              ) : (
                <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                  Market share data will appear here after analysis.
                </Typography>
              )}

              <Typography variant="body2" sx={{ mt: 2, fontSize: '0.85rem', opacity: 0.9 }}>
                Market dynamics and segment distribution based on current data
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Pricing & Switching Section */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#5E35B1', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <AttachMoney sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Pricing & Switching
                </Typography>
              </Box>
              
              {data.pricing_switching && Object.keys(data.pricing_switching).length > 0 ? (
                <Box>
                  {data.pricing_switching.price_range && (
                    <Box sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold' }}>
                        Price Range
                      </Typography>
                      <Typography variant="body1" sx={{ color: 'white', mt: 0.5 }}>
                        {data.pricing_switching.price_range}
                      </Typography>
                    </Box>
                  )}

                  {data.pricing_switching.switching_costs && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ color: '#B39DDB' }}>
                        Switching Costs: <strong>{data.pricing_switching.switching_costs}</strong>
                      </Typography>
                    </Box>
                  )}

                  {data.pricing_switching.insights && data.pricing_switching.insights.length > 0 && (
                    <>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1, color: 'white' }}>
                        Key Insights:
                      </Typography>
                      <List dense>
                        {data.pricing_switching.insights.map((insight: string, index: number) => (
                          <ListItem key={index} sx={{ px: 0 }}>
                            <ListItemText 
                              primary={`â€¢ ${insight}`}
                              primaryTypographyProps={{ fontSize: '0.85rem', color: '#E1BEE7' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Pricing and switching cost analysis will appear here.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Regulation, Tariffs & Supply Chain Section */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#7E57C2', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Policy sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Regulation & Supply Chain
                </Typography>
              </Box>
              
              {data.regulation_tariffs && Object.keys(data.regulation_tariffs).length > 0 ? (
                <Box>
                  {data.regulation_tariffs.key_regulations && data.regulation_tariffs.key_regulations.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 1 }}>
                        Key Regulations:
                      </Typography>
                      {data.regulation_tariffs.key_regulations.map((reg: string, index: number) => (
                        <Typography key={index} variant="body2" sx={{ color: '#E1BEE7', mb: 0.5 }}>
                          â€¢ {reg}
                        </Typography>
                      ))}
                    </Box>
                  )}

                  {data.regulation_tariffs.details && data.regulation_tariffs.details.length > 0 && (
                    <>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1, color: 'white' }}>
                        Impact Analysis:
                      </Typography>
                      <List dense>
                        {data.regulation_tariffs.details.map((detail: string, index: number) => (
                          <ListItem key={index} sx={{ px: 0 }}>
                            <ListItemText 
                              primary={`â€¢ ${detail}`}
                              primaryTypographyProps={{ fontSize: '0.85rem', color: '#E1BEE7' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Regulatory environment analysis will appear here.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Growth & Demand Section */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%', bgcolor: '#5E35B1', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <ShowChart sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Growth & Demand
                </Typography>
              </Box>
              
              {data.growth_demand && Object.keys(data.growth_demand).length > 0 ? (
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      {data.growth_demand.market_size && (
                        <>
                          <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold' }}>
                            Market Size:
                          </Typography>
                          <Typography variant="h5" sx={{ color: 'white', my: 1 }}>
                            {data.growth_demand.market_size}
                          </Typography>
                        </>
                      )}
                      {data.growth_demand.growth_rate && (
                        <Typography variant="body2" sx={{ color: '#E1BEE7' }}>
                          Growth Rate: <strong>{data.growth_demand.growth_rate}</strong>
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    {data.growth_demand.demand_drivers && data.growth_demand.demand_drivers.length > 0 && (
                      <Box>
                        <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 1 }}>
                          Demand Drivers:
                        </Typography>
                        {data.growth_demand.demand_drivers.map((driver: string, index: number) => (
                          <Typography key={index} variant="body2" sx={{ color: '#E1BEE7', mb: 0.5 }}>
                            â€¢ {driver}
                          </Typography>
                        ))}
                      </Box>
                    )}
                  </Grid>
                </Grid>
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Growth and demand analysis will appear here.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Market Fit Section */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#7E57C2', color: 'white', position: 'relative' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Market Fit
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 140, mb: 2 }}>
                <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress
                    variant="determinate"
                    value={(data.market_fit?.overall_score || 0) * 100}
                    size={100}
                    thickness={5}
                    sx={{ color: '#FF5722' }}
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="h3" component="div" sx={{ color: 'white', fontWeight: 'bold' }}>
                      {`${Math.round((data.market_fit?.overall_score || 0) * 100)}%`}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              {data.market_fit && Object.keys(data.market_fit).length > 1 && (
                <List dense>
                  {Object.entries(data.market_fit)
                    .filter(([key]) => key !== 'overall_score')
                    .map(([metric, value]) => (
                      <ListItem key={metric} sx={{ px: 0, py: 0.5 }}>
                        <ListItemText 
                          primary={`${metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${(value * 100).toFixed(0)}%`}
                          primaryTypographyProps={{ fontSize: '0.85rem', color: '#E1BEE7' }}
                        />
                      </ListItem>
                    ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

      </Grid>
    </Box>
  );
};

export default MarketResults;

