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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
        
        try:
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            self.logger.info("WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise
            
    def login(self) -> bool:
        """Log into John Pye Auctions website."""
        try:
            login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn?returnUrl=%2F"
            self.driver.get(login_url)
            
            # Wait for login form to load
            wait = WebDriverWait(self.driver, 10)
            
            # Find and fill username field
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "UserName"))
            )
            username_field.send_keys(self.config.get_username())
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "Password")
            password_field.send_keys(self.config.get_password())
            
            # Submit login form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            login_button.click()
            
            # Wait for redirect after successful login
            wait.until(EC.url_changes(login_url))
            
            # Check if login was successful
            if "Account/LogOn" not in self.driver.current_url:
                self.logger.info("Login successful")
                return True
            else:
                self.logger.error("Login failed - still on login page")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
            
    def get_watchlist_items(self) -> List[AuctionItem]:
        """Retrieve all items from the user's watchlist."""
        watchlist_items = []
        
        try:
            # Navigate to watchlist page
            watchlist_url = "https://www.johnpyeauctions.co.uk/Account/Watchlist"
            self.driver.get(watchlist_url)
            
            wait = WebDriverWait(self.driver, 10)
            
            # Wait for watchlist items to load
            items = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "watchlist-item"))
            )
            
            for item_element in items:
                try:
                    auction_item = self.parse_watchlist_item(item_element)
                    if auction_item:
                        watchlist_items.append(auction_item)
                except Exception as e:
                    self.logger.warning(f"Failed to parse watchlist item: {e}")
                    
            self.logger.info(f"Retrieved {len(watchlist_items)} watchlist items")
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve watchlist: {e}")
            
        return watchlist_items
        
    def parse_watchlist_item(self, item_element) -> Optional[AuctionItem]:
        """Parse a single watchlist item element into an AuctionItem object."""
        try:
            # Extract item details (this will need to be adjusted based on actual HTML structure)
            title = item_element.find_element(By.CLASS_NAME, "item-title").text
            lot_number = item_element.find_element(By.CLASS_NAME, "lot-number").text
            current_bid = item_element.find_element(By.CLASS_NAME, "current-bid").text
            end_time = item_element.find_element(By.CLASS_NAME, "end-time").text
            item_url = item_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            return AuctionItem(
                title=title,
                lot_number=lot_number,
                current_bid=current_bid,
                end_time=end_time,
                url=item_url
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse item element: {e}")
            return None
            
    def monitor_watchlist(self):
        """Main monitoring loop for watchlist items."""
        if not self.setup_driver():
            return
            
        try:
            if not self.login():
                self.logger.error("Cannot proceed without successful login")
                return
                
            while True:
                try:
                    watchlist_items = self.get_watchlist_items()
                    
                    for item in watchlist_items:
                        self.check_item_updates(item)
                        
                    # Save data
                    self.save_watchlist_data(watchlist_items)
                    
                    # Wait before next check
                    check_interval = self.config.get_check_interval()
                    self.logger.info(f"Waiting {check_interval} seconds before next check...")
                    time.sleep(check_interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("Monitoring stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Wait before retrying
                    
        finally:
            if self.driver:
                self.driver.quit()
                
    def check_item_updates(self, item: AuctionItem):
        """Check for updates on a specific auction item."""
        # This method would check for bid changes, time remaining updates, etc.
        # Implementation depends on specific requirements
        pass
        
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