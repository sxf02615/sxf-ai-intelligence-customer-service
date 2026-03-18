package com.smartticket.controller;

import com.smartticket.dto.ApiResponse;
import com.smartticket.dto.ChatRequest;
import com.smartticket.dto.ChatResponse;
import com.smartticket.service.ChatService;
import org.springframework.context.annotation.Lazy;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Chat controller handling user chat requests.
 * NFR7 - HTTP communication with Python core service
 * FR1.3 - Chat interaction
 */
@RestController
@RequestMapping("/api/v1/chat")
public class ChatController {
    
    private final ChatService chatService;
    
    public ChatController(@Lazy ChatService chatService) {
        this.chatService = chatService;
    }
    
    /**
     * Handles user chat messages.
     * POST /api/v1/chat
     * 
     * @param chatRequest containing session_id, user_id, and message
     * @return ApiResponse with ChatResponse containing system reply
     */
    @PostMapping
    public ResponseEntity<ApiResponse<ChatResponse>> chat(@RequestBody ChatRequest chatRequest) {
        // Validate request
        if (chatRequest == null) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Chat request is required", "CHAT_001"));
        }
        
        if (chatRequest.getSessionId() == null || chatRequest.getSessionId().isBlank()) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Session ID is required", "CHAT_002"));
        }
        
        if (chatRequest.getUserId() == null || chatRequest.getUserId().isBlank()) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("User ID is required", "CHAT_003"));
        }
        
        if (chatRequest.getMessage() == null || chatRequest.getMessage().isBlank()) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("Message is required", "CHAT_004"));
        }
        
        // Process chat message
        ApiResponse<ChatResponse> response = chatService.processChat(chatRequest);
        
        if (response.isSuccess()) {
            return ResponseEntity.ok(response);
        }
        
        return ResponseEntity.status(500).body(response);
    }
}