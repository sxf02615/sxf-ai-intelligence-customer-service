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
import org.springframework.stereotype.Service;

/**
 * Chat service for communicating with Python Core Service.
 * NFR7, NFR8 - HTTP communication with Python core service
 */
@Service
public class ChatService {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatService.class);
    
    private final TicketServiceClient ticketServiceClient;
    
    public ChatService(TicketServiceClient ticketServiceClient) {
        this.ticketServiceClient = ticketServiceClient;
    }
    
    /**
     * Process chat message and route to appropriate service.
     * FR1.3 - Chat interaction
     * 
     * @param request the chat request containing user message
     * @return ApiResponse containing chat response
     */
    public ApiResponse<ChatResponse> processChat(ChatRequest request) {
        try {
            logger.info("Processing chat request for session: {}", request.getSessionId());
            
            ChatResponse response = ticketServiceClient.chat(request);
            
            logger.debug("Chat response received, intent: {}", response.getIntent());
            
            return ApiResponse.success(response);
            
        } catch (Exception e) {
            logger.error("Error processing chat request: {}", e.getMessage(), e);
            return ApiResponse.error("Failed to process chat: " + e.getMessage(), "CHAT_ERROR");
        }
    }
    
    /**
     * Get logistics information for an order.
     * FR3.1, FR3.2, FR3.3, FR3.4 - Logistics query
     * 
     * @param orderId the order ID to query
     * @return ApiResponse containing logistics information
     */
    public ApiResponse<LogisticsResponse> getLogistics(String orderId) {
        try {
            logger.info("Fetching logistics for order: {}", orderId);
            
            LogisticsResponse response = ticketServiceClient.getLogistics(orderId);
            
            logger.debug("Logistics response received for order: {}", orderId);
            
            return ApiResponse.success(response);
            
        } catch (Exception e) {
            logger.error("Error fetching logistics for order {}: {}", orderId, e.getMessage(), e);
            return ApiResponse.error("Failed to fetch logistics: " + e.getMessage(), "LOGISTICS_ERROR");
        }
    }
    
    /**
     * Create an urgent ticket for an order.
     * FR4.1, FR4.2, FR4.3, FR4.4 - Urgent ticket creation
     * 
     * @param request the urgent ticket request
     * @return ApiResponse containing created ticket information
     */
    public ApiResponse<UrgentTicketResponse> createUrgentTicket(UrgentTicketRequest request) {
        try {
            logger.info("Creating urgent ticket for order: {}", request.getOrderId());
            
            UrgentTicketResponse response = ticketServiceClient.createUrgentTicket(request);
            
            logger.debug("Urgent ticket created: {}", response.getTicketId());
            
            return ApiResponse.success(response, "Urgent ticket created successfully");
            
        } catch (Exception e) {
            logger.error("Error creating urgent ticket for order {}: {}", request.getOrderId(), e.getMessage(), e);
            return ApiResponse.error("Failed to create urgent ticket: " + e.getMessage(), "URGENT_TICKET_ERROR");
        }
    }
    
    /**
     * Cancel an order.
     * FR5.1, FR5.2, FR5.3, FR5.4, FR5.5 - Order cancellation
     * 
     * @param request the cancel order request
     * @return ApiResponse containing cancellation result
     */
    public ApiResponse<CancelOrderResponse> cancelOrder(CancelOrderRequest request) {
        try {
            logger.info("Cancelling order: {}", request.getOrderId());
            
            CancelOrderResponse response = ticketServiceClient.cancelOrder(request);
            
            logger.debug("Order cancelled: {}, refund amount: {}", 
                    response.getOrderId(), response.getRefundAmount());
            
            return ApiResponse.success(response, "Order cancelled successfully");
            
        } catch (Exception e) {
            logger.error("Error cancelling order {}: {}", request.getOrderId(), e.getMessage(), e);
            return ApiResponse.error("Failed to cancel order: " + e.getMessage(), "CANCEL_ORDER_ERROR");
        }
    }
}