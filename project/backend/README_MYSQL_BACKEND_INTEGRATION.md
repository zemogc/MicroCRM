# MicroCRM - Integración MySQL con FastAPI

## Resumen del Proyecto

MicroCRM es una API REST para gestión de proyectos y tareas, desarrollada con FastAPI y MySQL. Este documento describe la integración completa de la base de datos MySQL con SQLModel.

## Base de Datos MySQL

### Estructura de Tablas

#### 1. users - Gestión de usuarios
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    active TINYINT(1) NOT NULL DEFAULT 1
);
```

#### 2. roles - Roles del sistema
```sql
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(150)
);
```

#### 3. projects - Proyectos
```sql
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(150),
    crated_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (crated_by) REFERENCES users(id) ON DELETE RESTRICT
);
```

#### 4. project_members - Miembros de proyectos
```sql
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
```

#### 5. tasks - Tareas
```sql
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
```

### Roles por Defecto
```sql
INSERT INTO roles (name, description) VALUES
('Admin', 'Project administrator with full access'),
('Manager', 'Project manager with management permissions'),
('Developer', 'Developer with development permissions'),
('Viewer', 'Read-only access to project information');
```

## Configuración Técnica

### Dependencias
```txt
# Base de datos
sqlmodel==0.0.21
sqlalchemy==2.0.36
pymysql==1.1.0
cryptography==42.0.7

# Seguridad
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# API
fastapi==0.112.2
uvicorn==0.30.6
pydantic==2.8.2
```

### Variables de Entorno
```bash
# Base de datos MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=microcrm_db

# Seguridad
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## API Endpoints

### Usuarios (/api/users)

#### 1. Registro de Usuario
```http
POST /api/users/register
Content-Type: application/json

{
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "password": "Password123"
}
```

Respuesta:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "name": "Juan Pérez",
        "email": "juan@example.com",
        "active": true,
        "created_at": "2025-01-07T17:50:31",
        "updated_at": "2025-01-07T17:50:31"
    }
}
```

#### 2. Login de Usuario
```http
POST /api/users/login
Content-Type: application/json

{
    "email": "juan@example.com",
    "password": "Password123"
}
```

#### 3. Listar Usuarios
```http
GET /api/users
```

#### 4. Obtener Usuario por ID
```http
GET /api/users/{user_id}
```

#### 5. Actualizar Usuario
```http
PUT /api/users/{user_id}
Content-Type: application/json

{
    "name": "Juan Carlos Pérez",
    "email": "juan.carlos@example.com"
}
```

#### 6. Eliminar Usuario
```http
DELETE /api/users/{user_id}
```

### Proyectos (/api/projects)

#### 1. Crear Proyecto
```http
POST /api/projects
Content-Type: application/json

{
    "name": "Proyecto Web",
    "description": "Desarrollo de aplicación web",
    "crated_by": 1
}
```

Respuesta:
```json
{
    "id": 1,
    "name": "Proyecto Web",
    "description": "Desarrollo de aplicación web",
    "crated_by": 1,
    "created_at": "2025-01-07T17:50:31",
    "updated_at": "2025-01-07T17:50:31",
    "creator_email": "juan@example.com"
}
```

#### 2. Listar Proyectos
```http
GET /api/projects
```

#### 3. Obtener Proyecto por ID
```http
GET /api/projects/{project_id}
```

#### 4. Actualizar Proyecto
```http
PUT /api/projects/{project_id}
Content-Type: application/json

{
    "name": "Proyecto Web Actualizado",
    "description": "Nueva descripción"
}
```

#### 5. Eliminar Proyecto
```http
DELETE /api/projects/{project_id}
```

### Tareas (/api/tasks)

#### 1. Crear Tarea
```http
POST /api/tasks
Content-Type: application/json

{
    "project_id": 1,
    "title": "Implementar login",
    "description": "Crear sistema de autenticación",
    "status": "pending",
    "assigned_to": 2,
    "due_date": "2025-01-15T23:59:59"
}
```

Respuesta:
```json
{
    "id": 1,
    "project_id": 1,
    "title": "Implementar login",
    "description": "Crear sistema de autenticación",
    "status": "pending",
    "crated_by": 1,
    "assigned_to": 2,
    "created_at": "2025-01-07T17:50:31",
    "due_date": "2025-01-15T23:59:59",
    "project_name": "Proyecto Web",
    "assigned_to_email": "maria@example.com",
    "created_by_email": "juan@example.com"
}
```

#### 2. Listar Todas las Tareas
```http
GET /api/tasks
```

#### 3. Listar Tareas por Proyecto
```http
GET /api/tasks/project/{project_id}
```

#### 4. Listar Tareas por Usuario
```http
GET /api/tasks/user/{user_id}
```

#### 5. Obtener Tarea por ID
```http
GET /api/tasks/{task_id}
```

#### 6. Actualizar Tarea
```http
PUT /api/tasks/{task_id}
Content-Type: application/json

