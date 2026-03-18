package com.smartticket.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Chat response DTO for system replies.
 * FR1.3 - Chat interaction
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponse {
    private boolean success;
    private String response;
    private String intent;
    private String sessionId;
    private boolean needsClarification;
}