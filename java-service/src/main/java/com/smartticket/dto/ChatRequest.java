package com.smartticket.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Chat request DTO for user messages.
 * FR1.3 - Chat interaction
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatRequest {
    @JsonProperty("session_id")
    private String sessionId;
    
    @JsonProperty("user_id")
    private String userId;
    
    private String message;
    private Map<String, Object> context;
}