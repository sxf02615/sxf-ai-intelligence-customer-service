package com.smartticket.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import feign.Client;
import feign.Logger;
import feign.Request;
import feign.Retryer;
import feign.codec.Decoder;
import feign.codec.Encoder;
import feign.jackson.JacksonDecoder;
import feign.jackson.JacksonEncoder;
import feign.okhttp.OkHttpClient;

/**
 * Feign client configuration for the Smart Ticket Service.
 * Configures the HTTP client to communicate with the Python Core service.
 */
@Configuration
public class FeignConfig {

    @Value("${python-core.url:http://localhost:8000}")
    private String pythonCoreUrl;

    @Bean
    public Client feignClient() {
        // Use OkHttpClient which is more robust and handles connection failures better
        return new OkHttpClient();
    }

    @Bean
    public Encoder feignEncoder() {
        return new JacksonEncoder();
    }

    @Bean
    public Decoder feignDecoder() {
        return new JacksonDecoder();
    }

    @Bean
    public Logger.Level feignLoggerLevel() {
        return Logger.Level.FULL;
    }

    @Bean
    public Request.Options requestOptions() {
        // Configure timeout options to prevent hanging on startup
        return new Request.Options(5000, 10000); // 5s connect timeout, 10s read timeout
    }

    @Bean
    public Retryer retryer() {
        // Configure retry policy
        return new Retryer.Default(100, 1000, 3);
    }
}