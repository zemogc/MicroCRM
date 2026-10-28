"""
Demo data
=========
Creates a demo team with projects, tasks and clients.

    python -m app.seed

Login: demo@microcrm.dev / Demo1234
Running it again does nothing if the demo user already exists.
"""

from datetime import timedelta
from sqlmodel import Session, select

from .core.clock import utcnow
from .core.database import engine, init_db
from .core.security import hash_password
from .models import Client, Project, ProjectMember, ProjectRole, Task, User
from .api.routes.projects import DEFAULT_ROLES

DEMO_EMAIL = "demo@microcrm.dev"
DEMO_PASSWORD = "Demo1234"

USERS = [
    ("Laura Méndez", DEMO_EMAIL),
    ("Carlos Ríos", "carlos@microcrm.dev"),
    ("Sofía Vargas", "sofia@microcrm.dev"),
    ("Andrés Ortiz", "andres@microcrm.dev"),
]

# (owner, name, description, [(member, role)])
PROJECTS = [
    ("Laura Méndez", "Rediseño tienda online", "Nuevo checkout, catálogo y pasarela de pagos",
     [("Carlos Ríos", "Desarrollador"), ("Sofía Vargas", "Revisor")]),
    ("Laura Méndez", "App de fidelización", "App móvil de puntos para clientes frecuentes",
     [("Andrés Ortiz", "Desarrollador")]),
    ("Laura Méndez", "Migración a la nube", "Mover servidores locales a contenedores", []),
    ("Carlos Ríos", "Campaña Black Friday", "Landing, correos y analítica de la campaña",
     [("Laura Méndez", "Administrador"), ("Sofía Vargas", "Desarrollador")]),
]

# (project, title, description, status, assignee, due in days)
TASKS = [
    ("Rediseño tienda online", "Wireframes del checkout", "Flujo en 3 pasos", "completed", "Sofía Vargas", -6),
    ("Rediseño tienda online", "Integrar pasarela de pagos", "Tarjetas y PSE", "in_progress", "Carlos Ríos", 3),
    ("Rediseño tienda online", "Filtros del catálogo", "Por precio, marca y talla", "in_review", "Laura Méndez", 2),
    ("Rediseño tienda online", "Pruebas de carga", None, "pending", "Carlos Ríos", 9),
    ("Rediseño tienda online", "Optimizar imágenes", "WebP y lazy loading", "pending", "Laura Méndez", -2),
    ("App de fidelización", "Diseñar sistema de puntos", None, "completed", "Laura Méndez", -10),
    ("App de fidelización", "Pantalla de recompensas", None, "in_progress", "Andrés Ortiz", 5),
    ("App de fidelización", "Notificaciones push", None, "pending", "Laura Méndez", 4),
    ("App de fidelización", "Publicar en tiendas", None, "pending", None, 25),
    ("Migración a la nube", "Inventario de servidores", None, "completed", "Laura Méndez", -15),
    ("Migración a la nube", "Dockerizar servicios", "API, workers y cron", "in_progress", "Laura Méndez", 1),
    ("Migración a la nube", "Plan de respaldo", None, "cancelled", None, None),
    ("Campaña Black Friday", "Landing de ofertas", None, "in_review", "Sofía Vargas", 6),
    ("Campaña Black Friday", "Secuencia de correos", "3 envíos segmentados", "in_progress", "Laura Méndez", 3),
    ("Campaña Black Friday", "Tablero de analítica", None, "pending", "Laura Méndez", 12),
]

# (name, company, email, phone, status, notes)
CLIENTS = [
    ("Mariana Restrepo", "Moda Andina", "mariana@modaandina.co", "+57 310 555 0101", "active", "Renovó contrato anual"),
    ("Julián Cárdenas", "Café Origen", "compras@cafeorigen.co", "+57 315 555 0144", "active", None),
    ("Paola Herrera", "Clínica Vital", "pherrera@clinicavital.com", "+57 300 555 0188", "lead", "Pidió cotización de app"),
    ("Diego Salazar", "Ferretería El Tornillo", "diego@eltornillo.co", "+57 320 555 0120", "lead", None),
    ("Valentina Gómez", "EduKids", "vale@edukids.io", "+57 311 555 0177", "active", "Interesada en módulo de pagos"),
    ("Ricardo Peña", "Transportes RP", "rpena@transportesrp.com", None, "inactive", "Pausado hasta 2026"),
    ("Natalia Ruiz", "Estudio Lumen", "hola@estudiolumen.co", "+57 318 555 0166", "lead", None),
]


def seed(session: Session) -> bool:
    if session.exec(select(User).where(User.email == DEMO_EMAIL)).first():
        return False

    now = utcnow()
    users = {}
    for name, email in USERS:
        user = User(name=name, email=email, password=hash_password(DEMO_PASSWORD))
        session.add(user)
        users[name] = user
    session.flush()

    projects = {}
    for owner, name, description, members in PROJECTS:
        project = Project(name=name, description=description, id_user=users[owner].id)
        session.add(project)
        session.flush()
        projects[name] = project

        roles = {}
        for role_name, role_description in DEFAULT_ROLES:
            role = ProjectRole(name=role_name, description=role_description, project_id=project.id)
            session.add(role)
            roles[role_name] = role
        session.flush()

        for member, role_name in members:
            session.add(ProjectMember(project_id=project.id, user_id=users[member].id, project_role_id=roles[role_name].id))

    for project, title, description, status, assignee, due_in in TASKS:
        session.add(Task(
            project_id=projects[project].id,
            title=title,
            description=description,
            status=status,
            assigned_to=users[assignee].id if assignee else None,
            due_date=now + timedelta(days=due_in) if due_in is not None else None,
        ))

    owner_id = users["Laura Méndez"].id
    for name, company, email, phone, status, notes in CLIENTS:
        session.add(Client(name=name, company=company, email=email, phone=phone,
                           status=status, notes=notes, owner_id=owner_id))

    session.commit()
    return True


def main() -> None:
    init_db()
    with Session(engine) as session:
        if seed(session):
            print(f"Datos de demo creados. Inicia sesión con {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print("Los datos de demo ya existen, no se hizo ningún cambio.")


if __name__ == "__main__":
    main()
