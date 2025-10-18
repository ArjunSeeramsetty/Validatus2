#!/usr/bin/env python3
"""
Test v2 analysis endpoint to create real factor data
"""

import requests
import time

def test_v2_analysis():
    """Test the v2 analysis endpoint"""
    
    try:
        print("Triggering v2 analysis...")
        response = requests.post(
            'https://validatus-backend-ssivkqhvhq-uc.a.run.app/api/v3/v2-scoring/topic-747b5405721c/analyze', 
            timeout=180
        )
        print(f"V2 Analysis Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("V2 Analysis completed successfully!")
            print(f"Success: {data.get('success', False)}")
            print(f"Message: {data.get('message', 'No message')}")
            
            if 'results_summary' in data:
                summary = data['results_summary']
                print(f"Overall Score: {summary.get('overall_score', 'N/A')}")
                print(f"Layers Analyzed: {summary.get('layers_analyzed', 'N/A')}")
                print(f"Factors Calculated: {summary.get('factors_calculated', 'N/A')}")
                print(f"Segments Evaluated: {summary.get('segments_evaluated', 'N/A')}")
        else:
            print(f"V2 Analysis failed: {response.text}")
            
    except Exception as e:
        print(f"Error triggering v2 analysis: {e}")

if __name__ == "__main__":
    test_v2_analysis()
