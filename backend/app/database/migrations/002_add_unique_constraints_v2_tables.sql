-- Migration: Add UNIQUE constraints for ON CONFLICT support
-- Required for upsert operations in v2.0 scoring system
-- Date: 2025-10-11

-- ===== LAYER_SCORES TABLE =====
-- Add UNIQUE constraint on (session_id, layer_id) for idempotent inserts
ALTER TABLE layer_scores 
    ADD CONSTRAINT layer_scores_session_layer_unique 
    UNIQUE (session_id, layer_id);

-- ===== FACTOR_CALCULATIONS TABLE =====
-- Add UNIQUE constraint on (session_id, factor_id) for idempotent inserts
ALTER TABLE factor_calculations 
    ADD CONSTRAINT factor_calculations_session_factor_unique 
    UNIQUE (session_id, factor_id);

-- ===== SEGMENT_ANALYSIS TABLE =====
-- Add UNIQUE constraint on (session_id, segment_id) for idempotent inserts
ALTER TABLE segment_analysis 
    ADD CONSTRAINT segment_analysis_session_segment_unique 
    UNIQUE (session_id, segment_id);

-- Add helpful comments
COMMENT ON CONSTRAINT layer_scores_session_layer_unique ON layer_scores IS 
    'Ensures one layer score per session-layer combination, enables ON CONFLICT upserts';
    
COMMENT ON CONSTRAINT factor_calculations_session_factor_unique ON factor_calculations IS 
    'Ensures one factor calculation per session-factor combination, enables ON CONFLICT upserts';
    
COMMENT ON CONSTRAINT segment_analysis_session_segment_unique ON segment_analysis IS 
    'Ensures one segment analysis per session-segment combination, enables ON CONFLICT upserts';

