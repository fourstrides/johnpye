#!/usr/bin/env python3
"""
Startup script for John Pye Auctions Web Dashboard
"""

import os
import sys

def main():
    print("🌐 JOHN PYE AUCTIONS WEB DASHBOARD")
    print("=" * 50)
    print()
    print("🚀 Starting web dashboard...")
    print("📊 Dashboard will be available at:")
    print("   • Local:     http://localhost:5000")
    print("   • Network:   http://0.0.0.0:5000")
    print()
    print("🔧 Features available:")
    print("   • View active bids and watchlist")
    print("   • Start/stop monitoring from web interface")
    print("   • Real-time status updates")
    print("   • Manual data refresh")
    print("   • Auto-refresh toggle")
    print()
    print("📱 Press Ctrl+C to stop the web server")
    print("=" * 50)
    print()
    
    # Import and run the web app
    from web_app import app
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()