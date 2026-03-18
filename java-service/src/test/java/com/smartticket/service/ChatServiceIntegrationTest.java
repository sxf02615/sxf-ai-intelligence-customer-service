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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * Integration tests for ChatService.
 * Tests: FR1.3, FR3.1, FR3.2, FR3.3, FR3.4, FR4.1, FR4.2, FR4.3, FR4.4, FR5.1, FR5.2, FR5.3, FR5.4, FR5.5
 * Validates: NFR7, NFR8 - HTTP communication with Python core service
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("ChatService Integration Tests")
class ChatServiceIntegrationTest {

    @Mock
    private TicketServiceClient ticketServiceClient;

    private ChatService chatService;

    @BeforeEach
    void setUp() {
        chatService = new ChatService(ticketServiceClient);
    }

    private ChatRequest createChatRequest(String sessionId, String userId, String message) {
        ChatRequest request = new ChatRequest();
        request.setSessionId(sessionId);
        request.setUserId(userId);
        request.setMessage(message);
        request.setContext(new HashMap<>());
        return request;
    }

    @Nested
    @DisplayName("Chat Processing Tests - FR1.3")
    class ChatProcessingTests {

        @Test
        @DisplayName("Test successful chat processing - FR1.3")
        void testSuccessfulChatProcessing() {
            ChatRequest request = createChatRequest("session-123", "user-1", "Track my order");
            ChatResponse expectedResponse = new ChatResponse(true, "Your order is on the way", 
                    "logistics_query", "session-123", false);

            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(expectedResponse);

            ApiResponse<ChatResponse> response = chatService.processChat(request);

            assertTrue(response.isSuccess());
            assertNotNull(response.getData());
            assertEquals("Your order is on the way", response.getData().getResponse());
            assertEquals("logistics_query", response.getData().getIntent());
            verify(ticketServiceClient, times(1)).chat(request);
        }

        @Test
        @DisplayName("Test chat processing with different intents - FR1.3")
        void testChatProcessingWithDifferentIntents() {
            // Test urgent ticket intent
            ChatRequest urgentRequest = createChatRequest("session-1", "user-1", "I need urgent help");
            ChatResponse urgentResponse = new ChatResponse(true, "Creating urgent ticket", 
                    "urgent_ticket", "session-1", false);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(urgentResponse);

            ApiResponse<ChatResponse> urgentApiResponse = chatService.processChat(urgentRequest);

            assertTrue(urgentApiResponse.isSuccess());
            assertEquals("urgent_ticket", urgentApiResponse.getData().getIntent());

            // Test cancel order intent
            ChatRequest cancelRequest = createChatRequest("session-2", "user-2", "Cancel my order");
            ChatResponse cancelResponse = new ChatResponse(true, "Order cancelled", 
                    "cancel_order", "session-2", false);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(cancelResponse);

            ApiResponse<ChatResponse> cancelApiResponse = chatService.processChat(cancelRequest);

            assertTrue(cancelApiResponse.isSuccess());
            assertEquals("cancel_order", cancelApiResponse.getData().getIntent());
        }

        @Test
        @DisplayName("Test chat processing error handling - NFR8")
        void testChatProcessingErrorHandling() {
            ChatRequest request = createChatRequest("session-123", "user-1", "Track my order");

            when(ticketServiceClient.chat(any(ChatRequest.class)))
                    .thenThrow(new RuntimeException("Python service unavailable"));

            ApiResponse<ChatResponse> response = chatService.processChat(request);

            assertFalse(response.isSuccess());
            assertNull(response.getData());
            assertNotNull(response.getMessage());
            assertEquals("CHAT_ERROR", response.getErrorCode());
        }
    }

    @Nested
    @DisplayName("Logistics Query Tests - FR3.1, FR3.2, FR3.3, FR3.4")
    class LogisticsQueryTests {

