#!/usr/bin/env python3
"""
Add a test contact to Google Contacts
"""

import sys
import os

# Add the emobot directory to the path
emobot_path = os.path.join(os.path.dirname(__file__), 'emobot')
sys.path.insert(0, emobot_path)
os.chdir(emobot_path)

from tools.mcp_server.email import EmailTool

def add_test_contact():
    """Add a test contact"""
    print("➕ Adding test contact...")
    
    email_tool = EmailTool()
    
    # Add Jason Huang as a test contact
    result = email_tool._add_contact(
        contact_name="Jason Huang",
        contact_email="jason.huang@example.com",
        contact_phone="+1234567890"
    )
    
    print(f"Add contact result: {result}")
    
    if result.get('status') == 'success':
        print("✅ Test contact added successfully!")
        
        # Now test searching for it
        print("\n🔍 Testing search for Jason Huang...")
        search_result = email_tool._search_contacts("Jason Huang")
        print(f"Search result: {search_result}")
        
        # Test listing all contacts
        print("\n📋 Testing list all contacts...")
        list_result = email_tool._get_contacts()
        print(f"List result: {list_result}")
        
    else:
        print("❌ Failed to add test contact")

if __name__ == "__main__":
    add_test_contact()
