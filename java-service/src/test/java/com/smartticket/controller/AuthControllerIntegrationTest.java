package com.smartticket.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartticket.dto.LoginRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for AuthController.
 * Tests: FR1.1, FR1.2, FR1.3 - Authentication flow end-to-end
 * Validates: NFR7, NFR8 - HTTP communication and response handling
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@DisplayName("AuthController Integration Tests")
class AuthControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Nested
    @DisplayName("Successful Login Tests")
    class SuccessfulLoginTests {

        @Test
        @DisplayName("Test successful login with valid admin credentials - FR1.1, FR1.2")
        void testSuccessfulLoginWithValidAdminCredentials() throws Exception {
            LoginRequest request = new LoginRequest("admin", "admin123");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.success").value(true))
                    .andExpect(jsonPath("$.data.token").isNotEmpty())
                    .andExpect(jsonPath("$.data.userId").value("1"))
                    .andExpect(jsonPath("$.data.expiresIn").value(3600))
                    .andExpect(jsonPath("$.message").value("Login successful"));
        }

        @Test
        @DisplayName("Test successful login with valid user credentials - FR1.1, FR1.2")
        void testSuccessfulLoginWithValidUserCredentials() throws Exception {
            LoginRequest request = new LoginRequest("user", "user123");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.success").value(true))
                    .andExpect(jsonPath("$.data.token").isNotEmpty())
                    .andExpect(jsonPath("$.data.userId").value("2"))
                    .andExpect(jsonPath("$.data.expiresIn").value(3600));
        }

        @Test
        @DisplayName("Test login generates unique tokens - FR1.3")
        void testLoginGeneratesUniqueTokens() throws Exception {
            LoginRequest request = new LoginRequest("admin", "admin123");

            MvcResult result1 = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andReturn();

            MvcResult result2 = mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andReturn();

            String token1 = objectMapper.readTree(result1.getResponse().getContentAsString())
                    .get("data").get("token").asText();
            String token2 = objectMapper.readTree(result2.getResponse().getContentAsString())
                    .get("data").get("token").asText();

            org.junit.jupiter.api.Assertions.assertNotEquals(token1, token2);
        }
    }

    @Nested
    @DisplayName("Failed Login Tests")
    class FailedLoginTests {

        @Test
        @DisplayName("Test failed login with invalid username - FR1.1, FR1.2")
        void testFailedLoginWithInvalidUsername() throws Exception {
            LoginRequest request = new LoginRequest("nonexistent", "password");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_002"))
                    .andExpect(jsonPath("$.message").value("Invalid username or password"));
        }

        @Test
        @DisplayName("Test failed login with invalid password - FR1.1, FR1.2")
        void testFailedLoginWithInvalidPassword() throws Exception {
            LoginRequest request = new LoginRequest("admin", "wrongpassword");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_002"));
        }

        @Test
        @DisplayName("Test failed login with empty username - FR1.1, FR1.2")
        void testFailedLoginWithEmptyUsername() throws Exception {
            LoginRequest request = new LoginRequest("", "password");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_001"));
        }

        @Test
        @DisplayName("Test failed login with empty password - FR1.1, FR1.2")
        void testFailedLoginWithEmptyPassword() throws Exception {
            LoginRequest request = new LoginRequest("admin", "");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_001"));
        }

        @Test
        @DisplayName("Test failed login with null request body - FR1.1, FR1.2")
        void testFailedLoginWithNullRequestBody() throws Exception {
            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{}"))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_001"));
        }

        @Test
        @DisplayName("Test failed login with blank credentials - FR1.1, FR1.2")
        void testFailedLoginWithBlankCredentials() throws Exception {
            LoginRequest request = new LoginRequest("   ", "   ");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.errorCode").value("AUTH_001"));
        }
    }

    @Nested
    @DisplayName("Response Format Tests - NFR7, NFR8")
    class ResponseFormatTests {

        @Test
        @DisplayName("Test response contains timestamp - NFR7")
        void testResponseContainsTimestamp() throws Exception {
            LoginRequest request = new LoginRequest("admin", "admin123");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.timestamp").isNotEmpty());
        }

        @Test
        @DisplayName("Test error response format consistency - NFR8")
        void testErrorResponseFormatConsistency() throws Exception {
            LoginRequest request = new LoginRequest("invalid", "invalid");

            mockMvc.perform(post("/api/v1/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").exists())
                    .andExpect(jsonPath("$.message").exists())
                    .andExpect(jsonPath("$.errorCode").exists())
                    .andExpect(jsonPath("$.timestamp").exists());
        }
    }
}