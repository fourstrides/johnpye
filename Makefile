# John Pye Auction Tracker Makefile
# Manages dashboard and supporting services

PYTHON = python3
PROJECT_DIR = $(PWD)
SRC_DIR = $(PROJECT_DIR)/src
DATA_DIR = $(PROJECT_DIR)/data
LOGS_DIR = $(PROJECT_DIR)/logs
PID_DIR = $(PROJECT_DIR)/pids
DASHBOARD_PORT = 8081
DASHBOARD_PID = $(PID_DIR)/dashboard.pid
DASHBOARD_LOG = $(LOGS_DIR)/dashboard.log

# Colors
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
CYAN = \033[0;36m
NC = \033[0m

.PHONY: help setup info check clean \
		start stop restart status logs logs-tail test dev url \
		sms-setup sms-update sms-fix \
		sms-test sms-validate sms-direct sms-final sms-advanced sms-notify \
		sms-status sms-diagnose sms-delivery sms-troubleshoot \
		sms-demo sms-help

all: help

#==============================================================================
# HELP & INFORMATION
#==============================================================================

help: ## Show grouped command help
	@echo "$(CYAN)John Pye Auction Tracker Management$(NC)"
	@echo "$(CYAN)====================================$(NC)"
	@echo ""
	@echo "$(GREEN)🔧 Setup & Configuration:$(NC)"
	@echo "  $(YELLOW)setup$(NC)           Create directories and files"
	@echo "  $(YELLOW)info$(NC)            Show project information"
	@echo "  $(YELLOW)check$(NC)           Check system requirements"
	@echo "  $(YELLOW)clean$(NC)           Clean up temporary files"
	@echo ""
	@echo "$(GREEN)📊 Dashboard Management:$(NC)"
	@echo "  $(YELLOW)start$(NC)           Start the dashboard service"
	@echo "  $(YELLOW)stop$(NC)            Stop all services"
	@echo "  $(YELLOW)restart$(NC)         Restart all services"
	@echo "  $(YELLOW)status$(NC)          Check service status"
	@echo "  $(YELLOW)logs$(NC)            View recent logs"
	@echo "  $(YELLOW)logs-tail$(NC)       Follow live logs"
	@echo "  $(YELLOW)test$(NC)            Test dashboard API"
	@echo "  $(YELLOW)dev$(NC)             Development mode with live logs"
	@echo "  $(YELLOW)url$(NC)             Show dashboard URLs"
	@echo ""
	@echo "$(GREEN)📱 SMS Setup & Configuration:$(NC)"
	@echo "  $(YELLOW)sms-setup$(NC)       Setup Twilio credentials"
	@echo "  $(YELLOW)sms-update$(NC)      Update Twilio credentials"
	@echo "  $(YELLOW)sms-fix$(NC)         Fix SMS setup issues"
	@echo ""
	@echo "$(GREEN)✅ SMS Testing & Validation:$(NC)"
	@echo "  $(YELLOW)sms-test$(NC)        Quick SMS notification test"
	@echo "  $(YELLOW)sms-validate$(NC)    Validate Twilio credentials"
	@echo "  $(YELLOW)sms-notify$(NC)      Send real auction notification SMS"
	@echo "  $(YELLOW)sms-direct$(NC)      Direct SMS test (simple)"
	@echo "  $(YELLOW)sms-final$(NC)       Final SMS test (comprehensive)"
	@echo "  $(YELLOW)sms-advanced$(NC)    Advanced Twilio testing"
	@echo ""
	@echo "$(GREEN)📋 SMS Status & Diagnostics:$(NC)"
	@echo "  $(YELLOW)sms-status$(NC)      Check SMS/Twilio account status"
	@echo "  $(YELLOW)sms-diagnose$(NC)    Diagnose SMS problems"
	@echo "  $(YELLOW)sms-delivery$(NC)    Check SMS delivery status"
	@echo "  $(YELLOW)sms-troubleshoot$(NC) Troubleshoot delivery issues"
	@echo ""
	@echo "$(GREEN)🎬 SMS Demo & Help:$(NC)"
	@echo "  $(YELLOW)sms-demo$(NC)        Demo SMS notifications"
	@echo "  $(YELLOW)sms-help$(NC)        Show SMS command help"
	@echo ""
	@echo "$(BLUE)💡 Quick Start: make start && make sms-notify$(NC)"

#==============================================================================
# SETUP & CONFIGURATION
#==============================================================================

setup: ## Create necessary directories and files
	@echo "$(CYAN)🔧 Setting up project structure...$(NC)"
	@mkdir -p $(DATA_DIR) $(LOGS_DIR) $(PID_DIR)
	@touch $(DASHBOARD_LOG)
	@echo "$(GREEN)✅ Project setup complete$(NC)"

info: ## Show project information
	@echo "$(CYAN)John Pye Auction Tracker$(NC)"
	@echo "$(CYAN)========================$(NC)"
	@echo "$(BLUE)Project Directory: $(PROJECT_DIR)$(NC)"
	@echo "$(BLUE)Dashboard Port:    $(DASHBOARD_PORT)$(NC)"
	@echo "$(BLUE)Update Interval:   30 seconds$(NC)"
	@echo "$(BLUE)Data Directory:    $(DATA_DIR)$(NC)"
	@echo "$(BLUE)Logs Directory:    $(LOGS_DIR)$(NC)"
	@echo ""
	@echo "$(GREEN)Features:$(NC)"
	@echo "  • Real-time bid monitoring"
	@echo "  • Watchlist tracking with deduplication"
	@echo "  • Enhanced time extraction (precise remaining time)"
	@echo "  • 30-second live updates for active bidding"
	@echo "  • SMS notifications"
	@echo "  • Web dashboard interface"

check: ## Check system requirements
	@echo "$(CYAN)🔍 Checking system requirements...$(NC)"
	@command -v $(PYTHON) >/dev/null 2>&1 && echo "$(GREEN)✅ Python3 available$(NC)" || echo "$(RED)❌ Python3 not found$(NC)"
	@command -v chromium-browser >/dev/null 2>&1 && echo "$(GREEN)✅ Chromium browser available$(NC)" || echo "$(RED)❌ Chromium browser not found$(NC)"
	@command -v chromedriver >/dev/null 2>&1 && echo "$(GREEN)✅ ChromeDriver available$(NC)" || echo "$(RED)❌ ChromeDriver not found$(NC)"
	@test -f .env && echo "$(GREEN)✅ .env file exists$(NC)" || echo "$(YELLOW)⚠️  .env file not found$(NC)"

clean: ## Clean up logs and temporary files
	@echo "$(CYAN)🧹 Cleaning up...$(NC)"
	@rm -f $(LOGS_DIR)/*.log $(PID_DIR)/*.pid
	@rm -f $(DATA_DIR)/*.json $(DATA_DIR)/*.csv
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

#==============================================================================
# DASHBOARD MANAGEMENT
#==============================================================================

start: setup ## Start the dashboard service
	@echo "$(CYAN)🚀 Starting John Pye Auction Tracker Dashboard...$(NC)"
	@cd $(PROJECT_DIR) && nohup $(PYTHON) $(SRC_DIR)/realtime_dashboard.py > $(DASHBOARD_LOG) 2>&1 & echo $$! > $(DASHBOARD_PID)
	@sleep 3
	@if [ -f $(DASHBOARD_PID) ] && kill -0 `cat $(DASHBOARD_PID)` 2>/dev/null; then \
		echo "$(GREEN)✅ Dashboard started successfully (PID: `cat $(DASHBOARD_PID)`)$(NC)"; \
		echo "$(BLUE)📊 Dashboard URL: http://localhost:$(DASHBOARD_PORT)$(NC)"; \
		echo "$(BLUE)🌐 Network URL: http://`hostname -I | awk '{print $$1}'`:$(DASHBOARD_PORT)$(NC)"; \
	else \
		echo "$(RED)❌ Failed to start dashboard$(NC)"; \
		echo "Check logs with: make logs"; \
	fi

stop: ## Stop all services
	@echo "$(CYAN)🛑 Stopping all services...$(NC)"
	@if [ -f $(DASHBOARD_PID) ]; then \
		kill `cat $(DASHBOARD_PID)` > /dev/null 2>&1 || true; \
		rm -f $(DASHBOARD_PID); \
	fi
	@echo "$(GREEN)✅ All services stopped$(NC)"

restart: stop start ## Restart all services
	@echo "$(GREEN)🔄 Services restarted$(NC)"

status: ## Check service status
	@echo "$(CYAN)📊 Service Status$(NC)"
	@echo "$(CYAN)===============$(NC)"
	@if [ -f $(DASHBOARD_PID) ] && kill -0 `cat $(DASHBOARD_PID)` 2>/dev/null; then \
		echo "$(GREEN)✅ Dashboard: Running (PID: `cat $(DASHBOARD_PID)`)$(NC)"; \
		echo "$(BLUE)   URL: http://localhost:$(DASHBOARD_PORT)$(NC)"; \
	else \
		echo "$(RED)❌ Dashboard: Not running$(NC)"; \
	fi
	@echo ""
	@echo "$(CYAN)Port Status:$(NC)"
	@if ss -tlnp | grep -q ":$(DASHBOARD_PORT) "; then \
		echo "$(GREEN)✅ Port $(DASHBOARD_PORT): In use$(NC)"; \
	else \
		echo "$(RED)❌ Port $(DASHBOARD_PORT): Free$(NC)"; \
	fi

logs: ## View recent logs
	@echo "$(CYAN)📋 Recent Dashboard Logs$(NC)"
	@echo "$(CYAN)========================$(NC)"
	@if [ -f $(DASHBOARD_LOG) ]; then \
		tail -n 50 $(DASHBOARD_LOG); \
	else \
		echo "$(YELLOW)No log file found$(NC)"; \
	fi

logs-tail: ## Follow live logs
	@echo "$(CYAN)📋 Following Dashboard Logs (Ctrl+C to exit)$(NC)"
	@echo "$(CYAN)============================================$(NC)"
	@if [ -f $(DASHBOARD_LOG) ]; then \
		tail -f $(DASHBOARD_LOG); \
	else \
		echo "$(YELLOW)No log file found$(NC)"; \
	fi

test: ## Test dashboard API
	@echo "$(CYAN)🧪 Testing API endpoints...$(NC)"
	@curl -s http://localhost:$(DASHBOARD_PORT)/api/tracker-status > /dev/null && echo "$(GREEN)✅ API responding$(NC)" || echo "$(RED)❌ API not responding$(NC)"

dev: ## Start in development mode with live logs
	@echo "$(CYAN)🔧 Starting in development mode...$(NC)"
	@$(MAKE) stop
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/realtime_dashboard.py

url: ## Show dashboard URLs
	@echo "$(CYAN)🌐 Dashboard URLs$(NC)"
	@echo "$(CYAN)=================$(NC)"
	@echo "$(BLUE)Local:   http://localhost:$(DASHBOARD_PORT)$(NC)"
	@echo "$(BLUE)Network: http://`hostname -I | awk '{print $$1}'`:$(DASHBOARD_PORT)$(NC)"

#==============================================================================
# SMS SETUP & CONFIGURATION
#==============================================================================

sms-setup: ## Setup Twilio credentials
	@echo "$(CYAN)🔧 Setting up Twilio credentials...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/setup_twilio.py

sms-update: ## Update Twilio credentials
	@echo "$(CYAN)🔄 Updating Twilio credentials...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) update_twilio_credentials.py

sms-fix: ## Fix SMS setup issues
	@echo "$(CYAN)🔧 Fixing SMS setup...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/fix_sms_setup.py

#==============================================================================
# SMS TESTING & VALIDATION
#==============================================================================

sms-test: ## Test SMS notifications
	@echo "$(CYAN)📱 Testing SMS notifications...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/test_sms_simple.py

sms-validate: ## Validate Twilio credentials
	@echo "$(CYAN)✅ Validating Twilio credentials...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/validate_twilio_credentials.py

sms-direct: ## Direct SMS test (simple)
	@echo "$(CYAN)📲 Running direct SMS test...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/direct_sms_test.py

sms-final: ## Final SMS test (comprehensive)
	@echo "$(CYAN)🏁 Running final SMS test...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/final_sms_test.py

sms-advanced: ## Advanced Twilio test
	@echo "$(CYAN)🚀 Running advanced Twilio test...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/twilio_advanced_test.py

sms-notify: ## Send real auction notification SMS
	@echo "$(CYAN)📢 Sending real auction notification...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/sms_notification_test.py

#==============================================================================
# SMS STATUS & DIAGNOSTICS
#==============================================================================

sms-status: ## Check SMS/Twilio status
	@echo "$(CYAN)📋 Checking SMS/Twilio status...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/check_twilio_account.py

sms-diagnose: ## Diagnose SMS issues
	@echo "$(CYAN)🔍 Diagnosing SMS issues...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/diagnose_sms.py

sms-delivery: ## Check SMS delivery status
	@echo "$(CYAN)📦 Checking SMS delivery status...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/check_sms_delivery.py

sms-troubleshoot: ## Troubleshoot SMS delivery issues
	@echo "$(CYAN)🔧 Running SMS troubleshooting tests...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/sms_troubleshoot.py

#==============================================================================
# SMS DEMO & HELP
#==============================================================================

sms-demo: ## Demo SMS notifications
	@echo "$(CYAN)🎬 Running SMS demo...$(NC)"
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/demo_sms_notifications.py

sms-help: ## Show SMS help information
	@echo "$(CYAN)📱 SMS/Notification Commands$(NC)"
	@echo "$(CYAN)=============================$(NC)"
	@echo ""
	@echo "$(GREEN)🔧 Setup & Configuration:$(NC)"
	@echo "  $(YELLOW)sms-setup$(NC)       Setup Twilio credentials"
	@echo "  $(YELLOW)sms-update$(NC)      Update Twilio credentials"
	@echo "  $(YELLOW)sms-fix$(NC)         Fix SMS setup issues"
	@echo ""
	@echo "$(GREEN)✅ Testing & Validation:$(NC)"
	@echo "  $(YELLOW)sms-test$(NC)        Quick SMS test"
	@echo "  $(YELLOW)sms-validate$(NC)    Validate credentials"
	@echo "  $(YELLOW)sms-notify$(NC)      Send real auction notification"
	@echo "  $(YELLOW)sms-direct$(NC)      Direct SMS test"
	@echo "  $(YELLOW)sms-final$(NC)       Comprehensive test"
	@echo "  $(YELLOW)sms-advanced$(NC)    Advanced testing"
	@echo ""
	@echo "$(GREEN)📋 Status & Diagnostics:$(NC)"
	@echo "  $(YELLOW)sms-status$(NC)      Check account status"
	@echo "  $(YELLOW)sms-diagnose$(NC)    Diagnose problems"
	@echo "  $(YELLOW)sms-delivery$(NC)    Check delivery status"
	@echo "  $(YELLOW)sms-troubleshoot$(NC) Troubleshoot delivery issues"
	@echo ""
	@echo "$(GREEN)🎬 Demo & Help:$(NC)"
	@echo "  $(YELLOW)sms-demo$(NC)        Demo notifications"
	@echo "  $(YELLOW)sms-help$(NC)        Show this help"
