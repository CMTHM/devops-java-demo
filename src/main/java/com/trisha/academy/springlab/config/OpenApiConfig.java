package com.trisha.academy.springlab.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.servers.Server;
import java.util.List;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI devopsJavaDemoOpenApi() {
        // Relative server URL: Swagger "Try it out" stays on the same host and port
        // the page was opened on (for example http://localhost:9090).
        return new OpenAPI()
                .servers(List.of(new Server().url("/").description("Current host")))
                .info(new Info()
                        .title("TRISHA ACADEMY DevOps Java Demo API")
                        .description("Welcome API and Student CRUD API")
                        .version("1.0.0"));
    }
}
