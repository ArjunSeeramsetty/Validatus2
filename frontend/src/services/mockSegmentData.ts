/**
 * Mock Segment Data Service
 * Provides comprehensive mock data for all segments when backend API is unavailable
 * This is a temporary solution while backend endpoint registration issues are resolved
 */

export interface MockSegmentData {
  topic_id: string;
  topic_name: string;
  segment: string;
  timestamp: string;
  factors: Record<string, { value: number; confidence: number; name: string }>;
  matched_patterns: Array<{
    pattern_id: string;
    pattern_name: string;
    pattern_type: string;
    confidence: number;
    match_score: number;
    strategic_response: string;
    effect_size_hints: string;
    probability_range: [number, number];
  }>;
  monte_carlo_scenarios: Array<{
    scenario_id: string;
    pattern_id: string;
    pattern_name: string;
    segment: string;
    strategic_response: string;
    kpi_results: Record<string, {
      mean: number;
      median: number;
      std: number;
      min: number;
      max: number;
      confidence_interval_95: [number, number];
      confidence_interval_68: [number, number];
      probability_positive: number;
      probability_target: number;
    }>;
    probability_success: number;
    confidence_interval: [number, number];
    iterations: number;
  }>;
  personas?: Array<{
    name: string;
    age: number;
    value_tier: string;
    market_share: number;
    confidence: number;
    demographics: {
      location: string;
      income: string;
      occupation: string;
    };
    pain_points: string[];
    key_messaging: string[];
  }>;
  rich_content?: any;
  scenario_count: number;
  required_scenarios: number;
  patterns_matched: number;
  content_items_analyzed: number;
}

export function generateMockSegmentData(topicId: string, segment: string): MockSegmentData {
  const segmentLower = segment.toLowerCase();
  
  return {
    topic_id: topicId,
    topic_name: `Analysis for ${topicId}`,
    segment: segmentLower,
    timestamp: new Date().toISOString(),
    factors: getMockFactors(segmentLower),
    matched_patterns: getMockPatterns(segmentLower),
    monte_carlo_scenarios: getMockMonteCarloScenarios(segmentLower),
    personas: segmentLower === 'consumer' ? getMockPersonas() : undefined,
    rich_content: ['product', 'brand', 'experience'].includes(segmentLower) ? getMockRichContent(segmentLower) : undefined,
    scenario_count: segmentLower === 'market' || segmentLower === 'consumer' || segmentLower === 'brand' ? 4 : segmentLower === 'product' ? 3 : 2,
    required_scenarios: segmentLower === 'market' || segmentLower === 'consumer' || segmentLower === 'brand' ? 4 : segmentLower === 'product' ? 3 : 2,
    patterns_matched: 4,
    content_items_analyzed: 5
  };
}

function getMockFactors(segment: string): Record<string, { value: number; confidence: number; name: string }> {
  const factorsBySegment: Record<string, Record<string, { value: number; confidence: number; name: string }>> = {
    market: {
      F1: { value: 0.75, confidence: 0.72, name: 'Market Timing' },
      F2: { value: 0.68, confidence: 0.68, name: 'Market Access' },
      F3: { value: 0.65, confidence: 0.70, name: 'Market Dynamics' },
      F4: { value: 0.80, confidence: 0.75, name: 'Regulatory Environment' },
      F16: { value: 0.77, confidence: 0.70, name: 'Market Size' },
      F19: { value: 0.80, confidence: 0.73, name: 'Market Growth' }
    },
    consumer: {
      F11: { value: 0.75, confidence: 0.70, name: 'Consumer Demand' },
      F12: { value: 0.73, confidence: 0.68, name: 'Willingness to Pay' },
      F13: { value: 0.65, confidence: 0.65, name: 'Customer Loyalty' },
      F14: { value: 0.70, confidence: 0.67, name: 'Purchase Frequency' },
      F15: { value: 0.77, confidence: 0.72, name: 'Adoption Readiness' },
      F20: { value: 0.72, confidence: 0.69, name: 'Target Audience Fit' }
    },
    product: {
      F6: { value: 0.80, confidence: 0.78, name: 'Product Quality' },
      F7: { value: 0.75, confidence: 0.70, name: 'Differentiation' },
      F8: { value: 0.77, confidence: 0.72, name: 'Technical Feasibility' },
      F9: { value: 0.73, confidence: 0.68, name: 'Scalability' },
      F10: { value: 0.83, confidence: 0.75, name: 'Innovation Potential' }
    },
    brand: {
      F21: { value: 0.73, confidence: 0.67, name: 'Brand Positioning' },
      F22: { value: 0.75, confidence: 0.70, name: 'Brand Equity' },
      F23: { value: 0.70, confidence: 0.65, name: 'Virality/Cultural Impact' },
      F24: { value: 0.77, confidence: 0.73, name: 'Brand Trust' },
      F25: { value: 0.65, confidence: 0.68, name: 'Brand Recognition' }
    },
    experience: {
      F26: { value: 0.75, confidence: 0.70, name: 'User Engagement' },
      F27: { value: 0.73, confidence: 0.72, name: 'Customer Satisfaction' },
      F28: { value: 0.77, confidence: 0.75, name: 'User Interface Quality' }
    }
  };
  
  return factorsBySegment[segment] || factorsBySegment.market;
}

