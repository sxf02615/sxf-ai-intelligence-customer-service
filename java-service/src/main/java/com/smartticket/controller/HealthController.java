package com.smartticket.controller;

import com.smartticket.dto.ApiResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * Health check controller for service monitoring.
 * NFR2 - Service health check endpoint
 */
@RestController
@RequestMapping("/health")
public class HealthController {
    
    private static final String SERVICE_NAME = "smart-ticket-service";
    private static final String SERVICE_VERSION = "1.0.0";
    
    /**
     * Health check endpoint for service monitoring.
     * GET /health
     * 
     * @return ApiResponse containing service status, version, and timestamp
     */
    @GetMapping
    public ResponseEntity<ApiResponse<Map<String, Object>>> health() {
        Map<String, Object> healthInfo = new HashMap<>();
        healthInfo.put("status", "UP");
        healthInfo.put("service", SERVICE_NAME);
        healthInfo.put("version", SERVICE_VERSION);
        healthInfo.put("timestamp", Instant.now().toString());
        
        return ResponseEntity.ok(ApiResponse.success(healthInfo, "Service is healthy"));
    }
}