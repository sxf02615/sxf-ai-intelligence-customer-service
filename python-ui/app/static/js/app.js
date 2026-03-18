/**
 * Smart Ticket System - Chat Application JavaScript
 * Handles message sending, display, and intent-specific formatting
 * 
 * Requirements: FR2.1, FR2.2, FR2.3, FR2.4
 */

// Chat Application Class
class ChatApplication {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatForm = document.getElementById('chatForm');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.errorMessage = document.getElementById('errorMessage');
        this.loading = document.getElementById('loading');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.logoutBtn = document.getElementById('logoutBtn');
        this.userInfo = document.getElementById('userInfo');
        
        this.sessionId = null;
        this.userId = null;
        this.isLoading = false;
        
        this.init();
    }

    /**
     * Initialize the chat application
     */
    async init() {
        this.setupEventListeners();
        await this.checkAuth();
        this.setupQuickActions();
    }

    /**
     * Set up all event listeners
     */
    setupEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Logout button
        this.logoutBtn.addEventListener('click', () => this.handleLogout());
        
        // Enter key to send
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    /**
     * Check authentication status
     */
    async checkAuth() {
        try {
            const response = await fetch('/api/auth/me');
            const data = await response.json();
            
            if (data.success) {
                this.userId = data.data.user_id;
                this.userInfo.textContent = `用户: ${this.userId}`;
            } else {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            window.location.href = '/login';
        }
    }

    /**
     * Set up quick action buttons
     */
    setupQuickActions() {
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.chatInput.value = btn.dataset.message;
                this.chatInput.focus();
            });
        });
    }

    /**
     * Handle form submission - send message
     */
    async handleSubmit(e) {
        e.preventDefault();
        
        const message = this.chatInput.value.trim();
        if (!message || this.isLoading) {
            return;
        }

        // Add user message to chat
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Show loading state
        this.setLoading(true);
        this.hideError();

        try {
            const response = await this.sendMessage(message);
            
            if (response.success) {
                this.sessionId = response.data.session_id;
                
                // Show typing indicator
                this.showTypingIndicator();
                
                // Simulate typing delay
                await this.delay(800);
                this.hideTypingIndicator();
                
                // Add assistant response with intent-specific formatting
                this.addAssistantMessage(response.data);
            } else {
                this.showError(response.message || '处理失败，请稍后重试');
            }
        } catch (error) {
            console.error('Message send error:', error);
            this.showError('网络错误，请稍后重试');
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Send message to the server
     * @param {string} message - User message
     * @returns {Promise<Object>} Response data
     */
    async sendMessage(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: this.sessionId,
                user_id: this.userId,
                message: message
            })
        });

        return await response.json();
    }

    /**
     * Set loading state
     * @param {boolean} loading - Loading state
     */
    setLoading(loading) {
        this.isLoading = loading;
        this.sendBtn.disabled = loading;
        this.chatInput.disabled = loading;
        
        if (loading) {
            this.loading.classList.add('show');
        } else {
            this.loading.classList.remove('show');
        }
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.typingIndicator.classList.add('show');
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.typingIndicator.classList.remove('show');
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.classList.add('show');
        this.scrollToBottom();
    }

    /**
     * Hide error message
     */
    hideError() {
        this.errorMessage.classList.remove('show');
    }

    /**
     * Add user message to chat
     * @param {string} content - Message content
     * @param {string} type - Message type ('user' or 'assistant')
     */
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const time = this.getCurrentTime();
        
        messageDiv.innerHTML = `
            <div class="message-content">${this.escapeHtml(content)}</div>
            <div class="message-time">${time}</div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * Add assistant message with intent-specific formatting
     * @param {Object} data - Response data from server
     */
    addAssistantMessage(data) {
        const { response, intent, data: structuredData } = data;
        
        // Create message container
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        
        const time = this.getCurrentTime();
        
        // Format response based on intent type
        const formattedContent = this.formatResponseByIntent(intent, response, structuredData);
        
        messageDiv.innerHTML = `
            <div class="message-content">${formattedContent}</div>
            <div class="message-time">${time}</div>
        `;

        this.chatMessages.appendChild(messageDiv);
        
        // Add intent tag if available
        if (intent) {
            this.addIntentTag(intent);
        }
        
        this.scrollToBottom();
    }

    /**
     * Format response based on intent type
     * @param {string} intent - Intent type (logistics, urgent, cancel)
     * @param {string} response - Text response
     * @param {Object} structuredData - Structured data from backend
     * @returns {string} Formatted HTML
     */
    formatResponseByIntent(intent, response, structuredData) {
        let formattedHtml = this.escapeHtml(response);
        
        // Add structured data based on intent type
        switch (intent) {
            case 'logistics':
                formattedHtml = this.formatLogisticsResponse(response, structuredData);
                break;
            case 'urgent':
                formattedHtml = this.formatUrgentResponse(response, structuredData);
                break;
            case 'cancel':
                formattedHtml = this.formatCancelResponse(response, structuredData);
                break;
        }
        
        return formattedHtml;
    }

    /**
     * Format logistics response with tracking information
     * @param {string} response - Base response text
     * @param {Object} data - Logistics data
     * @returns {string} Formatted HTML
     */
    formatLogisticsResponse(response, data) {
        if (!data || !data.order_info) {
            return this.escapeHtml(response);
        }

        const { order_info, tracking, estimated_delivery } = data;
        let html = `<p>${this.escapeHtml(response)}</p>`;
        
        // Order status card
        html += `
            <div style="margin-top: 12px; padding: 12px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                <strong style="color: #333;">📦 订单信息</strong>
                <div style="margin-top: 8px; font-size: 14px; color: #555;">
                    <div><strong>订单号：</strong>${this.escapeHtml(order_info.order_id || 'N/A')}</div>
                    <div><strong>状态：</strong>${this.formatOrderStatus(order_info.status)}</div>
                </div>
            </div>
        `;

        // Tracking history
        if (tracking && tracking.length > 0) {
            html += `
                <div style="margin-top: 12px;">
                    <strong style="color: #333;">📍 物流轨迹</strong>
                    <div style="margin-top: 8px; padding-left: 16px; border-left: 2px solid #e1e5e9;">
            `;
            
            tracking.slice(0, 3).forEach((event, index) => {
                const isLatest = index === 0;
                html += `
                    <div style="margin-bottom: 12px; position: relative; padding-left: 20px;">
                        <div style="position: absolute; left: -6px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: ${isLatest ? '#667eea' : '#ccc'};"></div>
                        <div style="font-size: 13px; color: ${isLatest ? '#333' : '#666'}; font-weight: ${isLatest ? '600' : '400'};">
                            ${this.escapeHtml(event.status || event.description || '')}
                        </div>
                        <div style="font-size: 12px; color: #999; margin-top: 2px;">
                            ${this.escapeHtml(event.time || event.timestamp || '')}
                        </div>
                    </div>
                `;
            });
            
            html += `</div></div>`;
        }

        // Estimated delivery
        if (estimated_delivery) {
            html += `
                <div style="margin-top: 12px; padding: 10px; background: #e8f4fd; border-radius: 8px; font-size: 14px;">
                    <strong style="color: #1976d2;">🚚 预计送达：</strong>
                    <span style="color: #1976d2;">${this.escapeHtml(estimated_delivery)}</span>
                </div>
            `;
        }

        return html;
    }

    /**
     * Format urgent ticket response
     * @param {string} response - Base response text
     * @param {Object} data - Ticket data
     * @returns {string} Formatted HTML
     */
    formatUrgentResponse(response, data) {
        let html = `<p>${this.escapeHtml(response)}</p>`;
        
        if (data && data.ticket_info) {
            const { ticket_id, estimated_time, contact } = data.ticket_info;
            
            html += `
                <div style="margin-top: 12px; padding: 12px; background: #fff3e0; border-radius: 8px; border-left: 4px solid #ff9800;">
                    <strong style="color: #e65100;">⚡ 催单工单已创建</strong>
                    <div style="margin-top: 8px; font-size: 14px; color: #555;">
                        <div><strong>工单号：</strong>${this.escapeHtml(ticket_id || 'N/A')}</div>
                        ${estimated_time ? `<div><strong>预计处理时间：</strong>${this.escapeHtml(estimated_time)}</div>` : ''}
                        ${contact ? `<div><strong>客服联系方式：</strong>${this.escapeHtml(contact)}</div>` : ''}
                    </div>
                </div>
            `;
        }
        
        return html;
    }

    /**
     * Format cancel order response
     * @param {string} response - Base response text
     * @param {Object} data - Cancel result data
     * @returns {string} Formatted HTML
     */
    formatCancelResponse(response, data) {
        let html = `<p>${this.escapeHtml(response)}</p>`;
        
        if (data && data.cancel_result) {
            const { success, refund_amount, refund_time, order_id } = data.cancel_result;
            
            if (success) {
                html += `
                    <div style="margin-top: 12px; padding: 12px; background: #e8f5e9; border-radius: 8px; border-left: 4px solid #4caf50;">
                        <strong style="color: #2e7d32;">✅ 取消成功</strong>
                        <div style="margin-top: 8px; font-size: 14px; color: #555;">
                            <div><strong>订单号：</strong>${this.escapeHtml(order_id || 'N/A')}</div>
                            <div><strong>退款金额：</strong>¥${refund_amount ? parseFloat(refund_amount).toFixed(2) : '0.00'}</div>
                            ${refund_time ? `<div><strong>退款到账时间：</strong>${this.escapeHtml(refund_time)}</div>` : ''}
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div style="margin-top: 12px; padding: 12px; background: #ffebee; border-radius: 8px; border-left: 4px solid #f44336;">
                        <strong style="color: #c62828;">❌ 取消失败</strong>
                        <div style="margin-top: 8px; font-size: 14px; color: #555;">
                            <div>${this.escapeHtml(data.cancel_result.message || '无法取消该订单')}</div>
                        </div>
                    </div>
                `;
            }
        }
        
        return html;
    }

    /**
     * Format order status for display
     * @param {string} status - Order status
     * @returns {string} Formatted status HTML
     */
    formatOrderStatus(status) {
        const statusMap = {
            'pending': { text: '待处理', color: '#ff9800' },
            'processing': { text: '处理中', color: '#2196f3' },
            'shipped': { text: '已发货', color: '#4caf50' },
            'delivered': { text: '已签收', color: '#4caf50' },
            'cancelled': { text: '已取消', color: '#9e9e9e' }
        };
        
        const statusInfo = statusMap[status?.toLowerCase()] || { text: status || '未知', color: '#666' };
        
        return `<span style="color: ${statusInfo.color}; font-weight: 600;">${statusInfo.text}</span>`;
    }

    /**
     * Add intent tag to message
     * @param {string} intent - Intent type
     */
    addIntentTag(intent) {
        const intentLabels = {
            'logistics': '📦 物流查询',
            'urgent': '⚡ 催单处理',
            'cancel': '❌ 取消订单'
        };
        
        const tagDiv = document.createElement('div');
        tagDiv.className = 'message assistant';
        tagDiv.style.marginTop = '4px';
        
        tagDiv.innerHTML = `
            <div class="message-content" style="font-size: 12px; background: #f0f2f5; color: #666; padding: 6px 12px;">
                识别意图: ${intentLabels[intent] || intent}
            </div>
        `;

        this.chatMessages.appendChild(tagDiv);
        this.scrollToBottom();
    }

    /**
     * Handle logout
     */
    async handleLogout() {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/login';
        }
    }

    /**
     * Get current time formatted
     * @returns {string} Formatted time string
     */
    getCurrentTime() {
        return new Date().toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Delay utility
     * @param {number} ms - Milliseconds to delay
     * @returns {Promise} Promise that resolves after delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize chat application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApplication();
});