function getMockPatterns(segment: string) {
  const patternsBySegment: Record<string, any[]> = {
    market: [
      {
        pattern_id: 'P001',
        pattern_name: 'Market Expansion Opportunity',
        pattern_type: 'Opportunity',
        confidence: 0.75,
        match_score: 0.82,
        strategic_response: 'Focus on geographic expansion and market penetration strategies',
        effect_size_hints: 'High growth potential with moderate risk',
        probability_range: [0.65, 0.85]
      },
      {
        pattern_id: 'P002',
        pattern_name: 'Competitive Advantage Pattern',
        pattern_type: 'Success',
        confidence: 0.70,
        match_score: 0.78,
        strategic_response: 'Leverage unique market position for sustainable growth',
        effect_size_hints: 'Strong competitive moat identified',
        probability_range: [0.70, 0.90]
      },
      {
        pattern_id: 'P003',
        pattern_name: 'Market Timing Optimization',
        pattern_type: 'Adaptation',
        confidence: 0.68,
        match_score: 0.75,
        strategic_response: 'Optimize launch timing based on market readiness',
        effect_size_hints: 'Moderate impact with high timing sensitivity',
        probability_range: [0.60, 0.80]
      },
      {
        pattern_id: 'P004',
        pattern_name: 'Regulatory Compliance Advantage',
        pattern_type: 'Success',
        confidence: 0.72,
        match_score: 0.80,
        strategic_response: 'Use regulatory compliance as competitive differentiator',
        effect_size_hints: 'Strong compliance foundation provides advantage',
        probability_range: [0.68, 0.88]
      }
    ],
    consumer: [
      {
        pattern_id: 'P005',
        pattern_name: 'Consumer Demand Surge',
        pattern_type: 'Opportunity',
        confidence: 0.78,
        match_score: 0.85,
        strategic_response: 'Capitalize on increasing consumer demand with targeted campaigns',
        effect_size_hints: 'High demand growth with strong conversion potential',
        probability_range: [0.70, 0.90]
      },
      {
        pattern_id: 'P006',
        pattern_name: 'Premium Positioning Strategy',
        pattern_type: 'Success',
        confidence: 0.73,
        match_score: 0.82,
        strategic_response: 'Position as premium solution for quality-conscious consumers',
        effect_size_hints: 'Strong willingness to pay identified',
        probability_range: [0.65, 0.85]
      },
      {
        pattern_id: 'P007',
        pattern_name: 'Customer Loyalty Building',
        pattern_type: 'Adaptation',
        confidence: 0.70,
        match_score: 0.77,
        strategic_response: 'Implement loyalty programs and retention strategies',
        effect_size_hints: 'Moderate loyalty potential with room for improvement',
        probability_range: [0.60, 0.80]
      },
      {
        pattern_id: 'P008',
        pattern_name: 'Adoption Acceleration',
        pattern_type: 'Opportunity',
        confidence: 0.75,
        match_score: 0.83,
        strategic_response: 'Accelerate market adoption through education and incentives',
        effect_size_hints: 'High adoption readiness with strong growth potential',
        probability_range: [0.68, 0.88]
      }
    ],
    product: [
      {
        pattern_id: 'P009',
        pattern_name: 'Product Innovation Leadership',
        pattern_type: 'Success',
        confidence: 0.80,
        match_score: 0.88,
        strategic_response: 'Lead market innovation with cutting-edge features',
        effect_size_hints: 'Exceptional innovation potential with strong differentiation',
        probability_range: [0.75, 0.95]
      },
      {
        pattern_id: 'P010',
        pattern_name: 'Quality Excellence Strategy',
        pattern_type: 'Success',
        confidence: 0.77,
        match_score: 0.85,
        strategic_response: 'Focus on superior quality as primary differentiator',
        effect_size_hints: 'High quality standards with strong market appeal',
        probability_range: [0.70, 0.90]
      },
      {
        pattern_id: 'P011',
        pattern_name: 'Technical Feasibility Advantage',
        pattern_type: 'Success',
        confidence: 0.72,
        match_score: 0.80,
        strategic_response: 'Leverage technical capabilities for market advantage',
        effect_size_hints: 'Strong technical foundation with implementation readiness',
        probability_range: [0.65, 0.85]
      }
    ],
    brand: [
      {
        pattern_id: 'P012',
        pattern_name: 'Brand Trust Building',
        pattern_type: 'Adaptation',
        confidence: 0.76,
        match_score: 0.84,
        strategic_response: 'Build brand trust through transparency and reliability',
        effect_size_hints: 'Strong trust foundation with growth potential',
        probability_range: [0.70, 0.90]
      },
      {
        pattern_id: 'P013',
        pattern_name: 'Brand Positioning Optimization',
        pattern_type: 'Adaptation',
        confidence: 0.73,
        match_score: 0.81,
        strategic_response: 'Optimize brand positioning for target market appeal',
        effect_size_hints: 'Good positioning with room for strategic refinement',
        probability_range: [0.65, 0.85]
      },
      {
        pattern_id: 'P014',
        pattern_name: 'Brand Equity Enhancement',
        pattern_type: 'Success',
        confidence: 0.75,
        match_score: 0.83,
        strategic_response: 'Enhance brand equity through consistent value delivery',
        effect_size_hints: 'Strong brand equity potential with market recognition',
        probability_range: [0.68, 0.88]
      },
      {
        pattern_id: 'P015',
        pattern_name: 'Cultural Impact Strategy',
        pattern_type: 'Opportunity',
        confidence: 0.70,
        match_score: 0.78,
        strategic_response: 'Build cultural impact through community engagement',
        effect_size_hints: 'Moderate cultural potential with viral opportunities',
        probability_range: [0.60, 0.80]
      }
    ],
    experience: [
      {
        pattern_id: 'P016',
        pattern_name: 'User Experience Excellence',
        pattern_type: 'Success',
        confidence: 0.78,
        match_score: 0.86,
        strategic_response: 'Deliver exceptional user experience across all touchpoints',
        effect_size_hints: 'High engagement potential with strong satisfaction drivers',
        probability_range: [0.72, 0.92]
      },
      {
        pattern_id: 'P017',
        pattern_name: 'Customer Journey Optimization',
        pattern_type: 'Adaptation',
        confidence: 0.75,
        match_score: 0.83,
        strategic_response: 'Optimize customer journey for seamless experience',
        effect_size_hints: 'Strong journey foundation with optimization opportunities',
        probability_range: [0.68, 0.88]
      }
    ]
  };
  
  return patternsBySegment[segment] || [];
}

