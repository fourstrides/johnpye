#!/usr/bin/env python3
"""
Real-time Dashboard for John Pye Auction Tracker
"""

from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import os
import json
import threading
import time
from datetime import datetime
from enhanced_tracker import EnhancedAuctionTracker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global tracker instance
tracker = None
tracker_thread = None
last_update = None
tracker_status = {
    'running': False,
    'last_update': None,
    'update_interval': 30,  # 30 seconds for live bidding
    'error': None
}

MODERN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>John Pye Auction Tracker - Real-time Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulse { animation: pulse 2s ease-in-out infinite; }
        .winning { background-color: #d1fae5; }
        .outbid { background-color: #fee2e2; }
        .ending-soon { background-color: #fef3c7; }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center">
                    <i class="fas fa-gavel text-blue-600 text-3xl mr-3"></i>
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900">John Pye Auction Tracker</h1>
                        <p class="text-sm text-gray-600">Real-time monitoring with SMS alerts</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <div id="status-indicator" class="flex items-center">
                        <span class="h-3 w-3 rounded-full mr-2" id="status-light"></span>
                        <span class="text-sm font-medium" id="status-text">Initializing...</span>
                    </div>
                    <button onclick="refreshData()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition">
                        <i class="fas fa-sync-alt mr-1"></i> Refresh
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Active Bids</p>
                        <p class="text-2xl font-bold text-gray-900" id="active-bids-count">0</p>
                    </div>
                    <div class="p-3 bg-blue-100 rounded-full">
                        <i class="fas fa-gavel text-blue-600"></i>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Winning</p>
                        <p class="text-2xl font-bold text-green-600" id="winning-count">0</p>
                    </div>
                    <div class="p-3 bg-green-100 rounded-full">
                        <i class="fas fa-trophy text-green-600"></i>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Outbid</p>
                        <p class="text-2xl font-bold text-red-600" id="outbid-count">0</p>
                    </div>
                    <div class="p-3 bg-red-100 rounded-full">
                        <i class="fas fa-exclamation-triangle text-red-600"></i>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Watchlist</p>
                        <p class="text-2xl font-bold text-purple-600" id="watchlist-count">0</p>
                    </div>
                    <div class="p-3 bg-purple-100 rounded-full">
                        <i class="fas fa-eye text-purple-600"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Control Panel -->
        <div class="bg-white rounded-lg shadow mb-6">
            <div class="px-6 py-4 border-b">
                <h2 class="text-lg font-semibold text-gray-900">
                    <i class="fas fa-cog mr-2"></i>Tracker Control
                </h2>
            </div>
            <div class="p-6">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h3 class="text-sm font-medium text-gray-700">Real-time Monitoring</h3>
                        <p class="text-xs text-gray-500">Automatically checks for updates every 30 seconds for live bidding</p>
                    </div>
                    <button id="tracker-toggle" onclick="toggleTracker()" class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition">
                        <i class="fas fa-play mr-2"></i>Start Monitoring
                    </button>
                </div>
                
                <div class="bg-gray-50 rounded-lg p-4">
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-gray-600">Last Update:</span>
                        <span class="font-medium" id="last-update">Never</span>
                    </div>
                    <div class="flex items-center justify-between text-sm mt-2">
                        <span class="text-gray-600">Next Update:</span>
                        <span class="font-medium" id="next-update">Not scheduled</span>
                    </div>
                    <div class="flex items-center justify-between text-sm mt-2">
                        <span class="text-gray-600">SMS Notifications:</span>
                        <span class="font-medium text-green-600"><i class="fas fa-check-circle"></i> Enabled</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Active Bids Section -->
        <div class="bg-white rounded-lg shadow mb-6">
            <div class="px-6 py-4 border-b flex justify-between items-center">
                <h2 class="text-lg font-semibold text-gray-900">
                    <i class="fas fa-gavel mr-2 text-red-600"></i>Active Bids
                </h2>
                <span class="text-sm text-gray-500">Auto-refreshes when monitoring is active</span>
            </div>
            <div id="active-bids-container" class="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                <div class="p-8 text-center text-gray-500">
                    <i class="fas fa-spinner fa-spin text-3xl mb-3"></i>
                    <p>Click "Start Monitoring" to load real-time data</p>
                </div>
            </div>
        </div>

        <!-- Watchlist Section -->
        <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b flex justify-between items-center">
                <h2 class="text-lg font-semibold text-gray-900">
                    <i class="fas fa-eye mr-2 text-purple-600"></i>Watchlist Items
                </h2>
                <span class="text-sm text-gray-500">Monitoring for price changes</span>
            </div>
            <div id="watchlist-container" class="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                <div class="p-8 text-center text-gray-500">
                    <i class="fas fa-spinner fa-spin text-3xl mb-3"></i>
                    <p>Click "Start Monitoring" to load real-time data</p>
                </div>
            </div>
        </div>
    </main>

    <!-- Toast Container -->
    <div id="toast-container" class="fixed bottom-4 right-4 z-50"></div>

    <script>
        let updateInterval = null;
        let trackerRunning = false;
        let nextUpdateTime = null;

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            checkTrackerStatus();
            setInterval(updateTimes, 1000); // Update times every second
        });

        function checkTrackerStatus() {
            axios.get('/api/tracker-status')
                .then(response => {
                    updateTrackerUI(response.data);
                    if (response.data.is_running) {
                        refreshData();
                    }
                })
                .catch(error => {
                    console.error('Error checking tracker status:', error);
                });
        }

        function toggleTracker() {
            const button = document.getElementById('tracker-toggle');
            button.disabled = true;
            
            if (trackerRunning) {
                // Stop tracker
                axios.post('/api/stop-tracker')
                    .then(response => {
                        showToast('Tracker stopped', 'success');
                        updateTrackerUI({is_running: false});
                        clearInterval(updateInterval);
                    })
                    .catch(error => {
                        showToast('Failed to stop tracker', 'error');
                        console.error('Error:', error);
                    })
                    .finally(() => {
                        button.disabled = false;
                    });
            } else {
                // Start tracker
                showToast('Starting tracker...', 'info');
                axios.post('/api/start-tracker')
                    .then(response => {
                        showToast('Tracker started! Loading real-time data...', 'success');
                        updateTrackerUI({is_running: true});
                        
                        // Initial data load after 5 seconds
                        setTimeout(() => {
                            refreshData();
                            // Set up automatic updates every 5 minutes
                            updateInterval = setInterval(refreshData, 300000);
                        }, 5000);
                    })
                    .catch(error => {
                        showToast('Failed to start tracker', 'error');
                        console.error('Error:', error);
                    })
                    .finally(() => {
                        button.disabled = false;
                    });
            }
        }

        function updateTrackerUI(status) {
            trackerRunning = status.is_running;
            const button = document.getElementById('tracker-toggle');
            const statusLight = document.getElementById('status-light');
            const statusText = document.getElementById('status-text');
            
            if (trackerRunning) {
                button.innerHTML = '<i class="fas fa-stop mr-2"></i>Stop Monitoring';
                button.className = 'bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-medium transition';
                statusLight.className = 'h-3 w-3 rounded-full mr-2 bg-green-500 pulse';
                statusText.textContent = 'Monitoring Active';
                statusText.className = 'text-sm font-medium text-green-600';
                
                if (status.update_interval) {
                    nextUpdateTime = new Date(Date.now() + status.update_interval * 1000);
                }
            } else {
                button.innerHTML = '<i class="fas fa-play mr-2"></i>Start Monitoring';
                button.className = 'bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition';
                statusLight.className = 'h-3 w-3 rounded-full mr-2 bg-gray-400';
                statusText.textContent = 'Monitoring Stopped';
                statusText.className = 'text-sm font-medium text-gray-600';
                nextUpdateTime = null;
            }
        }

        function refreshData() {
            showToast('Refreshing data...', 'info');
            
            // Fetch active bids
            axios.get('/api/active-bids')
                .then(response => {
                    displayActiveBids(response.data.bids);
                    updateStats(response.data);
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                    if (trackerRunning) {
                        nextUpdateTime = new Date(Date.now() + 30000); // 30 seconds for live bidding
                    }
                })
                .catch(error => {
                    showToast('Failed to fetch active bids', 'error');
                    console.error('Error:', error);
                });
            
            // Fetch watchlist
            axios.get('/api/watchlist')
                .then(response => {
                    displayWatchlist(response.data.items);
                    document.getElementById('watchlist-count').textContent = response.data.count;
                })
                .catch(error => {
                    showToast('Failed to fetch watchlist', 'error');
                    console.error('Error:', error);
                });
        }

        function updateStats(data) {
            document.getElementById('active-bids-count').textContent = data.count || 0;
            document.getElementById('winning-count').textContent = data.winning || 0;
            document.getElementById('outbid-count').textContent = data.outbid || 0;
        }

        function displayActiveBids(bids) {
            const container = document.getElementById('active-bids-container');
            
            if (!bids || bids.length === 0) {
                container.innerHTML = '<div class="p-8 text-center text-gray-500"><i class="fas fa-inbox text-3xl mb-3"></i><p>No active bids found</p></div>';
                return;
            }
            
            container.innerHTML = bids.map(bid => {
                const status = bid.status.toUpperCase();
                const statusClass = status === 'WINNING' ? 'winning' : status === 'OUTBID' ? 'outbid' : '';
                const statusIcon = status === 'WINNING' ? 'fa-trophy text-green-600' : 'fa-exclamation-triangle text-red-600';
                const endingSoon = isEndingSoon(bid.end_time);
                
                return `
                    <div class="p-4 hover:bg-gray-50 ${statusClass} ${endingSoon ? 'ending-soon' : ''}">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <h3 class="font-medium text-gray-900">${bid.title}</h3>
                                <p class="text-sm text-gray-600 mt-1">Lot #${bid.lot_number}</p>
                                
                                <div class="grid grid-cols-3 gap-3 mt-3">
                                    <div>
                                        <p class="text-xs text-gray-500">Current Bid</p>
                                        <p class="text-sm font-semibold">${bid.current_bid}</p>
                                    </div>
                                    <div>
                                        <p class="text-xs text-gray-500">Your Bid</p>
                                        <p class="text-sm font-semibold text-blue-600">${bid.my_bid || bid.current_bid}</p>
                                    </div>
                                    <div>
                                        <p class="text-xs text-gray-500">Your Max</p>
                                        <p class="text-sm font-semibold text-purple-600">${bid.my_max_bid}</p>
                                    </div>
                                </div>
                                
                                <div class="flex items-center mt-3 space-x-4">
                                    <span class="inline-flex items-center text-sm ${status === 'WINNING' ? 'text-green-600' : 'text-red-600'}">
                                        <i class="fas ${statusIcon} mr-1"></i>
                                        ${bid.status}
                                    </span>
                                    <span class="text-sm text-gray-600">
                                        <i class="fas fa-clock mr-1"></i>
                                        ${bid.end_time}
                                    </span>
                                    ${endingSoon ? '<span class="text-sm text-orange-600"><i class="fas fa-exclamation-circle mr-1"></i>Ending Soon!</span>' : ''}
                                </div>
                            </div>
                            <div class="ml-4">
                                <a href="${bid.url}" target="_blank" class="text-blue-600 hover:text-blue-800">
                                    <i class="fas fa-external-link-alt text-lg"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function displayWatchlist(items) {
            const container = document.getElementById('watchlist-container');
            
            if (!items || items.length === 0) {
                container.innerHTML = '<div class="p-8 text-center text-gray-500"><i class="fas fa-inbox text-3xl mb-3"></i><p>No watchlist items found</p></div>';
                return;
            }
            
            container.innerHTML = items.map(item => {
                const endingSoon = isEndingSoon(item.end_time);
                
                return `
                    <div class="p-4 hover:bg-gray-50 ${endingSoon ? 'ending-soon' : ''}">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <h3 class="font-medium text-gray-900">${item.title}</h3>
                                <p class="text-sm text-gray-600 mt-1">Lot #${item.lot_number}</p>
                                
                                <div class="mt-3">
                                    <p class="text-xs text-gray-500">Current Bid</p>
                                    <p class="text-lg font-semibold">${item.current_bid}</p>
                                </div>
                                
                                <div class="flex items-center mt-3 space-x-4">
                                    <span class="text-sm text-gray-600">
                                        <i class="fas fa-clock mr-1"></i>
                                        ${item.end_time}
                                    </span>
                                    ${endingSoon ? '<span class="text-sm text-orange-600"><i class="fas fa-exclamation-circle mr-1"></i>Ending Soon!</span>' : ''}
                                </div>
                            </div>
                            <div class="ml-4">
                                <a href="${item.url}" target="_blank" class="text-blue-600 hover:text-blue-800">
                                    <i class="fas fa-external-link-alt text-lg"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function isEndingSoon(endTime) {
            // Check if auction ends within 1 hour
            if (endTime && endTime.includes('Minutes')) {
                const minutes = parseInt(endTime.match(/\\d+/)?.[0] || '0');
                return minutes <= 60;
            }
            return false;
        }

        function updateTimes() {
            // Update next update time
            if (nextUpdateTime) {
                const now = new Date();
                const diff = nextUpdateTime - now;
                if (diff > 0) {
                    const minutes = Math.floor(diff / 60000);
                    const seconds = Math.floor((diff % 60000) / 1000);
                    document.getElementById('next-update').textContent = `${minutes}m ${seconds}s`;
                } else {
                    document.getElementById('next-update').textContent = 'Updating...';
                }
            }
        }

        function showToast(message, type = 'info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            
            const bgColor = type === 'success' ? 'bg-green-500' : 
                           type === 'error' ? 'bg-red-500' : 
                           type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500';
            
            const icon = type === 'success' ? 'fa-check-circle' : 
                        type === 'error' ? 'fa-times-circle' : 
                        type === 'warning' ? 'fa-exclamation-circle' : 'fa-info-circle';
            
            toast.className = `${bgColor} text-white px-6 py-3 rounded-lg shadow-lg mb-4 flex items-center`;
            toast.innerHTML = `<i class="fas ${icon} mr-2"></i> ${message}`;
            
            container.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                refreshData();
            }
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                toggleTracker();
            }
        });
    </script>
</body>
</html>
"""

# Background tracker management
def run_tracker_in_background():
    """Run the auction tracker in the background."""
    global tracker, last_update, tracker_status
    
    try:
        tracker_status['running'] = True
        tracker_status['error'] = None
        
        tracker = EnhancedAuctionTracker()
        if not tracker.setup_driver():
            raise Exception("Failed to initialize WebDriver")
        logger.info("Background tracker started")
        
        while tracker_status['running']:
            try:
                # Login and fetch data
                tracker.login()
                active_bids = tracker.get_active_bids()
                watchlist = tracker.get_watchlist()
                
                # Save data
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'active_bids': active_bids if isinstance(active_bids, list) else [],
                    'watchlist_items': watchlist if isinstance(watchlist, list) else [],
                    'is_running': True
                }
                
                # Use absolute path for data file
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
                os.makedirs(data_dir, exist_ok=True)
                data_file = os.path.join(data_dir, 'realtime_status.json')
                
                with open(data_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                last_update = datetime.now()
                tracker_status['last_update'] = last_update.isoformat()
                
                logger.info(f"Updated data: {len(active_bids)} bids, {len(watchlist)} watchlist items")
                
                # Wait for next update (30 seconds for live bidding)
                for _ in range(30):  # 30 seconds for live bidding
                    if not tracker_status['running']:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Tracker error: {e}")
                tracker_status['error'] = str(e)
                time.sleep(60)  # Wait 1 minute before retry
                
    except Exception as e:
        logger.error(f"Fatal tracker error: {e}")
        tracker_status['error'] = str(e)
    finally:
        tracker_status['running'] = False
        if tracker:
            tracker.stop_monitoring()
        logger.info("Background tracker stopped")

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template_string(MODERN_DASHBOARD_TEMPLATE)

@app.route('/api/tracker-status')
def get_tracker_status():
    """Get current tracker status."""
    return jsonify({
        'is_running': tracker_status['running'],
        'last_update': tracker_status['last_update'],
        'update_interval': tracker_status['update_interval'],
        'error': tracker_status['error']
    })

@app.route('/api/start-tracker', methods=['POST'])
def start_tracker():
    """Start the background tracker."""
    global tracker_thread
    
    if not tracker_status['running']:
        tracker_thread = threading.Thread(target=run_tracker_in_background, daemon=True)
        tracker_thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Tracker started'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Tracker already running'
        }), 400

@app.route('/api/stop-tracker', methods=['POST'])
def stop_tracker():
    """Stop the background tracker."""
    tracker_status['running'] = False
    
    return jsonify({
        'status': 'success',
        'message': 'Tracker stopped'
    })

@app.route('/api/active-bids')
def get_active_bids():
    """Get active bids data."""
    try:
        # Try to load realtime data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        data_file = os.path.join(data_dir, 'realtime_status.json')
        
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
                
            bids = data.get('active_bids', [])
            
            # Count statuses (handle different case variations)
            winning = sum(1 for bid in bids if bid.get('status', '').upper() == 'WINNING')
            outbid = sum(1 for bid in bids if bid.get('status', '').upper() == 'OUTBID')
            
            return jsonify({
                'bids': bids,
                'count': len(bids),
                'winning': winning,
                'outbid': outbid,
                'timestamp': data.get('timestamp')
            })
    except Exception as e:
        logger.error(f"Error loading active bids: {e}")
    
    return jsonify({
        'bids': [],
        'count': 0,
        'winning': 0,
        'outbid': 0,
        'error': 'No data available'
    })

@app.route('/api/watchlist')
def get_watchlist():
    """Get watchlist data."""
    try:
        # Try to load realtime data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        data_file = os.path.join(data_dir, 'realtime_status.json')
        
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
                
            items = data.get('watchlist_items', [])
            
            return jsonify({
                'items': items,
                'count': len(items),
                'timestamp': data.get('timestamp')
            })
    except Exception as e:
        logger.error(f"Error loading watchlist: {e}")
    
    return jsonify({
        'items': [],
        'count': 0,
        'error': 'No data available'
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Manually refresh data if tracker is running."""
    if tracker_status['running'] and tracker:
        try:
            active_bids = tracker.get_active_bids()
            watchlist = tracker.get_watchlist()
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'active_bids': active_bids if isinstance(active_bids, list) else [],
                'watchlist_items': watchlist if isinstance(watchlist, list) else [],
                'is_running': True
            }
            
            # Use absolute path for data file
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            os.makedirs(data_dir, exist_ok=True)
            data_file = os.path.join(data_dir, 'realtime_status.json')
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return jsonify({
                'status': 'success',
                'message': 'Data refreshed'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    else:
        return jsonify({
            'status': 'error',
            'message': 'Tracker not running'
        }), 400

if __name__ == '__main__':
    print("🚀 Starting Real-time John Pye Auction Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8081")
    print("✨ Features:")
    print("   • Real-time data from John Pye website")
    print("   • Automatic updates every 30 seconds for live bidding")
    print("   • Visual status indicators")
    print("   • SMS notifications for important events")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    app.run(host='0.0.0.0', port=8081, debug=True)
