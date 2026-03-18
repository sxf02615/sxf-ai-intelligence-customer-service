package com.smartticket.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response DTO for urgent ticket creation.
 * FR4.1, FR4.2, FR4.3, FR4.4 - Urgent ticket creation
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UrgentTicketResponse {
    
    @JsonProperty("ticket_id")
    private String ticketId;
    
    @JsonProperty("estimated_processing_time")
    private Instant estimatedProcessingTime;
    
    private String contact;
}