function getMockMonteCarloScenarios(segment: string) {
  const scenarioCount = ['market', 'consumer', 'brand'].includes(segment) ? 4 : segment === 'product' ? 3 : 2;
  const scenarios = [];
  
  for (let i = 0; i < scenarioCount; i++) {
    scenarios.push({
      scenario_id: `${segment}_scenario_${i + 1}`,
      pattern_id: `P${String(i + 1).padStart(3, '0')}`,
      pattern_name: `${segment.charAt(0).toUpperCase() + segment.slice(1)} Strategic Pattern ${i + 1}`,
      segment: segment,
      strategic_response: `Strategic recommendation for ${segment} segment pattern ${i + 1}`,
      kpi_results: {
        market_share_increase_pp: {
          mean: 12.5 + i * 2.5,
          median: 12.0 + i * 2.0,
          std: 3.2,
          min: 8.5,
          max: 18.5,
          confidence_interval_95: [8.5, 18.5],
          confidence_interval_68: [10.5, 16.5],
          probability_positive: 0.85 + i * 0.03,
          probability_target: 0.75 + i * 0.05
        },
        revenue_growth_pct: {
          mean: 22.5 + i * 3.0,
          median: 22.0 + i * 2.5,
          std: 4.8,
          min: 15.0,
          max: 32.0,
          confidence_interval_95: [15.0, 32.0],
          confidence_interval_68: [18.0, 28.0],
          probability_positive: 0.88 + i * 0.02,
          probability_target: 0.80 + i * 0.03
        },
        conversion_rate_increase_pp: {
          mean: 18.5 + i * 2.0,
          median: 18.0 + i * 1.5,
          std: 2.8,
          min: 13.0,
          max: 25.0,
          confidence_interval_95: [13.0, 25.0],
          confidence_interval_68: [15.5, 22.5],
          probability_positive: 0.82 + i * 0.04,
          probability_target: 0.78 + i * 0.04
        }
      },
      probability_success: 0.75 + i * 0.05,
      confidence_interval: [0.65 + i * 0.05, 0.85 + i * 0.05],
      iterations: 1000
    });
  }
  
  return scenarios;
}

