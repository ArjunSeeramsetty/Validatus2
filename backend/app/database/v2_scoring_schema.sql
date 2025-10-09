-- Validatus v2.0 Strategic Scoring Schema
-- 5 Segments → 28 Factors → 210 Layers Structure

-- ===== SEGMENTS TABLE (5 segments) =====
CREATE TABLE IF NOT EXISTS segments (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    friendly_name VARCHAR(100) NOT NULL,
    description TEXT,
    weight DECIMAL(5,4) DEFAULT 0.2000,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT chk_segment_weight CHECK (weight >= 0 AND weight <= 1)
);

-- ===== FACTORS TABLE (28 factors) =====
CREATE TABLE IF NOT EXISTS factors (
    id VARCHAR(10) PRIMARY KEY,
    segment_id VARCHAR(10) NOT NULL,
    name VARCHAR(150) NOT NULL,
    friendly_name VARCHAR(150) NOT NULL,
    description TEXT,
    calculation_formula TEXT,
    weight_in_segment DECIMAL(5,4),
    expert_persona VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (segment_id) REFERENCES segments(id) ON DELETE CASCADE,
    CONSTRAINT chk_factor_weight CHECK (weight_in_segment >= 0 AND weight_in_segment <= 1)
);

-- ===== LAYERS TABLE (210 layers) =====
CREATE TABLE IF NOT EXISTS layers (
    id VARCHAR(15) PRIMARY KEY,
    factor_id VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    friendly_name VARCHAR(200) NOT NULL,
    description TEXT,
    expert_persona VARCHAR(100),
    scoring_prompt_template TEXT,
    weight_in_factor DECIMAL(5,4),
    analysis_criteria TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (factor_id) REFERENCES factors(id) ON DELETE CASCADE,
    CONSTRAINT chk_layer_weight CHECK (weight_in_factor >= 0 AND weight_in_factor <= 1)
);

-- ===== LAYER SCORES TABLE =====
CREATE TABLE IF NOT EXISTS layer_scores (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    layer_id VARCHAR(15) NOT NULL,
    score DECIMAL(5,4) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    evidence_count INTEGER DEFAULT 0,
    key_insights TEXT[],
    evidence_summary TEXT,
    llm_analysis_raw TEXT,
    expert_persona VARCHAR(100),
    processing_time_ms INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (layer_id) REFERENCES layers(id) ON DELETE CASCADE,
    CONSTRAINT chk_layer_score CHECK (score >= 0 AND score <= 1),
    CONSTRAINT chk_layer_confidence CHECK (confidence >= 0 AND confidence <= 1)
);

CREATE INDEX IF NOT EXISTS idx_layer_scores_session ON layer_scores(session_id);
CREATE INDEX IF NOT EXISTS idx_layer_scores_layer ON layer_scores(layer_id);
CREATE INDEX IF NOT EXISTS idx_layer_scores_created ON layer_scores(created_at DESC);

-- ===== FACTOR CALCULATIONS TABLE =====
CREATE TABLE IF NOT EXISTS factor_calculations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    factor_id VARCHAR(10) NOT NULL,
    calculated_value DECIMAL(5,4) NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    input_layer_count INTEGER,
    calculation_method VARCHAR(50) DEFAULT 'weighted_average',
    calculation_formula TEXT,
    layer_contributions JSONB,
    validation_metrics JSONB,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (factor_id) REFERENCES factors(id) ON DELETE CASCADE,
    CONSTRAINT chk_factor_value CHECK (calculated_value >= 0 AND calculated_value <= 1),
    CONSTRAINT chk_factor_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

CREATE INDEX IF NOT EXISTS idx_factor_calc_session ON factor_calculations(session_id);
CREATE INDEX IF NOT EXISTS idx_factor_calc_factor ON factor_calculations(factor_id);

-- ===== SEGMENT ANALYSIS TABLE =====
CREATE TABLE IF NOT EXISTS segment_analysis (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    segment_id VARCHAR(10) NOT NULL,
    attractiveness_score DECIMAL(5,4),
    competitive_intensity DECIMAL(5,4),
    market_size_score DECIMAL(5,4),
    growth_potential DECIMAL(5,4),
    overall_segment_score DECIMAL(5,4),
    key_insights TEXT[],
    risk_factors TEXT[],
    opportunities TEXT[],
    recommendations TEXT[],
    factor_contributions JSONB,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (segment_id) REFERENCES segments(id) ON DELETE CASCADE,
    CONSTRAINT chk_segment_scores CHECK (
        attractiveness_score >= 0 AND attractiveness_score <= 1 AND
        competitive_intensity >= 0 AND competitive_intensity <= 1 AND
        market_size_score >= 0 AND market_size_score <= 1 AND
        growth_potential >= 0 AND growth_potential <= 1 AND
        overall_segment_score >= 0 AND overall_segment_score <= 1
    )
);

CREATE INDEX IF NOT EXISTS idx_segment_analysis_session ON segment_analysis(session_id);
CREATE INDEX IF NOT EXISTS idx_segment_analysis_segment ON segment_analysis(segment_id);

-- ===== COMPREHENSIVE ANALYSIS RESULTS TABLE =====
CREATE TABLE IF NOT EXISTS v2_analysis_results (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    analysis_type VARCHAR(50) DEFAULT 'validatus_v2_complete',
    overall_business_case_score DECIMAL(5,4),
    overall_confidence DECIMAL(5,4),
    layers_analyzed INTEGER,
    factors_calculated INTEGER,
    segments_evaluated INTEGER,
    scenarios_generated INTEGER,
    processing_time_seconds DECIMAL(10,2),
    content_items_analyzed INTEGER,
    analysis_summary JSONB,
    full_results JSONB,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT chk_overall_score CHECK (overall_business_case_score >= 0 AND overall_business_case_score <= 1)
);

CREATE INDEX IF NOT EXISTS idx_v2_analysis_session ON v2_analysis_results(session_id);
CREATE INDEX IF NOT EXISTS idx_v2_analysis_created ON v2_analysis_results(created_at DESC);

-- ===== AUTO-UPDATE TIMESTAMP TRIGGER =====
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_segments_updated_at BEFORE UPDATE ON segments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_factors_updated_at BEFORE UPDATE ON factors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_layers_updated_at BEFORE UPDATE ON layers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_v2_analysis_updated_at BEFORE UPDATE ON v2_analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

