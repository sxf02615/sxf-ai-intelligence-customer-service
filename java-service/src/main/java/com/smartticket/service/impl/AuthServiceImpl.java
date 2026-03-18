package com.smartticket.service.impl;

import com.smartticket.repository.AuthRepository;
import com.smartticket.service.AuthResult;
import com.smartticket.service.AuthService;
import com.smartticket.service.UserInfo;
import org.springframework.stereotype.Service;

import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

/**
 * Authentication service implementation.
 * FR1.3 - Token generation and validation
 * FR1.5 - Authentication abstraction for business system integration
 */
@Service
public class AuthServiceImpl implements AuthService {
    
    private static final long TOKEN_EXPIRATION_MS = 3600000; // 1 hour
    
    private final AuthRepository authRepository;
    private final ConcurrentMap<String, TokenInfo> validTokens;
    
    public AuthServiceImpl(AuthRepository authRepository) {
        this.authRepository = authRepository;
        this.validTokens = new ConcurrentHashMap<>();
    }
    
    @Override
    public AuthResult authenticate(String username, String password) {
        UserInfo user = authRepository.validateCredentials(username, password);
        
        if (user != null) {
            String token = generateToken();
            validTokens.put(token, new TokenInfo(user.getUserId(), username, System.currentTimeMillis() + TOKEN_EXPIRATION_MS));
            
            return new AuthResult(true, token, user.getUserId(), "Authentication successful");
        }
        
        return new AuthResult(false, null, null, "Invalid username or password");
    }
    
    @Override
    public UserInfo getUserByToken(String token) {
        TokenInfo tokenInfo = validTokens.get(token);
        
        if (tokenInfo != null && !isTokenExpired(tokenInfo)) {
            return authRepository.getUserByUsername(tokenInfo.username);
        }
        
        return null;
    }
    
    @Override
    public boolean validateToken(String token) {
        if (token == null) {
            return false;
        }
        TokenInfo tokenInfo = validTokens.get(token);
        return tokenInfo != null && !isTokenExpired(tokenInfo);
    }
    
    @Override
    public void logout(String token) {
        validTokens.remove(token);
    }
    
    /**
     * Generates a unique authentication token.
     * 
     * @return a UUID-based token string
     */
    private String generateToken() {
        return UUID.randomUUID().toString();
    }
    
    /**
     * Checks if a token has expired.
     * 
     * @param tokenInfo the token information to check
     * @return true if the token is expired, false otherwise
     */
    private boolean isTokenExpired(TokenInfo tokenInfo) {
        return System.currentTimeMillis() > tokenInfo.expirationTime;
    }
    
    /**
     * Internal class to store token metadata.
     */
    private static class TokenInfo {
        final String userId;
        final String username;
        final long expirationTime;
        
        TokenInfo(String userId, String username, long expirationTime) {
            this.userId = userId;
            this.username = username;
            this.expirationTime = expirationTime;
        }
    }
}