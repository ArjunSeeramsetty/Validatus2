#!/usr/bin/env python3
"""
Bootstrap Script: Initialize v2.0 Hierarchy (5 Segments + 28 Factors)
Uses advisory locks to prevent concurrent initialization race conditions
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database_config import db_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Advisory lock keys (app_id=42 for validatus, key=1 for hierarchy bootstrap)
HIERARCHY_LOCK_APP_ID = 42
HIERARCHY_LOCK_KEY = 1

SEGMENTS = [
    {'id': 'S1', 'name': 'Product_Intelligence', 'friendly_name': 'Product Intelligence', 
     'description': 'Product development and innovation analysis', 'weight': 0.2000},
    {'id': 'S2', 'name': 'Consumer_Intelligence', 'friendly_name': 'Consumer Intelligence',
     'description': 'Consumer behavior and preferences analysis', 'weight': 0.2000},
    {'id': 'S3', 'name': 'Market_Intelligence', 'friendly_name': 'Market Intelligence',
     'description': 'Market dynamics and competitive landscape', 'weight': 0.2000},
    {'id': 'S4', 'name': 'Brand_Intelligence', 'friendly_name': 'Brand Intelligence',
     'description': 'Brand positioning and equity analysis', 'weight': 0.2000},
    {'id': 'S5', 'name': 'Experience_Intelligence', 'friendly_name': 'Experience Intelligence',
     'description': 'User experience and interaction design', 'weight': 0.2000},
]

FACTORS = [
    # S1: Product Intelligence (F1-F10)
    {'id': 'F1', 'segment_id': 'S1', 'name': 'Market_Readiness_Timing', 
     'friendly_name': 'Market Readiness & Timing', 'weight': 0.1000},
    {'id': 'F2', 'segment_id': 'S1', 'name': 'Competitive_Disruption_Incumbent_Resistance',
     'friendly_name': 'Competitive Disruption & Incumbent Resistance', 'weight': 0.1000},
    {'id': 'F3', 'segment_id': 'S1', 'name': 'Dynamic_Disruption_Score_Habit_Formation',
     'friendly_name': 'Dynamic Disruption Score & Habit Formation', 'weight': 0.1000},
    {'id': 'F4', 'segment_id': 'S1', 'name': 'Business_Model_Resilience_Stability',
     'friendly_name': 'Business Model Resilience & Stability', 'weight': 0.1000},
    {'id': 'F5', 'segment_id': 'S1', 'name': 'Hype_Cycle_Engineering_Market_Timing',
     'friendly_name': 'Hype Cycle Engineering & Market Timing', 'weight': 0.1000},
    {'id': 'F6', 'segment_id': 'S1', 'name': 'Product_Market_Fit_Adoption_Potential',
     'friendly_name': 'Product-Market Fit & Adoption Potential', 'weight': 0.1000},
    {'id': 'F7', 'segment_id': 'S1', 'name': 'Innovation_Diffusion_Technology_S_Curve',
     'friendly_name': 'Innovation Diffusion & Technology S-Curve', 'weight': 0.1000},
    {'id': 'F8', 'segment_id': 'S1', 'name': 'Scalability_Infrastructure_Readiness',
     'friendly_name': 'Scalability & Infrastructure Readiness', 'weight': 0.1000},
    {'id': 'F9', 'segment_id': 'S1', 'name': 'IP_Patent_Landscape',
     'friendly_name': 'IP & Patent Landscape', 'weight': 0.1000},
    {'id': 'F10', 'segment_id': 'S1', 'name': 'Ecosystem_Partnership_Leverage',
     'friendly_name': 'Ecosystem & Partnership Leverage', 'weight': 0.1000},
    
    # S2: Consumer Intelligence (F11-F15)
    {'id': 'F11', 'segment_id': 'S2', 'name': 'Consumer_Needs_Demand_Strength',
     'friendly_name': 'Consumer Needs & Demand Strength', 'weight': 0.2000},
    {'id': 'F12', 'segment_id': 'S2', 'name': 'Behavioral_Patterns_Habits',
     'friendly_name': 'Behavioral Patterns & Habits', 'weight': 0.2000},
    {'id': 'F13', 'segment_id': 'S2', 'name': 'Customer_Journey_Touchpoints',
     'friendly_name': 'Customer Journey & Touchpoints', 'weight': 0.2000},
    {'id': 'F14', 'segment_id': 'S2', 'name': 'Sentiment_Perception_Analysis',
     'friendly_name': 'Sentiment & Perception Analysis', 'weight': 0.2000},
    {'id': 'F15', 'segment_id': 'S2', 'name': 'Value_Proposition_Resonance',
     'friendly_name': 'Value Proposition Resonance', 'weight': 0.2000},
    
    # S3: Market Intelligence (F16-F20)
    {'id': 'F16', 'segment_id': 'S3', 'name': 'Market_Size_Growth_Potential',
     'friendly_name': 'Market Size & Growth Potential', 'weight': 0.2000},
    {'id': 'F17', 'segment_id': 'S3', 'name': 'Competitive_Landscape_Intensity',
     'friendly_name': 'Competitive Landscape & Intensity', 'weight': 0.2000},
    {'id': 'F18', 'segment_id': 'S3', 'name': 'Regulatory_Policy_Environment',
     'friendly_name': 'Regulatory & Policy Environment', 'weight': 0.2000},
    {'id': 'F19', 'segment_id': 'S3', 'name': 'Economic_Socio_Cultural_Trends',
     'friendly_name': 'Economic & Socio-Cultural Trends', 'weight': 0.2000},
    {'id': 'F20', 'segment_id': 'S3', 'name': 'Geographic_Demographic_Segmentation',
     'friendly_name': 'Geographic & Demographic Segmentation', 'weight': 0.2000},
    
    # S4: Brand Intelligence (F21-F25)
    {'id': 'F21', 'segment_id': 'S4', 'name': 'Brand_Awareness_Recognition',
     'friendly_name': 'Brand Awareness & Recognition', 'weight': 0.2000},
    {'id': 'F22', 'segment_id': 'S4', 'name': 'Brand_Perception_Equity',
     'friendly_name': 'Brand Perception & Equity', 'weight': 0.2000},
    {'id': 'F23', 'segment_id': 'S4', 'name': 'Brand_Differentiation_Uniqueness',
     'friendly_name': 'Brand Differentiation & Uniqueness', 'weight': 0.2000},
    {'id': 'F24', 'segment_id': 'S4', 'name': 'Brand_Loyalty_Advocacy',
     'friendly_name': 'Brand Loyalty & Advocacy', 'weight': 0.2000},
    {'id': 'F25', 'segment_id': 'S4', 'name': 'Brand_Storytelling_Messaging',
     'friendly_name': 'Brand Storytelling & Messaging', 'weight': 0.2000},
    
    # S5: Experience Intelligence (F26-F28)
    {'id': 'F26', 'segment_id': 'S5', 'name': 'User_Experience_UX_Usability',
     'friendly_name': 'User Experience (UX) & Usability', 'weight': 0.3333},
    {'id': 'F27', 'segment_id': 'S5', 'name': 'Customer_Satisfaction_Delight',
     'friendly_name': 'Customer Satisfaction & Delight', 'weight': 0.3333},
    {'id': 'F28', 'segment_id': 'S5', 'name': 'Engagement_Retention_Metrics',
     'friendly_name': 'Engagement & Retention Metrics', 'weight': 0.3333},
]


async def bootstrap_hierarchy():
    """Bootstrap segments and factors with advisory lock protection"""
    try:
        connection = await db_manager.get_connection()
        
        # Acquire global advisory lock (app_id=42, key=1)
        logger.info(f"Acquiring advisory lock ({HIERARCHY_LOCK_APP_ID}, {HIERARCHY_LOCK_KEY})...")
        lock_acquired = await connection.fetchval(
            "SELECT pg_try_advisory_lock($1, $2)",
            HIERARCHY_LOCK_APP_ID,
            HIERARCHY_LOCK_KEY
        )
        
        if not lock_acquired:
            logger.warning("Another process is bootstrapping. Waiting for lock...")
            await connection.fetchval(
                "SELECT pg_advisory_lock($1, $2)",
                HIERARCHY_LOCK_APP_ID,
                HIERARCHY_LOCK_KEY
            )
            logger.info("Lock acquired after waiting")
        
        try:
            # Start transaction with deferred constraints
            async with connection.transaction():
                await connection.execute("SET CONSTRAINTS ALL DEFERRED")
                
                logger.info("Bootstrapping 5 segments...")
                segment_count = 0
                for segment in SEGMENTS:
                    result = await connection.fetchrow("""
                        INSERT INTO segments (id, name, friendly_name, description, weight)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            friendly_name = EXCLUDED.friendly_name,
                            description = EXCLUDED.description,
                            weight = EXCLUDED.weight,
                            updated_at = NOW()
                        RETURNING id
                    """, segment['id'], segment['name'], segment['friendly_name'],
                        segment.get('description'), segment['weight'])
                    
                    if result:
                        segment_count += 1
                        logger.info(f"  ✓ {segment['id']}: {segment['friendly_name']}")
                
                logger.info(f"✅ {segment_count}/5 segments initialized")
                
                logger.info("Bootstrapping 28 factors...")
                factor_count = 0
                for factor in FACTORS:
                    result = await connection.fetchrow("""
                        INSERT INTO factors (id, segment_id, name, friendly_name, weight_in_segment)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (id) DO UPDATE SET
                            segment_id = EXCLUDED.segment_id,
                            name = EXCLUDED.name,
                            friendly_name = EXCLUDED.friendly_name,
                            weight_in_segment = EXCLUDED.weight_in_segment
                        RETURNING id
                    """, factor['id'], factor['segment_id'], factor['name'],
                        factor['friendly_name'], factor['weight'])
                    
                    if result:
                        factor_count += 1
                        logger.info(f"  ✓ {factor['id']}: {factor['friendly_name']}")
                
                logger.info(f"✅ {factor_count}/28 factors initialized")
            
            # Verify counts
            seg_count = await connection.fetchval("SELECT COUNT(*) FROM segments")
            fac_count = await connection.fetchval("SELECT COUNT(*) FROM factors")
            
            logger.info(f"\n🎉 Bootstrap complete!")
            logger.info(f"   Segments: {seg_count}/5")
            logger.info(f"   Factors: {fac_count}/28")
            
            if seg_count != 5 or fac_count != 28:
                logger.error(f"⚠️  Expected 5 segments and 28 factors, got {seg_count} and {fac_count}")
                return False
            
            return True
            
        finally:
            # Release advisory lock
            await connection.fetchval(
                "SELECT pg_advisory_unlock($1, $2)",
                HIERARCHY_LOCK_APP_ID,
                HIERARCHY_LOCK_KEY
            )
            logger.info("Advisory lock released")
    
    except Exception as e:
        logger.error(f"Bootstrap failed: {e}", exc_info=True)
        return False


async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Validatus v2.0 Hierarchy Bootstrap")
    logger.info("=" * 60)
    
    success = await bootstrap_hierarchy()
    
    if success:
        logger.info("\n✅ Bootstrap successful!")
        sys.exit(0)
    else:
        logger.error("\n❌ Bootstrap failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

