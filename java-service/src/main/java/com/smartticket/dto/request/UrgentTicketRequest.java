package com.smartticket.dto.request;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request DTO for creating urgent tickets.
 * FR4.1, FR4.2 - Urgent ticket creation
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UrgentTicketRequest {
    private String orderId;
    private String reason;
}