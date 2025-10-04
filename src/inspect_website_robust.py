#!/usr/bin/env python3
"""
Robust script to inspect the John Pye website structure, handling Cloudflare protection.
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

def create_driver(visible=False):
    """Create a WebDriver instance with appropriate options."""
    chrome_options = Options()
    if not visible:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    # Add user agent to appear more like a real browser
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    
    service = Service('/usr/bin/chromedriver')
    return webdriver.Chrome(service=service, options=chrome_options)

def wait_for_cloudflare(driver, timeout=30):
    """Wait for Cloudflare protection to pass."""
    print("⏳ Waiting for Cloudflare protection to clear...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_title = driver.title
        print(f"   Current title: {current_title}")
        
        # Check if we're past the Cloudflare check
        if "Just a moment" not in current_title and current_title.strip():
            print("✅ Cloudflare protection cleared!")
            return True
        
        time.sleep(2)
    
    print("⚠️ Cloudflare protection did not clear within timeout")
    return False

def test_site_access():
    """Test basic site access with Cloudflare handling."""
    print("🔍 Testing John Pye site access with Cloudflare handling...")
    
    driver = create_driver(visible=False)
    
    try:
        # Navigate to main site
        main_url = "https://www.johnpyeauctions.co.uk"
        print(f"📱 Navigating to: {main_url}")
        driver.get(main_url)
        
        # Wait for Cloudflare to clear
        if wait_for_cloudflare(driver, timeout=45):
            print(f"📄 Final page title: {driver.title}")
            print(f"🔗 Final URL: {driver.current_url}")
            
            # Check page content
            print("\\n🔍 Analyzing page content...")
            page_source = driver.page_source
            
            # Look for common auction site elements
            elements_found = []
            if "auction" in page_source.lower():
                elements_found.append("auction content")
            if "lot" in page_source.lower():
                elements_found.append("lot references")
            if "bid" in page_source.lower():
                elements_found.append("bidding content")
            if "login" in page_source.lower() or "sign in" in page_source.lower():
                elements_found.append("login functionality")
                
            if elements_found:
                print(f"✅ Found relevant elements: {', '.join(elements_found)}")
            else:
                print("❌ No obvious auction-related content found")
                
            # Save a sample of the HTML for manual inspection
            with open('../data/sample_homepage.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("💾 Saved full page source to ../data/sample_homepage.html")
            
            return True
        else:
            print("❌ Could not bypass Cloudflare protection")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing site: {e}")
        return False
    
    finally:
        driver.quit()

def test_login_page_access():
    """Test access to login page specifically."""
    print("\\n🔍 Testing login page access...")
    
    driver = create_driver(visible=False)
    
    try:
        # Navigate directly to login page
        login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn"
        print(f"📱 Navigating to: {login_url}")
        driver.get(login_url)
        
        # Wait for Cloudflare to clear
        if wait_for_cloudflare(driver, timeout=45):
            print(f"📄 Login page title: {driver.title}")
            print(f"🔗 Login page URL: {driver.current_url}")
            
            # Look for login form elements
            print("\\n🔍 Looking for login form elements...")
            page_source = driver.page_source.lower()
            
            form_elements = []
            if 'input' in page_source and 'password' in page_source:
                form_elements.append("password field")
            if 'input' in page_source and ('username' in page_source or 'email' in page_source):
                form_elements.append("username/email field")
            if 'submit' in page_source or 'login' in page_source:
                form_elements.append("submit button")
                
            if form_elements:
                print(f"✅ Found form elements: {', '.join(form_elements)}")
            else:
                print("❌ No obvious login form elements found")
                
            # Save login page HTML
            with open('../data/sample_login.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("💾 Saved login page source to ../data/sample_login.html")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error accessing login page: {e}")
        return False
    
    finally:
        driver.quit()

def provide_recommendations():
    """Provide recommendations based on findings."""
    print("\\n" + "="*50)
    print("📋 RECOMMENDATIONS:")
    print("="*50)
    
    print("1. 🛡️ CLOUDFLARE PROTECTION:")
    print("   - The site uses Cloudflare protection")
    print("   - Consider adding delays and user-agent headers")
    print("   - May need to handle dynamic loading")
    
    print("\\n2. 🔍 NEXT STEPS FOR TESTING:")
    print("   - Check the saved HTML files in ../data/ directory")
    print("   - Manually inspect the HTML structure")
    print("   - Update CSS selectors based on actual structure")
    
    print("\\n3. 💡 IMPLEMENTATION SUGGESTIONS:")
    print("   - Add longer waits after navigation")
    print("   - Implement retry logic for Cloudflare")
    print("   - Consider using undetected-chromedriver if needed")
    print("   - Test with real credentials in a controlled manner")

if __name__ == "__main__":
    print("John Pye Auction Website - Robust Inspector")
    print("=" * 50)
    
    # Ensure data directory exists
    os.makedirs('../data', exist_ok=True)
    
    # Test site access
    main_success = test_site_access()
    login_success = test_login_page_access()
    
    # Provide recommendations
    provide_recommendations()
    
    # Final status
    print("\\n" + "="*50)
    print("📊 TEST RESULTS:")
    print(f"Main site access: {'✅ SUCCESS' if main_success else '❌ FAILED'}")
    print(f"Login page access: {'✅ SUCCESS' if login_success else '❌ FAILED'}")
    
    if main_success or login_success:
        print("\\n🎉 Partial success! Check the HTML files for structure details.")
    else:
        print("\\n⚠️ Site access challenges detected. May need alternative approaches.")