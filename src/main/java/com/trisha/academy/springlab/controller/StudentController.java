package com.trisha.academy.springlab.controller;

import com.trisha.academy.springlab.model.Student;
import com.trisha.academy.springlab.repository.StudentRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/students")
@Tag(name = "Students", description = "Student CRUD API")
public class StudentController {

    private static final Logger log = LoggerFactory.getLogger(StudentController.class);

    private final StudentRepository studentRepository;

    public StudentController(StudentRepository studentRepository) {
        this.studentRepository = studentRepository;
    }

    @PostMapping
    @Operation(summary = "Insert a student")
    public ResponseEntity<Student> insert(@RequestBody Student student) {
        student.setId(null);
        Student saved = studentRepository.save(student);
        log.info("Inserted student id={}, name={}, course={}", saved.getId(), saved.getName(), saved.getCourse());
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @GetMapping
    @Operation(summary = "Get all students")
    public List<Student> getAll() {
        List<Student> students = studentRepository.findAll();
        log.info("Fetching all students, count={}", students.size());
        return students;
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get a student by id")
    public ResponseEntity<Student> getById(@PathVariable Long id) {
        return studentRepository
                .findById(id)
                .map(student -> {
                    log.info("Fetched student id={}", id);
                    return ResponseEntity.ok(student);
                })
                .orElseGet(() -> {
                    log.warn("Student id={} not found", id);
                    return ResponseEntity.notFound().build();
                });
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update a student")
    public ResponseEntity<Student> update(@PathVariable Long id, @RequestBody Student student) {
        if (!studentRepository.existsById(id)) {
            log.warn("Update failed, student id={} not found", id);
            return ResponseEntity.notFound().build();
        }
        student.setId(id);
        Student saved = studentRepository.save(student);
        log.info("Updated student id={}, name={}, course={}", id, saved.getName(), saved.getCourse());
        return ResponseEntity.ok(saved);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete a student")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (!studentRepository.existsById(id)) {
            log.warn("Delete failed, student id={} not found", id);
            return ResponseEntity.notFound().build();
        }
        studentRepository.deleteById(id);
        log.info("Deleted student id={}", id);
        return ResponseEntity.noContent().build();
    }
}
