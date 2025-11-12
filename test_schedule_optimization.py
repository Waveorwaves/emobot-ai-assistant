#!/usr/bin/env python3
"""
Test script for schedule optimization features
Tests the new schedule optimization API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_optimize_schedule():
    """Test POST /api/schedule/optimize"""
    print_section("Testing Schedule Optimization")

    try:
        response = requests.post(f"{BASE_URL}/api/schedule/optimize", timeout=30)
        data = response.json()

        if data.get('success'):
            print("✅ Schedule optimization successful!")
            print(f"\n📊 Summary:")
            summary = data.get('summary', {})
            print(f"  - Total actions: {summary.get('total_actions', 0)}")
            print(f"  - Total approvals needed: {summary.get('total_approvals', 0)}")
            print(f"  - Emails processed: {summary.get('emails_processed', 0)}")
            print(f"  - Events analyzed: {summary.get('events_analyzed', 0)}")
            print(f"  - Tasks reviewed: {summary.get('tasks_reviewed', 0)}")

            print(f"\n🤖 AI Actions ({len(data.get('actions', []))}):")
            for action in data.get('actions', []):
                print(f"  - {action['description']} (count: {action['count']}, status: {action['status']})")

            print(f"\n⚠️  Approvals Needed ({len(data.get('approvals', []))}):")
            for approval in data.get('approvals', []):
                print(f"  - {approval['title']}")
                print(f"    Description: {approval['description']}")
                print(f"    Impact: {approval['impact']}")

            return data
        else:
            print(f"❌ Optimization failed: {data.get('error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_get_actions():
    """Test GET /api/schedule/actions"""
    print_section("Testing Get AI Actions")

    try:
        response = requests.get(f"{BASE_URL}/api/schedule/actions")
        data = response.json()

        if data.get('success'):
            actions = data.get('actions', [])
            print(f"✅ Retrieved {len(actions)} actions")
            for action in actions:
                print(f"  - {action['description']}")
            return actions
        else:
            print(f"❌ Failed to get actions: {data.get('error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_get_approvals():
    """Test GET /api/schedule/approvals"""
    print_section("Testing Get Approval Items")

    try:
        response = requests.get(f"{BASE_URL}/api/schedule/approvals")
        data = response.json()

        if data.get('success'):
            approvals = data.get('approvals', [])
            print(f"✅ Retrieved {len(approvals)} approval items")
            for approval in approvals:
                print(f"  - {approval['title']} (ID: {approval['id']})")
            return approvals
        else:
            print(f"❌ Failed to get approvals: {data.get('error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_approve_action(approval_id):
    """Test POST /api/schedule/approve"""
    print_section(f"Testing Approve Action: {approval_id}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/schedule/approve",
            json={'approval_id': approval_id}
        )
        data = response.json()

        if data.get('success'):
            print(f"✅ Action approved successfully!")
            print(f"   Message: {data.get('message')}")
            print(f"   Remaining approvals: {len(data.get('approvals', []))}")
            return True
        else:
            print(f"❌ Approval failed: {data.get('error')}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_reject_action(approval_id):
    """Test POST /api/schedule/reject"""
    print_section(f"Testing Reject Action: {approval_id}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/schedule/reject",
            json={'approval_id': approval_id}
        )
        data = response.json()

        if data.get('success'):
            print(f"✅ Action rejected successfully!")
            print(f"   Message: {data.get('message')}")
            print(f"   Remaining approvals: {len(data.get('approvals', []))}")
            return True
        else:
            print(f"❌ Rejection failed: {data.get('error')}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_health_check():
    """Test if server is running"""
    print_section("Health Check")

    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        data = response.json()

        if data.get('status') == 'healthy':
            print("✅ Server is healthy and ready")
            return True
        else:
            print("⚠️  Server responded but status is not healthy")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Server not reachable: {e}")
        print("\n💡 Make sure the backend is running:")
        print("   cd emobot && python web_app.py")
        return False

def main():
    print("\n🤖 Emobot Schedule Optimization Test Suite")
    print("=" * 60)

    # Step 1: Health check
    if not test_health_check():
        return

    time.sleep(1)

    # Step 2: Run optimization
    optimization_result = test_optimize_schedule()
    if not optimization_result:
        print("\n⚠️  Optimization returned no data. This might be normal if you have no emails/tasks.")

    time.sleep(1)

    # Step 3: Get actions
    actions = test_get_actions()

    time.sleep(1)

    # Step 4: Get approvals
    approvals = test_get_approvals()

    # Step 5: Test approve/reject if we have approvals
    if approvals and len(approvals) > 0:
        time.sleep(1)

        # Test approving first item
        if len(approvals) >= 1:
            test_approve_action(approvals[0]['id'])
            time.sleep(1)

        # Get updated approvals
        approvals = test_get_approvals()

        # Test rejecting next item if available
        if approvals and len(approvals) >= 1:
            time.sleep(1)
            test_reject_action(approvals[0]['id'])
    else:
        print("\n💡 No approval items to test approve/reject")
        print("   This is normal if optimization didn't find any suggestions")

    # Final summary
    print_section("Test Summary")
    print("✅ All tests completed!")
    print("\n📝 Next steps:")
    print("  1. Open http://localhost:3000 in your browser")
    print("  2. Go to the Dashboard page")
    print("  3. Click 'Optimize Schedule' button")
    print("  4. Check the 'AI Actions Taken' and 'Your Approval Needed' sections")
    print("  5. Try approving or rejecting suggestions")

if __name__ == '__main__':
    main()
