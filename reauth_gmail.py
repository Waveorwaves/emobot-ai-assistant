#!/usr/bin/env python3
"""
Simple script to re-authenticate Gmail with People API
"""

import sys
import os

# Add the emobot directory to the path
emobot_path = os.path.join(os.path.dirname(__file__), 'emobot')
sys.path.insert(0, emobot_path)
os.chdir(emobot_path)

from tools.mcp_server.gmail_auth import GmailAuthManager

def main():
    print("🔐 Starting Gmail re-authentication with People API...")
    
    # Delete existing token
    token_files = ['gmail_token.json', 'gmail_credentials.json']
    for token_file in token_files:
        if os.path.exists(token_file):
            os.remove(token_file)
            print(f"✅ Deleted {token_file}")
    
    try:
        # Initialize auth manager
        auth_manager = GmailAuthManager()
        
        # Force authentication
        print("🔄 Starting OAuth flow...")
        if auth_manager.authenticate():
            print("✅ Gmail authentication successful!")
            
            # Test Gmail service
            gmail_service = auth_manager.get_service()
            if gmail_service:
                print("✅ Gmail API connection verified")
            
            # Test People API service
            contacts_service = auth_manager.get_contacts_service()
            if contacts_service:
                print("✅ People API connection verified")
                
                # Test actual API call
                try:
                    results = contacts_service.people().connections().list(
                        resourceName='people/me',
                        pageSize=5,
                        personFields='names'
                    ).execute()
                    
                    connections = results.get('connections', [])
                    print(f"✅ Successfully retrieved {len(connections)} contacts")
                    print("🎉 People API is working correctly!")
                    return True
                    
                except Exception as e:
                    print(f"❌ People API test failed: {str(e)}")
                    return False
            else:
                print("❌ People API connection failed")
                return False
        else:
            print("❌ Gmail authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Authentication complete! You can now use contact features.")
    else:
        print("\n🔧 Authentication failed. Please check your Google Cloud Console settings.")
