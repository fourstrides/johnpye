#!/bin/bash

echo "🔍 John Pye Auction Tracker Dashboard Status Check"
echo "=================================================="
echo

# Check if dashboard process is running
DASHBOARD_PID=$(pgrep -f "realtime_dashboard.py")
if [ -z "$DASHBOARD_PID" ]; then
    echo "❌ Dashboard is NOT running"
    echo
    echo "🚀 To start the dashboard, run:"
    echo "   cd /home/ubuntu/projects/johnpye-auction-tracker"
    echo "   ./launch_dashboard.sh"
    exit 1
else
    echo "✅ Dashboard is running (PID: $DASHBOARD_PID)"
fi

# Check if port 8081 is listening
PORT_CHECK=$(ss -tlnp | grep ":8081")
if [ -z "$PORT_CHECK" ]; then
    echo "❌ Port 8081 is not listening"
    exit 1
else
    echo "✅ Port 8081 is listening"
fi

# Test local connection
LOCAL_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081)
if [ "$LOCAL_TEST" = "200" ]; then
    echo "✅ Local connection working (HTTP $LOCAL_TEST)"
else
    echo "❌ Local connection failed (HTTP $LOCAL_TEST)"
fi

# Get server IP addresses
echo
echo "🌐 Access URLs:"
echo "   Local: http://localhost:8081"
echo "   Local IP: http://127.0.0.1:8081"

# Get external IP addresses
for IP in $(hostname -I); do
    echo "   Network IP: http://$IP:8081"
done

echo
echo "📊 Recent dashboard activity:"
tail -5 /home/ubuntu/projects/johnpye-auction-tracker/logs/dashboard.log 2>/dev/null || echo "   No logs available"

echo
echo "🔧 If you can't access the dashboard:"
echo "   1. Make sure you're on the same network as this server"
echo "   2. Check if firewall is blocking port 8081"
echo "   3. Try accessing from localhost if you're on this machine"
echo "   4. Check the logs: tail -f /home/ubuntu/projects/johnpye-auction-tracker/logs/dashboard.log"

echo
echo "📱 Dashboard features:"
echo "   • Real-time auction data from John Pye"
echo "   • Live bid status monitoring (WINNING/OUTBID)"
echo "   • Watchlist tracking with price updates"
echo "   • SMS notifications (if Twilio configured)"
echo "   • Mobile-friendly responsive design"