package com.smartticket.service;

/**
 * Authentication service abstraction interface.
 * FR1.5 - Authentication abstraction for business system integration
 * FR1.6 - Support configuration-based switching (config file / business system integration)
 */
public interface AuthService {
    
    /**
     * Authenticates a user with username and password credentials.
     * 
     * @param username the username to authenticate
     * @param password the password to verify
     * @return AuthResult containing the authentication outcome, token on success
     */
    AuthResult authenticate(String username, String password);
    
    /**
     * Retrieves user information based on the provided authentication token.
     * 
     * @param token the authentication token
     * @return UserInfo containing user details, or null if token is invalid
     */
    UserInfo getUserByToken(String token);
    
    /**
     * Validates whether an authentication token is currently valid and not expired.
     * 
     * @param token the authentication token to validate
     * @return true if the token is valid, false otherwise
     */
    boolean validateToken(String token);
    
    /**
     * Logs out the user by invalidating the provided authentication token.
     * 
     * @param token the authentication token to invalidate
     */
    void logout(String token);
}