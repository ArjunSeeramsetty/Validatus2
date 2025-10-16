#!/usr/bin/env python3
"""
Test Enhanced Segment Results API
Tests all 5 segments with Monte Carlo scenarios and rich content
"""
import requests
import json

BACKEND_URL = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"

print("\n" + "="*70)
print("TESTING ENHANCED SEGMENT RESULTS API")
print("="*70 + "\n")

# First, get existing topics
print("1. Fetching existing topics...")
try:
    response = requests.get(f"{BACKEND_URL}/api/v3/topics/", timeout=10)
    topics = response.json()
    print(f"   Found {len(topics)} topics")
    
    if topics:
        # Use the first topic for testing
        test_topic = topics[0]
        topic_id = test_topic.get('session_id')
        topic_name = test_topic.get('topic_name', 'Unknown')
        print(f"   Using topic: {topic_name} ({topic_id})")
    else:
        print("   [WARNING] No topics found. Please create a topic first.")
        exit(0)
except Exception as e:
    print(f"   [FAILED]: {e}")
    exit(1)

print()

# Test all 5 segments
segments = ['market', 'consumer', 'product', 'brand', 'experience']
expected_scenarios = {
    'market': 4,
    'consumer': 4,
    'brand': 4,
    'product': 3,
    'experience': 2
}

results_summary = []

for segment in segments:
    print(f"2. Testing {segment.upper()} segment...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v3/enhanced-segment-results/{topic_id}/{segment}",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            monte_carlo = data.get('monte_carlo_scenarios', [])
            patterns = data.get('matched_patterns', [])
            rich_content = data.get('rich_content', {})
            personas = data.get('personas', [])
            
            scenario_count = len(monte_carlo)
            expected_count = expected_scenarios[segment]
            
            status = "[PASSED]" if scenario_count == expected_count else f"[WARNING: Expected {expected_count}, got {scenario_count}]"
            
            print(f"   Status: {response.status_code} {status}")
            print(f"   Monte Carlo Scenarios: {scenario_count}")
            print(f"   Matched Patterns: {len(patterns)}")
            print(f"   Rich Content Keys: {list(rich_content.keys()) if rich_content else 'None'}")
            
            if segment == 'consumer':
                print(f"   Personas Generated: {len(personas)}")
            
            # Check Monte Carlo details
            if monte_carlo:
                sample_scenario = monte_carlo[0]
                kpi_count = len(sample_scenario.get('kpi_results', {}))
                print(f"   Sample Scenario KPIs: {kpi_count}")
                print(f"   Success Probability: {sample_scenario.get('probability_success', 0)*100:.1f}%")
            
            results_summary.append({
                'segment': segment,
                'status': 'PASSED' if scenario_count == expected_count else 'WARNING',
                'scenarios': scenario_count,
                'expected': expected_count,
                'patterns': len(patterns),
                'rich_content': bool(rich_content),
                'personas': len(personas) if segment == 'consumer' else 0
            })
            
        elif response.status_code == 404:
            print(f"   Status: 404 [INFO] Endpoint exists but topic/segment not found")
            results_summary.append({
                'segment': segment,
                'status': 'ENDPOINT_EXISTS',
                'scenarios': 0,
                'expected': expected_scenarios[segment]
            })
        else:
            print(f"   Status: {response.status_code} [FAILED]")
            print(f"   Error: {response.text[:200]}")
            results_summary.append({
                'segment': segment,
                'status': 'FAILED',
                'scenarios': 0,
                'expected': expected_scenarios[segment]
            })
    
    except Exception as e:
        print(f"   [FAILED]: {e}")
        results_summary.append({
            'segment': segment,
            'status': 'ERROR',
            'error': str(e),
            'expected': expected_scenarios[segment]
        })
    
    print()

# Summary
print("="*70)
print("TEST SUMMARY")
print("="*70)

passed = sum(1 for r in results_summary if r.get('status') == 'PASSED')
total = len(results_summary)

print(f"\nTests Passed: {passed}/{total}\n")

for result in results_summary:
    segment = result['segment'].upper()
    status = result.get('status', 'UNKNOWN')
    
    if status == 'PASSED':
        print(f"[PASSED] {segment}: {result['scenarios']}/{result['expected']} scenarios, {result['patterns']} patterns")
        if result.get('rich_content'):
            print(f"         Rich content generated: YES")
        if result.get('personas', 0) > 0:
            print(f"         Personas: {result['personas']}")
    elif status == 'WARNING':
        print(f"[WARNING] {segment}: {result['scenarios']}/{result['expected']} scenarios (count mismatch)")
    elif status == 'ENDPOINT_EXISTS':
        print(f"[INFO] {segment}: Endpoint exists (404 for test data)")
    else:
        print(f"[FAILED] {segment}: {result.get('error', 'Unknown error')}")

print("\n" + "="*70)

if passed == total:
    print("[SUCCESS] All segment endpoints working correctly!")
else:
    print(f"[PARTIAL] {passed}/{total} segments passed")

print("="*70)

