package com.smartticket.feign;

import feign.Request;
import feign.Retryer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration for TicketServiceClient Feign client.
 * This configuration makes the Feign client more resilient to connection failures.
 */
@Configuration
public class TicketServiceClientConfig {

    @Bean
    public Request.Options ticketServiceRequestOptions() {
        // Configure timeout options to prevent hanging on startup
        // Connect timeout: 5 seconds, Read timeout: 10 seconds
        return new Request.Options(5000, 10000);
    }

    @Bean
    public Retryer ticketServiceRetryer() {
        // Configure retry policy: initial delay 100ms, max delay 1s, max attempts 3
        return new Retryer.Default(100, 1000, 3);
    }
}