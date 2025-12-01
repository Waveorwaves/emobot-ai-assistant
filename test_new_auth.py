#!/usr/bin/env python3
"""
Test script to verify the new Google auth works in the backup folder
"""

import sys
import os

# Add the emobot directory to the path
emobot_path = os.path.join(os.path.dirname(__file__), 'emobot')
sys.path.insert(0, emobot_path)
os.chdir(emobot_path)

from tools.mcp_server.gmail_auth import GmailAuthManager

def main():
    print("=" * 60)
    print("Testing New Google Authentication in Backup Folder")
    print("=" * 60)
    
    # Check config
    print("\n1. Checking Gmail config...")
    auth_manager = GmailAuthManager()
    
    if not auth_manager.config:
        print("❌ Failed to load Gmail config")
        return False
    
    print(f"✅ Config loaded")
    print(f"   Client ID: {auth_manager.config.get('client_id', 'N/A')[:20]}...")
    print(f"   User Email: {auth_manager.config.get('user_email', 'N/A')}")
    
    # Test authentication
    print("\n2. Testing authentication...")
    if auth_manager.authenticate():
        print("✅ Authentication successful!")
    else:
        print("❌ Authentication failed")
        return False
    
    # Test Gmail service
    print("\n3. Testing Gmail API...")
    gmail_service = auth_manager.get_service()
    if gmail_service:
        try:
            profile = gmail_service.users().getProfile(userId='me').execute()
            print(f"✅ Gmail API working - Connected as: {profile['emailAddress']}")
        except Exception as e:
            print(f"❌ Gmail API test failed: {e}")
            return False
    else:
        print("❌ Failed to get Gmail service")
        return False
    
    # Test People API
    print("\n4. Testing People API (Contacts)...")
    contacts_service = auth_manager.get_contacts_service()
    if contacts_service:
        try:
            results = contacts_service.people().connections().list(
                resourceName='people/me',
                pageSize=3,
                personFields='names,emailAddresses'
            ).execute()
            
            connections = results.get('connections', [])
            print(f"✅ People API working - Found {len(connections)} contacts")
            
            if connections:
                print("\n   Sample contacts:")
                for person in connections[:3]:
                    names = person.get('names', [])
                    if names:
                        print(f"   - {names[0].get('displayName', 'No name')}")
        except Exception as e:
            print(f"❌ People API test failed: {e}")
            print("   Note: Make sure People API is enabled in Google Cloud Console")
            return False
    else:
        print("❌ Failed to get Contacts service")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! The backup folder is ready to use.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
