#!/usr/bin/env python3
"""
Notification Manager for the John Pye Auctions Tracker.

Handles sending notifications for bid updates, auction endings, and other events.
"""

import logging
import os
from datetime import datetime
from typing import List, Optional
from auction_item import AuctionItem

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


class NotificationManager:
    """Manages notifications for auction events."""
    
    def __init__(self):
        """Initialize the notification manager."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize Twilio client if credentials are available
        self.twilio_client = None
        self.twilio_phone = None
        self.my_phone = None
        
        # Initialize email settings
        self.email_enabled = False
        self.email_host = None
        self.email_port = None
        self.email_username = None
        self.email_password = None
        self.email_to = None
        
        if TWILIO_AVAILABLE:
            try:
                account_sid = os.getenv('TWILIO_ACCOUNT_SID')
                auth_token = os.getenv('TWILIO_AUTH_TOKEN')
                self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
                self.my_phone = os.getenv('MY_PHONE_NUMBER')
                
                if account_sid and auth_token and self.twilio_phone and self.my_phone:
                    if account_sid != 'your_twilio_account_sid_here':
                        self.twilio_client = Client(account_sid, auth_token)
                        self.logger.info("Twilio SMS notifications enabled")
                    else:
                        self.logger.info("Twilio credentials not configured (using defaults)")
                else:
                    self.logger.info("Twilio credentials incomplete - SMS disabled")
            except Exception as e:
                self.logger.error(f"Failed to initialize Twilio: {e}")
        else:
            self.logger.warning("Twilio library not available - SMS disabled")
        
        # Initialize email settings
        if EMAIL_AVAILABLE:
            try:
                email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
                self.email_host = os.getenv('EMAIL_HOST')
                self.email_port = int(os.getenv('EMAIL_PORT', '587'))
                self.email_username = os.getenv('EMAIL_USERNAME')
                self.email_password = os.getenv('EMAIL_PASSWORD')
                self.email_to = os.getenv('EMAIL_TO')
                
                if email_enabled and all([self.email_host, self.email_username, self.email_password, self.email_to]):
                    self.email_enabled = True
                    self.logger.info("Email notifications enabled")
                else:
                    self.logger.info("Email notifications disabled or incomplete configuration")
                    
            except Exception as e:
                self.logger.error(f"Failed to initialize email settings: {e}")
        else:
            self.logger.warning("Email libraries not available - email disabled")
        
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
    
    def notify_outbidded(self, item: AuctionItem, new_bid_amount: float, your_bid_amount: float):
        """Send urgent notification when you've been outbidded."""
        try:
            message = (
                f"🚨 YOU'VE BEEN OUTBIDDED! 🚨\n"
                f"Item: {item.title[:50]}...\n"
                f"Lot: {item.lot_number}\n"
                f"Your Bid: £{your_bid_amount:.2f}\n"
                f"New High Bid: £{new_bid_amount:.2f}\n"
                f"Outbid by: £{new_bid_amount - your_bid_amount:.2f}\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
                f"Take action now: {item.url}"
            )
            
            # This is urgent, so we send it with high priority
            self._send_notification("OUTBIDDED!", message)
            self.logger.info(f"Outbidded notification sent for lot {item.lot_number}")
            
        except Exception as e:
            self.logger.error(f"Failed to send outbidded notification: {e}")
    
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
    
    def _send_sms(self, title: str, message: str):
        """Send SMS notification via Twilio."""
        if not self.twilio_client:
            return False
            
        try:
            # Create a concise SMS message
            sms_message = f"🎯 {title}\n{message[:140]}..." if len(message) > 140 else f"🎯 {title}\n{message}"
            
            sms_response = self.twilio_client.messages.create(
                body=sms_message,
                from_=self.twilio_phone,
                to=self.my_phone
            )
            
            self.logger.info(f"SMS sent successfully (SID: {sms_response.sid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")
            return False
    
    def _send_email(self, title: str, message: str):
        """Send email notification via SMTP."""
        if not self.email_enabled:
            return False
            
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = self.email_to
            msg['Subject'] = f"Auction Tracker - {title}"
            
            # Add body to email
            body = f"{message}\n\nSent by John Pye Auction Tracker at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg.attach(MIMEText(body, 'plain'))
            
            # Gmail SMTP configuration
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()  # Enable security
            server.login(self.email_username, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_username, self.email_to, text)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {self.email_to}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_notification(self, title: str, message: str):
        """Internal method to send notifications via various channels."""
        self.logger.info(f"NOTIFICATION - {title}")
        self.logger.info(f"Message: {message}")
        
        # Send SMS notification if available
        sms_sent = self._send_sms(title, message)
        
        # Send email notification if available
        email_sent = self._send_email(title, message)
        
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
            if sms_sent:
                print("📱 SMS notification sent!")
            if email_sent:
                print("📧 Email notification sent!")
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