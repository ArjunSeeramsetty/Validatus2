#!/usr/bin/env python3
"""
Individual Task Testing Script for Validatus2
=============================================

This script allows testing individual tasks of the Validatus2 platform.
Useful for debugging specific components or testing in isolation.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"

class IndividualTaskTester:
    """Test individual tasks in isolation"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_task1_only(self):
        """Test only Task 1: Topic Creation"""
        self.log("🚀 Testing Task 1: Topic Creation Only")
        
        topic_id = f"pergola_test_{int(time.time())}"
        user_id = "test_user"
        
        create_request = {
            "topic_id": topic_id,
            "user_id": user_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v3/sequential-analysis/topics/{topic_id}/analysis/create",
                json=create_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log(f"✅ Topic created: {topic_id}")
                    self.log(f"   Session ID: {result.get('session_id')}")
                    return result.get('session_id')
                else:
                    self.log(f"❌ Topic creation failed: {result.get('message')}", "ERROR")
            else:
                self.log(f"❌ Request failed: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", "ERROR")
        
        return None
    
    def test_stage1_only(self, session_id: str):
        """Test only Stage 1: Web Search and Content Processing"""
        self.log("🔍 Testing Stage 1: Web Search and Content Processing")
        
        try:
            # Start Stage 1
            response = requests.post(
                f"{self.base_url}/api/v3/sequential-analysis/analysis/{session_id}/stage1/start",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log("✅ Stage 1 started successfully")
                    
                    # Monitor progress
                    return self._monitor_stage_progress(session_id, 1)
                else:
                    self.log(f"❌ Stage 1 start failed: {result.get('message')}", "ERROR")
            else:
                self.log(f"❌ Stage 1 start failed: {response.status_code}", "ERROR")
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Stage 1 start failed: {e}", "ERROR")
        
        return False
    
    def test_stage2_only(self, session_id: str):
        """Test only Stage 2: Vector DB and Search"""
        self.log("🔗 Testing Stage 2: Vector DB Creation and Search")
        
        try:
            # Start Stage 2
            response = requests.post(
                f"{self.base_url}/api/v3/sequential-analysis/analysis/{session_id}/stage2/start",
                json={"query": "What is the pergola market size?"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log("✅ Stage 2 started successfully")
                    
                    # Monitor progress
                    return self._monitor_stage_progress(session_id, 2)
                else:
                    self.log(f"❌ Stage 2 start failed: {result.get('message')}", "ERROR")
            else:
                self.log(f"❌ Stage 2 start failed: {response.status_code}", "ERROR")
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Stage 2 start failed: {e}", "ERROR")
        
        return False
    
    def _monitor_stage_progress(self, session_id: str, stage: int, max_wait: int = 300):
        """Monitor stage progress"""
        self.log(f"⏳ Monitoring Stage {stage} progress...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v3/sequential-analysis/analysis/{session_id}/stage{stage}/status",
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status", "unknown")
                    
                    if status == "completed":
                        self.log(f"✅ Stage {stage} completed successfully")
                        return True
                    elif status == "failed":
                        self.log(f"❌ Stage {stage} failed", "ERROR")
                        return False
                    else:
                        self.log(f"   Stage {stage} status: {status}")
                        time.sleep(5)
                else:
                    self.log(f"   Status check failed: {response.status_code}")
                    time.sleep(5)
                    
            except requests.exceptions.RequestException as e:
                self.log(f"   Status check error: {e}")
                time.sleep(5)
        
        self.log(f"❌ Stage {stage} timed out", "ERROR")
        return False
    
    def test_pergola_intelligence_only(self):
        """Test only Pergola Intelligence endpoints"""
        self.log("🧠 Testing Pergola Intelligence Endpoints")
        
        endpoints = [
            ("/api/v3/pergola/market-intelligence", "Market Intelligence"),
            ("/api/v3/pergola-intelligence/", "Intelligence Dashboard"),
            ("/api/v3/pergola-intelligence/market-insights", "Market Insights"),
            ("/api/v3/pergola-intelligence/competitive-landscape", "Competitive Landscape")
        ]
        
        results = {}
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success" or result.get("success"):
                        self.log(f"✅ {name}: Success")
                        results[name] = "success"
                    else:
                        self.log(f"❌ {name}: Failed - {result.get('message', 'Unknown error')}", "ERROR")
                        results[name] = "failed"
                else:
                    self.log(f"❌ {name}: HTTP {response.status_code}", "ERROR")
                    results[name] = "failed"
                    
            except requests.exceptions.RequestException as e:
                self.log(f"❌ {name}: Request failed - {e}", "ERROR")
                results[name] = "failed"
        
        return results
    
    def test_semantic_search_only(self):
        """Test only Semantic Search functionality"""
        self.log("🔍 Testing Semantic Search")
        
        queries = [
            "What is the global pergola market size?",
            "What are the key trends in outdoor living?",
            "Which pergola materials are most popular?"
        ]
        
        results = {}
        
        for query in queries:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v3/pergola-intelligence/search",
                    params={"query": query, "max_results": 3},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    search_results = result.get("results", [])
                    self.log(f"✅ Query: '{query}' - {len(search_results)} results")
                    results[query] = {"status": "success", "results_count": len(search_results)}
                else:
                    self.log(f"❌ Query: '{query}' - HTTP {response.status_code}", "ERROR")
                    results[query] = {"status": "failed", "error": f"HTTP {response.status_code}"}
                    
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Query: '{query}' - Request failed: {e}", "ERROR")
                results[query] = {"status": "failed", "error": str(e)}
        
        return results

def main():
    """Main function for individual task testing"""
    if len(sys.argv) < 2:
        print("Usage: python test_individual_tasks.py <task> [base_url]")
        print("\nAvailable tasks:")
        print("  task1          - Test Topic Creation only")
        print("  stage1         - Test Stage 1 (Web Search + Content Processing)")
        print("  stage2         - Test Stage 2 (Vector DB + Search)")
        print("  pergola        - Test Pergola Intelligence endpoints")
        print("  search         - Test Semantic Search")
        print("  workflow       - Test complete workflow (Task 1 -> Stage 1 -> Stage 2)")
        print("\nExample: python test_individual_tasks.py task1")
        print("Example: python test_individual_tasks.py pergola http://localhost:8000")
        sys.exit(1)
    
    task = sys.argv[1]
    base_url = sys.argv[2] if len(sys.argv) > 2 else BASE_URL
    
    tester = IndividualTaskTester(base_url)
    
    print(f"🧪 Testing Task: {task}")
    print(f"🌐 Backend URL: {base_url}")
    print("=" * 50)
    
    if task == "task1":
        session_id = tester.test_task1_only()
        if session_id:
            print(f"\n✅ Task 1 completed successfully!")
            print(f"📝 Session ID: {session_id}")
        else:
            print(f"\n❌ Task 1 failed!")
    
    elif task == "stage1":
        session_id = input("Enter Session ID: ").strip()
        if not session_id:
            print("❌ Session ID is required for Stage 1 test")
            sys.exit(1)
        
        success = tester.test_stage1_only(session_id)
        if success:
            print(f"\n✅ Stage 1 completed successfully!")
        else:
            print(f"\n❌ Stage 1 failed!")
    
    elif task == "stage2":
        session_id = input("Enter Session ID: ").strip()
        if not session_id:
            print("❌ Session ID is required for Stage 2 test")
            sys.exit(1)
        
        success = tester.test_stage2_only(session_id)
        if success:
            print(f"\n✅ Stage 2 completed successfully!")
        else:
            print(f"\n❌ Stage 2 failed!")
    
    elif task == "pergola":
        results = tester.test_pergola_intelligence_only()
        success_count = sum(1 for r in results.values() if r == "success")
        total_count = len(results)
        print(f"\n📊 Pergola Intelligence Results: {success_count}/{total_count} passed")
    
    elif task == "search":
        results = tester.test_semantic_search_only()
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        total_count = len(results)
        print(f"\n📊 Semantic Search Results: {success_count}/{total_count} passed")
    
    elif task == "workflow":
        print("🚀 Running Complete Workflow Test...")
        session_id = tester.test_task1_only()
        if session_id:
            print(f"\n✅ Task 1 completed - Session ID: {session_id}")
            
            print("\n🔍 Starting Stage 1...")
            stage1_success = tester.test_stage1_only(session_id)
            if stage1_success:
                print("\n✅ Stage 1 completed successfully!")
                
                print("\n🔗 Starting Stage 2...")
                stage2_success = tester.test_stage2_only(session_id)
                if stage2_success:
                    print("\n✅ Complete workflow test successful!")
                else:
                    print("\n❌ Stage 2 failed - workflow incomplete")
            else:
                print("\n❌ Stage 1 failed - workflow stopped")
        else:
            print("\n❌ Task 1 failed - cannot proceed with workflow")
    
    else:
        print(f"❌ Unknown task: {task}")
        sys.exit(1)

if __name__ == "__main__":
    main()
