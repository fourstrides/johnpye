#!/usr/bin/env python3
"""
Test script to validate login functionality with the actual John Pye website.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(__file__))

from main import JohnPyeAuctionTracker

def test_login_flow():
    """Test the complete login flow without actual credentials."""
    print("Testing John Pye login flow...")
    
    tracker = JohnPyeAuctionTracker()
    
    try:
        # Setup driver with visible mode for testing
        success = tracker.setup_driver(headless=False)  # Set to True for headless
        
        if not success or not tracker.driver:
            print("❌ Failed to initialize WebDriver")
            return False
        
        print("✅ WebDriver initialized successfully")
        
        # Navigate to login page and test Cloudflare handling
        login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn"
        print(f"📱 Navigating to: {login_url}")
        tracker.driver.get(login_url)
        
        # Wait for Cloudflare
        if not tracker.wait_for_cloudflare():
            print("❌ Could not bypass Cloudflare protection")
            return False
        
        print("✅ Cloudflare protection bypassed")
        print(f"📄 Page title: {tracker.driver.title}")
        
        # Check if login form elements are present
        print("\\n🔍 Checking login form elements...")
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(tracker.driver, 15)
            
            # Check for username field
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            print("✅ Username field found")
            
            # Check for password field
            password_field = tracker.driver.find_element(By.ID, "password")
            print("✅ Password field found")
            
            # Check for submit button
            submit_button = tracker.driver.find_element(By.CSS_SELECTOR, "input.buttonbox[type='submit']")
            print("✅ Submit button found")
            
            print("\\n📋 Login form validation:")
            print(f"   Username field placeholder: {username_field.get_attribute('placeholder') or 'None'}")
            print(f"   Password field type: {password_field.get_attribute('type')}")
            print(f"   Submit button value: {submit_button.get_attribute('value')}")
            
            # Test form interaction (fill with test values)
            print("\\n🧪 Testing form interaction...")
            username_field.clear()
            username_field.send_keys("test@example.com")
            print("✅ Username field accepts input")
            
            password_field.clear()
            password_field.send_keys("testpassword")
            print("✅ Password field accepts input")
            
            # Clear the fields again
            username_field.clear()
            password_field.clear()
            print("✅ Fields cleared successfully")
            
            print("\\n🎉 All login form elements are working correctly!")
            
            # Keep browser open for a moment to observe
            if not tracker.config.get_headless_mode():
                print("\\n⏳ Keeping browser open for 10 seconds for observation...")
                time.sleep(10)
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing login form: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Login flow test failed: {e}")
        return False
    
    finally:
        if tracker.driver:
            tracker.driver.quit()
            print("🧹 Browser cleanup completed")

def test_with_real_credentials():
    """Test with real credentials if available in environment."""
    print("\\n" + "="*50)
    print("REAL CREDENTIALS TEST")
    print("="*50)
    
    # Check if we have real credentials
    import os
    username = os.getenv('JOHNPYE_USERNAME')
    password = os.getenv('JOHNPYE_PASSWORD')
    
    if not username or not password or username == 'test_user':
        print("⚠️ No real credentials found in environment.")
        print("   To test with real credentials, set:")
        print("   JOHNPYE_USERNAME=your_actual_username")
        print("   JOHNPYE_PASSWORD=your_actual_password")
        return False
    
    print("🔐 Real credentials found. Testing login...")
    
    tracker = JohnPyeAuctionTracker()
    
    try:
        # Test actual login
        success = tracker.setup_driver(headless=True)
        if success and tracker.login():
            print("✅ LOGIN SUCCESSFUL with real credentials!")
            
            # Test navigation to watchlist
            print("📋 Testing watchlist access...")
            watchlist_url = "https://www.johnpyeauctions.co.uk/Account/Watchlist"
            tracker.driver.get(watchlist_url)
            time.sleep(3)
            
            if "watchlist" in tracker.driver.current_url.lower():
                print("✅ Successfully accessed watchlist page")
            else:
                print(f"⚠️ Unexpected page: {tracker.driver.current_url}")
            
            return True
        else:
            print("❌ Login failed with real credentials")
            return False
            
    except Exception as e:
        print(f"❌ Real credentials test failed: {e}")
        return False
    
    finally:
        if tracker.driver:
            tracker.driver.quit()

if __name__ == "__main__":
    print("John Pye Auction Tracker - Login Tests")
    print("=" * 50)
    
    # Test form validation
    form_test_ok = test_login_flow()
    
    # Test with real credentials if available
    real_login_ok = test_with_real_credentials()
    
    print("\\n" + "=" * 50)
    print("TEST RESULTS:")
    print("=" * 50)
    print(f"Form validation: {'✅ PASS' if form_test_ok else '❌ FAIL'}")
    print(f"Real login test: {'✅ PASS' if real_login_ok else '⚠️ SKIPPED/FAILED'}")
    
    if form_test_ok:
        print("\\n🎉 Login functionality is working correctly!")
        print("💡 Ready to test with real credentials when available.")
    else:
        print("\\n⚠️ Login form validation failed. Check the issues above.")