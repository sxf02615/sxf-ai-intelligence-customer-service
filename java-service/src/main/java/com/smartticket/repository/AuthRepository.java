package com.smartticket.repository;

import com.smartticket.service.UserInfo;

/**
 * Abstract interface for user authentication data access.
 * FR1.1 - User authentication against configuration
 * FR1.2 - Support multiple users with different roles
 * FR1.6 - Support configuration-based switching
 */
public interface AuthRepository {
    
    /**
     * Validates user credentials and returns user information if valid.
     * 
     * @param username the username to look up
     * @param password the password to verify
     * @return UserInfo if credentials are valid, null otherwise
     */
    UserInfo validateCredentials(String username, String password);
    
    /**
     * Retrieves user information by username.
     * 
     * @param username the username to look up
     * @return UserInfo if user exists, null otherwise
     */
    UserInfo getUserByUsername(String username);
}