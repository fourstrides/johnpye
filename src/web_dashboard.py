#!/usr/bin/env python3
"""
Web Dashboard for John Pye Auction Tracker

A Flask-based web interface to monitor auction status, view bid history,
and manage tracker settings.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import pandas as pd

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_cors import CORS

from config_manager import ConfigManager
from auction_item import AuctionItem


class AuctionDashboard:
    """Web dashboard for monitoring auction tracker."""
    
    def __init__(self, tracker_instance=None):
        """Initialize the dashboard."""
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')
        CORS(self.app)
        
        self.config = ConfigManager()
        self.tracker_instance = tracker_instance
        self.logger = logging.getLogger(__name__)
        
        # Dashboard data
        self.current_watchlist = []
        self.bid_history = []
        self.monitoring_status = {
            'is_running': False,
            'started_at': None,
            'last_check': None,
            'total_checks': 0,
            'items_monitored': 0,
            'notifications_sent': 0
        }
        
        self.setup_routes()
    
    def setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template('dashboard.html',
                                 status=self.monitoring_status,
                                 watchlist=self.current_watchlist[:10],  # Show latest 10
                                 recent_activity=self.get_recent_activity(),
                                 config=self.get_dashboard_config())
        
        @self.app.route('/api/status')
        def api_status():
            """API endpoint for monitoring status."""
            return jsonify(self.monitoring_status)
        
        @self.app.route('/api/watchlist')
        def api_watchlist():
            """API endpoint for current watchlist."""
            return jsonify({
                'watchlist': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.current_watchlist],
                'count': len(self.current_watchlist),
                'last_updated': datetime.now().isoformat()
            })
        
        @self.app.route('/api/history')
        def api_history():
            """API endpoint for bid history."""
            limit = request.args.get('limit', 50, type=int)
            return jsonify({
                'history': self.bid_history[-limit:],
                'count': len(self.bid_history),
                'last_updated': datetime.now().isoformat()
            })
        
        @self.app.route('/api/config', methods=['GET', 'POST'])
        def api_config():
            """API endpoint for configuration management."""
            if request.method == 'POST':
                try:
                    new_config = request.json
                    self.update_config(new_config)
                    return jsonify({'success': True, 'message': 'Configuration updated'})
                except Exception as e:
                    return jsonify({'success': False, 'message': str(e)}), 400
            else:
                return jsonify(self.get_dashboard_config())
        
        @self.app.route('/api/logs')
        def api_logs():
            """API endpoint for recent log entries."""
            limit = request.args.get('limit', 100, type=int)
            logs = self.get_recent_logs(limit)
            return jsonify({
                'logs': logs,
                'count': len(logs),
                'last_updated': datetime.now().isoformat()
            })
        
        @self.app.route('/api/test-notification', methods=['POST'])
        def api_test_notification():
            """API endpoint to test notifications."""
            try:
                if self.tracker_instance and hasattr(self.tracker_instance, 'notification_manager'):
                    success = self.tracker_instance.notification_manager.test_notifications()
                    if success:
                        return jsonify({'success': True, 'message': 'Test notification sent'})
                    else:
                        return jsonify({'success': False, 'message': 'Failed to send test notification'}), 500
                else:
                    return jsonify({'success': False, 'message': 'Notification manager not available'}), 500
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/watchlist')
        def watchlist_page():
            """Detailed watchlist page."""
            return render_template('watchlist.html',
                                 watchlist=self.current_watchlist,
                                 status=self.monitoring_status)
        
        @self.app.route('/history')
        def history_page():
            """Bid history page."""
            return render_template('history.html',
                                 history=self.bid_history[-100:],  # Show latest 100
                                 status=self.monitoring_status)
        
        @self.app.route('/settings')
        def settings_page():
            """Settings page."""
            return render_template('settings.html',
                                 config=self.get_dashboard_config(),
                                 status=self.monitoring_status)
    
    def update_watchlist(self, watchlist_items: List[AuctionItem]):
        """Update the current watchlist data."""
        self.current_watchlist = watchlist_items
        self.monitoring_status['items_monitored'] = len(watchlist_items)
        self.monitoring_status['last_check'] = datetime.now().isoformat()
        self.monitoring_status['total_checks'] += 1
    
    def add_bid_history(self, item: AuctionItem, event_type: str, details: str = ""):
        """Add an entry to bid history."""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'lot_number': item.lot_number,
            'title': item.title[:50] + "..." if len(item.title) > 50 else item.title,
            'current_bid': item.current_bid,
            'event_type': event_type,  # 'bid_increase', 'new_item', 'ending_soon', etc.
            'details': details,
            'url': item.url
        }
        self.bid_history.append(history_entry)
        
        # Keep only last 1000 entries
        if len(self.bid_history) > 1000:
            self.bid_history = self.bid_history[-1000:]
    
    def update_monitoring_status(self, is_running: bool, started_at: str = None):
        """Update monitoring status."""
        self.monitoring_status['is_running'] = is_running
        if started_at:
            self.monitoring_status['started_at'] = started_at
    
    def increment_notifications(self):
        """Increment notification counter."""
        self.monitoring_status['notifications_sent'] += 1
    
    def get_recent_activity(self) -> List[Dict]:
        """Get recent activity for dashboard."""
        # Combine watchlist updates and bid history
        activity = []
        
        # Add recent bid history
        for entry in self.bid_history[-10:]:
            activity.append({
                'timestamp': entry['timestamp'],
                'type': entry['event_type'],
                'title': entry['title'],
                'description': f"{entry['event_type'].replace('_', ' ').title()}: {entry['details']}"
            })
        
        # Sort by timestamp
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        return activity[:10]
    
    def get_dashboard_config(self) -> Dict:
        """Get configuration data for dashboard."""
        return {
            'monitoring': {
                'check_interval_seconds': self.config.get_check_interval(),
                'headless_browser': self.config.config.get('monitoring', {}).get('headless_browser', True),
                'max_retries': self.config.config.get('monitoring', {}).get('max_retries', 3),
                'timeout_seconds': self.config.config.get('monitoring', {}).get('timeout_seconds', 30)
            },
            'notifications': {
                'enabled': self.config.config.get('notifications', {}).get('enabled', True),
                'bid_increase_threshold': self.config.config.get('notifications', {}).get('bid_increase_threshold', 10.00),
                'ending_soon_threshold_minutes': self.config.config.get('notifications', {}).get('ending_soon_threshold_minutes', 60)
            },
            'data_storage': {
                'save_historical_data': self.config.config.get('data_storage', {}).get('save_historical_data', True),
                'cleanup_old_data_days': self.config.config.get('data_storage', {}).get('cleanup_old_data_days', 30),
                'export_format': self.config.config.get('data_storage', {}).get('export_format', 'csv')
            }
        }
    
    def update_config(self, new_config: Dict):
        """Update configuration."""
        # Update the config file
        for section, settings in new_config.items():
            if section not in self.config.config:
                self.config.config[section] = {}
            self.config.config[section].update(settings)
        
        self.config.save_config()
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent log entries."""
        logs = []
        log_file = '../logs/auction_tracker.log'
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines[-limit:]:
                    line = line.strip()
                    if line:
                        # Simple log parsing
                        parts = line.split(' - ', 2)
                        if len(parts) >= 3:
                            logs.append({
                                'timestamp': parts[0],
                                'level': parts[1],
                                'message': parts[2]
                            })
                        else:
                            logs.append({
                                'timestamp': datetime.now().isoformat(),
                                'level': 'INFO',
                                'message': line
                            })
        except Exception as e:
            self.logger.error(f"Failed to read logs: {e}")
        
        return logs
    
    def run(self, host='localhost', port=8080, debug=False):
        """Run the web dashboard."""
        self.logger.info(f"Starting web dashboard on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)


def create_app(tracker_instance=None):
    """Factory function to create Flask app."""
    dashboard = AuctionDashboard(tracker_instance)
    return dashboard.app, dashboard


if __name__ == '__main__':
    # For testing the dashboard standalone
    app, dashboard = create_app()
    
    # Add some sample data for testing
    sample_item = AuctionItem(
        title="Sample Auction Item",
        lot_number="12345",
        current_bid="£150.00",
        end_time="2024-01-01 15:30:00",
        url="https://example.com"
    )
    
    dashboard.update_watchlist([sample_item])
    dashboard.add_bid_history(sample_item, "new_item", "Added to watchlist")
    dashboard.update_monitoring_status(True, datetime.now().isoformat())
    
    print("Starting dashboard at http://localhost:8080")
    app.run(host='localhost', port=8080, debug=True)