#!/usr/bin/env python3
"""
Helper script to set up Twilio SMS notifications.
"""

def setup_twilio_instructions():
    """Provide instructions for setting up Twilio SMS."""
    print("📱 TWILIO SMS SETUP INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1️⃣ CREATE TWILIO ACCOUNT:")
    print("   • Go to: https://www.twilio.com/try-twilio")
    print("   • Sign up for a free account (you get $15 credit)")
    print("   • Verify your phone number")
    
    print("\n2️⃣ GET YOUR CREDENTIALS:")
    print("   • Go to: https://console.twilio.com/")
    print("   • Find your Account SID and Auth Token on the dashboard")
    print("   • Get a Twilio phone number from the Phone Numbers section")
    
    print("\n3️⃣ UPDATE YOUR .ENV FILE:")
    print("   Edit the .env file in your project root and replace:")
    print("   ")
    print("   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here")
    print("   TWILIO_AUTH_TOKEN=your_twilio_auth_token_here")
    print("   TWILIO_PHONE_NUMBER=+15551234567  # Your Twilio number")
    print("   MY_PHONE_NUMBER=+15559876543      # Your personal number")
    
    print("\n4️⃣ TEST YOUR SETUP:")
    print("   Run: python test_sms.py")
    
    print("\n💰 PRICING INFO:")
    print("   • SMS messages cost ~$0.0075 each")
    print("   • With $15 free credit, you get ~2000 SMS messages")
    print("   • Perfect for auction notifications!")
    
    print("\n🔒 SECURITY TIPS:")
    print("   • Keep your Auth Token secret")
    print("   • Don't commit .env file to git (already in .gitignore)")
    print("   • Use environment variables in production")

if __name__ == "__main__":
    setup_twilio_instructions()