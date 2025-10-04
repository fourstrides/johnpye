#!/usr/bin/env python3
"""
John Pye Auctions Web Dashboard
A Flask web interface for monitoring auctions and managing bids
"""

import os
import json
import subprocess
import psutil
import signal
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv
from main import JohnPyeAuctionTracker

# Load environment variables
load_dotenv('../.env')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Global variables for monitoring
monitoring_process = None
monitoring_data = {}

def get_monitoring_process():
    """Check if monitoring process is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'start_monitoring.py' in ' '.join(cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def load_monitoring_data():
    """Load the latest monitoring data"""
    global monitoring_data
    data_file = '../data/monitoring_data.json'
    
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                monitoring_data = json.load(f)
        except Exception as e:
            print(f"Error loading monitoring data: {e}")
            monitoring_data = {}
    
    # Add monitoring status
    proc = get_monitoring_process()
    monitoring_data['is_monitoring'] = proc is not None
    monitoring_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return monitoring_data

@app.route('/')
def dashboard():
    """Main dashboard page"""
    data = load_monitoring_data()
    return render_template('dashboard.html', data=data)

@app.route('/api/data')
def api_data():
    """API endpoint to get latest monitoring data"""
    return jsonify(load_monitoring_data())

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    """Start the monitoring process"""
    global monitoring_process
    
    proc = get_monitoring_process()
    if proc:
        return jsonify({
            'success': False, 
            'message': 'Monitoring is already running',
            'pid': proc.pid
        })
    
    try:
        # Start monitoring in background with virtual environment
        venv_python = '/home/ubuntu/projects/johnpye-auction-tracker/venv/bin/python'
        cmd = [venv_python, 'start_monitoring.py']
        monitoring_process = subprocess.Popen(
            cmd,
            cwd='/home/ubuntu/projects/johnpye-auction-tracker/src',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Create new process group
        )
        
        return jsonify({
            'success': True,
            'message': 'Monitoring started successfully',
            'pid': monitoring_process.pid
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to start monitoring: {str(e)}'
        })

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop the monitoring process"""
    global monitoring_process
    
    proc = get_monitoring_process()
    if not proc:
        return jsonify({
            'success': False,
            'message': 'Monitoring is not running'
        })
    
    try:
        # Send SIGTERM to process group
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        
        # Wait for process to terminate
        try:
            proc.wait(timeout=10)
        except psutil.TimeoutExpired:
            # Force kill if it doesn't stop gracefully
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        
        monitoring_process = None
        
        return jsonify({
            'success': True,
            'message': 'Monitoring stopped successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to stop monitoring: {str(e)}'
        })

@app.route('/api/fetch_current_data', methods=['POST'])
def fetch_current_data():
    """Manually fetch current auction data"""
    try:
        # Initialize tracker
        tracker = JohnPyeAuctionTracker()
        
        # Login
        if not tracker.login():
            return jsonify({
                'success': False,
                'message': 'Failed to login to John Pye Auctions'
            })
        
        # Fetch data
        active_bids = tracker.get_active_bids()
        watchlist = tracker.get_watchlist()
        
        # Save data
        data = {
            'active_bids': active_bids,
            'watchlist': watchlist,
            'last_updated': datetime.now().isoformat(),
            'total_items': len(active_bids) + len(watchlist)
        }
        
        # Save to file
        os.makedirs('../data', exist_ok=True)
        with open('../data/monitoring_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        # Close tracker
        tracker.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully fetched {data["total_items"]} items',
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch data: {str(e)}'
        })

@app.route('/item/<lot_number>')
def view_item(lot_number):
    """View individual item details"""
    data = load_monitoring_data()
    
    # Find item in active bids or watchlist
    item = None
    for bid in data.get('active_bids', []):
        if bid.get('lot') == lot_number:
            item = bid
            item['type'] = 'active_bid'
            break
    
    if not item:
        for watch in data.get('watchlist', []):
            if watch.get('lot') == lot_number:
                item = watch
                item['type'] = 'watchlist'
                break
    
    if not item:
        return "Item not found", 404
    
    return render_template('item_detail.html', item=item)

if __name__ == '__main__':
    print("🌐 Starting John Pye Auctions Web Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔍 Press Ctrl+C to stop the web server")
    
    # Create data directory if it doesn't exist
    os.makedirs('../data', exist_ok=True)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)