# Fetch-DE-Full-Time

Fetch Rewards data engineering full-time take-home test

## Overview
This project involves developing a small application to perform an ETL (Extract, Transform, Load) process. The application reads JSON data containing user login behavior from an AWS SQS (Simple Queue Service) Queue, masks sensitive information, and writes the transformed data into a PostgreSQL database. Docker is used to create a local environment with all the necessary components, making it easy to run the application without an AWS account.

## Objectives
The main objectives of this project are as follows:
1. Read JSON data containing user login behavior from an AWS SQS Queue provided via a custom LocalStack image with pre-loaded data.
2. Mask personal identifiable information (PII) in the 'device_id' and 'ip' fields in a way that allows easy identification of duplicate values for data analysts.
3. Flatten the JSON data object and write each record to a Postgres database using a custom Postgres image with pre-created tables. The target table's DDL is provided in the assignment.

## Notes
1. Reading Messages from the Queue: The AWS SDK will be used to interact with the SQS Queue and retrieve messages.
2. Data Structures: Python dictionaries will be used to store and manipulate the JSON data.
3. Masking PII Data: SHA-256 hashing will be applied to the 'device_id' and 'ip' fields to mask the sensitive information.
4. The 'app_version' field is converted to an integer for better storage and indexing in the database.
5. Connecting and Writing to Postgres: psycopg2 library will be used to connect to the PostgreSQL database and execute SQL queries to insert the transformed data.
6. Running the Application: The application will be executed locally using Docker to set up the necessary services (LocalStack for SQS and custom Postgres image).

## Project Setup & running the application
1. Clone the repository
2. Setup Docker, Postgres and awscli
3. Run Docker
4. Execute the below code to start the local SQS and postgres 
   ```bash
   docker-compose up
5. Run main.py to read JSON data from the SQS Queue, mask the 'device_id' and 'ip' fields using SHA-256 hashing, and write the transformed data to the PostgreSQL database
    ```bash
   python3 main.py
