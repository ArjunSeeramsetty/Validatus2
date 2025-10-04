#!/usr/bin/env python3
"""
Complete deployment verification script for Validatus
Tests all components and provides comprehensive status report
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
import subprocess
import os


class DeploymentTester:
    def __init__(self, project_id: str, region: str = "us-central1", service_name: str = "validatus-backend"):
        self.project_id = project_id
        self.region = region
        self.service_name = service_name
        self.service_url = None
        self.test_results = {}
        
    def log(self, message: str, status: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        print(f"[{timestamp}] {status_emoji.get(status, 'ℹ️')} {message}")
    
    def get_service_url(self) -> Optional[str]:
        """Get the Cloud Run service URL"""
        try:
            result = subprocess.run([
                "gcloud", "run", "services", "describe", self.service_name,
                "--region", self.region,
                "--format", "value(status.url)"
            ], capture_output=True, text=True, check=True)
            
            self.service_url = result.stdout.strip()
            if self.service_url:
                self.log(f"Service URL: {self.service_url}", "SUCCESS")
                return self.service_url
            else:
                self.log("Failed to get service URL", "ERROR")
                return None
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to get service URL: {e}", "ERROR")
            return None
    
    def test_gcp_tools(self) -> bool:
        """Test if required GCP tools are available"""
        self.log("Testing GCP tools availability...")
        
        tools = {
            "gcloud": "gcloud version",
            "terraform": "terraform version",
            "gsutil": "gsutil version"
        }
        
        all_available = True
        for tool, command in tools.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True, check=True)
                version = result.stdout.split('\n')[0]
                self.log(f"{tool}: {version}", "SUCCESS")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log(f"{tool}: Not available", "ERROR")
                all_available = False
        
        self.test_results["gcp_tools"] = all_available
        return all_available
    
    def test_gcp_authentication(self) -> bool:
        """Test GCP authentication"""
        self.log("Testing GCP authentication...")
        
        try:
            result = subprocess.run([
                "gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"
            ], capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                account = result.stdout.strip()
                self.log(f"Authenticated as: {account}", "SUCCESS")
                
                # Check project
                result = subprocess.run([
                    "gcloud", "config", "get-value", "project"
                ], capture_output=True, text=True, check=True)
                
                current_project = result.stdout.strip()
                if current_project == self.project_id:
                    self.log(f"Project: {current_project}", "SUCCESS")
                    self.test_results["gcp_auth"] = True
                    return True
                else:
                    self.log(f"Project mismatch: {current_project} (expected: {self.project_id})", "WARNING")
                    self.test_results["gcp_auth"] = False
                    return False
            else:
                self.log("Not authenticated", "ERROR")
                self.test_results["gcp_auth"] = False
                return False
        except subprocess.CalledProcessError:
            self.log("Authentication check failed", "ERROR")
            self.test_results["gcp_auth"] = False
            return False
    
    def test_infrastructure(self) -> bool:
        """Test GCP infrastructure components"""
        self.log("Testing GCP infrastructure...")
        
        infrastructure_healthy = True
        
        # Test Cloud SQL
        try:
            result = subprocess.run([
                "gcloud", "sql", "instances", "list", "--filter=name:validatus-primary",
                "--format=value(name)"
            ], capture_output=True, text=True, check=True)
            
            if "validatus-primary" in result.stdout:
                self.log("Cloud SQL: validatus-primary exists", "SUCCESS")
            else:
                self.log("Cloud SQL: validatus-primary not found", "ERROR")
                infrastructure_healthy = False
        except subprocess.CalledProcessError:
            self.log("Cloud SQL check failed", "ERROR")
            infrastructure_healthy = False
        
        # Test Cloud Storage
        try:
            result = subprocess.run([
                "gsutil", "ls"
            ], capture_output=True, text=True, check=True)
            
            if "validatus" in result.stdout:
                self.log("Cloud Storage: Buckets found", "SUCCESS")
            else:
                self.log("Cloud Storage: No validatus buckets found", "WARNING")
        except subprocess.CalledProcessError:
            self.log("Cloud Storage check failed", "WARNING")
        
        # Test Redis
        try:
            result = subprocess.run([
                "gcloud", "redis", "instances", "list", "--filter=name:validatus-cache",
                "--format=value(name)"
            ], capture_output=True, text=True, check=True)
            
            if "validatus-cache" in result.stdout:
                self.log("Redis: validatus-cache exists", "SUCCESS")
            else:
                self.log("Redis: validatus-cache not found", "WARNING")
        except subprocess.CalledProcessError:
            self.log("Redis check failed", "WARNING")
        
        self.test_results["infrastructure"] = infrastructure_healthy
        return infrastructure_healthy
    
    def test_application_health(self) -> bool:
        """Test application health endpoint"""
        self.log("Testing application health...")
        
        if not self.service_url:
            self.log("Service URL not available", "ERROR")
            self.test_results["app_health"] = False
            return False
        
        try:
            response = requests.get(f"{self.service_url}/health", timeout=30)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    self.log("Application health: Healthy", "SUCCESS")
                    
                    # Check GCP services status
                    if "gcp_services" in health_data:
                        services = health_data["gcp_services"].get("services", {})
                        for service_name, service_status in services.items():
                            if service_status.get("status") == "healthy":
                                self.log(f"  {service_name}: Healthy", "SUCCESS")
                            else:
                                self.log(f"  {service_name}: {service_status.get('status', 'Unknown')}", "WARNING")
                    
                    self.test_results["app_health"] = True
                    return True
                else:
                    self.log(f"Application health: {health_data.get('status', 'Unknown')}", "WARNING")
                    self.test_results["app_health"] = False
                    return False
            else:
                self.log(f"Health check failed: HTTP {response.status_code}", "ERROR")
                self.test_results["app_health"] = False
                return False
        except requests.RequestException as e:
            self.log(f"Health check failed: {e}", "ERROR")
            self.test_results["app_health"] = False
            return False
    
    def test_api_functionality(self) -> bool:
        """Test API functionality"""
        self.log("Testing API functionality...")
        
        if not self.service_url:
            self.log("Service URL not available", "ERROR")
            self.test_results["api_functionality"] = False
            return False
        
        # Test topic creation
        try:
            topic_data = {
                "title": f"Test Topic {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "description": "Automated test topic creation",
                "analysis_type": "comprehensive",
                "user_id": "test_user_deployment"
            }
            
            response = requests.post(
                f"{self.service_url}/api/v3/topics/create",
                json=topic_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                topic_response = response.json()
                if "topic_id" in topic_response:
                    self.log(f"Topic creation: Success ({topic_response['topic_id']})", "SUCCESS")
                    
                    # Test topic retrieval
                    get_response = requests.get(f"{self.service_url}/api/v3/topics", timeout=30)
                    if get_response.status_code == 200:
                        topics_data = get_response.json()
                        topics_count = len(topics_data.get("topics", []))
                        self.log(f"Topic retrieval: Success ({topics_count} topics)", "SUCCESS")
                        self.test_results["api_functionality"] = True
                        return True
                    else:
                        self.log(f"Topic retrieval failed: HTTP {get_response.status_code}", "ERROR")
                        self.test_results["api_functionality"] = False
                        return False
                else:
                    self.log("Topic creation: No topic_id returned", "ERROR")
                    self.test_results["api_functionality"] = False
                    return False
            else:
                self.log(f"Topic creation failed: HTTP {response.status_code}", "ERROR")
                self.test_results["api_functionality"] = False
                return False
        except requests.RequestException as e:
            self.log(f"API test failed: {e}", "ERROR")
            self.test_results["api_functionality"] = False
            return False
    
    def test_performance(self) -> bool:
        """Test application performance"""
        self.log("Testing application performance...")
        
        if not self.service_url:
            self.log("Service URL not available", "ERROR")
            self.test_results["performance"] = False
            return False
        
        response_times = []
        test_count = 5
        
        for i in range(test_count):
            try:
                start_time = time.time()
                response = requests.get(f"{self.service_url}/health", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    response_times.append(response_time)
                    self.log(f"  Request {i+1}: {response_time:.0f}ms", "INFO")
                else:
                    self.log(f"  Request {i+1}: Failed (HTTP {response.status_code})", "ERROR")
            except requests.RequestException as e:
                self.log(f"  Request {i+1}: Failed ({e})", "ERROR")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            self.log(f"Performance: Avg {avg_response_time:.0f}ms, Min {min_response_time:.0f}ms, Max {max_response_time:.0f}ms", "SUCCESS")
            
            if avg_response_time < 2000:  # Less than 2 seconds
                self.log("Performance: Good (< 2s)", "SUCCESS")
                self.test_results["performance"] = True
                return True
            else:
                self.log("Performance: Slow (> 2s)", "WARNING")
                self.test_results["performance"] = False
                return False
        else:
            self.log("Performance: No successful requests", "ERROR")
            self.test_results["performance"] = False
            return False
    
    def generate_report(self) -> None:
        """Generate comprehensive test report"""
        self.log("Generating test report...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print("\n" + "="*60)
        print("🧪 VALIDATUS DEPLOYMENT TEST REPORT")
        print("="*60)
        print(f"Project ID: {self.project_id}")
        print(f"Region: {self.region}")
        print(f"Service: {self.service_name}")
        print(f"Service URL: {self.service_url or 'Not available'}")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*60)
        
        # Individual test results
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print("-"*60)
        print(f"Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Deployment is fully operational!")
            print("\n📋 Your Validatus application is ready for production use!")
            print(f"🌐 Application URL: {self.service_url}")
            print(f"📋 Health Check: {self.service_url}/health")
            print(f"📖 API Docs: {self.service_url}/docs")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ MOSTLY SUCCESSFUL - Minor issues detected")
            print("Review the failed tests above and address any issues.")
        else:
            print("❌ DEPLOYMENT ISSUES DETECTED")
            print("Please review the failed tests and check your deployment.")
        
        print("\n📚 Next Steps:")
        print("1. Test your application thoroughly")
        print("2. Configure monitoring and alerts")
        print("3. Set up backup and disaster recovery")
        print("4. Configure team access and permissions")
        
        print("="*60)
    
    async def run_all_tests(self) -> bool:
        """Run all deployment tests"""
        self.log("Starting comprehensive deployment tests...")
        
        # Get service URL first
        self.get_service_url()
        
        # Run all tests
        self.test_gcp_tools()
        self.test_gcp_authentication()
        self.test_infrastructure()
        self.test_application_health()
        self.test_api_functionality()
        self.test_performance()
        
        # Generate report
        self.generate_report()
        
        # Return overall success
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        return passed_tests == total_tests


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Validatus deployment")
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--region", default="us-central1", help="GCP Region")
    parser.add_argument("--service-name", default="validatus-backend", help="Cloud Run service name")
    
    args = parser.parse_args()
    
    print("🧪 Validatus Deployment Test Suite")
    print("="*50)
    
    tester = DeploymentTester(args.project_id, args.region, args.service_name)
    
    try:
        success = asyncio.run(tester.run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
