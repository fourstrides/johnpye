# John Pye Auction Tracker - Makefile Commands

This project includes a comprehensive Makefile for managing the dashboard and supporting services.

## Quick Start

```bash
# Quick Start (recommended)
make start && make sms-notify

# OR step by step
make start          # Start the dashboard
make status         # Check status  
make sms-status     # Check SMS functionality
make sms-notify     # Send real notification!
make logs           # View logs
make stop           # Stop services
```

## Available Commands

The commands are organized into logical groups for better usability:

### 🔧 Setup & Configuration
| Command | Description |
|---------|-------------|
| `make setup` | Create necessary directories and files |
| `make info` | Show project information |
| `make check` | Check system requirements |
| `make clean` | Clean up logs and temporary files |

### 📊 Dashboard Management
| Command | Description |
|---------|-------------|
| `make start` | Start the dashboard service |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make status` | Check service status |
| `make logs` | View recent logs |
| `make logs-tail` | Follow live logs (Ctrl+C to exit) |
| `make test` | Test dashboard API endpoints |
| `make dev` | Start in development mode with live logs |
| `make url` | Show dashboard URLs |

### 📱 SMS Setup & Configuration
| Command | Description |
|---------|-------------|
| `make sms-setup` | Setup Twilio credentials |
| `make sms-update` | Update Twilio credentials |
| `make sms-fix` | Fix SMS setup issues |

### ✅ SMS Testing & Validation
| Command | Description |
|---------|-------------|
| `make sms-test` | Quick SMS notification test |
| `make sms-validate` | Validate Twilio credentials |
| **`make sms-notify`** | **Send real auction notification SMS** |
| `make sms-direct` | Direct SMS test (simple) |
| `make sms-final` | Final SMS test (comprehensive) |
| `make sms-advanced` | Advanced Twilio testing |

### 📋 SMS Status & Diagnostics
| Command | Description |
|---------|-------------|
| `make sms-status` | Check SMS/Twilio account status |
| `make sms-diagnose` | Diagnose SMS problems |

### 🎬 SMS Demo & Help
| Command | Description |
|---------|-------------|
| `make sms-demo` | Demo SMS notifications |
| `make sms-help` | Show SMS command help |

## Features

✅ **Easy Management**: Simple commands to start, stop, and monitor services
✅ **Status Monitoring**: Real-time service status and port checking
✅ **Log Management**: View recent logs or follow live logs
✅ **API Testing**: Quick endpoint testing
✅ **Clean Setup**: Automatic directory and file creation
✅ **Development Mode**: Interactive development with live logs
✅ **SMS Notifications**: Complete Twilio SMS integration and testing
✅ **Notification Testing**: Comprehensive SMS diagnostics and validation

## Dashboard URLs

After running `make start`, the dashboard will be available at:
- **Local**: http://localhost:8081
- **Network**: http://[your-ip]:8081

## Service Management

The Makefile manages:
- 📊 **Dashboard Service** (Port 8081)
- 🔍 **Bid Tracking** (30-second updates)
- 📝 **Logging** (Centralized log management)
- 🗼️ **Data Storage** (JSON/CSV files)
- 📱 **SMS Notifications** (Twilio integration)
- 🧹 **Cleanup** (Temporary files and logs)

## Configuration

The Makefile uses these default settings:
- **Port**: 8081
- **Update Interval**: 30 seconds (for live bidding)
- **Log Directory**: `./logs/`
- **Data Directory**: `./data/`
- **PID Directory**: `./pids/`

## Examples

```bash
# Complete workflow
make check          # Verify system requirements
make start          # Start the dashboard
make status         # Verify it's running
make test           # Test the API
make logs           # Check recent activity
make stop           # Stop when done

# Development workflow  
make dev            # Start with live logs (interactive)

# Monitoring workflow
make start          # Start service
make logs-tail      # Follow logs in real-time
# Ctrl+C to exit log viewing
make status         # Check if still running

# SMS workflow
make sms-status     # Check Twilio account status
make sms-validate   # Validate credentials
make sms-notify     # Send real auction notification!
make sms-test       # Quick SMS test
make sms-demo       # Full notification demo
```

## Troubleshooting

- **Service won't start**: Run `make check` to verify requirements
- **Port already in use**: Run `make stop` first, then `make start`
- **Check logs**: Use `make logs` or `make logs-tail` to see what's happening
- **Clean slate**: Run `make clean` to remove old files, then `make start`
- **SMS not working**: Run `make sms-status` to check Twilio account
- **Invalid credentials**: Run `make sms-validate` to verify Twilio setup
- **SMS setup issues**: Run `make sms-diagnose` for detailed troubleshooting

The Makefile provides a robust, production-ready way to manage your John Pye Auction Tracker with watchlist deduplication, enhanced time extraction, and 30-second live updates!