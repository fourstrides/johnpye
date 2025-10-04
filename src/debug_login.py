#!/usr/bin/env python3
"""
Debug script to investigate login issues in detail.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(__file__))

from main import JohnPyeAuctionTracker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_login_process():
    """Debug the login process step by step."""
    print("🔍 DEBUGGING LOGIN PROCESS")
    print("=" * 50)
    
    tracker = JohnPyeAuctionTracker()
    
    try:
        # Setup driver (headless for server environment)
        success = tracker.setup_driver(headless=True)
        
        if not success:
            print("❌ WebDriver setup failed")
            return
        
        print("✅ WebDriver initialized")
        
        # Navigate to login page
        login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn"
        print(f"📱 Navigating to: {login_url}")
        tracker.driver.get(login_url)
        
        # Wait for Cloudflare
        if not tracker.wait_for_cloudflare():
            print("❌ Cloudflare protection failed")
            return
        
        print("✅ Cloudflare protection bypassed")
        
        # Handle overlays
        print("🔍 Handling page overlays...")
        tracker.handle_page_overlays()
        
        # Take a screenshot before login
        tracker.driver.save_screenshot("../data/debug_before_login.png")
        print("📸 Screenshot saved: debug_before_login.png")
        
        # Wait for form elements
        wait = WebDriverWait(tracker.driver, 15)
        
        print("🔍 Looking for form elements...")
        
        # Find form elements
        username_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        submit_button = tracker.driver.find_element(By.CSS_SELECTOR, "input.buttonbox[type='submit']")
        
        print("✅ Found all form elements")
        
        # Fill in credentials
        print("📝 Entering credentials...")
        username_field.clear()
        username_field.send_keys(tracker.config.get_username())
        print(f"   Username: {tracker.config.get_username()}")
        
        password_field.clear()
        password_field.send_keys(tracker.config.get_password())
        print("   Password: ***HIDDEN***")
        
        # Take screenshot after filling
        tracker.driver.save_screenshot("../data/debug_after_filling.png")
        print("📸 Screenshot saved: debug_after_filling.png")
        
        # Check for any validation errors
        print("🔍 Checking for validation errors...")
        error_elements = tracker.driver.find_elements(By.CSS_SELECTOR, ".error, .validation-error, .field-validation-error")
        if error_elements:
            for error in error_elements:
                if error.is_displayed():
                    print(f"⚠️ Validation error found: {error.text}")
        
        # Try to submit
        print("📤 Attempting to submit form...")
        
        # Use JavaScript click to avoid interception
        tracker.driver.execute_script("arguments[0].click();", submit_button)
        print("✅ Submit button clicked via JavaScript")
        
        # Wait a bit for response
        print("⏳ Waiting for response...")
        time.sleep(5)
        
        # Take screenshot after submission
        tracker.driver.save_screenshot("../data/debug_after_submit.png")
        print("📸 Screenshot saved: debug_after_submit.png")
        
        # Check current URL
        current_url = tracker.driver.current_url
        print(f"🔗 Current URL: {current_url}")
        
        # Check page title
        page_title = tracker.driver.title
        print(f"📄 Page title: {page_title}")
        
        # Look for error messages on the page
        print("🔍 Looking for error messages...")
        
        # Common error message selectors
        error_selectors = [
            ".error-message",
            ".alert-error",
            ".validation-summary-errors",
            ".field-validation-error",
            "[class*='error']",
            "[class*='invalid']"
        ]
        
        found_errors = []
        for selector in error_selectors:
            try:
                elements = tracker.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.text.strip():
                        found_errors.append(f"{selector}: {element.text}")
            except:
                continue
        
        if found_errors:
            print("❌ Error messages found:")
            for error in found_errors:
                print(f"   {error}")
        else:
            print("✅ No visible error messages found")
        
        # Check if we're still on login page
        if "Account/LogOn" in current_url:
            print("⚠️ Still on login page - login likely failed")
            
            # Check page source for hidden errors
            page_source = tracker.driver.page_source.lower()
            error_keywords = ["invalid", "incorrect", "wrong", "failed", "error", "denied"]
            found_keywords = [keyword for keyword in error_keywords if keyword in page_source]
            
            if found_keywords:
                print(f"🔍 Error keywords found in page source: {found_keywords}")
            
            # Look for any form validation issues
            print("🔍 Checking form validation...")
            
            # Re-examine form elements
            try:
                username_field = tracker.driver.find_element(By.ID, "username")
                password_field = tracker.driver.find_element(By.ID, "password")
                
                username_value = username_field.get_attribute("value")
                print(f"   Username field value: '{username_value}'")
                
                # Check if fields have validation classes
                username_classes = username_field.get_attribute("class")
                password_classes = password_field.get_attribute("class")
                
                print(f"   Username field classes: {username_classes}")
                print(f"   Password field classes: {password_classes}")
                
                if "error" in username_classes or "invalid" in username_classes:
                    print("⚠️ Username field has error styling")
                if "error" in password_classes or "invalid" in password_classes:
                    print("⚠️ Password field has error styling")
                    
            except Exception as e:
                print(f"❌ Could not re-examine form elements: {e}")
        else:
            print("✅ Successfully navigated away from login page")
        
        # Debug complete
        print("\n🔍 Debug analysis complete")
        
    except Exception as e:
        print(f"❌ Debug process failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if tracker.driver:
            tracker.driver.quit()
            print("🧹 Browser cleanup completed")

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs('../data', exist_ok=True)
    
    debug_login_process()