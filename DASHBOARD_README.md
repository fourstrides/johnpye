# John Pye Auction Tracker - Real-time Dashboard

## 🎯 Overview

This enhanced real-time dashboard provides comprehensive monitoring of your John Pye auction activities with a modern, user-friendly web interface.

## ✨ Key Features

### 🔴 Real-time Data
- **Live Updates**: Automatic refresh every 5 minutes when monitoring is active
- **Direct Integration**: Connects directly to John Pye website using your credentials
- **Instant Sync**: Real-time status changes for all your bids and watchlist items

### 📊 Comprehensive Monitoring
- **Active Bids**: Track all your current bids with status (WINNING/OUTBID)
- **Watchlist Items**: Monitor items you're interested in
- **Status Indicators**: Visual cues for bid status and ending times
- **Statistics Overview**: Quick summary cards showing counts and status

### 🎨 Modern Interface
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Clean UI**: Modern design with intuitive navigation
- **Visual Status**: Color-coded indicators for different bid states:
  - 🟢 **Winning bids**: Green background
  - 🔴 **Outbid items**: Red background  
  - 🟡 **Ending soon**: Yellow highlight for auctions ending within 1 hour
- **Toast Notifications**: Real-time feedback for all actions

### 📱 Smart Notifications
- **SMS Alerts**: Automatic SMS notifications for important events (requires Twilio setup)
- **Status Updates**: Notifications when tracker starts/stops
- **Error Alerts**: Immediate SMS alerts for any issues

### ⚡ Advanced Controls
- **Start/Stop Monitoring**: Easy control over the tracking process
- **Manual Refresh**: Force update data on demand
- **Status Tracking**: Real-time display of last update and next scheduled update
- **Keyboard Shortcuts**: 
  - `Ctrl+R`: Manual refresh
  - `Ctrl+S`: Toggle monitoring

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser installed
- Valid John Pye auction account
- (Optional) Twilio account for SMS notifications

### Quick Launch
```bash
# From the project root directory
./launch_dashboard.sh
```

### Manual Launch
```bash
# Activate virtual environment
source venv/bin/activate

# Change to src directory
cd src

# Run the dashboard
python realtime_dashboard.py
```

The dashboard will be available at: **http://localhost:8081**

## 🎮 How to Use

### 1. Start Monitoring
1. Open the dashboard in your web browser
2. Click the **"Start Monitoring"** button
3. Wait for initial data load (5-10 seconds)
4. The tracker will automatically update every 5 minutes

### 2. View Your Data
- **Active Bids Section**: Shows all your current bids with:
  - Item title and lot number
  - Current bid amount
  - Your maximum bid
  - Bid status (WINNING/OUTBID)
  - Auction end time
  - Direct link to auction page

- **Watchlist Section**: Displays items you're watching with:
  - Item details and current bid
  - End time information
  - Status indicators

### 3. Monitor Status
- **Status Indicator**: Green dot = monitoring active, Gray dot = stopped
- **Statistics Cards**: Overview of your bidding activity
- **Control Panel**: Shows last update time and next scheduled update

### 4. Stop Monitoring
- Click **"Stop Monitoring"** to pause the automatic updates
- Data remains visible but won't refresh automatically

## 📋 Dashboard Sections

### Header
- **Status Indicator**: Shows if monitoring is active
- **Refresh Button**: Manual data refresh
- **Title and Description**: Clear identification of the tool

### Stats Overview Cards
1. **Active Bids**: Total number of your active bids
2. **Winning**: Number of bids you're currently winning
3. **Outbid**: Number of bids where you've been outbid
4. **Watchlist**: Total watchlist items count

### Control Panel
- **Real-time Monitoring Toggle**: Start/stop automatic updates
- **Status Information**: Shows update timing and SMS notification status
- **System Health**: Last update time and next scheduled update

