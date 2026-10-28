-- =====================================================
-- MicroCRM - Esquema MySQL
-- Generado a partir de los modelos SQLModel (app/models).
-- La API crea estas tablas automaticamente al iniciar (AUTO_CREATE_TABLES=true);
-- este script sirve para crear la base manualmente.
-- =====================================================

CREATE DATABASE IF NOT EXISTS microcrm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE microcrm_db;

CREATE TABLE users (
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    active BOOL NOT NULL,
    id INTEGER NOT NULL AUTO_INCREMENT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE projects (
    name VARCHAR(100) NOT NULL,
    description VARCHAR(150),
    id INTEGER NOT NULL AUTO_INCREMENT,
    id_user INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(id_user) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE project_roles (
    name VARCHAR(50) NOT NULL,
    description VARCHAR(150),
    project_id INTEGER NOT NULL,
    id INTEGER NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);
CREATE INDEX ix_project_roles_name ON project_roles (name);

CREATE TABLE tasks (
    project_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    description VARCHAR(150),
    status VARCHAR(50) NOT NULL,
    assigned_to INTEGER,
    due_date DATETIME,
    id INTEGER NOT NULL AUTO_INCREMENT,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE,
    FOREIGN KEY(assigned_to) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE project_members (
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    project_role_id INTEGER NOT NULL,
    id INTEGER NOT NULL AUTO_INCREMENT,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY(project_role_id) REFERENCES project_roles (id) ON DELETE RESTRICT
);
