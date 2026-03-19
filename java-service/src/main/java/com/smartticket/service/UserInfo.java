package com.smartticket.service;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 从令牌验证中获取的用户信息。
 * FR1.5 - 业务系统集成的身份验证抽象
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserInfo {
    /**
     * 用户的唯一标识符
     */
    private String userId;
    
    /**
     * 用户名
     */
    private String username;
    
    /**
     * 额外的用户属性（例如，角色、部门）
     */
    private String attributes;
}