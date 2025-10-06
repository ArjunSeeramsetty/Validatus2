"""
Test script for Google Custom Search integration
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.integrated_topic_service import get_integrated_topic_service
from app.models.topic_models import TopicCreateRequest, AnalysisType

async def test_integrated_topic_creation():
    """Test the complete integrated workflow"""
    
    print("🧪 Testing Google Custom Search Integration")
    print("=" * 50)
    
    try:
        # Get service
        service = await get_integrated_topic_service()
        
        # Test topic creation with URL collection
        print("\n📋 Test 1: Creating topic with URL collection")
        
        request = TopicCreateRequest(
            topic="AI and Machine Learning Market Trends 2025",
            description="Comprehensive analysis of AI and ML market trends for 2025",
            search_queries=[
                "artificial intelligence market trends 2025",
                "machine learning enterprise adoption",
                "AI investment trends 2025"
            ],
            initial_urls=[
                "https://www.mckinsey.com/capabilities/quantumblack/our-insights",
                "https://www.gartner.com/en/information-technology"
            ],
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="test_user_integration",
            metadata={
                "test": True,
                "integration_test": "google_search"
            }
        )
        
        result = await service.create_topic_with_url_collection(request)
        
        print(f"✅ Topic created: {result['session_id']}")
        print(f"✅ URL collection status: {result['url_collection']['status']}")
        print(f"✅ URLs collected: {result['url_collection']['urls_collected']}")
        print(f"✅ Queries processed: {result['url_collection']['queries_processed']}")
        
        # Test retrieving topic with URLs
        print("\n📋 Test 2: Retrieving topic with URLs")
        
        topic_with_urls = await service.get_topic_with_urls(result['session_id'])
        
        if topic_with_urls and 'collected_urls' in topic_with_urls:
            urls_data = topic_with_urls['collected_urls']
            print(f"✅ Retrieved {urls_data['url_count']} URLs")
            
            # Show sample URLs
            for i, url in enumerate(urls_data.get('urls', [])[:3]):
                print(f"   {i+1}. {url['title'][:60]}...")
                print(f"      {url['url']}")
                print(f"      Source: {url['source']}, Score: {url['relevance_score']:.2f}")
        
        # Test topic listing with URL stats
        print("\n📋 Test 3: Listing topics with URL stats")
        
        topics_list = await service.list_topics_with_url_stats("test_user_integration")
        
        if topics_list and 'topics' in topics_list:
            for topic in topics_list['topics']:
                if 'url_stats' in topic:
                    stats = topic['url_stats']
                    print(f"✅ Topic: {topic['topic'][:50]}...")
                    print(f"   URLs: {stats.get('total_urls', 0)}, Status: {stats.get('campaign_status', 'unknown')}")
        
        # Test Stage 1 processing initiation
        print("\n📋 Test 4: Starting Stage 1 processing")
        
        stage1_result = await service.start_stage_1_processing(result['session_id'])
        print(f"✅ Stage 1 status: {stage1_result['status']}")
        print(f"✅ URLs to process: {stage1_result.get('urls_to_process', 0)}")
        
        print("\n🎉 All integration tests completed successfully!")
        
        return result['session_id']
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_google_search_service_directly():
    """Test Google Custom Search service directly"""
    
    print("\n🔍 Testing Google Custom Search Service Directly")
    print("=" * 50)
    
    try:
        from app.services.google_custom_search_service import get_google_search_service
        
        search_service = await get_google_search_service()
        
        # Test search
        search_results = await search_service.search_urls_for_topic(
            search_queries=["artificial intelligence trends 2025"],
            session_id="test_direct_search",
            max_results_per_query=5
        )
        
        print(f"✅ Search completed")
        print(f"✅ Queries processed: {search_results['queries_processed']}")
        print(f"✅ URLs discovered: {search_results['urls_discovered']}")
        print(f"✅ URLs after dedup: {search_results['urls_after_dedup']}")
        
        # Show results
        for i, result in enumerate(search_results['urls'][:3]):
            print(f"\n   {i+1}. {result.title}")
            print(f"      URL: {result.url}")
            print(f"      Domain: {result.domain}")
            print(f"      Score: {result.relevance_score:.2f}")
        
        await search_service.close()
        
    except Exception as e:
        print(f"❌ Direct search test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_url_collection_service():
    """Test URL collection service directly"""
    
    print("\n🔗 Testing URL Collection Service Directly")
    print("=" * 50)
    
    try:
        from app.services.enhanced_url_collection_service import get_url_collection_service, URLCollectionRequest
        
        url_service = await get_url_collection_service()
        
        # Test URL collection
        collection_request = URLCollectionRequest(
            session_id="test_url_collection",
            search_queries=["machine learning trends 2025"],
            initial_urls=["https://www.mckinsey.com/capabilities/quantumblack/our-insights"],
            max_urls_per_query=5,
            metadata={"test": True}
        )
        
        result = await url_service.collect_urls_for_topic(collection_request)
        
        print(f"✅ Collection completed")
        print(f"✅ Status: {result.collection_status}")
        print(f"✅ URLs discovered: {result.urls_discovered}")
        print(f"✅ URLs stored: {result.urls_stored}")
        print(f"✅ Campaign ID: {result.campaign_id}")
        
        # Get collected URLs
        urls_data = await url_service.get_collected_urls("test_url_collection")
        print(f"✅ Retrieved {urls_data['url_count']} URLs from database")
        
        for i, url in enumerate(urls_data.get('urls', [])[:3]):
            print(f"   {i+1}. {url['title'][:50]}...")
            print(f"      {url['url']}")
            print(f"      Source: {url['source']}, Status: {url['status']}")
        
    except Exception as e:
        print(f"❌ URL collection test failed: {e}")
        import traceback
        traceback.print_exc()

def check_environment_variables():
    """Check if required environment variables are set"""
    
    print("\n🔧 Checking Environment Variables")
    print("=" * 50)
    
    required_vars = [
        "GOOGLE_CSE_API_KEY",
        "GOOGLE_CSE_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set (length: {len(value)})")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the tests.")
        return False
    
    print("\n✅ All required environment variables are set!")
    return True

async def main():
    """Main test function"""
    
    print("🚀 Google Custom Search Integration Test Suite")
    print("=" * 60)
    
    # Check environment variables first
    if not check_environment_variables():
        print("\n❌ Cannot run tests due to missing environment variables")
        return
    
    try:
        # Run all tests
        session_id = await test_integrated_topic_creation()
        await test_google_search_service_directly()
        await test_url_collection_service()
        
        print("\n🎉 All tests completed successfully!")
        
        if session_id:
            print(f"\n📊 Test session ID: {session_id}")
            print("You can use this session ID to verify the data in your database.")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
