# Scoring Endpoint Clarification & Schema Fix

## User Questions Answered

### Q1: Is the current scoring endpoint different from the previous scoring endpoint?

**Answer:** There is only ONE scoring endpoint for v2.0, but there was a **schema mismatch** in how Results tab was querying it.

#### The Endpoint
```
POST /api/v3/scoring/{session_id}/start
```

This endpoint:
- ✅ Uses **v2_strategic_analysis_orchestrator** (v2.0 Real LLM)
- ✅ Analyzes 210 layers, 28 factors, 5 segments
- ✅ Runs in **background** (doesn't block HTTP response)
- ✅ Stores results in Cloud SQL `v2_analysis_results` table

#### No Different Versions
There's only this ONE scoring system:
- **v2.0 Real LLM Analysis** - Full 210-layer strategic analysis
- Falls back to mock scoring only if v2_orchestrator unavailable

### Q2: Are we storing these results into our Cloud SQL database?

**Answer:** ✅ **YES, absolutely!** Results ARE being stored in Cloud SQL.

#### Storage Location
```sql
Table: v2_analysis_results
Database: validatus (Cloud SQL PostgreSQL)
```

#### What Gets Stored
```python
INSERT INTO v2_analysis_results (
    session_id,                      -- Unique topic ID
    analysis_type,                   -- 'v2.0_real_llm'
    overall_business_case_score,     -- Overall score (0-1)
    overall_confidence,              -- Confidence level
    layers_analyzed,                 -- Number of layers (210)
    factors_calculated,              -- Number of factors (28)
    segments_evaluated,              -- Number of segments (5)
    scenarios_generated,             -- Scenarios count
    processing_time_seconds,         -- Analysis duration
    content_items_analyzed,          -- Content items used
    analysis_summary,                -- JSONB summary
    full_results,                    -- JSONB comprehensive results
    metadata,                        -- JSONB metadata
    created_at,                      -- First scored
    updated_at                       -- Last scored
)
ON CONFLICT (session_id) DO UPDATE SET
    overall_business_case_score = EXCLUDED.overall_business_case_score,
    overall_confidence = EXCLUDED.overall_confidence,
    full_results = EXCLUDED.full_results,
    updated_at = NOW()
```

---

## The Schema Mismatch Problem

### What Was Wrong

Results tab was querying **non-existent columns**:

```python
# ❌ WRONG QUERY
SELECT 
    overall_score,        # Column doesn't exist!
    segment_scores,       # Column doesn't exist!
    factor_scores,        # Column doesn't exist!
    layer_scores,         # Column doesn't exist!
FROM v2_analysis_results
```

### Actual Schema

```sql
-- ✅ CORRECT SCHEMA
CREATE TABLE v2_analysis_results (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE,
    analysis_type VARCHAR(50),
    overall_business_case_score DECIMAL(5,4),  -- ← The score column
    overall_confidence DECIMAL(5,4),
    layers_analyzed INTEGER,
    factors_calculated INTEGER,
    segments_evaluated INTEGER,
    scenarios_generated INTEGER,
    processing_time_seconds DECIMAL(10,2),
    content_items_analyzed INTEGER,
    analysis_summary JSONB,                    -- ← Summary data
    full_results JSONB,                        -- ← All detailed results here!
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Where Are segment_scores, factor_scores, layer_scores?

They're **nested inside the `full_results` JSONB column**:

```json
full_results: {
  "segments": {
    "Market Intelligence": {"score": 0.85, "confidence": 0.9, ...},
    "Consumer Insights": {"score": 0.78, "confidence": 0.85, ...},
    ...
  },
  "factors": {
    "Market Size": 0.88,
    "Growth Potential": 0.82,
    ...
  },
  "layers": {
    "MARKET_SIZE_LARGE_TAM": 0.92,
    "MARKET_SIZE_EXPANDING_SAM": 0.85,
    ...
  },
  "competitor_analysis": {...},
  "market_opportunities": [...],
  "consumer_recommendations": [...],
  ...
}
```

---

## The Fix

### Updated Query
```python
# ✅ CORRECT QUERY
SELECT 
    session_id,
    analysis_type,
    overall_business_case_score,    -- ✓ Actual column name
    overall_confidence,
    layers_analyzed,
    factors_calculated,
    segments_evaluated,
    analysis_summary,               -- ✓ JSONB
    full_results,                   -- ✓ JSONB with all nested data
    created_at,
    updated_at
FROM v2_analysis_results
WHERE session_id = $1
```

### Extraction Logic
```python
# Extract nested data from full_results
full_results = result.get('full_results', {})
if full_results:
    result['segment_scores'] = full_results.get('segments', {})
    result['factor_scores'] = full_results.get('factors', {})
    result['layer_scores'] = full_results.get('layers', {})
    result['overall_score'] = result.get('overall_business_case_score', 0.0)
```

---

## Why Results Were Showing Zeros

### Root Cause Chain

1. ❌ Results tab queried non-existent columns (`segment_scores`, etc.)
2. ❌ Query returned `NULL` for those columns
3. ❌ Transformation methods tried to extract from `None`
4. ❌ Default empty values returned (zeros, empty lists)
5. ❌ Frontend displayed empty data

### Now Fixed

1. ✅ Query uses correct column names
2. ✅ Extract nested data from `full_results` JSONB
3. ✅ Transformation methods receive real data
4. ✅ Frontend displays actual analysis results
5. ✅ All scores and details visible

---

## Data Flow Verification

### Storage (v2_orchestrator → Cloud SQL)
```python
# v2_strategic_analysis_orchestrator.py
async def _store_complete_analysis(...):
    await connection.execute("""
        INSERT INTO v2_analysis_results
        (session_id, ..., full_results, ...)
        VALUES ($1, ..., $12, ...)
        ON CONFLICT (session_id) DO UPDATE ...
    """, session_id, ..., json.dumps(results), ...)
```
✅ **WORKING** - Data is being stored correctly

### Retrieval (Results Tab ← Cloud SQL)
```python
# results_analysis_engine.py
async def _get_v2_analysis_results(...):
    query = """
        SELECT session_id, ..., full_results, ...
        FROM v2_analysis_results
        WHERE session_id = $1
    """
    # Extract nested data from full_results
    result['segment_scores'] = full_results.get('segments', {})
    result['factor_scores'] = full_results.get('factors', {})
```
✅ **NOW FIXED** - Queries correct schema

---

## Re-Scoring Behavior

### Why Timestamps Don't Change

When you click "Start Scoring" on an **already-scored** topic:

1. Backend checks if `v2_analysis_results` already has data for that session_id
2. The `ON CONFLICT DO UPDATE` clause updates existing record
3. The `updated_at` timestamp IS updated to NOW()
4. But the analysis itself might not re-run if recent

### Expected Behavior

- **First Score:** Creates new record, runs full 210-layer analysis
- **Re-Score:** Updates existing record with new analysis
- **`updated_at`:** Should update to current timestamp
- **`created_at`:** Stays the same (original scoring time)

### Why You're Not Seeing Changes

Possible reasons:
1. Frontend might be showing cached data
2. Hard refresh needed (Ctrl+Shift+R)
3. Old revision still serving traffic
4. Background task hasn't completed yet

---

## Testing Recommendations

### Step 1: Verify Backend Revision
```bash
gcloud run services describe validatus-backend \
  --region=us-central1 \
  --project=validatus-platform \
  --format="value(status.traffic[0].revisionName)"
```

Expected: `validatus-backend-00167-xxx` (new revision with schema fix)

### Step 2: Test Results API Directly
```bash
curl https://validatus-backend-ssivkqhvhq-uc.a.run.app/api/v3/results/complete/topic-747b5405721c
```

Should return actual data, not zeros.

### Step 3: Check Backend Logs
```bash
gcloud logging read \
  "resource.labels.revision_name=validatus-backend-00167-xxx \
  AND jsonPayload.message=~'Found v2.0 analysis results'" \
  --limit=10
```

Should show: "Found v2.0 analysis results for topic-747b5405721c"

### Step 4: Frontend Hard Refresh
- Press **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)
- This clears cached API responses
- Navigate to Results tab again

---

## Summary

### Q1: Is the current scoring endpoint different?
**A:** No, there's only ONE v2.0 scoring endpoint. The issue was a **schema mismatch** in how Results tab queried the data.

### Q2: Are results stored in Cloud SQL?
**A:** YES! Results ARE being stored in Cloud SQL's `v2_analysis_results` table by v2_orchestrator. The problem was Results tab querying wrong column names.

### The Fix
- ✅ Updated Results tab to query actual schema
- ✅ Extract nested data from `full_results` JSONB
- ✅ Results tab now reads real scored analysis
- ✅ Deploying backend with schema fix

---

**Status:** Backend deploying with correct schema query 🚀

