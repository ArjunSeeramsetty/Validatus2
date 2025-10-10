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


def generate_all_layers():
    """
    Generate all 210 layers across 28 factors
    Distribution: Variable layers per factor (3-10 each) totaling 210
    """
    layers = []
    
    # Define layer count per factor for 210 total
    # S1 (F1-F10): 30 layers = 3 per factor
    # S2 (F11-F15): 50 layers = 10 per factor
    # S3 (F16-F20): 50 layers = 10 per factor  
    # S4 (F21-F25): 50 layers = 10 per factor
    # S5 (F26-F28): 30 layers = 10 per factor
    
    layers_per_factor = {
        'F1': 3, 'F2': 3, 'F3': 3, 'F4': 3, 'F5': 3,
        'F6': 3, 'F7': 3, 'F8': 3, 'F9': 3, 'F10': 3,
        'F11': 10, 'F12': 10, 'F13': 10, 'F14': 10, 'F15': 10,
        'F16': 10, 'F17': 10, 'F18': 10, 'F19': 10, 'F20': 10,
        'F21': 10, 'F22': 10, 'F23': 10, 'F24': 10, 'F25': 10,
        'F26': 10, 'F27': 10, 'F28': 10
    }
    
    layer_templates = {
        # Product Intelligence (F1-F10) - 3 layers each
        'F1': ['Market Entry Barriers', 'Regulatory Approval Timeline', 'Technological Maturity'],
        'F2': ['Incumbent Market Share', 'Switching Costs', 'Competitive Response Speed'],
        'F3': ['Behavioral Change Required', 'Habit Formation Potential', 'Network Effects Potential'],
        'F4': ['Revenue Model Diversity', 'Cost Structure Efficiency', 'Scalability of Operations'],
        'F5': ['Innovation Adoption Rate', 'Market Timing Opportunity', 'Early Adopter Identification'],
        'F6': ['Problem Solution Fit', 'Target Market Size Fit', 'Product Differentiation'],
        'F7': ['Technology Maturity Curve', 'Innovation Cycle Speed', 'Disruptive Potential'],
        'F8': ['Infrastructure Scalability', 'Operational Efficiency', 'Supply Chain Robustness'],
        'F9': ['Patent Portfolio Strength', 'Freedom to Operate', 'Trade Secret Protection'],
        'F10': ['Partnership Opportunities', 'Ecosystem Integration', 'Channel Leverage'],
        
        # Consumer Intelligence (F11-F15) - 10 layers each
        'F11': ['Problem Severity', 'Unmet Needs', 'Purchase Intent', 'Willingness to Pay', 
                'Consumer Awareness', 'Need Urgency', 'Alternative Solutions', 'Pain Point Depth',
                'Demand Elasticity', 'Market Pull Strength'],
        'F12': ['Current Habits', 'Usage Frequency', 'Behavior Triggers', 'Decision Drivers',
                'Purchase Patterns', 'Loyalty Indicators', 'Switching Behavior', 'Adoption Barriers',
                'Habit Strength', 'Routine Integration'],
        'F13': ['Awareness Stage', 'Consideration Stage', 'Decision Stage', 'Purchase Touchpoints',
                'Post-Purchase Experience', 'Retention Touchpoints', 'Advocacy Drivers', 'Channel Preference',
                'Journey Complexity', 'Friction Points'],
        'F14': ['Brand Sentiment', 'Product Perception', 'Competitor Sentiment', 'Category Perception',
                'Trust Indicators', 'Satisfaction Levels', 'NPS Scores', 'Review Sentiment',
                'Social Buzz', 'Perception Trends'],
        'F15': ['Value Clarity', 'Benefit Recognition', 'Price Sensitivity', 'Feature Importance',
                'Competitive Advantage', 'Unique Benefits', 'Value Communication', 'ROI Perception',
                'Emotional Connection', 'Rational Benefits'],
        
        # Market Intelligence (F16-F20) - 10 layers each
        'F16': ['Total Addressable Market', 'Serviceable Market', 'Obtainable Market', 'Market Growth Rate',
                'Market Maturity', 'Geographic Reach', 'Demographic Size', 'Market Concentration',
                'Revenue Potential', 'Market Trends'],
        'F17': ['Direct Competition', 'Indirect Competition', 'Substitute Products', 'Market Leaders',
                'Competitive Intensity', 'Entry Barriers', 'Exit Barriers', 'Rivalry Dynamics',
                'Competitive Advantages', 'Market Position'],
        'F18': ['Compliance Requirements', 'Regulatory Risks', 'Policy Changes', 'Legal Framework',
                'Industry Standards', 'Certification Needs', 'Licensing Requirements', 'Trade Regulations',
                'Data Privacy Rules', 'Environmental Laws'],
        'F19': ['GDP Indicators', 'Economic Growth', 'Inflation Impact', 'Employment Trends',
                'Consumer Spending', 'Cultural Shifts', 'Demographic Changes', 'Technology Adoption',
                'Urbanization Trends', 'Social Values'],
        'F20': ['Regional Markets', 'Urban vs Rural', 'Age Demographics', 'Income Segments',
                'Education Levels', 'Cultural Groups', 'Lifestyle Segments', 'Behavioral Segments',
                'Psychographic Profiles', 'Channel Preferences'],
        
        # Brand Intelligence (F21-F25) - 10 layers each
        'F21': ['Brand Recall', 'Brand Recognition', 'Top-of-Mind Awareness', 'Aided Awareness',
                'Unaided Awareness', 'Category Association', 'Share of Voice', 'Media Reach',
                'Search Volume', 'Social Mentions'],
        'F22': ['Brand Image', 'Quality Perception', 'Trust Level', 'Credibility', 'Brand Personality',
                'Brand Associations', 'Emotional Resonance', 'Brand Consistency', 'Perceived Value',
                'Brand Equity'],
        'F23': ['Unique Selling Proposition', 'Competitive Positioning', 'Brand Voice', 'Visual Identity',
                'Brand Story', 'Category Differentiation', 'Feature Uniqueness', 'Experience Differentiation',
                'Value Differentiation', 'Positioning Clarity'],
        'F24': ['Repeat Purchase Rate', 'Customer Retention', 'Churn Rate', 'Advocacy Rate',
                'Referral Behavior', 'Community Engagement', 'Emotional Attachment', 'Purchase Frequency',
                'Lifetime Value', 'Loyalty Program Effectiveness'],
        'F25': ['Narrative Cohesion', 'Emotional Appeal', 'Cultural Relevance', 'Message Clarity',
                'Story Authenticity', 'Audience Connection', 'Content Consistency', 'Multi-Channel Messaging',
                'Campaign Effectiveness', 'Brand Purpose'],
        
        # Experience Intelligence (F26-F28) - 10 layers each
        'F26': ['Ease of Use', 'Learnability', 'Efficiency', 'Error Prevention', 'User Satisfaction',
                'Accessibility', 'Information Architecture', 'Visual Design', 'Interaction Design',
                'Mobile Experience'],
        'F27': ['Customer Support Quality', 'Response Time', 'Problem Resolution', 'Support Channels',
                'Self-Service Options', 'Proactive Support', 'Customer Success', 'Onboarding Experience',
                'Training Resources', 'Feedback Integration'],
        'F28': ['Daily Active Users', 'Session Duration', 'Feature Adoption', 'Engagement Rate',
                'Retention Cohorts', 'Churn Prediction', 'Stickiness', 'Viral Coefficient',
                'Time to Value', 'Activation Rate']
    }
    
    for factor_id, layer_count in layers_per_factor.items():
        factor_num = int(factor_id[1:])
        layer_names = layer_templates.get(factor_id, [f'Layer {i+1}' for i in range(layer_count)])
        
        for i in range(layer_count):
            layer_name = layer_names[i] if i < len(layer_names) else f'Layer {i+1}'
            layers.append({
                'id': f'L{factor_num}_{i+1}',
                'factor_id': factor_id,
                'name': layer_name.replace(' ', '_').replace('&', 'and'),
                'friendly_name': layer_name,
                'weight': 1.0 / layer_count  # Equal weight within factor
            })
    
    return layers


