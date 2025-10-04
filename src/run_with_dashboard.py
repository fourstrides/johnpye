#!/usr/bin/env python3
"""
Run John Pye Auction Tracker with Web Dashboard

This script starts both the auction tracker and the web dashboard
in separate threads for integrated monitoring.
"""

import threading
import time
import sys
import signal
import logging
from datetime import datetime

from main import JohnPyeAuctionTracker
from web_dashboard import create_app, AuctionDashboard


class IntegratedAuctionTracker:
    """Integrated auction tracker with web dashboard."""
    
    def __init__(self):
        """Initialize the integrated tracker."""
        self.tracker = JohnPyeAuctionTracker()
        self.app, self.dashboard = create_app(self.tracker)
        self.tracker.set_dashboard(self.dashboard)
        
        self.dashboard_thread = None
        self.tracker_thread = None
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logging.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def start_dashboard(self, host='localhost', port=8080):
        """Start the web dashboard in a separate thread."""
        def run_dashboard():
            try:
                self.tracker.logger.info(f"Starting web dashboard on http://{host}:{port}")
                self.app.run(host=host, port=port, debug=False, use_reloader=False)
            except Exception as e:
                self.tracker.logger.error(f"Dashboard error: {e}")
        
        self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        self.dashboard_thread.start()
        
        # Give the dashboard a moment to start
        time.sleep(2)
    
    def start_tracker(self):
        """Start the auction tracker in a separate thread."""
        def run_tracker():
            try:
                self.tracker.monitor_watchlist()
            except Exception as e:
                self.tracker.logger.error(f"Tracker error: {e}")
        
        self.tracker_thread = threading.Thread(target=run_tracker, daemon=False)
        self.tracker_thread.start()
    
    def start(self, dashboard_host='localhost', dashboard_port=8080):
        """Start both the tracker and dashboard."""
        self.running = True
        
        print("🚀 Starting John Pye Auction Tracker with Web Dashboard...")
        print(f"📊 Dashboard will be available at: http://{dashboard_host}:{dashboard_port}")
        print("⏹️  Press Ctrl+C to stop\n")
        
        try:
            # Start the web dashboard
            self.start_dashboard(dashboard_host, dashboard_port)
            
            # Start the auction tracker
            self.start_tracker()
            
            # Keep the main thread alive and wait for tracker to complete
            if self.tracker_thread:
                self.tracker_thread.join()
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
            self.stop()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.stop()
    
    def stop(self):
        """Stop both the tracker and dashboard."""
        if self.running:
            self.running = False
            
            # The dashboard will stop when the main process exits
            # The tracker has its own cleanup in the finally block
            
            print("✅ Shutdown complete")
            sys.exit(0)


def main():
    """Main entry point."""
    print("=" * 60)
    print("🎯 JOHN PYE AUCTION TRACKER WITH WEB DASHBOARD")
    print("=" * 60)
    
    # Configuration options
    dashboard_host = 'localhost'
    dashboard_port = 8080
    
    # Check if custom host/port provided via command line
    if len(sys.argv) > 1:
        try:
            dashboard_port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        dashboard_host = sys.argv[2]
    
    try:
        # Create and start the integrated tracker
        integrated_tracker = IntegratedAuctionTracker()
        integrated_tracker.start(dashboard_host, dashboard_port)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()