package com.smartticket.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
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
    @JsonProperty("order_id")
    private String orderId;
    private String reason;
}