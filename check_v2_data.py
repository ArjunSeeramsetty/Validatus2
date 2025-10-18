#!/usr/bin/env python3
"""
Check v2_analysis_results data for our test session
"""

import asyncio
import json
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database_config import DatabaseManager

async def check_v2_data():
    """Check what's in the v2_analysis_results table"""
    
    try:
        db_manager = DatabaseManager()
        connection = await db_manager.get_connection()
        
        # Check if v2_analysis_results exists and has data
        query = """
        SELECT session_id, overall_business_case_score, factors_calculated, 
               full_results
        FROM v2_analysis_results 
        WHERE session_id = 'topic-747b5405721c'
        ORDER BY updated_at DESC
        LIMIT 1
        """
        
        row = await connection.fetchrow(query)
        
        if row:
            session_id = row['session_id']
            overall_score = row['overall_business_case_score']
            factors_calculated = row['factors_calculated']
            print(f"Session ID: {session_id}")
            print(f"Overall Score: {overall_score}")
            print(f"Factors Calculated: {factors_calculated}")
            
            full_results = row['full_results']
            if isinstance(full_results, str):
                full_results = json.loads(full_results)
            
            factor_calculations = full_results.get('factor_calculations', [])
            print(f"Factor Calculations Count: {len(factor_calculations)}")
            
            if factor_calculations:
                print("Sample Factor Calculations:")
                for i, factor in enumerate(factor_calculations[:5]):
                    factor_id = factor.get('factor_id', 'unknown')
                    calculated_value = factor.get('calculated_value', 0.0)
                    confidence_score = factor.get('confidence_score', 0.0)
                    print(f"  {i+1}. Factor {factor_id}: value={calculated_value}, confidence={confidence_score}")
            else:
                print("No factor_calculations found in full_results")
                
            # Check what keys are in full_results
            print(f"Keys in full_results: {list(full_results.keys())}")
            
            # Check layer_scores and segment_analyses
            layer_scores = full_results.get('layer_scores', [])
            segment_analyses = full_results.get('segment_analyses', [])
            print(f"Layer Scores Count: {len(layer_scores)}")
            print(f"Segment Analyses Count: {len(segment_analyses)}")
            
        else:
            print("No v2_analysis_results found for topic-747b5405721c")
            
            # Check if the table exists and has any data
            check_table_query = """
            SELECT COUNT(*) as count
            FROM v2_analysis_results
            """
            count_row = await connection.fetchrow(check_table_query)
            print(f"Total records in v2_analysis_results: {count_row['count']}")
            
            # Check recent sessions
            recent_query = """
            SELECT session_id, overall_business_case_score, factors_calculated, created_at
            FROM v2_analysis_results
            ORDER BY created_at DESC
            LIMIT 5
            """
            recent_rows = await connection.fetchall(recent_query)
            print("Recent sessions:")
            for recent_row in recent_rows:
                print(f"  {recent_row['session_id']}: score={recent_row['overall_business_case_score']}, factors={recent_row['factors_calculated']}")
        
        await connection.close()
        
    except Exception as e:
        print(f"Error checking v2_analysis_results: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_v2_data())
