#!/usr/bin/env python3
"""
Script to fetch your current bids and watchlist items from the correct John Pye URLs.
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

def get_items_from_page(tracker, url, page_type):
    """Get items from a specific page."""
    items = []
    
    try:
        print(f"🔍 Fetching {page_type} from: {url}")
        tracker.driver.get(url)
        time.sleep(3)
        
        current_url = tracker.driver.current_url
        page_title = tracker.driver.title
        
        print(f"   Current URL: {current_url}")
        print(f"   Page title: {page_title}")
        
        if "NotFound" in current_url or "Error" in page_title:
            print(f"   ❌ Page not accessible")
            return items
        
        # Take screenshot for debugging
        screenshot_name = f"../data/{page_type.lower().replace(' ', '_')}_page.png"
        tracker.driver.save_screenshot(screenshot_name)
        print(f"   📸 Screenshot saved: {screenshot_name}")
        
        # Look for various selectors that might contain items
        selectors = [
            # Table-based layouts
            "tbody tr", "table tr", ".data-table tr", ".listing-table tr",
            # List-based layouts
            ".auction-item", ".bid-item", ".lot-item", ".watchlist-item",
            # Card-based layouts
            ".card", ".item-card", ".auction-card", ".bid-card",
            # Generic containers
            "[class*='item']", "[class*='lot']", "[class*='auction']", "[class*='bid']",
            # Div containers
            ".item", ".listing", ".row"
        ]
        
        for selector in selectors:
            try:
                elements = tracker.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 1:  # More than just header
                    print(f"   ✅ Found {len(elements)} elements with selector: {selector}")
                    
                    # Try to parse the first few elements
                    parsed_items = []
                    for i, element in enumerate(elements[:10]):  # Check first 10
                        try:
                            item_data = parse_item_element(element, page_type)
                            if item_data and item_data.get('title'):  # Valid item found
                                parsed_items.append(item_data)
                                print(f"      Item {i+1}: {item_data['title'][:50]}...")
                        except Exception as e:
                            continue
                    
                    if parsed_items:
                        items.extend(parsed_items)
                        print(f"   🎯 Successfully parsed {len(parsed_items)} {page_type.lower()} items")
                        break  # Found working selector, stop trying others
                        
            except Exception as e:
                continue
        
        if not items:
            print(f"   📝 No {page_type.lower()} items found on this page")
            
            # Let's check the page content for debugging
            page_text = tracker.driver.page_source
            if "no items" in page_text.lower() or "empty" in page_text.lower():
                print(f"   💡 Page indicates no {page_type.lower()} items available")
            elif len(page_text) < 1000:
                print(f"   ⚠️ Page content seems minimal ({len(page_text)} chars)")
            else:
                print(f"   🔍 Page has content ({len(page_text)} chars) - items may use different selectors")
        
    except Exception as e:
        print(f"   ❌ Error fetching {page_type}: {e}")
    
    return items

def parse_item_element(element, page_type):
    """Parse an individual item element to extract auction data."""
    try:
        # Get all text from the element
        text = element.text.strip()
        
        if not text or len(text) < 10:
            return None
        
        # Check if this looks like an auction item
        auction_keywords = ['lot', '£', 'bid', 'end', 'time', 'auction']
        if not any(keyword in text.lower() for keyword in auction_keywords):
            return None
        
        # Split text into lines for parsing
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        item_data = {
            'title': '',
            'lot_number': '',
            'current_bid': '',
            'my_bid': '',
            'status': page_type,
            'end_time': '',
            'url': '',
            'raw_text': text
        }
        
        # Try to extract structured information
        for line in lines:
            line_lower = line.lower()
            
            # Extract lot number
            if 'lot' in line_lower and not item_data['lot_number']:
                item_data['lot_number'] = line
            
            # Extract current bid (look for £ symbol)
            elif '£' in line and not item_data['current_bid']:
                item_data['current_bid'] = line
            
            # Extract status/time information
            elif any(word in line_lower for word in ['end', 'time', 'day', 'hour', 'minute']) and not item_data['end_time']:
                item_data['end_time'] = line
            
            # Title is usually the longest meaningful line
            elif not item_data['title'] and len(line) > 10 and '£' not in line:
                item_data['title'] = line
        
        # If we didn't find a title, use the first line
        if not item_data['title'] and lines:
            item_data['title'] = lines[0]
        
        # Try to get URL from any links in the element
        try:
            link_elements = element.find_elements(By.TAG_NAME, "a")
            if link_elements:
                href = link_elements[0].get_attribute('href')
                if href and 'johnpyeauctions' in href:
                    item_data['url'] = href
        except:
            pass
        
        return item_data if item_data['title'] else None
        
    except Exception as e:
        return None

def display_items(watchlist_items, bidding_items):
    """Display all items in a formatted way."""
    total_items = len(watchlist_items) + len(bidding_items)
    
    print(f"\n🎯 YOUR JOHN PYE AUCTION ITEMS ({total_items} total)")
    print("=" * 70)
    
    if bidding_items:
        print(f"\n🔥 ACTIVE BIDS ({len(bidding_items)} items)")
        print("-" * 50)
        for i, item in enumerate(bidding_items, 1):
            print(f"\n{i}. {item.get('title', 'Unknown Item')}")
            if item.get('lot_number'):
                print(f"   📦 Lot: {item['lot_number']}")
            if item.get('current_bid'):
                print(f"   💰 Current Bid: {item['current_bid']}")
            if item.get('end_time'):
                print(f"   ⏰ End Time: {item['end_time']}")
            if item.get('url'):
                print(f"   🔗 URL: {item['url']}")
    
    if watchlist_items:
        print(f"\n👀 WATCHLIST ({len(watchlist_items)} items)")
        print("-" * 50)
        for i, item in enumerate(watchlist_items, 1):
            print(f"\n{i}. {item.get('title', 'Unknown Item')}")
            if item.get('lot_number'):
                print(f"   📦 Lot: {item['lot_number']}")
            if item.get('current_bid'):
                print(f"   💰 Current Bid: {item['current_bid']}")
            if item.get('end_time'):
                print(f"   ⏰ End Time: {item['end_time']}")
            if item.get('url'):
                print(f"   🔗 URL: {item['url']}")
    
    if not watchlist_items and not bidding_items:
        print("\n📝 NO ITEMS FOUND")
        print("Possible reasons:")
        print("• No items currently in watchlist or active bids")
        print("• Items finished or expired")
        print("• Different page structure than expected")
        print("\n💡 Check the screenshots in ../data/ for visual confirmation")
    
    # Save to CSV
    if watchlist_items or bidding_items:
        try:
            all_items = []
            
            for item in bidding_items:
                item['type'] = 'Active Bid'
                all_items.append(item)
            
            for item in watchlist_items:
                item['type'] = 'Watchlist'
                all_items.append(item)
            
            df = pd.DataFrame(all_items)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../data/my_auction_items_{timestamp}.csv"
            df.to_csv(filename, index=False)
            print(f"\n💾 Items saved to: {filename}")
            
        except Exception as e:
            print(f"\n⚠️ Could not save to CSV: {e}")

def main():
    """Main function to fetch all items."""
    print("🎯 JOHN PYE AUCTION TRACKER - FETCHING YOUR ITEMS")
    print("Getting your active bids and watchlist items...")
    print()
    
    # Ensure data directory exists
    os.makedirs('../data', exist_ok=True)
    
    tracker = JohnPyeAuctionTracker()
    watchlist_items = []
    bidding_items = []
    
    try:
        # Setup and login
        print("🔧 Setting up WebDriver...")
        if not tracker.setup_driver(headless=True):
            print("❌ WebDriver setup failed")
            return
        
        print("🔐 Logging into your John Pye account...")
        if not tracker.login():
            print("❌ Login failed")
            return
        
        print("✅ Successfully logged in!")
        print()
        
        # Get active bids
        bidding_items = get_items_from_page(
            tracker, 
            "https://www.johnpyeauctions.co.uk/Account/Bidding/Active",
            "Active Bids"
        )
        
        print()  # Add spacing
        
        # Get watchlist items
        watchlist_items = get_items_from_page(
            tracker, 
            "https://www.johnpyeauctions.co.uk/Account/Bidding/Watching",
            "Watchlist"
        )
        
    except Exception as e:
        print(f"❌ Error during fetch: {e}")
    
    finally:
        if tracker.driver:
            tracker.driver.quit()
    
    # Display results
    display_items(watchlist_items, bidding_items)
    
    print("\n" + "=" * 70)
    print("🏁 COMPLETE!")
    print("\n💡 To start monitoring these items automatically:")
    print("   python main.py")

if __name__ == "__main__":
    main()