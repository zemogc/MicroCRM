-- Migration: Add CASCADE and SET NULL rules to foreign keys
-- This migration updates the foreign key constraints to add proper cascade rules

USE microcrm_db;

-- Drop existing foreign keys in tasks table
ALTER TABLE tasks 
    DROP FOREIGN KEY tasks_ibfk_1,
    DROP FOREIGN KEY tasks_ibfk_2,
    DROP FOREIGN KEY tasks_ibfk_3;

-- Modify assigned_to column to allow NULL (required for ON DELETE SET NULL)
ALTER TABLE tasks 
    MODIFY COLUMN assigned_to INT NULL;

-- Add foreign keys with cascade rules for tasks
ALTER TABLE tasks
    ADD CONSTRAINT tasks_ibfk_1 
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    ADD CONSTRAINT tasks_ibfk_2 
        FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    ADD CONSTRAINT tasks_ibfk_3 
        FOREIGN KEY (crated_by) REFERENCES users(id) ON DELETE CASCADE;

-- Drop existing foreign keys in projects table
ALTER TABLE projects 
    DROP FOREIGN KEY projects_ibfk_1;

-- Add foreign key with cascade rule for projects
ALTER TABLE projects
    ADD CONSTRAINT projects_ibfk_1 
        FOREIGN KEY (crated_by) REFERENCES users(id) ON DELETE CASCADE;

-- Drop existing foreign keys in project_members table
ALTER TABLE project_members 
    DROP FOREIGN KEY project_members_ibfk_1,
    DROP FOREIGN KEY project_members_ibfk_2,
    DROP FOREIGN KEY project_members_ibfk_3,
    DROP FOREIGN KEY project_members_ibfk_4;

-- Modify added_by column to allow NULL (required for ON DELETE SET NULL)
ALTER TABLE project_members 
    MODIFY COLUMN added_by INT NULL;

-- Add foreign keys with cascade rules for project_members
ALTER TABLE project_members
    ADD CONSTRAINT project_members_ibfk_1 
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    ADD CONSTRAINT project_members_ibfk_2 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    ADD CONSTRAINT project_members_ibfk_3 
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    ADD CONSTRAINT project_members_ibfk_4 
        FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL;


-- IMPORTANTE: Comportamiento de eliminación con estas reglas:
-- 
-- Cuando se elimina un USUARIO:
--   - CASCADE: Se eliminan todos sus proyectos creados (projects.crated_by)
--   - CASCADE: Se eliminan todas las tareas que creó (tasks.crated_by)
--   - CASCADE: Se eliminan todas sus membresías en proyectos (project_members.user_id)
--   - SET NULL: Las tareas asignadas a él quedan sin asignar (tasks.assigned_to = NULL)
--   - SET NULL: Los registros donde agregó miembros quedan sin referencia (project_members.added_by = NULL)
--
-- Cuando se elimina un PROYECTO:
--   - CASCADE: Se eliminan todas sus tareas (tasks.project_id)
--   - CASCADE: Se eliminan todos sus miembros (project_members.project_id)
--
-- Cuando se intenta eliminar un ROL:
--   - RESTRICT: NO se puede eliminar si está en uso en project_members
