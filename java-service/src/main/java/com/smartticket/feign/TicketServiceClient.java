package com.smartticket.feign;

import com.smartticket.dto.ChatRequest;
import com.smartticket.dto.ChatResponse;
import com.smartticket.dto.request.CancelOrderRequest;
import com.smartticket.dto.request.UrgentTicketRequest;
import com.smartticket.dto.response.CancelOrderResponse;
import com.smartticket.dto.response.LogisticsResponse;
import com.smartticket.dto.response.UrgentTicketResponse;
import com.smartticket.feign.TicketServiceClientConfig;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * Feign client for communicating with Python Core Service.
 * NFR7, NFR8 - HTTP communication with Python core service
 */
@FeignClient(name = "ticketServiceClient", url = "${python-core.url}", configuration = TicketServiceClientConfig.class)
@RequestMapping("/api/v1")
public interface TicketServiceClient {
    
    /**
     * Process chat message and route to appropriate service.
     * POST /api/v1/chat
     * 
     * @param request the chat request containing user message
     * @return chat response with intent and response text
     */
    @PostMapping(value = "/chat", consumes = MediaType.APPLICATION_JSON_VALUE)
    ChatResponse chat(@RequestBody ChatRequest request);
    
    /**
     * Get logistics information for an order.
     * GET /api/v1/logistics/{orderId}
     * 
     * @param orderId the order ID to query
     * @return logistics information including tracking history
     */
    @GetMapping("/logistics/{orderId}")
    LogisticsResponse getLogistics(@PathVariable("orderId") String orderId);
    
    /**
     * Create an urgent ticket for an order.
     * POST /api/v1/tickets/urgent
     * 
     * @param request the urgent ticket request
     * @return created ticket information
     */
    @PostMapping(value = "/tickets/urgent", consumes = MediaType.APPLICATION_JSON_VALUE)
    UrgentTicketResponse createUrgentTicket(@RequestBody UrgentTicketRequest request);
    
    /**
     * Cancel an order.
     * POST /api/v1/orders/cancel
     * 
     * @param request the cancel order request
     * @return cancellation result with refund information
     */
    @PostMapping(value = "/orders/cancel", consumes = MediaType.APPLICATION_JSON_VALUE)
    CancelOrderResponse cancelOrder(@RequestBody CancelOrderRequest request);
}