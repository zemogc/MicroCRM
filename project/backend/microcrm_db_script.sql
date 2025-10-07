-- =====================================================
-- MicroCRM Database Schema for MySQL
-- Simple version for Python/FastAPI Backend
-- =====================================================

-- Create database
-- CREATE DATABASE IF NOT EXISTS microcrm;
-- USE microcrm;

-- =====================================================
-- Table: users
-- =====================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    active TINYINT(1) NOT NULL DEFAULT 1
);

-- =====================================================
-- Table: roles
-- =====================================================
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(150)
);

-- =====================================================
-- Table: projects
-- =====================================================
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(150),
    crated_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (crated_by) REFERENCES users(id) ON DELETE RESTRICT
);

-- =====================================================
-- Table: project_members
-- =====================================================
CREATE TABLE project_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    added_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE RESTRICT,
    
    UNIQUE KEY unique_project_user (project_id, user_id)
);

-- =====================================================
-- Table: tasks
-- =====================================================
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description VARCHAR(150),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    crated_by INT NOT NULL,
    assigned_to INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME NULL,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (crated_by) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- Insert default roles
-- =====================================================
INSERT INTO roles (name, description) VALUES 
('Admin', 'Project administrator with full access'),
('Manager', 'Project manager with management permissions'),
('Developer', 'Developer with development permissions'),
('Viewer', 'Read-only access to project information');