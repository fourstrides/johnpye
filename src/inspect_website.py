#!/usr/bin/env python3
"""
Script to inspect the John Pye website structure and identify correct CSS selectors.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def inspect_login_page():
    """Inspect the login page structure."""
    print("🔍 Inspecting John Pye login page structure...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn?returnUrl=%2F"
        print(f"📱 Navigating to: {login_url}")
        driver.get(login_url)
        
        # Wait for page to load
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Try to find login form elements
        print("\\n🔍 Looking for login form elements...")
        
        # Check for various possible username field IDs/names
        username_selectors = [
            "#UserName", "#username", "#email", "[name='UserName']", "[name='username']", "[name='email']",
            "input[type='text']", "input[type='email']"
        ]
        
        for selector in username_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found username field: {selector} -> {element.tag_name}")
                if element.get_attribute('id'):
                    print(f"   ID: {element.get_attribute('id')}")
                if element.get_attribute('name'):
                    print(f"   Name: {element.get_attribute('name')}")
                if element.get_attribute('placeholder'):
                    print(f"   Placeholder: {element.get_attribute('placeholder')}")
            except:
                pass
        
        # Check for password field
        password_selectors = [
            "#Password", "#password", "[name='Password']", "[name='password']",
            "input[type='password']"
        ]
        
        for selector in password_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found password field: {selector} -> {element.tag_name}")
                if element.get_attribute('id'):
                    print(f"   ID: {element.get_attribute('id')}")
                if element.get_attribute('name'):
                    print(f"   Name: {element.get_attribute('name')}")
            except:
                pass
        
        # Check for login button
        button_selectors = [
            "input[type='submit']", "button[type='submit']", ".login-button", "#login-button",
            "input[value*='Log']", "button:contains('Log')"
        ]
        
        for selector in button_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found login button: {selector} -> {element.tag_name}")
                if element.get_attribute('value'):
                    print(f"   Value: {element.get_attribute('value')}")
                if element.text:
                    print(f"   Text: {element.text}")
            except:
                pass
        
        # Get page source sample
        print("\\n📝 Page source sample (first 1000 characters):")
        print(driver.page_source[:1000])
        print("...")
        
    except Exception as e:
        print(f"❌ Error inspecting login page: {e}")
    
    finally:
        driver.quit()

def inspect_watchlist_page():
    """Inspect the watchlist page structure (without login)."""
    print("\\n🔍 Inspecting John Pye watchlist page structure...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Try to access watchlist page (will likely redirect to login)
        watchlist_url = "https://www.johnpyeauctions.co.uk/Account/Watchlist"
        print(f"📱 Navigating to: {watchlist_url}")
        driver.get(watchlist_url)
        
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Check if we were redirected to login
        if "LogOn" in driver.current_url or "login" in driver.current_url.lower():
            print("🔄 Redirected to login page as expected")
        else:
            print("📋 Checking for watchlist elements...")
            
            # Look for potential watchlist item containers
            item_selectors = [
                ".watchlist-item", ".auction-item", ".lot-item", 
                "[class*='watchlist']", "[class*='auction']", "[class*='lot']",
                ".item", ".listing"
            ]
            
            for selector in item_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                except:
                    pass
        
    except Exception as e:
        print(f"❌ Error inspecting watchlist page: {e}")
    
    finally:
        driver.quit()

def inspect_main_page():
    """Inspect the main page for general site structure."""
    print("\\n🔍 Inspecting John Pye main page structure...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        main_url = "https://www.johnpyeauctions.co.uk"
        print(f"📱 Navigating to: {main_url}")
        driver.get(main_url)
        
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Check if site is accessible
        if "Error" in driver.title or "Not Found" in driver.title:
            print("❌ Site appears to be inaccessible")
        else:
            print("✅ Site is accessible")
            
            # Look for auction listings on main page
            print("\\n🔍 Looking for auction item elements...")
            
            item_selectors = [
                ".auction-item", ".lot-item", ".listing-item",
                "[class*='auction']", "[class*='lot']", "[class*='listing']",
                ".card", ".item"
            ]
            
            for selector in item_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        # Sample first element structure
                        if elements:
                            elem = elements[0]
                            print(f"   Sample element class: {elem.get_attribute('class')}")
                            print(f"   Sample element text: {elem.text[:100]}...")
                except:
                    pass
        
    except Exception as e:
        print(f"❌ Error inspecting main page: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    print("John Pye Auction Website Inspector")
    print("=" * 50)
    
    inspect_main_page()
    inspect_login_page()
    inspect_watchlist_page()
    
    print("\\n" + "=" * 50)
    print("💡 Inspection complete! Check the output above to understand")
    print("   the actual HTML structure and adjust CSS selectors accordingly.")