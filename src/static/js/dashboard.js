// John Pye Auctions Dashboard JavaScript
class Dashboard {
    constructor() {
        this.autoRefreshInterval = null;
        this.autoRefreshEnabled = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTabs();
        this.updateStatus();
        this.loadData();
    }

    setupEventListeners() {
        // Control buttons
        document.getElementById('startMonitoring').addEventListener('click', () => this.startMonitoring());
        document.getElementById('stopMonitoring').addEventListener('click', () => this.stopMonitoring());
        document.getElementById('refreshData').addEventListener('click', () => this.refreshData());
        document.getElementById('toggleAutoRefresh').addEventListener('click', () => this.toggleAutoRefresh());

        // Auto refresh status every 10 seconds
        setInterval(() => this.updateStatus(), 10000);
    }

    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked button and corresponding content
                button.classList.add('active');
                document.getElementById(targetTab).classList.add('active');
            });
        });
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('show');
    }

    showMessage(message, type = 'info') {
        const messagesContainer = document.getElementById('statusMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `status-message ${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 
                    type === 'error' ? 'fa-exclamation-circle' : 
                    'fa-info-circle';
        
        messageDiv.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        `;
        
        messagesContainer.appendChild(messageDiv);
        
        // Remove message after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    async startMonitoring() {
        try {
            this.showLoading();
            const response = await fetch('/api/start_monitoring', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showMessage(result.message, 'success');
                setTimeout(() => this.updateStatus(), 2000);
            } else {
                this.showMessage(result.message, 'error');
            }
        } catch (error) {
            this.showMessage('Failed to start monitoring: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async stopMonitoring() {
        try {
            this.showLoading();
            const response = await fetch('/api/stop_monitoring', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showMessage(result.message, 'success');
                setTimeout(() => this.updateStatus(), 2000);
            } else {
                this.showMessage(result.message, 'error');
            }
        } catch (error) {
            this.showMessage('Failed to stop monitoring: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async refreshData() {
        try {
            this.showLoading();
            const response = await fetch('/api/fetch_current_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showMessage(result.message, 'success');
                await this.loadData();
            } else {
                this.showMessage(result.message, 'error');
            }
        } catch (error) {
            this.showMessage('Failed to refresh data: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadData() {
        try {
            const response = await fetch('/api/data');
            const data = await response.json();
            
            this.updateUI(data);
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showMessage('Failed to load latest data', 'error');
        }
    }

    updateUI(data) {
        // Update statistics
        const stats = data.stats || {};
        document.getElementById('activeBidsCount').textContent = stats.total_active_bids || (data.active_bids ? data.active_bids.length : 0);
        document.getElementById('winningCount').textContent = stats.winning_bids || 0;
        document.getElementById('outbidCount').textContent = stats.outbid_count || 0;
        document.getElementById('watchlistCount').textContent = stats.watchlist_items || (data.watchlist ? data.watchlist.length : 0);
        document.getElementById('lastUpdated').textContent = data.last_updated || 'Never';

        // Update active bids
        this.updateActiveBids(data.active_bids || []);
        
        // Update watchlist
        this.updateWatchlist(data.watchlist || []);

        // Update monitoring status
        this.updateMonitoringStatus(data.is_monitoring);
    }

    updateActiveBids(bids) {
        const container = document.getElementById('activeBidsGrid');
        
        if (bids.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-hand-paper"></i>
                    <p>No active bids found</p>
                    <p class="text-muted">Click "Refresh Data" to check for new bids</p>
                </div>
            `;
            return;
        }

        container.innerHTML = bids.map(bid => {
            const statusClass = bid.status === 'WINNING' ? 'winning-bid' : bid.status === 'OUTBID' ? 'outbid-bid' : 'active-bid';
            const statusIcon = bid.status === 'WINNING' ? '🏆' : bid.status === 'OUTBID' ? '⚠️' : '📊';
            const statusText = bid.status || 'ACTIVE';
            
            return `
            <div class="item-card bid-card ${statusClass}" data-lot="${bid.lot || ''}">
                <div class="item-header">
                    <h3>${bid.title || 'Unknown Item'}</h3>
                    <div class="item-meta">
                        <span class="lot-number">Lot #${bid.lot || 'N/A'}</span>
                        <span class="bid-status ${statusClass}">${statusIcon} ${statusText}</span>
                    </div>
                </div>
                <div class="item-details">
                    <div class="bid-info">
                        <div class="current-bid">
                            <label>Current Bid:</label>
                            <span class="price">${bid.current_bid || 'N/A'}</span>
                        </div>
                        ${bid.my_max_bid ? `
                        <div class="my-bid">
                            <label>Your Max Bid:</label>
                            <span class="price">${bid.my_max_bid}</span>
                        </div>
                        ` : ''}
                        ${bid.end_time ? `
                        <div class="end-time">
                            <label>Ends:</label>
                            <span>${bid.end_time}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                <div class="item-actions">
                    ${bid.url ? `
                    <a href="${bid.url}" target="_blank" class="btn btn-primary btn-sm">
                        <i class="fas fa-external-link-alt"></i> View on Site
                    </a>
                    ` : ''}
                </div>
            </div>
            `;
        }).join('');
    }

    updateWatchlist(items) {
        const container = document.getElementById('watchlistGrid');
        
        if (items.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-eye"></i>
                    <p>No watchlist items found</p>
                    <p class="text-muted">Click "Refresh Data" to check for new items</p>
                </div>
            `;
            return;
        }

        container.innerHTML = items.map(item => `
            <div class="item-card watchlist-card" data-lot="${item.lot || ''}">
                <div class="item-header">
                    <h3>${item.title || 'Unknown Item'}</h3>
                    <span class="lot-number">Lot #${item.lot || 'N/A'}</span>
                </div>
                <div class="item-details">
                    <div class="bid-info">
                        ${item.current_bid ? `
                        <div class="current-bid">
                            <label>Current Bid:</label>
                            <span class="price">${item.current_bid}</span>
                        </div>
                        ` : ''}
                        ${item.end_time ? `
                        <div class="end-time">
                            <label>Ends:</label>
                            <span>${item.end_time}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                <div class="item-actions">
                    ${item.url ? `
                    <a href="${item.url}" target="_blank" class="btn btn-primary btn-sm">
                        <i class="fas fa-external-link-alt"></i> View on Site
                    </a>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    updateMonitoringStatus(isMonitoring) {
        const statusElement = document.getElementById('monitoringStatus');
        const startBtn = document.getElementById('startMonitoring');
        const stopBtn = document.getElementById('stopMonitoring');

        if (isMonitoring) {
            statusElement.className = 'status-indicator monitoring';
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Monitoring Active</span>';
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            statusElement.className = 'status-indicator stopped';
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Monitoring Stopped</span>';
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }

    async updateStatus() {
        try {
            const response = await fetch('/api/data');
            const data = await response.json();
            this.updateMonitoringStatus(data.is_monitoring);
            document.getElementById('lastUpdated').textContent = data.last_updated || 'Never';
        } catch (error) {
            console.error('Failed to update status:', error);
        }
    }

    toggleAutoRefresh() {
        const statusSpan = document.getElementById('autoRefreshStatus');
        const button = document.getElementById('toggleAutoRefresh');

        if (this.autoRefreshEnabled) {
            // Disable auto refresh
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
                this.autoRefreshInterval = null;
            }
            this.autoRefreshEnabled = false;
            statusSpan.textContent = 'OFF';
            button.classList.remove('btn-success');
            button.classList.add('btn-info');
            this.showMessage('Auto refresh disabled', 'info');
        } else {
            // Enable auto refresh (every 30 seconds)
            this.autoRefreshInterval = setInterval(() => {
                this.loadData();
            }, 30000);
            this.autoRefreshEnabled = true;
            statusSpan.textContent = 'ON';
            button.classList.remove('btn-info');
            button.classList.add('btn-success');
            this.showMessage('Auto refresh enabled (every 30 seconds)', 'success');
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});