#!/usr/bin/env python3
"""
Test script to check unread email count
"""

import sys
import os

# Add the emobot directory to the path
emobot_dir = os.path.join(os.path.dirname(__file__), 'emobot')
sys.path.insert(0, emobot_dir)
os.chdir(emobot_dir)

from tools.mcp_server.email import EmailTool

def test_unread_emails():
    """Test unread email fetching"""
    print("="*60)
    print("Testing Unread Email Count")
    print("="*60)
    
    try:
        # Initialize email tool
        print("\n1. Initializing email tool...")
        email_tool = EmailTool()
        print("✅ Email tool initialized")
        
        # Test with unread_only=False (all emails)
        print("\n2. Fetching ALL emails...")
        all_result = email_tool.execute(
            operation='read_inbox',
            max_results=50,
            unread_only=False
        )
        
        if all_result.get('status') == 'success':
            all_emails = all_result.get('emails', [])
            print(f"✅ Total emails in inbox: {len(all_emails)}")
        else:
            print(f"❌ Failed: {all_result.get('error_message')}")
            return False
        
        # Test with unread_only=True (unread emails)
        print("\n3. Fetching UNREAD emails only...")
        unread_result = email_tool.execute(
            operation='read_inbox',
            max_results=50,
            unread_only=True
        )
        
        if unread_result.get('status') == 'success':
            unread_emails = unread_result.get('emails', [])
            print(f"✅ Unread emails: {len(unread_emails)}")
            
            # Show details of unread emails
            if unread_emails:
                print("\nUnread email details:")
                for i, email in enumerate(unread_emails[:5], 1):
                    print(f"  {i}. From: {email.get('from', 'Unknown')}")
                    print(f"     Subject: {email.get('subject', 'No subject')}")
                    print(f"     is_read: {email.get('is_read', 'Unknown')}")
                    print(f"     Labels: {email.get('labels', [])}")
                    print()
        else:
            print(f"❌ Failed: {unread_result.get('error_message')}")
            return False
        
        print("\n" + "="*60)
        print("Summary:")
        print(f"  Total emails: {len(all_emails)}")
        print(f"  Unread emails: {len(unread_emails)}")
        print(f"  Read emails: {len(all_emails) - len(unread_emails)}")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_unread_emails()
    sys.exit(0 if success else 1)
