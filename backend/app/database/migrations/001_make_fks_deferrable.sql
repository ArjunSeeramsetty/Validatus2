-- Migration: Make foreign keys DEFERRABLE INITIALLY DEFERRED
-- This allows parent and child inserts in any order within a transaction
-- FK checks are deferred until COMMIT time

BEGIN;

-- 1. factors.segment_id → segments.id
ALTER TABLE factors DROP CONSTRAINT IF EXISTS factors_segment_id_fkey;
ALTER TABLE factors
  ADD CONSTRAINT factors_segment_id_fkey
  FOREIGN KEY (segment_id)
  REFERENCES segments(id)
  DEFERRABLE INITIALLY DEFERRED;

-- 2. layers.factor_id → factors.id
ALTER TABLE layers DROP CONSTRAINT IF EXISTS layers_factor_id_fkey;
ALTER TABLE layers
  ADD CONSTRAINT layers_factor_id_fkey
  FOREIGN KEY (factor_id)
  REFERENCES factors(id)
  DEFERRABLE INITIALLY DEFERRED;

-- 3. layer_scores.layer_id → layers.id
ALTER TABLE layer_scores DROP CONSTRAINT IF EXISTS layer_scores_layer_id_fkey;
ALTER TABLE layer_scores
  ADD CONSTRAINT layer_scores_layer_id_fkey
  FOREIGN KEY (layer_id)
  REFERENCES layers(id)
  DEFERRABLE INITIALLY DEFERRED;

-- 4. factor_calculations.factor_id → factors.id (if exists)
ALTER TABLE factor_calculations DROP CONSTRAINT IF EXISTS factor_calculations_factor_id_fkey;
ALTER TABLE factor_calculations
  ADD CONSTRAINT factor_calculations_factor_id_fkey
  FOREIGN KEY (factor_id)
  REFERENCES factors(id)
  DEFERRABLE INITIALLY DEFERRED;

-- 5. segment_analysis.segment_id → segments.id (if exists)
ALTER TABLE segment_analysis DROP CONSTRAINT IF EXISTS segment_analysis_segment_id_fkey;
ALTER TABLE segment_analysis
  ADD CONSTRAINT segment_analysis_segment_id_fkey
  FOREIGN KEY (segment_id)
  REFERENCES segments(id)
  DEFERRABLE INITIALLY DEFERRED;

COMMIT;

-- Verify constraints are now deferrable
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    rc.update_rule,
    rc.delete_rule,
    con.condeferrable,
    con.condeferred
FROM information_schema.table_constraints tc
JOIN information_schema.referential_constraints rc 
    ON tc.constraint_name = rc.constraint_name
JOIN pg_constraint con 
    ON con.conname = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name IN ('factors', 'layers', 'layer_scores', 'factor_calculations', 'segment_analysis')
ORDER BY tc.table_name, tc.constraint_name;

