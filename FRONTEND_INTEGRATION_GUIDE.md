# Frontend Integration Guide for New Features

## Overview
This guide explains how to integrate the new backend endpoints into the frontend Results components.

## New React Hooks Created

### 1. `useGrowthDemand(sessionId)`
**Purpose**: Fetch Growth & Demand analysis for Market segment
**Returns**: 
```typescript
{
  growthDemandData: {
    market_size: { score, confidence, value, evidence },
    growth_rate: { score, confidence, cagr, evidence }
  },
  loading: boolean,
  error: string | null
}
```

### 2. `usePersonas(sessionId)`
**Purpose**: Fetch generated consumer personas
**Returns**:
```typescript
{
  personas: Persona[],
  loading: boolean,
  error: string | null
}
```

### 3. `useSegmentPatterns(sessionId, segment)`
**Purpose**: Fetch top 4 patterns for any segment
**Returns**:
```typescript
{
  patternMatches: PatternMatch[],
  scenarios: Record<string, MonteCarloScenario>,
  loading: boolean,
  error: string | null,
  hasPatterns: boolean
}
```

## Integration Instructions

### MarketResults.tsx
**Add Growth & Demand Display**:
```typescript
import { useGrowthDemand } from '../../hooks/useGrowthDemand';
import { useSegmentPatterns } from '../../hooks/useSegmentPatterns';

// In component:
const { growthDemandData } = useGrowthDemand(sessionId);
const { patternMatches, scenarios } = useSegmentPatterns(sessionId, 'market');

// Replace zero scores with:
<Typography>Market Size: Score: {(growthDemandData?.market_size.score * 100).toFixed(2)}</Typography>
<Typography>Growth Rate: Score: {(growthDemandData?.growth_rate.score * 100).toFixed(2)}</Typography>

// Add pattern display (top 4):
{patternMatches.map(pattern => (
  <PatternMatchCard pattern={pattern} scenario={scenarios[pattern.pattern_id]} />
))}
```

### ConsumerResults.tsx
**Add Persona Display**:
```typescript
import { usePersonas } from '../../hooks/usePersonas';
import { useSegmentPatterns } from '../../hooks/useSegmentPatterns';

// In component:
const { personas } = usePersonas(sessionId);
const { patternMatches, scenarios } = useSegmentPatterns(sessionId, 'consumer');

// Replace placeholder with:
{personas.map(persona => (
  <PersonaCard persona={persona} />
))}

// Display top 4 consumer patterns
{patternMatches.map(pattern => (
  <PatternMatchCard pattern={pattern} scenario={scenarios[pattern.pattern_id]} />
))}
```

### ProductResults.tsx
**Add Pattern Display**:
```typescript
import { useSegmentPatterns } from '../../hooks/useSegmentPatterns';

// In component:
const { patternMatches, scenarios } = useSegmentPatterns(sessionId, 'product');

// Display top 4 product patterns
{patternMatches.map(pattern => (
  <PatternMatchCard pattern={pattern} scenario={scenarios[pattern.pattern_id]} />
))}
```

### BrandResults.tsx
**Add Pattern Display**:
```typescript
import { useSegmentPatterns } from '../../hooks/useSegmentPatterns';

// In component:
const { patternMatches, scenarios } = useSegmentPatterns(sessionId, 'brand');

// Display top 4 brand patterns
{patternMatches.map(pattern => (
  <PatternMatchCard pattern={pattern} scenario={scenarios[pattern.pattern_id]} />
))}
```

### ExperienceResults.tsx
**Add Pattern Display**:
```typescript
import { useSegmentPatterns } from '../../hooks/useSegmentPatterns';

// In component:
const { patternMatches, scenarios } = useSegmentPatterns(sessionId, 'experience');

// Display top 4 experience patterns
{patternMatches.map(pattern => (
  <PatternMatchCard pattern={pattern} scenario={scenarios[pattern.pattern_id]} />
))}
```

## Expected Results

### Before Integration
- Market Growth & Demand: 0.00 / 0.00 ❌
- Pattern Library: Consumer only ❌
- Personas: Placeholder text ❌
- Product/Brand/Experience: Empty ❌

### After Integration
- Market Growth & Demand: Actual scores (e.g., 0.72 / 0.68) ✅
- Pattern Library: ALL segments (4 patterns each) ✅
- Personas: 3-5 generated personas ✅
- Product/Brand/Experience: Rich content with patterns ✅

## Testing Checklist

- [ ] Market segment shows actual Growth & Demand scores
- [ ] Market segment shows top 4 market patterns
- [ ] Consumer segment shows 3-5 generated personas
- [ ] Consumer segment shows top 4 consumer patterns
- [ ] Product segment shows top 4 product patterns
- [ ] Brand segment shows top 4 brand patterns
- [ ] Experience segment shows top 4 experience patterns
- [ ] All Monte Carlo simulations display correctly
- [ ] No TypeScript errors
- [ ] No console errors

## Deployment

After integrating and testing locally:
```bash
cd frontend
npm run build
cd ..
git add frontend/
git commit -m "Integrate Growth/Demand, Personas, and Multi-Segment Patterns"
git push origin master
gcloud builds submit --config=cloudbuild.yaml --project=validatus-platform .
```

---

**Note**: The existing `useEnhancedAnalysis` hook will continue to work for backwards compatibility, but the new hooks provide more specific functionality for each feature.

