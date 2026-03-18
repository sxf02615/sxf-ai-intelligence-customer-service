package com.smartticket;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartticket.dto.*;
import com.smartticket.dto.request.CancelOrderRequest;
import com.smartticket.dto.request.UrgentTicketRequest;
import com.smartticket.dto.response.CancelOrderResponse;
import com.smartticket.dto.response.LogisticsResponse;
import com.smartticket.dto.response.UrgentTicketResponse;
import com.smartticket.feign.TicketServiceClient;
import com.smartticket.service.ChatService;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.time.Instant;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Comprehensive integration tests for Smart Ticket Java Service.
 * Tests: FR1.1, FR1.2, FR1.3, FR1.5, FR3.1, FR3.2, FR3.3, FR3.4, FR4.1, FR4.2, FR4.3, FR4.4, FR5.1, FR5.2, FR5.3, FR5.4, FR5.5
 * Validates: NFR7, NFR8 - HTTP communication and response handling
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@DisplayName("Smart Ticket Service Integration Tests")
class SmartTicketIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private TicketServiceClient ticketServiceClient;

    private static final String VALID_ADMIN_USERNAME = "admin";
    private static final String VALID_ADMIN_PASSWORD = "admin123";
    private static final String VALID_USER_USERNAME = "user";
    private static final String VALID_USER_PASSWORD = "user123";

    // ==================== Authentication Flow Tests ====================

    @Nested
    @DisplayName("Authentication Flow Tests - FR1.1, FR1.2, FR1.3")
    class AuthenticationFlowTests {

        @Test
        @DisplayName("Test complete authentication flow: login and token validation - FR1.1, FR1.2, FR1.3")
        void testCompleteAuthenticationFlow() throws Exception {
            // Step 1: Login with valid credentials
            LoginRequest loginRequest = new LoginRequest(VALID_ADMIN_USERNAME, VALID_ADMIN_PASSWORD);

            MvcResult loginResult = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(loginRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.success").value(true))
                    .andExpect(jsonPath("$.data.token").isNotEmpty())
                    .andExpect(jsonPath("$.data.userId").value("1"))
                    .andExpect(jsonPath("$.data.expiresIn").value(3600))
                    .andReturn();

            // Extract token from response
            String token = objectMapper.readTree(loginResult.getResponse().getContentAsString())
                    .get("data").get("token").asText();

            Assertions.assertNotNull(token, "Token should be generated on login");
            Assertions.assertFalse(token.isBlank(), "Token should not be blank");

            // Step 2: Use token for authenticated request (chat)
            ChatRequest chatRequest = new ChatRequest();
            chatRequest.setSessionId("test-session-001");
            chatRequest.setUserId("1");
            chatRequest.setMessage("Track my order");
            chatRequest.setContext(new HashMap<>());

            ChatResponse mockChatResponse = new ChatResponse(true, "Your order is in transit",
                    "logistics_query", "test-session-001", false);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockChatResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .header("Authorization", "Bearer " + token)
                            .content(objectMapper.writeValueAsString(chatRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.response").value("Your order is in transit"));
        }

        @Test
        @DisplayName("Test authentication with different user roles - FR1.2")
        void testAuthenticationWithDifferentUserRoles() throws Exception {
            // Test admin user
            LoginRequest adminRequest = new LoginRequest(VALID_ADMIN_USERNAME, VALID_ADMIN_PASSWORD);

            MvcResult adminResult = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(adminRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.userId").value("1"))
                    .andReturn();

            String adminToken = objectMapper.readTree(adminResult.getResponse().getContentAsString())
                    .get("data").get("token").asText();

            // Test regular user
            LoginRequest userRequest = new LoginRequest(VALID_USER_USERNAME, VALID_USER_PASSWORD);

            MvcResult userResult = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(userRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.userId").value("2"))
                    .andReturn();

            String userToken = objectMapper.readTree(userResult.getResponse().getContentAsString())
                    .get("data").get("token").asText();

            // Both users should have valid tokens
            Assertions.assertNotNull(adminToken);
            Assertions.assertNotNull(userToken);
            Assertions.assertNotEquals(adminToken, userToken, "Tokens should be unique per user");
        }

        @Test
        @DisplayName("Test token uniqueness for multiple logins - FR1.3")
        void testTokenUniquenessForMultipleLogins() throws Exception {
            LoginRequest request = new LoginRequest(VALID_ADMIN_USERNAME, VALID_ADMIN_PASSWORD);

            // Login multiple times
            MvcResult result1 = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andReturn();

            MvcResult result2 = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andReturn();

            MvcResult result3 = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andReturn();

            String token1 = objectMapper.readTree(result1.getResponse().getContentAsString())
                    .get("data").get("token").asText();
            String token2 = objectMapper.readTree(result2.getResponse().getContentAsString())
                    .get("data").get("token").asText();
            String token3 = objectMapper.readTree(result3.getResponse().getContentAsString())
                    .get("data").get("token").asText();

            // All tokens should be unique
            Assertions.assertNotEquals(token1, token2, "Tokens should be unique");
            Assertions.assertNotEquals(token2, token3, "Tokens should be unique");
            Assertions.assertNotEquals(token1, token3, "Tokens should be unique");
        }

        @Test
        @DisplayName("Test authentication failure with invalid credentials - FR1.1, FR1.2")
        void testAuthenticationFailureWithInvalidCredentials() throws Exception {
            // Invalid username
            LoginRequest invalidUsername = new LoginRequest("invalid_user", "password123");
            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(invalidUsername)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_002"));

            // Invalid password
            LoginRequest invalidPassword = new LoginRequest(VALID_ADMIN_USERNAME, "wrongpassword");
            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(invalidPassword)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_002"));

            // Both invalid
            LoginRequest bothInvalid = new LoginRequest("invalid", "invalid");
            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(bothInvalid)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_002"));
        }

        @Test
        @DisplayName("Test authentication validation with empty/blank credentials - FR1.1, FR1.2")
        void testAuthenticationValidationWithEmptyCredentials() throws Exception {
            // Empty username
            LoginRequest emptyUsername = new LoginRequest("", VALID_ADMIN_PASSWORD);
            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(emptyUsername)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_001"));

            // Empty password
            LoginRequest emptyPassword = new LoginRequest(VALID_ADMIN_USERNAME, "");
            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(emptyPassword)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_001"));

            // Blank username
            LoginRequest blankUsername = new LoginRequest("   ", "password");
            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(blankUsername)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_001"));

            // Blank password
            LoginRequest blankPassword = new LoginRequest("admin", "   ");
            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(blankPassword)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_001"));
        }
    }

    // ==================== Chat Routing Tests ====================

    @Nested
    @DisplayName("Chat Routing Tests - FR1.3, NFR7")
    class ChatRoutingTests {

        @Test
        @DisplayName("Test chat routing to Python core service - FR1.3, NFR7")
        void testChatRoutingToPythonCore() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-routing-001");
            request.setUserId("1");
            request.setMessage("I want to track my order");
            request.setContext(new HashMap<>());

            ChatResponse mockResponse = new ChatResponse(
                    true,
                    "Your order #ORD-12345 is currently in transit. Expected delivery: Tomorrow.",
                    "logistics_query",
                    "session-routing-001",
                    false
            );
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.success").value(true))
                    .andExpect(jsonPath("$.data.intent").value("logistics_query"))
                    .andExpect(jsonPath("$.data.response").value("Your order #ORD-12345 is currently in transit. Expected delivery: Tomorrow."))
                    .andExpect(jsonPath("$.data.sessionId").value("session-routing-001"));

            // Verify Feign client was called
            verify(ticketServiceClient, times(1)).chat(any(ChatRequest.class));
        }

        @Test
        @DisplayName("Test chat routing with different intents - FR1.3")
        void testChatRoutingWithDifferentIntents() throws Exception {
            // Test urgent ticket intent
            ChatRequest urgentRequest = new ChatRequest();
            urgentRequest.setSessionId("session-urgent-001");
            urgentRequest.setUserId("1");
            urgentRequest.setMessage("I need urgent help with my order");
            urgentRequest.setContext(new HashMap<>());

            ChatResponse urgentResponse = new ChatResponse(
                    true,
                    "Creating urgent ticket for your order. Our support team will contact you within 1 hour.",
                    "urgent_ticket",
                    "session-urgent-001",
                    false
            );
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(urgentResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(urgentRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.intent").value("urgent_ticket"));

            // Test cancel order intent
            ChatRequest cancelRequest = new ChatRequest();
            cancelRequest.setSessionId("session-cancel-001");
            cancelRequest.setUserId("1");
            cancelRequest.setMessage("I want to cancel my order");
            cancelRequest.setContext(new HashMap<>());

            ChatResponse cancelResponse = new ChatResponse(
                    true,
                    "Your order has been cancelled. Refund of $99.99 will be processed within 3-5 business days.",
                    "cancel_order",
                    "session-cancel-001",
                    false
            );
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(cancelResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(cancelRequest)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.intent").value("cancel_order"));
        }

        @Test
        @DisplayName("Test chat routing preserves session context - FR1.3")
        void testChatRoutingPreservesSessionContext() throws Exception {
            Map<String, Object> context = new HashMap<>();
            context.put("orderId", "ORD-12345");
            context.put("previousIntent", "logistics_query");

            ChatRequest request = new ChatRequest();
            request.setSessionId("session-context-001");
            request.setUserId("1");
            request.setMessage("What's the status?");
            request.setContext(context);

            ChatResponse mockResponse = new ChatResponse(
                    true,
                    "Your order is out for delivery.",
                    "logistics_query",
                    "session-context-001",
                    false
            );
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.sessionId").value("session-context-001"));

            // Verify the request was passed to the Feign client with context
            verify(ticketServiceClient).chat(argThat(req ->
                    req.getSessionId().equals("session-context-001") &&
                            req.getContext() != null &&
                            req.getContext().containsKey("orderId")
            ));
        }
    }

    // ==================== Error Handling Tests ====================

    @Nested
    @DisplayName("Error Handling Tests - NFR8")
    class ErrorHandlingTests {

        @Test
        @DisplayName("Test error handling when Python core service is unavailable - NFR8")
        void testErrorHandlingWhenServiceUnavailable() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-error-001");
            request.setUserId("1");
            request.setMessage("Track my order");
            request.setContext(new HashMap<>());

            when(ticketServiceClient.chat(any(ChatRequest.class)))
                    .thenThrow(new RuntimeException("Connection refused: python-core:8000"));

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isInternalServerError())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_ERROR"))
                    .andExpect(jsonPath("$.message").exists())
                    .andExpect(jsonPath("$.message").value("Failed to process chat: Connection refused: python-core:8000"));
        }

        @Test
        @DisplayName("Test error handling for timeout scenarios - NFR8")
        void testErrorHandlingForTimeout() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-timeout-001");
            request.setUserId("1");
            request.setMessage("Track my order");
            request.setContext(new HashMap<>());

            when(ticketServiceClient.chat(any(ChatRequest.class)))
                    .thenThrow(new RuntimeException("Read timed out"));

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isInternalServerError())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_ERROR"))
                    .andExpect(jsonPath("$.message").value("Failed to process chat: Read timed out"));
        }

        @Test
        @DisplayName("Test error handling for invalid JSON - NFR8")
        void testErrorHandlingForInvalidJson() throws Exception {
            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{invalid json}"))
                    .andExpect(status().isBadRequest());
        }

        @Test
        @DisplayName("Test error handling for missing required fields - NFR8")
        void testErrorHandlingForMissingRequiredFields() throws Exception {
            // Missing session ID
            String missingSessionId = "{\"userId\": \"1\", \"message\": \"test\"}";
            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(missingSessionId))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.errorCode").value("CHAT_002"));

            // Missing user ID
            String missingUserId = "{\"sessionId\": \"session-1\", \"message\": \"test\"}";
            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(missingUserId))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.errorCode").value("CHAT_003"));

            // Missing message
            String missingMessage = "{\"sessionId\": \"session-1\", \"userId\": \"1\"}";
            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(missingMessage))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.errorCode").value("CHAT_004"));
        }

        @Test
        @DisplayName("Test error response format consistency - NFR8")
        void testErrorResponseFormatConsistency() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-consistency-001");
            request.setUserId("1");
            request.setMessage("Track my order");
            request.setContext(new HashMap<>());

            when(ticketServiceClient.chat(any(ChatRequest.class)))
                    .thenThrow(new RuntimeException("Service error"));

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isInternalServerError())
                    .andExpect(jsonPath("$.success").exists())
                    .andExpect(jsonPath("$.message").exists())
                    .andExpect(jsonPath("$.errorCode").exists())
                    .andExpect(jsonPath("$.timestamp").exists())
                    .andExpect(jsonPath("$.data").doesNotExist());
        }
    }

    // ==================== Response Mapping Tests ====================

    @Nested
    @DisplayName("Response Mapping Tests - NFR8")
    class ResponseMappingTests {

        @Test
        @DisplayName("Test chat response mapping from Python core - NFR8")
        void testChatResponseMappingFromPythonCore() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-mapping-001");
            request.setUserId("1");
            request.setMessage("Track my order");
            request.setContext(new HashMap<>());

            ChatResponse pythonResponse = new ChatResponse(
                    true,
                    "Your order is ready for pickup at Store A",
                    "logistics_query",
                    "session-mapping-001",
                    false
            );
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(pythonResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.success").value(true))
                    .andExpect(jsonPath("$.data.response").value("Your order is ready for pickup at Store A"))
                    .andExpect(jsonPath("$.data.intent").value("logistics_query"))
                    .andExpect(jsonPath("$.data.sessionId").value("session-mapping-001"))
                    .andExpect(jsonPath("$.data.needsClarification").value(false));
        }

        @Test
        @DisplayName("Test logistics response mapping - FR3.1, FR3.2, FR3.3, FR3.4, NFR8")
        void testLogisticsResponseMapping() throws Exception {
            String orderId = "ORD-12345";

            LogisticsResponse.TrackingEvent event1 = new LogisticsResponse.TrackingEvent(
                    "Order placed", "Online", Instant.parse("2024-01-15T10:00:00Z"));
            LogisticsResponse.TrackingEvent event2 = new LogisticsResponse.TrackingEvent(
                    "Processing", "Warehouse", Instant.parse("2024-01-15T14:00:00Z"));
            LogisticsResponse.TrackingEvent event3 = new LogisticsResponse.TrackingEvent(
                    "Shipped", "Distribution Center", Instant.parse("2024-01-16T09:00:00Z"));

            LogisticsResponse pythonResponse = new LogisticsResponse(
                    orderId,
                    "In Transit",
                    "In Transit",
                    Instant.parse("2024-01-18T18:00:00Z"),
                    Arrays.asList(event1, event2, event3)
            );

            when(ticketServiceClient.getLogistics(orderId)).thenReturn(pythonResponse);

            ApiResponse<LogisticsResponse> response = new ChatService(ticketServiceClient).getLogistics(orderId);

            Assertions.assertTrue(response.isSuccess());
            Assertions.assertNotNull(response.getData());
            Assertions.assertEquals(orderId, response.getData().getOrderId());
            Assertions.assertEquals("In Transit", response.getData().getStatus());
            Assertions.assertEquals("In Transit", response.getData().getLatestStatus());
            Assertions.assertEquals(3, response.getData().getTrackingHistory().size());
            Assertions.assertNotNull(response.getData().getEstimatedDelivery());
        }

        @Test
        @DisplayName("Test urgent ticket response mapping - FR4.1, FR4.2, FR4.3, FR4.4, NFR8")
        void testUrgentTicketResponseMapping() throws Exception {
            UrgentTicketRequest request = new UrgentTicketRequest("ORD-12345", "Urgent delivery needed");

            UrgentTicketResponse pythonResponse = new UrgentTicketResponse(
                    "TKT-789",
                    Instant.parse("2024-01-17T12:00:00Z"),
                    "Priority Support Team"
            );

            when(ticketServiceClient.createUrgentTicket(any(UrgentTicketRequest.class)))
                    .thenReturn(pythonResponse);

            ApiResponse<UrgentTicketResponse> response = new ChatService(ticketServiceClient).createUrgentTicket(request);

            Assertions.assertTrue(response.isSuccess());
            Assertions.assertNotNull(response.getData());
            Assertions.assertEquals("TKT-789", response.getData().getTicketId());
            Assertions.assertNotNull(response.getData().getEstimatedProcessingTime());
            Assertions.assertEquals("Priority Support Team", response.getData().getContact());
        }

        @Test
        @DisplayName("Test cancel order response mapping - FR5.1, FR5.2, FR5.3, FR5.4, FR5.5, NFR8")
        void testCancelOrderResponseMapping() throws Exception {
            CancelOrderRequest request = new CancelOrderRequest("ORD-12345", "Customer changed mind");

            CancelOrderResponse pythonResponse = new CancelOrderResponse(
                    "ORD-12345",
                    149.99,
                    Instant.parse("2024-01-20T12:00:00Z"),
                    "Your order has been cancelled successfully. A full refund of $149.99 will be processed within 3-5 business days."
            );

            when(ticketServiceClient.cancelOrder(any(CancelOrderRequest.class)))
                    .thenReturn(pythonResponse);

            ApiResponse<CancelOrderResponse> response = new ChatService(ticketServiceClient).cancelOrder(request);

            Assertions.assertTrue(response.isSuccess());
            Assertions.assertNotNull(response.getData());
            Assertions.assertEquals("ORD-12345", response.getData().getOrderId());
            Assertions.assertEquals(149.99, response.getData().getRefundAmount());
            Assertions.assertNotNull(response.getData().getRefundArrivalTime());
            Assertions.assertNotNull(response.getData().getMessage());
        }

        @Test
        @DisplayName("Test response mapping preserves all fields - NFR8")
        void testResponseMappingPreservesAllFields() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-all-fields-001");
            request.setUserId("1");
            request.setMessage("Test message");
            request.setContext(new HashMap<>());

            ChatResponse pythonResponse = new ChatResponse(
                    true,
                    "Test response",
                    "test_intent",
                    "session-all-fields-001",
                    true
            );
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(pythonResponse);

            ApiResponse<ChatResponse> response = new ChatService(ticketServiceClient).processChat(request);

            Assertions.assertNotNull(response.getData());
            Assertions.assertEquals(pythonResponse.isSuccess(), response.getData().isSuccess());
            Assertions.assertEquals(pythonResponse.getResponse(), response.getData().getResponse());
            Assertions.assertEquals(pythonResponse.getIntent(), response.getData().getIntent());
            Assertions.assertEquals(pythonResponse.getSessionId(), response.getData().getSessionId());
            Assertions.assertEquals(pythonResponse.isNeedsClarification(), response.getData().isNeedsClarification());
        }
    }

    // ==================== API Response Format Tests ====================

    @Nested
    @DisplayName("API Response Format Tests - NFR7")
    class ApiResponseFormatTests {

        @Test
        @DisplayName("Test successful response format - NFR7")
        void testSuccessfulResponseFormat() throws Exception {
            LoginRequest request = new LoginRequest(VALID_ADMIN_USERNAME, VALID_ADMIN_PASSWORD);

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data").exists())
                    .andExpect(jsonPath("$.data.success").exists())
                    .andExpect(jsonPath("$.data.token").exists())
                    .andExpect(jsonPath("$.data.userId").exists())
                    .andExpect(jsonPath("$.data.expiresIn").exists())
                    .andExpect(jsonPath("$.message").exists())
                    .andExpect(jsonPath("$.timestamp").exists());
        }

        @Test
        @DisplayName("Test error response format - NFR7")
        void testErrorResponseFormat() throws Exception {
            LoginRequest request = new LoginRequest("invalid", "invalid");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.data").doesNotExist())
                    .andExpect(jsonPath("$.message").exists())
                    .andExpect(jsonPath("$.errorCode").exists())
                    .andExpect(jsonPath("$.timestamp").exists());
        }

        @Test
        @DisplayName("Test response timestamp format - NFR7")
        void testResponseTimestampFormat() throws Exception {
            LoginRequest request = new LoginRequest(VALID_ADMIN_USERNAME, VALID_ADMIN_PASSWORD);

            MvcResult result = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andReturn();

            String responseBody = result.getResponse().getContentAsString();
            Instant timestamp = Instant.parse(objectMapper.readTree(responseBody).get("timestamp").asText());

            Assertions.assertNotNull(timestamp);
            Assertions.assertTrue(timestamp.isBefore(Instant.now().plusSeconds(1)));
            Assertions.assertTrue(timestamp.isAfter(Instant.now().minusSeconds(5)));
        }
    }

    // ==================== Content Type and Headers Tests ====================

    @Nested
    @DisplayName("Content Type and Headers Tests")
    class ContentTypeAndHeadersTests {

        @Test
        @DisplayName("Test response content type is JSON")
        void testResponseContentTypeIsJson() throws Exception {
            LoginRequest request = new LoginRequest(VALID_ADMIN_USERNAME, VALID_ADMIN_PASSWORD);

            MvcResult result = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andReturn();

            String contentType = result.getResponse().getContentType();
            Assertions.assertNotNull(contentType);
            Assertions.assertTrue(contentType.contains("application/json"));
        }

        @Test
        @DisplayName("Test request with valid content type")
        void testRequestWithValidContentType() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-content-001");
            request.setUserId("1");
            request.setMessage("Test");
            request.setContext(new HashMap<>());

            ChatResponse mockResponse = new ChatResponse(true, "Response", "test", "session-content-001", false);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true));
        }
    }
}