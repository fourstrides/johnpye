#!/usr/bin/env python3
"""
Demo SMS notifications - shows what you'll receive from the auction tracker
"""

import time
from datetime import datetime

def demo_sms_notifications():
    """Demonstrate the SMS notifications you'll receive."""
    
    print("📱 SMS NOTIFICATIONS DEMO")
    print("=" * 50)
    print("🎭 This shows exactly what SMS messages you'll receive")
    print("   on your phone when the auction tracker is running.")
    print("=" * 50)
    
    # Demo 1: Tracker Started
    print("\n🚀 DEMO 1: TRACKER STARTUP NOTIFICATION")
    print("-" * 40)
    show_sms_message(
        "🚀 John Pye Auction Tracker STARTED\n"
        "✅ Monitoring 5 active bids, 30 watchlist items\n"
        "💰 Total current value: £1,415\n"
        "🎯 Total max bid value: £1,446\n"
        f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}\n"
        "📊 Dashboard: http://localhost:8080"
    )
    
    input("\nPress Enter to see next notification...")
    
    # Demo 2: Outbidded Alert (URGENT!)
    print("\n🚨 DEMO 2: OUTBIDDED ALERT (URGENT!)")
    print("-" * 40)
    show_sms_message(
        "🚨 YOU'VE BEEN OUTBIDDED! 🚨\n"
        "Item: TCL 98P745K 98\" 4K, UHD, SMART TV\n"
        "Lot: 2\n"
        "Your Bid: £340.00\n"
        "New High Bid: £350.00\n"
        "Outbid by: £10.00\n"
        f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
        "Take action now: https://www.johnpyeauctions.co.uk/Account/Bidding/Active"
    )
    
    input("\nPress Enter to see next notification...")
    
    # Demo 3: Auction Ending Soon
    print("\n⏰ DEMO 3: AUCTION ENDING SOON")
    print("-" * 40)
    show_sms_message(
        "⏰ AUCTION ENDING SOON!\n"
        "Item: PALLET OF ASSORTED PRINTERS\n"
        "Lot: 86\n"
        "Current Bid: £55.00\n"
        "Your Max Bid: £86.00\n"
        "Time Remaining: ~15 minutes\n"
        f"Alert sent: {datetime.now().strftime('%H:%M:%S')}\n"
        "Check now: https://www.johnpyeauctions.co.uk/Event/LotDetails/..."
    )
    
    input("\nPress Enter to see next notification...")
    
    # Demo 4: Bid Increase Alert
    print("\n📈 DEMO 4: BID INCREASE ON WATCHLIST ITEM")
    print("-" * 40)
    show_sms_message(
        "📈 BID INCREASE ALERT!\n"
        "Item: HISENSE 100E7NQTUK 100\" 4K SMART TV\n"
        "Lot: 425953434\n"
        "Previous Bid: £320.00\n"
        "Current Bid: £340.00\n"
        "Increase: £20.00\n"
        f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
        "Consider bidding: https://www.johnpyeauctions.co.uk/Event/LotDetails/425953434"
    )
    
    input("\nPress Enter to see final notification...")
    
    # Demo 5: Tracker Stopped
    print("\n⏹️ DEMO 5: TRACKER STOPPED")
    print("-" * 40)
    show_sms_message(
        "⏹️ John Pye Auction Tracker STOPPED\n"
        "📊 Final Status:\n"
        "   • 4 bids still winning 🏆\n"
        "   • 1 bid outbid 🚨\n"
        "   • 30 watchlist items monitored 👁️\n"
        "⏱️ Monitored for: 2 hours 15 minutes\n"
        f"Stopped: {datetime.now().strftime('%H:%M:%S')}\n"
        "Dashboard: http://localhost:8080"
    )

def show_sms_message(message):
    """Display a message as it would appear on your phone."""
    
    print("📱 YOUR PHONE RECEIVES:")
    print("┌" + "─" * 48 + "┐")
    
    lines = message.split('\n')
    for line in lines:
        # Truncate long lines to fit mobile screen width
        if len(line) > 46:
            line = line[:43] + "..."
        print("│ " + line.ljust(46) + " │")
    
    print("└" + "─" * 48 + "┘")
    print(f"📲 From: +447830353517 (Twilio)")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")

def show_sms_settings():
    """Show how SMS notifications are configured."""
    
    print("\n" + "=" * 50)
    print("⚙️ SMS NOTIFICATION SETTINGS")
    print("=" * 50)
    
    print("\n🔔 WHEN YOU'LL RECEIVE SMS:")
    print("   ✅ When auction tracker starts/stops")
    print("   🚨 When you're outbidded (URGENT)")
    print("   ⏰ When auctions are ending soon (< 30 minutes)")
    print("   📈 When bids increase on watchlist items (> £10)")
    print("   ❌ When tracker encounters errors")
    
    print("\n⚡ SMS DELIVERY:")
    print("   📞 From: +447830353517 (Your Twilio number)")
    print("   📱 To: +447902366190 (Your phone)")
    print("   💨 Speed: Instant delivery (usually < 10 seconds)")
    print("   💰 Cost: ~£0.005 per message")
    
    print("\n🎛️ CUSTOMIZATION OPTIONS:")
    print("   • Bid increase threshold (default £10)")
    print("   • Ending soon threshold (default 30 minutes)")
    print("   • Enable/disable specific notification types")
    print("   • Multiple phone numbers support")

if __name__ == "__main__":
    demo_sms_notifications()
    show_sms_settings()
    
    print("\n" + "=" * 50)
    print("🎯 TO ENABLE REAL SMS NOTIFICATIONS:")
    print("1. Fix your Twilio credentials (see fix_sms_setup.py)")
    print("2. Run: python3 test_sms_direct.py")
    print("3. When successful, start the auction tracker!")
    print("4. You'll get these exact notifications on your phone!")
    print("=" * 50)
    
    print("\n💡 TIP: SMS notifications work great with:")
    print("   • Phone on silent - SMS still comes through")
    print("   • Multiple devices - forward SMS to email")
    print("   • Away from computer - get alerts anywhere")
    print("   • Night monitoring - wake you for urgent outbids")