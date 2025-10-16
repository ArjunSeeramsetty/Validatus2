#!/usr/bin/env python3
"""
Test Data Cleanup Utility
Consolidated from: cleanup_test_data.py
Cleans up test data from the database
"""
import requests
import argparse

BASE_URL = "http://localhost:8000"


def cleanup_test_data(base_url: str = BASE_URL, dry_run: bool = False):
    """Clean up test data"""
    
    print("Cleaning up test data...")
    print("="*40)
    
    # Get all topics
    response = requests.get(f"{base_url}/api/v3/topics/", timeout=10)
    if response.status_code != 200:
        print(f"Failed to get topics: {response.text}")
        return
    
    topics_list = response.json()
    print(f"Found {topics_list['total']} topics")
    
    if dry_run:
        print("\n[DRY RUN MODE - No data will be deleted]")
        for topic in topics_list['topics']:
            print(f"  Would delete: {topic['topic']} ({topic['session_id']})")
        return
    
    # Delete test topics
    deleted_count = 0
    failed_count = 0
    
    for topic in topics_list['topics']:
        session_id = topic['session_id']
        topic_name = topic['topic']
        
        # Only delete test topics
        if any(keyword in topic_name.lower() for keyword in ['test', 'demo', 'integration', 'persistence', 'workflow']):
            print(f"Deleting: {topic_name} ({session_id})")
            
            delete_response = requests.delete(f"{base_url}/api/v3/topics/{session_id}", timeout=10)
            if delete_response.status_code in [200, 204]:
                print(f"  ✓ Deleted {topic_name}")
                deleted_count += 1
            else:
                print(f"  ✗ Failed to delete {topic_name}: {delete_response.text}")
                failed_count += 1
    
    # Verify cleanup
    response = requests.get(f"{base_url}/api/v3/topics/", timeout=10)
    if response.status_code == 200:
        topics_list = response.json()
        print(f"\nCleanup complete:")
        print(f"  Deleted: {deleted_count} topics")
        print(f"  Failed: {failed_count} topics")
        print(f"  Remaining: {topics_list['total']} topics")
    else:
        print(f"Failed to verify cleanup: {response.text}")


def main():
    """Main function with CLI support"""
    parser = argparse.ArgumentParser(description="Clean up test data from Validatus2")
    parser.add_argument("--url", default=BASE_URL, help="Base URL for the API")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    parser.add_argument("--prod", action="store_true", help="Clean production database (use with caution)")
    
    args = parser.parse_args()
    
    if args.prod:
        response = input("⚠️  WARNING: Clean production database? This cannot be undone! Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
        base_url = "https://validatus-backend-ssivkqhvhq-uc.a.run.app"
    else:
        base_url = args.url
    
    cleanup_test_data(base_url=base_url, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

