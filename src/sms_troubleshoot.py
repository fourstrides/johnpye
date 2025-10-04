#!/usr/bin/env python3
"""
SMS Troubleshooting - Send very simple test messages to help diagnose delivery issues
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

def load_config():
    """Load configuration from .env file."""
    env_paths = ['.env', '../.env', os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print(f"✅ Loading config from: {env_path}")
            load_dotenv(env_path)
            return True
    
    print("❌ No .env file found")
    return False

def send_simple_sms():
    """Send a very simple SMS without emojis or special characters."""
    
    print("📱 SIMPLE SMS TROUBLESHOOTING TEST")
    print("=" * 50)
    
    # Load configuration
    if not load_config():
        return False
    
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    my_phone = os.getenv('MY_PHONE_NUMBER')
    
    if not all([twilio_sid, twilio_token, twilio_phone, my_phone]):
        print("❌ Missing Twilio credentials")
        return False
    
    print(f"📱 To: {my_phone}")
    print(f"📞 From: {twilio_phone}")
    print()
    
    # Very simple message without emojis
    message = f"Test SMS {datetime.now().strftime('%H:%M:%S')} - John Pye Tracker"
    
    print(f"📝 Simple message: {message}")
    print()
    
    try:
        from twilio.rest import Client
        
        client = Client(twilio_sid, twilio_token)
        
        print("📡 Sending simple SMS...")
        sms = client.messages.create(
            body=message,
            from_=twilio_phone,
            to=my_phone
        )
        
        print(f"✅ SMS SENT!")
        print(f"📧 Message SID: {sms.sid}")
        print(f"📱 Status: {sms.status}")
        
        return sms.sid
        
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False

def send_emoji_sms():
    """Send a message with emojis to test if that's the issue."""
    
    print("\n" + "=" * 50)
    print("📱 EMOJI SMS TEST")
    print("=" * 50)
    
    if not load_config():
        return False
    
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    my_phone = os.getenv('MY_PHONE_NUMBER')
    
    # Message with emojis
    message = f"🎯 Emoji test {datetime.now().strftime('%H:%M:%S')} - John Pye 📱✅"
    
    print(f"📝 Emoji message: {message}")
    print()
    
    try:
        from twilio.rest import Client
        
        client = Client(twilio_sid, twilio_token)
        
        print("📡 Sending emoji SMS...")
        sms = client.messages.create(
            body=message,
            from_=twilio_phone,
            to=my_phone
        )
        
        print(f"✅ EMOJI SMS SENT!")
        print(f"📧 Message SID: {sms.sid}")
        
        return sms.sid
        
    except Exception as e:
        print(f"❌ Emoji SMS failed: {e}")
        return False

def send_url_sms():
    """Send a message with a URL to test if URLs are being blocked."""
    
    print("\n" + "=" * 50)
    print("🔗 URL SMS TEST")
    print("=" * 50)
    
    if not load_config():
        return False
    
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    my_phone = os.getenv('MY_PHONE_NUMBER')
    
    # Message with URL
    message = f"URL test {datetime.now().strftime('%H:%M:%S')} - Dashboard: http://localhost:8081"
    
    print(f"📝 URL message: {message}")
    print()
    
    try:
        from twilio.rest import Client
        
        client = Client(twilio_sid, twilio_token)
        
        print("📡 Sending URL SMS...")
        sms = client.messages.create(
            body=message,
            from_=twilio_phone,
            to=my_phone
        )
        
        print(f"✅ URL SMS SENT!")
        print(f"📧 Message SID: {sms.sid}")
        
        return sms.sid
        
    except Exception as e:
        print(f"❌ URL SMS failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 SMS TROUBLESHOOTING TESTS")
    print("=" * 50)
    print()
    print("This will send 3 different types of test messages:")
    print("1. Simple text (no emojis, no URLs)")
    print("2. Text with emojis")  
    print("3. Text with URL")
    print()
    
    try:
        response = input("❓ Continue with tests? (y/n): ").lower().strip()
        if response not in ['y', 'yes']:
            print("👋 Cancelled by user")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
        sys.exit(0)
    
    sids = []
    
    # Test 1: Simple SMS
    print("🧪 TEST 1: Simple text message")
    sid1 = send_simple_sms()
    if sid1:
        sids.append(sid1)
    
    # Test 2: Emoji SMS  
    print("\n🧪 TEST 2: Message with emojis")
    sid2 = send_emoji_sms()
    if sid2:
        sids.append(sid2)
    
    # Test 3: URL SMS
    print("\n🧪 TEST 3: Message with URL")
    sid3 = send_url_sms()
    if sid3:
        sids.append(sid3)
    
    print("\n" + "=" * 50)
    print("✅ TROUBLESHOOTING TESTS COMPLETE")
    print("=" * 50)
    print()
    print(f"📱 Sent {len(sids)} test messages")
    print("📞 Check your phone now for any of these messages:")
    print()
    for i, sid in enumerate(sids, 1):
        print(f"   {i}. {sid}")
    print()
    print("🔧 TROUBLESHOOTING STEPS:")
    print("1. Check phone notifications/alerts")
    print("2. Check SMS app inbox")
    print("3. Check spam/junk SMS folder")
    print("4. Check if phone has signal/connectivity")
    print("5. Try restarting your phone")
    print("6. Check if SMS from unknown numbers is blocked")
    print("7. Check carrier SMS filtering settings")
    print()
    print("📋 If none arrive, the issue is likely:")
    print("   • Carrier blocking messages")
    print("   • Phone number incorrect") 
    print("   • Phone settings blocking SMS")
    print("   • Regional SMS restrictions")