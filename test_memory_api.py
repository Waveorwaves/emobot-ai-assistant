#!/usr/bin/env python3
"""
Test script for Memory Analysis API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_memory_analyze():
    """Test the memory analyze endpoint"""
    print("=" * 60)
    print("Testing Memory Analysis API")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n1. Checking if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running: {e}")
        print("\n💡 Please start the server first:")
        print("   cd emobot1-backup-before-memory-upgrade-20251113-015517/emobot")
        print("   python web_app.py")
        return False
    
    # Test 2: Call memory analyze endpoint
    print("\n2. Testing memory analysis endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/memory/analyze",
            headers={'Content-Type': 'application/json'},
            timeout=60  # Analysis can take time
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Memory analysis successful!")
                print(f"\n📊 Statistics:")
                stats = data.get('stats', {})
                print(f"   Total Memories: {stats.get('total_memories', 0)}")
                print(f"   Recent Memories: {stats.get('recent_memories', 0)}")
                print(f"   Analysis Date: {stats.get('analysis_date', 'N/A')}")
                
                print(f"\n📝 Analysis Preview:")
                analysis = data.get('analysis', '')
                preview = analysis[:200] + "..." if len(analysis) > 200 else analysis
                print(f"   {preview}")
                
                if data.get('profile_suggestions'):
                    profile = data['profile_suggestions'].get('description', '')
                    print(f"\n👤 Profile Suggestion Preview:")
                    profile_preview = profile[:200] + "..." if len(profile) > 200 else profile
                    print(f"   {profile_preview}")
                
                return True
            else:
                print(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (analysis takes time, this might be normal)")
        print("   Try increasing the timeout or check server logs")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return False

def main():
    print("\n🧪 Memory API Test Suite\n")
    
    success = test_memory_analyze()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
        print("\n✅ Backend memory API is working correctly")
        print("   You can now integrate the frontend")
    else:
        print("❌ Some tests failed")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure the backend server is running")
        print("   2. Check that episodic_memory.json exists in agent_memory/")
        print("   3. Check server logs for errors")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