### Active Bids Display
- **Comprehensive Information**: All bid details in an easy-to-read format
- **Visual Status Indicators**: Color coding and icons for quick status identification
- **Direct Links**: Click to open auction pages in new tabs
- **Ending Soon Alerts**: Special highlighting for auctions ending within 1 hour

### Watchlist Display
- **Item Monitoring**: Track items you haven't bid on yet
- **Price Tracking**: Monitor current bid amounts
- **Timing Information**: See when auctions end
- **Quick Access**: Direct links to auction pages

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root with:

```env
# John Pye Credentials (Required)
JOHNPYE_USERNAME=your_email@example.com
JOHNPYE_PASSWORD=your_password

# Twilio SMS Notifications (Optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_FROM=+1234567890
TWILIO_PHONE_TO=+0987654321

# Email Notifications (Optional)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=notifications@example.com
```

### Update Frequency
The dashboard checks for updates every 5 minutes by default. This can be modified in the code by changing the `update_interval` value.

## 📱 Mobile Usage

The dashboard is fully responsive and works great on mobile devices:
- **Touch-friendly**: Large buttons and easy navigation
- **Optimized Layout**: Content adjusts to screen size
- **Fast Loading**: Efficient data handling for mobile networks
- **Offline Viewing**: Previously loaded data remains visible

## 🔧 Technical Details

### Architecture
- **Backend**: Flask web server with real-time data fetching
- **Frontend**: Modern HTML5/CSS3/JavaScript with Tailwind CSS
- **Data Storage**: JSON files for caching and persistence
- **Web Scraping**: Selenium WebDriver for John Pye integration
- **Notifications**: Twilio API for SMS alerts

### API Endpoints
- `GET /` - Main dashboard interface
- `GET /api/tracker-status` - Current tracker status
- `POST /api/start-tracker` - Start monitoring
- `POST /api/stop-tracker` - Stop monitoring  
- `GET /api/active-bids` - Get active bids data
- `GET /api/watchlist` - Get watchlist data

### Data Flow
1. **Login**: Authenticates with John Pye website
2. **Scraping**: Extracts bid and watchlist data
3. **Processing**: Cleans and structures the data
4. **Storage**: Saves to JSON for API access
5. **Display**: Real-time updates in web interface

## 🛡️ Security & Privacy

- **Local Processing**: All data processing happens on your machine
- **Secure Storage**: Credentials stored in environment variables
- **No Data Sharing**: Your auction data never leaves your system
- **HTTPS Ready**: Can be configured for secure connections

## 🚨 Troubleshooting

### Common Issues

**Dashboard won't start**
- Check that port 8081 is available
- Ensure Chrome/Chromium is installed
- Verify Python dependencies are installed

**Login fails**
- Verify JOHNPYE_USERNAME and JOHNPYE_PASSWORD in .env
- Check if account is active on John Pye website
- Look for Cloudflare protection delays

**No data showing**
- Ensure you have active bids or watchlist items on John Pye
- Check browser console for JavaScript errors
- Verify tracker status in control panel

**SMS notifications not working**
- Verify Twilio credentials in .env file
- Check Twilio account balance and phone number verification
- Look for error messages in console logs

### Logs and Debugging
- Dashboard logs: Console output when running
- Tracker logs: `../logs/enhanced_tracker.log`
- Browser console: F12 developer tools for frontend issues

## 🔄 Updates and Maintenance

The dashboard automatically handles most maintenance tasks:
- **Data Cleanup**: Old cache files are managed automatically  
- **Error Recovery**: Automatic retry on connection issues
- **Status Monitoring**: Self-monitoring for health checks

## 📧 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review console logs for error messages
3. Verify all configuration settings
4. Test with manual scripts first to isolate issues

## 🎉 Success Indicators

You'll know everything is working when you see:
- ✅ Green status indicator showing "Monitoring Active"
- 📊 Real data in your active bids and watchlist sections
- ⏰ Regular update times showing in the control panel
- 📱 SMS notifications arriving for important events

Enjoy your enhanced auction tracking experience! 🎯