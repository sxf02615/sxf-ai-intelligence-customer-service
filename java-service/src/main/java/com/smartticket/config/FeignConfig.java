package com.smartticket.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import feign.Client;
import feign.Logger;
import feign.Request;
import feign.Retryer;
import feign.codec.Decoder;
import feign.codec.Encoder;
import feign.jackson.JacksonDecoder;
import feign.jackson.JacksonEncoder;
import feign.okhttp.OkHttpClient;

/**
 * 智能工单服务的Feign客户端配置。
 * 配置HTTP客户端以与Python核心服务通信。
 */
@Configuration
public class FeignConfig {

    @Value("${python-core.url:http://localhost:8000}")
    private String pythonCoreUrl;

    @Bean
    public Client feignClient() {
        // 使用OkHttpClient，它更健壮，能更好地处理连接失败
        return new OkHttpClient();
    }

    @Bean
    public Encoder feignEncoder(ObjectMapper objectMapper) {
        // 使用配置了snake_case的ObjectMapper
        return new JacksonEncoder(objectMapper);
    }

    @Bean
    public Decoder feignDecoder(ObjectMapper objectMapper) {
        // 使用配置了snake_case的ObjectMapper
        return new JacksonDecoder(objectMapper);
    }

    @Bean
    public Logger.Level feignLoggerLevel() {
        return Logger.Level.FULL;
    }

    @Bean
    public Request.Options requestOptions() {
        // 配置超时选项以防止启动时挂起
        return new Request.Options(5000, 10000); // 5秒连接超时，10秒读取超时
    }

    @Bean
    public Retryer retryer() {
        // 配置重试策略
        return new Retryer.Default(100, 1000, 3);
    }
}