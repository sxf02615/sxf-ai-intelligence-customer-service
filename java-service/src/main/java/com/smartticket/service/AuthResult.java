package com.smartticket.service;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Authentication result containing the outcome of an authentication attempt.
 * FR1.5 - Authentication abstraction for business system integration
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AuthResult {
    /**
     * Whether the authentication was successful
     */
    private boolean success;
    
    /**
     * The authentication token (set on successful authentication)
     */
    private String token;
    
    /**
     * The user ID (set on successful authentication)
     */
    private String userId;
    
    /**
     * Error or status message
     */
    private String message;
}