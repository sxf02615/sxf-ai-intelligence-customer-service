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
 * 认证服务实现。
 * FR1.3 - 令牌生成和验证
 * FR1.5 - 业务系统集成的身份验证抽象
 */
@Service
public class AuthServiceImpl implements AuthService {
    
    private static final long TOKEN_EXPIRATION_MS = 3600000; // 1小时
    
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
     * 生成唯一的认证令牌。
     * 
     * @return 基于UUID的令牌字符串
     */
    private String generateToken() {
        return UUID.randomUUID().toString();
    }
    
    /**
     * 检查令牌是否已过期。
     * 
     * @param tokenInfo 要检查的令牌信息
     * @return 如果令牌已过期返回true，否则返回false
     */
    private boolean isTokenExpired(TokenInfo tokenInfo) {
        return System.currentTimeMillis() > tokenInfo.expirationTime;
    }
    
    /**
     * 存储令牌元数据的内部类。
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