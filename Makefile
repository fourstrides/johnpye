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

.PHONY: help start stop restart status clean logs setup info url

all: help

help: ## Show this help message
	@echo "$(CYAN)John Pye Auction Tracker Management$(NC)"
	@echo "$(CYAN)====================================$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Create necessary directories and files
	@echo "$(CYAN)🔧 Setting up project structure...$(NC)"
	@mkdir -p $(DATA_DIR) $(LOGS_DIR) $(PID_DIR)
	@touch $(DASHBOARD_LOG)
	@echo "$(GREEN)✅ Project setup complete$(NC)"

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

clean: ## Clean up logs and temporary files
	@echo "$(CYAN)🧹 Cleaning up...$(NC)"
	@rm -f $(LOGS_DIR)/*.log $(PID_DIR)/*.pid
	@rm -f $(DATA_DIR)/*.json $(DATA_DIR)/*.csv
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

dev: ## Start in development mode with live logs
	@echo "$(CYAN)🔧 Starting in development mode...$(NC)"
	@$(MAKE) stop
	@cd $(PROJECT_DIR) && $(PYTHON) $(SRC_DIR)/realtime_dashboard.py

url: ## Show dashboard URLs
	@echo "$(CYAN)🌐 Dashboard URLs$(NC)"
	@echo "$(CYAN)=================$(NC)"
	@echo "$(BLUE)Local:   http://localhost:$(DASHBOARD_PORT)$(NC)"
	@echo "$(BLUE)Network: http://`hostname -I | awk '{print $$1}'`:$(DASHBOARD_PORT)$(NC)"

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