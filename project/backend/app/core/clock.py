from datetime import datetime, timezone


def utcnow() -> datetime:
    """Fecha y hora actual en UTC sin zona horaria (como se guarda en la base de datos)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
