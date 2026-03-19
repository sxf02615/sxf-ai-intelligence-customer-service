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
        // 配置超时选项以防止启动时挂起
        // 连接超时：5秒，读取超时：10秒
        return new Request.Options(5000, 10000);
    }

    @Bean
    public Retryer ticketServiceRetryer() {
        // 配置重试策略：初始延迟100ms，最大延迟1s，最大重试次数3
        return new Retryer.Default(100, 1000, 3);
    }
}