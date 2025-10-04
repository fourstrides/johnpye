#!/usr/bin/env python3
"""
Simple Working Dashboard for John Pye Auction Tracker
"""

from flask import Flask, render_template_string, jsonify
import os
import sys
import json
from datetime import datetime

# Simple HTML template
SIMPLE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>John Pye Auction Tracker - Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <div class="flex items-center">
                    <i class="fas fa-gavel text-blue-600 text-2xl mr-3"></i>
                    <h1 class="text-2xl font-bold text-gray-900">John Pye Auction Tracker</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <span class="text-sm text-gray-600">Dashboard Active</span>
                    <button id="refreshBtn" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
                        <i class="fas fa-sync-alt mr-1"></i> Refresh
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <!-- Status Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <!-- Dashboard Status -->
            <div class="bg-white overflow-hidden shadow-lg rounded-lg">
                <div class="p-5">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <i class="fas fa-check-circle text-green-500 text-2xl"></i>
                        </div>
                        <div class="ml-5 w-0 flex-1">
                            <dl>
                                <dt class="text-sm font-medium text-gray-500 truncate">Dashboard Status</dt>
                                <dd class="text-lg font-medium text-gray-900">Running</dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Current Time -->
            <div class="bg-white overflow-hidden shadow-lg rounded-lg">
                <div class="p-5">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <i class="fas fa-clock text-blue-500 text-2xl"></i>
                        </div>
                        <div class="ml-5 w-0 flex-1">
                            <dl>
                                <dt class="text-sm font-medium text-gray-500 truncate">Current Time</dt>
                                <dd class="text-lg font-medium text-gray-900" id="currentTime">{{ current_time }}</dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Info -->
            <div class="bg-white overflow-hidden shadow-lg rounded-lg">
                <div class="p-5">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <i class="fas fa-server text-purple-500 text-2xl"></i>
                        </div>
                        <div class="ml-5 w-0 flex-1">
                            <dl>
                                <dt class="text-sm font-medium text-gray-500 truncate">Port</dt>
                                <dd class="text-lg font-medium text-gray-900">8080</dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white shadow-lg rounded-lg overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                    <i class="fas fa-cog mr-2 text-gray-600"></i>
                    Quick Actions
                </h2>
            </div>
            <div class="px-6 py-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button id="testBtn" class="bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg">
                        <i class="fas fa-test mr-2"></i> Test Connection
                    </button>
                    <button id="statusBtn" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-lg">
                        <i class="fas fa-info-circle mr-2"></i> Check Status
                    </button>
                    <button onclick="startFullTracker()" class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-3 rounded-lg">
                        <i class="fas fa-play mr-2"></i> Start Full Tracker
                    </button>
                </div>
                
                <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h3 class="font-semibold text-gray-800 mb-2">Features:</h3>
                    <ul class="text-sm text-gray-600 space-y-1">
                        <li>✅ Dashboard is working correctly</li>
                        <li>🔄 Click "Start Full Tracker" to begin auction monitoring</li>
                        <li>📊 Monitor will track your John Pye active bids and watchlist</li>
                        <li>📱 SMS notifications when started/stopped and for important events</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Active Bids and Watchlist Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8" id="dataSection">
            <!-- Active Bids -->
            <div class="bg-white shadow-lg rounded-lg overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-200">
                    <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                        <i class="fas fa-gavel mr-2 text-red-600"></i>
                        Active Bids (<span id="activeBidsCount">0</span>)
                        <button onclick="refreshActiveBids()" class="ml-auto text-sm bg-blue-500 text-white px-3 py-1 rounded">
                            <i class="fas fa-sync-alt mr-1"></i> Refresh
                        </button>
                    </h2>
                </div>
                <div class="max-h-96 overflow-y-auto" id="activeBidsContainer">
                    <div class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                        <p>Click "Start Full Tracker" to load active bids</p>
                    </div>
                </div>
            </div>

            <!-- Watchlist -->
            <div class="bg-white shadow-lg rounded-lg overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-200">
                    <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                        <i class="fas fa-eye mr-2 text-green-600"></i>
                        Watchlist (<span id="watchlistCount">0</span>)
                        <button onclick="refreshWatchlist()" class="ml-auto text-sm bg-blue-500 text-white px-3 py-1 rounded">
                            <i class="fas fa-sync-alt mr-1"></i> Refresh
                        </button>
                    </h2>
                </div>
                <div class="max-h-96 overflow-y-auto" id="watchlistContainer">
                    <div class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                        <p>Click "Start Full Tracker" to load watchlist</p>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        // Update current time every second
        function updateTime() {
            document.getElementById('currentTime').textContent = new Date().toLocaleString();
        }
        setInterval(updateTime, 1000);
        updateTime();

        // Test button
        document.getElementById('testBtn').addEventListener('click', function() {
            fetch('/api/test')
                .then(response => response.json())
                .then(data => {
                    alert('✅ Connection Test: ' + data.message);
                })
                .catch(error => {
                    alert('❌ Connection Test Failed: ' + error);
                });
        });

        // Status button
        document.getElementById('statusBtn').addEventListener('click', function() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    alert('📊 Status: Dashboard is ' + data.status);
                })
                .catch(error => {
                    alert('❌ Status Check Failed: ' + error);
                });
        });

        // Start full tracker
        function startFullTracker() {
            if (confirm('This will start the full auction monitoring with SMS notifications. Continue?')) {
                const btn = event.target;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Starting...';
                btn.disabled = true;
                
                fetch('/api/start-tracker', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert('🚀 ' + data.message);
                        // Start refreshing data every 30 seconds
                        setTimeout(() => {
                            startDataRefresh();
                        }, 10000); // Wait 10s for tracker to get initial data
                    })
                    .catch(error => {
                        alert('❌ Failed to start tracker: ' + error);
                    })
                    .finally(() => {
                        btn.innerHTML = '<i class="fas fa-play mr-2"></i> Start Full Tracker';
                        btn.disabled = false;
                    });
            }
        }
        
        // Refresh active bids
        function refreshActiveBids() {
            fetch('/api/active-bids')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('activeBidsCount').textContent = data.count;
                    displayActiveBids(data.active_bids);
                })
                .catch(error => {
                    console.error('Error fetching active bids:', error);
                });
        }
        
        // Refresh watchlist
        function refreshWatchlist() {
            fetch('/api/watchlist')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('watchlistCount').textContent = data.count;
                    displayWatchlist(data.watchlist);
                })
                .catch(error => {
                    console.error('Error fetching watchlist:', error);
                });
        }
        
        // Display active bids
        function displayActiveBids(bids) {
            const container = document.getElementById('activeBidsContainer');
            if (!bids || bids.length === 0) {
                container.innerHTML = '<div class="px-6 py-8 text-center text-gray-500"><i class="fas fa-inbox text-2xl mb-2"></i><p>No active bids found</p></div>';
                return;
            }
            
            let html = '<div class="divide-y divide-gray-200">';
            bids.forEach(bid => {
                const statusColor = bid.status === 'Winning' ? 'text-green-600' : bid.status === 'Outbid' ? 'text-red-600' : 'text-yellow-600';
                html += `
                    <div class="px-6 py-4 hover:bg-gray-50">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <h3 class="text-sm font-medium text-gray-900">${bid.title}</h3>
                                <p class="text-sm text-gray-500">Lot: ${bid.lot_number}</p>
                                <div class="mt-1 flex space-x-4 text-sm">
                                    <span class="text-gray-600">Current: ${bid.current_bid}</span>
                                    <span class="text-gray-600">My Max: ${bid.my_max_bid}</span>
                                    <span class="${statusColor} font-medium">${bid.status}</span>
                                </div>
                                <p class="text-xs text-gray-400 mt-1">Ends: ${bid.end_time}</p>
                            </div>
                            <a href="${bid.url}" target="_blank" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }
        
        // Display watchlist
        function displayWatchlist(items) {
            const container = document.getElementById('watchlistContainer');
            if (!items || items.length === 0) {
                container.innerHTML = '<div class="px-6 py-8 text-center text-gray-500"><i class="fas fa-inbox text-2xl mb-2"></i><p>No watchlist items found</p></div>';
                return;
            }
            
            let html = '<div class="divide-y divide-gray-200">';
            items.forEach(item => {
                html += `
                    <div class="px-6 py-4 hover:bg-gray-50">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <h3 class="text-sm font-medium text-gray-900">${item.title}</h3>
                                <p class="text-sm text-gray-500">Lot: ${item.lot_number}</p>
                                <div class="mt-1 flex space-x-4 text-sm">
                                    <span class="text-gray-600">Current: ${item.current_bid}</span>
                                </div>
                                <p class="text-xs text-gray-400 mt-1">Ends: ${item.end_time}</p>
                            </div>
                            <a href="${item.url}" target="_blank" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }
        
        // Start auto-refresh of data
        function startDataRefresh() {
            refreshActiveBids();
            refreshWatchlist();
            setInterval(() => {
                refreshActiveBids();
                refreshWatchlist();
            }, 30000); // Refresh every 30 seconds
        }
        
        // Load initial data on page load
        window.addEventListener('load', () => {
            refreshActiveBids();
            refreshWatchlist();
        });

        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', function() {
            location.reload();
        });
    </script>
