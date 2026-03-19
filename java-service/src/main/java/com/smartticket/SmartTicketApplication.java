package com.smartticket;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

/**
 * 智能工单服务 - 主应用程序入口点
 * 
 * 这是智能工单系统的Java用户层。
 * 它处理身份验证、会话管理，并作为UI层和Python核心业务层之间的API网关。
 */
@SpringBootApplication
@EnableFeignClients
public class SmartTicketApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(SmartTicketApplication.class, args);
    }
}