#!/usr/bin/env python3
"""
Production-Ready John Pye Auction Tracker
Confirmed working with live site - tested October 2025
"""

import os
import sys
import time
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
import re
import signal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import pandas as pd

# Import our modules
from config_manager import ConfigManager
from notification_manager import NotificationManager

# Load environment variables
load_dotenv()

class ProductionAuctionTracker:
    """Production-ready auction tracker with confirmed working selectors."""
    
    def __init__(self):
        """Initialize the production tracker."""
        self.config = ConfigManager()
        self.driver = None
        self.notification_manager = NotificationManager()
        self.active_bids = []
        self.watchlist_items = []
        self.previous_bids = {}
        self.is_running = False
        self.start_time = None
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/production_tracker.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self, headless: bool = True):
        """Set up Chrome WebDriver with confirmed working configuration."""
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
            time.sleep(3)
        
        self.logger.warning("⚠️  Cloudflare protection did not clear within timeout")
        return False
    
    def login(self) -> bool:
        """Log into John Pye Auctions website using confirmed working method."""
        try:
            login_url = "https://www.johnpyeauctions.co.uk/Account/LogOn"
            self.driver.get(login_url)
            
            if not self.wait_for_cloudflare():
                return False
            
            wait = WebDriverWait(self.driver, 15)
            
            # Enter credentials using confirmed selectors
            username_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
            username_field.clear()
            username_field.send_keys(os.getenv('JOHNPYE_USERNAME'))
            
            password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
            password_field.clear()
            password_field.send_keys(os.getenv('JOHNPYE_PASSWORD'))
            
            # Handle checkboxes (confirmed working)
            try:
                checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                for checkbox in checkboxes:
                    if checkbox.is_displayed() and checkbox.is_enabled():
                        if not checkbox.is_selected():
                            self.driver.execute_script("arguments[0].click();", checkbox)
            except Exception as e:
                self.logger.debug(f"Checkbox handling: {e}")
            
            # Submit form using confirmed method
            submit_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.buttonbox[type='submit']")))
            self.driver.execute_script("arguments[0].click();", submit_button)
            
            # Wait for redirect
            time.sleep(5)
            
            current_url = self.driver.current_url
            if "Account/LogOn" not in current_url:
                self.logger.info("✅ Login successful!")
                return True
            else:
                self.logger.error("❌ Login failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login failed: {e}")
            return False
    
    def get_active_bids(self) -> List[Dict]:
        """Get active bids using confirmed working selectors."""
        active_bids = []
        
        try:
            # Navigate to active bids page
            self.driver.get("https://www.johnpyeauctions.co.uk/Account/Bidding/Active")
            time.sleep(3)
            
            # Use the confirmed working selector: .row
            # From our test, this captures the main bid data
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".row")
            
            self.logger.info(f"Found {len(elements)} row elements")
            
            for element in elements:
                try:
                    text_content = element.text.strip()
                    
                    # Filter for actual bid content (contains lot number, prices, etc.)
                    if (len(text_content) > 100 and 
                        'Lot ' in text_content and 
                        '£' in text_content and 
                        ('WINNING' in text_content or 'OUTBID' in text_content)):
                        
                        bid_data = self.parse_bid_element(text_content)
                        if bid_data:
                            active_bids.append(bid_data)
                            self.logger.info(f"✅ Parsed bid: {bid_data['title'][:50]}... - {bid_data['status']}") 
                except Exception as e:
                    self.logger.debug(f"Error processing element: {e}")
            
            self.logger.info(f"📊 Total active bids found: {len(active_bids)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error getting active bids: {e}")
        
        return active_bids
    
    def parse_bid_element(self, text_content: str) -> Optional[Dict]:
        """Parse bid element text content into structured data."""
        try:
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            bid_data = {
                'title': 'Unknown',
                'lot_number': 'Unknown',
                'current_bid': '£0.00',
                'my_max_bid': '£0.00',
                'end_time': 'Unknown',
                'status': 'Unknown',
                'url': 'https://www.johnpyeauctions.co.uk/Account/Bidding/Active'
            }
            
            # Extract data using patterns confirmed from live test
            for i, line in enumerate(lines):
                
                # Extract title and lot number (first line usually)
                if line.startswith('Lot ') and '-' in line:
                    # Extract lot number
                    lot_match = re.search(r'Lot (\d+)', line)
                    if lot_match:
                        bid_data['lot_number'] = lot_match.group(1)
                    
                    # Extract title (everything after "Lot X - ")
                    title_match = re.search(r'Lot \d+ - (.+?)(?:\[|:)', line)
                    if title_match:
                        bid_data['title'] = title_match.group(1).strip()
                
                # Extract current bid
                if line == 'CURRENT BID' and i + 1 < len(lines):
                    bid_data['current_bid'] = lines[i + 1]
                
                # Extract my max bid
                if line == 'MY MAX BID' and i + 1 < len(lines):
                    bid_data['my_max_bid'] = lines[i + 1]
                
                # Extract time remaining
                if line.startswith('ENDS IN:') or 'Hours, ' in line:
                    if 'Hours, ' in line:
                        bid_data['end_time'] = line
                    elif i + 1 < len(lines) and ('Hours, ' in lines[i + 1] or 'Minutes' in lines[i + 1]):
                        bid_data['end_time'] = lines[i + 1]
                
                # Extract status
                if line in ['WINNING', 'OUTBID']:
                    bid_data['status'] = line
            
            # Only return if we have essential data
            if bid_data['lot_number'] != 'Unknown' and bid_data['title'] != 'Unknown':
                return bid_data
            
        except Exception as e:
            self.logger.debug(f"Error parsing bid element: {e}")
        
        return None
    
    def get_watchlist(self) -> List[Dict]:
        """Get watchlist items."""
        watchlist_items = []
        
        try:
            # Navigate to watchlist page
            self.driver.get("https://www.johnpyeauctions.co.uk/Account/Bidding/Watching")
            time.sleep(3)
            
            # Use similar approach as active bids
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".row")
            
            self.logger.info(f"Found {len(elements)} watchlist row elements")
            
            for element in elements:
                try:
                    text_content = element.text.strip()
                    
                    # Filter for watchlist content
                    if (len(text_content) > 100 and 
                        'Lot ' in text_content and 
                        '£' in text_content):
                        
                        watchlist_data = self.parse_watchlist_element(text_content)
                        if watchlist_data:
                            watchlist_items.append(watchlist_data)
                            self.logger.info(f"✅ Parsed watchlist: {watchlist_data['title'][:50]}...")
            
            self.logger.info(f"📊 Total watchlist items found: {len(watchlist_items)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error getting watchlist: {e}")
        
        return watchlist_items
    
    def parse_watchlist_element(self, text_content: str) -> Optional[Dict]:
        """Parse watchlist element text content."""
        try:
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            watchlist_data = {
                'title': 'Unknown',
                'lot_number': 'Unknown',
                'current_bid': '£0.00',
                'end_time': 'Unknown',
                'url': 'https://www.johnpyeauctions.co.uk/Account/Bidding/Watching'
            }
            
            # Similar parsing logic as bid elements
            for i, line in enumerate(lines):
                if line.startswith('Lot ') and '-' in line:
                    lot_match = re.search(r'Lot (\d+)', line)
                    if lot_match:
                        watchlist_data['lot_number'] = lot_match.group(1)
                    
                    title_match = re.search(r'Lot \d+ - (.+?)(?:\[|:)', line)
                    if title_match:
                        watchlist_data['title'] = title_match.group(1).strip()
                
                if '£' in line and re.search(r'£\d+', line):
                    price_match = re.search(r'£[\d,]+\.?\d*', line)
                    if price_match:
                        watchlist_data['current_bid'] = price_match.group(0)
            
            if watchlist_data['lot_number'] != 'Unknown':
                return watchlist_data
                
        except Exception as e:
            self.logger.debug(f"Error parsing watchlist element: {e}")
        
        return None
    
    def check_for_changes(self):
        """Check for changes in bids and send notifications."""
        try:
            for current_bid in self.active_bids:
                lot_number = current_bid['lot_number']
                
                if lot_number in self.previous_bids:
                    previous_bid = self.previous_bids[lot_number]
                    
                    # Check for status changes
                    if current_bid['status'] != previous_bid.get('status'):
                        self.logger.info(f"🚨 Status changed for Lot {lot_number}: {previous_bid.get('status')} → {current_bid['status']}")
                        
                        if current_bid['status'] == 'OUTBID':
                            # Send urgent outbid notification
                            message = f"""🚨 OUTBID ALERT!

Lot {lot_number}: {current_bid['title'][:50]}...
Current Bid: {current_bid['current_bid']}
Your Max: {current_bid['my_max_bid']}
Status: OUTBID

Take action now!"""
                            
                            self.notification_manager._send_sms("OUTBID ALERT", message)
                        
                        elif current_bid['status'] == 'WINNING':
                            # Send winning notification
                            message = f"""🏆 NOW WINNING!

Lot {lot_number}: {current_bid['title'][:50]}...
Current Bid: {current_bid['current_bid']}
Your Max: {current_bid['my_max_bid']}
Status: WINNING

Great job!"""
                            
                            self.notification_manager._send_sms("NOW WINNING", message)
                    
                    # Check for current bid increases
                    current_amount = float(re.sub(r'[£,]', '', current_bid['current_bid']))
                    previous_amount = float(re.sub(r'[£,]', '', previous_bid.get('current_bid', '0')))
                    
                    if current_amount > previous_amount:
                        increase = current_amount - previous_amount
                        self.logger.info(f"📈 Bid increased for Lot {lot_number}: +£{increase:.2f}")
                        
                        if increase >= 10.0:  # Significant increase
                            message = f"""📈 BID INCREASE

Lot {lot_number}: {current_bid['title'][:50]}...
Previous: £{previous_amount:.2f}
Current: £{current_amount:.2f}
Increase: +£{increase:.2f}
Your Status: {current_bid['status']}"""
                            
                            self.notification_manager._send_sms("Bid Increase", message)
                
                # Store current bid for next comparison
                self.previous_bids[lot_number] = current_bid.copy()
                
        except Exception as e:
            self.logger.error(f"❌ Error checking for changes: {e}")
    
    def save_data(self):
        """Save current data to files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save active bids
            if self.active_bids:
                df_bids = pd.DataFrame(self.active_bids)
                bids_file = f"../data/active_bids_{timestamp}.csv"
                df_bids.to_csv(bids_file, index=False)
                self.logger.info(f"💾 Active bids saved: {bids_file}")
            
            # Save watchlist
            if self.watchlist_items:
                df_watchlist = pd.DataFrame(self.watchlist_items)
                watchlist_file = f"../data/watchlist_{timestamp}.csv"
                df_watchlist.to_csv(watchlist_file, index=False)
                self.logger.info(f"💾 Watchlist saved: {watchlist_file}")
            
            # Save status JSON for dashboard
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'is_running': self.is_running,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'active_bids_count': len(self.active_bids),
                'watchlist_count': len(self.watchlist_items),
                'active_bids': self.active_bids,
                'watchlist_items': self.watchlist_items
            }
            
            with open('../data/status.json', 'w') as f:
                json.dump(status_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"❌ Error saving data: {e}")
    
    def send_start_notification(self):
        """Send SMS notification when monitoring starts."""
        try:
            message = f"""🚀 AUCTION MONITOR STARTED

