package com.trisha.academy.springlab.repository;

import com.trisha.academy.springlab.model.Student;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StudentRepository extends JpaRepository<Student, Long> {}
