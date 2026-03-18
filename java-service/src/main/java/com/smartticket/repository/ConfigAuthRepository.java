package com.smartticket.repository;

import com.smartticket.service.UserInfo;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;

import jakarta.annotation.PostConstruct;
import java.util.HashMap;
import java.util.Map;

/**
 * Configuration-based authentication repository implementation.
 * Reads user credentials from application configuration.
 * FR1.1 - User authentication against configuration
 * FR1.2 - Support multiple users with different roles
 * FR1.6 - Support configuration-based switching
 */
@Repository
public class ConfigAuthRepository implements AuthRepository {
    
    private final Map<String, UserInfo> users = new HashMap<>();
    private final Map<String, String> passwordStore = new HashMap<>();
    
    @Value("${auth.users.admin.username:admin}")
    private String adminUsername;
    
    @Value("${auth.users.admin.password:admin123}")
    private String adminPassword;
    
    @Value("${auth.users.admin.attributes:role:admin}")
    private String adminAttributes;
    
    @Value("${auth.users.user.username:user}")
    private String userUsername;
    
    @Value("${auth.users.user.password:user123}")
    private String userPassword;
    
    @Value("${auth.users.user.attributes:role:user}")
    private String userAttributes;
    
    @PostConstruct
    public void init() {
        // Load admin user
        UserInfo adminUser = new UserInfo("1", adminUsername, adminAttributes);
        users.put(adminUsername, adminUser);
        passwordStore.put(adminUsername, adminPassword);
        
        // Load regular user
        UserInfo regularUser = new UserInfo("2", userUsername, userAttributes);
        users.put(userUsername, regularUser);
        passwordStore.put(userUsername, userPassword);
    }
    
    @Override
    public UserInfo validateCredentials(String username, String password) {
        UserInfo user = users.get(username);
        if (user != null) {
            String storedPassword = passwordStore.get(username);
            if (storedPassword != null && storedPassword.equals(password)) {
                return user;
            }
        }
        return null;
    }
    
    @Override
    public UserInfo getUserByUsername(String username) {
        return users.get(username);
    }
}