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
        this.context = null;  // 保存上下文
        
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
            
            console.log('==> 处理响应:');
            console.log('    response.success:', response.success);
            console.log('    response:', response);
            
            if (response.success) {
                this.sessionId = response.session_id;
                this.context = response.context;  // 保存上下文
                console.log('    保存context:', this.context);
                
                // Show typing indicator
                this.showTypingIndicator();
                
                // Simulate typing delay
                await this.delay(800);
                this.hideTypingIndicator();
                
                // Add assistant response with intent-specific formatting
                this.addAssistantMessage(response);
            } else {
                console.log('    显示错误:', response.message);
                this.showError(response.message || '处理失败，请稍后重试');
            }
        } catch (error) {
            console.error('Message send error:', error);
            if (error.name === 'AbortError') {
                this.showError('请求超时，请稍后重试');
            } else {
                this.showError('网络错误，请稍后重试');
            }
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
        const payload = {
            session_id: this.sessionId,
            user_id: this.userId,
            message: message,
            context: this.context
        };
        
        console.log('==> 发送请求到 Python UI 服务: /api/chat');
        console.log('    请求地址: http://127.0.0.1:8001/api/chat');
        console.log('    请求内容:', payload);
        console.log('    发送的context:', this.context);
        
        // 设置30秒超时
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);

        const result = await response.json();
        
        console.log('<== 收到 Python UI 服务响应:');
        console.log('    状态码:', response.status);
        console.log('    响应内容:', result);
        
        return result;
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
        console.log('==> addAssistantMessage 收到数据:');
        console.log('    data:', data);
        
        const response = data.response || '';
        const intent = data.intent || null;
        const structuredData = data.data || null;
        
        console.log('    解析后 - response:', response);
        console.log('    解析后 - intent:', intent);
        console.log('    解析后 - structuredData:', structuredData);
        
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
        console.log('==> formatResponseByIntent:');
        console.log('    intent:', intent);
        console.log('    response:', response);
        console.log('    structuredData:', structuredData);
        
        let formattedHtml = this.escapeHtml(response);
        
        // If there's no structured data, just return the plain response
        if (!structuredData) {
            console.log('    无 structuredData，直接返回纯文本');
            return formattedHtml;
        }
        
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
            default:
                console.log('    未知的 intent，不格式化');
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
        console.log('==> formatLogisticsResponse:');
        console.log('    data:', data);
        
        // Handle flat data structure
        const orderId = data?.order_id || data?.order_info?.order_id;
        const status = data?.status || data?.order_info?.status;
        const tracking = data?.tracking_history || data?.tracking || data?.order_info?.tracking;
        const estimatedDelivery = data?.estimated_delivery;
        
        console.log('    解析后 - orderId:', orderId, 'status:', status);
        
        if (!orderId) {
            console.log('    无 orderId，返回纯文本');
            return this.escapeHtml(response);
        }

        let html = `<p>${this.escapeHtml(response)}</p>`;
        
        // Order status card
        html += `
            <div style="margin-top: 12px; padding: 12px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                <strong style="color: #333;">📦 订单信息</strong>
                <div style="margin-top: 8px; font-size: 14px; color: #555;">
                    <div><strong>订单号：</strong>${this.escapeHtml(orderId || 'N/A')}</div>
                    <div><strong>状态：</strong>${this.formatOrderStatus(status)}</div>
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
        if (estimatedDelivery) {
            html += `
                <div style="margin-top: 12px; padding: 10px; background: #e8f4fd; border-radius: 8px; font-size: 14px;">
                    <strong style="color: #1976d2;">🚚 预计送达：</strong>
                    <span style="color: #1976d2;">${this.escapeHtml(estimatedDelivery)}</span>
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
        console.log('==> formatUrgentResponse:');
        console.log('    data:', data);
        
        // Handle flat data structure
        const ticketId = data?.ticket_id || data?.ticket_info?.ticket_id;
        const estimatedTime = data?.estimated_processing_time || data?.ticket_info?.estimated_time;
        const contact = data?.contact || data?.ticket_info?.contact;
        
        console.log('    解析后 - ticketId:', ticketId);
        
        let html = `<p>${this.escapeHtml(response)}</p>`;
        
        if (ticketId) {
            html += `
                <div style="margin-top: 12px; padding: 12px; background: #fff3e0; border-radius: 8px; border-left: 4px solid #ff9800;">
                    <strong style="color: #e65100;">⚡ 催单工单已创建</strong>
                    <div style="margin-top: 8px; font-size: 14px; color: #555;">
                        <div><strong>工单号：</strong>${this.escapeHtml(ticketId || 'N/A')}</div>
                        ${estimatedTime ? `<div><strong>预计处理时间：</strong>${this.escapeHtml(estimatedTime)}</div>` : ''}
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
        console.log('==> formatCancelResponse:');
        console.log('    data:', data);
        
        // Handle flat data structure
        const success = data?.success;
        const refundAmount = data?.refund_amount;
        const refundTime = data?.refund_arrival_time || data?.refund_time;
        const orderId = data?.order_id;
        const message = data?.message;
        
        console.log('    解析后 - orderId:', orderId, 'success:', success);
        
        let html = `<p>${this.escapeHtml(response)}</p>`;
        
        if (orderId) {
            if (success) {
                html += `
                    <div style="margin-top: 12px; padding: 12px; background: #e8f5e9; border-radius: 8px; border-left: 4px solid #4caf50;">
                        <strong style="color: #2e7d32;">✅ 取消成功</strong>
                        <div style="margin-top: 8px; font-size: 14px; color: #555;">
                            <div><strong>订单号：</strong>${this.escapeHtml(orderId || 'N/A')}</div>
                            <div><strong>退款金额：</strong>¥${refundAmount ? parseFloat(refundAmount).toFixed(2) : '0.00'}</div>
                            ${refundTime ? `<div><strong>退款到账时间：</strong>${this.escapeHtml(refundTime)}</div>` : ''}
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div style="margin-top: 12px; padding: 12px; background: #ffebee; border-radius: 8px; border-left: 4px solid #f44336;">
                        <strong style="color: #c62828;">❌ 取消失败</strong>
                        <div style="margin-top: 8px; font-size: 14px; color: #555;">
                            <div>${this.escapeHtml(message || '无法取消该订单')}</div>
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
    console.log('==> app.js 已加载');
    console.log('    ChatApplication:', typeof ChatApplication);
    window.chatApp = new ChatApplication();
    console.log('    chatApp 初始化完成:', window.chatApp);
});