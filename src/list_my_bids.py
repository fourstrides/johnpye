#!/usr/bin/env python3
"""
Script to list all products the user is currently bidding on.
"""

import sys
import os
import time
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

from main import JohnPyeAuctionTracker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_my_bids():
    """Get all items the user is currently bidding on."""
    print("🎯 FETCHING YOUR CURRENT BIDS FROM JOHN PYE")
    print("=" * 60)
    
    tracker = JohnPyeAuctionTracker()
    my_bids = []
    
    try:
        # Setup and login
        print("🔧 Setting up WebDriver...")
        if not tracker.setup_driver(headless=True):
            print("❌ WebDriver setup failed")
            return []
        
        print("🔐 Logging into your John Pye account...")
        if not tracker.login():
            print("❌ Login failed")
            return []
        
        print("✅ Successfully logged in!")
        
        # Navigate to "My Bids" page
        print("📋 Fetching your current bids...")
        
        # Try different URLs that might contain bid information
        bid_urls = [
            "https://www.johnpyeauctions.co.uk/Account/MyBids",
            "https://www.johnpyeauctions.co.uk/Account/Bids",
            "https://www.johnpyeauctions.co.uk/MyAccount/Bids",
            "https://www.johnpyeauctions.co.uk/Account",
            "https://www.johnpyeauctions.co.uk/Account/Watchlist"
        ]
        
        wait = WebDriverWait(tracker.driver, 10)
        
        for url in bid_urls:
            try:
                print(f"🔍 Trying: {url}")
                tracker.driver.get(url)
                time.sleep(3)
                
                current_url = tracker.driver.current_url
                page_title = tracker.driver.title
                
                print(f"   Current URL: {current_url}")
                print(f"   Page title: {page_title}")
                
                # Look for bid-related content
                if "NotFound" not in current_url and "Error" not in page_title:
                    # Look for various selectors that might contain bid information
                    bid_selectors = [
                        ".bid-item", ".my-bid", ".auction-item", ".lot-item",
                        "[class*='bid']", "[class*='auction']", "[class*='lot']",
                        "tr", ".listing", ".item", ".card"
                    ]
                    
                    found_items = False
                    for selector in bid_selectors:
                        try:
                            items = tracker.driver.find_elements(By.CSS_SELECTOR, selector)
                            if items and len(items) > 0:
                                print(f"   Found {len(items)} items with selector: {selector}")
                                
                                # Try to extract information from the first few items
                                for i, item in enumerate(items[:5]):  # Check first 5 items
                                    try:
                                        item_text = item.text.strip()
                                        if item_text and len(item_text) > 10:  # Has meaningful content
                                            print(f"      Item {i+1}: {item_text[:100]}...")
                                            
                                            # Try to extract structured data
                                            bid_info = extract_bid_info(item)
                                            if bid_info:
                                                my_bids.append(bid_info)
                                                found_items = True
                                    except Exception as e:
                                        continue
                                        
                                if found_items:
                                    break
                        except Exception as e:
                            continue
                    
                    if found_items:
                        print(f"✅ Found bid information on: {url}")
                        break
                        
            except Exception as e:
                print(f"   ❌ Error accessing {url}: {e}")
                continue
        
        # Also try to get watchlist items
        print("\\n📋 Checking watchlist...")
        try:
            watchlist_items = get_watchlist_items(tracker)
            if watchlist_items:
                my_bids.extend(watchlist_items)
                print(f"✅ Found {len(watchlist_items)} watchlist items")
        except Exception as e:
            print(f"⚠️ Watchlist check failed: {e}")
        
        # Take a screenshot for debugging
        try:
            tracker.driver.save_screenshot("../data/my_bids_page.png")
            print("📸 Screenshot saved: my_bids_page.png")
        except:
            pass
            
    except Exception as e:
        print(f"❌ Error fetching bids: {e}")
    
    finally:
        if tracker.driver:
            tracker.driver.quit()
    
    return my_bids

def extract_bid_info(element):
    """Extract bid information from a page element."""
    try:
        text = element.text
        
        # Look for patterns that indicate this is a bid/auction item
        if any(keyword in text.lower() for keyword in ['lot', 'bid', '£', 'auction', 'ending']):
            # Try to extract basic information
            lines = [line.strip() for line in text.split('\\n') if line.strip()]
            
            bid_info = {
                'title': '',
                'lot_number': '',
                'current_bid': '',
                'status': '',
                'end_time': '',
                'full_text': text
            }
            
            # Try to parse information from the text
            for line in lines:
                if 'lot' in line.lower() and not bid_info['lot_number']:
                    bid_info['lot_number'] = line
                elif '£' in line and not bid_info['current_bid']:
                    bid_info['current_bid'] = line
                elif any(word in line.lower() for word in ['ending', 'ended', 'active']) and not bid_info['status']:
                    bid_info['status'] = line
                elif not bid_info['title'] and len(line) > 5:
                    bid_info['title'] = line
            
            return bid_info
            
    except Exception as e:
        return None

def get_watchlist_items(tracker):
    """Get items from watchlist as a fallback."""
    watchlist_items = []
    
    try:
        # Try the main watchlist method from our tracker
        items = tracker.get_watchlist_items()
        
        for item in items:
            watchlist_items.append({
                'title': item.title,
                'lot_number': item.lot_number,
                'current_bid': item.current_bid,
                'status': 'Watchlist',
                'end_time': item.end_time,
                'url': item.url
            })
            
    except Exception as e:
        print(f"   Watchlist extraction error: {e}")
    
    return watchlist_items

def display_bids(bids):
    """Display the bids in a nice format."""
    if not bids:
        print("\\n📝 NO ACTIVE BIDS FOUND")
        print("=" * 60)
        print("You don't appear to have any active bids or watchlist items.")
        print("\\nPossible reasons:")
        print("• No items in your watchlist")
        print("• No active bids placed")
        print("• Items may be on different account pages")
        print("• Website structure may have changed")
        return
    
    print(f"\\n🎯 YOUR CURRENT BIDS AND WATCHLIST ({len(bids)} items)")
    print("=" * 60)
    
    for i, bid in enumerate(bids, 1):
        print(f"\\n{i}. {bid.get('title', 'Unknown Item')}")
        print(f"   📦 Lot: {bid.get('lot_number', 'Unknown')}")
        print(f"   💰 Current Bid: {bid.get('current_bid', 'Unknown')}")
        print(f"   📊 Status: {bid.get('status', 'Unknown')}")
        if bid.get('end_time'):
            print(f"   ⏰ End Time: {bid.get('end_time', 'Unknown')}")
        if bid.get('url'):
            print(f"   🔗 URL: {bid.get('url', 'N/A')}")
    
    # Save to CSV
    try:
        df = pd.DataFrame(bids)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../data/my_bids_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"\\n💾 Bid data saved to: {filename}")
    except Exception as e:
        print(f"\\n⚠️ Could not save to CSV: {e}")

def main():
    """Main function."""
    print("📋 JOHN PYE AUCTION TRACKER - MY BIDS")
    print("Fetching your current bids and watchlist items...")
    print()
    
    # Ensure data directory exists
    os.makedirs('../data', exist_ok=True)
    
    # Get bids
    bids = get_my_bids()
    
    # Display results
    display_bids(bids)
    
    print("\\n" + "=" * 60)
    print("🏁 COMPLETE!")
    print("\\n💡 To start monitoring these items automatically:")
    print("   python main.py")

if __name__ == "__main__":
    main()