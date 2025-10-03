#!/usr/bin/env python3
"""
Notification Manager for the John Pye Auctions Tracker.

Handles sending notifications for bid updates, auction endings, and other events.
"""

import logging
from datetime import datetime
from typing import List, Optional
from auction_item import AuctionItem


class NotificationManager:
    """Manages notifications for auction events."""
    
    def __init__(self):
        """Initialize the notification manager."""
        self.logger = logging.getLogger(__name__)
        
    def notify_bid_increase(self, item: AuctionItem, previous_item: AuctionItem):
        """Send notification when a bid increases on a watched item."""
        try:
            current_bid = item.parse_bid_amount()
            previous_bid = previous_item.parse_bid_amount()
            increase = current_bid - previous_bid
            
            message = (
                f"BID INCREASE ALERT!\n"
                f"Item: {item.title}\n"
                f"Lot: {item.lot_number}\n"
                f"Previous Bid: £{previous_bid:.2f}\n"
                f"Current Bid: £{current_bid:.2f}\n"
                f"Increase: £{increase:.2f}\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
                f"URL: {item.url}"
            )
            
            self._send_notification("Bid Increase", message)
            self.logger.info(f"Bid increase notification sent for lot {item.lot_number}")
            
        except Exception as e:
            self.logger.error(f"Failed to send bid increase notification: {e}")
    
    def notify_auction_ending_soon(self, item: AuctionItem, minutes_remaining: int):
        """Send notification when an auction is ending soon."""
        try:
            message = (
                f"AUCTION ENDING SOON!\n"
                f"Item: {item.title}\n"
                f"Lot: {item.lot_number}\n"
                f"Current Bid: {item.current_bid}\n"
                f"Time Remaining: ~{minutes_remaining} minutes\n"
                f"End Time: {item.end_time}\n"
                f"URL: {item.url}"
            )
            
            self._send_notification("Auction Ending Soon", message)
            self.logger.info(f"Ending soon notification sent for lot {item.lot_number}")
            
        except Exception as e:
            self.logger.error(f"Failed to send ending soon notification: {e}")
    
    def notify_auction_ended(self, item: AuctionItem):
        """Send notification when an auction has ended."""
        try:
            message = (
                f"AUCTION ENDED!\n"
                f"Item: {item.title}\n"
                f"Lot: {item.lot_number}\n"
                f"Final Bid: {item.current_bid}\n"
                f"Ended: {datetime.now().strftime('%H:%M:%S')}\n"
                f"URL: {item.url}"
            )
            
            self._send_notification("Auction Ended", message)
            self.logger.info(f"Auction ended notification sent for lot {item.lot_number}")
            
        except Exception as e:
            self.logger.error(f"Failed to send auction ended notification: {e}")
    
    def notify_new_watchlist_item(self, item: AuctionItem):
        """Send notification when a new item is added to watchlist."""
        try:
            message = (
                f"NEW WATCHLIST ITEM!\n"
                f"Item: {item.title}\n"
                f"Lot: {item.lot_number}\n"
                f"Starting Bid: {item.current_bid}\n"
                f"End Time: {item.end_time}\n"
                f"URL: {item.url}"
            )
            
            self._send_notification("New Watchlist Item", message)
            self.logger.info(f"New watchlist item notification sent for lot {item.lot_number}")
            
        except Exception as e:
            self.logger.error(f"Failed to send new item notification: {e}")
    
    def notify_watchlist_item_removed(self, item: AuctionItem):
        """Send notification when an item is removed from watchlist."""
        try:
            message = (
                f"WATCHLIST ITEM REMOVED!\n"
                f"Item: {item.title}\n"
                f"Lot: {item.lot_number}\n"
                f"Last Known Bid: {item.current_bid}\n"
                f"Removed: {datetime.now().strftime('%H:%M:%S')}"
            )
            
            self._send_notification("Watchlist Item Removed", message)
            self.logger.info(f"Item removed notification sent for lot {item.lot_number}")
            
        except Exception as e:
            self.logger.error(f"Failed to send item removed notification: {e}")
    
    def notify_error(self, error_message: str, context: Optional[str] = None):
        """Send notification when an error occurs."""
        try:
            message = (
                f"ERROR ALERT!\n"
                f"Error: {error_message}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            if context:
                message += f"\nContext: {context}"
            
            self._send_notification("Error Alert", message)
            self.logger.warning(f"Error notification sent: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")
    
    def notify_monitoring_started(self):
        """Send notification when monitoring starts."""
        try:
            message = (
                f"MONITORING STARTED!\n"
                f"John Pye Auctions Tracker is now monitoring your watchlist.\n"
                f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            self._send_notification("Monitoring Started", message)
            self.logger.info("Monitoring started notification sent")
            
        except Exception as e:
            self.logger.error(f"Failed to send monitoring started notification: {e}")
    
    def notify_monitoring_stopped(self, reason: Optional[str] = None):
        """Send notification when monitoring stops."""
        try:
            message = (
                f"MONITORING STOPPED!\n"
                f"John Pye Auctions Tracker has stopped monitoring.\n"
                f"Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            if reason:
                message += f"\nReason: {reason}"
            
            self._send_notification("Monitoring Stopped", message)
            self.logger.info("Monitoring stopped notification sent")
            
        except Exception as e:
            self.logger.error(f"Failed to send monitoring stopped notification: {e}")
    
    def _send_notification(self, title: str, message: str):
        """Internal method to send notifications via various channels."""
        # For now, just log the notification
        # In the future, this could be extended to support:
        # - Email notifications
        # - Desktop notifications
        # - Push notifications
        # - Webhook notifications
        # - SMS notifications
        
        self.logger.info(f"NOTIFICATION - {title}")
        self.logger.info(f"Message: {message}")
        
        # Desktop notification (Linux)
        try:
            import subprocess
            subprocess.run([
                'notify-send', 
                f'Auction Tracker - {title}', 
                message
            ], check=False)
        except (ImportError, FileNotFoundError, subprocess.SubprocessError):
            # Fall back to console output if notify-send is not available
            print(f"\n{'='*50}")
            print(f"NOTIFICATION: {title}")
            print(f"{'='*50}")
            print(message)
            print(f"{'='*50}\n")
    
    def test_notifications(self):
        """Test the notification system."""
        try:
            test_item = AuctionItem(
                title="Test Auction Item",
                lot_number="12345",
                current_bid="£100.00",
                end_time="2024-01-01 12:00:00",
                url="https://example.com"
            )
            
            self._send_notification("Test Notification", 
                                  "This is a test notification from the auction tracker.")
            
            return True
        except Exception as e:
            self.logger.error(f"Notification test failed: {e}")
            return False