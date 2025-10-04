#!/usr/bin/env python3
"""
Check SMS delivery status for sent messages
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

def check_message_status(message_sid):
    """Check the delivery status of a specific message."""
    
    # Load configuration
    if not load_config():
        return False
    
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not twilio_sid or not twilio_token:
        print("❌ Missing Twilio credentials")
        return False
    
    try:
        from twilio.rest import Client
        
        client = Client(twilio_sid, twilio_token)
        
        print(f"🔍 Checking message: {message_sid}")
        print("-" * 50)
        
        message = client.messages(message_sid).fetch()
        
        print(f"📱 To: {message.to}")
        print(f"📞 From: {message.from_}")
        print(f"📊 Status: {message.status}")
        print(f"📧 Error Code: {message.error_code or 'None'}")
        print(f"❌ Error Message: {message.error_message or 'None'}")
        print(f"💰 Price: {message.price or 'Unknown'} {message.price_unit or ''}")
        print(f"🕐 Date Created: {message.date_created}")
        print(f"🕐 Date Updated: {message.date_updated}")
        print(f"🕐 Date Sent: {message.date_sent or 'Not sent yet'}")
        print(f"🔄 Direction: {message.direction}")
        
        # Show message body (truncated)
        if message.body:
            body_preview = message.body[:100] + "..." if len(message.body) > 100 else message.body
            print(f"📝 Message: {body_preview}")
        
        print()
        
        # Status explanation
        status_explanations = {
            'queued': '📤 Message is queued for delivery',
            'sending': '📡 Message is being sent',
            'sent': '✅ Message was sent to carrier',
            'delivered': '🎉 Message was delivered to phone',
            'undelivered': '❌ Message failed to deliver',
            'failed': '💥 Message failed completely',
            'receiving': '📨 Receiving message',
            'received': '📧 Message received'
        }
        
        explanation = status_explanations.get(message.status.lower(), f"❓ Unknown status: {message.status}")
        print(f"📋 Status Meaning: {explanation}")
        
        # Common issues and solutions
        if message.status.lower() in ['failed', 'undelivered']:
            print("\n🚨 DELIVERY FAILED:")
            if message.error_code:
                print(f"   Error Code: {message.error_code}")
            if message.error_message:
                print(f"   Error: {message.error_message}")
            
            print("\n🔧 Possible Solutions:")
            print("   • Check if the phone number is correct")
            print("   • Verify the phone can receive SMS")
            print("   • Check if phone is turned on and has signal")
            print("   • Some carriers block messages with URLs")
            print("   • International SMS might have restrictions")
        
        elif message.status.lower() == 'sent':
            print("\n⚠️  MESSAGE SENT BUT NOT DELIVERED YET:")
            print("   • Message was sent to carrier successfully")
            print("   • Delivery can take a few minutes")
            print("   • Check phone for signal/connectivity")
            print("   • Some carriers don't provide delivery receipts")
        
        elif message.status.lower() == 'delivered':
            print("\n✅ MESSAGE DELIVERED SUCCESSFULLY!")
            print("   • Check phone notifications")
            print("   • Check spam/junk folders")
            print("   • Message might be in a different conversation")
        
        return True
        
    except ImportError:
        print("❌ Twilio library not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking message: {e}")
        return False

def check_recent_messages():
    """Check recent messages sent from this account."""
    
    print("🔍 CHECKING RECENT SMS MESSAGES")
    print("=" * 50)
    
    # Load configuration
    if not load_config():
        return False
    
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not twilio_sid or not twilio_token:
        print("❌ Missing Twilio credentials")
        return False
    
    try:
        from twilio.rest import Client
        
        client = Client(twilio_sid, twilio_token)
        
        print("📱 Recent messages (last 10):")
        print("-" * 50)
        
        messages = client.messages.list(limit=10)
        
        for i, message in enumerate(messages, 1):
            print(f"{i}. SID: {message.sid}")
            print(f"   To: {message.to}")
            print(f"   Status: {message.status}")
            print(f"   Created: {message.date_created}")
            if message.error_code:
                print(f"   Error: {message.error_code} - {message.error_message}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")
        return False

if __name__ == "__main__":
    print("📱 SMS DELIVERY STATUS CHECKER")
    print("=" * 50)
    print()
    
    # Check the specific message SIDs from our recent test
    recent_sids = [
        "SM3bf57c170a44721bbcb97c4dc4162836",  # Status notification
        "SM5963151bc938a863b4b93b93b7cf3403"   # Bid alert example
    ]
    
    print("🔍 Checking our recent test messages...")
    print()
    
    for sid in recent_sids:
        success = check_message_status(sid)
        if success:
            print("\n" + "=" * 50)
        print()
    
    print("\n🔍 Checking all recent messages...")
    print()
    check_recent_messages()