#!/usr/bin/env python3
"""
Live Connection Test for John Pye Auctions
This script tests actual connection to the live site and data extraction.
"""

import os
import sys
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LiveConnectionTest:
    """Test live connection to John Pye Auctions."""
    
    def __init__(self):
        """Initialize the test."""
        self.driver = None
        self.logger = self.setup_logging()
        
    def setup_logging(self):
        """Set up logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def setup_driver(self, headless=False):
        """Set up Chrome WebDriver."""
        self.logger.info("🔧 Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.binary_location = '/usr/bin/chromium-browser'
        
        try:
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.logger.info("✅ WebDriver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize WebDriver: {e}")
            return False
    
    def wait_for_cloudflare(self, timeout=45):
        """Wait for Cloudflare protection to clear."""
        self.logger.info("⏳ Waiting for Cloudflare protection to clear...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_title = self.driver.title
            if "Just a moment" not in current_title and current_title.strip():
                self.logger.info("✅ Cloudflare protection cleared")
                return True
            self.logger.info(f"   Current title: {current_title}")
            time.sleep(3)
        
        self.logger.warning("⚠️  Cloudflare protection did not clear within timeout")
        return False
    
    def test_homepage(self):
        """Test accessing the homepage."""
        self.logger.info("🌐 Testing homepage access...")
        
        try:
            self.driver.get("https://www.johnpyeauctions.co.uk")
            
            if not self.wait_for_cloudflare():
                return False
            
            # Take a screenshot
            screenshot_path = "../data/homepage_test.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"📸 Homepage screenshot saved: {screenshot_path}")
            
            # Check title
            title = self.driver.title
            self.logger.info(f"📄 Page title: {title}")
            
            if "John Pye" in title:
                self.logger.info("✅ Homepage loaded successfully")
                return True
            else:
                self.logger.error("❌ Homepage title doesn't contain 'John Pye'")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Homepage test failed: {e}")
            return False
    
    def test_login(self):
        """Test login functionality."""
        self.logger.info("🔐 Testing login...")
        
        try:
            login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn"
            self.driver.get(login_url)
            
            if not self.wait_for_cloudflare():
                return False
            
            # Take screenshot of login page
            screenshot_path = "../data/login_page_test.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"📸 Login page screenshot saved: {screenshot_path}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Find username field
            self.logger.info("👤 Entering username...")
            username_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
            username_field.clear()
            username_field.send_keys(os.getenv('JOHNPYE_USERNAME'))
            
            # Find password field
            self.logger.info("🔑 Entering password...")
            password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
            password_field.clear()
            password_field.send_keys(os.getenv('JOHNPYE_PASSWORD'))
            
            # Handle checkboxes
            self.logger.info("☑️  Handling checkboxes...")
            try:
                checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                self.logger.info(f"   Found {len(checkboxes)} checkboxes")
                for i, checkbox in enumerate(checkboxes):
                    if checkbox.is_displayed() and checkbox.is_enabled():
                        if not checkbox.is_selected():
                            self.driver.execute_script("arguments[0].click();", checkbox)
                            self.logger.info(f"   ✅ Checked checkbox {i+1}")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Checkbox handling issue: {e}")
            
            # Submit form
            self.logger.info("📤 Submitting login form...")
            try:
                submit_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.buttonbox[type='submit']")))
                self.driver.execute_script("arguments[0].click();", submit_button)
                self.logger.info("   Form submitted via JavaScript")
            except Exception as e:
                self.logger.error(f"   ❌ Form submission failed: {e}")
                return False
            
            # Wait for redirect
            self.logger.info("⏳ Waiting for login redirect...")
            time.sleep(5)
            
            # Check current URL
            current_url = self.driver.current_url
            self.logger.info(f"📍 Current URL after login: {current_url}")
            
            # Take screenshot after login
            screenshot_path = "../data/after_login_test.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"📸 After login screenshot saved: {screenshot_path}")
            
            if "Account/LogOn" not in current_url:
                self.logger.info("✅ Login successful - redirected from login page")
                return True
            else:
                self.logger.error("❌ Login failed - still on login page")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login test failed: {e}")
            return False
    
    def test_account_pages(self):
        """Test accessing account pages."""
        self.logger.info("📊 Testing account pages access...")
        
        pages_to_test = [
            ("Active Bids", "https://www.johnpyeauctions.co.uk/Account/Bidding/Active"),
            ("Watchlist", "https://www.johnpyeauctions.co.uk/Account/Bidding/Watching"),
            ("Bidding History", "https://www.johnpyeauctions.co.uk/Account/Bidding")
        ]
        
        results = {}
        
        for page_name, url in pages_to_test:
            self.logger.info(f"   🔍 Testing {page_name} page...")
            try:
                self.driver.get(url)
                time.sleep(3)
                
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                # Take screenshot
                screenshot_path = f"../data/{page_name.lower().replace(' ', '_')}_test.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.info(f"      📸 Screenshot saved: {screenshot_path}")
                
                # Check if we're redirected to login (indicating not logged in)
                if "Account/LogOn" in current_url:
                    self.logger.error(f"      ❌ Redirected to login - authentication may have failed")
                    results[page_name] = False
                else:
                    self.logger.info(f"      ✅ {page_name} page accessible")
                    self.logger.info(f"      📄 Title: {page_title}")
                    results[page_name] = True
                    
                    # Try to extract some content
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    self.logger.info(f"      📝 Page content length: {len(body_text)} characters")
                    
                    if len(body_text) > 100:
                        # Save sample content
                        content_file = f"../data/{page_name.lower().replace(' ', '_')}_content.txt"
                        with open(content_file, 'w') as f:
                            f.write(f"URL: {current_url}\n")
                            f.write(f"Title: {page_title}\n")
                            f.write(f"Content sample (first 1000 chars):\n")
                            f.write("-" * 50 + "\n")
                            f.write(body_text[:1000])
                        self.logger.info(f"      💾 Content sample saved: {content_file}")
                
            except Exception as e:
                self.logger.error(f"      ❌ Error testing {page_name}: {e}")
                results[page_name] = False
        
        return results
    
    def extract_bid_data(self):
        """Try to extract actual bid data."""
        self.logger.info("🎯 Attempting to extract real bid data...")
        
        # Navigate to active bids page
        try:
            self.driver.get("https://www.johnpyeauctions.co.uk/Account/Bidding/Active")
            time.sleep(3)
            
            current_url = self.driver.current_url
            if "Account/LogOn" in current_url:
                self.logger.error("❌ Can't access bids page - authentication issue")
                return []
            
            # Try multiple selectors to find bid data
            selectors_to_try = [
                "tr",
                ".bid-row", 
                ".auction-item",
                "[class*='bid']",
                "[class*='lot']",
                "table tbody tr",
                ".row"
            ]
            
            all_bids = []
            
            for selector in selectors_to_try:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"   🔍 Found {len(elements)} elements with selector '{selector}'")
                    
                    if len(elements) > 0:
                        for i, element in enumerate(elements[:5]):  # Check first 5
                            try:
                                text_content = element.text.strip()
                                if text_content and len(text_content) > 50:  # Substantial content
                                    self.logger.info(f"      Element {i+1} content: {text_content[:100]}...")
                                    
                                    # Try to extract structured data
                                    if any(keyword in text_content.lower() for keyword in ['lot', 'bid', '£', 'auction']):
                                        all_bids.append({
                                            'element_index': i,
                                            'selector': selector,
                                            'content': text_content,
                                            'length': len(text_content)
                                        })
                            except Exception as e:
                                self.logger.debug(f"      Error processing element {i}: {e}")
                                
                except Exception as e:
                    self.logger.debug(f"   Selector '{selector}' failed: {e}")
            
            self.logger.info(f"✅ Found {len(all_bids)} potential bid elements")
            
            # Save findings to file
            if all_bids:
                findings_file = "../data/bid_data_extraction.txt"
                with open(findings_file, 'w') as f:
                    f.write(f"Bid Data Extraction Results - {datetime.now()}\n")
                    f.write("=" * 60 + "\n\n")
                    for i, bid in enumerate(all_bids):
                        f.write(f"BID ELEMENT {i+1}:\n")
                        f.write(f"Selector: {bid['selector']}\n")
                        f.write(f"Content Length: {bid['length']}\n")
                        f.write(f"Content:\n{bid['content']}\n")
                        f.write("-" * 40 + "\n\n")
                
                self.logger.info(f"💾 Bid extraction results saved: {findings_file}")
            
            return all_bids
            
        except Exception as e:
            self.logger.error(f"❌ Bid data extraction failed: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.logger.info("🧹 Browser closed")
    
    def run_full_test(self):
        """Run complete test suite."""
        self.logger.info("🚀 Starting Live Connection Test Suite")
        self.logger.info("=" * 60)
        
        results = {
            'homepage': False,
            'driver_setup': False,
            'login': False,
            'account_pages': {},
            'bid_extraction': []
        }
        
        try:
            # Test 1: Driver setup
            if self.setup_driver(headless=False):  # Visible browser for testing
                results['driver_setup'] = True
                
                # Test 2: Homepage
                if self.test_homepage():
                    results['homepage'] = True
                    
                    # Test 3: Login
                    if self.test_login():
                        results['login'] = True
                        
                        # Test 4: Account pages
                        results['account_pages'] = self.test_account_pages()
                        
                        # Test 5: Bid data extraction
                        results['bid_extraction'] = self.extract_bid_data()
        
        except Exception as e:
            self.logger.error(f"❌ Test suite failed: {e}")
        
        finally:
            self.cleanup()
        
        # Print results
        self.print_results(results)
        return results
    
    def print_results(self, results):
        """Print test results summary."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 TEST RESULTS SUMMARY")
        self.logger.info("=" * 60)
        
        self.logger.info(f"✅ Driver Setup: {'PASS' if results['driver_setup'] else 'FAIL'}")
        self.logger.info(f"✅ Homepage Access: {'PASS' if results['homepage'] else 'FAIL'}")
        self.logger.info(f"✅ Login: {'PASS' if results['login'] else 'FAIL'}")
        
        if results['account_pages']:
            self.logger.info("✅ Account Pages:")
            for page, status in results['account_pages'].items():
                self.logger.info(f"   {page}: {'PASS' if status else 'FAIL'}")
        
        self.logger.info(f"✅ Bid Data Extraction: Found {len(results['bid_extraction'])} potential elements")
        
        # Overall assessment
        critical_tests = [results['driver_setup'], results['homepage'], results['login']]
        if all(critical_tests):
            self.logger.info("\n🎉 CRITICAL TESTS PASSED - Ready for live monitoring!")
        else:
            self.logger.info("\n❌ SOME CRITICAL TESTS FAILED - Check issues above")


def main():
    """Main test function."""
    print("🎯 JOHN PYE AUCTIONS - LIVE CONNECTION TEST")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This test will open a browser window to test the live connection")
    print()
    
    # Check credentials
    username = os.getenv('JOHNPYE_USERNAME')
    password = os.getenv('JOHNPYE_PASSWORD')
    
    if not username or not password:
        print("❌ CREDENTIALS MISSING!")
        print("Please ensure JOHNPYE_USERNAME and JOHNPYE_PASSWORD are set in .env")
        return False
    
    print(f"✅ Using credentials: {username[:3]}...@{username.split('@')[1] if '@' in username else 'unknown'}")
    print()
    
    # Run test
    test = LiveConnectionTest()
    results = test.run_full_test()
    
    # Return success status
    critical_tests = [results['driver_setup'], results['homepage'], results['login']]
    return all(critical_tests)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)