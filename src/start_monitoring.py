#!/usr/bin/env python3
"""
Continuous monitoring script for John Pye auctions with SMS notifications.
"""

import sys
import os
import time
import signal
import json
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

from main import JohnPyeAuctionTracker
from auction_item import AuctionItem
from notification_manager import NotificationManager
from get_my_items import get_items_from_page

class AuctionMonitor:
    """Enhanced auction monitor with outbid detection."""
    
    def __init__(self):
        self.tracker = JohnPyeAuctionTracker()
        self.running = True
        self.previous_items = {}  # Store previous state for comparison
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("\\n🛑 Shutdown signal received. Stopping monitoring...")
        self.running = False
    
    def load_previous_state(self):
        """Load previous auction state from file."""
        try:
            with open('../data/auction_state.json', 'r') as f:
                data = json.load(f)
                # Convert back to AuctionItem objects
                for key, item_data in data.items():
                    if item_data:
                        self.previous_items[key] = AuctionItem.from_dict(item_data)
        except FileNotFoundError:
            print("📝 No previous state found - starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading previous state: {e}")
    
    def save_current_state(self, items):
        """Save current auction state to file."""
        try:
            # Convert AuctionItem objects to dictionaries
            data = {}
            for item in items:
                key = f"{item.lot_number}_{item.title[:50]}"
                data[key] = item.to_dict()
            
            with open('../data/auction_state.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving state: {e}")
    
    def save_web_interface_data(self, active_bids, watchlist_items):
        """Save data in format expected by web interface."""
        try:
            # Prepare data for web interface
            data = {
                'active_bids': active_bids or [],
                'watchlist': watchlist_items or [],
                'last_updated': datetime.now().isoformat(),
                'total_items': len((active_bids or []) + (watchlist_items or [])),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save to monitoring data file
            with open('../data/monitoring_data.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error saving web interface data: {e}")
    
    def compare_and_notify(self, current_items):
        """Compare current items with previous state and send notifications."""
        notifications_sent = 0
        
        for current_item in current_items:
            key = f"{current_item.lot_number}_{current_item.title[:50]}"
            
            if key in self.previous_items:
                previous_item = self.previous_items[key]
                current_bid = current_item.parse_bid_amount()
                previous_bid = previous_item.parse_bid_amount()
                
                # Check for bid increases (someone outbid you or bid increased)
                if current_bid > previous_bid:
                    print(f"📈 Bid increase detected on {current_item.title[:50]}...")
                    print(f"   Previous: £{previous_bid:.2f} -> Current: £{current_bid:.2f}")
                    
                    # Send outbidded notification
                    self.tracker.notification_manager.notify_outbidded(
                        current_item, 
                        current_bid, 
                        previous_bid
                    )
                    notifications_sent += 1
                    
            else:
                # New item detected
                print(f"🆕 New item detected: {current_item.title[:50]}...")
                self.tracker.notification_manager.notify_new_watchlist_item(current_item)
                notifications_sent += 1
        
        return notifications_sent
    
    def fetch_current_items(self):
        """Fetch current auction items."""
        current_items = []
        
        try:
            # Get active bids
            active_bids = get_items_from_page(
                self.tracker,
                "https://www.johnpyeauctions.co.uk/Account/Bidding/Active",
                "Active Bids"
            )
            
            # Get watchlist items  
            watchlist_items = get_items_from_page(
                self.tracker,
                "https://www.johnpyeauctions.co.uk/Account/Bidding/Watching", 
                "Watchlist"
            )
            
            # Convert to AuctionItem objects
            for item_data in active_bids + watchlist_items:
                if item_data and item_data.get('title'):
                    auction_item = AuctionItem(
                        title=item_data.get('title', ''),
                        lot_number=item_data.get('lot_number', ''),
                        current_bid=item_data.get('current_bid', ''),
                        end_time=item_data.get('end_time', ''),
                        url=item_data.get('url', '')
                    )
                    current_items.append(auction_item)
            
            print(f"📊 Found {len(current_items)} total auction items")
            
            # Save data for web interface
            self.save_web_interface_data(active_bids, watchlist_items)
            
        except Exception as e:
            print(f"❌ Error fetching current items: {e}")
        
        return current_items
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle."""
        try:
            print(f"🔍 Checking auctions at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
            
            # Fetch current items
            current_items = self.fetch_current_items()
            
            if not current_items:
                print("📝 No items found to monitor")
                return
            
            # Compare with previous state and send notifications
            notifications_sent = self.compare_and_notify(current_items)
            
            # Update previous state
            self.save_current_state(current_items)
            
            # Update previous_items for next comparison
            self.previous_items = {}
            for item in current_items:
                key = f"{item.lot_number}_{item.title[:50]}"
                self.previous_items[key] = item
            
            print(f"✅ Monitoring cycle complete. Notifications sent: {notifications_sent}")
            
        except Exception as e:
            print(f"❌ Error in monitoring cycle: {e}")
            # Send error notification
            self.tracker.notification_manager.notify_error(str(e), "Monitoring cycle")
    
    def start_monitoring(self):
        """Start continuous monitoring."""
        print("🎯 JOHN PYE AUCTION TRACKER - STARTING CONTINUOUS MONITORING")
        print("=" * 70)
        
        # Ensure data directory exists
        os.makedirs('../data', exist_ok=True)
        
        try:
            # Setup and login
            print("🔧 Setting up WebDriver...")
            if not self.tracker.setup_driver(headless=True):
                print("❌ WebDriver setup failed")
                return
            
            print("🔐 Logging into your John Pye account...")
            if not self.tracker.login():
                print("❌ Login failed")
                return
            
            print("✅ Successfully logged in!")
            
            # Load previous state
            self.load_previous_state()
            
            # Send startup notification
            self.tracker.notification_manager.notify_monitoring_started()
            
            # Main monitoring loop
            check_interval = self.tracker.config.get_check_interval()
            print(f"⏰ Monitoring every {check_interval} seconds...")
            print("🔔 SMS notifications enabled for outbidding alerts!")
            print("📱 Press Ctrl+C to stop monitoring")
            print()
            
            while self.running:
                try:
                    self.run_monitoring_cycle()
                    
                    # Wait for next check
                    print(f"⏳ Next check in {check_interval} seconds...")
                    
                    # Sleep in smaller chunks to allow for graceful shutdown
                    for _ in range(check_interval):
                        if not self.running:
                            break
                        time.sleep(1)
                    
                except KeyboardInterrupt:
                    self.running = False
                    break
                except Exception as e:
                    print(f"❌ Unexpected error: {e}")
                    print("⏳ Retrying in 60 seconds...")
                    time.sleep(60)
            
        except Exception as e:
            print(f"❌ Critical error: {e}")
            self.tracker.notification_manager.notify_error(str(e), "Critical system error")
            
        finally:
            # Cleanup
            print("\\n🛑 Stopping monitoring...")
            if self.tracker.driver:
                self.tracker.driver.quit()
            
            # Send shutdown notification
            self.tracker.notification_manager.notify_monitoring_stopped("User requested shutdown")
            print("✅ Monitoring stopped successfully")

def main():
    """Main function."""
    monitor = AuctionMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()