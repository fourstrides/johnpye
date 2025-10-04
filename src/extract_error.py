#!/usr/bin/env python3
"""
Script to extract the exact error message from login failure.
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

def extract_login_error():
    """Extract and display the exact error message."""
    print("🔍 EXTRACTING LOGIN ERROR DETAILS")
    print("=" * 50)
    
    tracker = JohnPyeAuctionTracker()
    
    try:
        success = tracker.setup_driver(headless=True)
        if not success:
            return
        
        # Navigate and login
        login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn"
        tracker.driver.get(login_url)
        
        if not tracker.wait_for_cloudflare():
            return
        
        tracker.handle_page_overlays()
        
        # Fill and submit form
        wait = WebDriverWait(tracker.driver, 15)
        username_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        
        username_field.clear()
        username_field.send_keys(tracker.config.get_username())
        password_field.clear()
        password_field.send_keys(tracker.config.get_password())
        
        submit_button = tracker.driver.find_element(By.CSS_SELECTOR, "input.buttonbox[type='submit']")
        tracker.driver.execute_script("arguments[0].click();", submit_button)
        
        # Wait for response
        time.sleep(5)
        
        # Extract page source and look for errors
        page_source = tracker.driver.page_source
        
        print("🔍 ANALYZING PAGE SOURCE FOR ERRORS...")
        
        # Look for common error patterns
        error_patterns = [
            r'<div[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</div>',
            r'<span[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</span>',
            r'<p[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</p>',
            r'Invalid.*?username.*?password',
            r'Login.*?failed',
            r'Authentication.*?failed',
            r'Incorrect.*?credentials',
        ]
        
        found_errors = []
        
        for pattern in error_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE | re.DOTALL)
            if matches:
                for match in matches:
                    # Clean up HTML tags
                    clean_match = re.sub(r'<[^>]+>', '', str(match)).strip()
                    if clean_match and len(clean_match) > 3:
                        found_errors.append(clean_match)
        
        if found_errors:
            print("❌ ERROR MESSAGES FOUND:")
            for error in found_errors:
                print(f"   • {error}")
        else:
            print("❌ No specific error messages extracted")
        
        # Check if username field shows as invalid
        try:
            username_field = tracker.driver.find_element(By.ID, "username")
            username_value = username_field.get_attribute("value")
            print(f"\\n📧 Username field after submission: '{username_value}'")
            
            if not username_value:
                print("⚠️ Username field was cleared - possible validation issue")
        except:
            pass
        
        # Look for validation summary
        print("\\n🔍 LOOKING FOR VALIDATION SUMMARY...")
        validation_selectors = [
            ".validation-summary-errors",
            ".validation-summary",
            "#validation-summary",
            ".error-summary",
            ".alert-danger",
            ".alert-error"
        ]
        
        for selector in validation_selectors:
            try:
                elements = tracker.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.text.strip():
                        print(f"✅ Found validation summary: {element.text}")
            except:
                continue
        
        # Save a sample of the page source around error keywords
        print("\\n🔍 EXAMINING PAGE SOURCE CONTEXT...")
        
        error_keywords = ['failed', 'error', 'invalid', 'incorrect']
        for keyword in error_keywords:
            keyword_lower = keyword.lower()
            page_lower = page_source.lower()
            
            if keyword_lower in page_lower:
                # Find context around the keyword
                index = page_lower.find(keyword_lower)
                start = max(0, index - 200)
                end = min(len(page_source), index + 200)
                
                context = page_source[start:end]
                print(f"\\n📝 Context around '{keyword}':")
                print(f"   {context[:400]}...")
                break
        
        # Check if this might be a CAPTCHA or other security measure
        captcha_selectors = [
            "[class*='captcha']",
            "[class*='recaptcha']",
            "#captcha",
            ".cf-turnstile"
        ]
        
        for selector in captcha_selectors:
            try:
                elements = tracker.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"⚠️ Possible CAPTCHA/security measure found: {selector}")
            except:
                continue
        
        # Final assessment
        print("\\n" + "=" * 50)
        print("📋 ASSESSMENT:")
        
        current_url = tracker.driver.current_url
        if "LogOn" in current_url:
            print("❌ Login definitively failed - still on login page")
            print("💡 Possible causes:")
            print("   1. Invalid credentials")
            print("   2. Account locked/disabled")
            print("   3. Additional verification required")
            print("   4. Rate limiting/bot detection")
            print("   5. Website changes requiring code updates")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if tracker.driver:
            tracker.driver.quit()

if __name__ == "__main__":
    extract_login_error()