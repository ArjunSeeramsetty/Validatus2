#!/usr/bin/env python3
"""
Validatus API Endpoint Verification Script
This script tests all Phase 1 and Phase 2 API endpoints to ensure complete functionality
"""

import requests
import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None

class APIEndpointVerifier:
    """Comprehensive API endpoint verification"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        
        # Test data
        self.sample_urls = [
            "https://example.com/ai-article1",
            "https://example.com/ai-article2",
            "https://example.com/ai-article3"
        ]
        
        self.sample_content = """
        This is a comprehensive article about artificial intelligence and machine learning.
        It covers various topics including deep learning, neural networks, and natural language processing.
        The article provides detailed explanations with examples and use cases.
        It includes references to recent research and industry applications.
        """
        
        self.sample_documents = [
            {
                "content": "AI is transforming healthcare with diagnostic tools",
                "url": "https://example.com/ai-healthcare",
                "title": "AI in Healthcare"
            },
            {
                "content": "Machine learning algorithms improve business processes",
                "url": "https://example.com/ml-business",
                "title": "ML in Business"
            }
        ]
    
    def test_endpoint(self, method: str, endpoint: str, **kwargs) -> TestResult:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, **kwargs, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, **kwargs, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            success = 200 <= response.status_code < 400
            
            result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                response_data=response_data
            )
            
            if not success:
                result.error_message = f"HTTP {response.status_code}: {response.text}"
            
            return result
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
    
    def verify_health_endpoints(self):
        """Verify health and monitoring endpoints"""
        logger.info("🔍 Verifying health endpoints...")
        
        # Health check
        result = self.test_endpoint("GET", "/health")
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Health check: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Health check failed: {result.error_message}")
    
    def verify_phase1_endpoints(self):
        """Verify Phase 1 basic topic management endpoints"""
        logger.info("🔍 Verifying Phase 1 endpoints...")
        
        # List topics
        result = self.test_endpoint("GET", "/api/v3/topics")
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ List topics: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ List topics failed: {result.error_message}")
        
        # Create topic
        result = self.test_endpoint("POST", "/api/v3/topics/create", 
                                  json={
                                      "topic": "test-verification-topic",
                                      "urls": self.sample_urls
                                  })
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Create topic: {result.status_code} ({result.response_time:.3f}s)")
            topic_id = result.response_data.get("topic_id", "test-topic")
        else:
            logger.error(f"❌ Create topic failed: {result.error_message}")
            topic_id = "test-topic"
        
        # Collect URLs
        result = self.test_endpoint("POST", f"/api/v3/topics/{topic_id}/collect-urls",
                                  json={
                                      "search_query": "artificial intelligence",
                                      "max_urls": 10
                                  })
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Collect URLs: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Collect URLs failed: {result.error_message}")
        
        # Get evidence
        result = self.test_endpoint("GET", f"/api/v3/topics/{topic_id}/evidence/consumer")
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Get evidence: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Get evidence failed: {result.error_message}")
    
    def verify_phase2_enhanced_endpoints(self):
        """Verify Phase 2 enhanced topic management endpoints"""
        logger.info("🔍 Verifying Phase 2 enhanced endpoints...")
        
        # Create enhanced topic
        result = self.test_endpoint("POST", "/api/v3/enhanced/topics/create",
                                  json={
                                      "topic": "enhanced-test-topic",
                                      "urls": self.sample_urls,
                                      "quality_threshold": 0.7
                                  })
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Create enhanced topic: {result.status_code} ({result.response_time:.3f}s)")
            topic_id = result.response_data.get("topic_id", "enhanced-test-topic")
        else:
            logger.error(f"❌ Create enhanced topic failed: {result.error_message}")
            topic_id = "enhanced-test-topic"
        
        # Get enhanced topic knowledge
        result = self.test_endpoint("GET", f"/api/v3/enhanced/topics/{topic_id}/knowledge")
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Get enhanced knowledge: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Get enhanced knowledge failed: {result.error_message}")
        
        # Update enhanced topic
        result = self.test_endpoint("PUT", f"/api/v3/enhanced/topics/{topic_id}/update",
                                  json={
                                      "new_urls": ["https://example.com/new-article"],
                                      "quality_threshold": 0.8
                                  })
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Update enhanced topic: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Update enhanced topic failed: {result.error_message}")
        
        # Analyze topic performance
        result = self.test_endpoint("GET", f"/api/v3/enhanced/topics/{topic_id}/performance")
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Analyze topic performance: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Analyze topic performance failed: {result.error_message}")
    
    def verify_strategic_analysis_endpoints(self):
        """Verify strategic analysis endpoints"""
        logger.info("🔍 Verifying strategic analysis endpoints...")
        
        # Create analysis session
        result = self.test_endpoint("POST", "/api/v3/analysis/sessions/create",
                                  json={
                                      "topic": "strategic-analysis-test",
                                      "user_id": "test-user-123",
                                      "analysis_parameters": {
                                          "quality_threshold": 0.7,
                                          "include_competitive_analysis": True
                                      }
                                  })
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Create analysis session: {result.status_code} ({result.response_time:.3f}s)")
            session_id = result.response_data.get("session_id", "test-session-123")
        else:
            logger.error(f"❌ Create analysis session failed: {result.error_message}")
            session_id = "test-session-123"
        
        # Execute strategic analysis
        result = self.test_endpoint("POST", f"/api/v3/analysis/sessions/{session_id}/execute")
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Execute strategic analysis: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Execute strategic analysis failed: {result.error_message}")
        
        # Get analysis status
        result = self.test_endpoint("GET", f"/api/v3/analysis/sessions/{session_id}/status")
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Get analysis status: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Get analysis status failed: {result.error_message}")
        
        # Get analysis results
        result = self.test_endpoint("GET", f"/api/v3/analysis/sessions/{session_id}/results")
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Get analysis results: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Get analysis results failed: {result.error_message}")
    
    def verify_content_processing_endpoints(self):
        """Verify content processing endpoints"""
        logger.info("🔍 Verifying content processing endpoints...")
        
        # Analyze content quality
        result = self.test_endpoint("POST", "/api/v3/content/analyze-quality",
                                  json={
                                      "content": self.sample_content,
                                      "url": "https://example.com/test-article",
                                      "topic": "artificial intelligence"
                                  })
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Analyze content quality: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Analyze content quality failed: {result.error_message}")
        
        # Deduplicate content
        result = self.test_endpoint("POST", "/api/v3/content/deduplicate",
                                  json={
                                      "documents": self.sample_documents,
                                      "similarity_threshold": 0.85
                                  })
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Deduplicate content: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Deduplicate content failed: {result.error_message}")
    
    def verify_optimization_endpoints(self):
        """Verify optimization endpoints"""
        logger.info("🔍 Verifying optimization endpoints...")
        
        # Optimize parallel processing
        result = self.test_endpoint("POST", "/api/v3/optimization/parallel-processing",
                                  json={
                                      "analysis_tasks": [
                                          {
                                              "id": "task_1",
                                              "type": "layer_scoring",
                                              "complexity": "medium",
                                              "layer": "consumer"
                                          },
                                          {
                                              "id": "task_2",
                                              "type": "factor_calculation",
                                              "complexity": "light",
                                              "factor": "market_attractiveness"
                                          }
                                      ],
                                      "max_concurrent": 10
                                  })
        self.test_results.append(result)
        
        if result.success:
            logger.info(f"✅ Optimize parallel processing: {result.status_code} ({result.response_time:.3f}s)")
        else:
            logger.error(f"❌ Optimize parallel processing failed: {result.error_message}")
    
    def verify_error_handling(self):
        """Verify error handling for invalid requests"""
        logger.info("🔍 Verifying error handling...")
        
        # Test invalid endpoint
        result = self.test_endpoint("GET", "/api/v3/nonexistent-endpoint")
        self.test_results.append(result)
        
        if result.status_code == 404:
            logger.info(f"✅ Error handling (404): {result.status_code}")
        else:
            logger.error(f"❌ Error handling failed: Expected 404, got {result.status_code}")
        
        # Test invalid request data
        result = self.test_endpoint("POST", "/api/v3/topics/create",
                                  json={
                                      "topic": "",  # Empty topic
                                      "urls": []    # Empty URLs
                                  })
        self.test_results.append(result)
        
        if result.status_code == 422:  # Validation error
            logger.info(f"✅ Error handling (422): {result.status_code}")
        else:
            logger.error(f"❌ Error handling failed: Expected 422, got {result.status_code}")
    
    def verify_performance_requirements(self):
        """Verify that endpoints meet performance requirements"""
        logger.info("🔍 Verifying performance requirements...")
        
        slow_endpoints = []
        
        for result in self.test_results:
            if result.success and result.response_time > 5.0:  # More than 5 seconds
                slow_endpoints.append(f"{result.method} {result.endpoint}: {result.response_time:.3f}s")
        
        if slow_endpoints:
            logger.warning("⚠️ Slow endpoints detected:")
            for endpoint in slow_endpoints:
                logger.warning(f"   - {endpoint}")
        else:
            logger.info("✅ All endpoints meet performance requirements")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - successful_tests
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group results by endpoint category
        categories = {
            "Health": [],
            "Phase 1": [],
            "Phase 2 Enhanced": [],
            "Strategic Analysis": [],
            "Content Processing": [],
            "Optimization": [],
            "Error Handling": []
        }
        
        for result in self.test_results:
            endpoint = result.endpoint
            if endpoint.startswith("/health"):
                categories["Health"].append(result)
            elif endpoint.startswith("/api/v3/topics") and "enhanced" not in endpoint:
                categories["Phase 1"].append(result)
            elif "enhanced" in endpoint:
                categories["Phase 2 Enhanced"].append(result)
            elif "analysis" in endpoint:
                categories["Strategic Analysis"].append(result)
            elif "content" in endpoint:
                categories["Content Processing"].append(result)
            elif "optimization" in endpoint:
                categories["Optimization"].append(result)
            else:
                categories["Error Handling"].append(result)
        
        # Calculate average response times
        avg_response_time = sum(result.response_time for result in self.test_results) / total_tests if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": round(success_rate, 2),
                "average_response_time": round(avg_response_time, 3),
                "test_timestamp": datetime.now().isoformat()
            },
            "categories": {},
            "failed_endpoints": [
                {
                    "endpoint": result.endpoint,
                    "method": result.method,
                    "status_code": result.status_code,
                    "error_message": result.error_message
                }
                for result in self.test_results if not result.success
            ],
            "performance_issues": [
                {
                    "endpoint": result.endpoint,
                    "method": result.method,
                    "response_time": result.response_time
                }
                for result in self.test_results if result.response_time > 5.0
            ]
        }
        
        # Add category summaries
        for category, results in categories.items():
            if results:
                category_success = sum(1 for r in results if r.success)
                category_total = len(results)
                category_success_rate = (category_success / category_total * 100) if category_total > 0 else 0
                
                report["categories"][category] = {
                    "total_tests": category_total,
                    "successful_tests": category_success,
                    "success_rate": round(category_success_rate, 2),
                    "average_response_time": round(sum(r.response_time for r in results) / category_total, 3)
                }
        
        return report
    
    def run_all_tests(self):
        """Run all endpoint verification tests"""
        logger.info("🚀 Starting Validatus API Endpoint Verification")
        logger.info(f"Base URL: {self.base_url}")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.verify_health_endpoints()
        self.verify_phase1_endpoints()
        self.verify_phase2_enhanced_endpoints()
        self.verify_strategic_analysis_endpoints()
        self.verify_content_processing_endpoints()
        self.verify_optimization_endpoints()
        self.verify_error_handling()
        self.verify_performance_requirements()
        
        total_time = time.time() - start_time
        
        # Generate and display report
        report = self.generate_report()
        
        logger.info("=" * 60)
        logger.info("📊 VERIFICATION REPORT")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Successful: {report['summary']['successful_tests']}")
        logger.info(f"Failed: {report['summary']['failed_tests']}")
        logger.info(f"Success Rate: {report['summary']['success_rate']}%")
        logger.info(f"Average Response Time: {report['summary']['average_response_time']}s")
        logger.info(f"Total Test Time: {total_time:.2f}s")
        
        logger.info("\n📋 CATEGORY BREAKDOWN:")
        for category, stats in report['categories'].items():
            if stats['total_tests'] > 0:
                logger.info(f"  {category}: {stats['successful_tests']}/{stats['total_tests']} ({stats['success_rate']}%) - {stats['average_response_time']}s avg")
        
        if report['failed_endpoints']:
            logger.info("\n❌ FAILED ENDPOINTS:")
            for failure in report['failed_endpoints']:
                logger.info(f"  {failure['method']} {failure['endpoint']}: {failure['status_code']} - {failure['error_message']}")
        
        if report['performance_issues']:
            logger.info("\n⚠️ PERFORMANCE ISSUES:")
            for issue in report['performance_issues']:
                logger.info(f"  {issue['method']} {issue['endpoint']}: {issue['response_time']}s")
        
        # Save detailed report
        report_file = f"api_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n📄 Detailed report saved to: {report_file}")
        
        # Return success status
        return report['summary']['success_rate'] >= 80  # 80% success rate threshold

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Validatus API endpoints")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the API (default: http://localhost:8000)")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    verifier = APIEndpointVerifier(args.url)
    success = verifier.run_all_tests()
    
    if success:
        logger.info("\n🎉 API verification completed successfully!")
        exit(0)
    else:
        logger.error("\n💥 API verification failed!")
        exit(1)

if __name__ == "__main__":
    main()
