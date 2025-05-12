# BikeCorpDB Security System

Project with the aim of creating a role-based access control system for securing database operations in the BikeCorpDB database. 
This project implements multi-level security with table permissions, column-level security, and row-level filtering.

## Overview
This security system provides a framework for controlling access to the BikeCorpDB bicycle store database based on user roles. It ensures that users only have access to the data they need for their job functions, enforcing the principle of least privilege.

### Features

Role-Based Access Control: 
Different permissions for administrators, store managers, sales staff, and customers

Multi-Level Security:

Table-level permissions (which operations are allowed on each table)
Column-level restrictions (which fields each role can see)
Row-level filtering (which records each role can access)


Secure Database Operations: Protected SELECT, INSERT, UPDATE, and DELETE operations

Audit Logging: Tracking all database access for compliance and security monitoring

## Project Structure

user_auth.py - User authentication functionality
role_definitions.py - Role permissions and access rules
secure_db.py - Base secure database access class
secure_operations.py - Secure database operation implementations
db_logger.py - Audit logging functionality
test_secure_operations.py - Test cases demonstrating security features

## User Roles
The system implements the following user roles:

Administrator: Full access to all data and operations
Executive: Company-wide data access with some restrictions
Store Manager: Access limited to their own store's data
Team Lead: Team-specific access within a store
Sales Staff: Limited access for day-to-day sales operations
Customer: Access to only their own account and order data

## Installation and Setup

Clone the repository
Configure database connection in db_config.json:
json{
  "host": "localhost",
  "user": "your_username",
  "password": "your_password",
  "database": "BikeCorpDB"
}

Install required dependencies:
pip install mysql-connector-python