{
    "status": "in_progress",
    "assigned_to": 3
}
```

#### 7. Eliminar Tarea
```http
DELETE /api/tasks/{task_id}
```

### Roles (/api/roles)

#### 1. Crear Rol
```http
POST /api/roles
Content-Type: application/json

{
    "name": "Tester",
    "description": "Responsable de pruebas"
}
```

#### 2. Listar Roles
```http
GET /api/roles
```

#### 3. Obtener Rol por ID
```http
GET /api/roles/{role_id}
```

#### 4. Actualizar Rol
```http
PUT /api/roles/{role_id}
Content-Type: application/json

{
    "name": "Senior Tester",
    "description": "Tester senior con más responsabilidades"
}
```

#### 5. Eliminar Rol
```http
DELETE /api/roles/{role_id}
```

### Miembros de Proyecto (/api/project-members)

#### 1. Agregar Miembro a Proyecto
```http
POST /api/project-members
Content-Type: application/json

{
    "project_id": 1,
    "user_id": 2,
    "role_id": 3,
    "added_by": 1
}
```

Respuesta:
```json
{
    "id": 1,
    "project_id": 1,
    "user_id": 2,
    "role_id": 3,
    "added_by": 1,
    "created_at": "2025-01-07T17:50:31",
    "user_name": "María García",
    "role_name": "Developer",
    "added_by_name": "Juan Pérez"
}
```

#### 2. Listar Miembros de Proyecto
```http
GET /api/project-members/project/{project_id}
```

#### 3. Listar Proyectos de Usuario
```http
GET /api/project-members/user/{user_id}
```

#### 4. Actualizar Rol de Miembro
```http
PUT /api/project-members/{member_id}
Content-Type: application/json

{
    "role_id": 2
}
```

#### 5. Eliminar Miembro de Proyecto
```http
DELETE /api/project-members/{member_id}
```

## Seguridad

### Autenticación
- JWT Tokens con expiración configurable
- Password Hashing con pbkdf2_sha256
- Validación de contraseñas (mínimo 8 caracteres, mayúscula, minúscula, número)

### Validaciones
- Email único en registro
- Validación de campos con Pydantic
- Foreign Key constraints en base de datos
- Status válidos para tareas: `pending`, `in_progress`, `completed`, `cancelled`

## Comandos de Prueba

### Registro y Login
```bash
# Registro
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Usuario Test", "email": "test@example.com", "password": "Password123"}'

# Login
curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Password123"}'
```

### Crear Proyecto y Tarea
```bash
# Crear proyecto
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{"name": "Mi Proyecto", "description": "Descripción del proyecto", "crated_by": 1}'

# Crear tarea
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "title": "Mi Tarea", "description": "Descripción de la tarea", "crated_by": 1}'
```

## Estructura del Proyecto

```
project/backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── users.py          # Endpoints de usuarios
│   │       ├── projects.py       # Endpoints de proyectos
│   │       ├── tasks.py          # Endpoints de tareas
│   │       ├── roles.py          # Endpoints de roles
│   │       └── project_members.py # Endpoints de miembros
│   ├── core/
│   │   ├── database.py           # Configuración MySQL
│   │   ├── settings.py           # Variables de entorno
│   │   └── security.py           # Autenticación y hashing
│   ├── models/
│   │   ├── user.py               # Modelo Usuario
│   │   ├── project.py            # Modelo Proyecto
│   │   ├── task.py               # Modelo Tarea
│   │   ├── role.py               # Modelo Rol
│   │   └── project_member.py     # Modelo Miembro
│   └── main.py                   # Aplicación FastAPI
├── requirements.txt              # Dependencias Python
└── microcrm_db_script.sql       # Script de base de datos
```

## Instalación y Uso

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar MySQL
```bash
# Ejecutar script SQL
mysql -u root -p < microcrm_db_script.sql
```

### 3. Configurar variables de entorno
```bash
# Crear archivo .env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=microcrm_db
SECRET_KEY=your-secret-key-here
```

### 4. Ejecutar aplicación
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Probar API
```bash
curl http://localhost:8000/health
```

## Características Implementadas

- Integración MySQL completa con SQLModel
- API REST completa con CRUD para todas las entidades
- Autenticación JWT con registro y login
- Validaciones robustas con Pydantic
- Respuestas enriquecidas con datos relacionados
- Password hashing seguro con pbkdf2_sha256
- Relaciones de base de datos con foreign keys
- Endpoints especializados (tareas por proyecto, usuarios por proyecto, etc.)
- Manejo de errores con HTTPException
- Configuración flexible con variables de entorno
