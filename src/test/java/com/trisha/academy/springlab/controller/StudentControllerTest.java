package com.trisha.academy.springlab.controller;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.trisha.academy.springlab.model.Student;
import com.trisha.academy.springlab.repository.StudentRepository;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(StudentController.class)
class StudentControllerTest {

    private static final String STUDENT_JSON = "{\"name\":\"Asha\",\"course\":\"DevOps\"}";

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private StudentRepository studentRepository;

    @Nested
    @DisplayName("POST /students")
    class Insert {

        @Test
        @DisplayName("returns 201 with the saved student and ignores any client-supplied id")
        void insertReturnsCreated() throws Exception {
            when(studentRepository.save(any(Student.class))).thenReturn(new Student(1L, "Asha", "DevOps"));

            mockMvc.perform(post("/students")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{\"id\":99,\"name\":\"Asha\",\"course\":\"DevOps\"}"))
                    .andExpect(status().isCreated())
                    .andExpect(jsonPath("$.id").value(1))
                    .andExpect(jsonPath("$.name").value("Asha"))
                    .andExpect(jsonPath("$.course").value("DevOps"));

            ArgumentCaptor<Student> captor = ArgumentCaptor.forClass(Student.class);
            verify(studentRepository).save(captor.capture());
            assertThat(captor.getValue().getId()).isNull();
        }

        @Test
        @DisplayName("returns 400 when the body is not valid JSON")
        void insertWithBadJsonReturnsBadRequest() throws Exception {
            mockMvc.perform(post("/students")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{bad json"))
                    .andExpect(status().isBadRequest());
        }

        @Test
        @DisplayName("returns 415 when the content type is not JSON")
        void insertWithWrongContentTypeReturnsUnsupportedMediaType() throws Exception {
            mockMvc.perform(post("/students").contentType(MediaType.TEXT_PLAIN).content("Asha"))
                    .andExpect(status().isUnsupportedMediaType());
        }
    }

    @Nested
    @DisplayName("GET /students")
    class GetAll {

        @Test
        @DisplayName("returns 200 with every student")
        void getAllReturnsList() throws Exception {
            when(studentRepository.findAll())
                    .thenReturn(List.of(new Student(1L, "Asha", "DevOps"), new Student(2L, "Ravi", "Java")));

            mockMvc.perform(get("/students"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$", hasSize(2)))
                    .andExpect(jsonPath("$[1].name").value("Ravi"));
        }

        @Test
        @DisplayName("returns 200 with an empty list when there are no students")
        void getAllReturnsEmptyList() throws Exception {
            when(studentRepository.findAll()).thenReturn(List.of());

            mockMvc.perform(get("/students")).andExpect(status().isOk()).andExpect(jsonPath("$", hasSize(0)));
        }
    }

    @Nested
    @DisplayName("GET /students/{id}")
    class GetById {

        @Test
        @DisplayName("returns 200 when the student exists")
        void getByIdFound() throws Exception {
            when(studentRepository.findById(1L)).thenReturn(Optional.of(new Student(1L, "Asha", "DevOps")));

            mockMvc.perform(get("/students/1"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.name").value("Asha"));
        }

        @Test
        @DisplayName("returns 404 when the student does not exist")
        void getByIdNotFound() throws Exception {
            when(studentRepository.findById(42L)).thenReturn(Optional.empty());

            mockMvc.perform(get("/students/42")).andExpect(status().isNotFound());
        }

        @Test
        @DisplayName("returns 400 when the id is not a number")
        void getByIdWithInvalidId() throws Exception {
            mockMvc.perform(get("/students/abc")).andExpect(status().isBadRequest());
        }
    }

    @Nested
    @DisplayName("PUT /students/{id}")
    class Update {

        @Test
        @DisplayName("returns 200 with the updated student")
        void updateFound() throws Exception {
            when(studentRepository.existsById(1L)).thenReturn(true);
            when(studentRepository.save(any(Student.class))).thenReturn(new Student(1L, "Asha", "DevOps"));

            mockMvc.perform(put("/students/1")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(STUDENT_JSON))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.id").value(1))
                    .andExpect(jsonPath("$.course").value("DevOps"));
        }

        @Test
        @DisplayName("returns 404 and saves nothing when the student does not exist")
        void updateNotFound() throws Exception {
            when(studentRepository.existsById(42L)).thenReturn(false);

            mockMvc.perform(put("/students/42")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(STUDENT_JSON))
                    .andExpect(status().isNotFound());

            verify(studentRepository, never()).save(any(Student.class));
        }
    }

    @Nested
    @DisplayName("DELETE /students/{id}")
    class Delete {

        @Test
        @DisplayName("returns 204 and deletes the student")
        void deleteFound() throws Exception {
            when(studentRepository.existsById(1L)).thenReturn(true);

            mockMvc.perform(delete("/students/1")).andExpect(status().isNoContent());

            verify(studentRepository).deleteById(1L);
        }

        @Test
        @DisplayName("returns 404 and deletes nothing when the student does not exist")
        void deleteNotFound() throws Exception {
            when(studentRepository.existsById(42L)).thenReturn(false);

            mockMvc.perform(delete("/students/42")).andExpect(status().isNotFound());

            verify(studentRepository, never()).deleteById(any());
        }
    }
}
