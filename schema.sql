-- MySQL 8+ starter schema for the Welfare Scheme System.
-- Flask-SQLAlchemy can create the same schema automatically with db.create_all().

CREATE DATABASE IF NOT EXISTS welfare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE welfare_db;

-- Recommended: let Flask-SQLAlchemy create tables from app/models.py.
-- This file is provided for database setup/reference.
