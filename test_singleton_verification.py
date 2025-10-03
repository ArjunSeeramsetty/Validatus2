#!/usr/bin/env python3
"""
Test script to verify singleton behavior
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_singleton_verification():
    """Test if TopicService singleton is working"""
    print("Testing TopicService singleton verification...")
    
    try:
        from app.services.topic_service import get_topic_service_instance
        
        # Get multiple instances
        instance1 = get_topic_service_instance()
        instance2 = get_topic_service_instance()
        instance3 = get_topic_service_instance()
        
        print(f"Instance 1: {id(instance1)}")
        print(f"Instance 2: {id(instance2)}")
        print(f"Instance 3: {id(instance3)}")
        
        if id(instance1) == id(instance2) == id(instance3):
            print("SUCCESS: Singleton pattern working - all instances are the same")
            
            # Test local storage
            print(f"Instance 1 local storage: {id(instance1._local_storage)}")
            print(f"Instance 2 local storage: {id(instance2._local_storage)}")
            print(f"Instance 3 local storage: {id(instance3._local_storage)}")
            
            if (id(instance1._local_storage) == id(instance2._local_storage) == 
                id(instance3._local_storage)):
                print("SUCCESS: Local storage is shared between instances")
                return True
            else:
                print("FAILED: Local storage is not shared between instances")
                return False
        else:
            print("FAILED: Singleton pattern not working - instances are different")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_singleton_verification()
    if success:
        print("\nSUCCESS: Singleton verification passed!")
    else:
        print("\nFAILED: Singleton verification failed.")
