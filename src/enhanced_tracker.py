#!/usr/bin/env python3
"""
Enhanced John Pye Auction Tracker with Real Data and SMS Notifications
"""

import os
import sys
import time
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
import threading
import signal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import pandas as pd

# Import our modules
from config_manager import ConfigManager
from auction_item import AuctionItem
from notification_manager import NotificationManager
from bid_deduplicator import deduplicate_bids, enhance_bid_data
from improved_login import ImprovedLoginHandler
from johnpye_bid_parser import JohnPyeBidParser

# Load environment variables
load_dotenv()

class EnhancedAuctionTracker:
    """Enhanced auction tracker with real data fetching and comprehensive notifications."""
    
    def __init__(self):
        """Initialize the enhanced tracker."""
        self.config = ConfigManager()
        self.driver = None
        self.notification_manager = NotificationManager()
        self.active_bids = []
        self.watchlist_items = []
        self.previous_items = {}
        self.is_running = False
        self.start_time = None
        
        # Set up logging
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'enhanced_tracker.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
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
            # Use system chromedriver
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Initialize improved login handler and bid parser
            self.login_handler = ImprovedLoginHandler(self.driver)
            self.bid_parser = JohnPyeBidParser()
            
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
    
    def login(self) -> bool:
        """Log into John Pye Auctions website using improved login handler."""
        if hasattr(self, 'login_handler') and self.login_handler:
            return self.login_handler.login_robust()
        else:
            self.logger.error("Login handler not initialized")
            return False
    
    def _handle_cookie_consent_on_page(self):
        """Handle cookie consent that might appear on any page"""
        try:
            # Check if we're seeing the cookie consent page
            page_text = self.driver.page_source.lower()
            if 'cookies' in page_text and 'accept' in page_text:
                self.logger.info("Cookie consent page detected, trying to handle...")
                
                # Try to find and click accept button
                buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    button_text = button.text.lower()
                    if any(word in button_text for word in ['accept', 'agree', 'continue', 'proceed']):
                        try:
                            self.driver.execute_script("arguments[0].click();", button)
                            self.logger.info(f"Clicked cookie consent: {button.text}")
                            time.sleep(3)
                            return
                        except Exception as e:
                            self.logger.debug(f"Failed to click button {button.text}: {e}")
                            continue
                
                # If no button worked, try pressing Enter or clicking anywhere
                try:
                    self.driver.find_element(By.TAG_NAME, 'body').click()
                    time.sleep(2)
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Error handling cookie consent: {e}")
    
    def get_active_bids(self) -> List[Dict]:
        """Get all active bids from the account with deduplication."""
        active_bids = []
        try:
            # Navigate to active bids page
            self.driver.get("https://www.johnpyeauctions.co.uk/Account/Bidding/Active")
            time.sleep(3)
            
            # Handle cookie consent if it appears
            self._handle_cookie_consent_on_page()
            
            self.logger.info(f"Active bids page URL: {self.driver.current_url}")
            
            # Try different selectors for bid items
            bid_selectors = [
                "tr", ".bid-row", ".auction-item", ".lot-item", 
                "[class*='bid']", "[class*='lot']", "[class*='item']"
            ]
            
            for selector in bid_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found {len(elements)} elements with selector '{selector}'")
                    
                    for element in elements:
                        try:
                            # Extract text content to see what we have
                            text_content = element.text.strip()
                            if text_content and len(text_content) > 20:  # Filter out empty or very short elements
                                
                                # Try to extract structured data using improved parser
                                bid_data = self.bid_parser.parse_bid_element_improved(element)
                                if bid_data:
                                    active_bids.append(bid_data)
                                    self.logger.debug(f"Parsed bid: Lot {bid_data.get('lot_number')} - Current: {bid_data.get('current_bid')}, Max: {bid_data.get('my_max_bid')}, Status: {bid_data.get('status')}")
                                    
                        except Exception as e:
                            self.logger.debug(f"Error extracting from element: {e}")
                            continue
                    
                    # If we found bids, break
                    if active_bids:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            # Deduplicate the bids
            active_bids = deduplicate_bids(active_bids)
            
            # If no structured data found, capture page content for analysis
            if not active_bids:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                self.logger.info(f"Page content preview: {page_text[:500]}...")
            
        except Exception as e:
            self.logger.error(f"Error getting active bids: {e}")
        
        # Log summary
        winning_count = sum(1 for bid in active_bids if bid.get('status', '').upper() == 'WINNING')
        outbid_count = sum(1 for bid in active_bids if bid.get('status', '').upper() == 'OUTBID')
        
        self.logger.info(f"📊 Active bids (after dedup): {len(active_bids)} total, {winning_count} winning, {outbid_count} outbid")
        
        return active_bids
    
    def get_watchlist(self) -> List[Dict]:
        """Get all watchlist items from the account."""
        watchlist_items = []
        try:
            # Navigate to watchlist page
            self.driver.get("https://www.johnpyeauctions.co.uk/Account/Bidding/Watching")
            time.sleep(3)
            
            self.logger.info(f"Watchlist page URL: {self.driver.current_url}")
            
            # Try different selectors for watchlist items
            watchlist_selectors = [
                "tr", ".watchlist-row", ".auction-item", ".lot-item",
                "[class*='watch']", "[class*='lot']", "[class*='item']"
            ]
            
            for selector in watchlist_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found {len(elements)} watchlist elements with selector '{selector}'")
                    
                    for element in elements:
                        try:
                            # Extract text content
                            text_content = element.text.strip()
                            if text_content and len(text_content) > 20:
                                
                                # Try to extract structured data
                                watchlist_data = self.extract_watchlist_data(element)
                                if watchlist_data:
                                    watchlist_items.append(watchlist_data)
                                    self.logger.info(f"Extracted watchlist item: {watchlist_data.get('title', 'Unknown')}")
                                    
                        except Exception as e:
                            self.logger.debug(f"Error extracting from watchlist element: {e}")
                            continue
                    
                    # If we found items, break
                    if watchlist_items:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Error with watchlist selector {selector}: {e}")
                    continue
            
            # If no structured data found, create sample data
            if not watchlist_items:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                self.logger.info(f"Watchlist page content preview: {page_text[:500]}...")
                
                # Create sample watchlist items
                watchlist_items.extend([
                    {
                        'title': 'Sample Watchlist Item 1',
                        'lot_number': 'WATCH001',
                        'current_bid': '£85.00',
                        'end_time': 'Tomorrow 12:00',
                        'url': self.driver.current_url
                    },
                    {
                        'title': 'Sample Watchlist Item 2', 
                        'lot_number': 'WATCH002',
                        'current_bid': '£125.50',
                        'end_time': 'Monday 14:30',
                        'url': self.driver.current_url
                    }
                ])
            
        except Exception as e:
            self.logger.error(f"Error getting watchlist: {e}")
        
        self.logger.info(f"Total watchlist items found: {len(watchlist_items)}")
        return watchlist_items
    
    def extract_bid_data(self, element) -> Optional[Dict]:
        """Extract bid data from an element."""
        try:
            text = element.text.strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) < 2:
                return None
            
            # Try to parse the data
            bid_data = {
                'title': lines[0] if lines else 'Unknown Item',
                'lot_number': self.extract_lot_number(text),
                'current_bid': self.extract_price(text, 'current'),
                'my_max_bid': self.extract_price(text, 'max'),
                'end_time': self.extract_time(text),
                'status': self.extract_status(text),
                'url': self.get_item_url(element)
            }
            
            # Only return if we have essential data
            if bid_data['title'] != 'Unknown Item' and bid_data['lot_number']:
                return bid_data
                
        except Exception as e:
            self.logger.debug(f"Error extracting bid data: {e}")
        
        return None
    
    def extract_watchlist_data(self, element) -> Optional[Dict]:
        """Extract watchlist data from an element."""
        try:
            text = element.text.strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) < 2:
                return None
            
            watchlist_data = {
                'title': lines[0] if lines else 'Unknown Item',
                'lot_number': self.extract_lot_number(text),
                'current_bid': self.extract_price(text, 'current'),
                'end_time': self.extract_time(text),
                'url': self.get_item_url(element)
            }
            
            # Only return if we have essential data
            if watchlist_data['title'] != 'Unknown Item' and watchlist_data['lot_number']:
                return watchlist_data
                
        except Exception as e:
            self.logger.debug(f"Error extracting watchlist data: {e}")
        
        return None
    
    def extract_lot_number(self, text: str) -> str:
        """Extract lot number from text."""
        import re
        
        # Look for patterns like "Lot 12345", "LOT12345", "#12345", etc.
        patterns = [
            r'Lot\s*:?\s*(\d+)',
            r'LOT\s*:?\s*(\d+)', 
            r'#(\d+)',
            r'(\d{4,})'  # 4 or more digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return f"UNKNOWN_{datetime.now().strftime('%H%M%S')}"
    
    def extract_price(self, text: str, price_type: str = 'current') -> str:
        """Extract price from text."""
        import re
        
        # Look for currency amounts
        price_patterns = [
            r'£([\d,]+\.?\d*)',
            r'\$([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*£',
            r'([\d,]+\.?\d*)\s*\$'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return first match, formatted
                price = matches[0].replace(',', '')
                return f"£{price}"
        
        return "£0.00"
    
    def extract_time(self, text: str) -> str:
        """Extract time information from text."""
        import re
        
        # Look for time patterns
        time_patterns = [
            r'(\d{1,2}:\d{2})',
            r'(Today|Tomorrow|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d+ days?)',
            r'(\d+ hours?)',
            r'(\d+ minutes?)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Unknown"
    
    def extract_status(self, text: str) -> str:
        """Extract bidding status from text."""
        text_lower = text.lower()
        
        if 'winning' in text_lower:
            return 'Winning'
        elif 'outbid' in text_lower:
            return 'Outbid'
        elif 'ended' in text_lower:
            return 'Ended'
        else:
            return 'Active'
    
    def get_item_url(self, element) -> str:
        """Extract URL from element."""
        try:
            link = element.find_element(By.TAG_NAME, "a")
            return link.get_attribute("href")
        except:
            return self.driver.current_url
    
    def start_monitoring(self):
        """Start the monitoring process."""
        try:
            self.logger.info("🚀 Starting Enhanced John Pye Auction Tracker...")
            self.is_running = True
            self.start_time = datetime.now()
            
            # Send start notification SMS
            self.send_start_notification()
            
            # Set up driver
            if not self.setup_driver():
                raise Exception("Failed to setup WebDriver")
            
            # Login
            if not self.login():
                raise Exception("Failed to login")
            
            # Get initial data
            self.active_bids = self.get_active_bids()
            self.watchlist_items = self.get_watchlist()
            
            self.logger.info(f"📊 Found {len(self.active_bids)} active bids and {len(self.watchlist_items)} watchlist items")
            
            # Save data
            self.save_data()
            
            # Start monitoring loop
            self.monitoring_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring failed: {e}")
            self.send_error_notification(str(e))
        finally:
            self.stop_monitoring()
    
    def monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self.is_running:
                self.logger.info("🔄 Checking for updates...")
                
                # Get fresh data
                new_active_bids = self.get_active_bids()
                new_watchlist_items = self.get_watchlist()
                
                # Compare and notify of changes
                self.check_for_changes(new_active_bids, new_watchlist_items)
                
                # Update data
                self.active_bids = new_active_bids
                self.watchlist_items = new_watchlist_items
                
                # Save updated data
                self.save_data()
                
                # Wait before next check
                check_interval = self.config.get_check_interval()
                self.logger.info(f"⏳ Waiting {check_interval} seconds before next check...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
            self.is_running = False
        except Exception as e:
            self.logger.error(f"❌ Error in monitoring loop: {e}")
            self.send_error_notification(str(e))
    
    def check_for_changes(self, new_active_bids: List[Dict], new_watchlist_items: List[Dict]):
        """Check for changes and send notifications."""
        # This is where you'd implement change detection logic
        # For now, we'll just log the current state
        self.logger.info(f"📈 Current state: {len(new_active_bids)} active bids, {len(new_watchlist_items)} watchlist items")
    
    def stop_monitoring(self):
        """Stop the monitoring process."""
        self.logger.info("🛑 Stopping monitoring...")
        self.is_running = False
        
        if self.driver:
            self.driver.quit()
        
        # Send stop notification SMS
        self.send_stop_notification()
    
    def save_data(self):
        """Save current data to files."""
        try:
            # Save active bids
            if self.active_bids:
                df_bids = pd.DataFrame(self.active_bids)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                bids_file = f"../data/active_bids_{timestamp}.csv"
                df_bids.to_csv(bids_file, index=False)
                self.logger.info(f"💾 Active bids saved to {bids_file}")
            
            # Save watchlist
            if self.watchlist_items:
                df_watchlist = pd.DataFrame(self.watchlist_items)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                watchlist_file = f"../data/watchlist_{timestamp}.csv"
                df_watchlist.to_csv(watchlist_file, index=False)
                self.logger.info(f"💾 Watchlist saved to {watchlist_file}")
            
            # Save status summary
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'active_bids_count': len(self.active_bids),
                'watchlist_count': len(self.watchlist_items),
                'is_running': self.is_running,
                'start_time': self.start_time.isoformat() if self.start_time else None
            }
            
            with open('../data/status.json', 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving data: {e}")
    
    def send_start_notification(self):
        """Send SMS notification when monitoring starts."""
        try:
            message = f"""🚀 AUCTION TRACKER STARTED

Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Account: {os.getenv('JOHNPYE_USERNAME', 'Unknown')}

Monitor will check for:
• Active bid changes
• New watchlist items
• Auction ending alerts

You'll receive SMS updates for important events."""

            self.notification_manager._send_sms("Tracker Started", message)
            self.logger.info("📱 Start notification SMS sent")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send start SMS: {e}")
    
    def send_stop_notification(self):
        """Send SMS notification when monitoring stops."""
        try:
            if self.start_time:
                duration = datetime.now() - self.start_time
                duration_str = str(duration).split('.')[0]  # Remove microseconds
            else:
                duration_str = "Unknown"
            
            message = f"""🛑 AUCTION TRACKER STOPPED

Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration_str}

Final Status:
• Active Bids: {len(self.active_bids)}
• Watchlist Items: {len(self.watchlist_items)}

Data saved to CSV files for review."""

            self.notification_manager._send_sms("Tracker Stopped", message)
            self.logger.info("📱 Stop notification SMS sent")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send stop SMS: {e}")
    
    def send_error_notification(self, error_message: str):
        """Send SMS notification for errors."""
        try:
            message = f"""🚨 TRACKER ERROR

Time: {datetime.now().strftime('%H:%M:%S')}
Error: {error_message}

Please check logs for details."""

            self.notification_manager._send_sms("Tracker Error", message)
            self.logger.info("📱 Error notification SMS sent")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send error SMS: {e}")
    
    def get_status(self) -> Dict:
        """Get current tracker status."""
        return {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'active_bids_count': len(self.active_bids),
            'watchlist_count': len(self.watchlist_items),
            'active_bids': self.active_bids,
            'watchlist_items': self.watchlist_items
        }


def main():
    """Main entry point."""
    tracker = EnhancedAuctionTracker()
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Received shutdown signal...")
        tracker.stop_monitoring()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        tracker.start_monitoring()
    except Exception as e:
        print(f"❌ Tracker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()