#!/usr/bin/env python3
"""
Test script to check email MCP server connection
"""

import sys
import os

# Add the emobot directory to the path
emobot_dir = os.path.join(os.path.dirname(__file__), 'emobot')
sys.path.insert(0, emobot_dir)

# Change to emobot directory so relative paths work
os.chdir(emobot_dir)

from tools.mcp_server.email import EmailTool
import json

def test_email_tool():
    """Test the email tool directly"""
    print("="*60)
    print("Testing Email Tool Connection")
    print("="*60)
    
    try:
        # Initialize email tool
        print("\n1. Initializing email tool...")
        email_tool = EmailTool()
        print("✅ Email tool initialized successfully")
        
        # Test reading inbox
        print("\n2. Testing inbox read...")
        result = email_tool.execute(operation='read_inbox', max_results=5)
        
        print(f"\nResult status: {result.get('status')}")
        
        if result.get('status') == 'success':
            emails = result.get('emails', [])
            print(f"✅ Successfully fetched {len(emails)} emails")
            
            if emails:
                print("\nFirst email preview:")
                first_email = emails[0]
                print(f"  From: {first_email.get('from', 'N/A')}")
                print(f"  Subject: {first_email.get('subject', 'N/A')}")
                print(f"  Date: {first_email.get('date', 'N/A')}")
                print(f"  Snippet: {first_email.get('snippet', 'N/A')[:100]}...")
        else:
            error_msg = result.get('error_message', 'Unknown error')
            print(f"❌ Failed to fetch emails: {error_msg}")
            
            if 'Gmail' in error_msg or 'auth' in error_msg.lower():
                print("\n💡 Troubleshooting:")
                print("  1. Make sure Gmail API is enabled in Google Cloud Console")
                print("  2. Check if credentials.json exists in emobot/tools/mcp_server/")
                print("  3. Run the authentication flow if token.json doesn't exist")
                print("  4. Check if the Gmail API scope is correct")
        
        print("\n" + "="*60)
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Troubleshooting:")
        print("  1. Check if Gmail API credentials are configured")
        print("  2. Make sure all dependencies are installed")
        print("  3. Check the error message above for specific issues")
        return False

if __name__ == '__main__':
    success = test_email_tool()
    sys.exit(0 if success else 1)
