#!/usr/bin/env python3
"""
Simple SMS test to check Twilio configuration
"""

import os
import sys
from dotenv import load_dotenv

def test_sms_simple():
    """Test SMS setup by checking environment variables first."""
    
    print("🧪 SIMPLE SMS TEST")
    print("=" * 40)
    
    # Load environment variables from .env file
    env_path = '../.env'
    if os.path.exists(env_path):
        print(f"✅ Found .env file at: {env_path}")
        load_dotenv(env_path)
    else:
        print(f"❌ No .env file found at: {env_path}")
        return False
    
    # Check environment variables
    print("\n🔍 Checking environment variables:")
    
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN') 
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    my_phone = os.getenv('MY_PHONE_NUMBER')
    
    if not twilio_sid or twilio_sid == 'your_twilio_account_sid_here':
        print("❌ TWILIO_ACCOUNT_SID not configured")
        return False
    else:
        print(f"✅ TWILIO_ACCOUNT_SID: {twilio_sid[:8]}...")
    
    if not twilio_token or twilio_token == 'your_twilio_auth_token_here':
        print("❌ TWILIO_AUTH_TOKEN not configured")
        return False
    else:
        print(f"✅ TWILIO_AUTH_TOKEN: {twilio_token[:8]}...")
    
    if not twilio_phone or twilio_phone == '+1234567890':
        print("❌ TWILIO_PHONE_NUMBER not configured")
        return False
    else:
        print(f"✅ TWILIO_PHONE_NUMBER: {twilio_phone}")
    
    if not my_phone or my_phone == '+1234567890':
        print("❌ MY_PHONE_NUMBER not configured")
        return False
    else:
        print(f"✅ MY_PHONE_NUMBER: {my_phone}")
    
    print("\n📱 Testing Twilio connection...")
    
    try:
        from twilio.rest import Client
        
        client = Client(twilio_sid, twilio_token)
        
        # Test by sending a message
        message = client.messages.create(
            body="🧪 Test SMS from John Pye Auction Tracker! SMS notifications are working! 🎉",
            from_=twilio_phone,
            to=my_phone
        )
        
        print(f"✅ SMS sent successfully!")
        print(f"📧 Message SID: {message.sid}")
        print(f"📱 Status: {message.status}")
        
        return True
        
    except ImportError:
        print("❌ Twilio library not installed. Install with: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False

if __name__ == "__main__":
    success = test_sms_simple()
    
    if success:
        print(f"\n🎉 SMS TEST SUCCESSFUL!")
        print("📱 Check your phone for the test message!")
        print("🚀 SMS notifications are ready for the auction tracker!")
    else:
        print(f"\n❌ SMS test failed.")
        print("🔧 Run 'python setup_twilio.py' for setup instructions.")