        @Test
        @DisplayName("Test successful logistics query - FR3.1, FR3.2")
        void testSuccessfulLogisticsQuery() {
            String orderId = "ORD-12345";
            LogisticsResponse.TrackingEvent event1 = new LogisticsResponse.TrackingEvent(
                    "Order placed", "Warehouse A", Instant.now());
            LogisticsResponse.TrackingEvent event2 = new LogisticsResponse.TrackingEvent(
                    "Shipped", "Warehouse A", Instant.now());
            LogisticsResponse expectedResponse = new LogisticsResponse(
                    orderId, "In Transit", "In Transit", Instant.now().plusSeconds(86400),
                    Arrays.asList(event1, event2)
            );

            when(ticketServiceClient.getLogistics(orderId)).thenReturn(expectedResponse);

            ApiResponse<LogisticsResponse> response = chatService.getLogistics(orderId);

            assertTrue(response.isSuccess());
            assertNotNull(response.getData());
            assertEquals(orderId, response.getData().getOrderId());
            assertEquals("In Transit", response.getData().getStatus());
            assertEquals(2, response.getData().getTrackingHistory().size());
            verify(ticketServiceClient, times(1)).getLogistics(orderId);
        }

        @Test
        @DisplayName("Test logistics query error handling - NFR8")
        void testLogisticsQueryErrorHandling() {
            String orderId = "ORD-12345";

            when(ticketServiceClient.getLogistics(orderId))
                    .thenThrow(new RuntimeException("Service unavailable"));

            ApiResponse<LogisticsResponse> response = chatService.getLogistics(orderId);

            assertFalse(response.isSuccess());
            assertNull(response.getData());
            assertNotNull(response.getMessage());
            assertEquals("LOGISTICS_ERROR", response.getErrorCode());
        }
    }

    @Nested
    @DisplayName("Urgent Ticket Tests - FR4.1, FR4.2, FR4.3, FR4.4")
    class UrgentTicketTests {

        @Test
        @DisplayName("Test successful urgent ticket creation - FR4.1, FR4.2")
        void testSuccessfulUrgentTicketCreation() {
            UrgentTicketRequest request = new UrgentTicketRequest("ORD-12345", "Urgent delivery needed");
            UrgentTicketResponse expectedResponse = new UrgentTicketResponse(
                    "TKT-001", Instant.now().plusSeconds(3600), "Support Team A"
            );

            when(ticketServiceClient.createUrgentTicket(any(UrgentTicketRequest.class)))
                    .thenReturn(expectedResponse);

            ApiResponse<UrgentTicketResponse> response = chatService.createUrgentTicket(request);

            assertTrue(response.isSuccess());
            assertNotNull(response.getData());
            assertEquals("TKT-001", response.getData().getTicketId());
            assertNotNull(response.getData().getEstimatedProcessingTime());
            assertEquals("Support Team A", response.getData().getContact());
            verify(ticketServiceClient, times(1)).createUrgentTicket(request);
        }

        @Test
        @DisplayName("Test urgent ticket error handling - NFR8")
        void testUrgentTicketErrorHandling() {
            UrgentTicketRequest request = new UrgentTicketRequest("ORD-12345", "Urgent delivery needed");

            when(ticketServiceClient.createUrgentTicket(any(UrgentTicketRequest.class)))
                    .thenThrow(new RuntimeException("Ticket service error"));

            ApiResponse<UrgentTicketResponse> response = chatService.createUrgentTicket(request);

            assertFalse(response.isSuccess());
            assertNull(response.getData());
            assertNotNull(response.getMessage());
            assertEquals("URGENT_TICKET_ERROR", response.getErrorCode());
        }
    }

    @Nested
    @DisplayName("Order Cancellation Tests - FR5.1, FR5.2, FR5.3, FR5.4, FR5.5")
    class OrderCancellationTests {

