package com.smartticket.dto.request;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request DTO for cancelling orders.
 * FR5.1, FR5.2 - Order cancellation
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CancelOrderRequest {
    private String orderId;
    private String reason;
}