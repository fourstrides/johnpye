#!/usr/bin/env python3
"""
Check if auction monitoring is currently running
"""

import psutil
import os
import json
from datetime import datetime

def check_monitoring_status():
    """Check if monitoring process is running"""
    monitoring_running = False
    monitoring_pid = None
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'start_monitoring.py' in ' '.join(cmdline):
                monitoring_running = True
                monitoring_pid = proc.pid
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Update monitoring data file with current status
    data_file = '../data/monitoring_data.json'
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            data['is_monitoring'] = monitoring_running
            data['monitoring_pid'] = monitoring_pid
            data['status_checked'] = datetime.now().isoformat()
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error updating status: {e}")
    
    return monitoring_running, monitoring_pid

def main():
    """Main function"""
    print("🔍 CHECKING MONITORING STATUS")
    print("=" * 40)
    
    is_running, pid = check_monitoring_status()
    
    if is_running:
        print(f"✅ Monitoring is RUNNING")
        print(f"📊 Process ID: {pid}")
        print(f"🔔 SMS notifications are ACTIVE")
        print(f"📱 You will receive SMS alerts when outbid")
    else:
        print(f"❌ Monitoring is STOPPED")
        print(f"📴 SMS notifications are INACTIVE")
        print(f"💡 Start monitoring from web dashboard or run:")
        print(f"   python start_monitoring.py")
    
    print()
    print("🌐 Web Dashboard: http://localhost:5000")

if __name__ == '__main__':
    main()