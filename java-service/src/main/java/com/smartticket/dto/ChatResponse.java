package com.smartticket.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
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
    
    @JsonProperty("session_id")
    private String sessionId;
    
    @JsonProperty("needs_clarification")
    private boolean needsClarification;
    
    @JsonProperty("clarification_question")
    private String clarificationQuestion;
}