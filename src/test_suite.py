#!/usr/bin/env python3
"""
Comprehensive Test Suite for John Pye Auction Tracker

This script tests all major components of the auction tracker system.
"""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auction_item import AuctionItem
from config_manager import ConfigManager
from notification_manager import NotificationManager
from web_dashboard import AuctionDashboard


class TestAuctionItem(unittest.TestCase):
    """Test cases for AuctionItem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.item = AuctionItem(
            title="Test Laptop Computer",
            lot_number="12345",
            current_bid="£150.50",
            end_time="2024-12-31 15:30:00",
            url="https://example.com/lot/12345"
        )
    
    def test_auction_item_creation(self):
        """Test auction item creation."""
        self.assertEqual(self.item.title, "Test Laptop Computer")
        self.assertEqual(self.item.lot_number, "12345")
        self.assertEqual(self.item.current_bid, "£150.50")
        self.assertIsNotNone(self.item.last_updated)
    
    def test_parse_bid_amount(self):
        """Test bid amount parsing."""
        self.assertEqual(self.item.parse_bid_amount(), 150.50)
        
        # Test various formats
        item2 = AuctionItem("Test", "123", "£1,250.75", "2024-01-01", "http://test.com")
        self.assertEqual(item2.parse_bid_amount(), 1250.75)
        
        item3 = AuctionItem("Test", "123", "$500", "2024-01-01", "http://test.com")
        self.assertEqual(item3.parse_bid_amount(), 500.0)
        
        item4 = AuctionItem("Test", "123", "invalid", "2024-01-01", "http://test.com")
        self.assertEqual(item4.parse_bid_amount(), 0.0)
    
    def test_parse_lot_number(self):
        """Test lot number parsing."""
        self.assertEqual(self.item.parse_lot_number(), "12345")
        
        # Test with "Lot " prefix
        item2 = AuctionItem("Test", "Lot 67890", "£100", "2024-01-01", "http://test.com")
        self.assertEqual(item2.parse_lot_number(), "67890")
    
    def test_has_bid_increased(self):
        """Test bid increase detection."""
        previous_item = AuctionItem(
            title="Test Laptop Computer",
            lot_number="12345",
            current_bid="£100.00",
            end_time="2024-12-31 15:30:00",
            url="https://example.com/lot/12345"
        )
        
        self.assertTrue(self.item.has_bid_increased(previous_item))
        
        # Test no increase
        same_item = AuctionItem(
            title="Test Laptop Computer",
            lot_number="12345",
            current_bid="£150.50",
            end_time="2024-12-31 15:30:00",
            url="https://example.com/lot/12345"
        )
        
        self.assertFalse(self.item.has_bid_increased(same_item))
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        data = self.item.to_dict()
        
        self.assertEqual(data['title'], "Test Laptop Computer")
        self.assertEqual(data['lot_number'], "12345")
        self.assertEqual(data['current_bid'], "£150.50")
        self.assertEqual(data['current_bid_amount'], 150.50)
        self.assertIn('last_updated', data)
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'title': 'Test Item',
            'lot_number': '999',
            'current_bid': '£200.00',
            'end_time': '2024-01-01 12:00:00',
            'url': 'http://test.com',
            'last_updated': datetime.now().isoformat()
        }
        
        item = AuctionItem.from_dict(data)
        self.assertEqual(item.title, 'Test Item')
        self.assertEqual(item.lot_number, '999')
        self.assertIsNotNone(item.last_updated)


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        os.makedirs('../config', exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        # Clean up test directory if needed
    
    def test_config_creation(self):
        """Test configuration manager creation."""
        with patch.dict(os.environ, {'JOHNPYE_USERNAME': 'testuser', 'JOHNPYE_PASSWORD': 'testpass'}):
            config_manager = ConfigManager()
            
            self.assertIsNotNone(config_manager.config)
            self.assertEqual(config_manager.get_username(), 'testuser')
            self.assertEqual(config_manager.get_password(), 'testpass')
    
    def test_default_config(self):
        """Test default configuration values."""
        config_manager = ConfigManager()
        
        # Should have default check interval
        self.assertGreater(config_manager.get_check_interval(), 0)
        
        # Should have monitoring settings
        self.assertIn('monitoring', config_manager.config)
        self.assertIn('notifications', config_manager.config)
        self.assertIn('data_storage', config_manager.config)


class TestNotificationManager(unittest.TestCase):
    """Test cases for NotificationManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.notification_manager = NotificationManager()
        self.test_item = AuctionItem(
            title="Test Item",
            lot_number="123",
            current_bid="£100.00",
            end_time="2024-01-01 12:00:00",
            url="https://example.com"
        )
    
    @patch('notification_manager.subprocess.run')
    def test_desktop_notification(self, mock_subprocess):
        """Test desktop notification functionality."""
        mock_subprocess.return_value = None
        
        self.notification_manager._send_notification("Test", "Test message")
        
        # Should attempt to call notify-send
        mock_subprocess.assert_called()
    
    def test_bid_increase_notification(self):
        """Test bid increase notification."""
        previous_item = AuctionItem(
            title="Test Item",
            lot_number="123",
            current_bid="£50.00",
            end_time="2024-01-01 12:00:00",
            url="https://example.com"
        )
        
        # Should not raise an exception
        self.notification_manager.notify_bid_increase(self.test_item, previous_item)
    
    def test_auction_ending_notification(self):
        """Test auction ending soon notification."""
        # Should not raise an exception
        self.notification_manager.notify_auction_ending_soon(self.test_item, 30)
    
    def test_new_item_notification(self):
        """Test new watchlist item notification."""
        # Should not raise an exception
        self.notification_manager.notify_new_watchlist_item(self.test_item)
    
    def test_error_notification(self):
        """Test error notification."""
        # Should not raise an exception
        self.notification_manager.notify_error("Test error", "Test context")


