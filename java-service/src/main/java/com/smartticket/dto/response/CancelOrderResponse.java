package com.smartticket.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response DTO for order cancellation.
 * FR5.1, FR5.2, FR5.3, FR5.4, FR5.5 - Order cancellation
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CancelOrderResponse {
    
    @JsonProperty("order_id")
    private String orderId;
    
    @JsonProperty("refund_amount")
    private Double refundAmount;
    
    @JsonProperty("refund_arrival_time")
    private Instant refundArrivalTime;
    
    private String message;
}