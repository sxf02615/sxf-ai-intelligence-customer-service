package com.smartticket.dto;

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
    private String sessionId;
    private String userId;
    private String message;
    private Map<String, Object> context;
}