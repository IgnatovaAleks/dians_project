package com.finance.ingestion;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class DataIngestionApplication {
    public static void main(String[] args) {
        SpringApplication.run(DataIngestionApplication.class, args);
    }
}