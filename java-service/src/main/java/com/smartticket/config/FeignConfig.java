package com.smartticket.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import feign.Client;
import feign.Logger;
import feign.codec.Decoder;
import feign.codec.Encoder;
import feign.jackson.JacksonDecoder;
import feign.jackson.JacksonEncoder;

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
        return new Client.Default(null, null);
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
}