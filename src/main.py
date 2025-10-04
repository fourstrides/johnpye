#!/usr/bin/env python3
"""
John Pye Auctions Watchlist Tracker

This application logs into John Pye Auctions, monitors your watchlist,
and tracks bidding activity on watched items.
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import pandas as pd

from config_manager import ConfigManager
from auction_item import AuctionItem
from notification_manager import NotificationManager


class JohnPyeAuctionTracker:
    """Main class for tracking John Pye Auctions watchlist items."""
    
    def __init__(self):
        """Initialize the auction tracker."""
        load_dotenv()
        self.config = ConfigManager()
        self.driver = None
        self.notification_manager = NotificationManager()
        self.previous_items = {}  # Store previous item states for comparison
        self.dashboard = None  # Will be set if web dashboard is enabled
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/auction_tracker.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self, headless: bool = True):
        """Set up Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        # Anti-detection measures
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # Set the binary location for Chromium
        chrome_options.binary_location = '/usr/bin/chromium-browser'
        
        try:
            # Use system chromedriver with Service class (Selenium 4.x)
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            return False
            
    def wait_for_cloudflare(self, timeout=45) -> bool:
        """Wait for Cloudflare protection to clear."""
        self.logger.info("Waiting for Cloudflare protection to clear...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_title = self.driver.title
            if "Just a moment" not in current_title and current_title.strip():
                self.logger.info("Cloudflare protection cleared")
                return True
            time.sleep(2)
        
        self.logger.warning("Cloudflare protection did not clear within timeout")
        return False
    
    def handle_page_overlays(self):
        """Handle common page overlays like cookie consent, popups, etc."""
        try:
            # Wait a bit for overlays to appear
            time.sleep(2)
            
            # Common overlay selectors to close
            overlay_selectors = [
                "button:contains('Accept')",
                "button:contains('OK')",
                "button:contains('Close')",
                ".close-button",
                ".modal-close",
                "[data-dismiss='modal']",
                ".cookie-accept",
                ".accept-cookies"
            ]
            
            for selector in overlay_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            self.logger.info(f"Closed overlay using selector: {selector}")
                            time.sleep(1)
                            break
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error handling overlays: {e}")
    
    def login(self) -> bool:
        """Log into John Pye Auctions website."""
        try:
            login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn"
            self.driver.get(login_url)
            
            # Wait for Cloudflare protection to clear
            if not self.wait_for_cloudflare():
                self.logger.error("Could not bypass Cloudflare protection")
                return False
            
            # Handle any page overlays
            self.handle_page_overlays()
            
            # Wait for login form to load
            wait = WebDriverWait(self.driver, 15)
            
            # Find and fill username field with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    username_field = wait.until(
                        EC.element_to_be_clickable((By.ID, "username"))
                    )
                    username_field.clear()
                    username_field.send_keys(self.config.get_username())
                    self.logger.info("Username entered successfully")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(2)
            
            # Find and fill password field with retry logic
            for attempt in range(max_retries):
                try:
                    password_field = wait.until(
                        EC.element_to_be_clickable((By.ID, "password"))
                    )
                    password_field.clear()
                    password_field.send_keys(self.config.get_password())
                    self.logger.info("Password entered successfully")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(2)
            
            # Handle both Remember Me and Terms & Conditions checkboxes
            try:
                # Find all checkboxes on the page
                checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                self.logger.info(f"Found {len(checkboxes)} checkboxes on login page")
                
                for i, checkbox in enumerate(checkboxes):
                    try:
                        if checkbox.is_displayed() and checkbox.is_enabled():
                            if not checkbox.is_selected():
                                # Use JavaScript click to avoid interception issues
                                self.driver.execute_script("arguments[0].click();", checkbox)
                                self.logger.info(f"Checkbox {i+1} checked via JavaScript")
                            else:
                                self.logger.info(f"Checkbox {i+1} was already selected")
                    except Exception as e:
                        self.logger.debug(f"Could not interact with checkbox {i+1}: {e}")
                        
            except Exception as e:
                self.logger.debug(f"Error handling checkboxes: {e}")
            
            # Try multiple methods to submit the form
            submitted = False
            
            # Method 1: Click submit button with JavaScript if intercepted
            try:
                submit_button = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input.buttonbox[type='submit']"))
                )
                # Use JavaScript click if regular click is intercepted
                self.driver.execute_script("arguments[0].click();", submit_button)
                self.logger.info("Login submitted via JavaScript click")
                submitted = True
            except Exception as e:
                self.logger.warning(f"JavaScript click failed: {e}")
            
            # Method 2: Submit form directly if button click failed
            if not submitted:
                try:
                    form = self.driver.find_element(By.TAG_NAME, "form")
                    form.submit()
                    self.logger.info("Login submitted via form submission")
                    submitted = True
                except Exception as e:
                    self.logger.warning(f"Form submission failed: {e}")
            
            # Method 3: Press Enter key in password field
            if not submitted:
                try:
                    password_field.send_keys(Keys.RETURN)
                    self.logger.info("Login submitted via Enter key")
                    submitted = True
                except Exception as e:
                    self.logger.warning(f"Enter key submission failed: {e}")
            
            if not submitted:
                self.logger.error("Could not submit login form")
                return False
            
            # Wait for redirect after successful login
            try:
                wait.until(EC.url_changes(login_url), timeout=10)
            except:
                self.logger.warning("URL did not change after login attempt")
            
            # Wait a bit more for page to fully load
            time.sleep(3)
            
            # Check if login was successful
            current_url = self.driver.current_url
            self.logger.info(f"Current URL after login: {current_url}")
            
            if "Account/LogOn" not in current_url:
                self.logger.info("Login successful")
                return True
            else:
                # Check if there are any error messages on the page
                page_source = self.driver.page_source.lower()
                if "invalid" in page_source or "incorrect" in page_source or "error" in page_source:
                    self.logger.error("Login failed - invalid credentials or error on page")
                else:
                    self.logger.error("Login failed - still on login page")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
            
    def get_watchlist_items(self) -> List[AuctionItem]:
        """Retrieve all items from the user's watchlist and bidding items."""
        watchlist_items = []
        
        try:
            # Navigate to the correct watchlist/bidding page
            watchlist_url = "https://www.johnpyeauctions.co.uk/Account/Bidding/Watching"
            self.driver.get(watchlist_url)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if we successfully reached the page
            current_url = self.driver.current_url
            if "NotFound" in current_url:
                self.logger.error(f"Watchlist page not found: {current_url}")
                return watchlist_items
            
            self.logger.info(f"Successfully navigated to watchlist page: {current_url}")
            
            # Look for various selectors that might contain watchlist items
            item_selectors = [
                ".watchlist-item", ".bid-item", ".auction-item", ".lot-item",
                "[class*='watchlist']", "[class*='bidding']", "[class*='auction']", 
                "[class*='lot']", "[class*='item']", "tr", ".listing", ".card"
            ]
            
            for selector in item_selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items and len(items) > 0:
                        self.logger.info(f"Found {len(items)} elements with selector: {selector}")
                        
                        for item_element in items:
                            try:
                                auction_item = self.parse_watchlist_item(item_element)
                                if auction_item:
                                    watchlist_items.append(auction_item)
                            except Exception as e:
                                self.logger.debug(f"Failed to parse item: {e}")
                        
                        # If we found items with this selector, break
                        if watchlist_items:
                            break
                            
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {e}")
                    continue
                    
            self.logger.info(f"Retrieved {len(watchlist_items)} watchlist items")
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve watchlist: {e}")
            
        return watchlist_items
        
    def parse_watchlist_item(self, item_element) -> Optional[AuctionItem]:
        """Parse a single watchlist item element into an AuctionItem object."""
        try:
            # Multiple selectors for title - try in order of preference
            title_selectors = [
                ".item-title", ".lot-title", ".title", "h3", "h2", "h4", 
                "[class*='title']", "[class*='name']", "[data-title]", "strong"
            ]
            title = self.extract_text_by_selectors(item_element, title_selectors, "Unknown Item")
            
            # Multiple selectors for lot number
            lot_selectors = [
                ".lot-number", ".lot", ".lot-id", "[class*='lot']", 
                "[data-lot]", ".item-id", "[class*='id']", "span"
            ]
            lot_number = self.extract_text_by_selectors(item_element, lot_selectors, "Unknown")
            
            # Clean up lot number (remove "Lot " prefix if present)
            lot_number = lot_number.replace("Lot ", "").replace("#", "").strip()
            
            # Multiple selectors for current bid
            bid_selectors = [
                ".current-bid", ".bid", ".price", ".amount", "[class*='bid']", 
                "[class*='price']", "[data-price]", ".cost", "[class*='amount']"
            ]
            current_bid = self.extract_text_by_selectors(item_element, bid_selectors, "£0.00")
            
            # Clean up bid amount
            current_bid = self.clean_bid_amount(current_bid)
            
            # Multiple selectors for end time
            time_selectors = [
                ".end-time", ".time", ".ends", ".ending", "[class*='time']", 
                "[class*='end']", "[data-time]", ".date", "[class*='date']", "time"
            ]
            end_time = self.extract_text_by_selectors(item_element, time_selectors, "Unknown")
            
            # Multiple selectors for item URL
            url_selectors = ["a[href*='lot']", "a[href*='item']", "a[href*='auction']", "a"]
            item_url = self.extract_link_by_selectors(item_element, url_selectors)
            
            # Only create item if we have essential data
            if title and title != "Unknown Item" and lot_number and lot_number != "Unknown":
                return AuctionItem(
                    title=title.strip(),
                    lot_number=lot_number.strip(),
                    current_bid=current_bid.strip(),
                    end_time=end_time.strip(),
                    url=item_url or ""
                )
            else:
                self.logger.debug(f"Insufficient data for item: title={title}, lot={lot_number}")
                return None
            
        except Exception as e:
            self.logger.warning(f"Failed to parse item element: {e}")
            return None
    
    def extract_text_by_selectors(self, element, selectors: List[str], default: str = "") -> str:
        """Try multiple CSS selectors to extract text, return first successful match."""
        for selector in selectors:
            try:
                found_element = element.find_element(By.CSS_SELECTOR, selector)
                text = found_element.text.strip()
                if text:  # Only return non-empty text
                    return text
            except:
                continue
        
        # If no selector worked, try getting text content from the element itself
        try:
            text = element.text.strip()
            if text:
                return text
        except:
            pass
            
        return default
    
    def extract_link_by_selectors(self, element, selectors: List[str]) -> Optional[str]:
        """Try multiple CSS selectors to extract href attribute."""
        for selector in selectors:
            try:
                found_element = element.find_element(By.CSS_SELECTOR, selector)
                href = found_element.get_attribute("href")
                if href:
                    return href
            except:
                continue
        return None
    
    def clean_bid_amount(self, bid_text: str) -> str:
        """Clean and standardize bid amount text."""
        if not bid_text:
            return "£0.00"
            
        # Remove extra whitespace and common prefixes
        bid_text = bid_text.strip()
        bid_text = bid_text.replace("Current bid:", "").replace("Bid:", "").replace("Price:", "")
        bid_text = bid_text.replace("Starting at", "").replace("From", "")
        
        # If no currency symbol, assume GBP and add £
        if not any(symbol in bid_text for symbol in ["£", "$", "€", "¥"]):
            # Try to extract number and add £
            import re
            numbers = re.findall(r'[0-9,]+\.?[0-9]*', bid_text)
            if numbers:
                return f"£{numbers[0]}"
            return "£0.00"
        
        return bid_text.strip()
            
    def monitor_watchlist(self):
        """Main monitoring loop for watchlist items."""
        if not self.setup_driver():
            return
            
        try:
            if not self.login():
                self.logger.error("Cannot proceed without successful login")
                return
                
            # Send monitoring started notification
            self.notification_manager.notify_monitoring_started()
            
            # Update dashboard status if available
            if self.dashboard:
                self.dashboard.update_monitoring_status(True, datetime.now().isoformat())
            
            while True:
                try:
                    watchlist_items = self.get_watchlist_items()
                    
                    # Update dashboard with current watchlist
                    if self.dashboard:
                        self.dashboard.update_watchlist(watchlist_items)
                    
                    # Get current lot numbers for cleanup
                    current_lot_numbers = [item.lot_number for item in watchlist_items]
                    
                    # Check each item for updates
                    for item in watchlist_items:
                        self.check_item_updates(item)
                    
                    # Clean up removed items
                    self.cleanup_old_items(current_lot_numbers)
                        
                    # Save data
                    self.save_watchlist_data(watchlist_items)
                    
                    # Wait before next check
                    check_interval = self.config.get_check_interval()
                    self.logger.info(f"Waiting {check_interval} seconds before next check...")
                    time.sleep(check_interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("Monitoring stopped by user")
                    self.notification_manager.notify_monitoring_stopped("Stopped by user")
                    
                    if self.dashboard:
                        self.dashboard.update_monitoring_status(False)
                    break
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    self.notification_manager.notify_error(str(e), "Monitoring loop error")
                    time.sleep(60)  # Wait before retrying
                    
        finally:
            if self.driver:
                self.driver.quit()
                
            # Final notification
            self.notification_manager.notify_monitoring_stopped("Application shutdown")
            
            if self.dashboard:
                self.dashboard.update_monitoring_status(False)
                
    def check_item_updates(self, item: AuctionItem):
        """Check for updates on a specific auction item."""
        try:
            # Check if we have a previous version of this item
            previous_item = self.get_previous_item(item.lot_number)
            
            if previous_item:
                # Check for bid increases
                if item.has_bid_increased(previous_item):
                    bid_increase = item.parse_bid_amount() - previous_item.parse_bid_amount()
                    threshold = self.config.config.get('notifications', {}).get('bid_increase_threshold', 10.0)
                    
                    if bid_increase >= threshold:
                        self.logger.info(f"Significant bid increase detected for lot {item.lot_number}: £{bid_increase:.2f}")
                        self.notification_manager.notify_bid_increase(item, previous_item)
                        
                        # Update dashboard if available
                        if hasattr(self, 'dashboard'):
                            self.dashboard.add_bid_history(item, 'bid_increase', f'Increased by £{bid_increase:.2f}')
                            self.dashboard.increment_notifications()
                
                # Check if item title or details changed
                if item.title != previous_item.title:
                    self.logger.info(f"Item title changed for lot {item.lot_number}")
                    if hasattr(self, 'dashboard'):
                        self.dashboard.add_bid_history(item, 'item_updated', 'Title or details changed')
            
            else:
                # This is a new item
                self.logger.info(f"New item detected: {item.title} (Lot {item.lot_number})")
                self.notification_manager.notify_new_watchlist_item(item)
                
                if hasattr(self, 'dashboard'):
                    self.dashboard.add_bid_history(item, 'new_item', 'Added to watchlist')
                    self.dashboard.increment_notifications()
            
            # Check if auction is ending soon
            if item.is_ending_soon():
                ending_threshold = self.config.config.get('notifications', {}).get('ending_soon_threshold_minutes', 60)
                self.logger.info(f"Auction ending soon for lot {item.lot_number}")
                self.notification_manager.notify_auction_ending_soon(item, ending_threshold)
                
                if hasattr(self, 'dashboard'):
                    self.dashboard.add_bid_history(item, 'ending_soon', f'Ending within {ending_threshold} minutes')
                    self.dashboard.increment_notifications()
            
            # Update the stored item information
            self.store_item(item)
            
        except Exception as e:
            self.logger.error(f"Error checking updates for item {item.lot_number}: {e}")
        
    def save_watchlist_data(self, items: List[AuctionItem]):
        """Save current watchlist data to file."""
        try:
            data = [item.to_dict() for item in items]
            df = pd.DataFrame(data)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../data/watchlist_{timestamp}.csv"
            
            df.to_csv(filename, index=False)
            self.logger.info(f"Watchlist data saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save watchlist data: {e}")
    
    def get_previous_item(self, lot_number: str) -> Optional[AuctionItem]:
        """Get the previously stored version of an item."""
        return self.previous_items.get(lot_number)
    
    def store_item(self, item: AuctionItem):
        """Store an item for future comparison."""
        self.previous_items[item.lot_number] = item
    
    def cleanup_old_items(self, current_lot_numbers: List[str]):
        """Remove items that are no longer in the watchlist."""
        removed_lot_numbers = set(self.previous_items.keys()) - set(current_lot_numbers)
        
        for lot_number in removed_lot_numbers:
            removed_item = self.previous_items.pop(lot_number, None)
            if removed_item:
                self.logger.info(f"Item removed from watchlist: {removed_item.title} (Lot {lot_number})")
                self.notification_manager.notify_watchlist_item_removed(removed_item)
                
                if self.dashboard:
                    self.dashboard.add_bid_history(removed_item, 'item_removed', 'Removed from watchlist')
                    self.dashboard.increment_notifications()
    
    def set_dashboard(self, dashboard):
        """Set the web dashboard instance for integration."""
        self.dashboard = dashboard


def main():
    """Main entry point of the application."""
    tracker = JohnPyeAuctionTracker()
    
    try:
        tracker.monitor_watchlist()
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()