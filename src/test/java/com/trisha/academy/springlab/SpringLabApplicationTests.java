package com.trisha.academy.springlab;

import static org.assertj.core.api.Assertions.assertThat;

import com.trisha.academy.springlab.controller.StudentController;
import com.trisha.academy.springlab.controller.WelcomeController;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;

@SpringBootTest
class SpringLabApplicationTests {

    @Autowired
    private ApplicationContext context;

    @Test
    void contextLoads() {
        assertThat(context.getBean(WelcomeController.class)).isNotNull();
        assertThat(context.getBean(StudentController.class)).isNotNull();
    }
}
