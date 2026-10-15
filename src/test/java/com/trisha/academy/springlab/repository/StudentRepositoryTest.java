package com.trisha.academy.springlab.repository;

import static org.assertj.core.api.Assertions.assertThat;

import com.trisha.academy.springlab.model.Student;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class StudentRepositoryTest {

    @Autowired
    private StudentRepository studentRepository;

    @Test
    @DisplayName("save generates an id and the student can be read back")
    void saveAndFind() {
        Student saved = studentRepository.save(new Student(null, "Asha", "DevOps"));

        assertThat(saved.getId()).isNotNull();
        assertThat(studentRepository.findById(saved.getId())).get().satisfies(s -> {
            assertThat(s.getName()).isEqualTo("Asha");
            assertThat(s.getCourse()).isEqualTo("DevOps");
        });
    }

    @Test
    @DisplayName("deleteById removes the student")
    void deleteById() {
        Student saved = studentRepository.save(new Student(null, "Ravi", "Java"));

        studentRepository.deleteById(saved.getId());

        assertThat(studentRepository.existsById(saved.getId())).isFalse();
    }
}
