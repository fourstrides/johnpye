#!/usr/bin/env python3
"""
Enhanced script to explore the account area and find bids/watchlist items.
"""

import sys
import os
import time
import re
sys.path.append(os.path.dirname(__file__))

from main import JohnPyeAuctionTracker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def explore_account():
    """Explore the account area to find bids and watchlist items."""
    print("🔍 EXPLORING YOUR JOHN PYE ACCOUNT")
    print("=" * 60)
    
    tracker = JohnPyeAuctionTracker()
    
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
        
        # Navigate to Account Summary
        print("\\n📋 Exploring Account Summary page...")
        tracker.driver.get("https://www.johnpyeauctions.co.uk/Account/Summary")
        time.sleep(3)
        
        print(f"Current URL: {tracker.driver.current_url}")
        print(f"Page title: {tracker.driver.title}")
        
        # Take screenshot
        tracker.driver.save_screenshot("../data/account_summary.png")
        print("📸 Screenshot saved: account_summary.png")
        
        # Look for navigation links
        print("\\n🔍 Looking for navigation links...")
        links = tracker.driver.find_elements(By.TAG_NAME, "a")
        
        relevant_links = []
        keywords = ['bid', 'watch', 'auction', 'lot', 'my', 'account', 'history', 'active', 'summary']
        
        for link in links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if href and any(keyword in href.lower() for keyword in keywords):
                    relevant_links.append((text, href))
                elif text and any(keyword in text.lower() for keyword in keywords):
                    relevant_links.append((text, href))
            except:
                continue
        
        print(f"Found {len(relevant_links)} potentially relevant links:")
        for i, (text, href) in enumerate(relevant_links[:20], 1):  # Show first 20
            print(f"   {i}. '{text}' -> {href}")
        
        # Look for any data tables or lists on the current page
        print("\\n📊 Looking for data on current page...")
        
        # Check for tables
        tables = tracker.driver.find_elements(By.TAG_NAME, "table")
        if tables:
            print(f"Found {len(tables)} tables on the page")
            for i, table in enumerate(tables[:3], 1):  # Check first 3 tables
                try:
                    table_text = table.text.strip()
                    if table_text and len(table_text) > 20:
                        print(f"\\n   Table {i} content (first 300 chars):")
                        print(f"   {table_text[:300]}...")
                except:
                    continue
        
        # Check for div elements that might contain bid/auction info
        print("\\n🎯 Looking for auction-related content...")
        content_selectors = [
            "[class*='bid']", "[class*='auction']", "[class*='watchlist']",
            "[class*='lot']", "[class*='item']", ".summary", ".account-info"
        ]
        
        for selector in content_selectors:
            try:
                elements = tracker.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\\nFound {len(elements)} elements with selector '{selector}':")
                    for i, elem in enumerate(elements[:3], 1):  # Check first 3
                        try:
                            text = elem.text.strip()
                            if text and len(text) > 10:
                                print(f"   Element {i}: {text[:100]}...")
                        except:
                            continue
            except:
                continue
        
        # Try to find menu items or navigation
        print("\\n🧭 Looking for navigation menu...")
        nav_selectors = [
            "nav", ".nav", ".navigation", ".menu", ".sidebar", 
            "[class*='menu']", "[class*='nav']"
        ]
        
        for selector in nav_selectors:
            try:
                navs = tracker.driver.find_elements(By.CSS_SELECTOR, selector)
                if navs:
                    print(f"\\nFound navigation with selector '{selector}':")
                    for i, nav in enumerate(navs[:2], 1):
                        try:
                            nav_text = nav.text.strip()
                            if nav_text and len(nav_text) > 5:
                                print(f"   Nav {i}: {nav_text}")
                        except:
                            continue
            except:
                continue
        
        # Try some common account URLs directly
        print("\\n🔍 Testing additional account URLs...")
        test_urls = [
            "https://www.johnpyeauctions.co.uk/Account/Profile",
            "https://www.johnpyeauctions.co.uk/Account/Orders",
            "https://www.johnpyeauctions.co.uk/Account/History",
            "https://www.johnpyeauctions.co.uk/Account/Activity",
            "https://www.johnpyeauctions.co.uk/MyAccount",
            "https://www.johnpyeauctions.co.uk/Account/Dashboard",
            "https://www.johnpyeauctions.co.uk/User/Bids",
            "https://www.johnpyeauctions.co.uk/User/Watchlist"
        ]
        
        for url in test_urls:
            try:
                tracker.driver.get(url)
                time.sleep(2)
                current_url = tracker.driver.current_url
                title = tracker.driver.title
                
                if "NotFound" not in current_url and "Error" not in title:
                    print(f"✅ Accessible: {url}")
                    print(f"   Redirects to: {current_url}")
                    print(f"   Title: {title}")
                    
                    # Quick check for content
                    page_text = tracker.driver.page_source.lower()
                    if any(word in page_text for word in ['bid', 'auction', 'lot', 'watchlist']):
                        print(f"   📋 Contains relevant content!")
                        
                        # Take screenshot of this page
                        filename = url.split('/')[-1] or 'page'
                        tracker.driver.save_screenshot(f"../data/{filename}_page.png")
                        print(f"   📸 Screenshot saved: {filename}_page.png")
                else:
                    print(f"❌ Not found: {url}")
                    
            except Exception as e:
                print(f"❌ Error accessing {url}: {e}")
        
        # Check the main page for any account-related areas
        print("\\n🏠 Checking main page for account links...")
        tracker.driver.get("https://www.johnpyeauctions.co.uk/")
        time.sleep(2)
        
        # Look for login status or account links
        account_indicators = tracker.driver.find_elements(By.XPATH, "//*[contains(text(), 'Account') or contains(text(), 'My') or contains(text(), 'Welcome')]")
        
        if account_indicators:
            print(f"Found {len(account_indicators)} account-related elements on main page:")
            for elem in account_indicators[:5]:
                try:
                    print(f"   • {elem.text}")
                except:
                    continue
        
        # Final summary
        print("\\n" + "=" * 60)
        print("📋 EXPLORATION COMPLETE")
        print("=" * 60)
        print("Check the screenshots in ../data/ directory for visual inspection.")
        print("\\nNext steps:")
        print("1. Review screenshots to identify the correct pages")
        print("2. Look for 'My Bids', 'Watchlist', or similar links")
        print("3. Update the application to use the correct URLs")
        
    except Exception as e:
        print(f"❌ Error during exploration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if tracker.driver:
            tracker.driver.quit()

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs('../data', exist_ok=True)
    explore_account()