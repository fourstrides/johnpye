#!/usr/bin/env python3
"""
Test script to debug live data fetching from John Pye
"""

import os
import time
import json
from dotenv import load_dotenv
from enhanced_tracker import EnhancedAuctionTracker

load_dotenv()

def test_live_data_fetch():
    """Test fetching live data from John Pye"""
    print("🧪 Testing live data fetch from John Pye...")
    print("=" * 50)
    
    tracker = EnhancedAuctionTracker()
    
    try:
        # Setup driver (non-headless for debugging)
        print("🔧 Setting up WebDriver...")
        if not tracker.setup_driver(headless=False):
            print("❌ Failed to setup WebDriver")
            return
        
        print("✅ WebDriver setup successful")
        
        # Test login
        print("🔐 Testing login...")
        login_success = tracker.login()
        
        if login_success:
            print("✅ Login successful!")
            
            # Take screenshot after successful login
            tracker.driver.save_screenshot("../data/after_login_test.png")
            print("📸 Screenshot saved: after_login_test.png")
            
            # Wait a moment
            time.sleep(3)
            
            # Test fetching active bids
            print("📊 Testing active bids fetch...")
            active_bids = tracker.get_active_bids()
            
            print(f"📈 Found {len(active_bids)} active bids")
            
            if active_bids:
                print("✅ Sample active bids:")
                for i, bid in enumerate(active_bids[:3]):
                    print(f"  {i+1}. Lot {bid.get('lot_number')}: {bid.get('title', 'Unknown')[:60]}...")
                    print(f"      Status: {bid.get('status')} | Current: {bid.get('current_bid')} | Max: {bid.get('my_max_bid')}")
            else:
                print("❌ No active bids found")
                
                # Debug: Save page content
                page_content = tracker.driver.page_source
                with open('../data/active_bids_debug_page.html', 'w') as f:
                    f.write(page_content)
                print("📄 Page content saved for debugging: active_bids_debug_page.html")
            
            # Test watchlist
            print("👁️  Testing watchlist fetch...")
            watchlist = tracker.get_watchlist()
            print(f"👀 Found {len(watchlist)} watchlist items")
            
            if watchlist:
                print("✅ Sample watchlist items:")
                for i, item in enumerate(watchlist[:3]):
                    print(f"  {i+1}. Lot {item.get('lot_number')}: {item.get('title', 'Unknown')[:60]}...")
                    print(f"      Current: {item.get('current_bid')}")
            
            # Save all data
            all_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'active_bids': active_bids,
                'watchlist': watchlist,
                'login_successful': True
            }
            
            with open('../data/live_test_data.json', 'w') as f:
                json.dump(all_data, f, indent=2)
            print("💾 Data saved to: live_test_data.json")
            
        else:
            print("❌ Login failed")
            
            # Save screenshot for debugging
            tracker.driver.save_screenshot("../data/login_failed_debug.png")
            print("📸 Debug screenshot saved: login_failed_debug.png")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        if tracker.driver:
            tracker.driver.save_screenshot("../data/error_debug.png")
            print("📸 Error screenshot saved: error_debug.png")
    
    finally:
        # Keep browser open for manual inspection
        print("🔍 Browser window left open for manual inspection...")
        print("Press Enter to close and continue...")
        input()
        
        if tracker.driver:
            tracker.driver.quit()
            print("🔚 Browser closed")

if __name__ == "__main__":
    test_live_data_fetch()