        @Test
        @DisplayName("Test successful order cancellation - FR5.1, FR5.2")
        void testSuccessfulOrderCancellation() {
            CancelOrderRequest request = new CancelOrderRequest("ORD-12345", "Customer changed mind");
            CancelOrderResponse expectedResponse = new CancelOrderResponse(
                    "ORD-12345", 99.99, Instant.now().plusSeconds(86400), "Your order has been cancelled"
            );

            when(ticketServiceClient.cancelOrder(any(CancelOrderRequest.class)))
                    .thenReturn(expectedResponse);

            ApiResponse<CancelOrderResponse> response = chatService.cancelOrder(request);

            assertTrue(response.isSuccess());
            assertNotNull(response.getData());
            assertEquals("ORD-12345", response.getData().getOrderId());
            assertEquals(99.99, response.getData().getRefundAmount());
            assertNotNull(response.getData().getRefundArrivalTime());
            verify(ticketServiceClient, times(1)).cancelOrder(request);
        }

        @Test
        @DisplayName("Test order cancellation error handling - NFR8")
        void testOrderCancellationErrorHandling() {
            CancelOrderRequest request = new CancelOrderRequest("ORD-12345", "Customer changed mind");

            when(ticketServiceClient.cancelOrder(any(CancelOrderRequest.class)))
                    .thenThrow(new RuntimeException("Cancellation service error"));

            ApiResponse<CancelOrderResponse> response = chatService.cancelOrder(request);

            assertFalse(response.isSuccess());
            assertNull(response.getData());
            assertNotNull(response.getMessage());
            assertEquals("CANCEL_ORDER_ERROR", response.getErrorCode());
        }
    }

    @Nested
    @DisplayName("Response Mapping Tests - NFR8")
    class ResponseMappingTests {

        @Test
        @DisplayName("Test chat response mapping preserves all fields - NFR8")
        void testChatResponseMappingPreservesAllFields() {
            ChatRequest request = createChatRequest("session-123", "user-1", "Test message");
            ChatResponse expectedResponse = new ChatResponse(true, "Response text", 
                    "test_intent", "session-123", true);

            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(expectedResponse);

            ApiResponse<ChatResponse> response = chatService.processChat(request);

            assertNotNull(response.getData());
            assertEquals(expectedResponse.isSuccess(), response.getData().isSuccess());
            assertEquals(expectedResponse.getResponse(), response.getData().getResponse());
            assertEquals(expectedResponse.getIntent(), response.getData().getIntent());
            assertEquals(expectedResponse.getSessionId(), response.getData().getSessionId());
            assertEquals(expectedResponse.isNeedsClarification(), response.getData().isNeedsClarification());
        }

        @Test
        @DisplayName("Test logistics response mapping preserves all fields - NFR8")
        void testLogisticsResponseMappingPreservesAllFields() {
            String orderId = "ORD-12345";
            LogisticsResponse.TrackingEvent event1 = new LogisticsResponse.TrackingEvent(
                    "Order placed", "Warehouse A", Instant.now());
            LogisticsResponse.TrackingEvent event2 = new LogisticsResponse.TrackingEvent(
                    "Shipped", "Warehouse A", Instant.now());
            LogisticsResponse expectedResponse = new LogisticsResponse(
                    orderId, "Delivered", "Delivered", Instant.now().plusSeconds(86400),
                    Arrays.asList(event1, event2)
            );

            when(ticketServiceClient.getLogistics(orderId)).thenReturn(expectedResponse);

            ApiResponse<LogisticsResponse> response = chatService.getLogistics(orderId);

            assertNotNull(response.getData());
            assertEquals(expectedResponse.getOrderId(), response.getData().getOrderId());
            assertEquals(expectedResponse.getStatus(), response.getData().getStatus());
            assertEquals(expectedResponse.getLatestStatus(), response.getData().getLatestStatus());
            assertEquals(expectedResponse.getTrackingHistory().size(), response.getData().getTrackingHistory().size());
            assertEquals(expectedResponse.getEstimatedDelivery(), response.getData().getEstimatedDelivery());
        }
    }
}