package com.trisha.academy.springlab.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI devopsJavaDemoOpenApi() {
        return new OpenAPI()
                .info(new Info()
                        .title("TRISHA ACADEMY DevOps Java Demo API")
                        .description("Welcome API and Student CRUD API")
                        .version("1.0.0"));
    }
}