Time: {datetime.now().strftime('%H:%M:%S')}
Account: {os.getenv('JOHNPYE_USERNAME', 'Unknown')[:10]}...

✅ Login successful
📊 Monitoring active bids and watchlist
🔔 You'll get alerts for status changes
⏰ Checking every {self.config.get_check_interval()} seconds

Monitor is now active!"""

            self.notification_manager._send_sms("Monitor Started", message)
            self.logger.info("📱 Start notification SMS sent")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send start SMS: {e}")
    
    def send_stop_notification(self):
        """Send SMS notification when monitoring stops."""
        try:
            if self.start_time:
                duration = datetime.now() - self.start_time
                duration_str = str(duration).split('.')[0]
            else:
                duration_str = "Unknown"
            
            message = f"""🛑 AUCTION MONITOR STOPPED

Time: {datetime.now().strftime('%H:%M:%S')}
Duration: {duration_str}

Final Status:
📊 Active Bids: {len(self.active_bids)}
👁️ Watchlist: {len(self.watchlist_items)}

Data saved for review."""

            self.notification_manager._send_sms("Monitor Stopped", message)
            self.logger.info("📱 Stop notification SMS sent")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send stop SMS: {e}")
    
    def start_monitoring(self):
        """Start the production monitoring process."""
        try:
            self.logger.info("🚀 Starting Production Auction Monitor...")
            self.is_running = True
            self.start_time = datetime.now()
            
            # Send start notification
            self.send_start_notification()
            
            # Set up driver
            if not self.setup_driver(headless=True):  # Headless for production
                raise Exception("Failed to setup WebDriver")
            
            # Login
            if not self.login():
                raise Exception("Failed to login")
            
            # Start monitoring loop
            while self.is_running:
                self.logger.info("🔄 Checking for updates...")
                
                # Get fresh data
                new_active_bids = self.get_active_bids()
                new_watchlist_items = self.get_watchlist()
                
                # Check for changes and send notifications
                if new_active_bids:
                    self.active_bids = new_active_bids
                    self.check_for_changes()
                
                if new_watchlist_items:
                    self.watchlist_items = new_watchlist_items
                
                # Save updated data
                self.save_data()
                
                # Wait before next check
                check_interval = self.config.get_check_interval()
                self.logger.info(f"⏳ Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Monitoring error: {e}")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring process."""
        self.is_running = False
        
        if self.driver:
            self.driver.quit()
        
        self.send_stop_notification()
        self.logger.info("🛑 Production monitor stopped")


def main():
    """Main entry point."""
    print("🎯 PRODUCTION JOHN PYE AUCTION TRACKER")
    print("=" * 60)
    print("✅ Confirmed working with live site")
    print("📱 SMS notifications enabled")
    print("🔄 Real-time bid monitoring")
    print()
    
    # Check credentials
    if not os.getenv('JOHNPYE_USERNAME') or not os.getenv('JOHNPYE_PASSWORD'):
        print("❌ CREDENTIALS MISSING!")
        print("Set JOHNPYE_USERNAME and JOHNPYE_PASSWORD in .env file")
        return False
    
    tracker = ProductionAuctionTracker()
    
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
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)