class TestWebDashboard(unittest.TestCase):
    """Test cases for Web Dashboard."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dashboard = AuctionDashboard()
        self.test_item = AuctionItem(
            title="Test Dashboard Item",
            lot_number="456",
            current_bid="£200.00",
            end_time="2024-01-01 12:00:00",
            url="https://example.com"
        )
    
    def test_dashboard_creation(self):
        """Test dashboard creation."""
        self.assertIsNotNone(self.dashboard.app)
        self.assertEqual(len(self.dashboard.current_watchlist), 0)
        self.assertEqual(len(self.dashboard.bid_history), 0)
    
    def test_update_watchlist(self):
        """Test watchlist update."""
        items = [self.test_item]
        self.dashboard.update_watchlist(items)
        
        self.assertEqual(len(self.dashboard.current_watchlist), 1)
        self.assertEqual(self.dashboard.monitoring_status['items_monitored'], 1)
        self.assertIsNotNone(self.dashboard.monitoring_status['last_check'])
    
    def test_add_bid_history(self):
        """Test adding bid history."""
        self.dashboard.add_bid_history(self.test_item, 'bid_increase', 'Increased by £50.00')
        
        self.assertEqual(len(self.dashboard.bid_history), 1)
        self.assertEqual(self.dashboard.bid_history[0]['lot_number'], '456')
        self.assertEqual(self.dashboard.bid_history[0]['event_type'], 'bid_increase')
    
    def test_monitoring_status_update(self):
        """Test monitoring status update."""
        self.dashboard.update_monitoring_status(True, datetime.now().isoformat())
        
        self.assertTrue(self.dashboard.monitoring_status['is_running'])
        self.assertIsNotNone(self.dashboard.monitoring_status['started_at'])
    
    def test_notification_increment(self):
        """Test notification counter increment."""
        initial_count = self.dashboard.monitoring_status['notifications_sent']
        self.dashboard.increment_notifications()
        
        self.assertEqual(
            self.dashboard.monitoring_status['notifications_sent'], 
            initial_count + 1
        )
    
    def test_get_recent_activity(self):
        """Test recent activity retrieval."""
        # Add some bid history
        self.dashboard.add_bid_history(self.test_item, 'new_item', 'Added to watchlist')
        self.dashboard.add_bid_history(self.test_item, 'bid_increase', 'Increased by £25.00')
        
        activity = self.dashboard.get_recent_activity()
        
        self.assertGreater(len(activity), 0)
        self.assertIn('timestamp', activity[0])
        self.assertIn('type', activity[0])
        self.assertIn('title', activity[0])


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_auction_item_notification_integration(self):
        """Test integration between auction items and notifications."""
        notification_manager = NotificationManager()
        
        item1 = AuctionItem(
            title="Integration Test Item",
            lot_number="789",
            current_bid="£75.00",
            end_time="2024-01-01 12:00:00",
            url="https://example.com"
        )
        
        item2 = AuctionItem(
            title="Integration Test Item",
            lot_number="789",
            current_bid="£100.00",
            end_time="2024-01-01 12:00:00",
            url="https://example.com"
        )
        
        # Test that bid increase detection works with notifications
        if item2.has_bid_increased(item1):
            # This should not raise an exception
            notification_manager.notify_bid_increase(item2, item1)
    
    def test_dashboard_notification_integration(self):
        """Test integration between dashboard and notifications."""
        dashboard = AuctionDashboard()
        notification_manager = NotificationManager()
        
        test_item = AuctionItem(
            title="Dashboard Integration Test",
            lot_number="999",
            current_bid="£300.00",
            end_time="2024-01-01 12:00:00",
            url="https://example.com"
        )
        
        # Update dashboard
        dashboard.update_watchlist([test_item])
        dashboard.add_bid_history(test_item, 'new_item', 'Added to watchlist')
        dashboard.increment_notifications()
        
        # Check that data is properly stored
        self.assertEqual(len(dashboard.current_watchlist), 1)
        self.assertEqual(len(dashboard.bid_history), 1)
        self.assertEqual(dashboard.monitoring_status['notifications_sent'], 1)


def run_all_tests():
    """Run all tests and return results."""
    print("🧪 Running John Pye Auction Tracker Test Suite...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestAuctionItem,
        TestConfigManager,
        TestNotificationManager,
        TestWebDashboard,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print(f"\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)