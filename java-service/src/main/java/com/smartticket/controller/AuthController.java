package com.smartticket.controller;

import com.smartticket.dto.ApiResponse;
import com.smartticket.dto.LoginRequest;
import com.smartticket.dto.LoginResponse;
import com.smartticket.service.AuthResult;
import com.smartticket.service.AuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Authentication controller handling user login requests.
 * FR1.1 - Login page endpoint
 * FR1.2 - Validate credentials via Java backend
 * FR1.3 - Return token on successful authentication
 */
@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {
    
    private final AuthService authService;
    
    public AuthController(AuthService authService) {
        this.authService = authService;
    }
    
    /**
     * Handles user login requests.
     * POST /api/v1/auth/login
     * 
     * @param loginRequest containing username and password
     * @return ApiResponse with LoginResponse containing token on success,
     *         or error message on failure
     */
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<LoginResponse>> login(@RequestBody LoginRequest loginRequest) {
        // 验证请求
        if (loginRequest == null || 
            loginRequest.getUsername() == null || 
            loginRequest.getPassword() == null ||
            loginRequest.getUsername().isBlank() || 
            loginRequest.getPassword().isBlank()) {
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error("用户名和密码不能为空", "AUTH_001"));
        }
        
        // 验证用户
        AuthResult result = authService.authenticate(loginRequest.getUsername(), loginRequest.getPassword());
        
        if (result.isSuccess()) {
            LoginResponse loginResponse = new LoginResponse(
                    true,
                    result.getToken(),
                    result.getUserId(),
                    3600 // Token有效期1小时（秒）
            );
            
            return ResponseEntity.ok(ApiResponse.success(loginResponse, "登录成功"));
        }
        
        return ResponseEntity.status(401)
                .body(ApiResponse.error(result.getMessage(), "AUTH_002"));
    }
}