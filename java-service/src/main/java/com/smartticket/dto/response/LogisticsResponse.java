package com.smartticket.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response DTO for logistics information.
 * FR3.1, FR3.2, FR3.3, FR3.4 - Logistics query
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class LogisticsResponse {
    
    private String orderId;
    private String status;
    
    @JsonProperty("latest_status")
    private String latestStatus;
    
    @JsonProperty("estimated_delivery")
    private Instant estimatedDelivery;
    
    @JsonProperty("tracking_history")
    private List<TrackingEvent> trackingHistory;
    
    /**
     * Tracking event for logistics history.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TrackingEvent {
        private String status;
        private String description;
        private Instant timestamp;
    }
}