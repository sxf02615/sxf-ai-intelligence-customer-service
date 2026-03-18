package com.smartticket;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

/**
 * Smart Ticket Service - Main Application Entry Point
 * 
 * This is the Java User Layer for the Smart Ticket System.
 * It handles authentication, session management, and acts as an API gateway
 * between the UI layer and the Python Core business layer.
 */
@SpringBootApplication
@EnableFeignClients
public class SmartTicketApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(SmartTicketApplication.class, args);
    }
}