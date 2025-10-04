# John Pye Auction Tracker - Makefile Commands

This project includes a comprehensive Makefile for managing the dashboard and supporting services.

## Quick Start

```bash
# Start the dashboard
make start

# Check status
make status

# View logs
make logs

# Stop services
make stop
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make start` | Start the dashboard service |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make status` | Check service status |
| `make logs` | View recent logs |
| `make logs-tail` | Follow live logs (Ctrl+C to exit) |
| `make test` | Test dashboard API endpoints |
| `make url` | Show dashboard URLs |
| `make info` | Show project information |
| `make check` | Check system requirements |
| `make setup` | Create necessary directories |
| `make clean` | Clean up logs and temporary files |
| `make dev` | Start in development mode with live logs |

## Features

✅ **Easy Management**: Simple commands to start, stop, and monitor services
✅ **Status Monitoring**: Real-time service status and port checking
✅ **Log Management**: View recent logs or follow live logs
✅ **API Testing**: Quick endpoint testing
✅ **Clean Setup**: Automatic directory and file creation
✅ **Development Mode**: Interactive development with live logs

## Dashboard URLs

After running `make start`, the dashboard will be available at:
- **Local**: http://localhost:8081
- **Network**: http://[your-ip]:8081

## Service Management

The Makefile manages:
- 📊 **Dashboard Service** (Port 8081)
- 🔍 **Bid Tracking** (30-second updates)
- 📝 **Logging** (Centralized log management)
- 🗂️ **Data Storage** (JSON/CSV files)
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
```

## Troubleshooting

- **Service won't start**: Run `make check` to verify requirements
- **Port already in use**: Run `make stop` first, then `make start`
- **Check logs**: Use `make logs` or `make logs-tail` to see what's happening
- **Clean slate**: Run `make clean` to remove old files, then `make start`

The Makefile provides a robust, production-ready way to manage your John Pye Auction Tracker with watchlist deduplication, enhanced time extraction, and 30-second live updates!