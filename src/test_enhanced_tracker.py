#!/usr/bin/env python3
"""
Test script for Enhanced John Pye Auction Tracker
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work."""
    print("🧪 Testing imports...")
    
    try:
        from enhanced_tracker import EnhancedAuctionTracker
        print("✅ Enhanced tracker import: OK")
    except Exception as e:
        print(f"❌ Enhanced tracker import failed: {e}")
        return False
    
    try:
        from notification_manager import NotificationManager
        print("✅ Notification manager import: OK")
    except Exception as e:
        print(f"❌ Notification manager import failed: {e}")
        return False
    
    return True

def test_notification_manager():
    """Test SMS notification capabilities."""
    print("\n📱 Testing SMS notifications...")
    
    try:
        from notification_manager import NotificationManager
        nm = NotificationManager()
        
        if nm.twilio_client:
            print("✅ Twilio client initialized")
            
            # Test SMS notification
            print("📤 Sending test SMS...")
            success = nm._send_sms("Test", "Enhanced Auction Tracker Test SMS")
            if success:
                print("✅ Test SMS sent successfully!")
            else:
                print("⚠️  Test SMS failed - check credentials")
        else:
            print("⚠️  Twilio client not initialized - check credentials in .env")
            
    except Exception as e:
        print(f"❌ SMS test failed: {e}")

def test_tracker_creation():
    """Test that tracker can be created."""
    print("\n🚀 Testing tracker creation...")
    
    try:
        from enhanced_tracker import EnhancedAuctionTracker
        tracker = EnhancedAuctionTracker()
        print("✅ Enhanced tracker created successfully")
        
        # Test status method
        status = tracker.get_status()
        print(f"✅ Status method works: {status['is_running']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tracker creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🎯 ENHANCED JOHN PYE AUCTION TRACKER - TEST SUITE")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    test_notification_manager()  # This doesn't return pass/fail
    
    if test_tracker_creation():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ ALL CORE TESTS PASSED!")
        print("\n🚀 Ready to use! Instructions:")
        print("1. Visit: http://localhost:8080")
        print("2. Click 'Start Full Tracker'")
        print("3. You'll receive SMS notifications when started/stopped")
        print("4. Active bids and watchlist will appear in the dashboard")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)