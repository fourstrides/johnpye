#!/usr/bin/env python3
"""
Simple test script to verify WebDriver initialization works.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import JohnPyeAuctionTracker

def test_driver_initialization():
    """Test basic driver setup without attempting login."""
    print("Testing WebDriver initialization...")
    
    tracker = JohnPyeAuctionTracker()
    
    try:
        # Test driver setup
        success = tracker.setup_driver(headless=True)
        if success and tracker.driver:
            print("✅ WebDriver initialized successfully!")
            
            # Test basic navigation
            tracker.driver.get("https://www.google.com")
            title = tracker.driver.title
            print(f"✅ Basic navigation test passed. Page title: {title}")
            
            # Clean up
            tracker.driver.quit()
            print("✅ WebDriver cleanup completed.")
            return True
        else:
            print("❌ WebDriver initialization failed.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        if tracker.driver:
            tracker.driver.quit()
        return False

def test_notification_system():
    """Test the notification system."""
    print("\nTesting notification system...")
    
    tracker = JohnPyeAuctionTracker()
    
    try:
        result = tracker.notification_manager.test_notifications()
        if result:
            print("✅ Notification system test passed!")
        else:
            print("❌ Notification system test failed.")
        return result
    except Exception as e:
        print(f"❌ Notification test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("John Pye Auction Tracker - Component Tests")
    print("=" * 50)
    
    # Test WebDriver
    driver_ok = test_driver_initialization()
    
    # Test notifications
    notif_ok = test_notification_system()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"WebDriver: {'✅ PASS' if driver_ok else '❌ FAIL'}")
    print(f"Notifications: {'✅ PASS' if notif_ok else '❌ FAIL'}")
    
    if driver_ok and notif_ok:
        print("\n🎉 All basic tests passed! The application is ready for testing.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        sys.exit(1)