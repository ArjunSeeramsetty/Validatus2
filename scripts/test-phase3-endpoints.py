#!/usr/bin/env python3
"""
Phase 3 API Endpoint Test Script
Tests the new Analysis Results Manager endpoints
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_phase3_endpoints():
    """Test Phase 3 Analysis Results endpoints"""
    logger.info("🚀 Testing Phase 3 Analysis Results Endpoints")
    logger.info("=" * 60)
    
    # Test data
    test_session_id = "test-session-123"
    test_user_id = "test-user-456"
    
    endpoints_to_test = [
        {
            "name": "Get Complete Analysis Results",
            "method": "GET",
            "url": f"/api/v3/results/sessions/{test_session_id}/complete",
            "expected_status": 200
        },
        {
            "name": "Get Dashboard Summary",
            "method": "GET", 
            "url": f"/api/v3/results/dashboard/{test_user_id}?limit=10",
            "expected_status": 200
        },
        {
            "name": "Export Analysis Results (JSON)",
            "method": "POST",
            "url": f"/api/v3/results/sessions/{test_session_id}/export",
            "data": {
                "format": "json",
                "user_id": test_user_id
            },
            "expected_status": 200
        },
        {
            "name": "Export Analysis Results (PDF)",
            "method": "POST",
            "url": f"/api/v3/results/sessions/{test_session_id}/export",
            "data": {
                "format": "pdf",
                "user_id": test_user_id
            },
            "expected_status": 200
        },
        {
            "name": "Export Analysis Results (Excel)",
            "method": "POST",
            "url": f"/api/v3/results/sessions/{test_session_id}/export",
            "data": {
                "format": "excel",
                "user_id": test_user_id
            },
            "expected_status": 200
        },
        {
            "name": "Get Real-time Progress",
            "method": "GET",
            "url": f"/api/v3/results/sessions/{test_session_id}/progress",
            "expected_status": 200
        },
        {
            "name": "Get Analytics Trends",
            "method": "GET",
            "url": f"/api/v3/results/analytics/trends?user_id={test_user_id}&timeframe=30d",
            "expected_status": 200
        }
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        logger.info(f"🔍 Testing: {endpoint['name']}")
        
        start_time = time.time()
        
        try:
            if endpoint["method"] == "GET":
                response = requests.get(f"{BASE_URL}{endpoint['url']}", timeout=10)
            elif endpoint["method"] == "POST":
                response = requests.post(
                    f"{BASE_URL}{endpoint['url']}", 
                    json=endpoint.get("data", {}),
                    timeout=10
                )
            
            response_time = time.time() - start_time
            
            result = {
                "name": endpoint["name"],
                "url": endpoint["url"],
                "method": endpoint["method"],
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == endpoint["expected_status"],
                "response_data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
            }
            
            results.append(result)
            
            if result["success"]:
                logger.info(f"✅ {endpoint['name']}: {response.status_code} ({response_time:.3f}s)")
            else:
                logger.error(f"❌ {endpoint['name']}: Expected {endpoint['expected_status']}, got {response.status_code}")
                if response.status_code != 200:
                    logger.error(f"   Response: {result['response_data']}")
        
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                "name": endpoint["name"],
                "url": endpoint["url"],
                "method": endpoint["method"],
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
            results.append(result)
            logger.error(f"❌ {endpoint['name']}: {str(e)}")
    
    # Generate summary
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - successful_tests
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    avg_response_time = sum(r["response_time"] for r in results) / total_tests if total_tests > 0 else 0
    
    logger.info("=" * 60)
    logger.info("📊 PHASE 3 VERIFICATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Successful: {successful_tests}")
    logger.info(f"Failed: {failed_tests}")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    logger.info(f"Average Response Time: {avg_response_time:.3f}s")
    
    if failed_tests > 0:
        logger.info("\n❌ FAILED TESTS:")
        for result in results:
            if not result["success"]:
                logger.info(f"   {result['method']} {result['url']}: {result['status_code']}")
                if "error" in result:
                    logger.info(f"      Error: {result['error']}")
    
    # Save detailed results
    report_file = f"phase3_verification_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "average_response_time": avg_response_time
            },
            "results": results
        }, f, indent=2)
    
    logger.info(f"\n📄 Detailed report saved to: {report_file}")
    
    return success_rate >= 80  # 80% success threshold

if __name__ == "__main__":
    success = test_phase3_endpoints()
    if success:
        logger.info("\n🎉 Phase 3 verification completed successfully!")
        exit(0)
    else:
        logger.error("\n💥 Phase 3 verification failed!")
        exit(1)
