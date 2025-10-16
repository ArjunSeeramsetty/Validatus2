# Validatus2 - User Guide

**Version**: 3.1.0  
**Last Updated**: October 16, 2025  
**Audience**: End Users, Business Analysts, Strategic Planners  

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Topic](#creating-your-first-topic)
3. [Understanding the Workflow](#understanding-the-workflow)
4. [URLs Tab](#urls-tab)
5. [Content Tab](#content-tab)
6. [Scoring Tab](#scoring-tab)
7. [Results Tab](#results-tab)
8. [Interpreting Results](#interpreting-results)
9. [Pattern Insights](#pattern-insights)
10. [Best Practices](#best-practices)
11. [FAQs](#faqs)
12. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing Validatus2

**Web Interface**:
- URL: https://your-validatus-frontend-domain.com
- Login with your credentials
- Dashboard loads automatically

### Platform Overview

Validatus2 is a strategic analysis platform that helps you:
- 📊 **Analyze market opportunities**
- 👥 **Understand consumer behavior**
- 🛠️ **Evaluate product potential**
- 🎯 **Assess brand positioning**
- ✨ **Optimize user experience**

### Main Navigation

```
┌─────────────────────────────────────┐
│  HOME   TOPICS   RESULTS   SETTINGS │
├─────────────────────────────────────┤
│                                     │
│  Topic List                         │
│  ├─ Topic 1                         │
│  ├─ Topic 2                         │
│  └─ Topic 3                         │
│                                     │
└─────────────────────────────────────┘
```

---

## Creating Your First Topic

### Step 1: Navigate to Topic Creation

1. Click **"Create New Topic"** button
2. You'll see a form with several fields

### Step 2: Fill Out Topic Details

**Required Fields**:

**1. Topic Name** (Required)
```
Example: "Outdoor Pergola Market Analysis in Czech Republic"
```
- Be specific and descriptive
- Include geography if relevant
- Keep under 100 characters

**2. Topic Description** (Optional but recommended)
```
Example: "Comprehensive analysis of the outdoor living pergola market 
in Czech Republic, focusing on consumer demand, competitive landscape, 
and growth opportunities for smart/bioclimatic pergola solutions."
```
- Provide context
- Mention key areas of interest
- Include target audience if applicable

**3. Search Queries** (Optional)
```
Example queries:
- "pergola market Czech Republic"
- "outdoor living trends Europe"
- "smart pergola technology"
- "bioclimatic pergola demand"
```
- 3-5 queries recommended
- Mix broad and specific terms
- Include synonyms and variants

**4. Initial URLs** (Optional)
```
Example URLs:
- https://www.industry-report-site.com/pergola-market
- https://www.competitor-site.com/products
- https://www.news-site.com/outdoor-living-trends
```
- Add high-quality sources
- Industry reports work well
- Competitor websites are valuable

### Step 3: Create Topic

1. Click **"Create Topic"** button
2. System will:
   - Create topic in database
   - Start URL collection (if search queries provided)
   - Begin content scraping
   - Queue for analysis

### Step 4: Monitor Progress

Watch the status indicator:
- 🟡 **Created**: Topic exists, processing starting
- 🔵 **URL Collection**: Gathering relevant URLs
- 🟢 **Content Scraping**: Downloading and analyzing content
- 🟣 **Scoring**: Running expert analysis
- ✅ **Complete**: Results ready to view

---

## Understanding the Workflow

### Complete Analysis Pipeline

```
┌──────────────────────┐
│  1. TOPIC CREATION   │
│  User defines topic  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  2. URL COLLECTION   │
│  52 URLs gathered    │
│  (Google Search API) │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  3. CONTENT SCRAPING │
│  18 documents        │
│  45,237 words total  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  4. V2.0 SCORING     │
│  210 Layers          │
│  28 Factors          │
│  5 Segments          │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  5. RESULTS          │
│  Interactive         │
│  dashboard           │
└──────────────────────┘
```

**Typical Timeline**:
- URL Collection: 2-5 minutes
- Content Scraping: 5-10 minutes
- Scoring Analysis: 10-20 minutes
- **Total**: 20-35 minutes

---

## URLs Tab

### What You'll See

**URL List**:
- Source URL
- Relevance score (0-1)
- Collection date
- Status (collected, scraped, failed)

**Actions Available**:
- View URL details
- Remove unwanted URLs
- Add additional URLs manually
- Refresh collection

### Understanding Relevance Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 0.8-1.0 | Highly relevant | Keep |
| 0.6-0.8 | Moderately relevant | Review |
| 0.4-0.6 | Somewhat relevant | Consider removing |
| 0-0.4 | Low relevance | Remove |

### Adding URLs Manually

1. Click **"Add URL"** button
2. Paste URL
3. System will:
   - Validate URL
   - Scrape content
   - Add to analysis queue

---

## Content Tab

### What You'll See

**Content Cards**:
- Document title
- Source URL
- Word count
- Quality score (0-1)
- Scraping date

**Quality Metrics** (8 metrics):
1. **Relevance**: How well it matches topic (0-1)
2. **Authority**: Source credibility (0-1)
3. **Freshness**: Content recency (0-1)
4. **Depth**: Comprehensiveness (0-1)
5. **Readability**: Text clarity (0-1)
6. **Sentiment**: Emotional tone (-1 to 1)
7. **Factuality**: Verifiable claims (0-1)
8. **Uniqueness**: Original content (0-1)

### Content Quality Indicators

**High Quality** (>0.7):
- ✅ Authoritative source
- ✅ Recent content
- ✅ Comprehensive coverage
- ✅ Well-written

**Medium Quality** (0.5-0.7):
- ⚠️ Some gaps in coverage
- ⚠️ Older content
- ⚠️ Average writing quality

**Low Quality** (<0.5):
- ❌ Unreliable source
- ❌ Outdated
- ❌ Thin content
- ❌ Poor quality

### Actions Available

- **View Full Content**: See complete scraped text
- **Remove**: Exclude from analysis
- **Re-scrape**: Fetch fresh content
- **Export**: Download content

---

## Scoring Tab

### What You'll See

**Scoring Status**:
- Current phase (Layer scoring, Factor calculation, Segment aggregation)
- Progress indicator (0-100%)
- Estimated time remaining
- Expert persona currently analyzing

### Scoring Phases

**Phase 1: Layer Scoring** (210 layers)
- 10 expert personas analyze content
- Each persona scores 21 layers
- Takes 10-15 minutes

**Phase 2: Factor Calculation** (28 factors)
- Layers aggregated into factors
- Mathematical formulas applied
- Takes 2-3 minutes

**Phase 3: Segment Aggregation** (5 segments)
- Factors combined into segments
- Final scores calculated
- Takes 1-2 minutes

### Expert Personas

While scoring, you'll see which persona is active:

1. 📊 **Market Dynamics Analyst**
2. 🧠 **Consumer Psychology Expert**
3. 🚀 **Product Innovation Strategist**
4. 🎯 **Brand Positioning Specialist**
5. ✨ **User Experience Designer**
6. 🔍 **Competitive Intelligence Analyst**
7. ⚙️ **Operational Excellence Consultant**
8. 💰 **Financial Performance Analyst**
9. ⚠️ **Risk Management Advisor**
10. 📋 **Strategic Planning Director**

---

## Results Tab

### Tab Overview

Results are organized into 5 tabs:
1. **Market** - Market dynamics and opportunities
2. **Consumer** - Consumer behavior and insights
3. **Product** - Product features and innovation
4. **Brand** - Brand positioning and perception
5. **Experience** - User journey and touchpoints

### Understanding the Layout

Each tab contains:
```
┌─────────────────────────────────────────┐
│  Segment Score: 48.5%  📊               │
│  (Donut chart showing score)            │
├─────────────────────────────────────────┤
│  Key Metrics                            │
│  ├─ Current Market: 45.2%               │
│  ├─ Addressable Market: 67.8%           │
│  └─ Growth Potential: 72.1%             │
├─────────────────────────────────────────┤
│  Strategic Insights                     │
│  • Insight 1 (from LLM analysis)        │
│  • Insight 2                            │
│  • Insight 3                            │
├─────────────────────────────────────────┤
│  🎯 Pattern Insights (NEW)              │
│  Pattern Cards with Monte Carlo         │
└─────────────────────────────────────────┘
```

### Market Tab

**What You'll Find**:
- **Market Opportunities**: Growth areas identified
- **Competitor Analysis**: Key competitors and their positioning
- **Market Share**: Distribution across segments
- **Pricing & Switching**: Price ranges and switching costs
- **Regulation & Supply Chain**: Regulatory environment
- **Growth & Demand**: Market size and growth rate
- **Market Fit**: Overall market-product fit score

**Example Insights**:
- "Strong demand in suburban markets (72% growth potential)"
- "Limited competition in smart pergola segment"
- "Regulatory environment favorable with EU standards"

---

### Consumer Tab

**What You'll Find**:
- **Recommendations**: Strategic actions to take
- **Challenges**: Consumer pain points
- **Top Motivators**: What drives purchase decisions
- **Relevant Personas**: Target customer profiles
- **Target Audience**: Demographics and psychographics
- **Consumer Fit**: Product-market fit for consumers

**Example Personas**:
```
Name: Quality-Conscious Homeowner
Age: 45-60
Description: Values durability and design, willing to pay 
premium for quality outdoor living solutions
```

---

### Product Tab

**What You'll Find**:
- **Product Features**: Key features and their importance
- **Competitive Positioning**: How product compares
- **Innovation Opportunities**: Areas for improvement
- **Technical Specifications**: Technical details
- **Product Roadmap**: Development timeline
- **Product Fit**: Product-market fit score

**Feature Importance Levels**:
- 🔴 Critical (>0.8): Must-have features
- 🟡 Important (0.6-0.8): Strong differentiators
- 🟢 Nice-to-have (<0.6): Enhancement opportunities

---

### Brand Tab

**What You'll Find**:
- **Brand Positioning**: Current market position
- **Brand Perception**: How consumers view brand
- **Competitor Brands**: Competitive brand landscape
- **Brand Opportunities**: Growth areas
- **Messaging Strategy**: Communication approach
- **Brand Fit**: Brand-market fit score

**Positioning Metrics**:
- Heritage & Innovation balance
- Trust & Reputation strength
- Market differentiation level
- Cultural relevance score

---

### Experience Tab

**What You'll Find**:
- **User Journey**: End-to-end customer experience
- **Touchpoints**: Interaction points and their quality
- **Pain Points**: Friction areas in journey
- **Experience Metrics**: Quantitative measurements
- **Improvement Recommendations**: Enhancement suggestions
- **Experience Fit**: Experience-market fit score

**Journey Stages**:
1. Awareness
2. Consideration
3. Decision
4. Purchase
5. Post-Purchase
6. Loyalty

---

## Pattern Insights

### What Are Pattern Insights?

Pattern Insights use the **Pattern Library** (P001-P041) to identify strategic patterns in your data and generate probabilistic scenarios using Monte Carlo simulation.

### How to Read Pattern Cards

**Pattern Card Structure**:
```
┌──────────────────────────────────────────┐
│ P003: Premium Feature Upsell            │
│ Confidence: 72% | Type: Opportunity      │
├──────────────────────────────────────────┤
│ Strategic Response:                      │
│ "Smart/bioclimatic feature positioning;  │
│  energy efficiency messaging"            │
├──────────────────────────────────────────┤
│ Expected Impact:                         │
│ "Premium adoption +15-20 pp;             │
│  ATV +€3k-€5k"                          │
├──────────────────────────────────────────┤
│ Monte Carlo Results (1000 simulations)  │
│ ▼ Click to expand                        │
└──────────────────────────────────────────┘
```

### Pattern Types

**🟢 Success Patterns**:
- What's working well
- Proven strategies
- Best practices

**🔴 Fragility Patterns**:
- Vulnerability areas
- Risk factors
- Weak points

**🔵 Adaptation Patterns**:
- Market changes
- Required adjustments
- Evolution needs

**🟡 Opportunity Patterns**:
- Growth areas
- Untapped potential
- Innovation spaces

### Understanding Confidence Scores

| Confidence | Meaning | Action |
|------------|---------|--------|
| 80-100% | Very strong match | Implement immediately |
| 60-80% | Good match | Prioritize |
| 40-60% | Moderate match | Consider |
| 0-40% | Weak match | Monitor |

### Monte Carlo Simulation Results

**What You'll See** (when you expand pattern card):

**KPI: premium_adoption_increase_pp**
- **Mean**: 17.2% (expected average outcome)
- **95% Confidence Interval**: [12.1%, 22.3%]
  - "We're 95% confident the outcome will be in this range"
- **Probability of Success**: 100%
  - "Chance of positive outcome"
- **Standard Deviation**: 3.1% (variability/risk)

**How to Interpret**:

✅ **High Confidence (narrow CI)**:
```
Mean: 17%
95% CI: [15%, 19%]  ← Only 4% range
Interpretation: Very predictable outcome
```

⚠️ **Low Confidence (wide CI)**:
```
Mean: 17%
95% CI: [5%, 29%]  ← 24% range
Interpretation: High uncertainty
```

### Real Example

**Pattern**: P003 - Premium Feature Upsell  
**Confidence**: 72%  
**Type**: Opportunity  

**Strategic Response**:
"Position smart/bioclimatic features prominently. Emphasize energy efficiency and technology benefits. Create tiered pricing structure."

**Expected Impact**:
- Premium adoption: +15-20 percentage points
- Average transaction value: +€3,000-€5,000

**Monte Carlo Results**:
```
KPI: Premium Adoption Increase
├─ Mean: 17.2%
├─ 95% CI: [12.1%, 22.3%]
├─ Success Probability: 100%
└─ Risk Level: Low (SD: 3.1%)

KPI: ATV Increase (EUR)
├─ Mean: €4,000
├─ 95% CI: [€2,700, €5,300]
├─ Success Probability: 99.8%
└─ Risk Level: Medium (SD: €800)
```

**Translation**: "If we implement this strategy, we expect premium adoption to increase by about 17%, with 95% confidence it will be between 12% and 22%. There's virtually no chance of a negative outcome."

---

## Best Practices

### Creating Effective Topics

**DO**:
- ✅ Be specific about geography and industry
- ✅ Provide detailed description
- ✅ Include 3-5 search queries
- ✅ Add high-quality initial URLs
- ✅ Review URL relevance before scraping

**DON'T**:
- ❌ Use vague topic names
- ❌ Skip the description
- ❌ Rely only on search queries OR only on manual URLs
- ❌ Include low-quality sources

### Example Topics

**Good** ✅:
```
Topic: "Premium Bioclimatic Pergola Market in Central Europe"
Description: "Analysis of the high-end outdoor living market 
for smart pergolas with automated louvres in CZ, PL, HU..."
Search Queries:
- "bioclimatic pergola Central Europe"
- "smart outdoor living premium segment"
- "automated louvre system market"
```

**Bad** ❌:
```
Topic: "Pergolas"
Description: ""
Search Queries: []
```

### Maximizing Analysis Quality

1. **Provide Context**: Detailed description helps LLM understand
2. **Diverse Sources**: Mix industry reports, competitors, news
3. **Recent Content**: Prefer fresh content (< 6 months old)
4. **Quality Over Quantity**: 20 good URLs > 100 poor URLs
5. **Review Before Scoring**: Remove irrelevant URLs

### Interpreting Results

1. **Look at All Segments**: Don't focus on just one score
2. **Read the Insights**: LLM-generated insights provide context
3. **Check Pattern Matches**: Patterns provide actionable strategies
4. **Review Confidence**: Higher confidence = more reliable
5. **Compare Factors**: See which factors drive segment scores

---

## FAQs

### General Questions

**Q: How long does analysis take?**  
A: Typically 20-35 minutes for complete analysis (URL collection → Results)

**Q: Can I analyze in different languages?**  
A: Yes, but English content yields best results currently

**Q: How many topics can I create?**  
A: No hard limit, but recommend 10-20 active topics for organization

**Q: Can I re-run analysis?**  
A: Yes, click "Re-analyze" to refresh with latest data

### Scoring Questions

**Q: What do the scores mean?**  
A: Scores are 0-100% indicating strength/viability in that dimension

**Q: Why are my scores low?**  
A: Could indicate:
- Weak market fit
- Limited content quality
- Early-stage concept
- Data gaps

**Q: Can I improve scores?**  
A: Yes, by:
- Adding better URLs
- Providing more context
- Re-scraping with updated content

### Pattern Questions

**Q: What if no patterns match?**  
A: Means your situation is unique or scores don't trigger any patterns. This is normal for novel concepts.

**Q: Should I implement all patterns?**  
A: No, prioritize by:
1. Highest confidence
2. Biggest expected impact
3. Easiest to implement

**Q: How accurate are Monte Carlo predictions?**  
A: Confidence intervals show range. Wider intervals = more uncertainty. Real outcomes typically fall within 95% CI.

---

## Troubleshooting

### Common Issues

#### No URLs Collected

**Symptoms**: URL tab empty after 5+ minutes

**Causes**:
- Search queries too specific
- API rate limit reached
- No results for queries

**Solutions**:
1. Broaden search queries
2. Add manual URLs
3. Wait and retry

---

#### Poor Quality Content

**Symptoms**: Content quality scores < 0.5

**Causes**:
- Low-authority sources
- Irrelevant content
- Outdated information

**Solutions**:
1. Remove low-quality URLs
2. Add authoritative sources
3. Use recent content

---

#### Scoring Stuck

**Symptoms**: Scoring progress stops at X%

**Causes**:
- LLM API timeout
- Rate limiting
- Server error

**Solutions**:
1. Wait 5 minutes and refresh
2. Check system status
3. Contact support if persists

---

#### Results Show Zero

**Symptoms**: Segment scores show 0% or N/A

**Causes**:
- Scoring incomplete
- Data extraction error
- Database sync issue

**Solutions**:
1. Wait for scoring to complete
2. Refresh page
3. Re-run analysis

---

#### Patterns Not Showing

**Symptoms**: No pattern insights in Results tab

**Causes**:
- Scores don't match any patterns
- Pattern matching not complete
- Sophisticated engines disabled

**Solutions**:
1. Check if scoring is complete
2. Verify segment scores are reasonable
3. Check engine status endpoint

---

## Getting Help

### Documentation
- **Main Guide**: VALIDATUS2_COMPLETE_IMPLEMENTATION_GUIDE.md
- **Deployment**: DEPLOYMENT_GUIDE.md
- **Development**: DEVELOPMENT_HISTORY.md

### Support Channels
- **GitHub Issues**: https://github.com/ArjunSeeramsetty/Validatus2/issues
- **Email**: support@validatus.com (if available)

### System Status
- **Backend Health**: https://validatus-backend-ssivkqhvhq-uc.a.run.app/health
- **Engine Status**: https://validatus-backend-ssivkqhvhq-uc.a.run.app/api/v3/enhanced-analysis/formula-status

---

**Version**: 3.1.0  
**Last Updated**: October 16, 2025  
**Feedback**: Please report issues or suggestions via GitHub Issues

