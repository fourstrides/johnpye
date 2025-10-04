#!/usr/bin/env python3
"""
Test script for SMS notifications.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from notification_manager import NotificationManager
from auction_item import AuctionItem

def test_sms_setup():
    """Test SMS notification setup."""
    print("📱 TESTING SMS NOTIFICATIONS")
    print("=" * 40)
    
    # Initialize notification manager
    notif_manager = NotificationManager()
    
    # Check if SMS is configured
    if not notif_manager.twilio_client:
        print("❌ SMS notifications not configured")
        print("\\nTo set up SMS notifications:")
        print("1. Run: python setup_twilio.py")
        print("2. Follow the instructions to get Twilio credentials")
        print("3. Update your .env file with the credentials")
        print("4. Run this test again")
        return False
    
    print("✅ Twilio client initialized successfully")
    print(f"📞 Twilio phone number: {notif_manager.twilio_phone}")
    print(f"📱 Your phone number: {notif_manager.my_phone}")
    
    # Send test SMS
    print("\\n📤 Sending test SMS...")
    
    try:
        test_item = AuctionItem(
            title="Test Auction Item - SMS Working!",
            lot_number="TEST123",
            current_bid="£50.00",
            end_time="2025-01-15 18:00:00",
            url="https://www.johnpyeauctions.co.uk/test"
        )
        
        # Test regular notification
        notif_manager.notify_monitoring_started()
        print("✅ Test notification sent!")
        
        # Test outbidded notification
        print("\\n📤 Sending outbidded test SMS...")
        notif_manager.notify_outbidded(test_item, 55.00, 50.00)
        print("✅ Outbidded test notification sent!")
        
        print("\\n🎉 SMS SETUP SUCCESSFUL!")
        print("Check your phone for the test messages.")
        
        return True
        
    except Exception as e:
        print(f"❌ SMS test failed: {e}")
        print("\\nCheck your Twilio credentials in the .env file")
        return False

if __name__ == "__main__":
    success = test_sms_setup()
    
    if success:
        print("\\n✅ SMS notifications are ready!")
        print("You'll now receive SMS alerts when you're outbidded.")
    else:
        print("\\n❌ SMS setup needs attention.")
        print("Run 'python setup_twilio.py' for setup instructions.")