function getMockPersonas() {
  return [
    {
      name: 'Sarah Chen',
      age: 34,
      value_tier: 'Premium',
      market_share: 0.28,
      confidence: 0.82,
      demographics: {
        location: 'San Francisco Bay Area',
        income: '$120,000-150,000',
        occupation: 'Software Engineer'
      },
      pain_points: [
        'Limited time for research and comparison',
        'Concern about long-term value and durability',
        'Need for professional installation services'
      ],
      key_messaging: [
        'Premium quality with lifetime warranty',
        'Professional installation included',
        'Smart home integration capabilities'
      ]
    },
    {
      name: 'Mike Rodriguez',
      age: 42,
      value_tier: 'Value',
      market_share: 0.35,
      confidence: 0.78,
      demographics: {
        location: 'Austin, Texas',
        income: '$80,000-100,000',
        occupation: 'Construction Manager'
      },
      pain_points: [
        'Budget constraints for home improvements',
        'Need for DIY-friendly solutions',
        'Concern about maintenance requirements'
      ],
      key_messaging: [
        'Best value for quality ratio',
        'Easy DIY installation',
        'Low maintenance design'
      ]
    },
    {
      name: 'Jennifer Kim',
      age: 29,
      value_tier: 'Innovation',
      market_share: 0.22,
      confidence: 0.85,
      demographics: {
        location: 'Seattle, Washington',
        income: '$100,000-130,000',
        occupation: 'Product Manager'
      },
      pain_points: [
        'Want cutting-edge technology features',
        'Need sustainable and eco-friendly options',
        'Desire customizable design options'
      ],
      key_messaging: [
        'Latest smart technology integration',
        '100% sustainable materials',
        'Fully customizable design options'
      ]
    }
  ];
}

function getMockRichContent(segment: string) {
  if (segment === 'product') {
    return {
      features: [
        {
          name: 'Smart Weather Integration',
          description: 'Automatically adjusts based on weather conditions',
          importance: 0.85,
          market_validation: 'High demand from weather-sensitive users'
        },
        {
          name: 'Modular Design System',
          description: 'Customizable components for different space requirements',
          importance: 0.78,
          market_validation: 'Strong preference for flexibility'
        },
        {
          name: 'Energy Efficient Materials',
          description: 'Sustainable materials with low environmental impact',
          importance: 0.82,
          market_validation: 'Growing eco-conscious market segment'
        }
      ],
      competitive_advantages: [
        {
          advantage: 'Superior Weather Resistance',
          strength_score: 0.88,
          explanation: 'Industry-leading 15-year weather warranty'
        },
        {
          advantage: 'Smart Home Integration',
          strength_score: 0.85,
          explanation: 'Seamless integration with major smart home platforms'
        }
      ],
      innovation_opportunities: [
        {
          opportunity: 'Solar Panel Integration',
          impact: 'High revenue potential',
          feasibility: 'Medium complexity',
          timeline: '12-18 months'
        },
        {
          opportunity: 'AI-Powered Climate Control',
          impact: 'Premium pricing opportunity',
          feasibility: 'High complexity',
          timeline: '18-24 months'
        }
      ]
    };
  } else if (segment === 'brand') {
    return {
      positioning: {
        current: 'Quality solutions provider',
        desired: 'Premium ecosystem leader',
        gap_analysis: 'Need to emphasize technology and ecosystem integration',
        strategy: 'Position as innovation leader'
      },
      perception: {
        strengths: ['High quality and durability', 'Strong customer service', 'Reliable warranty coverage'],
        weaknesses: ['Limited brand awareness', 'Premium pricing perception', 'Limited digital presence'],
        market_sentiment: 'Positive but needs technology positioning'
      }
    };
  } else if (segment === 'experience') {
    return {
      journey_stages: [
        {
          stage: 'Discovery',
          touchpoints: ['Website', 'Social media', 'Referrals'],
          pain_points: ['Information overload', 'Complex product options'],
          satisfaction_score: 0.72,
          optimization_opportunities: ['Simplified product comparison', 'Interactive configurator']
        },
        {
          stage: 'Purchase',
          touchpoints: ['Online store', 'Sales team', 'Financing options'],
          pain_points: ['Complex checkout process', 'Limited payment options'],
          satisfaction_score: 0.75,
          optimization_opportunities: ['Streamlined checkout', 'More payment methods']
        }
      ]
    };
  }
  
  return {};
}

