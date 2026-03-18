package com.smartticket.service;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * User information retrieved from token validation.
 * FR1.5 - Authentication abstraction for business system integration
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserInfo {
    /**
     * The unique identifier of the user
     */
    private String userId;
    
    /**
     * The username of the user
     */
    private String username;
    
    /**
     * Additional user attributes (e.g., role, department)
     */
    private String attributes;
}