LAYERS = generate_all_layers()


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
                
                logger.info(f"Bootstrapping 210 layers...")
                layer_count = 0
                for layer in LAYERS:
                    result = await connection.fetchrow("""
                        INSERT INTO layers (id, factor_id, name, friendly_name, weight_in_factor)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (id) DO UPDATE SET
                            factor_id = EXCLUDED.factor_id,
                            name = EXCLUDED.name,
                            friendly_name = EXCLUDED.friendly_name,
                            weight_in_factor = EXCLUDED.weight_in_factor
                        RETURNING id
                    """, layer['id'], layer['factor_id'], layer['name'],
                        layer['friendly_name'], layer['weight'])
                    
                    if result:
                        layer_count += 1
                        if layer_count % 50 == 0:
                            logger.info(f"  ... {layer_count} layers initialized")
                
                logger.info(f"✅ {layer_count}/210 layers initialized")
            
            # Verify counts
            seg_count = await connection.fetchval("SELECT COUNT(*) FROM segments")
            fac_count = await connection.fetchval("SELECT COUNT(*) FROM factors")
            lay_count = await connection.fetchval("SELECT COUNT(*) FROM layers")
            
            logger.info(f"\n🎉 Bootstrap complete!")
            logger.info(f"   Segments: {seg_count}/5")
            logger.info(f"   Factors: {fac_count}/28")
            logger.info(f"   Layers: {lay_count}/210")
            
            if seg_count != 5 or fac_count != 28 or lay_count != 210:
                logger.error(f"⚠️  Expected 5/28/210, got {seg_count}/{fac_count}/{lay_count}")
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

