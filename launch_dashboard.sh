#!/bin/bash

# Launch John Pye Auction Tracker Real-time Dashboard
# This script sets up the environment and starts the dashboard

echo "🚀 Launching John Pye Auction Tracker Dashboard..."
echo

# Check if we're in the right directory
if [ ! -d "src" ]; then
    echo "❌ Error: Please run this script from the johnpye-auction-tracker root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required environment variables are set
if [ -z "$JOHNPYE_USERNAME" ] || [ -z "$JOHNPYE_PASSWORD" ]; then
    echo "⚠️  Warning: JOHNPYE_USERNAME or JOHNPYE_PASSWORD not set in environment"
    echo "Please ensure your .env file contains these credentials"
    echo
fi

# Check if Twilio credentials are set (for SMS notifications)
if [ -z "$TWILIO_ACCOUNT_SID" ] || [ -z "$TWILIO_AUTH_TOKEN" ]; then
    echo "ℹ️  Info: Twilio credentials not set - SMS notifications will be disabled"
    echo
fi

# Change to src directory
cd src

# Create logs directory if it doesn't exist
mkdir -p ../logs
mkdir -p ../data

echo "📊 Starting Real-time Dashboard Server..."
echo "🌐 Dashboard will be available at: http://localhost:8081"
echo "⏹️  Press Ctrl+C to stop the server"
echo
echo "✨ Features available:"
echo "   • Real-time data from John Pye website"
echo "   • Live bid status monitoring"
echo "   • Watchlist tracking"
echo "   • SMS alerts for important events"
echo "   • Modern responsive web interface"
echo

# Start the dashboard
python realtime_dashboard.py