</body>
</html>
"""

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template_string(SIMPLE_TEMPLATE, 
                                current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/test')
def api_test():
    """Test API endpoint."""
    return jsonify({
        'status': 'success',
        'message': 'Dashboard is working correctly!',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """Status API endpoint."""
    return jsonify({
        'status': 'running',
        'uptime': 'Active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start-tracker', methods=['POST'])
def api_start_tracker():
    """Start the enhanced tracker."""
    try:
        import subprocess
        import os
        
        # Start the enhanced tracker in background
        cmd = f"cd {os.path.dirname(os.path.abspath(__file__))} && source ../venv/bin/activate && nohup python enhanced_tracker.py > ../logs/enhanced_tracker.log 2>&1 &"
        subprocess.run(cmd, shell=True)
        
        return jsonify({
            'status': 'success',
            'message': 'Enhanced tracker started! You will receive SMS notifications when it starts and stops. Check logs/enhanced_tracker.log for detailed monitoring status.'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start tracker: {str(e)}'
        }), 500

@app.route('/api/active-bids')
def api_active_bids():
    """Get active bids data."""
    try:
        # Try to load from saved status
        status_file = '../data/status.json'
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                data = json.load(f)
                return jsonify({
                    'active_bids': data.get('active_bids', []),
                    'count': data.get('active_bids_count', 0),
                    'timestamp': data.get('timestamp', datetime.now().isoformat())
                })
        else:
            return jsonify({
                'active_bids': [],
                'count': 0,
                'message': 'No data yet. Start the tracker to collect active bids.'
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'active_bids': [],
            'count': 0
        }), 500

@app.route('/api/watchlist')
def api_watchlist():
    """Get watchlist data."""
    try:
        # Try to load from saved status
        status_file = '../data/status.json'
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                data = json.load(f)
                return jsonify({
                    'watchlist': data.get('watchlist_items', []),
                    'count': data.get('watchlist_count', 0),
                    'timestamp': data.get('timestamp', datetime.now().isoformat())
                })
        else:
            return jsonify({
                'watchlist': [],
                'count': 0,
                'message': 'No data yet. Start the tracker to collect watchlist items.'
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'watchlist': [],
            'count': 0
        }), 500

@app.route('/api/tracker-status')
def api_tracker_status():
    """Get detailed tracker status."""
    try:
        # Check if tracker process is running
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'enhanced_tracker.py'], capture_output=True)
        is_process_running = result.returncode == 0
        
        # Try to load saved status
        status_file = '../data/status.json'
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                data = json.load(f)
                data['process_running'] = is_process_running
                return jsonify(data)
        else:
            return jsonify({
                'is_running': False,
                'process_running': is_process_running,
                'active_bids_count': 0,
                'watchlist_count': 0,
                'message': 'Tracker not started yet'
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'is_running': False,
            'process_running': False
        }), 500

if __name__ == '__main__':
    print("🚀 Starting John Pye Auction Tracker Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    app.run(host='0.0.0.0', port=8080, debug=True)