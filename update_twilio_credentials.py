#!/usr/bin/env python3
"""
Update Twilio credentials in .env file
"""

import os
import sys

def update_twilio_credentials():
    """Interactive script to update Twilio credentials."""
    
    print("🔧 UPDATE TWILIO CREDENTIALS")
    print("=" * 50)
    
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"❌ .env file not found at: {env_file}")
        return False
    
    print("📋 Current credentials in .env file:")
    print("-" * 30)
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Show current Twilio settings
    for line in lines:
        if line.startswith('TWILIO_') or line.startswith('MY_PHONE'):
            print(f"   {line.strip()}")
    
    print("\n🆕 Enter your CORRECT Twilio credentials:")
    print("   (Get these from https://console.twilio.com/)")
    print("-" * 50)
    
    # Get new credentials
    new_account_sid = input("📋 Account SID (starts with AC): ").strip()
    new_auth_token = input("🔐 Auth Token (32 character string): ").strip()
    new_twilio_phone = input("📞 Twilio Phone Number (+44...): ").strip()
    new_my_phone = input("📱 Your Phone Number (+44...): ").strip()
    
    # Validate inputs
    if not new_account_sid.startswith('AC') or len(new_account_sid) != 34:
        print("❌ Account SID should start with 'AC' and be 34 characters long")
        return False
    
    if len(new_auth_token) != 32:
        print("❌ Auth Token should be 32 characters long")
        return False
    
    if not new_twilio_phone.startswith('+'):
        print("❌ Phone numbers should start with '+' and include country code")
        return False
        
    if not new_my_phone.startswith('+'):
        print("❌ Phone numbers should start with '+' and include country code")
        return False
    
    print(f"\n✅ Credentials look valid!")
    print(f"   Account SID: {new_account_sid}")
    print(f"   Auth Token: {new_auth_token[:8]}...{new_auth_token[-4:]}")
    print(f"   Twilio Phone: {new_twilio_phone}")
    print(f"   Your Phone: {new_my_phone}")
    
    confirm = input(f"\n❓ Update .env file with these credentials? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Update cancelled")
        return False
    
    # Update the .env file
    updated_lines = []
    credentials_updated = set()
    
    for line in lines:
        if line.startswith('TWILIO_ACCOUNT_SID='):
            updated_lines.append(f'TWILIO_ACCOUNT_SID={new_account_sid}\n')
            credentials_updated.add('SID')
        elif line.startswith('TWILIO_AUTH_TOKEN='):
            updated_lines.append(f'TWILIO_AUTH_TOKEN={new_auth_token}\n')
            credentials_updated.add('TOKEN')
        elif line.startswith('TWILIO_PHONE_NUMBER='):
            updated_lines.append(f'TWILIO_PHONE_NUMBER={new_twilio_phone}\n')
            credentials_updated.add('TWILIO_PHONE')
        elif line.startswith('MY_PHONE_NUMBER='):
            updated_lines.append(f'MY_PHONE_NUMBER={new_my_phone}\n')
            credentials_updated.add('MY_PHONE')
        else:
            updated_lines.append(line)
    
    # Add any missing credentials
    if 'SID' not in credentials_updated:
        updated_lines.append(f'TWILIO_ACCOUNT_SID={new_account_sid}\n')
    if 'TOKEN' not in credentials_updated:
        updated_lines.append(f'TWILIO_AUTH_TOKEN={new_auth_token}\n')
    if 'TWILIO_PHONE' not in credentials_updated:
        updated_lines.append(f'TWILIO_PHONE_NUMBER={new_twilio_phone}\n')
    if 'MY_PHONE' not in credentials_updated:
        updated_lines.append(f'MY_PHONE_NUMBER={new_my_phone}\n')
    
    # Create backup
    backup_file = f"{env_file}.backup"
    with open(backup_file, 'w') as f:
        f.writelines(lines)
    print(f"📁 Backup created: {backup_file}")
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"✅ Credentials updated successfully!")
    
    # Show updated file
    print(f"\n📋 Updated .env file:")
    print("-" * 30)
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith('TWILIO_') or line.startswith('MY_PHONE'):
                if 'AUTH_TOKEN' in line:
                    # Hide most of the auth token
                    parts = line.split('=')
                    if len(parts) == 2:
                        token = parts[1].strip()
                        print(f"   TWILIO_AUTH_TOKEN={token[:8]}...{token[-4:]}")
                else:
                    print(f"   {line.strip()}")
    
    return True

def show_next_steps():
    """Show what to do after updating credentials."""
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Test the new credentials:")
    print("   python3 src/twilio_advanced_test.py")
    print("")
    print("2. If successful, you'll receive a test SMS!")
    print("")
    print("3. Then start the auction tracker with SMS:")
    print("   python3 src/enhanced_tracker.py")
    print("")
    print("4. You'll get SMS notifications for:")
    print("   🚨 When you're outbidded")
    print("   ⏰ When auctions end soon")
    print("   🚀 When tracker starts/stops")

if __name__ == "__main__":
    print("🔐 This will help you update your Twilio credentials")
    print("💡 Get your correct credentials from: https://console.twilio.com/")
    print("")
    
    success = update_twilio_credentials()
    
    if success:
        show_next_steps()
    else:
        print("\n❌ Credential update failed")
        print("💡 Make sure you have the correct values from Twilio Console")