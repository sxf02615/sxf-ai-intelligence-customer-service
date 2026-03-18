package com.smartticket.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartticket.dto.ChatRequest;
import com.smartticket.dto.ChatResponse;
import com.smartticket.feign.TicketServiceClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.util.HashMap;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for ChatController.
 * Tests: FR1.3 - Chat interaction
 * Validates: NFR7, NFR8 - HTTP communication with Python core service
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@DisplayName("ChatController Integration Tests")
class ChatControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private TicketServiceClient ticketServiceClient;

    private ChatRequest createChatRequest(String sessionId, String userId, String message) {
        ChatRequest request = new ChatRequest();
        request.setSessionId(sessionId);
        request.setUserId(userId);
        request.setMessage(message);
        request.setContext(new HashMap<>());
        return request;
    }

    @Nested
    @DisplayName("Successful Chat Tests")
    class SuccessfulChatTests {

        @Test
        @DisplayName("Test successful chat request routing to Python core - FR1.3, NFR7")
        void testSuccessfulChatRequestRouting() throws Exception {
            ChatRequest request = createChatRequest("session-123", "user-1", "Track my order");

            ChatResponse mockResponse = new ChatResponse(true, "Your order is on the way", 
                    "logistics_query", "session-123", false);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.success").value(true))
                    .andExpect(jsonPath("$.data.response").value("Your order is on the way"))
                    .andExpect(jsonPath("$.data.intent").value("logistics_query"))
                    .andExpect(jsonPath("$.data.sessionId").value("session-123"));
        }

        @Test
        @DisplayName("Test chat with needsClarification flag - FR1.3")
        void testChatWithNeedsClarification() throws Exception {
            ChatRequest request = createChatRequest("session-456", "user-2", "Help");

            ChatResponse mockResponse = new ChatResponse(false, "Could you clarify?", 
                    "needs_clarification", "session-456", true);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.needsClarification").value(true));
        }

        @Test
        @DisplayName("Test chat response mapping from Python core - NFR8")
        void testChatResponseMapping() throws Exception {
            ChatRequest request = createChatRequest("session-789", "user-3", "Cancel my order");

            ChatResponse mockResponse = new ChatResponse(true, "Order cancelled successfully", 
                    "cancel_order", "session-789", false);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.data.intent").value("cancel_order"))
                    .andExpect(jsonPath("$.data.response").isNotEmpty());
        }
    }

    @Nested
    @DisplayName("Validation Error Tests")
    class ValidationErrorTests {

        @Test
        @DisplayName("Test chat with null request body - CHAT_001")
        void testChatWithNullRequestBody() throws Exception {
            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{}"))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_001"));
        }

        @Test
        @DisplayName("Test chat with missing session ID - CHAT_002")
        void testChatWithMissingSessionId() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setUserId("user-1");
            request.setMessage("Track my order");
            request.setContext(new HashMap<>());

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_002"));
        }

        @Test
        @DisplayName("Test chat with blank session ID - CHAT_002")
        void testChatWithBlankSessionId() throws Exception {
            ChatRequest request = createChatRequest("", "user-1", "Track my order");

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_002"));
        }

        @Test
        @DisplayName("Test chat with missing user ID - CHAT_003")
        void testChatWithMissingUserId() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-123");
            request.setMessage("Track my order");
            request.setContext(new HashMap<>());

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_003"));
        }

        @Test
        @DisplayName("Test chat with blank user ID - CHAT_003")
        void testChatWithBlankUserId() throws Exception {
            ChatRequest request = createChatRequest("session-123", "", "Track my order");

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_003"));
        }

        @Test
        @DisplayName("Test chat with missing message - CHAT_004")
        void testChatWithMissingMessage() throws Exception {
            ChatRequest request = new ChatRequest();
            request.setSessionId("session-123");
            request.setUserId("user-1");
            request.setContext(new HashMap<>());

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_004"));
        }

        @Test
        @DisplayName("Test chat with blank message - CHAT_004")
        void testChatWithBlankMessage() throws Exception {
            ChatRequest request = createChatRequest("session-123", "user-1", "   ");

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("CHAT_004"));
        }
    }

    @Nested
    @DisplayName("Error Handling Tests - NFR8")
    class ErrorHandlingTests {

        @Test
        @DisplayName("Test chat when Python core service is unavailable - NFR8")
        void testChatWhenServiceUnavailable() throws Exception {
            ChatRequest request = createChatRequest("session-123", "user-1", "Track my order");

            when(ticketServiceClient.chat(any(ChatRequest.class)))
                    .thenThrow(new RuntimeException("Connection refused"));

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isInternalServerError())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.message").exists())
                    .andExpect(jsonPath("$.errorCode").value("CHAT_ERROR"));
        }

        @Test
        @DisplayName("Test error response format consistency - NFR8")
        void testErrorResponseFormatConsistency() throws Exception {
            ChatRequest request = createChatRequest("session-123", "user-1", "Track my order");

            when(ticketServiceClient.chat(any(ChatRequest.class)))
                    .thenThrow(new RuntimeException("Service error"));

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isInternalServerError())
                    .andExpect(jsonPath("$.success").exists())
                    .andExpect(jsonPath("$.message").exists())
                    .andExpect(jsonPath("$.errorCode").exists())
                    .andExpect(jsonPath("$.timestamp").exists());
        }
    }

    @Nested
    @DisplayName("Response Format Tests - NFR7")
    class ResponseFormatTests {

        @Test
        @DisplayName("Test response contains timestamp - NFR7")
        void testResponseContainsTimestamp() throws Exception {
            ChatRequest request = createChatRequest("session-123", "user-1", "Track my order");

            ChatResponse mockResponse = new ChatResponse(true, "Your order is on the way", 
                    "logistics_query", "session-123", false);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.timestamp").isNotEmpty());
        }

        @Test
        @DisplayName("Test successful response structure - NFR7")
        void testSuccessfulResponseStructure() throws Exception {
            ChatRequest request = createChatRequest("session-123", "user-1", "Track my order");

            ChatResponse mockResponse = new ChatResponse(true, "Your order is on the way", 
                    "logistics_query", "session-123", false);
            when(ticketServiceClient.chat(any(ChatRequest.class))).thenReturn(mockResponse);

            mockMvc.perform(post("/api/v1/chat")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").exists())
                    .andExpect(jsonPath("$.data").exists())
                    .andExpect(jsonPath("$.data.success").exists())
                    .andExpect(jsonPath("$.data.response").exists())
                    .andExpect(jsonPath("$.data.intent").exists())
                    .andExpect(jsonPath("$.data.sessionId").exists());
        }
    }
}