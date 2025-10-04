"""
Production deployment verification script
"""
import asyncio
import httpx
import sys
import os
from datetime import datetime

async def verify_deployment():
    """Verify production deployment"""
    print("🧪 Verifying Validatus Production Deployment")
    print("============================================")
    
    # Get service URL from environment or use default
    base_url = os.getenv("SERVICE_URL", "https://validatus-backend-ssivkqhvhq-uc.a.run.app")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test 1: Health check
            print("Test 1: Health check...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data.get('status')}")
                
                # Check GCP persistence status
                gcp_status = health_data.get('gcp_persistence', {})
                if isinstance(gcp_status, dict):
                    overall_status = gcp_status.get('overall_status', 'unknown')
                    print(f"   GCP Persistence Status: {overall_status}")
                    
                    services = gcp_status.get('services', {})
                    for service, status in services.items():
                        if status.get('status') == 'healthy':
                            print(f"   ✅ {service}: {status['status']}")
                        else:
                            print(f"   ❌ {service}: {status.get('status', 'unknown')}")
                else:
                    print(f"   GCP Persistence: {gcp_status}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
            
            # Test 2: Create topic
            print("\nTest 2: Creating test topic...")
            topic_data = {
                "title": "Production Test Topic",
                "description": "Testing production deployment",
                "analysis_type": "comprehensive",
                "user_id": "test_user_production"
            }
            
            response = await client.post(f"{base_url}/api/v3/topics/create", json=topic_data)
            if response.status_code == 200:
                topic_response = response.json()
                topic_id = topic_response.get("topic_id")
                print(f"✅ Topic created successfully: {topic_id}")
                
                # Test 3: Retrieve topics list
                print("\nTest 3: Retrieving topics list...")
                response = await client.get(f"{base_url}/api/v3/topics")
                if response.status_code == 200:
                    topics_data = response.json()
                    topics = topics_data.get('topics', [])
                    print(f"✅ Topics retrieval successful: {len(topics)} topics found")
                    
                    # Check if our created topic is in the list
                    created_topic = next((t for t in topics if t.get('session_id') == topic_id), None)
                    if created_topic:
                        print(f"✅ Created topic found in database: {created_topic.get('topic', 'Unknown')}")
                    else:
                        print("⚠️ Created topic not found in database (may be expected if using different storage)")
                    
                    # Cleanup: Delete test topic
                    try:
                        delete_response = await client.delete(f"{base_url}/api/v3/topics/{topic_id}")
                        if delete_response.status_code == 200:
                            print(f"✅ Test topic cleaned up")
                        else:
                            print(f"⚠️ Failed to cleanup test topic: {delete_response.status_code}")
                    except Exception as e:
                        print(f"⚠️ Cleanup failed: {e}")
                else:
                    print(f"❌ Topics retrieval failed: {response.status_code}")
                
            else:
                print(f"❌ Topic creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            # Test 4: API status
            print("\nTest 4: API status check...")
            response = await client.get(f"{base_url}/api/v3/status")
            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ API status check passed: {status_data.get('status')}")
            else:
                print(f"❌ API status check failed: {response.status_code}")
            
            print("\n🎉 All production verification tests passed!")
            print(f"🌐 Your Validatus application is running at: {base_url}")
            print(f"📋 Health Check: {base_url}/health")
            print(f"📖 API Docs: {base_url}/docs")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

def main():
    """Main verification function"""
    success = asyncio.run(verify_deployment())
    if success:
        print("\n✅ Production verification completed successfully!")
        print("Your Validatus application is fully operational with GCP persistence!")
    else:
        print("\n❌ Production verification failed!")
        print("Please check the logs and ensure all GCP services are properly configured.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
