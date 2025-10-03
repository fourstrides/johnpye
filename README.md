# John Pye Auctions Watchlist Tracker

A Python application that automatically monitors your watchlist on John Pye Auctions (https://www.johnpyeauctions.co.uk) and tracks bidding activity on your watched items.

## Features

- **Automated Login**: Securely logs into your John Pye Auctions account
- **Watchlist Monitoring**: Continuously monitors all items in your watchlist
- **Bid Tracking**: Tracks bid changes and price increases
- **Real-time Notifications**: Desktop notifications for important events
- **Data Export**: Saves tracking data to CSV files for analysis
- **Configurable Settings**: Customizable monitoring intervals and thresholds
- **Headless Operation**: Runs in the background without opening browser windows

## Requirements

- Python 3.8 or higher
- Chrome or Chromium browser
- Linux environment (Ubuntu recommended)

## Installation

1. **Clone or download this project** (if you received it from elsewhere)

2. **Navigate to the project directory**:
   ```bash
   cd johnpye-auction-tracker
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your credentials**:
   ```bash
   cp .env.template .env
   nano .env  # or use your preferred editor
   ```
   
   Edit the `.env` file and add your John Pye Auctions credentials:
   ```
   JOHNPYE_USERNAME=your_username_here
   JOHNPYE_PASSWORD=your_password_here
   ```

## Usage

### Basic Monitoring

To start monitoring your watchlist:

```bash
cd src
python main.py
```

The application will:
1. Log into your John Pye Auctions account
2. Retrieve your current watchlist
3. Monitor each item for changes
4. Send notifications when bids increase or auctions are ending soon
5. Save tracking data to the `data/` directory

### Stopping the Monitor

Press `Ctrl+C` to stop the monitoring process gracefully.

## Configuration

The application creates a configuration file at `config/settings.json` with default settings. You can modify these settings to customize the behavior:

### Monitoring Settings
- `check_interval_seconds`: How often to check for updates (default: 300 seconds/5 minutes)
- `headless_browser`: Run browser in headless mode (default: true)
- `max_retries`: Maximum retries for failed operations (default: 3)
- `timeout_seconds`: Timeout for web operations (default: 30)

### Notification Settings
- `enabled`: Enable/disable notifications (default: true)
- `bid_increase_threshold`: Minimum bid increase to trigger notification (default: £10.00)
- `ending_soon_threshold_minutes`: Minutes before end to send "ending soon" notification (default: 60)

### Data Storage Settings
- `save_historical_data`: Save tracking data to files (default: true)
- `cleanup_old_data_days`: Days to keep old data files (default: 30)
- `export_format`: Format for exported data (default: "csv")

## Project Structure

```
johnpye-auction-tracker/
├── src/                          # Source code
│   ├── main.py                   # Main application entry point
│   ├── auction_item.py           # Data class for auction items
│   ├── config_manager.py         # Configuration management
│   └── notification_manager.py   # Notification handling
├── config/                       # Configuration files
├── data/                         # Exported tracking data
├── logs/                         # Application logs
├── docs/                         # Additional documentation
├── tests/                        # Unit tests (future)
├── requirements.txt              # Python dependencies
├── .env.template                 # Environment variables template
├── .env                          # Your credentials (not in git)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Data Files

The application saves tracking data in the `data/` directory:

- `watchlist_YYYYMMDD_HHMMSS.csv`: Snapshots of your watchlist at each check
- Each file contains: item title, lot number, current bid, end time, URL, timestamps

## Notifications

The application sends desktop notifications for:

- **Bid Increases**: When someone outbids the current amount
- **Ending Soon**: When an auction is about to end (configurable threshold)
- **New Items**: When items are added to your watchlist
- **Removed Items**: When items are removed from your watchlist
- **Errors**: When the application encounters problems

## Troubleshooting

### Common Issues

1. **Login Failed**:
   - Check your username and password in the `.env` file
   - Verify your John Pye Auctions account is active
   - Check if the website login page has changed

2. **Chrome Driver Issues**:
   - The application automatically downloads the Chrome driver
   - Ensure Chrome/Chromium is installed on your system
   - Try running with `headless_browser: false` to see what's happening

3. **No Notifications**:
   - Ensure `notify-send` is installed: `sudo apt install libnotify-bin`
   - Check that notifications are enabled in the config
   - Test notifications with the test function

4. **Permission Errors**:
   - Ensure the application has write permissions to `logs/`, `data/`, and `config/` directories
   - Check that the `.env` file is readable

### Debug Mode

To run in debug mode with visible browser:
1. Edit `config/settings.json`
2. Set `"headless_browser": false` in the monitoring section
3. Restart the application

### Logs

Check the log file at `logs/auction_tracker.log` for detailed information about the application's operation.

## Security Notes

- Your credentials are stored locally in the `.env` file
- The `.env` file is excluded from git to prevent accidental commits
- Never share your `.env` file or commit it to version control
- Consider using application-specific passwords if your account supports them

## Limitations

- Only works with John Pye Auctions website
- Requires Chrome/Chromium browser
- Monitoring frequency is limited to prevent overwhelming the website
- HTML structure changes on the website may require code updates

## Future Enhancements

Potential improvements for future versions:

- Email notifications
- SMS notifications via Twilio
- Webhook notifications
- Web dashboard for monitoring
- Mobile app companion
- Support for other auction sites
- Automated bidding (with user confirmation)
- Price prediction algorithms
- Historical price analysis

## Legal Disclaimer

This application is for personal use only. Users are responsible for:
- Complying with John Pye Auctions Terms of Service
- Not overwhelming the website with excessive requests
- Respecting rate limits and website policies
- Using the application ethically and legally

The developers are not responsible for any misuse of this application or any consequences resulting from its use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the log files for error messages
3. Ensure all requirements are properly installed
4. Verify your configuration settings

## License

This project is provided as-is for personal use. Please respect the terms of service of John Pye Auctions and use this application responsibly.