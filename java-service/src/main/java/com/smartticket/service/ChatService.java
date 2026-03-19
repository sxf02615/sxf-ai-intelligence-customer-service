package com.smartticket.service;

import com.smartticket.dto.ApiResponse;
import com.smartticket.dto.ChatRequest;
import com.smartticket.dto.ChatResponse;
import com.smartticket.dto.request.CancelOrderRequest;
import com.smartticket.dto.request.UrgentTicketRequest;
import com.smartticket.dto.response.CancelOrderResponse;
import com.smartticket.dto.response.LogisticsResponse;
import com.smartticket.dto.response.UrgentTicketResponse;
import com.smartticket.feign.TicketServiceClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Service;

/**
 * 与Python核心服务通信的聊天服务。
 * NFR7, NFR8 - 与Python核心服务的HTTP通信
 */
@Service
public class ChatService {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatService.class);
    
    private final TicketServiceClient ticketServiceClient;
    
    public ChatService(@Lazy TicketServiceClient ticketServiceClient) {
        this.ticketServiceClient = ticketServiceClient;
    }
    
    /**
     * 处理聊天消息并路由到相应的服务。
     * FR1.3 - 聊天交互
     * 
     * @param request 包含用户消息的聊天请求
     * @return 包含聊天响应的ApiResponse
     */
    public ApiResponse<ChatResponse> processChat(ChatRequest request) {
        try {
            logger.info("正在处理会话 {} 的聊天请求", request.getSessionId());
            
            ChatResponse response = ticketServiceClient.chat(request);
            
            logger.debug("收到聊天响应，意图: {}", response.getIntent());
            
            return ApiResponse.success(response);
            
        } catch (Exception e) {
            logger.error("处理聊天请求时出错: {}", e.getMessage(), e);
            return ApiResponse.error("处理聊天失败: " + e.getMessage(), "CHAT_ERROR");
        }
    }
    
    /**
     * 获取订单的物流信息。
     * FR3.1, FR3.2, FR3.3, FR3.4 - 物流查询
     * 
     * @param orderId 要查询的订单ID
     * @return 包含物流信息的ApiResponse
     */
    public ApiResponse<LogisticsResponse> getLogistics(String orderId) {
        try {
            logger.info("正在获取订单 {} 的物流信息", orderId);
            
            LogisticsResponse response = ticketServiceClient.getLogistics(orderId);
            
            logger.debug("收到订单 {} 的物流响应", orderId);
            
            return ApiResponse.success(response);
            
        } catch (Exception e) {
            logger.error("获取订单 {} 的物流信息时出错: {}", orderId, e.getMessage(), e);
            return ApiResponse.error("获取物流信息失败: " + e.getMessage(), "LOGISTICS_ERROR");
        }
    }
    
    /**
     * 为订单创建催单工单。
     * FR4.1, FR4.2, FR4.3, FR4.4 - 催单工单创建
     * 
     * @param request 催单工单请求
     * @return 包含已创建工单信息的ApiResponse
     */
    public ApiResponse<UrgentTicketResponse> createUrgentTicket(UrgentTicketRequest request) {
        try {
            logger.info("正在为订单 {} 创建催单工单", request.getOrderId());
            
            UrgentTicketResponse response = ticketServiceClient.createUrgentTicket(request);
            
            logger.debug("催单工单已创建: {}", response.getTicketId());
            
            return ApiResponse.success(response, "催单工单创建成功");
            
        } catch (Exception e) {
            logger.error("为订单 {} 创建催单工单时出错: {}", request.getOrderId(), e.getMessage(), e);
            return ApiResponse.error("创建催单工单失败: " + e.getMessage(), "URGENT_TICKET_ERROR");
        }
    }
    
    /**
     * 取消订单。
     * FR5.1, FR5.2, FR5.3, FR5.4, FR5.5 - 订单取消
     * 
     * @param request 取消订单请求
     * @return 包含取消结果的ApiResponse
     */
    public ApiResponse<CancelOrderResponse> cancelOrder(CancelOrderRequest request) {
        try {
            logger.info("正在取消订单: {}", request.getOrderId());
            
            CancelOrderResponse response = ticketServiceClient.cancelOrder(request);
            
            logger.debug("订单已取消: {}, 退款金额: {}", 
                    response.getOrderId(), response.getRefundAmount());
            
            return ApiResponse.success(response, "订单取消成功");
            
        } catch (Exception e) {
            logger.error("取消订单 {} 时出错: {}", request.getOrderId(), e.getMessage(), e);
            return ApiResponse.error("取消订单失败: " + e.getMessage(), "CANCEL_ORDER_ERROR");
        }
    }
}