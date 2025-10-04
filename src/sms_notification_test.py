#!/usr/bin/env python3
"""
Real SMS Notification Test - Sends practical auction tracker notifications
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

def load_config():
    """Load configuration from .env file."""
    # Try different .env locations
    env_paths = ['.env', '../.env', os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print(f"✅ Loading config from: {env_path}")
            load_dotenv(env_path)
            return True
    
    print("❌ No .env file found. Checked:")
    for path in env_paths:
        print(f"   - {path}")
    return False

def get_auction_status():
    """Get current auction status from data files."""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        data_file = os.path.join(data_dir, 'realtime_status.json')
        
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            active_bids = data.get('active_bids', [])
            watchlist = data.get('watchlist_items', [])
            timestamp = data.get('timestamp', 'Unknown')
            
            winning = sum(1 for bid in active_bids if bid.get('status', '').upper() == 'WINNING')
            outbid = sum(1 for bid in active_bids if bid.get('status', '').upper() == 'OUTBID')
            
            return {
                'active_bids': len(active_bids),
                'winning': winning,
                'outbid': outbid,
                'watchlist': len(watchlist),
                'last_update': timestamp,
                'has_data': True
            }
    except Exception as e:
        print(f"⚠️  Could not load auction data: {e}")
    
    return {'has_data': False}

def send_notification_sms():
    """Send a real notification SMS about auction tracker status."""
    
    print("📱 REAL SMS NOTIFICATION TEST")
    print("=" * 50)
    
    # Load configuration
    if not load_config():
        return False
    
    # Get required credentials
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    my_phone = os.getenv('MY_PHONE_NUMBER')
    
    # Validate credentials
    missing = []
    if not twilio_sid or twilio_sid == 'your_twilio_account_sid_here':
        missing.append('TWILIO_ACCOUNT_SID')
    if not twilio_token or twilio_token == 'your_twilio_auth_token_here':
        missing.append('TWILIO_AUTH_TOKEN')
    if not twilio_phone or twilio_phone == '+1234567890':
        missing.append('TWILIO_PHONE_NUMBER')
    if not my_phone or my_phone == '+1234567890':
        missing.append('MY_PHONE_NUMBER')
    
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        print("🔧 Run 'make sms-setup' to configure credentials")
        return False
    
    print(f"📋 From: {twilio_phone}")
    print(f"📱 To: {my_phone}")
    print()
    
    # Get auction status
    print("🔍 Checking auction tracker status...")
    status = get_auction_status()
    
    # Create message based on current status
    if status['has_data']:
        message = f"""🎯 John Pye Auction Tracker Alert!

📊 Current Status:
• Active Bids: {status['active_bids']}
• Winning: {status['winning']} 🏆
• Outbid: {status['outbid']} ⚠️
• Watchlist: {status['watchlist']} 👁️

🕐 Last Update: {status['last_update'][:19] if status['last_update'] != 'Unknown' else 'Never'}

🚀 System: ONLINE & MONITORING
Dashboard: http://localhost:8081"""
    else:
        message = f"""🎯 John Pye Auction Tracker Alert!

🚀 System Status: ONLINE
📊 Dashboard: http://localhost:8081
🔧 Ready to monitor your bids!

⏰ Test sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a test notification to confirm SMS alerts are working properly. 📱✅"""
    
    print("📝 Message to send:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    print()
    
    # Send SMS
    try:
        from twilio.rest import Client
        
        print("📡 Sending SMS notification...")
        client = Client(twilio_sid, twilio_token)
        
        sms = client.messages.create(
            body=message,
            from_=twilio_phone,
            to=my_phone
        )
        
        print(f"✅ SMS SENT SUCCESSFULLY!")
        print(f"📧 Message SID: {sms.sid}")
        print(f"📱 Status: {sms.status}")
        print(f"🕐 Created: {sms.date_created}")
        
        return True
        
    except ImportError:
        print("❌ Twilio library not installed")
        print("🔧 Install with: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False

def send_bid_alert_example():
    """Send an example bid alert notification."""
    
    print("\n" + "=" * 50)
    print("📱 EXAMPLE BID ALERT NOTIFICATION")
    print("=" * 50)
    
    # Load configuration
    if not load_config():
        return False
    
    # Get credentials
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    my_phone = os.getenv('MY_PHONE_NUMBER')
    
    if not all([twilio_sid, twilio_token, twilio_phone, my_phone]):
        print("❌ Missing credentials")
        return False
    
    # Example bid alert message
    message = f"""🚨 BID ALERT - OUTBID! 🚨

📦 Item: "Vintage Tools Collection"
🏷️  Lot: #A12345
💰 Your Bid: £125.00
💸 Current Bid: £135.00
⏰ Ends: 15 minutes

🎯 Action Needed:
Visit: http://localhost:8081
Or go to John Pye directly

⏰ Alert: {datetime.now().strftime('%H:%M:%S')}"""
    
    print("📝 Example bid alert message:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    print()
    
    try:
        from twilio.rest import Client
        
        print("📡 Sending example bid alert...")
        client = Client(twilio_sid, twilio_token)
        
        sms = client.messages.create(
            body=message,
            from_=twilio_phone,
            to=my_phone
        )
        
        print(f"✅ EXAMPLE ALERT SENT!")
        print(f"📧 Message SID: {sms.sid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alert failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting SMS Notification Tests...")
    print()
    
    # Test 1: Status notification
    success1 = send_notification_sms()
    
    if success1:
        print("\n🎉 Status notification sent successfully!")
        
        # Ask if user wants to send example bid alert
        try:
            response = input("\n❓ Send example bid alert too? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                success2 = send_bid_alert_example()
                if success2:
                    print("\n🎉 Example bid alert sent!")
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
    
    print("\n" + "=" * 50)
    if success1:
        print("✅ SMS NOTIFICATION TEST COMPLETE")
        print("📱 Check your phone for the messages!")
        print("🚀 SMS alerts are ready for live auction monitoring!")
    else:
        print("❌ SMS test failed")
        print("🔧 Run 'make sms-setup' or 'make sms-diagnose' for help")
    print("=" * 50)