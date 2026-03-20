package com.smartticket.feign;

import feign.Request;
import feign.Retryer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration for TicketServiceClient Feign client.
 * This configuration makes the Feign client more resilient to connection failures.
 */
@Configuration
public class TicketServiceClientConfig {

    @Bean
    public Request.Options ticketServiceRequestOptions() {
        // 配置超时选项：连接超时30秒，读取超时30秒
        return new Request.Options(30 * 1000, 30 * 1000);
    }

    @Bean
    public Retryer ticketServiceRetryer() {
        // 配置重试策略：初始延迟100ms，最大延迟1s，最大重试次数3
        return new Retryer.Default(100, 1000, 3);
    }
}