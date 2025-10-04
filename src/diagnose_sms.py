#!/usr/bin/env python3
"""
Diagnostic test for Twilio SMS issues
"""

import os
import sys
from dotenv import load_dotenv

def diagnose_sms_issue():
    """Diagnose potential SMS configuration issues."""
    
    print("🔍 TWILIO DIAGNOSTIC TEST")
    print("=" * 40)
    
    # Load environment variables
    env_path = '../.env'
    load_dotenv(env_path)
    
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN') 
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    my_phone = os.getenv('MY_PHONE_NUMBER')
    
    print("📋 Configuration Status:")
    print(f"   Account SID: {twilio_sid[:8]}...{twilio_sid[-4:]}")
    print(f"   Auth Token: {twilio_token[:8]}...{twilio_token[-4:]}")
    print(f"   Twilio Phone: {twilio_phone}")
    print(f"   Your Phone: {my_phone}")
    
    print("\n🧪 Testing Twilio API Connection...")
    
    try:
        from twilio.rest import Client
        
        client = Client(twilio_sid, twilio_token)
        
        # Test 1: Check account status
        print("\n1️⃣ Checking account status...")
        try:
            account = client.api.account.fetch()
            print(f"   ✅ Account Status: {account.status}")
            print(f"   📞 Account Type: {account.type}")
            
            if account.status != 'active':
                print(f"   ⚠️  Account is not active! Status: {account.status}")
                return False
                
        except Exception as e:
            print(f"   ❌ Account check failed: {e}")
            print("   💡 This usually means invalid Account SID or Auth Token")
            return False
        
        # Test 2: Check phone number
        print("\n2️⃣ Checking Twilio phone number...")
        try:
            # Get incoming phone numbers
            phone_numbers = client.incoming_phone_numbers.list()
            
            if not phone_numbers:
                print("   ❌ No phone numbers found on your Twilio account!")
                print("   💡 You need to purchase a phone number from Twilio Console")
                return False
            
            twilio_number_found = False
            for number in phone_numbers:
                print(f"   📞 Available: {number.phone_number}")
                if number.phone_number == twilio_phone:
                    twilio_number_found = True
            
            if not twilio_number_found:
                print(f"   ❌ Configured number {twilio_phone} not found in your account!")
                print("   💡 Update TWILIO_PHONE_NUMBER in .env file")
                return False
            else:
                print(f"   ✅ Phone number {twilio_phone} verified")
                
        except Exception as e:
            print(f"   ❌ Phone number check failed: {e}")
            return False
        
        # Test 3: Check trial account limitations
        print("\n3️⃣ Checking trial account status...")
        try:
            balance = client.balance.fetch()
            print(f"   💰 Account Balance: {balance.balance} {balance.currency}")
            
            if balance.balance == '0.00' or balance.balance == '0':
                print("   ⚠️  Zero balance - may be a trial account")
                print("   💡 Trial accounts can only send SMS to verified numbers")
                
        except Exception as e:
            print(f"   ⚠️  Could not check balance: {e}")
        
        # Test 4: Try sending SMS with better error handling
        print("\n4️⃣ Attempting to send test SMS...")
        try:
            message = client.messages.create(
                body="🧪 TEST: John Pye Auction Tracker SMS is working!",
                from_=twilio_phone,
                to=my_phone
            )
            
            print(f"   ✅ SMS sent successfully!")
            print(f"   📧 Message SID: {message.sid}")
            print(f"   📱 Status: {message.status}")
            print(f"   💰 Price: {message.price} {message.price_unit}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ SMS failed: {e}")
            
            # Parse specific error messages
            error_str = str(e)
            if "20003" in error_str:
                print("   🔍 Error 20003: Authentication failed")
                print("   💡 Solutions:")
                print("      - Check your Account SID and Auth Token are correct")
                print("      - Make sure you're using the correct Twilio account")
                print("      - Try regenerating your Auth Token in Twilio Console")
                
            elif "21211" in error_str:
                print("   🔍 Error 21211: Invalid phone number")
                print("   💡 Solutions:")
                print("      - Check phone numbers are in E.164 format (+country code)")
                print("      - Make sure both numbers are verified if using trial account")
                
            elif "21608" in error_str or "21614" in error_str:
                print("   🔍 Trial account restriction")
                print("   💡 Solutions:")
                print("      - Verify your destination phone number in Twilio Console")
                print("      - Or upgrade to a paid account")
            
            return False
            
    except ImportError:
        print("❌ Twilio library not installed")
        print("💡 Install with: pip install twilio")
        return False

def show_next_steps(success):
    """Show next steps based on test results."""
    
    if success:
        print(f"\n🎉 SMS DIAGNOSTICS PASSED!")
        print("✅ SMS notifications are working properly!")
        print("🚀 You can now use the auction tracker with SMS alerts!")
        
    else:
        print(f"\n🔧 NEXT STEPS TO FIX SMS:")
        print("1️⃣ Visit https://console.twilio.com/")
        print("2️⃣ Check your Account SID and Auth Token")
        print("3️⃣ Make sure you have a phone number purchased")
        print("4️⃣ If using trial account, verify your destination phone number")
        print("5️⃣ Update your .env file with correct values")
        print("6️⃣ Run this diagnostic again")

if __name__ == "__main__":
    success = diagnose_sms_issue()
    show_next_steps(success)