package com.smartticket.service.impl;

import com.smartticket.repository.AuthRepository;
import com.smartticket.service.AuthResult;
import com.smartticket.service.AuthService;
import com.smartticket.service.UserInfo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for AuthServiceImpl.
 * Tests: FR1.1, FR1.2, FR1.3
 */
@DisplayName("AuthService Tests")
class AuthServiceImplTest {
    
    private AuthService authService;
    private AuthRepository authRepository;
    
    @BeforeEach
    void setUp() {
        authRepository = new MockAuthRepository();
        authService = new AuthServiceImpl(authRepository);
    }
    
    @Nested
    @DisplayName("Successful Login Tests")
    class SuccessfulLoginTests {
        
        @Test
        @DisplayName("Test successful login with valid admin credentials - FR1.1, FR1.2")
        void testSuccessfulLoginWithValidAdminCredentials() {
            AuthResult result = authService.authenticate("admin", "admin123");
            
            assertTrue(result.isSuccess());
            assertNotNull(result.getToken());
            assertEquals("1", result.getUserId());
            assertEquals("Authentication successful", result.getMessage());
        }
        
        @Test
        @DisplayName("Test successful login with valid user credentials - FR1.1, FR1.2")
        void testSuccessfulLoginWithValidUserCredentials() {
            AuthResult result = authService.authenticate("user", "user123");
            
            assertTrue(result.isSuccess());
            assertNotNull(result.getToken());
            assertEquals("2", result.getUserId());
            assertEquals("Authentication successful", result.getMessage());
        }
        
        @Test
        @DisplayName("Test login generates unique tokens - FR1.3")
        void testLoginGeneratesUniqueTokens() {
            AuthResult result1 = authService.authenticate("admin", "admin123");
            AuthResult result2 = authService.authenticate("admin", "admin123");
            
            assertNotEquals(result1.getToken(), result2.getToken());
        }
    }
    
    @Nested
    @DisplayName("Failed Login Tests")
    class FailedLoginTests {
        
        @Test
        @DisplayName("Test failed login with invalid username - FR1.1, FR1.2")
        void testFailedLoginWithInvalidUsername() {
            AuthResult result = authService.authenticate("nonexistent", "password");
            
            assertFalse(result.isSuccess());
            assertNull(result.getToken());
            assertNull(result.getUserId());
            assertEquals("Invalid username or password", result.getMessage());
        }
        
        @Test
        @DisplayName("Test failed login with invalid password - FR1.1, FR1.2")
        void testFailedLoginWithInvalidPassword() {
            AuthResult result = authService.authenticate("admin", "wrongpassword");
            
            assertFalse(result.isSuccess());
            assertNull(result.getToken());
            assertNull(result.getUserId());
            assertEquals("Invalid username or password", result.getMessage());
        }
        
        @Test
        @DisplayName("Test failed login with empty credentials - FR1.1, FR1.2")
        void testFailedLoginWithEmptyCredentials() {
            AuthResult result = authService.authenticate("", "");
            
            assertFalse(result.isSuccess());
            assertNull(result.getToken());
            assertNull(result.getUserId());
        }
    }
    
    @Nested
    @DisplayName("Token Validation Tests")
    class TokenValidationTests {
        
        @Test
        @DisplayName("Test token validation for valid token - FR1.3")
        void testTokenValidationForValidToken() {
            AuthResult loginResult = authService.authenticate("admin", "admin123");
            String token = loginResult.getToken();
            
            assertTrue(authService.validateToken(token));
        }
        
        @Test
        @DisplayName("Test token validation for invalid token - FR1.3")
        void testTokenValidationForInvalidToken() {
            assertFalse(authService.validateToken("invalid-token"));
        }
        
        @Test
        @DisplayName("Test token validation for null token - FR1.3")
        void testTokenValidationForNullToken() {
            assertFalse(authService.validateToken(null));
        }
        
        @Test
        @DisplayName("Test getUserByToken returns correct user - FR1.3")
        void testGetUserByTokenReturnsCorrectUser() {
            AuthResult loginResult = authService.authenticate("admin", "admin123");
            String token = loginResult.getToken();
            
            UserInfo user = authService.getUserByToken(token);
            
            assertNotNull(user);
            assertEquals("1", user.getUserId());
            assertEquals("admin", user.getUsername());
        }
        
        @Test
        @DisplayName("Test getUserByToken returns null for invalid token - FR1.3")
        void testGetUserByTokenReturnsNullForInvalidToken() {
            UserInfo user = authService.getUserByToken("invalid-token");
            
            assertNull(user);
        }
    }
    
    @Nested
    @DisplayName("Logout Tests")
    class LogoutTests {
        
        @Test
        @DisplayName("Test logout invalidates token - FR1.3")
        void testLogoutInvalidatesToken() {
            AuthResult loginResult = authService.authenticate("admin", "admin123");
            String token = loginResult.getToken();
            
            assertTrue(authService.validateToken(token));
            
            authService.logout(token);
            
            assertFalse(authService.validateToken(token));
        }
        
        @Test
        @DisplayName("Test logout of invalid token does not throw exception - FR1.3")
        void testLogoutOfInvalidTokenDoesNotThrowException() {
            assertDoesNotThrow(() -> authService.logout("invalid-token"));
        }
        
        @Test
        @DisplayName("Test logout multiple times does not throw exception - FR1.3")
        void testLogoutMultipleTimesDoesNotThrowException() {
            AuthResult loginResult = authService.authenticate("admin", "admin123");
            String token = loginResult.getToken();
            
            authService.logout(token);
            assertDoesNotThrow(() -> authService.logout(token));
        }
    }
    
    /**
     * Mock implementation of AuthRepository for testing.
     */
    private static class MockAuthRepository implements AuthRepository {
        private final java.util.Map<String, UserInfo> users = new java.util.HashMap<>();
        private final java.util.Map<String, String> passwordStore = new java.util.HashMap<>();
        
        public MockAuthRepository() {
            UserInfo adminUser = new UserInfo("1", "admin", "role:admin");
            users.put("admin", adminUser);
            passwordStore.put("admin", "admin123");
            
            UserInfo regularUser = new UserInfo("2", "user", "role:user");
            users.put("user", regularUser);
            passwordStore.put("user", "user123");
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
}