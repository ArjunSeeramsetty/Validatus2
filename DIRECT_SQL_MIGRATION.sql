-- Direct SQL Migration for Results Persistence Tables
-- Run this directly on Cloud SQL if API endpoints are not working

-- ============================================
-- RESULTS PERSISTENCE TABLES
-- ============================================

-- 1. Computed Factors Table
CREATE TABLE IF NOT EXISTS computed_factors (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    factor_id VARCHAR(10) NOT NULL,
    factor_value DECIMAL(10,6) NOT NULL,
    confidence DECIMAL(10,6) NOT NULL,
    formula_applied TEXT,
    calculation_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_session_factor UNIQUE(session_id, factor_id)
);

CREATE INDEX IF NOT EXISTS idx_factors_session ON computed_factors(session_id);
CREATE INDEX IF NOT EXISTS idx_factors_segment ON computed_factors(session_id, segment);

-- 2. Pattern Matches Table
CREATE TABLE IF NOT EXISTS pattern_matches (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    pattern_id VARCHAR(10) NOT NULL,
    pattern_name VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    confidence DECIMAL(10,6) NOT NULL,
    match_score DECIMAL(10,6) NOT NULL,
    strategic_response TEXT,
    effect_size_hints TEXT,
    probability_range JSONB,
    factors_triggered JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patterns_session ON pattern_matches(session_id);
CREATE INDEX IF NOT EXISTS idx_patterns_segment ON pattern_matches(session_id, segment);

-- 3. Monte Carlo Scenarios Table
CREATE TABLE IF NOT EXISTS monte_carlo_scenarios (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    scenario_id VARCHAR(100) NOT NULL,
    pattern_id VARCHAR(10) NOT NULL,
    pattern_name VARCHAR(255) NOT NULL,
    strategic_response TEXT,
    kpi_results JSONB NOT NULL,
    probability_success DECIMAL(10,6) NOT NULL,
    confidence_interval JSONB NOT NULL,
    iterations INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_session_scenario UNIQUE(session_id, scenario_id)
);

CREATE INDEX IF NOT EXISTS idx_scenarios_session ON monte_carlo_scenarios(session_id);
CREATE INDEX IF NOT EXISTS idx_scenarios_segment ON monte_carlo_scenarios(session_id, segment);

-- 4. Consumer Personas Table
CREATE TABLE IF NOT EXISTS consumer_personas (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    persona_name VARCHAR(255) NOT NULL,
    age VARCHAR(50),
    demographics JSONB,
    psychographics JSONB,
    pain_points JSONB,
    goals JSONB,
    buying_behavior JSONB,
    market_share DECIMAL(10,6),
    value_tier VARCHAR(50),
    key_messaging JSONB,
    confidence DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_personas_session ON consumer_personas(session_id);

-- 5. Segment Rich Content Table
CREATE TABLE IF NOT EXISTS segment_rich_content (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    content_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_session_segment_content UNIQUE(session_id, segment, content_type)
);

CREATE INDEX IF NOT EXISTS idx_rich_content_session ON segment_rich_content(session_id);

-- 6. Results Generation Status Table
CREATE TABLE IF NOT EXISTS results_generation_status (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    topic VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_stage VARCHAR(100),
    progress_percentage INTEGER DEFAULT 0,
    total_segments INTEGER DEFAULT 5,
    completed_segments INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_results_status ON results_generation_status(session_id, status);

-- ============================================
-- VERIFICATION QUERY
-- ============================================
-- Run this to verify all tables were created:

SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_name IN (
    'computed_factors',
    'pattern_matches',
    'monte_carlo_scenarios',
    'consumer_personas',
    'segment_rich_content',
    'results_generation_status'
)
ORDER BY table_name;
