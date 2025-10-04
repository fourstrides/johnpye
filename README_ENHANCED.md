# John Pye Auctions Watchlist Tracker - Enhanced Edition

A comprehensive Python application that automatically monitors your watchlist on John Pye Auctions (https://www.johnpyeauctions.co.uk) with advanced features including **web dashboard**, **SMS/email notifications**, and **real-time bid tracking**.

## 🚀 New Features Added

### ✨ Web Dashboard
- **Modern responsive interface** built with Tailwind CSS
- **Real-time monitoring status** with auto-refresh
- **Interactive watchlist management** 
- **Bid history tracking** with timeline view
- **System configuration** through web interface
- **Live notifications testing**

### 📱 Enhanced Notifications
- **SMS notifications** via Twilio integration
- **Email notifications** with SMTP support  
- **Desktop notifications** (Linux/Ubuntu)
- **Multi-channel alerts** for important events
- **Customizable notification thresholds**

### 🎯 Advanced Bid Tracking
- **Real-time bid monitoring** with change detection
- **Intelligent alerts** for significant price increases
- **Auction ending warnings** with configurable timing
- **New item detection** when added to watchlist
- **Removed item notifications** when items disappear

### 🧪 Comprehensive Testing
- **Full test suite** with 25+ unit tests
- **Integration testing** for all components
- **Mock testing** for external dependencies
- **Automated test runner** with detailed reporting

## 📋 Features Overview

### Core Functionality
- ✅ **Automated Login**: Secure authentication with John Pye Auctions
- ✅ **Watchlist Monitoring**: Continuous monitoring of all watched items
- ✅ **Bid Tracking**: Real-time detection of bid changes and increases
- ✅ **Data Export**: Automatic CSV export with timestamps
- ✅ **Configurable Settings**: Customizable monitoring intervals and thresholds
- ✅ **Headless Operation**: Runs silently in the background

### Advanced Features
- 🆕 **Web Dashboard**: Modern browser-based monitoring interface
- 🆕 **SMS Alerts**: Instant text notifications via Twilio
- 🆕 **Email Notifications**: SMTP-based email alerts
- 🆕 **Multi-threaded**: Dashboard and tracker run simultaneously
- 🆕 **API Endpoints**: RESTful API for integration
- 🆕 **Real-time Updates**: Live status updates and notifications

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Chrome or Chromium browser
- Linux environment (Ubuntu recommended)

### Quick Setup

1. **Clone and navigate to project**:
   ```bash
   cd johnpye-auction-tracker
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials**:
   ```bash
   cp .env.template .env
   nano .env  # Edit with your credentials
   ```

## ⚙️ Configuration

### Basic Configuration (.env file)

```bash
# John Pye Auctions credentials
JOHNPYE_USERNAME=your_username_here
JOHNPYE_PASSWORD=your_password_here

# SMS notifications (optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
MY_PHONE_NUMBER=+1234567890

# Email notifications (optional)
EMAIL_ENABLED=true
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=notifications@yourdomain.com
```

### Advanced Settings

The system creates a `config/settings.json` file with advanced options:

```json
{
  "monitoring": {
    "check_interval_seconds": 300,
    "headless_browser": true,
    "max_retries": 3,
    "timeout_seconds": 30
  },
  "notifications": {
    "enabled": true,
    "bid_increase_threshold": 10.00,
    "ending_soon_threshold_minutes": 60
  },
  "data_storage": {
    "save_historical_data": true,
    "cleanup_old_data_days": 30,
    "export_format": "csv"
  }
}
```

## 🚀 Usage Options

### Option 1: Traditional Command Line
```bash
cd src
python main.py
```

### Option 2: With Web Dashboard (Recommended)
```bash
cd src
python run_with_dashboard.py
```

Then open your browser to: **http://localhost:8080**

### Option 3: Custom Dashboard Port
```bash
python run_with_dashboard.py 9000  # Use port 9000
```

### Option 4: Background Operation
```bash
nohup python run_with_dashboard.py > ../logs/tracker.log 2>&1 &
```

## 📊 Web Dashboard Features

### Main Dashboard
- **Status Cards**: Monitor system status, item count, checks performed
- **Watchlist Overview**: Current items with bid amounts and links
- **Recent Activity**: Timeline of bid changes and notifications
- **System Information**: Startup time, last check, configuration
- **Quick Actions**: Test notifications, access settings

### API Endpoints
- `GET /api/status` - Current monitoring status
- `GET /api/watchlist` - Current watchlist items
- `GET /api/history` - Bid history and activity
- `GET /api/logs` - Recent application logs
- `POST /api/test-notification` - Test notification systems
- `GET/POST /api/config` - System configuration

## 📱 Notification Types

### SMS Notifications (via Twilio)
- 🔔 **Bid Increases**: When bids exceed threshold
- ⏰ **Ending Soon**: Configurable time warnings
- ➕ **New Items**: Items added to watchlist
- ➖ **Removed Items**: Items removed from watchlist
- 🚨 **System Alerts**: Errors and status changes

### Email Notifications
- 📧 **Comprehensive reports** with full details
- 🔗 **Direct links** to auction items
- 📈 **Bid history** tracking
- ⚡ **Instant delivery** via SMTP

### Desktop Notifications
- 💻 **Native Linux notifications** via notify-send
- 🖥️ **Fallback console output** if notify-send unavailable
- 🎨 **Rich formatting** with icons and colors

## 🧪 Testing

### Run Complete Test Suite
```bash
cd src
python test_suite.py
```

### Test Individual Components
```bash
# Test notifications only
python -c "from notification_manager import NotificationManager; NotificationManager().test_notifications()"

# Test dashboard only
python web_dashboard.py

# Test configuration
python -c "from config_manager import ConfigManager; print('Config OK:', ConfigManager().get_check_interval())"
```

## 📁 Enhanced Project Structure

```
johnpye-auction-tracker/
├── src/                          # Source code
│   ├── main.py                   # Core auction tracker
│   ├── run_with_dashboard.py     # 🆕 Integrated runner
│   ├── web_dashboard.py          # 🆕 Web dashboard
│   ├── auction_item.py           # Auction item data model
│   ├── config_manager.py         # Configuration management
│   ├── notification_manager.py   # 📱 Enhanced notifications
│   ├── test_suite.py             # 🧪 Comprehensive tests
│   └── templates/
│       └── dashboard.html        # 🆕 Modern dashboard UI
├── config/                       # Configuration files
├── data/                         # CSV exports and tracking data
├── logs/                         # Application and error logs
├── requirements.txt              # 📦 Updated dependencies
├── .env.template                 # 📝 Enhanced environment template
├── .env                          # Your credentials
└── README_ENHANCED.md            # This enhanced documentation
```

## 🔧 Advanced Usage

### Custom Notification Thresholds
```python
# Modify config/settings.json
{
  "notifications": {
    "bid_increase_threshold": 25.00,    # Alert on £25+ increases
    "ending_soon_threshold_minutes": 30 # Alert 30min before end
  }
}
```

### Integration with External Systems
```python
# Use the API for external integration
import requests

# Get current status
response = requests.get('http://localhost:8080/api/status')
status = response.json()

# Get watchlist
response = requests.get('http://localhost:8080/api/watchlist')
watchlist = response.json()
```

### Custom Dashboard Styling
The dashboard uses Tailwind CSS and can be customized by editing:
- `src/templates/dashboard.html`
- Add custom CSS in the `<style>` section

## 🚨 Troubleshooting

### Common Issues & Solutions

1. **"SMS not sending"**:
   ```bash
   # Check Twilio credentials in .env
   python -c "from notification_manager import NotificationManager; nm = NotificationManager(); print('Twilio OK:', nm.twilio_client is not None)"
   ```

2. **"Email notifications failing"**:
   ```bash
   # Test SMTP settings
   python -c "from notification_manager import NotificationManager; nm = NotificationManager(); print('Email OK:', nm.email_enabled)"
   ```

3. **"Dashboard not accessible"**:
   ```bash
   # Check if port is in use
   netstat -tulpn | grep :8080
   
   # Try different port
   python run_with_dashboard.py 9000
   ```

4. **"Tests failing"**:
   ```bash
   # Run individual test components
   python test_suite.py
   
   # Check dependencies
   pip install -r requirements.txt
   ```

### Debug Mode
```bash
# Run with verbose logging
python main.py --verbose

# Run dashboard in debug mode
python web_dashboard.py  # Standalone debug mode
```

## 🔐 Security Best Practices

- ✅ **Environment Variables**: Credentials stored in `.env` (excluded from git)
- ✅ **No Hardcoded Secrets**: All sensitive data externalized
- ✅ **Secure Defaults**: Safe configuration defaults
- ✅ **Rate Limiting**: Respectful request intervals to auction site
- ✅ **Input Validation**: Sanitized data processing
- ✅ **HTTPS Ready**: Dashboard supports HTTPS deployment

## 🎯 Performance

- **Low Resource Usage**: Headless browser operation
- **Efficient Monitoring**: Configurable check intervals
- **Background Processing**: Non-blocking dashboard operation
- **Memory Management**: Automatic cleanup of old data
- **Concurrent Operation**: Multi-threaded dashboard + tracker

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd johnpye-auction-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/test_suite.py  # Ensure all tests pass
```

### Code Style
- Follow PEP 8 Python style guidelines
- Add docstrings for all functions
- Include type hints where appropriate
- Write tests for new features

## 📜 License

This project is provided as-is for personal use. Please respect John Pye Auctions' Terms of Service and use responsibly.

## 🙋‍♂️ Support

### Quick Diagnostics
```bash
# System health check
cd src && python -c "
from main import JohnPyeAuctionTracker
from web_dashboard import AuctionDashboard  
from notification_manager import NotificationManager
print('✅ All imports successful')
"
```

### Getting Help
1. **Check logs**: `logs/auction_tracker.log`
2. **Run tests**: `python src/test_suite.py`
3. **Verify config**: Check `.env` and `config/settings.json`
4. **Test notifications**: Use dashboard "Test Notifications" button

---

## 🎉 Success! 

**The John Pye Auction Tracker is now a comprehensive, production-ready monitoring solution with:**

- 🎯 **Enhanced monitoring** with real-time bid tracking
- 📊 **Modern web dashboard** for easy management  
- 📱 **Multi-channel notifications** (SMS, email, desktop)
- 🧪 **Full test coverage** for reliability
- 🔧 **Advanced configuration** options
- 📈 **Scalable architecture** for future enhancements

**Ready to monitor your auctions like a pro!** 🚀